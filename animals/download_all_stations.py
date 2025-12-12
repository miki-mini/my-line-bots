"""
download_stations_simple.py - 720駅を確実に取得（シンプル版）
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

ODPT_API_KEY = os.getenv("ODPT_API_KEY")

if not ODPT_API_KEY:
    print("❌ ODPT_API_KEYが設定されていません")
    exit(1)

print("🔄 ODPT APIから駅データをダウンロード中...")

# シンプルに1回のリクエストで取得
url = "https://api.odpt.org/api/v4/odpt:Station"
params = {"acl:consumerKey": ODPT_API_KEY}

try:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    all_stations = response.json()

    print(f"✅ {len(all_stations)}件の駅データを取得しました！")

    # station_data.py 形式に変換
    stations_list = []

    for station in all_stations:
        station_id = station.get("owl:sameAs", "")

        # 日本語名を取得
        titles = station.get("dc:title", "")
        if isinstance(titles, str):
            station_name = titles
        else:
            # 日本語を優先
            station_name = None
            if isinstance(titles, dict):
                for key in ["ja", "@ja", "jp"]:
                    if key in titles:
                        station_name = titles[key]
                        break
                if not station_name and titles:
                    station_name = list(titles.values())[0]
            else:
                station_name = str(titles)

        # 路線情報を取得
        railway = station.get("odpt:railway", "")
        railway_name = railway.split(":")[-1].split(".")[0] if railway else "Unknown"

        if station_id and station_name:
            stations_list.append({
                "name": station_name,
                "id": station_id,
                "railway": railway_name
            })

    # 駅名でソート
    stations_list.sort(key=lambda x: x["name"])

    # station_data.py に保存
    with open("station_data.py", "w", encoding="utf-8") as f:
        f.write('"""\n')
        f.write('station_data.py - 駅データ一覧（ODPT APIから取得）\n')
        f.write(f'合計: {len(stations_list)}駅\n')
        f.write('"""\n\n')
        f.write('STATIONS = [\n')

        for station in stations_list:
            # エスケープ処理（駅名にクォートがある場合）
            name_escaped = station["name"].replace('"', '\\"')
            id_escaped = station["id"].replace('"', '\\"')

            f.write('    {\n')
            f.write(f'        "name": "{name_escaped}",\n')
            f.write(f'        "id": "{id_escaped}",\n')
            f.write(f'        "railway": "{station["railway"]}"\n')
            f.write('    },\n')

        f.write(']\n')

    print(f"✅ station_data.py に {len(stations_list)}駅を保存しました！")

    # 統計情報
    print("\n📊 会社別の駅数:")
    from collections import Counter
    company_counts = Counter([s["railway"] for s in stations_list])

    for i, (company, count) in enumerate(company_counts.most_common(15), 1):
        print(f"  {i:2d}. {company}: {count}駅")

    # 主要駅の確認
    print("\n🔍 主要駅の確認:")
    major_stations = ["東京", "新宿", "渋谷", "池袋", "横浜", "大阪", "京都"]
    for name in major_stations:
        found = [s for s in stations_list if name in s["name"]]
        if found:
            print(f"  ✅ {name}: {len(found)}件")
        else:
            print(f"  ❌ {name}: 見つかりません")

    file_size = os.path.getsize('station_data.py') / 1024
    print(f"\n✨ 完了！")
    print(f"📁 ファイルサイズ: {file_size:.1f} KB")
    print(f"📊 合計: {len(stations_list)}駅")

except requests.exceptions.Timeout:
    print("❌ タイムアウト")
except Exception as e:
    print(f"❌ エラー: {e}")
    import traceback
    traceback.print_exc()