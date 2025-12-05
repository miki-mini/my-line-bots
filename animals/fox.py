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
    YouTube動画を要約（Google検索補足 + コメント分析 + 長文対応）
    """
    print(f"🦊 YouTube要約開始: {video_id}")

    try:
        YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
        if not YOUTUBE_API_KEY:
            print("⚠️ YOUTUBE_API_KEY が設定されていません")
            return "🦊 YouTube APIキーが設定されていないコン...管理者に連絡してコン！"

        # ========================================
        # 1. YouTube Data API で動画情報を取得
        # ========================================
        youtube_url = f"https://www.googleapis.com/youtube/v3/videos"
        params = {
            "id": video_id,
            "key": YOUTUBE_API_KEY,
            "part": "snippet,contentDetails,statistics",
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
        comment_count = statistics.get("commentCount", "0")

        print(f"✅ 動画情報取得成功: {title}")

        # ========================================
        # 2. コメントを取得（最新30件に増量）
        # ========================================
        comments_text = ""
        try:
            comments_url = f"https://www.googleapis.com/youtube/v3/commentThreads"
            comments_params = {
                "videoId": video_id,
                "key": YOUTUBE_API_KEY,
                "part": "snippet",
                "maxResults": 30,  # 少し増やしました
                "order": "relevance",
            }

            print("🦊 コメント取得中...")
            comments_response = requests.get(
                comments_url, params=comments_params, timeout=10
            )
            comments_response.raise_for_status()
            comments_data = comments_response.json()

            if comments_data.get("items"):
                comment_list = []
                for item in comments_data["items"]:
                    raw_comment = item["snippet"]["topLevelComment"]["snippet"][
                        "textDisplay"
                    ]
                    clean_comment = re.sub(r"<[^>]+>", "", raw_comment)  # HTMLタグ除去
                    comment_list.append(f"- {clean_comment}")

                comments_text = "\n".join(comment_list)
                print(f"✅ コメント取得成功: {len(comment_list)}件")
            else:
                comments_text = "（コメントなし）"
        except Exception as e:
            print(f"⚠️ コメント取得エラー: {e}")
            comments_text = "（取得失敗）"

        # ========================================
        # 3. Google検索で関連情報を取得 (RAG)
        # ========================================
        search_context = ""
        if search_model:
            print("🔍 関連情報をGoogle検索中...")
            # 検索クエリを少し工夫
            search_query = f"{title} {channel_title} 評判 解説"

            try:
                # 検索専用の軽いプロンプト
                search_prompt = f"""検索クエリ: {search_query}
                この動画やトピックに関する「最新の補足情報」や「世間の評価」を検索して、重要な事実を3つ抽出してください。"""

                search_response = search_model.generate_content(
                    search_prompt,
                    generation_config={"temperature": 0.5, "max_output_tokens": 1000},
                )

                if search_response and search_response.text:
                    search_context = f"\n【Google検索による補足情報】\n{search_response.text.strip()}\n"
                    print("✅ 検索情報取得成功")
            except Exception as e:
                print(f"⚠️ 検索失敗: {e}")

        # ========================================
        # 4. Geminiで要約を生成 (ここが本番！)
        # ========================================
        print("🦊 Geminiで要約生成中...")
        model = text_model if text_model else search_model
        if not model:
            return "🦊 AIモデルのエラーだコン..."

        # プロンプトの大幅強化
        summary_prompt = f"""
あなたはプロの動画解説者「キツネ先生」です。
以下の情報を元に、YouTube動画の魅力と内容を「詳細に」解説してください。
途中で文章が切れないように、最後まで完結させてください。

【動画基本情報】
タイトル: {title}
チャンネル: {channel_title}
公開日: {published_at[:10]}
再生数: {view_count}回 / コメント数: {comment_count}件

【動画の説明文】
{description[:1000]}...

【視聴者のコメント（反応）】
{comments_text[:2000]}

{search_context}

【解説のルール】
1. **挨拶**: 「キツネ先生だコン！今回の動画はこれだコン！」から始める。
2. **概要**: 動画がどんな内容か、3行程度で分かりやすく。
3. **詳細ポイント**: 動画の重要なポイントを、長くなっても良いので詳しく解説する（箇条書きでも文章でも可）。
4. **世間の反応**: 視聴者のコメントや検索情報を元に、みんながどう思っているか紹介する。
5. **まとめ**: 最後に一言で締める。
6. **語尾**: 文末は「〜コン」「〜だコン」など、キツネキャラを崩さないこと。

解説をお願いするコン！
"""

        # 🚀 ここが修正の核心です！ max_output_tokens を大幅アップ
        response = model.generate_content(
            summary_prompt,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 8192,  # 👈 1024から8192へ変更！これで切れません
            },
        )

        if response and response.text:
            summary = response.text.strip()
            print("✅ 要約生成成功")

            # LINEの見やすさのために少し整形して返す
            result = f"""{summary}

🔗 動画を見る: https://youtu.be/{video_id}"""
            return result
        else:
            return "🦊 うまく要約できなかったコン...もう一度試してほしいコン！"

    except Exception as e:
        print(f"❌ 全体エラー: {e}")
        import traceback

        print(traceback.format_exc())
        return "🦊 エラーが発生したコン...ごめんコン💦"
