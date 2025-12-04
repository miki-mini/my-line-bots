"""
fox.py - キツネのYouTube要約BOT
"""

import os
import re
import requests
from linebot.v3.messaging import (
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhook import MessageEvent
from linebot.v3.webhooks import TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError


def register_fox_handler(app, handler_fox, configuration_fox, search_model, text_model):
    """
    キツネのハンドラーを登録

    Args:
        app: FastAPIアプリ
        handler_fox: LINE Webhookハンドラー
        configuration_fox: LINE API設定
        search_model: 検索対応Geminiモデル
        text_model: 通常のGeminiモデル
    """

    from fastapi import Request, HTTPException

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
            # YouTube URLの検出
            youtube_regex = r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)'
            match = re.search(youtube_regex, user_message)

            if match:
                video_id = match.group(1)
                print(f"🦊 YouTube動画ID検出: {video_id}")

                # YouTube動画の要約
                msg = summarize_youtube_with_search(
                    video_id,
                    search_model,
                    text_model
                )
            else:
                msg = "🦊 キツネ先生だコン！\n要約したいYouTube動画のURLを送ってコン！"

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
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=msg)]
                    )
                )
            print("📨 キツネ返信送信完了！")

        except Exception as e:
            print(f"❌ 返信送信エラー: {e}")
            import traceback
            print(traceback.format_exc())


def summarize_youtube_with_search(video_id: str, search_model, text_model) -> str:
    """
    YouTube動画を要約（Google検索で補足情報も取得）

    Args:
        video_id: YouTube動画ID
        search_model: 検索対応Geminiモデル
        text_model: 通常のGeminiモデル

    Returns:
        要約テキスト
    """

    print(f"🦊 YouTube要約開始: {video_id}")

    try:
        YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

        if not YOUTUBE_API_KEY:
            print("⚠️ YOUTUBE_API_KEY が設定されていません")
            return "🦊 YouTube APIキーが設定されていないコン...管理者に連絡してコン！"

        # YouTube Data API で動画情報を取得
        youtube_url = f"https://www.googleapis.com/youtube/v3/videos"
        params = {
            "id": video_id,
            "key": YOUTUBE_API_KEY,
            "part": "snippet,contentDetails,statistics"
        }

        print("🦊 YouTube API呼び出し中...")
        response = requests.get(youtube_url, params=params, timeout=10)
        response.raise_for_status()

        video_data = response.json()

        if not video_data.get("items"):
            return "🦊 この動画は見つからなかったコン...URLを確認してコン！"

        item = video_data["items"][0]
        snippet = item["snippet"]
        statistics = item.get("statistics", {})

        title = snippet["title"]
        description = snippet["description"]
        channel_title = snippet["channelTitle"]
        published_at = snippet["publishedAt"]
        view_count = statistics.get("viewCount", "不明")

        print(f"✅ 動画情報取得成功: {title}")

        # Google検索で関連情報を取得
        search_context = ""

        if search_model:
            print("🔍 関連情報をGoogle検索中...")

            search_query = f"{title} {channel_title} 解説 まとめ"

            search_prompt = f"""以下の検索クエリに関する最新情報を簡潔にまとめてください：

検索クエリ: {search_query}

重要なポイントを3つ程度、箇条書きで教えてください。"""

            try:
                search_response = search_model.generate_content(
                    search_prompt,
                    generation_config={
                        "temperature": 0.5,
                        "max_output_tokens": 512,
                    }
                )

                if search_response and hasattr(search_response, 'text') and search_response.text:
                    search_context = f"\n\n【関連情報（ネット検索結果）】\n{search_response.text.strip()}\n"
                    print("✅ 検索情報取得成功")
            except Exception as e:
                print(f"⚠️ 検索失敗: {e}")

        # Geminiで要約を生成
        print("🦊 Geminiで要約生成中...")

        model = text_model if text_model else search_model

        if not model:
            return "🦊 AIモデルが利用できないコン...管理者に連絡してコン！"

        # 説明文を適切な長さに制限
        description_preview = description[:1000] if len(description) > 1000 else description

        summary_prompt = f"""あなたはYouTube動画要約の専門家「キツネ先生」です。
以下の動画情報を読んで、視聴者が知りたい要点を分かりやすく要約してください。

【動画情報】
タイトル: {title}
チャンネル: {channel_title}
公開日: {published_at[:10]}
視聴回数: {view_count}回

【説明文】
{description_preview}
{search_context}

【要約の条件】
- 要点を3〜5つの箇条書きで
- 語尾に「〜コン！」「〜だコン！」を付けて親しみやすく
- 専門用語は分かりやすく説明
- 挨拶は不要、要点から始める

要約:"""

        response = model.generate_content(
            summary_prompt,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 1024,
            }
        )

        if response and hasattr(response, 'text') and response.text:
            summary = response.text.strip()
            print("✅ 要約生成成功")

            # 最終的な返信メッセージ
            result = f"""🦊 キツネ先生の要約だコン！

【📹 動画タイトル】
{title}

【📺 チャンネル】
{channel_title}

【👀 視聴回数】
{view_count}回

{summary}

🔗 動画URL: https://youtu.be/{video_id}"""

            return result
        else:
            return "🦊 要約の生成に失敗したコン...もう一度試してコン！"

    except requests.Timeout:
        print("❌ YouTube API タイムアウト")
        return "🦊 YouTube APIの応答が遅いコン...もう一度試してコン！"

    except requests.RequestException as e:
        print(f"❌ YouTube API エラー: {e}")
        return "🦊 YouTube APIでエラーが発生したコン...💦"

    except Exception as e:
        print(f"❌ YouTube要約エラー: {e}")
        import traceback
        print(traceback.format_exc())
        return f"🦊 エラーが発生したコン...💦"