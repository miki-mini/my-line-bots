
import os
import uuid
import requests
import google.generativeai as genai
from google.cloud import storage

class VoidollService:
    def __init__(self):
        self.voicevox_url = os.getenv("VOICEVOX_URL")
        self.gcs_bucket_name = os.getenv("GCS_BUCKET_NAME")

        # Initialize Gemini
        # Note: API key should be set in environment variable GOOGLE_API_KEY by default for genai
        # If not, it might need explicit configuration here, but usually genai.configure() is called globally or env var is used.
        # Assuming genai is configured globally in main.py, but for desktop app we might need to configure it.
        # Ideally, we check if it needs config.
        pass

    def generate_chat_reply(self, user_text: str, is_audio_input: bool = False) -> str:
        """
        Generates a text reply from Voidoll using Gemini.
        """
        try:
            model_name = "gemini-2.5-flash" if is_audio_input else "gemini-1.5-flash"
            model = genai.GenerativeModel(model_name)

            system_prompt = """
            あなたは高度な知能を持つ「ネコ型アンドロイド」です。
            以下のルールを厳守して返答してください。

            【キャラクター設定】
            * 見た目はクールな女性アンドロイドですが、猫耳が生えています。
            * 知能は非常に高いですが、猫の本能には逆らえません。

            【話し方のルール】
            * **語尾:** 必ず「〜だにゃ」「〜にゃ」「〜にゃん」をつけてください。
            * **トーン:** 知的かつ冷静に話してください（ギャップを演出するため）。
            * **絵文字:** 文末にたまに猫の絵文字（🐈, 🐾, 🌙）をつけてください。
            """

            if is_audio_input:
                system_prompt += """
                【特殊機能：猫語翻訳】
                * ユーザーの音声が「ニャー」「ミャー」などの鳴き声だけだった場合、その「猫語」が何を訴えているか勝手に翻訳して答えてください。
                """

            prompt = [
                system_prompt,
                f"ユーザーの{'音声' if is_audio_input else ''}入力: {user_text}"
            ]

            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"❌ Voidoll Chat Error: {e}")
            return "回路にノイズが走ったようだにゃ...😿 もう一度言ってほしいにゃ。"

    def generate_voice_url(self, text: str) -> str:
        """
        Generates audio using VoiceVox and uploads to GCS, returning the public URL.
        """
        if not self.voicevox_url or not self.gcs_bucket_name:
            print("⚠️ Voice config missing, skipping audio generation.")
            return None

        try:
            # Query
            query_response = requests.post(
                f"{self.voicevox_url}/audio_query",
                params={"text": text, "speaker": 89}, # 89: Custom or specific speaker ID
                timeout=30
            )
            query_response.raise_for_status()
            audio_query = query_response.json()

            # Synthesis
            synthesis_response = requests.post(
                f"{self.voicevox_url}/synthesis",
                params={"speaker": 89},
                json=audio_query,
                timeout=60
            )
            synthesis_response.raise_for_status()
            audio_content = synthesis_response.content

            # GCS Upload
            client = storage.Client()
            bucket = client.bucket(self.gcs_bucket_name)
            filename = f"voidoll_voice_{uuid.uuid4()}.wav"
            blob = bucket.blob(filename)
            blob.upload_from_string(audio_content, content_type="audio/wav")

            try:
                blob.make_public()
            except Exception:
                pass

            return blob.public_url

        except Exception as e:
            print(f"❌ Voidoll Voice Gen Error: {e}")
            return None
