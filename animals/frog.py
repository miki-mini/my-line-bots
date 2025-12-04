"""
frog.py - お天気ケロくん（Googleマップ機能付き）
"""

import os
import datetime as dt
from linebot.v3.messaging import (
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhook import MessageEvent
from linebot.v3.webhooks import TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError


def register_frog_handler(app, handler_frog, configuration_frog, search_model, text_model):
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
        """カエルのメッセージ処理"""

        print(f"🐸 カエル受信: {event.message.text}")
        print(f"🐸 ユーザーID: {event.source.user_id if hasattr(event.source, 'user_id') else 'unknown'}")
        print(f"🐸 reply_token: {event.reply_token}")

        user_message = event.message.text
        msg = ""

        try:
            print("🐸 ステップ1: 処理開始")

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
                # Googleマップ機能
                prompt = f"""現在日時: {today}
ユーザーの質問: {user_message}

あなたは場所案内が得意なカエル「お天気ケロくん」です。
ユーザーが場所について聞いている場合：
1. Google検索で最新の情報を調べて
2. 場所の住所・アクセス方法を簡潔に説明
3. 可能であればGoogleマップのリンクを含める
   形式: https://www.google.com/maps/search/?api=1&query=場所名

回答は親しみやすく、語尾に「ケロ」をつけてください。"""

            else:
                # 天気予報機能
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
                }
            )

            print("🐸 ステップ5: 生成完了")

            # レスポンス取得
            if response and hasattr(response, 'text') and response.text:
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

        # LINEに返信
        try:
            print("🐸 ステップ6: LINE返信開始")
            print(f"   返信先token: {event.reply_token}")
            print(f"   メッセージ: {msg[:50]}...")

            with ApiClient(configuration_frog) as c:
                api = MessagingApi(c)
                api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=msg)]
                    )
                )
            print("📨 カエル返信送信完了！")

        except Exception as e:
            print(f"❌ 返信送信エラー: {e}")
            print(f"   エラータイプ: {type(e).__name__}")
            import traceback
            print(f"   スタックトレース:\n{traceback.format_exc()}")


def create_google_maps_link(location: str) -> str:
    """
    Googleマップのリンクを生成

    Args:
        location: 場所名

    Returns:
        Googleマップの検索URL
    """
    import urllib.parse
    encoded_location = urllib.parse.quote(location)
    return f"https://www.google.com/maps/search/?api=1&query={encoded_location}"