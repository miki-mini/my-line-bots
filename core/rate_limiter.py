"""
rate_limiter.py - 全ボット共通の使用回数制限ユーティリティ
1日10回/ユーザー/ボット別（JST基準でリセット）
"""

import hashlib
from datetime import datetime, timedelta, timezone
from google.cloud import firestore

DAILY_LIMIT = 10
COLLECTION_NAME = "usage_limits"
JST = timezone(timedelta(hours=9))

LIMIT_MESSAGES = {
    "fox": "🦊 今日はもう10回要約したコン！また明日来てほしいコン！",
    "frog": "🐸 今日はもう10回答えたケロ！また明日聞いてほしいケロ〜",
    "mole": "🦡 今日はもう10回調べたモグ！明日また来てほしいモグ〜",
    "capybara": "今日は10回おしゃべりしたっぴ〜♨️ また明日遊びに来てほしいっぴ",
    "bat": "🦇 今日はもう10回検索したモリ！また明日の夜に会えるのを待ってるモリ〜🌙",
    "beaver": "🦫 今日はもう10回お手伝いしたでヤンス！また明日がんばるでヤンス！",
    "penguin": "🐧 今日はもう10回対応したペン！明日またお手伝いするペン✨",
    "voidoll": "🤖 本日の処理上限（10回）に達したにゃ。また明日アクセスしてほしいにゃん🐾",
    "whale": "🐋 今日は10回、星の話をしましたね...✨\nまた明日、宇宙の海でお会いしましょう🌌",
    "owl": "🦉 今日はもう10回分析しました。また明日、一緒に健康管理しましょう",
    "raccoon": "🦝 今日は10回片付けを手伝ったよ！また明日も一緒にがんばろう✨",
    "butsubutsu": "🐺 今日は10回翻訳したよ。また明日、独り言を聞かせてね。",
    "alpaca": "🦙 今日はもう10回診断しました♪ また明日お越しくださいね✨",
    "butterfly": "🦋 今日はもう10回診断したわ♪ また明日お待ちしてますね✨",
    "flamingo": "🦩 今日はもう10回診断しました！また明日お会いしましょう♪",
}


def check_and_increment(db, user_id: str, bot_name: str) -> tuple[bool, str | None]:
    """
    使用回数をチェックし、許可ならカウントUP。

    Returns:
        (True, None) - 使用可能
        (False, メッセージ) - 制限到達
    """
    if not db:
        return (True, None)

    try:
        date_str = datetime.now(JST).strftime("%Y-%m-%d")
        doc_id = f"{user_id}_{bot_name}_{date_str}"
        doc_ref = db.collection(COLLECTION_NAME).document(doc_id)

        doc = doc_ref.get()
        if doc.exists:
            count = doc.to_dict().get("count", 0)
            if count >= DAILY_LIMIT:
                msg = LIMIT_MESSAGES.get(bot_name, "本日の利用上限に達しました。また明日お試しください。")
                return (False, msg)

        doc_ref.set({
            "user_id": user_id,
            "bot_name": bot_name,
            "date": date_str,
            "count": firestore.Increment(1),
            "last_used": firestore.SERVER_TIMESTAMP,
        }, merge=True)

        return (True, None)

    except Exception as e:
        print(f"[RateLimit] Error: {e}")
        return (True, None)


def get_user_id_from_request(request) -> str:
    """Web APIエンドポイント用: クライアントIPをハッシュ化して識別子にする"""
    try:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            ip = forwarded_for.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        return f"ip_{hashlib.sha256(ip.encode()).hexdigest()[:16]}"
    except Exception:
        return "ip_unknown"


def check_and_increment_by_ip(db, request, bot_name: str) -> tuple[bool, str | None]:
    """Web APIエンドポイント用: IPベースでレート制限チェック"""
    user_id = get_user_id_from_request(request)
    return check_and_increment(db, user_id, bot_name)
