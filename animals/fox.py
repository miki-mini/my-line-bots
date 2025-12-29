"""
fox.py - キツネのYouTube要約BOT (修正版: 長文対応 + 検索強化)
"""

import os
import re
import requests
from linebot.v3.messaging import (
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhook import MessageEvent
from linebot.v3.webhooks import TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError
from fastapi import Request, HTTPException


def register_fox_handler(app, handler_fox, configuration_fox, search_model, text_model):
    """
    キツネのハンドラーを登録
    """

    @app.post("/callback_fox")
    async def callback_fox(request: Request):
        """キツネ用Webhook"""
        print("🦊🦊🦊 キツネWebhook受信！")

        signature = request.headers.get("X-Line-Signature")
        body = await request.body()

        try:
            handler_fox.handle(body.decode("utf-8"), signature)
            print("🦊 handler_fox.handle() 完了")
        except InvalidSignatureError:
            print(f"🦊❌ 署名検証エラー")
            raise HTTPException(status_code=400, detail="Invalid signature")
        except Exception as e:
            print(f"🦊❌ handler エラー: {e}")
            import traceback

            print(traceback.format_exc())

        return {"status": "ok"}

    @handler_fox.add(MessageEvent, message=TextMessageContent)
    def handle_fox_message(event):
        """キツネのメッセージ処理"""

        print(f"🦊 キツネ受信: {event.message.text}")
        user_message = event.message.text
        msg = ""

        try:
            # YouTube URLの検出 (短縮URLやモバイルURLにも対応)
            youtube_regex = r"(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)"
            match = re.search(youtube_regex, user_message)

            if match:
                video_id = match.group(1)
                print(f"🦊 YouTube動画ID検出: {video_id}")

                # 処理中のメッセージを送る（オプション: LINEの仕様上、応答は1回なのでここはスキップしますが、ログには残します）
                print("🦊 動画要約プロセスを開始します...")

                # YouTube動画の要約実行
                msg = summarize_youtube_with_search(video_id, search_model, text_model)
            else:
                msg = "🦊 キツネ先生だコン！\n要約したいYouTube動画のURLを送ってコン！\n長〜い動画でもバッチリ解説するコン！"

        except Exception as e:
            print(f"❌ キツネ処理エラー: {e}")
            import traceback

            print(traceback.format_exc())
            msg = "🦊 エラーが起きたコン...💦"

        # LINEに返信
        try:
            print("🦊 LINE返信開始")
            with ApiClient(configuration_fox) as c:
                api = MessagingApi(c)
                api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token, messages=[TextMessage(text=msg)]
                    )
                )
            print("📨 キツネ返信送信完了！")

        except Exception as e:
            print(f"❌ 返信送信エラー: {e}")
            import traceback

            print(traceback.format_exc())


def summarize_youtube_with_search(video_id: str, search_model, text_model) -> str:
    """
    YouTube動画を要約（ヘッダー固定表示 + 動画の長さに応じた賢い要約）
    """
    print(f"🦊 YouTube要約開始: {video_id}")

    try:
        YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
        if not YOUTUBE_API_KEY:
            return "🦊 APIキーがないコン..."

        # 1. 動画情報を取得
        youtube_url = f"https://www.googleapis.com/youtube/v3/videos"
        params = {
            "id": video_id,
            "key": YOUTUBE_API_KEY,
            "part": "snippet,contentDetails,statistics",
        }

        response = requests.get(youtube_url, params=params, timeout=10)
        video_data = response.json()

        if not video_data.get("items"):
            return "🦊 動画が見つからないコン..."

        item = video_data["items"][0]
        snippet = item["snippet"]
        statistics = item.get("statistics", {})
        content_details = item.get("contentDetails", {})

        title = snippet["title"]
        description = snippet["description"]
        channel_title = snippet["channelTitle"]
        published_at = snippet["publishedAt"]
        view_count = statistics.get("viewCount", "不明")
        comment_count = statistics.get("commentCount", "0")
        duration = content_details.get("duration", "不明")  # 動画の長さ

        print(f"✅ 動画情報取得: {title} (長さ: {duration})")

        # 2. コメント取得
        comments_text = ""
        try:
            comments_url = f"https://www.googleapis.com/youtube/v3/commentThreads"
            comments_params = {
                "videoId": video_id,
                "key": YOUTUBE_API_KEY,
                "part": "snippet",
                "maxResults": 30,
                "order": "relevance",
            }
            c_res = requests.get(comments_url, params=comments_params, timeout=10)
            c_data = c_res.json()
            if c_data.get("items"):
                c_list = [
                    re.sub(
                        r"<[^>]+>",
                        "",
                        i["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
                    )
                    for i in c_data["items"]
                ]
                comments_text = "\n- ".join(c_list)
            else:
                comments_text = "（なし）"
        except:
            comments_text = "（取得失敗）"

        # 3. 検索（RAG）
        search_context = ""
        if search_model:
            try:
                search_prompt = f"動画「{title}」の評判や補足情報を簡潔に検索して"
                s_res = search_model.generate_content(search_prompt)
                if s_res and s_res.text:
                    search_context = f"\n【検索情報】\n{s_res.text.strip()}\n"
            except:
                pass

        # 4. Geminiで要約本文のみ生成
        print("🦊 Geminiで要約生成中...")
        model = text_model if text_model else search_model

        # プロンプト（本文だけを書かせる）
        summary_prompt = f"""
あなたは動画解説のプロ「キツネ先生」です。
以下のYouTube動画の「要約・解説部分のみ」を作成してください。
タイトルや再生数などは私が書くので、あなたは書かなくていいです。

【動画情報】
タイトル: {title}
長さ: {duration} (ISO8601形式)
説明文: {description[:1000]}
コメント: {comments_text[:2000]}
{search_context}

【⚠️ 重要：長さの調整】
動画の「長さ ({duration})」を見て、解説のボリュームを変えてください。
- **短い動画（1分未満）の場合**: 「3行要約」＋「一言コメント」くらいで**サクッと簡潔に**。
- **長い動画（数分以上）の場合**: 内容をしっかり深掘りして「詳細に」解説。

【出力構成】
1. 挨拶（「キツネ先生の要約だコン！」などは不要。いきなり本文から）
2. 動画の概要・要点
3. みんなの反応
4. まとめ

語尾は「〜コン」で統一してください。
"""

        response = model.generate_content(
            summary_prompt,
            generation_config={"temperature": 0.7, "max_output_tokens": 8192},
        )

        if response and response.text:
            summary_body = response.text.strip()

            # 5. ここでガッチャンコ！Python側で綺麗に整形して返します
            result = f"""🦊 キツネ先生の要約だコン！

【📹 動画タイトル】
{title}

【📺 チャンネル】
{channel_title}

【👀 視聴回数】
{view_count}回

【💬 コメント数】
{comment_count}件

-----------------------------

{summary_body}

🔗 動画URL: https://youtu.be/{video_id}"""

            return result
        else:
            return "🦊 失敗したコン..."

    except Exception as e:
        print(f"❌ エラー: {e}")
        return "🦊 エラーだコン..."

    # ==========================================
    # 🦊 Web App API
    # ==========================================
    from pydantic import BaseModel
    class FoxRequest(BaseModel):
        url: str

    @app.post("/api/fox/summary")
    async def fox_web_summary(req: FoxRequest):
        """Webからの要約リクエスト処理"""
        url = req.url
        print(f"🦊 Web Request: {url}")

        # URLからID抽出
        youtube_regex = r"(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)"
        match = re.search(youtube_regex, url)

        if match:
            video_id = match.group(1)
            summary = summarize_youtube_with_search(video_id, search_model, text_model)
            return {"status": "success", "summary": summary}
        else:
            return {"status": "error", "message": "YouTubeのURLじゃないコン...💦"}
