# ========================================
# 🦫 まめなビーバー - メモ・リマインダーBot
# ========================================
import json
import re
from datetime import datetime, timedelta

from fastapi import Request, HTTPException
from pydantic import BaseModel
from typing import Optional

from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    PushMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent, ImageMessageContent
from linebot.v3.exceptions import InvalidSignatureError

import google.generativeai as genai
from google.cloud import firestore


# ========================================
# グローバル変数（register時に設定）
# ========================================
_db = None
_db = None
_text_model = None
_configuration = None

# ========================================
# API Router definition
# ========================================
from fastapi import APIRouter
router = APIRouter()



# ========================================
# Pydantic モデル
# ========================================
class MemoRequest(BaseModel):
    user_id: str
    memo_text: str
    reminder_time: Optional[str] = None


# ========================================
# メイン登録関数
# ========================================
def register_beaver_handler(app, handler, configuration, db, text_model=None):
    """
    ビーバーボットのハンドラーを登録する

    Args:
        app: FastAPIアプリケーション
        handler: LINE WebhookHandler
        configuration: LINE Configuration
        db: Firestore client
        text_model: Geminiモデル（オプション）
    """
    global _db, _text_model, _configuration
    _db = db
    _text_model = text_model
    _configuration = configuration

    # ========================================
    # Webhook エンドポイント
    # ========================================
    @app.post("/callback/beaver")
    async def callback_beaver(request: Request):
        signature = request.headers.get("X-Line-Signature", "")
        body = await request.body()
        body_text = body.decode()

        try:
            handler.handle(body_text, signature)
        except InvalidSignatureError:
            print("🦫 ❌ 署名エラー")
            raise HTTPException(status_code=400, detail="Invalid signature")
        except Exception as e:
            print(f"🦫 ❌ /callback/beaver エラー: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

        return "OK"

    # ========================================
    # 画像メッセージ処理（プリント解析）
    # ========================================
    @handler.add(MessageEvent, message=ImageMessageContent)
    def handle_beaver_image(event):
        print(f"🦫 📸 画像を受信 ID: {event.message.id}")
        message_id = event.message.id
        user_id = event.source.user_id

        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_blob_api = MessagingApiBlob(api_client)

            try:
                # 1. 画像ダウンロード
                print("🦫 📥 画像ダウンロード中...")
                image_content = line_bot_blob_api.get_message_content(message_id)
                print(f"🦫 ✅ ダウンロード完了！ ({len(image_content)} bytes)")

                # MIMEタイプ判定
                mime_type = "image/jpeg"
                if image_content.startswith(b"\x89PNG"):
                    mime_type = "image/png"

                # 2. Geminiで解析
                model_name = "gemini-2.5-flash"
                print(f"🦫 🤖 {model_name} に送信...")
                model_flash = genai.GenerativeModel(model_name)

                today_str = datetime.now().strftime("%Y-%m-%d")

                prompt = f"""
                この画像を分析し、学校や地域のプリントに書かれている「重要なイベント」や「提出期限」を抽出してください。

                【重要なルール】
                1. 本日（{today_str}）より過去の日付は、たとえ記載があっても絶対に除外してください。
                2. 「印刷日」「発行日」「作成日」などの事務的な日付は除外してください。
                3. 年が省略されている場合は、適切な年（今年または来年）を補完してください。

                【出力形式】JSON形式のみ（Markdown記号なし）:
                [
                  {{"date": "YYYY-MM-DD", "content": "イベント内容"}}
                ]
                """

                image_data = {"mime_type": mime_type, "data": image_content}
                response = model_flash.generate_content([prompt, image_data])

                # JSONパース
                cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
                try:
                    events_list = json.loads(cleaned_text)
                except:
                    match = re.search(r"\[.*\]", cleaned_text, re.DOTALL)
                    if match:
                        events_list = json.loads(match.group())
                    else:
                        print("🦫 ⚠️ JSONパース失敗")
                        events_list = []

                # 3. 結果処理
                if not events_list:
                    reply_text = "プリントを読んだけど、これからの予定は見つからなかったでヤンス...🦫"
                else:
                    saved_count = 0
                    reply_lines = ["📸 これからの予定を整理したでヤンス！🪵\n"]

                    for item in events_list:
                        event_date = item.get("date")
                        content = item.get("content")

                        if event_date and content:
                            doc_data = {
                                "user_id": user_id,
                                "text": f"【プリント】{content}",
                                "reminder_time": f"{event_date} 08:00",
                                "timestamp": firestore.SERVER_TIMESTAMP,
                            }
                            if _db:
                                _db.collection("memos").add(doc_data)
                            saved_count += 1
                            reply_lines.append(f"📅 {event_date}: {content}")

                    if saved_count > 0:
                        reply_lines.append(f"\n計{saved_count}件を登録したでヤンス！")
                        reply_text = "\n".join(reply_lines)
                    else:
                        reply_text = "有効な予定が見つからなかったでヤンス...🦫"

            except Exception as e:
                print(f"🦫 ❌ エラー発生: {e}")
                reply_text = "画像の読み取りに失敗したでヤンス...🦫💦"

            # 返信
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text)],
                )
            )

    # ========================================
    # テキストメッセージ処理
    # ========================================
    @handler.add(MessageEvent, message=TextMessageContent)
    def handle_beaver_message(event):
        user_text = event.message.text.strip()
        user_id = event.source.user_id

        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            reply_text = ""

            try:
                # 🆔 0. ID確認
                if user_text in ["ID", "id", "ID教えて", "自分のID"]:
                     reply_text = f"あなたのIDだでヤンス！\n\n{user_id}\n\nこれをコピーしてWebアプリに入れるでヤンス！"

                # 📝 1. メモ一覧・予定一覧
                elif user_text in ["メモ一覧", "予定一覧", "スケジュール"]:
                    reply_text = _get_memo_list(user_id)

                # 🗑️ 2. メモ削除
                elif user_text.startswith("メモ削除"):
                    reply_text = _delete_memos(user_id, user_text)

                # 📝 3. その他（AI自動判断：メモ or 雑談）
                else:
                    reply_text = _process_memo_or_chat(user_id, user_text)

            except Exception as e:
                print(f"🦫 ❌ エラー: {e}")
                reply_text = f"エラーだでヤンス...💦 {str(e)}"

            if reply_text:
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=reply_text)],
                    )
                )

    # ========================================
    # API エンドポイント群（GAS連携用）
    # ========================================
    print("🦫 ビーバーハンドラー登録完了")


# ========================================
# API エンドポイント群（Router）
# ========================================
@router.post("/add-memo")
async def add_memo(r: MemoRequest):
    if _db:
        _db.collection("memos").add({
            "user_id": r.user_id,
            "text": r.memo_text,
            "reminder_time": r.reminder_time,
            "timestamp": firestore.SERVER_TIMESTAMP,
        })
    return {"status": "success"}

@router.get("/get-memos/{user_id}")
async def get_memos(user_id: str):
    if not _db:
        return {"memos": []}
    docs = _db.collection("memos").where("user_id", "==", user_id).stream()
    return {
        "memos": [
            {
                "memo_id": d.id,
                "text": d.to_dict().get("text"),
                "reminder_time": d.to_dict().get("reminder_time"),
            }
            for d in docs
        ]
    }

@router.delete("/delete-memo/{memo_id}")
async def delete_memo(memo_id: str):
    if _db:
        _db.collection("memos").document(memo_id).delete()
    return {"status": "success"}

    @app.get("/get-due-memos")
    def get_due_memos():
        """時間になったメモを取得（GASの5分タイマー用）"""
        now = datetime.now() + timedelta(hours=9)
        current_time = now.strftime("%Y-%m-%d %H:%M")

        print(f"🦫 ⏰ チェック中... 現在 {current_time} 以前の予定を探します")

        if not _db:
            return {"due_memos": []}

        try:
            docs = _db.collection("memos").stream()
            due_memos = []

            for doc in docs:
                data = doc.to_dict()
                reminder_time = data.get("reminder_time", "")

                if (
                    reminder_time
                    and reminder_time != "NO_TIME"
                    and reminder_time <= current_time
                ):
                    due_memos.append({
                        "memo_id": doc.id,
                        "user_id": data.get("user_id"),
                        "text": data.get("text"),
                    })

            if due_memos:
                print(f"🦫 🔔 {len(due_memos)}件の通知を見つけました！")

            return {"due_memos": due_memos}

        except Exception as e:
            print(f"🦫 ❌ エラー: {e}")
            return {"due_memos": []}

    @app.get("/get-daily-summary-memos")
    async def get_daily_summary_memos():
        """日次要約用のメモ取得（GASの日次タイマー用）"""
        if not _db:
            return {"memos_by_user": {}}

        # reminder_time が空文字のものを検索（日次要約用）
        docs = _db.collection("memos").where("reminder_time", "==", "").stream()
        memos = {}

        for d in docs:
            uid = d.to_dict().get("user_id")
            if uid:
                memos.setdefault(uid, []).append({
                    "memo_id": d.id,
                    "text": d.to_dict().get("text")
                })

        return {"memos_by_user": memos}

    @app.get("/trigger-check-reminders")
    def trigger_check_reminders():
        """前日・当日の予定を通知（GASの朝タイマー用）"""
        import datetime as dt

        if not _db:
            raise HTTPException(status_code=500, detail="No DB")

        try:
            jst = dt.timezone(dt.timedelta(hours=+9), "JST")
            now = dt.datetime.now(jst)
            today = now.strftime("%Y-%m-%d")
            tomorrow = (now + dt.timedelta(days=1)).strftime("%Y-%m-%d")

            notifications = {}
            docs = _db.collection("memos").stream()

            for doc in docs:
                data = doc.to_dict()
                uid = data.get("user_id")
                r_time = data.get("reminder_time", "")
                text = data.get("text", "")

                if not uid or not r_time:
                    continue

                date_part = r_time.split(" ")[0]
                if date_part == today:
                    notifications.setdefault(uid, []).append(f"🔴【今日】: {text}")
                elif date_part == tomorrow:
                    notifications.setdefault(uid, []).append(f"🟡【明日】: {text}")

            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                for uid, msgs in notifications.items():
                    push_text = "🦫 ビーバー通知でヤンス！\n\n" + "\n".join(msgs)
                    try:
                        line_bot_api.push_message(
                            PushMessageRequest(
                                to=uid, messages=[TextMessage(text=push_text)]
                            )
                        )
                    except:
                        pass

            return {"status": "ok", "count": len(notifications)}

        except Exception as e:
            print(f"🦫 ❌ Check Error: {e}")
            return {"error": str(e)}

    @app.get("/check_reminders")
    def check_reminders():
        """明日の予定をチェックして通知"""
        import datetime as dt

        print("🦫 ⏰ リマインダーチェック開始...")

        tomorrow = dt.date.today() + dt.timedelta(days=1)
        tomorrow_str = tomorrow.strftime("%Y-%m-%d")
        target_time = f"{tomorrow_str} 08:00"

        print(f"🦫 🔍 検索対象の日時: {target_time}")

        if not _db:
            return {"status": "error", "message": "DB未接続"}

        try:
            docs = _db.collection("memos").where("reminder_time", "==", target_time).stream()

            count = 0
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)

                for doc in docs:
                    data = doc.to_dict()
                    user_id = data.get("user_id")
                    text = data.get("text")

                    if user_id and text:
                        print(f"🦫 📩 送信中: {user_id} -> {text}")
                        line_bot_api.push_message(
                            PushMessageRequest(
                                to=user_id,
                                messages=[
                                    TextMessage(text=f"明日の予定でヤンス！🦫\n\n{text}")
                                ],
                            )
                        )
                        count += 1

            return {"status": "success", "sent_count": count}

        except Exception as e:
            print(f"🦫 ❌ リマインダーエラー: {e}")
            return {"status": "error", "message": str(e)}

    print("🦫 ビーバーハンドラー登録完了")


# ========================================
# 内部ヘルパー関数
# ========================================
def _get_memo_list(user_id: str) -> str:
    """メモ一覧を取得"""
    if not _db:
        return "データベースに接続できないでヤンス...💦"

    docs = (
        _db.collection("memos")
        .where("user_id", "==", user_id)
        .order_by("timestamp")
        .stream()
    )

    memos = []
    for i, doc in enumerate(docs):
        data = doc.to_dict()
        text = data.get("text", "")
        display_text = text[:20] + "..." if len(text) > 20 else text
        date_info = data.get("reminder_time", "日時なし")
        memos.append(f"{i+1}. [{date_info}] {display_text}")

    if memos:
        return (
            "🦫 予定一覧でヤンス！\n\n"
            + "\n".join(memos)
            + "\n\n削除したい時は「メモ削除 1」のように番号で教えてヤンス！"
        )
    else:
        return "予定は空っぽでヤンス！🦫"


def _delete_memos(user_id: str, user_text: str) -> str:
    """メモを削除（複数対応）"""
    try:
        input_str = (
            user_text.replace("メモ削除", "")
            .replace(",", " ")
            .replace("、", " ")
        )

        target_indices = []
        for s in input_str.split():
            if s.strip().isdigit():
                target_indices.append(int(s) - 1)

        if not target_indices:
            raise ValueError("数字が見つかりません")

        docs = list(
            _db.collection("memos")
            .where("user_id", "==", user_id)
            .order_by("timestamp")
            .stream()
        )

        deleted_numbers = []
        for index in target_indices:
            if 0 <= index < len(docs):
                docs[index].reference.delete()
                deleted_numbers.append(str(index + 1))

        if deleted_numbers:
            deleted_str = ", ".join(deleted_numbers)
            return f"🗑️ {deleted_str}番のメモをまとめて削除したでヤンス！"
        else:
            return "指定された番号のメモは見つからなかったでヤンス...🦫"

    except:
        return "削除したい番号を「メモ削除 1 3」のように教えてほしいでヤンス！"


def _process_memo_or_chat(user_id: str, user_text: str) -> str:
    """AI自動判断：メモ登録 or 雑談"""
    print(f"🦫 🤖 AI自動判断を実行: {user_text}")

    now_str = (datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")

    prompt = f"""
    現在日時: {now_str}
    ユーザーの入力: {user_text}

    あなたは「まめなビーバー」です。
    ユーザーの入力が「予定」なのか「雑談」なのかを判断し、以下のJSON形式のみで答えてください。Markdown記号は不要です。

    【重要：キャラクター設定】
    * 語尾には必ず「〜でヤンス」や「〜ヤンス」をつけて話してください。
    * 絵文字（🦫, 🪵, 📅, 📝, 💦, ✨など）をふんだんに使って、親しみやすいビーバーとして振る舞ってください。
    * 雑談の返事 ("content") も、この口調で生成してください。

    【ルール】
    1. 「5分後」「明日12時」などの時間表現があれば、現在日時から計算して "reminder_time" に "YYYY-MM-DD HH:MM" 形式で入れてください。
    2. 「12月23日」「来週月曜」など、日付のみで時間が指定されていない場合は、その日付の "08:00" にセットしてください。（例: "2025-12-23 08:00"）
    3. 日時が全く指定されていないただのメモの場合は、"reminder_time" を "NO_TIME" にしてください。
    4. 予定ではなく、ただの挨拶や雑談の場合は "is_memo" を false にしてください。
    5. "content" には、予定の内容（または雑談の返事）を入れてください。雑談の返事はキャラクター設定に従ってください。

    【出力JSON形式】
    {{
        "is_memo": true または false,
        "reminder_time": "YYYY-MM-DD HH:MM" または "NO_TIME",
        "content": "予定の内容、または雑談の返信テキスト"
    }}
    """

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    cleaned_text = response.text.replace("```json", "").replace("```", "").strip()

    try:
        data = json.loads(cleaned_text)
        is_memo = data.get("is_memo", False)
        reminder_time = data.get("reminder_time", "NO_TIME")
        content = data.get("content", "")

        if is_memo:
            doc_data = {
                "user_id": user_id,
                "text": content,
                "reminder_time": "" if reminder_time == "NO_TIME" else reminder_time,
                "timestamp": firestore.SERVER_TIMESTAMP,
            }
            if _db:
                _db.collection("memos").add(doc_data)

            if reminder_time != "NO_TIME":
                return f"🦫 ガッテンでヤンス！\n「{content}」を【{reminder_time}】に通知するでヤンス！⏰"
            else:
                return f"🦫 メモしたでヤンス！\n「{content}」"
        else:
            return content

    except Exception as e:
        print(f"🦫 JSONパース失敗: {e}")
        return "うまく聞き取れなかったでヤンス...🦫💦"

@router.get("/get-due-memos")
def get_due_memos():
    """時間になったメモを取得（GASの5分タイマー用）"""
    now = datetime.now() + timedelta(hours=9)
    current_time = now.strftime("%Y-%m-%d %H:%M")

    print(f"🦫 ⏰ チェック中... 現在 {current_time} 以前の予定を探します")

    if not _db:
        return {"due_memos": []}

    try:
        docs = _db.collection("memos").stream()
        due_memos = []

        for doc in docs:
            data = doc.to_dict()
            reminder_time = data.get("reminder_time", "")

            if (
                reminder_time
                and reminder_time != "NO_TIME"
                and reminder_time <= current_time
            ):
                due_memos.append({
                    "memo_id": doc.id,
                    "user_id": data.get("user_id"),
                    "text": data.get("text"),
                })

        if due_memos:
            print(f"🦫 🔔 {len(due_memos)}件の通知を見つけました！")

        return {"due_memos": due_memos}

    except Exception as e:
        print(f"🦫 ❌ エラー: {e}")
        return {"due_memos": []}

@router.get("/get-daily-summary-memos")
async def get_daily_summary_memos():
    """日次要約用のメモ取得（GASの日次タイマー用）"""
    if not _db:
        return {"memos_by_user": {}}

    # reminder_time が空文字のものを検索（日次要約用）
    docs = _db.collection("memos").where("reminder_time", "==", "").stream()
    memos = {}

    for d in docs:
        uid = d.to_dict().get("user_id")
        if uid:
            memos.setdefault(uid, []).append({
                "memo_id": d.id,
                "text": d.to_dict().get("text")
            })

    return {"memos_by_user": memos}

@router.get("/trigger-check-reminders")
def trigger_check_reminders():
    """前日・当日の予定を通知（GASの朝タイマー用）"""
    import datetime as dt

    # Check if _configuration is available
    if not _db:
        raise HTTPException(status_code=500, detail="No DB")

    try:
        jst = dt.timezone(dt.timedelta(hours=+9), "JST")
        now = dt.datetime.now(jst)
        today = now.strftime("%Y-%m-%d")
        tomorrow = (now + dt.timedelta(days=1)).strftime("%Y-%m-%d")

        notifications = {}
        docs = _db.collection("memos").stream()

        for doc in docs:
            data = doc.to_dict()
            uid = data.get("user_id")
            r_time = data.get("reminder_time", "")
            text = data.get("text", "")

            if not uid or not r_time:
                continue

            date_part = r_time.split(" ")[0]
            if date_part == today:
                notifications.setdefault(uid, []).append(f"🔴【今日】: {text}")
            elif date_part == tomorrow:
                notifications.setdefault(uid, []).append(f"🟡【明日】: {text}")

        if _configuration:
             with ApiClient(_configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                for uid, msgs in notifications.items():
                    push_text = "🦫 ビーバー通知でヤンス！\n\n" + "\n".join(msgs)
                    try:
                        line_bot_api.push_message(
                            PushMessageRequest(
                                to=uid, messages=[TextMessage(text=push_text)]
                            )
                        )
                    except:
                        pass

        return {"status": "ok", "count": len(notifications)}

    except Exception as e:
        print(f"🦫 ❌ Check Error: {e}")
        return {"error": str(e)}

@router.get("/check_reminders")
def check_reminders():
    """明日の予定をチェックして通知"""
    import datetime as dt

    print("🦫 ⏰ リマインダーチェック開始...")

    tomorrow = dt.date.today() + dt.timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    target_time = f"{tomorrow_str} 08:00"

    print(f"🦫 🔍 検索対象の日時: {target_time}")

    if not _db:
        return {"status": "error", "message": "DB未接続"}

    try:
        docs = _db.collection("memos").where("reminder_time", "==", target_time).stream()

        count = 0
        if _configuration:
            with ApiClient(_configuration) as api_client:
                line_bot_api = MessagingApi(api_client)

                for doc in docs:
                    data = doc.to_dict()
                    user_id = data.get("user_id")
                    text = data.get("text")

                    if user_id and text:
                        print(f"🦫 📩 送信中: {user_id} -> {text}")
                        line_bot_api.push_message(
                            PushMessageRequest(
                                to=user_id,
                                messages=[
                                    TextMessage(text=f"明日の予定でヤンス！🦫\n\n{text}")
                                ],
                            )
                        )
                        count += 1

        return {"status": "success", "sent_count": count}

    except Exception as e:
        print(f"🦫 ❌ リマインダーエラー: {e}")
        return {"status": "error", "message": str(e)}