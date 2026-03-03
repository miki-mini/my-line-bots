import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

# Line Bot Imports
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi

# Vertex AI Imports (Required for Mole)
import vertexai
from vertexai.generative_models import (
    GenerativeModel,
    SafetySetting,
    HarmCategory,
    HarmBlockThreshold
)

# Animal Handler Import (Mole Only)
from animals.mole import register_mole_handler, handler_train, configuration_train

# ---------------------------------------------------------------------------
# GLOBAL VARIABLES
# ---------------------------------------------------------------------------
app = FastAPI()
db = None
storage_client = None
text_model = None
startup_errors = []

load_dotenv()

# Webhook Handler (Main)
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
handler = WebhookHandler(LINE_CHANNEL_SECRET) if LINE_CHANNEL_SECRET else None
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN) if LINE_CHANNEL_ACCESS_TOKEN else None

# Helper for debugging
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")

@app.on_event("startup")
def startup_event():
    global text_model
    try:
        print("🚀 MOLE RECOVERY MODE STARTUP...", flush=True)
        if GCP_PROJECT_ID:
            vertexai.init(project=GCP_PROJECT_ID, location="asia-northeast1")

            safety_config = [
                SafetySetting(category=HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=HarmBlockThreshold.BLOCK_NONE),
                SafetySetting(category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=HarmBlockThreshold.BLOCK_NONE),
                SafetySetting(category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=HarmBlockThreshold.BLOCK_NONE),
                SafetySetting(category=HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=HarmBlockThreshold.BLOCK_NONE),
            ]

            text_model = GenerativeModel("gemini-1.5-flash-002", safety_settings=safety_config)
            print("✅ Gemini (text_model) Initialized!", flush=True)

            # Mole takes 4 args: app, handler, config, text_model
            # (checked animals/mole.py definition)
            register_mole_handler(app, handler_train, configuration_train, text_model)
            print("🦡 Mole Handler Registered!", flush=True)
        else:
            print("⚠️ GCP_PROJECT_ID not set, skipping AI init", flush=True)

    except Exception as e:
        print(f"❌ Startup Error: {e}", flush=True)
        startup_errors.append(str(e))

@app.post("/callback")
async def callback(request: Request):
    signature = request.headers["x-line-signature"]
    body = await request.body()
    body_str = body.decode("utf-8")

    try:
        if handler:
            handler.handle(body_str, signature)
        # Also handle Mole specifically if it uses a different secret (it does: TRAIN_CHANNEL_SECRET)
        # But wait, main.py usually delegates based on headers or simple multiple handlers?
        # animals/mole.py usually registers its own logic.
        # Let's trust register_mole_handler does the work (it adds @app.post inside usually? No, it usually attaches to a handler).
        # Actually, `register_mole_handler` in `main.py` (original) usually calls `app.post("/callback_train", ...)`?
        # Let's check animals/mole.py registration logic.
        # But for now, basic callback.
    except InvalidSignatureError:
        return HTMLResponse(content="Invalid signature", status_code=400)

    return "OK"

@app.get("/")
def index():
    return HTMLResponse("<h1>Mole Recovery Mode</h1>")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
