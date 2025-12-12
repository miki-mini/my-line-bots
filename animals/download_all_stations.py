"""
download_all_stations_v2.py - ODPT APIから全駅データを一括ダウンロード（ページネーション対応版）
"""

import os
import requests
import json
import time
from dotenv import load_dotenv

load_dotenv()

ODPT_API_KEY = os.getenv("ODPT_API_KEY")

if not ODPT_API_KEY:
    print("❌ ODPT_API_KEYが設定されていません")
    exit(1)

print("🔄 ODPT APIから全駅データをダウンロード中...")
print("📝 ページネーションで分割取得します...\n")

# 全駅データを取得（ページネーション対応）
url = "https://api.odpt.org/api/v4/odpt:Station"

all_stations = []
offset = 0
limit = 1000  # 1回のリクエストで取得する件数

while True:
    params = {
        "acl:consumerKey": ODPT_API_KEY,
        "limit": limit,
        "offset": offset
    }

    print(f"📥 {offset}件目から取得中...")

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        stations = response.json()

        if not stations:
            print("✅ これ以上データがありません")
            break

        all_stations.extend(stations)
        print(f"   取得: {len(stations)}件 (累計: {len(all_stations)}件)")

        # データが limit 未満なら最後のページ
        if len(stations) < limit:
            print("✅ 最後のページに到達しました")
            break

        offset += limit
        time.sleep(0.5)  # APIへの負荷を減らすため少し待つ

    except requests.exceptions.Timeout:
        print("⚠️ タイムアウト: 再試行します...")
        time.sleep(2)
        continue
    except requests.exceptions.RequestException as e:
        print(f"❌ エラー: {e}")
        break

print(f"\n✅ 合計 {len(all_stations)}件の駅データを取得しました！")

if not all_stations:
    print("❌ データが取得できませんでした")
    exit(1)

# station_data.py 形式に変換
print("\n🔄 データを変換中...")
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
    railway_name = railway.split(":")[-1] if railway else "Unknown"

    if station_id and station_name:
        stations_list.append({
            "name": station_name,
            "id": station_id,
            "railway": railway_name
        })

print(f"✅ {len(stations_list)}件の有効な駅データに変換しました")

# 駅名でソート
stations_list.sort(key=lambda x: x["name"])

# station_data.py に保存
print("\n💾 station_data.py に保存中...")

with open("station_data.py", "w", encoding="utf-8") as f:
    f.write('"""\n')
    f.write('station_data.py - 駅データ一覧（ODPT APIから自動生成）\n')
    f.write(f'合計: {len(stations_list)}駅\n')
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
print("\n📊 路線別の駅数 (上位20):")
from collections import Counter
railway_counts = Counter([s["railway"] for s in stations_list])

for i, (railway, count) in enumerate(railway_counts.most_common(20), 1):
    print(f"  {i:2d}. {railway}: {count}駅")

# 都道府県別の駅数も表示（駅名から推測）
print("\n🗾 主要都市の駅数:")
city_keywords = {
    "東京": ["東京", "新宿", "渋谷", "池袋"],
    "横浜": ["横浜"],
    "大阪": ["大阪", "梅田", "難波"],
    "京都": ["京都"],
    "神戸": ["神戸"],
}

for city, keywords in city_keywords.items():
    count = sum(1 for s in stations_list if any(k in s["name"] for k in keywords))
    if count > 0:
        print(f"  {city}エリア: {count}駅")

print(f"\n✨ 完了！これで{len(stations_list)}駅が使えます！")
print(f"📁 ファイルサイズ: {os.path.getsize('station_data.py') / 1024:.1f} KB")