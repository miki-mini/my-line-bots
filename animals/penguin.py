"""
penguin.py - スーパー秘書ペンギンのメール送信 & コンシェルジュBOT（カルーセル版）
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
    CarouselTemplate,  # 追加！
    CarouselColumn,  # 追加！
    PostbackAction,
    URIAction,
)
from linebot.v3.webhooks import MessageEvent, PostbackEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError
from fastapi import Request, HTTPException

# ユーザーごとのメール下書きを一時保存
pending_emails = {}


def register_penguin_handler(app, handler_penguin, configuration_penguin, text_model):

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
        user_id = event.source.user_id
        user_message = event.message.text

        try:
            if user_message.startswith("メール："):
                handle_email_request(
                    event, user_message, user_id, configuration_penguin, text_model
                )

            elif user_message.startswith(("お店：", "接待：", "手土産：")):
                handle_concierge_request(
                    event, user_message, configuration_penguin, text_model
                )

            else:
                reply_text = """🐧 スーパー秘書ペンギンだペン！

【メール作成】
「メール：宛先」で始めてペン！

【お店・手土産探し】
「お店：新宿で焼肉デート」
「接待：大阪で静かな和食」
みたいに話しかけてペン！カードで提案するペン！✨"""
                reply_simple_message(
                    event.reply_token, reply_text, configuration_penguin
                )

        except Exception as e:
            print(f"❌ エラー: {e}")
            import traceback

            print(traceback.format_exc())
            reply_simple_message(
                event.reply_token, "エラーが起きたペン...💦", configuration_penguin
            )

    @handler_penguin.add(PostbackEvent)
    def handle_penguin_postback(event):
        user_id = event.source.user_id
        data = event.postback.data

        if data == "action=cancel":
            if user_id in pending_emails:
                del pending_emails[user_id]
            reply_simple_message(
                event.reply_token, "送信を中止したペン！🗑️", configuration_penguin
            )

        elif data == "action=send":
            email_data = pending_emails.get(user_id)
            if not email_data:
                reply_simple_message(
                    event.reply_token,
                    "タイムアウトしちゃったペン💦",
                    configuration_penguin,
                )
                return

            success, msg = send_email_via_gas(
                email_data["to"], email_data["subject"], email_data["body"]
            )
            if success:
                del pending_emails[user_id]
                reply_simple_message(
                    event.reply_token, "✅ 送信完了だペン！🐧✨", configuration_penguin
                )
            else:
                reply_simple_message(
                    event.reply_token,
                    f"❌ 送信失敗だペン...💦\n{msg}",
                    configuration_penguin,
                )


# ---------------------------------------------------------
# ロジック関数群
# ---------------------------------------------------------


def handle_email_request(event, text, user_id, conf, model):
    parts = text.split("\n")
    if len(parts) < 3:
        reply_simple_message(
            event.reply_token,
            "形式が違うペン💦\nメール：宛先\n件名\n本文\nの順で頼むペン！",
            conf,
        )
        return

    target_email = parts[0].replace("メール：", "").strip()
    raw_subject = parts[1].strip()
    raw_body = "\n".join(parts[2:])

    subject, body = call_gemini_email(raw_subject, raw_body, model)
    pending_emails[user_id] = {"to": target_email, "subject": subject, "body": body}

    confirm_msg = TemplateMessage(
        alt_text="メール確認",
        template=ButtonsTemplate(
            title="メール確認だペン🐧",
            text=f"【件名】{subject[:20]}...",
            actions=[
                PostbackAction(
                    label="送信する 🚀", display_text="送信する！", data="action=send"
                ),
                PostbackAction(
                    label="キャンセル ❌", display_text="やめる", data="action=cancel"
                ),
            ],
        ),
    )

    with ApiClient(conf) as c:
        api = MessagingApi(c)
        api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text=f"下書きしたペン！\n\n【件名】\n{subject}\n\n【本文】\n{body}"
                    ),
                    confirm_msg,
                ],
            )
        )


def handle_concierge_request(event, text, conf, model):
    """お店選び（カルーセル表示版）"""
    query = (
        text.replace("お店：", "").replace("接待：", "").replace("手土産：", "").strip()
    )

    # Geminiから「3つのリスト」をもらう
    shops_list, intro_msg = call_gemini_concierge_list(query, model)

    if not shops_list:
        reply_simple_message(
            event.reply_token, "ごめんペン、うまく探せなかったペン...💦", conf
        )
        return

    # カルーセルの列（カラム）を作成
    columns = []
    for shop in shops_list:
        # 地図のURLを作る
        map_query = urllib.parse.quote(shop["search_keyword"])
        map_url = f"https://www.google.com/maps/search/?api=1&query={map_query}"

        # 説明文が長すぎるとエラーになるので60文字でカット
        desc = shop["description"][:60]
        if len(shop["description"]) > 60:
            desc += "..."

        columns.append(
            CarouselColumn(
                title=shop["name"][:40],  # タイトル制限40文字
                text=desc,  # 本文制限60文字
                actions=[URIAction(label="地図を見る 🗺️", uri=map_url)],
            )
        )

    # カルーセルメッセージを作成
    carousel_msg = TemplateMessage(
        alt_text="おすすめのお店リスト", template=CarouselTemplate(columns=columns)
    )

    with ApiClient(conf) as c:
        api = MessagingApi(c)
        api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text=intro_msg),  # 「候補を見つけたペン！」などの挨拶
                    carousel_msg,
                ],
            )
        )


def call_gemini_email(raw_subject, raw_body, model):
    try:
        import google.generativeai as genai

        use_model = model if model else genai.GenerativeModel("gemini-2.5-flash")
        prompt = f"""
        以下のメールをビジネスメールとして修正しJSONで出力。
        {{ "subject": "...", "body": "..." }}
        元件名: {raw_subject}
        元本文: {raw_body}
        """
        res = use_model.generate_content(prompt)
        text = res.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        return data["subject"], data["body"]
    except:
        return raw_subject, raw_body


def call_gemini_concierge_list(query, model):
    """
    コンシェルジュ用Gemini（リスト形式で出力させる）
    Returns: (list_of_shops, intro_message)
    """
    try:
        import google.generativeai as genai

        use_model = model if model else genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
        あなたは秘書です。以下のリクエストにおすすめのお店/手土産を3つ提案してください。
        リクエスト: 「{query}」

        【出力形式】
        必ず以下のJSONフォーマットのみを出力してください。

        {{
            "intro": "上司、候補を3つピックアップしました！などの短い挨拶",
            "shops": [
                {{
                    "name": "店名（短く）",
                    "description": "特徴やおすすめ理由を簡潔に（50文字以内）",
                    "search_keyword": "Googleマップ検索用キーワード"
                }},
                {{ ... }},
                {{ ... }}
            ]
        }}
        """
        res = use_model.generate_content(prompt)
        text = res.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        return data["shops"], data["intro"]
    except Exception as e:
        print(f"Concierge Error: {e}")
        return [], "エラーだペン..."


def reply_simple_message(token, text, conf):
    with ApiClient(conf) as c:
        MessagingApi(c).reply_message(
            ReplyMessageRequest(reply_token=token, messages=[TextMessage(text=text)])
        )


def send_email_via_gas(to, sub, body):
    url = os.environ.get("GAS_MAIL_WEB_APP_URL")
    if not url:
        return False, "URL未設定"
    try:
        res = requests.post(
            url, json={"to": to, "subject": sub, "body": body}, timeout=10
        )
        return (True, "OK") if res.status_code in [200, 302] else (False, res.text)
    except Exception as e:
        return False, str(e)
