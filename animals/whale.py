# ========================================
# 🐋 whale.py - 星くじらからの光の便り (Star Whale)
# 天体観測、ジェイムズ・ウェッブの写真をLINEに送信
# NASA API連携で実際の宇宙画像を配信
# 深宇宙から優しく語りかける神秘的なキャラクター
# ========================================

import os
import random
import requests

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
            # NASA APIから画像を探す
            image_url = _get_jwst_image()

            if image_url:
                # 1通目：メッセージ
                reply_messages.append(
                    TextMessage(text="銀河の彼方から、光の便りが届きましたよ...🐋💫")
                )
                # 2通目：画像
                reply_messages.append(
                    ImageMessage(
                        original_content_url=image_url,
                        preview_image_url=image_url
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

    print("🐋 星くじらハンドラー登録完了（NASA API連携・画像送信対応）")


# ==========================================
# 🔭 NASA API から JWST 画像を取得
# ==========================================
def _get_jwst_image():
    """
    NASAのAPIを叩いて、ジェイムズ・ウェッブの最新っぽい画像のURLを取得する関数
    LINEはHTTPS必須なので、http:// は https:// に変換する
    """
    search_url = "https://images-api.nasa.gov/search"

    # 2025年の画像を探す設定（年が変わったらここを変えます）
    params = {
        "q": "James Webb Space Telescope",
        "media_type": "image",
        "year_start": "2025"
    }

    try:
        response = requests.get(search_url, params=params, timeout=10)
        data = response.json()

        # 画像が見つかったか確認
        if "items" in data["collection"] and len(data["collection"]["items"]) > 0:
            # 検索結果の1つ目を取得
            first_item = data["collection"]["items"][0]

            # 画像ファイルのリストがあるURL（collection）を取得
            json_href = first_item["href"]
            image_response = requests.get(json_href, timeout=10)
            image_list = image_response.json()

            # LINEで送りやすい "medium" サイズの画像を探す
            for img_url in image_list:
                if "medium.jpg" in img_url:
                    # HTTPSに変換（LINE必須）
                    if img_url.startswith("http://"):
                        img_url = img_url.replace("http://", "https://")
                    print(f"🐋 JWST画像取得成功: {img_url}")
                    return img_url

            # mediumがなければリストの1つ目を返す
            if image_list:
                img_url = image_list[0]
                # HTTPSに変換（LINE必須）
                if img_url.startswith("http://"):
                    img_url = img_url.replace("http://", "https://")
                print(f"🐋 JWST画像取得成功（フォールバック）: {img_url}")
                return img_url

    except requests.exceptions.Timeout:
        print("❌ 星くじら: NASA API タイムアウト")
    except Exception as e:
        print(f"❌ 星くじら: NASA API エラー: {e}")

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