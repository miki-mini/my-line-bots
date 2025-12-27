import logging
import os
import uuid
from datetime import datetime, timedelta, date
import requests
import json
import time
import re
import traceback
import io
import uvicorn

# ========================================
# Vertex AI（検索機能 & 画像生成で使う）
# ========================================
import vertexai
from vertexai.generative_models import (
    GenerativeModel,
    Part,
    Tool as VertexTool,
    grounding
)
from vertexai.preview.vision_models import ImageGenerationModel

# ========================================
# Google Generative AI（一部のボットで使う）
# ========================================
import google.generativeai as genai

# ========================================
# その他
# ========================================
from PIL import Image
import googlemaps
from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration
from linebot.v3.messaging import ApiClient
from linebot.v3.messaging import MessagingApi
from linebot.v3.messaging import ReplyMessageRequest
from linebot.v3.messaging import TextMessage
from linebot.v3.messaging import BroadcastRequest
from linebot.v3.messaging import MessagingApiBlob
from linebot.v3.messaging import AudioMessage
from linebot.v3.messaging import PushMessageRequest
from linebot.v3.webhooks import MessageEvent
from linebot.v3.webhooks import TextMessageContent
from linebot.v3.webhooks import AudioMessageContent
from linebot.v3.webhooks import ImageMessageContent
from linebot.v3.webhooks import LocationMessageContent
from google.cloud import storage
from google.cloud import firestore

import matplotlib.pyplot as plt
import japanize_matplotlib
from fastapi.responses import StreamingResponse
import pandas as pd
from fastapi.responses import HTMLResponse


# ========================================
# 🦊🐸🐧🦡🤖🐹🦉🐋🦫
from animals.fox import register_fox_handler
from animals.frog import register_frog_handler
from animals.penguin import register_penguin_handler
from animals.mole import register_mole_handler
from animals.voidoll import register_voidoll_handler
from animals.capybara import register_capybara_handler
from animals.owl import register_owl_handler
from animals.whale import register_whale_handler
from animals.beaver import register_beaver_handler
from animals.bat import register_bat_handler

# ========================================

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


# --- グローバル変数 ---
image_model = None
text_model = None
vision_model = None
search_model = None
startup_errors = []
app = FastAPI()
storage_client = None

GCS_BUCKET_NAME = None
db = None
model = None
load_dotenv()

GAS_MAIL_WEB_APP_URL = os.environ.get("GAS_MAIL_WEB_APP_URL")

# Google Mapsの設定
GMAPS_API_KEY = os.environ.get("GMAPS_API_KEY")
gmaps = googlemaps.Client(key=GMAPS_API_KEY)

# --- 🤖 各ボットの設定 ---
# 🦡 もぐら駅長
configuration_train = Configuration(access_token=os.getenv("TRAIN_ACCESS_TOKEN"))
handler_train = WebhookHandler(os.getenv("TRAIN_CHANNEL_SECRET"))

# 🤖 ボイドール
configuration_voidoll = Configuration(access_token=os.getenv("VOIDOLL_ACCESS_TOKEN"))
handler_voidoll = WebhookHandler(os.getenv("VOIDOLL_CHANNEL_SECRET"))

# 🐸 カエル
configuration_frog = Configuration(access_token=os.getenv("FROG_ACCESS_TOKEN"))
handler_frog = WebhookHandler(os.getenv("FROG_CHANNEL_SECRET"))

# 🐧 ペンギン
configuration_penguin = Configuration(access_token=os.getenv("PENGUIN_ACCESS_TOKEN"))
handler_penguin = WebhookHandler(os.getenv("PENGUIN_CHANNEL_SECRET"))

# 🦊 キツネ
LINE_TOKEN_FOX = os.getenv("FOX_ACCESS_TOKEN")
LINE_SECRET_FOX = os.getenv("FOX_CHANNEL_SECRET")
configuration_fox = (Configuration(access_token=LINE_TOKEN_FOX) if LINE_TOKEN_FOX else None)
handler_fox = WebhookHandler(LINE_SECRET_FOX) if LINE_SECRET_FOX else None

# 🐹 カピバラ
configuration_capybara = Configuration(access_token=os.getenv("CAPYBARA_ACCESS_TOKEN"))
handler_capybara = WebhookHandler(os.getenv("CAPYBARA_CHANNEL_SECRET"))

# 🐋 星くじら
configuration_whale = Configuration(access_token=os.getenv("WHALE_ACCESS_TOKEN"))
handler_whale = WebhookHandler(os.getenv("WHALE_CHANNEL_SECRET"))

# 🦫 ビーバー
configuration_beaver = Configuration(access_token=os.getenv("BEAVER_ACCESS_TOKEN"))
handler_beaver = WebhookHandler(os.getenv("BEAVER_CHANNEL_SECRET"))

# 🦇 テレビコウモリ
LINE_TOKEN_BAT = os.getenv("BAT_ACCESS_TOKEN")
LINE_SECRET_BAT = os.getenv("BAT_CHANNEL_SECRET")
configuration_bat = (Configuration(access_token=LINE_TOKEN_BAT) if LINE_TOKEN_BAT else None)
handler_bat = WebhookHandler(LINE_SECRET_BAT) if LINE_SECRET_BAT else None

# --- ボイドール用クライアント ---
api_client_voidoll = ApiClient(configuration_voidoll)
line_bot_api_voidoll = MessagingApi(api_client_voidoll)
line_bot_blob_api_voidoll = MessagingApiBlob(api_client_voidoll)

# Gemini API設定
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


@app.on_event("startup")
def startup_event():
    print("🚀 起動プロセス開始 (SAFE MODE)...", flush=True)
    pass
    # GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
    # if not GCP_PROJECT_ID:
    #     print("⚠️ GCP_PROJECT_ID not found in env, using fallback: usaginooekaki", flush=True)
    #     GCP_PROJECT_ID = "usaginooekaki"

    # GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
    # ...


# ========================================
# ========================================
# ヘルスチェック
# ========================================
@app.get("/", response_class=HTMLResponse)
def index():
    """Botのポータル画面を表示"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Portal is coming soon!</h1><p>Please check back later.</p>")


@app.get("/health")
def health_check_detail():
    """ヘルスチェック＆モデル状態確認"""
    try:
        return {
            "status": "ok",
            "models": {
                "text_model": text_model is not None,
                "vision_model": vision_model is not None,
                "search_model": search_model is not None,
                "image_model": image_model is not None,
            },
            "search_enabled": (
                search_model is not None
                and text_model is not None
                and id(search_model) != id(text_model)
            ),
            "search_model_type": type(search_model).__name__ if search_model else None,
            "text_model_type": type(text_model).__name__ if text_model else None,
            "startup_errors": startup_errors if startup_errors else [],
            "has_tools": hasattr(search_model, "_tools") if search_model else False,
            "tools_count": (
                len(getattr(search_model, "_tools", [])) if search_model else 0
            ),
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "error_type": type(e).__name__}


# ========================================
# 汎用エンドポイント
# ========================================
class GenerateRequest(BaseModel):
    prompt: str


@app.post("/generate")
def generate_text_endpoint(req: GenerateRequest):
    try:
        res = genai.GenerativeModel("gemini-2.5-flash").generate_content(req.prompt)
        return {"response_text": res.text}
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.post("/generate-image")
def generate_image_endpoint(req: GenerateRequest):
    try:
        from vertexai.vision_models import ImageGenerationModel
        import vertexai

        vertexai.init(project=os.getenv("GCP_PROJECT_ID"), location="asia-northeast1")

        model = ImageGenerationModel.from_pretrained("imagen-3.0-fast-generate-001")
        imgs = model.generate_images(prompt=req.prompt, number_of_images=1)

        client = storage.Client()
        blob = client.bucket(os.getenv("GCS_BUCKET_NAME")).blob(
            f"owl-{uuid.uuid4()}.png"
        )
        blob.upload_from_string(imgs[0]._image_bytes, content_type="image/png")
        blob.make_public()

        return {"image_url": blob.public_url}
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.get("/debug-grounding")
def debug_grounding():
    """grounding の使用可能なメソッドを確認"""
    try:
        from vertexai.generative_models import grounding, Tool

        return {
            "grounding_attrs": [a for a in dir(grounding) if not a.startswith('_')],
            "tool_attrs": [a for a in dir(Tool) if not a.startswith('_')],
            "has_GoogleSearchRetrieval": hasattr(grounding, 'GoogleSearchRetrieval'),
            "has_from_google_search_retrieval": hasattr(Tool, 'from_google_search_retrieval'),
        }
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}