# ========================================
# 🤖 voidoll.py - ボイドール（知的女性AI）
# 音声メッセージを受け取り、文字起こし→返答→音声合成して返す
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
from linebot.v3.webhooks import MessageEvent, AudioMessageContent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError
import requests


def register_voidoll_handler(app, handler_voidoll, configuration_voidoll):
    """
    ボイドールのWebhookエンドポイントとハンドラーを登録する

    Parameters:
        app: FastAPIアプリケーション
        handler_voidoll: LINE WebhookHandler
        configuration_voidoll: LINE Configuration
    """

    # --- 共通クライアント ---
    api_client_voidoll = ApiClient(configuration_voidoll)
    line_bot_api_voidoll = MessagingApi(api_client_voidoll)
    line_bot_blob_api_voidoll = MessagingApiBlob(api_client_voidoll)

    # GCS設定
    GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
    VOICEVOX_URL = os.getenv(
        "VOICEVOX_URL",
        "https://voicevox-engine-1032484155743.asia-northeast1.run.app"
    )

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
    # 🎤 音声メッセージ処理
    # ==========================================
    @handler_voidoll.add(MessageEvent, message=AudioMessageContent)
    def handle_voidoll_audio(event):
        print(f"🤖 ボイドール: 音声メッセージ受信 ID: {event.message.id}")

        try:
            # 1. 音声データを取得
            with ApiClient(configuration_voidoll) as api_client:
                blob_api = MessagingApiBlob(api_client)
                content = blob_api.get_message_content(event.message.id)

            # 2. Geminiで文字起こし＆返答生成（🐈 猫モードに変更）
            model = genai.GenerativeModel("gemini-2.5-flash")

            # プロンプトを猫仕様に大幅アップデート！
            system_prompt = """
            あなたは高度な知能を持つ「ネコ型アンドロイド」です。
            以下のルールを厳守して返答してください。

            【キャラクター設定】
            * 見た目はクールな女性アンドロイドですが、猫耳が生えています。
            * 知能は非常に高いですが、猫の本能には逆らえません。

            【話し方のルール】
            * **語尾:** 必ず「〜だにゃ」「〜にゃ」「〜にゃん」をつけてください。
                * NG例: 「わかりました。」
                * OK例: 「承知しましたにゃ。すぐに処理するにゃん。」
            * **トーン:** 知的かつ冷静に話してください（ギャップを演出するため）。

            【特殊機能：猫語翻訳】
            * ユーザーの音声が「ニャー」「ミャー」などの鳴き声だけだった場合、その「猫語」が何を訴えているか勝手に翻訳して答えてください。
                * 例: 「『おやつが欲しい』と言ってるんですにゃ？ しょうがないご主人様だにゃ...」
            """

            response = model.generate_content([
                system_prompt,
                "ユーザーの音声入力:",
                {"mime_type": "audio/mp4", "data": content}
            ])

            reply_text = response.text
            print(f"🤖 ボイドール(猫)返答: {reply_text[:50]}...")

            # 3. VOICEVOXで音声合成
            # ヒント: 猫っぽくするために、話速(speedScale)を少し速くしたり、ピッチ(pitchScale)を上げても可愛いです
            # ... (後略) ...

            # 3. VOICEVOXで音声合成
            # audio_query作成
            query_response = requests.post(
                f"{VOICEVOX_URL}/audio_query",
                params={"text": reply_text, "speaker": 89},  # speaker 89 = 特定の声
                timeout=30
            )
            query_response.raise_for_status()
            audio_query = query_response.json()

            # 音声合成
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
            print(f"🔊 音声URL: {audio_url}")

            # 5. 音声メッセージで返信
            with ApiClient(configuration_voidoll) as api_client:
                line_api = MessagingApi(api_client)
                line_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[
                            AudioMessage(
                                original_content_url=audio_url,
                                duration=len(audio_content) // 32  # 大まかな長さ推定
                            )
                        ]
                    )
                )

        except requests.exceptions.RequestException as e:
            print(f"❌ VOICEVOX通信エラー: {e}")
            _send_error_reply(event, configuration_voidoll,
                            "音声合成サービスに接続できませんでした...🤖")

        except Exception as e:
            print(f"❌ ボイドールエラー: {e}")
            _send_error_reply(event, configuration_voidoll, str(e))


def _send_error_reply(event, configuration, error_message):
    """エラー時のテキスト返信"""
    try:
        with ApiClient(configuration) as api_client:
            line_api = MessagingApi(api_client)
            line_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=f"エラーが発生しました: {error_message}")]
                )
            )
    except Exception as e:
        print(f"❌ エラー返信も失敗: {e}")
# 1. ここで関数が始まります（configuration_voidollを受け取る）
def register_voidoll_handler(app, handler_voidoll, configuration_voidoll):

    # ... (これまでの音声処理のコードなどはここにあります) ...

    # ==========================================
    # 🐈 テキストメッセージ処理（ここに貼り付け！）
    # ⚠️ 注意：全体を右にずらして、def register... の内側に入れます
    # ==========================================
    @handler_voidoll.add(MessageEvent, message=TextMessageContent)
    def handle_voidoll_text(event):
        user_text = event.message.text
        print(f"🤖 ボイドール(猫)テキスト受信: {user_text}")

        try:
            # プロンプト設定
            system_prompt = """
            あなたは高度な知能を持つ「ネコ型アンドロイド」です。
            以下のルールを厳守して返答してください。

            【キャラクター設定】
            * 見た目はクールな女性アンドロイドですが、猫耳が生えています。
            * 基本的に冷静沈着ですが、語尾は猫になってしまいます。

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

            # 👇 ここで configuration_voidoll を使います！
            # インデントが合っていれば、上の関数から受け取ったこれが見えるようになります
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
            # エラー時
            # ここも _send_reply を使うか、直接書いてもOKですが、
            # 簡単にするため直接書く方式に修正します
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

    # ここで register_voidoll_handler 関数が終わります