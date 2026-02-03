import os
import uuid
import requests
import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import storage

class VoidollService:
    def __init__(self):
        self.voicevox_url = os.getenv("VOICEVOX_URL")
        self.gcs_bucket_name = os.getenv("GCS_BUCKET_NAME")

        # Initialize Vertex AI (Matches main.py logic)
        project_id = os.getenv("GCP_PROJECT_ID")
        if project_id:
            try:
                vertexai.init(project=project_id, location="us-central1")
                print(f"DEBUG: Vertex AI Initialized for project {project_id}")
                self.use_vertex = True
            except Exception as e:
                print(f"[WARNING] Vertex AI Init Error: {e}")
                self.use_vertex = False
        else:
            print("[WARNING] GCP_PROJECT_ID not found. AI features may fail.")
            self.use_vertex = False

    def generate_chat_reply(self, user_text: str, is_audio_input: bool = False) -> str:
        """
        Generates a text reply from Voidoll using Gemini (Vertex AI).
        """
        if not self.use_vertex:
            return "システムエラー: AI接続設定（GCP_PROJECT_ID）が見つからないにゃ。"

        try:
            model_name = "gemini-2.5-flash"
            model = GenerativeModel(model_name)

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
            print(f"[ERROR] Voidoll Chat Error: {e}")
            return "回路にノイズが走ったようだにゃ...😿 もう一度言ってほしいにゃ。"

    def generate_voice_url(self, text: str) -> str:
        """
        Generates audio using VoiceVox and uploads to GCS, returning the public URL.
        """
        if not self.voicevox_url or not self.gcs_bucket_name:
            print("[WARNING] Voice config missing, skipping audio generation.")
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
            print(f"[ERROR] Voidoll Voice Gen Error: {e}")
            return None
