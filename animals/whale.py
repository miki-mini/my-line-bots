# ========================================
# 🐋 whale.py - 星くじらからの光の便り (Star Whale)
# 天体観測、NASAの天文写真をLINEに送信
# NASA APOD API連携で実際の宇宙画像を配信
# 深宇宙から優しく語りかける神秘的なキャラクター
# ========================================

import os
import random
import requests
from datetime import datetime, timedelta

from fastapi import Request, HTTPException
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    ImageMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError


def register_whale_handler(app, handler_whale, configuration_whale):
    """
    星くじらのWebhookエンドポイントとハンドラーを登録する

    Parameters:
        app: FastAPIアプリケーション
        handler_whale: LINE WebhookHandler
        configuration_whale: LINE Configuration
    """

    # ==========================================
    # 🐋 星くじら Webhook エンドポイント
    # ==========================================
    @app.post("/callback_whale")
    async def callback_whale(request: Request):
        signature = request.headers.get("X-Line-Signature", "")
        body = await request.body()

        try:
            handler_whale.handle(body.decode("utf-8"), signature)
        except InvalidSignatureError:
            print("❌ 星くじら: 署名エラー")
            raise HTTPException(status_code=400, detail="Invalid signature")
        except Exception as e:
            print(f"❌ 星くじら: Webhookエラー: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        return "OK"

    # ==========================================
    # 🐋 テキストメッセージ処理
    # ==========================================
    @handler_whale.add(MessageEvent, message=TextMessageContent)
    def handle_whale_message(event):
        user_text = event.message.text
        print(f"🐋 星くじら受信: {user_text}")

        # 星くじらのセリフ集
        greetings = [
            "銀河の彼方から、こんにちは...🐋💫",
            "ふふ、宇宙の海は今日も静かですよ。",
            "星の光があなたを照らしますように...",
            "深宇宙の波に乗って、あなたの元へ...🌌",
        ]

        facts = [
            "知っていますか？宇宙には2兆個以上の銀河があるんですよ...✨",
            "ジェイムズ・ウェッブ望遠鏡は、130億年前の光を捉えています🔭",
            "私たちの体を作る元素は、かつて星の中で生まれたのです⭐",
            "天の川銀河の直径は約10万光年...途方もない旅ですね🐋",
        ]

        reply_messages = []  # 返信するメッセージを入れるリスト

        # --- 会話ロジック ---
        if "写真" in user_text or "画像" in user_text:
            # NASA APOD APIから画像を探す
            image_data = _get_nasa_apod_image()

            if image_data and image_data.get("url"):
                # 1通目：メッセージ（タイトル付き）
                title = image_data.get("title", "宇宙からの便り")
                reply_messages.append(
                    TextMessage(text=f"銀河の彼方から、光の便りが届きましたよ...🐋💫\n\n📷 {title}")
                )
                # 2通目：画像
                reply_messages.append(
                    ImageMessage(
                        original_content_url=image_data["url"],
                        preview_image_url=image_data["url"]
                    )
                )
            else:
                reply_messages.append(
                    TextMessage(
                        text="申し訳ありません...宇宙の雲が厚くて、うまく写真が見つかりませんでした。🐋💦"
                    )
                )

        elif "こんにちは" in user_text or "おはよう" in user_text:
            reply_messages.append(
                TextMessage(text=f"{random.choice(greetings)}\nあなたの声、届いていますよ。")
            )

        elif "星" in user_text or "宇宙" in user_text or "銀河" in user_text:
            reply_messages.append(TextMessage(text=random.choice(facts)))

        elif "ありがとう" in user_text:
            reply_messages.append(
                TextMessage(
                    text="こちらこそ...あなたと話せて、星の海が少し温かくなりました🐋💫"
                )
            )

        else:
            # デフォルト返答
            reply_messages.append(
                TextMessage(text=f"「{user_text}」...その言葉、星に刻んでおきますね。")
            )

        # LINEに返信
        _send_reply_messages(event, configuration_whale, reply_messages)

    print("🐋 星くじらハンドラー登録完了（NASA APOD API連携・画像送信対応）")


# ==========================================
# 🔭 NASA APOD API から天文写真を取得
# ==========================================
def _get_nasa_apod_image():
    """
    NASA APOD (Astronomy Picture of the Day) APIから宇宙画像を取得する
    毎日1枚の美しい天文写真が必ずあるので失敗しにくい
    """

    # NASA APIキー（DEMO_KEYは1時間50回制限だが、テストには十分）
    # 本格運用時は https://api.nasa.gov/ で無料キーを取得推奨
    api_key = os.getenv("NASA_API_KEY", "DEMO_KEY")

    # ランダムな日付を選ぶ（過去30日から）
    days_ago = random.randint(0, 30)
    target_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

    apod_url = "https://api.nasa.gov/planetary/apod"
    params = {
        "api_key": api_key,
        "date": target_date,
        "thumbs": True  # 動画の場合サムネイルを取得
    }

    try:
        print(f"🐋 NASA APOD API 呼び出し: {target_date}")
        response = requests.get(apod_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # 画像かどうか確認（たまに動画の日がある）
        media_type = data.get("media_type", "")

        if media_type == "image":
            image_url = data.get("hdurl") or data.get("url")
            # HTTPSに変換（LINE必須）
            if image_url and image_url.startswith("http://"):
                image_url = image_url.replace("http://", "https://")

            print(f"🐋 APOD画像取得成功: {image_url}")
            return {
                "url": image_url,
                "title": data.get("title", ""),
                "explanation": data.get("explanation", "")
            }

        elif media_type == "video":
            # 動画の日はサムネイルを使う
            thumb_url = data.get("thumbnail_url")
            if thumb_url:
                if thumb_url.startswith("http://"):
                    thumb_url = thumb_url.replace("http://", "https://")
                print(f"🐋 APOD動画サムネイル取得: {thumb_url}")
                return {
                    "url": thumb_url,
                    "title": data.get("title", "") + "（動画より）",
                    "explanation": data.get("explanation", "")
                }
            else:
                # サムネイルがない場合は別の日を試す
                print("🐋 動画でサムネイルなし、別の日を試行...")
                return _get_nasa_apod_image_fallback(api_key)

    except requests.exceptions.Timeout:
        print("❌ 星くじら: NASA APOD API タイムアウト")
    except requests.exceptions.HTTPError as e:
        print(f"❌ 星くじら: NASA APOD API HTTPエラー: {e}")
    except Exception as e:
        print(f"❌ 星くじら: NASA APOD API エラー: {e}")

    return None


def _get_nasa_apod_image_fallback(api_key):
    """
    メインの取得が失敗した時用のフォールバック
    より古い日付から確実に画像を取得
    """
    # 60〜90日前のどこかから取得（動画じゃない確率が高い日を狙う）
    days_ago = random.randint(60, 90)
    target_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

    apod_url = "https://api.nasa.gov/planetary/apod"
    params = {
        "api_key": api_key,
        "date": target_date
    }

    try:
        response = requests.get(apod_url, params=params, timeout=10)
        data = response.json()

        if data.get("media_type") == "image":
            image_url = data.get("hdurl") or data.get("url")
            if image_url and image_url.startswith("http://"):
                image_url = image_url.replace("http://", "https://")
            return {
                "url": image_url,
                "title": data.get("title", ""),
                "explanation": data.get("explanation", "")
            }
    except Exception as e:
        print(f"❌ フォールバックも失敗: {e}")

    return None


# ==========================================
# 📨 返信ヘルパー関数
# ==========================================
def _send_reply_messages(event, configuration, messages):
    """複数メッセージ対応の返信ヘルパー関数"""
    try:
        with ApiClient(configuration) as api_client:
            line_api = MessagingApi(api_client)
            line_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=messages
                )
            )
    except Exception as e:
        print(f"❌ 星くじら返信エラー: {e}")