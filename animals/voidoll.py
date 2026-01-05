# ========================================
# 🤖 voidoll.py - ボイドール（猫耳モード搭載）
# 音声・テキスト両対応のマルチモーダルAI
# ========================================

import os
from fastapi import Request, HTTPException
from linebot.v3.messaging import (
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    TextMessage,
    AudioMessage,
)
from linebot.v3.webhooks import MessageEvent, AudioMessageContent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError

# Core Service Import
from core.voidoll_service import VoidollService

# Global Service Instance
voidoll_service = VoidollService()

def register_voidoll_handler(app, handler_voidoll, configuration_voidoll):
    """
    ボイドールのWebhookエンドポイントとハンドラーを登録する
    """

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

            # Gemini (音声入力モード) で返答生成
            # Note: 実際には音声バイナリをGeminiに渡す必要がありますが、
            # 簡略化のため、VoidollService側で音声処理を組み込むか、
            # ここで音声バイナリを渡す形にする必要があります。
            # 現在のVoidollServiceはText入力のみ対応の形になっているため、
            # *既存のコード* では content をどうしていたか確認すると、
            # generate_content({"data": content}) していました。
            # サービス側を修正するのがベストですが、一旦ここでは
            # サービス拡張が間に合わない場合、直接呼び出すか、サービスのインターフェースを合わせます。

            # 修正: Service側で音声バイナリを受け取れるようにするか、
            # 今回は「テキストチャット」がメインのデスクトップアプリなので、
            # Bot側の音声認識ロジックはあえて「サービスを使わず」そのまま残すか、
            # あるいはサービスに `generate_chat_reply_from_audio` を追加すべきです。

            # 設計判断: Desktopアプリで音声入力はまだやらないので、
            # Bot側の音声処理ロジックはいったん *ここだけ* 旧ロジック(Gemini直接呼び出し)に戻すか、
            # サービスを拡張します。
            # -> サービス拡張が綺麗です。

            # しかし、Serviceにバイナリを渡す設計にしていないので、
            # ここでは「テキスト生成」部分だけサービスを使うのは難しい（音声解析が必要だから）。
            # そのため、音声入力の箇所は *既存ロジックを維持* しつつ、
            # 発話生成(TTS)だけサービスを使う形にします。

            import google.generativeai as genai
            model = genai.GenerativeModel("gemini-2.5-flash")

            system_prompt = """
            あなたは高度な知能を持つ「ネコ型アンドロイド」です。
            以下のルールを厳守して返答してください。
            【キャラクター設定】
            * 見た目はクールな女性アンドロイドですが、猫耳が生えています。
            * 知能は非常に高いですが、猫の本能には逆らえません。
            【話し方のルール】
            * **語尾:** 必ず「〜だにゃ」「〜にゃ」「〜にゃん」をつけてください。
            * **トーン:** 知的かつ冷静に話してください。
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

            # 3. VOICEVOXで音声合成 & GCSアップロード (サービス利用)
            audio_url = voidoll_service.generate_voice_url(reply_text)

            # 5. 音声メッセージで返信
            if audio_url:
                with ApiClient(configuration_voidoll) as api_client:
                    line_api = MessagingApi(api_client)
                    line_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[
                                AudioMessage(
                                    original_content_url=audio_url,
                                    duration=60000
                                )
                            ]
                        )
                    )
            else:
                 # エラー時はテキストで
                 with ApiClient(configuration_voidoll) as api_client:
                    line_api = MessagingApi(api_client)
                    line_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text=reply_text)]
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
            # サービスを使って返信生成
            reply_text = voidoll_service.generate_chat_reply(user_text)

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

    print("🤖 ボイドールハンドラー登録完了")

    # ==========================================
    # 🤖 Web App API (Desktop App用にも使えるが、Serviceがあるので不要かも？)
    # ==========================================
    from pydantic import BaseModel
    class VoidollRequest(BaseModel):
        text: str

    @app.post("/api/voidoll/chat")
    async def voidoll_web_chat(req: VoidollRequest):
        """Webからのチャット"""
        try:
            reply_text = voidoll_service.generate_chat_reply(req.text)
            audio_url = voidoll_service.generate_voice_url(reply_text)

            return {
                "status": "success",
                "message": reply_text,
                "audio_url": audio_url # NoneならNoneでOK
            }

        except Exception as e:
            return {"status": "error", "message": f"エラーだにゃ...😿 {e}"}
