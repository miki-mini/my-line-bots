# ========================================
# 🤖 voidoll.py - ボイドール（猫耳モード搭載）
# 音声・テキスト両対応のマルチモーダルAI
# ========================================

import os
import uuid
import google.generativeai as genai
from google.cloud import storage

from fastapi import Request, HTTPException
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    TextMessage,
    AudioMessage,
)
# ⚠️ ここが重要！ TextMessageContent を追加しました
from linebot.v3.webhooks import MessageEvent, AudioMessageContent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError
import requests


def register_voidoll_handler(app, handler_voidoll, configuration_voidoll):
    """
    ボイドールのWebhookエンドポイントとハンドラーを登録する
    """

    # GCS設定
    GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

# デフォルト値をなくすか、Noneにします。
# URLは必ず環境変数で設定するように強制します。
    VOICEVOX_URL = os.getenv("VOICEVOX_URL")
    if not VOICEVOX_URL:
    # URLが設定されていなかったらエラーで止める（安全装置）
        raise ValueError("⚠️ 環境変数 VOICEVOX_URL が設定されていません！")

    # ==========================================
    # 🤖 ボイドール Webhook エンドポイント
    # ==========================================
    @app.post("/callback_voidoll")
    async def callback_voidoll(request: Request):
        signature = request.headers.get("X-Line-Signature", "")
        body = await request.body()
        try:
            handler_voidoll.handle(body.decode("utf-8"), signature)
        except InvalidSignatureError:
            print("❌ ボイドール: 署名エラー")
            raise HTTPException(status_code=400, detail="Invalid signature")
        except Exception as e:
            print(f"❌ ボイドール: Webhookエラー: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        return "OK"

    # ==========================================
    # 🎤 音声メッセージ処理（猫モード）
    # ==========================================
    @handler_voidoll.add(MessageEvent, message=AudioMessageContent)
    def handle_voidoll_audio(event):
        print(f"🤖 ボイドール: 音声メッセージ受信 ID: {event.message.id}")

        try:
            # 1. 音声データを取得
            with ApiClient(configuration_voidoll) as api_client:
                blob_api = MessagingApiBlob(api_client)
                content = blob_api.get_message_content(event.message.id)

            # 2. Geminiで文字起こし＆返答生成（🐈 猫モード）
            model = genai.GenerativeModel("gemini-2.5-flash")

            system_prompt = """
            あなたは高度な知能を持つ「ネコ型アンドロイド」です。
            以下のルールを厳守して返答してください。

            【キャラクター設定】
            * 見た目はクールな女性アンドロイドですが、猫耳が生えています。
            * 知能は非常に高いですが、猫の本能には逆らえません。

            【話し方のルール】
            * **語尾:** 必ず「〜だにゃ」「〜にゃ」「〜にゃん」をつけてください。
            * **トーン:** 知的かつ冷静に話してください（ギャップを演出するため）。

            【特殊機能：猫語翻訳】
            * ユーザーの音声が「ニャー」「ミャー」などの鳴き声だけだった場合、その「猫語」が何を訴えているか勝手に翻訳して答えてください。
            """

            response = model.generate_content([
                system_prompt,
                "ユーザーの音声入力:",
                {"mime_type": "audio/mp4", "data": content}
            ])
            reply_text = response.text
            print(f"🤖 ボイドール返答: {reply_text[:50]}...")

            # 3. VOICEVOXで音声合成
            # speaker=58 (九州そら) などに変えると雰囲気が変わります
            query_response = requests.post(
                f"{VOICEVOX_URL}/audio_query",
                params={"text": reply_text, "speaker": 89},
                timeout=30
            )
            query_response.raise_for_status()
            audio_query = query_response.json()

            synthesis_response = requests.post(
                f"{VOICEVOX_URL}/synthesis",
                params={"speaker": 89},
                json=audio_query,
                timeout=60
            )
            synthesis_response.raise_for_status()
            audio_content = synthesis_response.content

            # 4. GCSにアップロード
            client = storage.Client()
            bucket = client.bucket(GCS_BUCKET_NAME)
            blob = bucket.blob(f"voidoll_voice_{uuid.uuid4()}.wav")
            blob.upload_from_string(audio_content, content_type="audio/wav")
            blob.make_public()
            audio_url = blob.public_url

            # 5. 音声メッセージで返信
            with ApiClient(configuration_voidoll) as api_client:
                line_api = MessagingApi(api_client)
                line_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[
                            AudioMessage(
                                original_content_url=audio_url,
                                duration=len(audio_content) // 32
                            )
                        ]
                    )
                )

        except Exception as e:
            print(f"❌ ボイドールエラー: {e}")
            # エラー時はテキストでこっそり教える
            try:
                with ApiClient(configuration_voidoll) as api_client:
                    line_api = MessagingApi(api_client)
                    line_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text="音声回路にエラーだにゃ...😿")]
                        )
                    )
            except:
                pass

    # ==========================================
    # 🐈 テキストメッセージ処理（猫モード追加）
    # ==========================================
    @handler_voidoll.add(MessageEvent, message=TextMessageContent)
    def handle_voidoll_text(event):
        user_text = event.message.text
        print(f"🤖 ボイドール(猫)テキスト受信: {user_text}")

        try:
            # プロンプト設定（テキスト用）
            system_prompt = """
            あなたは高度な知能を持つ「ネコ型アンドロイド」です。

            【話し方のルール】
            * **語尾:** 必ず「〜だにゃ」「〜にゃ」「〜にゃん」をつけてください。
            * **絵文字:** 文末にたまに猫の絵文字（🐈, 🐾, 🌙）をつけてください。
            * **性格:** 知的で役に立つことを言いますが、猫なので少し気まぐれでもOKです。
            """

            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content([
                system_prompt,
                f"ユーザーのメッセージ: {user_text}",
            ])
            reply_text = response.text

            # テキストで返信
            with ApiClient(configuration_voidoll) as api_client:
                line_api = MessagingApi(api_client)
                line_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=reply_text)]
                    )
                )

        except Exception as e:
            print(f"❌ ボイドール生成エラー: {e}")
            try:
                with ApiClient(configuration_voidoll) as api_client:
                    line_api = MessagingApi(api_client)
                    line_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text="システムエラーだにゃ...😿")]
                        )
                    )
            except:
                pass

    print("🤖 ボイドールハンドラー登録完了")

    # ==========================================
    # 🤖 Web App API
    # ==========================================
    from pydantic import BaseModel
    class VoidollRequest(BaseModel):
        text: str

    @app.post("/api/voidoll/chat")
    async def voidoll_web_chat(req: VoidollRequest):
        """Webからのチャット"""
        try:
            # プロンプト（猫モード）既存ロジック再利用
            system_prompt = """
            あなたは高度な知能を持つ「ネコ型アンドロイド」です。

            【話し方のルール】
            * **語尾:** 必ず「〜だにゃ」「〜にゃ」「〜にゃん」をつけてください。
            * **絵文字:** 文末にたまに猫の絵文字（🐈, 🐾, 🌙）をつけてください。
            * **性格:** 知的で役に立つことを言いますが、猫なので少し気まぐれでもOKです。
            """

            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content([
                system_prompt,
                f"ユーザーのメッセージ: {req.text}",
            ])
            return {"status": "success", "message": response.text}
        except Exception as e:
            return {"status": "error", "message": f"エラーだにゃ...😿 {e}"}