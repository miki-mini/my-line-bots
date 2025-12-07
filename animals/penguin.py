"""
penguin.py - スーパー秘書ペンギンのメール送信 & コンシェルジュBOT
"""

import os
import requests
import json
import urllib.parse
from linebot.v3.messaging import (
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    TemplateMessage,
    ButtonsTemplate,
    PostbackAction,
    URIAction
)
from linebot.v3.webhook import MessageEvent, PostbackEvent
from linebot.v3.webhooks import TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError
from fastapi import Request, HTTPException

# ユーザーごとのメール下書きを一時保存
pending_emails = {}

def register_penguin_handler(app, handler_penguin, configuration_penguin, text_model):
    """
    ペンギンのハンドラーを登録
    """

    @app.post("/callback_penguin")
    async def callback_penguin(request: Request):
        signature = request.headers.get("X-Line-Signature")
        body = await request.body()
        try:
            handler_penguin.handle(body.decode("utf-8"), signature)
        except InvalidSignatureError:
            raise HTTPException(status_code=400, detail="Invalid signature")
        except Exception as e:
            print(f"🐧❌ handler エラー: {e}")
            import traceback
            print(traceback.format_exc())
        return {"status": "ok"}

    @handler_penguin.add(MessageEvent, message=TextMessageContent)
    def handle_penguin_message(event):
        """メッセージ受信時の処理"""
        user_id = event.source.user_id
        user_message = event.message.text

        try:
            # -------------------------------------------
            # 機能1：メール作成（メール：〜）
            # -------------------------------------------
            if user_message.startswith("メール："):
                handle_email_request(event, user_message, user_id, configuration_penguin, text_model)

            # -------------------------------------------
            # 機能2：お店・手土産選び（お店：〜 / 接待：〜 / 手土産：〜）
            # -------------------------------------------
            elif user_message.startswith(("お店：", "接待：", "手土産：")):
                handle_concierge_request(event, user_message, configuration_penguin, text_model)

            # -------------------------------------------
            # その他：使い方の説明
            # -------------------------------------------
            else:
                reply_text = """🐧 スーパー秘書ペンギンだペン！

【できること】
📧 メールの下書き
「メール：宛先」で始めてペン！

🍽️ お店・手土産の相談
「お店：新宿で焼肉デート」
「接待：大阪で静かな和食」
「手土産：甘くないもの 3000円」

みたいに話しかけてペン！私が探すペン！✨"""
                reply_simple_message(event.reply_token, reply_text, configuration_penguin)

        except Exception as e:
            print(f"❌ エラー: {e}")
            import traceback
            print(traceback.format_exc())
            reply_simple_message(event.reply_token, "エラーが起きたペン...💦", configuration_penguin)

    @handler_penguin.add(PostbackEvent)
    def handle_penguin_postback(event):
        """メール送信確認ボタンの処理"""
        user_id = event.source.user_id
        data = event.postback.data

        if data == "action=cancel":
            if user_id in pending_emails: del pending_emails[user_id]
            reply_simple_message(event.reply_token, "送信を中止したペン！🗑️", configuration_penguin)

        elif data == "action=send":
            email_data = pending_emails.get(user_id)
            if not email_data:
                reply_simple_message(event.reply_token, "タイムアウトしちゃったペン💦 もう一度作ってペン！", configuration_penguin)
                return

            success, msg = send_email_via_gas(email_data["to"], email_data["subject"], email_data["body"])
            if success:
                del pending_emails[user_id]
                reply_simple_message(event.reply_token, "✅ 送信完了だペン！お仕事完了！🐧✨", configuration_penguin)
            else:
                reply_simple_message(event.reply_token, f"❌ 送信失敗だペン...💦\n{msg}", configuration_penguin)


# ---------------------------------------------------------
# ロジック関数群
# ---------------------------------------------------------

def handle_email_request(event, text, user_id, conf, model):
    """メール作成のリクエスト処理"""
    parts = text.split("\n")
    if len(parts) < 3:
        reply_simple_message(event.reply_token, "入力形式が違うペン💦\nメール：宛先\n件名\n本文\nの順で頼むペン！", conf)
        return

    target_email = parts[0].replace("メール：", "").strip()
    raw_subject = parts[1].strip()
    raw_body = "\n".join(parts[2:])

    # Geminiで推敲
    subject, body = call_gemini_email(raw_subject, raw_body, model)

    # 一時保存
    pending_emails[user_id] = {"to": target_email, "subject": subject, "body": body}

    # 確認ボタン送信
    confirm_msg = TemplateMessage(
        alt_text='メール確認',
        template=ButtonsTemplate(
            title='メール確認だペン🐧',
            text=f"【件名】{subject[:20]}...",
            actions=[
                PostbackAction(label='送信する 🚀', display_text='送信する！', data='action=send'),
                PostbackAction(label='修正/キャンセル ❌', display_text='やめる', data='action=cancel')
            ]
        )
    )

    with ApiClient(conf) as c:
        api = MessagingApi(c)
        api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text=f"下書きしたペン！\n\n【件名】\n{subject}\n\n【本文】\n{body}"),
                    confirm_msg
                ]
            )
        )

def handle_concierge_request(event, text, conf, model):
    """お店・手土産選びのリクエスト処理"""
    # キーワードを取り除く（"お店："などを消す）
    query = text.replace("お店：", "").replace("接待：", "").replace("手土産：", "").strip()

    # Geminiでおすすめを考える
    recommendation_text, search_query = call_gemini_concierge(query, model)

    # Googleマップの検索URLを作成
    encoded_query = urllib.parse.quote(search_query)
    map_url = f"https://www.google.com/maps/search/?api=1&query={encoded_query}"

    # LINEで返信（ボタン付き）
    buttons_msg = TemplateMessage(
        alt_text='おすすめのお店',
        template=ButtonsTemplate(
            title='検索結果だペン🔍',
            text='最新情報や場所はここからチェックしてペン！',
            actions=[
                URIAction(label='Googleマップで見る 🗺️', uri=map_url)
            ]
        )
    )

    with ApiClient(conf) as c:
        api = MessagingApi(c)
        api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text=recommendation_text),
                    buttons_msg
                ]
            )
        )

def call_gemini_email(raw_subject, raw_body, model):
    """メール推敲用Gemini"""
    try:
        import google.generativeai as genai
        use_model = model if model else genai.GenerativeModel("gemini-2.5-flash")
        prompt = f"""
        以下のメールをビジネスメールとして修正しJSONで出力してください。
        {{ "subject": "件名", "body": "本文" }}

        元件名: {raw_subject}
        元本文: {raw_body}
        """
        res = use_model.generate_content(prompt)
        text = res.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        return data["subject"], data["body"]
    except:
        return raw_subject, raw_body

def call_gemini_concierge(query, model):
    """
    コンシェルジュ用Gemini
    戻り値: (解説テキスト, 検索用クエリ)
    """
    try:
        import google.generativeai as genai
        use_model = model if model else genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
        あなたは有能な秘書です。上司から以下のリクエストを受けました。
        リクエスト: 「{query}」

        これに対して、おすすめの「お店」または「商品」を3つ提案してください。

        【出力ルール】
        1. 3つの候補を挙げ、それぞれの「名前」「特徴」「おすすめ理由」を簡潔に書く。
        2. 最後に、Googleマップで検索するための「最適な検索キーワード」を1つだけ提案する。
        3. 出力はJSON形式のみ。

        {{
            "message": "（ここに提案文全体を入れる。Markdownで見やすく。絵文字も使って）",
            "search_keyword": "（Googleマップ検索用のキーワード例: 新宿 焼肉 個室）"
        }}
        """
        res = use_model.generate_content(prompt)
        text = res.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        return data["message"], data["search_keyword"]
    except Exception as e:
        print(f"Concierge Error: {e}")
        return "ごめんペン、うまく探せなかったペン...💦", query

def reply_simple_message(token, text, conf):
    with ApiClient(conf) as c:
        MessagingApi(c).reply_message(ReplyMessageRequest(reply_token=token, messages=[TextMessage(text=text)]))

def send_email_via_gas(to, sub, body):
    url = os.environ.get("GAS_MAIL_WEB_APP_URL")
    if not url: return False, "URL未設定"
    try:
        res = requests.post(url, json={"to": to, "subject": sub, "body": body}, timeout=10)
        return (True, "OK") if res.status_code in [200, 302] else (False, res.text)
    except Exception as e: return False, str(e)