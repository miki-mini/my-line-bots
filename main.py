import os
import uvicorn
from fastapi import FastAPI, Request, BackgroundTasks, Depends
from core.auth_handler import get_current_username
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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

# Animal Handler Import (All Animals)
from animals.mole import register_mole_handler
from animals.fox import register_fox_handler
from animals.frog import register_frog_handler
from animals.penguin import register_penguin_handler
from animals.voidoll import register_voidoll_handler
from animals.capybara import register_capybara_handler
from animals.whale import register_whale_handler, get_whale_reply_content # Imported new function
from animals.beaver import register_beaver_handler
from animals.bat import register_bat_handler
from animals.owl import register_owl_handler

from routers import web_apps
from animals import beaver, fox, bat, mole, frog, capybara, penguin, owl

# Google Cloud Imports
from google.cloud import storage
from google.cloud import firestore

# ---------------------------------------------------------------------------
# GLOBAL VARIABLES
# ---------------------------------------------------------------------------
# GLOBAL VARIABLES
# ---------------------------------------------------------------------------
app = FastAPI()
app.include_router(web_apps.router)
app.include_router(beaver.router)
app.include_router(fox.router)
app.include_router(bat.router)
app.include_router(mole.router)
app.include_router(frog.router)

app.include_router(capybara.router)
app.include_router(penguin.router)
app.include_router(owl.router)
db = None
storage_client = None
text_model = None
search_model = None  # Added for Owl/Capybara/Fox RAG
startup_errors = []

# ---------------------------------------------------------------------------
# AUTHENTICATION (Basic Auth)
# ---------------------------------------------------------------------------
# Authentication logic moved to core/security.py

# ---------------------------------------------------------------------------
# SEARCH MODEL WRAPPER (Restored for Owl/Search features)
# ---------------------------------------------------------------------------
class SearchModelWrapper:
    """動物たちが今まで通り使えるようにするラッパー"""

    def __init__(self, project_id, location="asia-northeast1"):
        from google import genai
        from google.genai import types

        self.client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location
        )
        self.model_name = "gemini-2.5-flash"
        self.types = types

    def generate_content(self, prompt, generation_config=None):
        """今まで通りの呼び出し方で使える"""
        from google.genai import types

        config_dict = {
            "tools": [types.Tool(google_search=types.GoogleSearch())]
        }

        if generation_config:
            if "temperature" in generation_config:
                config_dict["temperature"] = generation_config["temperature"]
            if "max_output_tokens" in generation_config:
                config_dict["max_output_tokens"] = generation_config["max_output_tokens"]

        config = types.GenerateContentConfig(**config_dict)

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=config
        )
        return response

load_dotenv()

# Webhook Handler (Main)
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
handler = WebhookHandler(LINE_CHANNEL_SECRET) if LINE_CHANNEL_SECRET else None
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN) if LINE_CHANNEL_ACCESS_TOKEN else None

# 🦡 Mole (Train) Bot Settings
TRAIN_ACCESS_TOKEN = os.getenv("TRAIN_ACCESS_TOKEN")
TRAIN_CHANNEL_SECRET = os.getenv("TRAIN_CHANNEL_SECRET")
configuration_train = Configuration(access_token=TRAIN_ACCESS_TOKEN) if TRAIN_ACCESS_TOKEN else None
handler_train = WebhookHandler(TRAIN_CHANNEL_SECRET) if TRAIN_CHANNEL_SECRET else None

# 🦊 Fox (YouTube) Bot Settings
FOX_ACCESS_TOKEN = os.getenv("FOX_ACCESS_TOKEN")
FOX_CHANNEL_SECRET = os.getenv("FOX_CHANNEL_SECRET")
configuration_fox = Configuration(access_token=FOX_ACCESS_TOKEN) if FOX_ACCESS_TOKEN else None
handler_fox = WebhookHandler(FOX_CHANNEL_SECRET) if FOX_CHANNEL_SECRET else None

# 🐸 Frog (Weather) Bot Settings
FROG_ACCESS_TOKEN = os.getenv("FROG_ACCESS_TOKEN")
FROG_CHANNEL_SECRET = os.getenv("FROG_CHANNEL_SECRET")
configuration_frog = Configuration(access_token=FROG_ACCESS_TOKEN) if FROG_ACCESS_TOKEN else None
handler_frog = WebhookHandler(FROG_CHANNEL_SECRET) if FROG_CHANNEL_SECRET else None

# 🐧 Penguin (Concierge) Bot Settings
PENGUIN_ACCESS_TOKEN = os.getenv("PENGUIN_ACCESS_TOKEN")
PENGUIN_CHANNEL_SECRET = os.getenv("PENGUIN_CHANNEL_SECRET")
configuration_penguin = Configuration(access_token=PENGUIN_ACCESS_TOKEN) if PENGUIN_ACCESS_TOKEN else None
handler_penguin = WebhookHandler(PENGUIN_CHANNEL_SECRET) if PENGUIN_CHANNEL_SECRET else None

# 🤖 Voidoll (Voice) Bot Settings
VOIDOLL_ACCESS_TOKEN = os.getenv("VOIDOLL_ACCESS_TOKEN")
VOIDOLL_CHANNEL_SECRET = os.getenv("VOIDOLL_CHANNEL_SECRET")
configuration_voidoll = Configuration(access_token=VOIDOLL_ACCESS_TOKEN) if VOIDOLL_ACCESS_TOKEN else None
handler_voidoll = WebhookHandler(VOIDOLL_CHANNEL_SECRET) if VOIDOLL_CHANNEL_SECRET else None

# 🐹 Capybara (Relax) Bot Settings
CAPYBARA_ACCESS_TOKEN = os.getenv("CAPYBARA_ACCESS_TOKEN")
CAPYBARA_CHANNEL_SECRET = os.getenv("CAPYBARA_CHANNEL_SECRET")
configuration_capybara = Configuration(access_token=CAPYBARA_ACCESS_TOKEN) if CAPYBARA_ACCESS_TOKEN else None
handler_capybara = WebhookHandler(CAPYBARA_CHANNEL_SECRET) if CAPYBARA_CHANNEL_SECRET else None

# 🐋 Whale (Space) Bot Settings
WHALE_ACCESS_TOKEN = os.getenv("WHALE_ACCESS_TOKEN")
WHALE_CHANNEL_SECRET = os.getenv("WHALE_CHANNEL_SECRET")
configuration_whale = Configuration(access_token=WHALE_ACCESS_TOKEN) if WHALE_ACCESS_TOKEN else None
handler_whale = WebhookHandler(WHALE_CHANNEL_SECRET) if WHALE_CHANNEL_SECRET else None

# 🦫 Beaver (OCR) Bot Settings
BEAVER_ACCESS_TOKEN = os.getenv("BEAVER_ACCESS_TOKEN")
BEAVER_CHANNEL_SECRET = os.getenv("BEAVER_CHANNEL_SECRET")
configuration_beaver = Configuration(access_token=BEAVER_ACCESS_TOKEN) if BEAVER_ACCESS_TOKEN else None
handler_beaver = WebhookHandler(BEAVER_CHANNEL_SECRET) if BEAVER_CHANNEL_SECRET else None

# 🦇 Bat (TV) Bot Settings
BAT_ACCESS_TOKEN = os.getenv("BAT_ACCESS_TOKEN")
BAT_CHANNEL_SECRET = os.getenv("BAT_CHANNEL_SECRET")
configuration_bat = Configuration(access_token=BAT_ACCESS_TOKEN) if BAT_ACCESS_TOKEN else None
handler_bat = WebhookHandler(BAT_CHANNEL_SECRET) if BAT_CHANNEL_SECRET else None

# 🦉 Owl (Diet/Search) Bot Settings
# Owl uses HTTP endpoints mostly, but may have LINE settings for future use
OWL_ACCESS_TOKEN = os.getenv("OWL_ACCESS_TOKEN")
OWL_CHANNEL_SECRET = os.getenv("OWL_CHANNEL_SECRET")
# Backup didn't show Owl config vars, but we can define them for safety or skip.
# Based on register_owl_handler(app), it doesn't take config args.

from routers import web_apps



# 🐰 Rabbit (Moon) Bot Settings
RABBIT_ACCESS_TOKEN = os.getenv("RABBIT_ACCESS_TOKEN")
RABBIT_CHANNEL_SECRET = os.getenv("RABBIT_CHANNEL_SECRET")
configuration_rabbit = Configuration(access_token=RABBIT_ACCESS_TOKEN) if RABBIT_ACCESS_TOKEN else None
handler_rabbit = WebhookHandler(RABBIT_CHANNEL_SECRET) if RABBIT_CHANNEL_SECRET else None

# Helper for debugging
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
# Include Routers (Available at startup)
# app.include_router(web_apps.router) is already included at the top

# Static Files Mount (Ensure images/CSS are served)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def startup_event():
    global text_model, db, storage_client, GCS_BUCKET_NAME, search_model
    try:
        print("🚀 PHASE 1 RESTORATION STARTUP...", flush=True)

        # Initialize Google Cloud Resources
        if GCP_PROJECT_ID:
            # 1. Vertex AI
            vertexai.init(project=GCP_PROJECT_ID, location="asia-northeast1")

            safety_config = [
                SafetySetting(category=HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=HarmBlockThreshold.BLOCK_NONE),
                SafetySetting(category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=HarmBlockThreshold.BLOCK_NONE),
                SafetySetting(category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=HarmBlockThreshold.BLOCK_NONE),
                SafetySetting(category=HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=HarmBlockThreshold.BLOCK_NONE),
            ]

            text_model = GenerativeModel("gemini-2.5-flash", safety_settings=safety_config)
            print("✅ Gemini (text_model) Initialized!", flush=True)

            # Initialize Search Model (The Owl) via Wrapper
            try:
                search_model = SearchModelWrapper(project_id=GCP_PROJECT_ID)
                print("✅ Compass (Search Model) Initialized!", flush=True)
            except Exception as sm_err:
                print(f"⚠️ Search Model Init Failed: {sm_err}", flush=True)
                search_model = None

            # 2. Firestore & Storage
            db = firestore.Client(project=GCP_PROJECT_ID)
            storage_client = storage.Client(project=GCP_PROJECT_ID)
            GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
            print("✅ Firestore & Storage Initialized!", flush=True)

            # ---------------------------
            # Register Animal Handlers
            # ---------------------------

            # 1. Mole (4 args)
            register_mole_handler(app, handler_train, configuration_train, text_model)
            print("🦡 Mole Registered!", flush=True)

            # 2. Fox (5 args) - Now passing search_model!
            register_fox_handler(app, handler_fox, configuration_fox, search_model, text_model)
            print("🦊 Fox Registered!", flush=True)

            # 3. Frog (5 args) - Now passing search_model!
            register_frog_handler(app, handler_frog, configuration_frog, search_model, text_model)
            print("🐸 Frog Registered!", flush=True)

            # 4. Penguin (4 args)
            register_penguin_handler(app, handler_penguin, configuration_penguin, text_model)
            print("🐧 Penguin Registered!", flush=True)

            # 7. Owl (フクロウ) - Router化済みのため関数呼び出し不要 (Deprecated)
            # register_owl_handler(app, None)

            # 8. Voidoll (ボイドール)
            register_voidoll_handler(app, handler_voidoll, text_model)
            print(" Voidoll Registered!", flush=True)

            # 6. Capybara (5 args: app, handler, config, search_model, text_model)
            register_capybara_handler(app, handler_capybara, configuration_capybara, search_model, text_model)
            print(" Capybara Registered!", flush=True)

            # 7. Whale (4 args: app, handler, config, model) -> Passing text_model
            register_whale_handler(app, handler_whale, configuration_whale, text_model)
            print("🐋 Whale Registered!", flush=True)

            # 8. Beaver (5 args: app, handler, config, db, text_model)
            register_beaver_handler(app, handler_beaver, configuration_beaver, db, text_model)
            print("🦫 Beaver Registered!", flush=True)

            # 9. Bat (5 args: app, handler, config, search_model, db)
            register_bat_handler(app, handler_bat, configuration_bat, search_model, db)
            print("🦇 Bat Registered!", flush=True)





        else:
            print("⚠️ GCP_PROJECT_ID not set, skipping AI init", flush=True)

    except Exception as e:
        import traceback
        print(f"❌ Startup Error: {e}", flush=True)
        traceback.print_exc()  # ← 詳細なエラーを表示

@app.post("/callback")
async def callback(request: Request):
    signature = request.headers["x-line-signature"]
    body = await request.body()
    body_str = body.decode("utf-8")

    try:
        if handler:
            handler.handle(body_str, signature)
    except InvalidSignatureError:
        return HTMLResponse(content="Invalid signature", status_code=400)

    return "OK"

# ---------------------------------------------------------------------------
# API Models
# ---------------------------------------------------------------------------
class WhaleChatRequest(BaseModel):
    text: str

@app.post("/api/whale/chat")
async def chat_whale(request: WhaleChatRequest):
    """
    星くじらとチャットするAPI

    - **text**: ユーザーからのメッセージ
    - **return**: 星くじらからの返信（テキスト、画像URLなど）
    """
    # グローバル変数のtext_modelを使用
    # text_modelはstartup時に初期化される
    response = get_whale_reply_content(request.text, text_model)
    return {"results": response}

# Endpoints (Web Apps moved to routers/web_apps.py)
# Authentication logic moved to core/security.py

# Index route is handled by web_apps.py

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)