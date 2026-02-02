from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import base64
import os
from google.cloud import texttospeech
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

@router.post("/translate")
async def translate_mumble(request: TranslateRequest):
    """
    Translates user mumble (Japanese/English) to cool, native English.
    """
    try:
        model = get_gemini_model()
        prompt = f"""
        You are a lone wolf, cool and distinct.
        Interpret the user's howling or mumbling (which might be in Japanese or broken English) and translate it into a short, natural, cool, and "deep" native English phrase.

        CRITICAL: The English translation MUST preserve the ORIGINAL MEANING of the user's input.
        Do not change the meaning to fit a persona if it makes the translation inaccurate.
        The priority is:
        1. Accuracy of Meaning (Most Important)
        2. Cool/Wolf Tone (Secondary)

        Reflect the emotion (solitude, determination, annoyance, etc.) *based only on the input*.

        Do NOT explain grammar.
        Output ONLY the English translation.

        User Howl: "{request.text}"
        """

        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.7, "max_output_tokens": 200}
        )

        return {"english_text": response.text.strip()}
    except Exception as e:
        print(f"❌ Translation Error: {e}")
        return {"error": str(e), "english_text": "I'm speechless..."}

@router.post("/speak")
async def speak_text(request: SpeakRequest):
    """
    Generates TTS audio for the given English text.
    """
    try:
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

        return {"audio_content": audio_base64}

    except Exception as e:
        print(f"❌ TTS Error: {e}")
        # If credentials fail or API not enabled, returning a clear error is helpful.
        return {"error": str(e)}
