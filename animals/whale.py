# ========================================
# 🐋 whale.py - 星くじらからの光の便り (Star Whale)
# 天体観測、ジェイムズ・ウェッブの写真をLINEに送信
# 深宇宙から優しく語りかける神秘的なキャラクター
# ========================================

import os
import random

from fastapi import Request, HTTPException
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
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

        # --- 会話ロジック ---
        if "写真" in user_text or "画像" in user_text:
            reply_text = (
                "ジェイムズ・ウェッブの新しい写真ですね？\n"
                "深宇宙から探してきますので、少しお待ちを...🐋\n"
                "（※画像機能は準備中です）"
            )
        elif "こんにちは" in user_text or "おはよう" in user_text:
            reply_text = f"{random.choice(greetings)}\nあなたの声、届いていますよ。"
        elif "星" in user_text or "宇宙" in user_text or "銀河" in user_text:
            reply_text = random.choice(facts)
        elif "ありがとう" in user_text:
            reply_text = "こちらこそ...あなたと話せて、星の海が少し温かくなりました🐋💫"
        else:
            reply_text = f"「{user_text}」...素敵な響きですね。深宇宙まで聞こえてきそうです。"

        # LINEに返信
        _send_reply(event, configuration_whale, reply_text)

    print("🐋 星くじらハンドラー登録完了")


def _send_reply(event, configuration, text):
    """テキスト返信のヘルパー関数"""
    try:
        with ApiClient(configuration) as api_client:
            line_api = MessagingApi(api_client)
            line_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=text)]
                )
            )
    except Exception as e:
        print(f"❌ 星くじら返信エラー: {e}")