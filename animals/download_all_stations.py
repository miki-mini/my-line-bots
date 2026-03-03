"""
download_all_stations.py - 全駅取得（事業者別ループ ＋ 補完版）
APIの上限で取得できない駅（吉祥寺など）を手動で補完します。
"""

import os
import requests
import time
import json
from dotenv import load_dotenv

load_dotenv()

ODPT_API_KEY = os.getenv("ODPT_API_KEY")

if not ODPT_API_KEY:
    print("❌ ODPT_API_KEYが設定されていません")
    exit(1)

API_ENDPOINT = "https://api.odpt.org/api/v4"

# 🛑 APIで取れない場合の補完リスト（吉祥寺など）
MANUAL_ADDITIONS = [
    {
        "name": "吉祥寺",
        "id": "odpt.Station:JR-East.Chuo.Kichijoji",
        "railway": "JR-East"
    },
    {
        "name": "吉祥寺",
        "id": "odpt.Station:Keio.Inokashira.Kichijoji",
        "railway": "Keio"
    }
]

def get_all_operators():
    """全事業者を取得"""
    print("🔄 事業者リストを取得中...")
    url = f"{API_ENDPOINT}/odpt:Operator"
    params = {"acl:consumerKey": ODPT_API_KEY}

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ 事業者取得エラー: {e}")
        return []

def get_stations_by_operator(operator_id):
    """事業者IDを指定して駅を取得"""
    url = f"{API_ENDPOINT}/odpt:Station"
    params = {
        "acl:consumerKey": ODPT_API_KEY,
        "odpt:operator": operator_id
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"⚠️ {operator_id} の取得失敗: {e}")
        return []

def main():
    print("🚀 駅データ全件ダウンロードを開始します...")

    # 1. 事業者一覧取得
    operators = get_all_operators()
    print(f"📦 全事業者数: {len(operators)}件")

    # 2. 駅情報を収集
    all_stations_raw = []

    total_ops = len(operators)

    for i, operator in enumerate(operators, 1):
        op_id = operator.get("owl:sameAs", "")
        op_title = operator.get("dc:title", op_id)

        # print(f"[{i}/{total_ops}] {op_title} ...", end="\r")

        stations = get_stations_by_operator(op_id)
        if stations:
            # print(f"✅ [{i}/{total_ops}] {op_title}: {len(stations)}駅")
            all_stations_raw.extend(stations)

        time.sleep(0.05)

    print(f"\n🎉 API取得完了！ 合計: {len(all_stations_raw)}件")

    # 3. 整形 & 補完
    print("🛠 データを整形・補完中...")

    formatted_stations = []
    seen_ids = set()
    seen_names = set() # 名前重複チェック用（デバッグ）

    # (A) API取得分を追加
    for station in all_stations_raw:
        s_id = station.get("owl:sameAs", "")

        if not s_id or s_id in seen_ids:
            continue

        # 駅名（日本語優先）
        titles = station.get("dc:title", "")
        station_name = ""

        if isinstance(titles, str):
            station_name = titles
        elif isinstance(titles, dict):
            station_name = titles.get("ja") or titles.get("@ja") or titles.get("jp")
            if not station_name and titles:
                station_name = list(titles.values())[0]
        else:
            station_name = str(titles)

        # 路線名
        railway = station.get("odpt:railway", "")
        railway_name = railway.split(":")[-1].split(".")[0] if railway else "Unknown"

        if station_name:
            seen_ids.add(s_id)
            seen_names.add(station_name)

            formatted_stations.append({
                "name": station_name,
                "id": s_id,
                "railway": railway_name
            })

    # (B) 手動補完リストを追加（まだ入っていなければ）
    added_manual_count = 0
    for manual in MANUAL_ADDITIONS:
        # 名前チェック（ある程度）
        if manual["name"] not in seen_names:
             # IDチェック
            if manual["id"] not in seen_ids:
                formatted_stations.append(manual)
                seen_ids.add(manual["id"])
                seen_names.add(manual["name"])
                added_manual_count += 1
                print(f"➕ 手動追加: {manual['name']} ({manual['railway']})")

    # 名前順にソート
    formatted_stations.sort(key=lambda x: x["name"])

    # 4. 吉祥寺チェック
    kichijoji = [s for s in formatted_stations if "吉祥寺" in s["name"]]
    print(f"\n🔍 確認: '吉祥寺' -> {len(kichijoji)}件")

    # 5. 保存
    output_path = os.path.join(os.path.dirname(__file__), "station_data.py")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write('"""\n')
        f.write('station_data.py - 駅データ一覧（ODPT API + 手動補完）\n')
        f.write(f'合計: {len(formatted_stations)}駅\n')
        f.write(f'更新日: {time.strftime("%Y-%m-%d %H:%M:%S")}\n')
        f.write('"""\n\n')
        f.write('STATIONS = [\n')

        for s in formatted_stations:
            name_esc = s["name"].replace('"', '\\"')
            id_esc = s["id"].replace('"', '\\"')
            rail_esc = s["railway"].replace('"', '\\"')

            f.write('    {\n')
            f.write(f'        "name": "{name_esc}",\n')
            f.write(f'        "id": "{id_esc}",\n')
            f.write(f'        "railway": "{rail_esc}"\n')
            f.write('    },\n')

        f.write(']\n')

    print(f"\n💾 {output_path} に保存しました！")

if __name__ == "__main__":
    main()