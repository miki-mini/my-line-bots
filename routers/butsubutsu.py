from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import base64
import os
import hashlib
from google.cloud import texttospeech, firestore
from vertexai.generative_models import GenerativeModel, SafetySetting, HarmCategory, HarmBlockThreshold

router = APIRouter(
    prefix="/api/butsubutsu",
    tags=["butsubutsu"]
)

# Models
class TranslateRequest(BaseModel):
    text: str

class SpeakRequest(BaseModel):
    text: str

# Helper to get TTS Client
def get_tts_client():
    return texttospeech.TextToSpeechClient()

# Helper to get Gemini Model
def get_gemini_model():
    safety_config = [
        SafetySetting(category=HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=HarmBlockThreshold.BLOCK_NONE),
        SafetySetting(category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=HarmBlockThreshold.BLOCK_NONE),
        SafetySetting(category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=HarmBlockThreshold.BLOCK_NONE),
        SafetySetting(category=HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=HarmBlockThreshold.BLOCK_NONE),
    ]
    return GenerativeModel("gemini-2.5-flash", safety_settings=safety_config)

# Helper for Firestore (Lazy Init)
_db = None
def get_db():
    global _db
    if _db is None:
        try:
            _db = firestore.Client()
        except Exception as e:
            print(f"⚠️ Firestore Init Error: {e}")
            return None
    return _db

@router.post("/translate")
async def translate_mumble(request: TranslateRequest):
    """
    Translates user mumble (Japanese/English) to cool, native English.
    """
    try:
        # Check Cache
        db = get_db()
        doc_ref = None

        if db:
            try:
                # Hash the input text to create a document ID
                doc_id = hashlib.sha256(request.text.encode("utf-8")).hexdigest()
                doc_ref = db.collection("wolf_translations").document(doc_id)
                doc = doc_ref.get()

                if doc.exists:
                    print(f"[CACHE] Using Cached Translation for: {request.text[:10]}...")
                    return {"english_text": doc.to_dict()["english_text"]}
            except Exception as e:
                print(f"[WARNING] Firestore Read Error (Proceeding without cache): {e}")
                doc_ref = None

        model = get_gemini_model()
        prompt = f"""
        あなたは日本語ネイティブが独り言で言いそうなフレーズを、ネイティブ英語話者が同じシチュエーションで自然に言う英語に変換する翻訳者です。

        重要なルール:
        - 直訳ではなく、英語話者が同じ感情・状況で実際に口にする表現にする
        - 日本語の感情やニュアンス（喜び、イライラ、疲れ、達成感など）をそのまま英語で表現する
        - カジュアルな独り言なので、堅い表現は避ける
        - 短く、自然に口から出る表現にする
        - 説明や文法解説は一切不要。英語のみ出力

        例:
        - 「めっちゃ疲れた」→ "I'm so done."
        - 「やばい、遅刻する」→ "Crap, I'm gonna be late."
        - 「今日のプレゼンうまくいった！」→ "Nailed it today!"
        - 「だるい」→ "Ugh, I can't be bothered."
        - 「腹減った」→ "Man, I'm starving."

        ユーザーの独り言: "{request.text}"
        """

        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.7, "max_output_tokens": 512}
        )

        english_text = response.text.strip()

        # Save to Cache
        if doc_ref:
            try:
                doc_ref.set({
                    "original_text": request.text,
                    "english_text": english_text,
                    "created_at": firestore.SERVER_TIMESTAMP
                })
            except Exception as e:
                print(f"⚠️ Firestore Write Error (Proceeding): {e}")

        return {"english_text": english_text}
    except Exception as e:
        print(f"❌ Translation Error: {e}")
        return {"error": str(e), "english_text": "I'm speechless..."}

@router.post("/speak")
async def speak_text(request: SpeakRequest):
    """
    Generates TTS audio for the given English text.
    """
    try:
        if not request.text:
             return {"error": "No text provided"}

        # Check Cache
        db = get_db()
        doc_ref = None

        if db:
            try:
                doc_id = hashlib.sha256(request.text.encode("utf-8")).hexdigest()
                doc_ref = db.collection("wolf_tts").document(doc_id)
                doc = doc_ref.get()

                if doc.exists:
                    print(f"🔊 Using Cached Audio for: {request.text[:10]}...")
                    return {"audio_content": doc.to_dict()["audio_content"]}
            except Exception as e:
                print(f"⚠️ Firestore Read Error (Proceeding without cache): {e}")
                doc_ref = None

        client = get_tts_client()
        synthesis_input = texttospeech.SynthesisInput(text=request.text)

        # Build the voice request, select the language code ("en-US") and the ssml voice gender ("NEUTRAL")
        # We can make it more specific/cool later
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Journey-F", # A generally pleasant, expressive voice
            # ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
             speaking_rate=0.9 # Slightly slower for shadowing initially? Or let frontend handle speed (frontend can't checking playbackRate, but TTS generation speed is fixed here. 0.9 is safe)
        )

        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # The response's audio_content is binary.
        audio_base64 = base64.b64encode(response.audio_content).decode("utf-8")

        # Save to Cache (Be careful with FireStore size limits, base64 audio is big but usually ok for short phrases)
        # Max document size is 1MB. A short sentence MP3 is only a few KB.
        if doc_ref:
            try:
                doc_ref.set({
                    "text": request.text,
                    "audio_content": audio_base64,
                    "created_at": firestore.SERVER_TIMESTAMP
                })
            except Exception as e:
                print(f"⚠️ Failed to cache audio: {e}")

        return {"audio_content": audio_base64}

    except Exception as e:
        print(f"❌ TTS Error: {e}")
        # If credentials fail or API not enabled, returning a clear error is helpful.
        return {"error": str(e)}
