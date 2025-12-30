"""
bat.py - テレビコウモリ（チロちゃん）のTV通知BOT
スクレイピング無しで、Geminiの検索機能を使って番組表を確認します。
Firestoreを使って「見たい番組リスト」を動的に管理します。
"""

import os
import datetime
from fastapi import Request, HTTPException
from linebot.v3.messaging import (
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    PushMessageRequest,
    BroadcastRequest
)
from linebot.v3.webhooks import MessageEvent
from linebot.v3.webhooks import TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError
from pydantic import BaseModel

# Firestore Collection Name
COLLECTION_NAME = "tv_watch_lists"

def register_bat_handler(app, handler_bat, configuration_bat, search_model, db):
    """
    テレビコウモリのハンドラーを登録
    Parameters:
        db: Firestore Client
    """

    # ==========================================
    # 🦇 Webhook エンドポイント
    # ==========================================
    @app.post("/callback_bat")
    async def callback_bat(request: Request):
        signature = request.headers.get("X-Line-Signature", "")
        body = await request.body()

        try:
            handler_bat.handle(body.decode("utf-8"), signature)
        except InvalidSignatureError:
            raise HTTPException(status_code=400, detail="Invalid signature")
        except Exception as e:
            print(f"🦇❌ Webhook Error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        return "OK"

    # ==========================================
    # 🦇 メッセージ処理
    # ==========================================
    @handler_bat.add(MessageEvent, message=TextMessageContent)
    def handle_bat_message(event):
        text = event.message.text.strip()
        print(f"🦇 受信: {text}")

        user_id = event.source.user_id
        reply_text = ""

        # --- コマンド処理 ---
        if text.startswith("追加:") or text.startswith("追加："):
            # キーワード追加
            keyword = text.split(":", 1)[1].split("：", 1)[-1].strip()
            if keyword:
                _add_to_watch_list(db, user_id, keyword)
                reply_text = f"🦇 「{keyword}」を監視リストに入れたモリ！\n放送が見つかったら教えるモリ〜📺"
            else:
                reply_text = "🦇 追加したい番組名を入れてモリ！\n例：「追加: ポケモン」"

        elif text.startswith("削除:") or text.startswith("削除："):
            # キーワード削除
            keyword = text.split(":", 1)[1].split("：", 1)[-1].strip()
            if keyword:
                if _remove_from_watch_list(db, user_id, keyword):
                    reply_text = f"🦇 「{keyword}」をリストから消したモリ。"
                else:
                    reply_text = f"🦇 「{keyword}」はリストになかったモリ..."
            else:
                reply_text = "🦇 削除したい番組名を入れてモリ！\n例：「削除: ジブリ」"

        elif text == "リスト" or text == "一覧":
            # リスト確認
            keywords = _get_user_watch_list(db, user_id)
            if keywords:
                list_str = "\n".join([f"・{k}" for k in keywords])
                reply_text = f"🦇 今チェックしてる番組だモリ：\n\n{list_str}"
            else:
                reply_text = "🦇 今は何もチェックしてないモリ。\n「追加: 〇〇」で教えてくれモリ！"

        else:
            # --- 通常会話（検索） ---
            reply_text = _search_tv_schedule_with_gemini(text, search_model)

        # 返信送信
        try:
            with ApiClient(configuration_bat) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=reply_text)]
                    )
                )
        except Exception as e:
            print(f"🦇❌ Reply Error: {e}")


    # ==========================================
    # 🕒 Cron用チェック機能 (動的リスト対応)
    # ==========================================
    @app.get("/cron/bat_check")
    def cron_bat_check():
        """
        全ユーザーの登録キーワードをチェックし、該当があれば通知する。
        """
        print("🦇 Cron: TVスケジュールチェック開始 (Dynamic)...")

        # 1. 全監視キーワードを取得 (重複排除)
        all_keywords = _get_all_unique_keywords(db)
        if not all_keywords:
             print("🦇 監視対象キーワードなし")
             return {"status": "ok", "message": "No keywords to check"}

        found_shows = []

        # 2. キーワードごとに検索
        for keyword in all_keywords:
            # クエリ作成
            # クエリ作成（「今日」に限定）
            today_str = datetime.date.today().strftime("%Y年%m月%d日")
            query = f"今日は{today_str}です。今日、地上波テレビで「{keyword}」の放送予定はある？"

            # 検索チェック
            result_text = _check_schedule_strict(keyword, query, search_model)

            if result_text:
                found_shows.append(result_text)

        if not found_shows:
            print("🦇 今回は特に放送予定なし")
            return {"status": "ok", "message": "No shows found"}

        # 3. 通知（簡易実装：全員にブロードキャスト）
        # ※本来は「そのキーワードを登録している人」だけに送るべきだが、
        #   個人の趣味開発レベルなら全員に教えてあげても共有になって楽しいので
        #   あえてBroadcastで実装します。

        push_text = "🦇 キキキ...監視中の番組が見つかったモリ！📺\n\n" + "\n\n".join(found_shows)

        try:
            with ApiClient(configuration_bat) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.broadcast(
                    BroadcastRequest(messages=[TextMessage(text=push_text)])
                )
            print("🦇 ブロードキャスト送信完了")
        except Exception as e:
            print(f"🦇❌ Broadcast Error: {e}")
            return {"status": "error", "detail": str(e)}

        return {"status": "ok", "message": f"Sent notifications for: {len(found_shows)} shows"}

    # ==========================================
    # 🦇 Web App API (Watchlist Management)
    # ==========================================

    class WatchListRequest(BaseModel):
        user_id: str
        keyword: str

    @app.get("/api/bat/keywords/{user_id}")
    async def get_bat_keywords(user_id: str):
        keywords = _get_user_watch_list(db, user_id)
        return {"keywords": keywords}

    @app.post("/api/bat/keywords")
    async def add_bat_keyword(req: WatchListRequest):
        _add_to_watch_list(db, req.user_id, req.keyword)
        return {"status": "success", "keyword": req.keyword}

    @app.delete("/api/bat/keywords")
    async def remove_bat_keyword(req: WatchListRequest):
        if _remove_from_watch_list(db, req.user_id, req.keyword):
            return {"status": "success", "keyword": req.keyword}
        else:
            return {"status": "not_found", "message": "Keyword not in list"}


# ==========================================
# 🔥 Firestore ヘルパー関数
# ==========================================
def _add_to_watch_list(db, user_id, keyword):
    """リストにキーワードを追加（Setで重複防ぐ）"""
    if not db: return
    doc_ref = db.collection(COLLECTION_NAME).document(user_id)
    doc = doc_ref.get()

    current_list = []
    if doc.exists:
        current_list = doc.to_dict().get("keywords", [])

    if keyword not in current_list:
        current_list.append(keyword)
        doc_ref.set({"keywords": current_list}, merge=True)
        print(f"🦇 Firestore: Added {keyword} for {user_id}")

def _remove_from_watch_list(db, user_id, keyword):
    """リストから削除"""
    if not db: return False
    doc_ref = db.collection(COLLECTION_NAME).document(user_id)
    doc = doc_ref.get()

    if doc.exists:
        current_list = doc.to_dict().get("keywords", [])
        if keyword in current_list:
            current_list.remove(keyword)
            doc_ref.set({"keywords": current_list}, merge=True)
            print(f"🦇 Firestore: Removed {keyword} for {user_id}")
            return True
    return False

def _get_user_watch_list(db, user_id):
    """ユーザーのリスト取得"""
    if not db: return []
    doc_ref = db.collection(COLLECTION_NAME).document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict().get("keywords", [])
    return []

def _get_all_unique_keywords(db):
    """全ユーザーのキーワードを重複なしで取得"""
    if not db: return []
    keywords_set = set()
    docs = db.collection(COLLECTION_NAME).stream()
    for doc in docs:
        user_keywords = doc.to_dict().get("keywords", [])
        for k in user_keywords:
            keywords_set.add(k)

    # デフォルトも混ぜておく（誰かが消しても最低限チェックするため）
    defaults = ["ジブリ", "ホーム・アローン"]
    for d in defaults:
        keywords_set.add(d)

    return list(keywords_set)


# ==========================================
# 🧠 Gemini Logic (Existing)
# ==========================================
def _search_tv_schedule_with_gemini(user_text, search_model):
    """
    ユーザーの自由な質問に対して、Gemini検索を使って答える
    """
    if not search_model:
        return "🦇 ごめんモリ...今、目が悪くて検索できないモリ...（モデル未設定）"

    prompt = f"""
    あなたは「テレビコウモリ（チロちゃん）」という妖怪キャラクターです。
    ユーザーからのテレビ番組に関する質問に答えてください。

    【キャラクター設定】
    - 語尾は「〜モリ」「〜キキ」などを使う。
    - 夜行性で、テレビが大好き。
    - 少し毒舌だが、親切に教えてくれる。

    【ユーザーの質問】
    {user_text}

    【指示】
    - Google検索ツールを使って、最新の日本のテレビ番組表情報を調べてください。
    - 特に「地上波」の情報を優先してください。
    - 放送日時、放送局、簡単なあらすじを含めて教えてください。
    - もし放送予定がなさそうな場合は、正直に「見つからないモリ」と答えてください。
    """

    try:
        response = search_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"🦇❌ Gemini Search Error: {e}")
        return "🦇 電波が悪くて調べられないモリ...また後で聞いてくれモリ。"


def _check_schedule_strict(keyword, query, search_model):
    """
    特定のキーワード番組があるか厳密にチェックし、ある場合のみテキストを返す
    """
    if not search_model:
        return None

    prompt = f"""
    以下の質問についてGoogle検索を行い、その結果に基づいて、
    「{keyword}」の放送予定が **今日** あるかどうか判断してください。

    質問: {query}

    【ルール】
    - 放送予定が **明確に「今日」ある場合のみ**、その詳細（日時・放送局・タイトル）を
      「100文字以内の通知用テキスト」として出力してください。
    - 来週や明日など、「今日」でない場合は「False」とだけ出力してください。
      「False」とだけ出力してください。
    - 嘘やハルシネーションは絶対に避けてください。確証がないならFalseにしてください。
    """

    try:
        response = search_model.generate_content(prompt)
        text = response.text.strip()

        if "False" in text or "false" in text:
            return None

        # 放送がある場合、テキストを整形して返す
        return f"📺 **{keyword}**\n{text}"

    except Exception as e:
        print(f"🦇❌ Check Error ({keyword}): {e}")
        return None
