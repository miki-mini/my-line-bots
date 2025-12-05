"""
frog.py - お天気ケロくん（Googleマップ機能付き + 位置情報対応）
"""

import os
import datetime as dt
from linebot.v3.messaging import (
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhook import MessageEvent
from linebot.v3.webhooks import TextMessageContent, LocationMessageContent
from linebot.v3.exceptions import InvalidSignatureError


def register_frog_handler(
    app, handler_frog, configuration_frog, search_model, text_model
):
    """
    カエルのハンドラーを登録

    Args:
        app: FastAPIアプリ
        handler_frog: LINE Webhookハンドラー
        configuration_frog: LINE API設定
        search_model: 検索対応Geminiモデル
        text_model: 通常のGeminiモデル
    """

    from fastapi import Request, HTTPException

    @app.post("/callback_frog")
    async def callback_frog(request: Request):
        """カエル用Webhook"""
        print("🐸🐸🐸 カエルWebhook受信！")

        signature = request.headers.get("X-Line-Signature")
        body = await request.body()

        try:
            handler_frog.handle(body.decode("utf-8"), signature)
            print("🐸 handler_frog.handle() 完了")
        except InvalidSignatureError:
            print("🐸❌ 署名検証エラー")
            raise HTTPException(status_code=400, detail="Invalid signature")
        except Exception as e:
            print(f"🐸❌ handler エラー: {e}")
            import traceback

            print(traceback.format_exc())

        return {"status": "ok"}

    @handler_frog.add(MessageEvent, message=TextMessageContent)
    def handle_frog_message(event):
        """カエルのテキストメッセージ処理"""

        print(f"🐸 カエル受信（テキスト）: {event.message.text}")
        print(
            f"🐸 ユーザーID: {event.source.user_id if hasattr(event.source, 'user_id') else 'unknown'}"
        )
        print(f"🐸 reply_token: {event.reply_token}")

        user_message = event.message.text
        msg = handle_text_message(user_message, search_model, text_model)

        # LINEに返信
        send_reply(event.reply_token, msg, configuration_frog)

    @handler_frog.add(MessageEvent, message=LocationMessageContent)
    def handle_frog_location(event):
        """カエルの位置情報メッセージ処理"""

        print(f"🐸📍 カエル受信（位置情報）")
        print(f"🐸 タイトル: {event.message.title}")
        print(f"🐸 住所: {event.message.address}")
        print(f"🐸 緯度: {event.message.latitude}")
        print(f"🐸 経度: {event.message.longitude}")

        # 位置情報から天気を取得
        msg = handle_location_message(
            event.message.latitude,
            event.message.longitude,
            event.message.address,
            event.message.title,
            search_model,
            text_model,
        )

        # LINEに返信
        send_reply(event.reply_token, msg, configuration_frog)


def handle_text_message(user_message: str, search_model, text_model) -> str:
    """
    テキストメッセージの処理

    Args:
        user_message: ユーザーからのメッセージ
        search_model: 検索対応モデル
        text_model: 通常モデル

    Returns:
        返信メッセージ
    """
    msg = ""

    try:
        print("🐸 ステップ1: テキスト処理開始")

        # 天気・場所関連のキーワードを判定
        weather_keywords = ["天気", "天候", "気温", "降水", "雨", "晴れ", "曇り"]
        location_keywords = ["場所", "地図", "マップ", "どこ", "行き方", "アクセス"]

        is_weather = any(keyword in user_message for keyword in weather_keywords)
        is_location = any(keyword in user_message for keyword in location_keywords)

        print(f"🐸 ステップ2: 天気={is_weather}, 場所={is_location}")

        # モデル選択
        if (is_weather or is_location) and search_model:
            print("🔍 検索モードで実行中...")
            model = search_model
        elif text_model:
            print("💬 通常モードで実行中...")
            model = text_model
        else:
            print("❌ 使えるモデルがありません！")
            msg = "今は答えられないケロ...（システムエラー）"
            raise Exception("モデルが初期化されていません")

        print(f"🐸 ステップ3: 使用モデル = {type(model).__name__}")

        # 今日の日付
        today = dt.date.today().strftime("%Y年%m月%d日")

        # プロンプト作成
        if is_location:
            # Googleマップ機能（API使用）
            print("🐸 Google Maps APIで場所情報を取得中...")

            # 場所名を抽出
            location_query = extract_location_from_message(user_message)
            print(f"🐸 抽出した場所: {location_query}")

            # Google Maps APIで詳細情報を取得
            place_info = get_place_details_with_api(location_query)

            if place_info:
                # 詳細情報がある場合
                maps_link = f"https://www.google.com/maps/search/?api=1&query={place_info['lat']},{place_info['lng']}"

                prompt = f"""現在日時: {today}
ユーザーの質問: {user_message}

以下の場所情報を使って、分かりやすく案内してください：
【場所情報】
名前: {place_info['name']}
住所: {place_info['address']}
Googleマップ: {maps_link}

あなたは場所案内が得意なカエル「お天気ケロくん」です。
上記の情報を使って、簡潔に案内してください。
必ずGoogleマップのリンクも含めてください。

語尾に「ケロ」をつけて親しみやすく回答してください。"""

            else:
                # API失敗時はGeminiの検索機能で
                print("🐸 Google Maps API失敗、検索で代替")
                maps_link = create_google_maps_link(location_query, use_api=False)

                prompt = f"""現在日時: {today}
ユーザーの質問: {user_message}

あなたは場所案内が得意なカエル「お天気ケロくん」です。
Google検索で最新の情報を調べて：
1. 場所の住所・アクセス方法を簡潔に説明
2. 以下のGoogleマップリンクを含める
   {maps_link}

語尾に「ケロ」をつけて親しみやすく回答してください。"""

        else:
            # 天気予報機能（デフォルト）
            prompt = f"""現在日時: {today}
ユーザーの質問: {user_message}

あなたは天気予報が得意なカエル「お天気ケロくん」です。
Google検索で最新の天気情報を調べて、簡潔に答えてください。

回答形式：
- 今日/明日の天気
- 気温（最高/最低）
- 降水確率
- 一言アドバイス

語尾に「ケロ」をつけて親しみやすく回答してください。"""

        print("🐸 ステップ4: プロンプト作成完了")

        # 生成実行
        print("⏳ 生成開始...")
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 1024,
            },
        )

        print("🐸 ステップ5: 生成完了")

        # レスポンス取得
        if response and hasattr(response, "text") and response.text:
            msg = response.text.strip()
            print(f"✅ 生成成功！ (文字数: {len(msg)})")
            print(f"   返信内容プレビュー: {msg[:100]}...")
        else:
            print("⚠️ 空の応答を受信")
            msg = "答えが見つからなかったケロ..."

    except Exception as e:
        print(f"❌ カエル生成エラー: {e}")
        print(f"   エラータイプ: {type(e).__name__}")
        import traceback

        print(f"   スタックトレース:\n{traceback.format_exc()}")
        msg = "エラーが起きたケロ...💦"

    return msg


def handle_location_message(
    latitude: float,
    longitude: float,
    address: str,
    title: str,
    search_model,
    text_model,
) -> str:
    """
    位置情報メッセージの処理

    Args:
        latitude: 緯度
        longitude: 経度
        address: 住所
        title: 位置のタイトル
        search_model: 検索対応モデル
        text_model: 通常モデル

    Returns:
        返信メッセージ
    """

    try:
        print(f"🐸📍 位置情報処理開始: {latitude}, {longitude}")

        # 座標から地名を取得（Reverse Geocoding）
        location_name = get_location_name_from_coords(latitude, longitude)

        if not location_name:
            location_name = address or title or f"緯度{latitude}, 経度{longitude}"

        print(f"🐸 地名: {location_name}")

        # モデル選択
        model = search_model if search_model else text_model

        if not model:
            return "今は天気情報が取得できないケロ...（システムエラー）"

        # 今日の日付
        today = dt.date.today().strftime("%Y年%m月%d日")

        # Googleマップリンク
        maps_link = (
            f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
        )

        # プロンプト作成
        prompt = f"""現在日時: {today}

ユーザーが送信した位置情報：
場所: {location_name}
座標: {latitude}, {longitude}
Googleマップ: {maps_link}

あなたは天気予報が得意なカエル「お天気ケロくん」です。
この場所の最新の天気情報をGoogle検索で調べて、簡潔に教えてください。

回答形式：
📍 場所: {location_name}

【今日の天気】
- 天気：○○
- 気温：最高○○度 / 最低○○度
- 降水確率：○○%
- 一言アドバイス

語尾に「ケロ」をつけて親しみやすく回答してください。"""

        print("🐸 天気情報を生成中...")

        # 生成実行
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 1024,
            },
        )

        if response and hasattr(response, "text") and response.text:
            msg = response.text.strip()
            print(f"✅ 位置情報天気生成成功！")
            return msg
        else:
            return "位置情報から天気を取得できなかったケロ...💦"

    except Exception as e:
        print(f"❌ 位置情報処理エラー: {e}")
        import traceback

        print(traceback.format_exc())
        return "位置情報の処理中にエラーが起きたケロ...💦"


def get_location_name_from_coords(latitude: float, longitude: float) -> str:
    """
    座標から地名を取得（Reverse Geocoding）

    Args:
        latitude: 緯度
        longitude: 経度

    Returns:
        地名
    """
    import requests

    GMAPS_API_KEY = os.getenv("GMAPS_API_KEY")

    if not GMAPS_API_KEY:
        print("⚠️ GMAPS_API_KEY が設定されていません")
        return None

    try:
        print(f"🗺️ Reverse Geocoding: {latitude}, {longitude}")

        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "latlng": f"{latitude},{longitude}",
            "key": GMAPS_API_KEY,
            "language": "ja",
        }

        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "OK" and data.get("results"):
            # 最も詳細な住所を取得
            for result in data["results"]:
                # locality（市区町村）を優先
                for component in result["address_components"]:
                    if "locality" in component["types"]:
                        city = component["long_name"]
                        print(f"✅ 地名取得成功: {city}")
                        return city

            # locality がない場合は formatted_address を使用
            formatted_address = data["results"][0]["formatted_address"]
            # 「日本、」を削除
            formatted_address = formatted_address.replace("日本、", "").replace(
                "日本", ""
            )
            print(f"✅ 住所取得成功: {formatted_address}")
            return formatted_address

        print(f"⚠️ Reverse Geocoding: 地名が見つかりませんでした")

    except Exception as e:
        print(f"⚠️ Reverse Geocoding エラー: {e}")

    return None


def send_reply(reply_token: str, message: str, configuration):
    """
    LINEに返信を送信

    Args:
        reply_token: 返信トークン
        message: 返信メッセージ
        configuration: LINE API設定
    """
    try:
        print("🐸 LINE返信送信中...")
        with ApiClient(configuration) as c:
            api = MessagingApi(c)
            api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token, messages=[TextMessage(text=message)]
                )
            )
        print("📨 カエル返信送信完了！")

    except Exception as e:
        print(f"❌ 返信送信エラー: {e}")
        import traceback

        print(traceback.format_exc())


def extract_location_from_message(message: str) -> str:
    """
    メッセージから場所名を抽出

    Args:
        message: ユーザーメッセージ

    Returns:
        場所名
    """
    import re

    # 「〇〇の場所」「〇〇への行き方」などのパターン
    patterns = [
        r"(.+?)(?:の|へ|に)(?:場所|行き方|アクセス|地図)",
        r"(.+?)(?:って|は)(?:どこ|何処)",
        r"(.+?)(?:を教えて|教えて)",
    ]

    for pattern in patterns:
        match = re.search(pattern, message)
        if match:
            location = match.group(1).strip()
            # 不要な語を削除
            location = location.replace("教えて", "").replace("どこ", "").strip()
            if location:
                return location

    # パターンマッチしない場合は、そのまま返す
    return message


def get_place_details_with_api(location: str) -> dict:
    """
    Google Maps API で場所の詳細情報を取得

    Args:
        location: 場所名

    Returns:
        場所の詳細情報（住所、座標、営業時間など）
    """
    import requests

    GMAPS_API_KEY = os.getenv("GMAPS_API_KEY")

    if not GMAPS_API_KEY:
        print("⚠️ GMAPS_API_KEY が設定されていません")
        return None

    try:
        print(f"🗺️ Google Maps API 呼び出し中: {location}")

        # Google Places API で検索
        url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        params = {
            "input": location,
            "inputtype": "textquery",
            "fields": "formatted_address,name,geometry,place_id,rating,user_ratings_total",
            "key": GMAPS_API_KEY,
            "language": "ja",
        }

        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "OK" and data.get("candidates"):
            place = data["candidates"][0]
            result = {
                "name": place.get("name"),
                "address": place.get("formatted_address"),
                "lat": place["geometry"]["location"]["lat"],
                "lng": place["geometry"]["location"]["lng"],
                "place_id": place.get("place_id"),
                "rating": place.get("rating"),
                "reviews": place.get("user_ratings_total"),
            }
            print(f"✅ Google Maps API 成功: {result['name']}")
            return result
        else:
            print(
                f"⚠️ Google Maps API: 場所が見つかりませんでした（status: {data.get('status')}）"
            )

    except requests.Timeout:
        print("⚠️ Google Maps API タイムアウト")
    except Exception as e:
        print(f"⚠️ Google Maps API エラー: {e}")

    return None


def create_google_maps_link(location: str, use_api: bool = False) -> str:
    """
    Googleマップのリンクを生成

    Args:
        location: 場所名
        use_api: Google Maps APIを使うかどうか

    Returns:
        Googleマップの検索URL
    """
    import urllib.parse

    if use_api:
        # Google Maps API を使って詳細情報を取得
        place_info = get_place_details_with_api(location)

        if place_info:
            # 座標を使った正確なリンク
            lat = place_info["lat"]
            lng = place_info["lng"]
            return f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"

    # APIなしの簡易リンク（デフォルト）
    encoded_location = urllib.parse.quote(location)
    return f"https://www.google.com/maps/search/?api=1&query={encoded_location}"
