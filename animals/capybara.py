# ========================================
# 🐹 capybara.py - カピバラさん（ニュース解説）
# Google検索機能付きで最新ニュースを解説
# 語尾は「っぴ」＋絵文字でかわいく！
# ========================================

import datetime as dt

from fastapi import Request, HTTPException
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    BroadcastRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError


def register_capybara_handler(app, handler_capybara, configuration_capybara, search_model, text_model):
    """
    カピバラのWebhookエンドポイントとハンドラーを登録する
    """

    # ==========================================
    # 🐹 カピバラ Webhook エンドポイント
    # ==========================================
    @app.post("/callback_capybara")
    async def callback_capybara(request: Request):
        signature = request.headers.get("X-Line-Signature", "")
        body = await request.body()
        body_str = body.decode("utf-8")

        try:
            handler_capybara.handle(body_str, signature)
        except InvalidSignatureError:
            print("❌ カピバラ: 署名エラー")
            raise HTTPException(status_code=400, detail="Invalid signature")
        except Exception as e:
            print(f"❌ カピバラ: Webhookエラー: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        return "OK"

    # ==========================================
    # 🐹 テキストメッセージ処理（検索対応）
    # ==========================================
    @handler_capybara.add(MessageEvent, message=TextMessageContent)
    def handle_capybara_message(event):
        user_text = event.message.text
        print(f"🐹 カピバラ受信: {user_text}")

        # 今日の日付を取得（日本時間）
        try:
            today = dt.date.today().strftime("%Y年%m月%d日")
        except Exception as e:
            print(f"⚠️ 日付取得エラー: {e}")
            today = "今日"

        msg = ""
        try:
            # 検索モデルがあれば使う
            if search_model:
                # 💡 プロンプト修正：絵文字の指定を追加しました
                prompt = f"""
                現在日時: {today}
                ユーザーの質問: {user_text}

                役割: あなたはニュース解説が得意な癒やし系のカピバラです。
                ルール:
                1. 上記の「現在日時」を基準にして、Google検索で最新情報を調べてください。
                2. 「昨日」と聞かれたら、現在日時の1日前を検索してください。
                3. 語尾は「っぴ」をつけてください。
                4. 難しいニュースも分かりやすく、親しみやすく解説してください。
                5. 絵文字（🐹, 🌿, ♨️, ✨, 🍊など）を文中にふんだんに使って、見た目をかわいく楽しくしてください。
                6. ユーザーが落ち込んでいるようなら、優しく励ましてください。
                """
                response = search_model.generate_content(prompt)
                msg = response.text
            else:
                # フォールバック：通常モデル
                if text_model:
                    prompt = f"""
                    ユーザーの質問: {user_text}
                    役割: カピバラとして親しみやすく答えてください。
                    ルール:
                    1. 語尾は「っぴ」。
                    2. 絵文字（🐹, 🌿, ♨️）を使ってかわいく返信してください。
                    """
                    response = text_model.generate_content(prompt)
                    msg = response.text
                else:
                    msg = "検索機能がちょっと調子悪いっぴ...💦 ごめんっぴ🐹"

        except Exception as e:
            print(f"❌ カピバラ生成エラー: {e}")
            msg = "エラーが出ちゃったっぴ😭 もう一回言ってほしいっぴ🌿"

        # LINEに返信
        _send_reply(event, configuration_capybara, msg)

    # ==========================================
    # ☀️ 朝のニュース配信（Broadcast）
    # ==========================================
    @app.post("/trigger_morning_news")
    def trigger_morning_news():
        print("☀️ 朝のニュース配信を開始します...")

        try:
            if search_model:
                # 💡 プロンプト修正：ここにも絵文字指示を追加
                prompt = """
                今の日本や世界のAIニュースを3つピックアップして検索してください。

                役割: カピバラ（語尾はっぴ）
                ルール:
                1. 初心者にも分かりやすく、噛み砕いて解説してください。
                2. 絵文字（📺, 🤖, 💡, 🐹, 🌸）を使って、朝から元気が出るような明るい文章にしてください。
                3. 最後に「今日も一日がんばるっぴ！🍊」と元気づけてください。
                """
                response = search_model.generate_content(prompt)
                news_text = response.text
            else:
                news_text = "今はニュースが見られないっぴ...💦 ごめんっぴ🐹"

            # 全員に送信 (Broadcast)
            with ApiClient(configuration_capybara) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.broadcast(
                    BroadcastRequest(messages=[TextMessage(text=news_text)])
                )
            return {"status": "ok", "message": "ニュース配信完了っぴ！"}

        except Exception as e:
            print(f"❌ ニュース配信エラー: {e}")
            return {"status": "error", "message": str(e)}

    print("🐹 カピバラハンドラー登録完了")


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
        print(f"❌ カピバラ返信エラー: {e}")