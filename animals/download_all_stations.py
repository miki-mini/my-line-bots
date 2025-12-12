"""
download_stations_debug.py - デバッグ版
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

ODPT_API_KEY = os.getenv("ODPT_API_KEY")

print("🔍 デバッグモード")
print(f"APIキー: {ODPT_API_KEY[:10]}... (最初の10文字)" if ODPT_API_KEY else "❌ APIキーなし")
print()

if not ODPT_API_KEY:
    print("❌ ODPT_API_KEYが設定されていません")
    print("📝 .env ファイルを確認してください")
    exit(1)

# まず単純なリクエストを試す
url = "https://api.odpt.org/api/v4/odpt:Station"
params = {
    "acl:consumerKey": ODPT_API_KEY,
    "limit": 10  # まず10件だけ試す
}

print(f"🌐 リクエストURL: {url}")
print(f"📋 パラメータ: {params}")
print()

try:
    print("📡 APIリクエスト送信中...")
    response = requests.get(url, params=params, timeout=30)

    print(f"📥 ステータスコード: {response.status_code}")
    print(f"📄 Content-Type: {response.headers.get('Content-Type')}")
    print(f"📊 レスポンスサイズ: {len(response.content)} bytes")
    print()

    if response.status_code != 200:
        print(f"❌ HTTPエラー: {response.status_code}")
        print(f"📝 エラー内容:\n{response.text[:500]}")
        exit(1)

    # JSONパース
    data = response.json()

    print(f"✅ データ取得成功！")
    print(f"📊 取得件数: {len(data)}件")
    print()

    if not data:
        print("⚠️ データが空です")
        print("🔍 考えられる原因:")
        print("  1. APIキーが無効")
        print("  2. APIの仕様が変わった")
        print("  3. アクセス制限がかかっている")
        exit(1)

    # 最初の1件を詳しく表示
    print("📋 サンプルデータ (最初の1件):")
    print(json.dumps(data[0], indent=2, ensure_ascii=False)[:1000])
    print()

    # 駅名とIDを抽出
    print("📍 最初の10駅:")
    for i, station in enumerate(data[:10], 1):
        station_id = station.get("owl:sameAs", "ID不明")
        titles = station.get("dc:title", "")

        if isinstance(titles, str):
            name = titles
        elif isinstance(titles, dict):
            name = titles.get("ja") or titles.get("@ja") or "不明"
        else:
            name = "不明"

        print(f"  {i}. {name} ({station_id})")

    print("\n✅ デバッグ完了！APIは正常に動作しています")
    print("📝 次は download_stations_by_railway.py を実行してください")

except requests.exceptions.Timeout:
    print("❌ タイムアウト: APIの応答がありません")
except requests.exceptions.ConnectionError:
    print("❌ 接続エラー: インターネット接続を確認してください")
except json.JSONDecodeError as e:
    print(f"❌ JSONパースエラー: {e}")
    print(f"📝 レスポンス内容:\n{response.text[:500]}")
except Exception as e:
    print(f"❌ 予期しないエラー: {e}")
    import traceback
    traceback.print_exc()