import os
from datetime import datetime
from fastapi import Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from google.cloud import firestore
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import ApiClient, MessagingApi, ReplyMessageRequest, TextMessage

# ========================================
# 🐇 rabbit.py - 月うさぎ (Moon Rabbit)
# ========================================

# Firestore Client
db = firestore.Client()
RABBIT_COLLECTION = "rabbit_users"


def get_rabbit_reply(text: str) -> str:
    """
    メッセージを受け取って、月うさぎとしての返信を返す純粋関数
    """
    reply = "うさぎは月で餅をついています...🐇🌕"
    if "おはよう" in text:
        reply = "おはよう！今日もキラキラ光る月のかけらを集めよう✨"
    return reply

def register_rabbit_handler(app, handler_rabbit, configuration_rabbit, auth_dependency=None):
    """
    月うさぎのエンドポイントを登録
    """

    # --- LINE Webhook ---
    @app.post("/callback_rabbit")
    async def callback_rabbit(request: Request):
        signature = request.headers["X-Line-Signature"]
        body = await request.body()
        try:
            handler_rabbit.handle(body.decode("utf-8"), signature)
        except Exception as e:
            print(f"❌ Rabbit Webhook Error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        return "OK"

    @handler_rabbit.add(MessageEvent, message=TextMessageContent)
    def handle_rabbit_message(event):
        # シンプルな返信のみ実装（LINE側）
        text = event.message.text
        reply = get_rabbit_reply(text)


        with ApiClient(configuration_rabbit) as api_client:
            line_api = MessagingApi(api_client)
            line_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply)]
                )
            )

    # --- Web App API (Secured) ---
    if auth_dependency:

        @app.get("/api/rabbit/stats", dependencies=[auth_dependency])
        async def get_rabbit_stats():
            # 全体の合計ポイントなどを返す（簡易実装）
            # 本来はユーザーごとのIDが必要だが、Webアプリは共通Basic認証なので
            # 「みんなの合計」または「特定ドキュメント」で管理する
            doc_ref = db.collection(RABBIT_COLLECTION).document("global_stats")
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                return {"total_clicks": data.get("total_clicks", 0)}
            else:
                return {"total_clicks": 0}

        @app.post("/api/rabbit/action", dependencies=[auth_dependency])
        async def post_rabbit_action():
            # クリック数をカウントアップ
            doc_ref = db.collection(RABBIT_COLLECTION).document("global_stats")

            # トランザクション推奨だが簡易的にupdate/set
            if doc_ref.get().exists:
                doc_ref.update({"total_clicks": firestore.Increment(1)})
            else:
                doc_ref.set({"total_clicks": 1})

            # 更新後の値を取得
            new_data = doc_ref.get().to_dict()
            return {"message": "Success", "total_clicks": new_data.get("total_clicks", 0)}

    print("🐇 月うさぎハンドラー登録完了")
