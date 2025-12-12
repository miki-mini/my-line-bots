"""
download_all_stations.py - ODPT APIから全駅データを一括ダウンロード
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

ODPT_API_KEY = os.getenv("ODPT_API_KEY")

if not ODPT_API_KEY:
    print("❌ ODPT_API_KEYが設定されていません")
    exit(1)

print("🔄 ODPT APIから全駅データをダウンロード中...")

# 全駅データを取得
url = "https://api.odpt.org/api/v4/odpt:Station"
params = {
    "acl:consumerKey": ODPT_API_KEY
}

try:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    all_stations = response.json()

    print(f"✅ {len(all_stations)}件の駅データを取得しました！")

    # station_data.py 形式に変換
    stations_list = []

    for station in all_stations:
        station_id = station.get("owl:sameAs", "")

        # 日本語名を取得（複数言語対応）
        titles = station.get("dc:title", "")
        if isinstance(titles, str):
            station_name = titles
        else:
            # 日本語を優先
            station_name = None
            for lang, name in titles.items():
                if lang == "ja" or lang == "@ja":
                    station_name = name
                    break
            if not station_name and titles:
                station_name = list(titles.values())[0]

        # 路線情報を取得
        railway = station.get("odpt:railway", "")
        railway_name = railway.split(":")[-1] if railway else "Unknown"

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
        f.write('station_data.py - 駅データ一覧（ODPT APIから自動生成）\n')
        f.write('"""\n\n')
        f.write('STATIONS = [\n')

        for station in stations_list:
            f.write('    {\n')
            f.write(f'        "name": "{station["name"]}",\n')
            f.write(f'        "id": "{station["id"]}",\n')
            f.write(f'        "railway": "{station["railway"]}"\n')
            f.write('    },\n')

        f.write(']\n')

    print(f"✅ station_data.py に {len(stations_list)}件の駅を保存しました！")

    # 統計情報を表示
    from collections import Counter
    railway_counts = Counter([s["railway"] for s in stations_list])

    print("\n📊 路線別の駅数:")
    for railway, count in railway_counts.most_common(10):
        print(f"  {railway}: {count}駅")

    print(f"\n✨ 完了！これで日本全国の駅が使えます！")

except requests.exceptions.Timeout:
    print("❌ タイムアウト: APIの応答が遅すぎます")
except requests.exceptions.RequestException as e:
    print(f"❌ エラー: {e}")
except Exception as e:
    print(f"❌ 予期しないエラー: {e}")
    import traceback
    traceback.print_exc()