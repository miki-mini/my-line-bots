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

            # 3. VOICEVOXで音声合成 & GCSアップロード (共通関数呼び出し)
            audio_url = _generate_voice(reply_text)

            # 5. 音声メッセージで返信
            with ApiClient(configuration_voidoll) as api_client:
                line_api = MessagingApi(api_client)
                line_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[
                            AudioMessage(
                                original_content_url=audio_url,
                                duration=60000 # 適当な長さ(ミリ秒) LINE側で調整される
                            )
                        ]
                    )
                )

        except Exception as e:
            print(f"❌ ボイドールエラー: {e}")
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

            model = genai.GenerativeModel("gemini-1.5-flash") # Use 1.5-flash for speed/cost
            response = model.generate_content([
                system_prompt,
                f"ユーザーのメッセージ: {user_text}",
            ])
            reply_text = response.text

            # テキストで返信 (LINEはテキストのみで返す運用？必要ならここも音声化可能)
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
            # ... (ErrorHandler)

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
            system_prompt = """
            あなたは高度な知能を持つ「ネコ型アンドロイド」です。

            【話し方のルール】
            * **語尾:** 必ず「〜だにゃ」「〜にゃ」「〜にゃん」をつけてください。
            * **絵文字:** 文末にたまに猫の絵文字（🐈, 🐾, 🌙）をつけてください。
            * **性格:** 知的で役に立つことを言いますが、猫なので少し気まぐれでもOKです。
            """

            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content([
                system_prompt,
                f"ユーザーのメッセージ: {req.text}",
            ])
            reply_text = response.text

            # 音声合成
            try:
                audio_url = _generate_voice(reply_text)
                return {
                    "status": "success",
                    "message": reply_text,
                    "audio_url": audio_url
                }
            except Exception as ve:
                print(f"⚠️ VoiceGen Error: {ve}")
                return {
                    "status": "success",
                    "message": reply_text,
                    "audio_url": None
                }

        except Exception as e:
            return {"status": "error", "message": f"エラーだにゃ...😿 {e}"}

def _generate_voice(text: str) -> str:
    """VoiceVoxで音声生成しGCSの公開URLを返すヘルパー関数"""
    VOICEVOX_URL = os.getenv("VOICEVOX_URL")
    GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

    if not VOICEVOX_URL or not GCS_BUCKET_NAME:
         print("⚠️ Voice config missing, skipping audio generation.")
         return None

    # Query
    query_response = requests.post(
        f"{VOICEVOX_URL}/audio_query",
        params={"text": text, "speaker": 89}, # 58:九州そら, 89:?? (Keep original)
        timeout=30
    )
    query_response.raise_for_status()
    audio_query = query_response.json()

    # Synthesis
    synthesis_response = requests.post(
        f"{VOICEVOX_URL}/synthesis",
        params={"speaker": 89},
        json=audio_query,
        timeout=60
    )
    synthesis_response.raise_for_status()
    audio_content = synthesis_response.content

    # GCS Upload
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET_NAME)
    filename = f"voidoll_voice_{uuid.uuid4()}.wav"
    blob = bucket.blob(filename)
    blob.upload_from_string(audio_content, content_type="audio/wav")

    # 公開設定 (Uniform Bucket Level Accessの場合はIAMでAllUsers:Viewerが必要だが
    # ここでは個別にACLを設定する従来の書き方を使用。エラー時はIAM設定を確認)
    try:
        blob.make_public()
    except Exception:
        pass # Bucket policy might prevent ACL changes, strictly rely on public URL logic if bucket is public

    return blob.public_url