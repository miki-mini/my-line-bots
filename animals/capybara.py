# ========================================
# 🐹 capybara.py - カピバラさん（ニュース解説）
# Google検索機能付きで最新ニュースを解説
# 語尾は「っぴ」＋絵文字でかわいく！
# ========================================

import datetime as dt
from datetime import timezone, timedelta

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
from pydantic import BaseModel

class CapybaraChatRequest(BaseModel):
    message: str


# Globals
_search_model = None
_text_model = None
JST = timezone(timedelta(hours=9), 'JST')

def register_capybara_handler(app, handler_capybara, configuration_capybara, search_model, text_model):
    global _search_model, _text_model
    _search_model = search_model
    _text_model = text_model
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
    # 🐹 テキストメッセージ処理（検索対応 ＋ ♨️温泉モード）
    # ==========================================
    @handler_capybara.add(MessageEvent, message=TextMessageContent)
    def handle_capybara_message(event):
        user_text = event.message.text
        print(f"🐹 カピバラ受信: {user_text}")

        # 今日の日付を取得 (JST)
        try:
            today = dt.datetime.now(JST).strftime("%Y年%m月%d日")
        except Exception as e:
            today = "今日"

        # ♨️ 温泉モード判定（キーワード検知）
        onsen_keywords = ["疲れた", "つかれた", "しんどい", "休憩", "休みたい", "癒やして", "温泉", "つらい"]
        is_onsen_mode = any(keyword in user_text for keyword in onsen_keywords)

        msg = ""
        try:
            # ♨️ 温泉モード（癒やし優先）
            if is_onsen_mode:
                if text_model:
                    prompt = f"""
ユーザーの発言: {user_text}

役割: あなたは柚子湯に浸かっている、のんびり屋のカピバラです。
目的: 疲れているユーザーを全力で癒やしてください。
ルール:
1. ニュースの話はしないでください。
2. 「動物のほっこりする雑学」を1つ教えてあげるか、優しく労ってください。
3. 語尾は「〜だっぴ」「〜っぴ」で、とてものんびりした口調で。
4. 絵文字（♨️, 🍊, 🧼, 🌿, ☁️, 🐹）を使って、温かい雰囲気にしてください。
"""
                    target_model = text_model if text_model else search_model
                    response = target_model.generate_content(prompt)
                    msg = response.text
                else:
                    msg = "お疲れ様だっぴ...♨️ 背中流すっぴ？🧼"

            # 📰 通常モード（ニュース解説）
            elif search_model:
                prompt = f"""
現在日時: {today}
ユーザーの質問: {user_text}

役割: ニュース解説が得意なカピバラ（語尾はっぴ）。
ルール:
1. Google検索で最新情報を調べて解説する。
2. 絵文字（🐹, ✨, 📝）を使ってかわいく分かりやすく。
3. ユーザーの質問に答えられない場合は、正直に検索できなかったと伝えて。
"""
                response = search_model.generate_content(prompt)
                msg = response.text
            else:
                msg = "ちょっと調子悪いっぴ...💦 ごめんっぴ🐹"

        except Exception as e:
            print(f"❌ カピバラ生成エラー: {e}")
            msg = "エラーが発生したっぴ...🐹"

        # 返信
        with ApiClient(configuration_capybara) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=msg)]
                )
            )

    @app.post("/trigger_morning_news")
    def trigger_morning_news():
        print("☀️ 朝のニュース配信を開始します...")

        try:
            if search_model:
                # JSTで日付取得
                today = dt.datetime.now(JST).strftime("%Y年%m月%d日")

                prompt = f"""
【重要】本日の日付は {today} です。

タスク: 最新の日本や世界のAIニュースを3つピックアップして検索し、解説してください。

【検索のポント】
- 基本的に「今日」や「ここ24時間」のニュースを探してください。
- もし今日 ({today}) のニュースが少なければ、ここ2〜3日以内のニュースでも構いません。
- 「未来のニュースは見つかりません」といった言い訳は不要です。検索で見つかった最新情報を紹介してください。

【厳守事項】
- 1週間以上前の古いニュースは含めないこと
- 1週間以上前のニュースは絶対に含めないこと

【出力フォーマット】
最初の1行目: 必ず以下の文言を一言一句変えずに出力してください（重複はさせないこと）
「はっぴー！今日も元気いっぱいのカピバラさんだよ！🐹🌸 {today}の日本の世界もAIのニュースをチェックするっぴ！📺🤖」

その後:
### 1. [ニュースタイトル] [絵文字]
[本文]
**【カピバラさんからの解説】** [解説]

### 2. [ニュースタイトル] [絵文字]
[本文]
**【カピバラさんからの解説】** [解説]

### 3. [ニュースタイトル] [絵文字]
[本文]
**【カピバラさんからの解説】** [解説]

最終行: 「今日も一日がんばるっぴ！🍊」

【スタイル】
- 役割: カピバラ（語尾は「〜っぴ」）
- 絵文字: 📺, 🤖, 💡, 🐹, 🌸 を適度に使用
- 初心者にも分かりやすく、朝から元気が出る明るい文章
"""
                response = search_model.generate_content(prompt)
                news_text = response.text
            else:
                news_text = "今はニュースが見られないっぴ...💦 ごめんっぴ🐹"

            # 全員に送信
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


# ==========================================
# 🌍 Web API (Router)
# ==========================================
from fastapi import APIRouter

router = APIRouter()

@router.get("/api/capybara/news")
async def get_capybara_news():
    """Webアプリ用: 今日のニュースを取得"""
    global _search_model # グローバル変数を参照
    if not _search_model:
        return {"news": "機能がメンテナンス中だっぴ...🐹 (Model loading)"}

    # JSTで日付取得
    today = dt.datetime.now(JST).strftime("%Y年%m月%d日")

    prompt = f"""
    本日は {today} です。
    今日のAIトレンド、ニュースを3つピックアップして検索してください。

    役割: ニュースキャスターのカピバラ（語尾はっぴ）
    ルール:
    1. タイトルと短い要約で3つ紹介。
    2. 絵文字（📺, 🤖, 📝）を使ってかわいく。
    3. HTML形式（<p>, <ul>など）で返してください。
    """
    try:
        response = _search_model.generate_content(prompt)
        return {"news": response.text}
    except Exception as e:
        return {"news": f"エラーだっぴ... {str(e)}"}

@router.post("/api/capybara/chat")
async def chat_capybara_web(req: CapybaraChatRequest):
    """Webアプリ用: チャット"""
    global _search_model # グローバル変数を参照
    if not _search_model:
        return {"reply": "今は眠いっぴ... (Model Not Loaded)"}

    prompt = f"""
    ユーザーの質問: {req.message}
    役割: 物知りなカピバラ（語尾はっぴ）。
    ルール: 最新情報をGoogle検索して答えてください。
    """
    try:
        response = _search_model.generate_content(prompt)
        return {"reply": response.text}
    except Exception as e:
        return {"reply": "うまく調べられなかったっぴ...💦"}
