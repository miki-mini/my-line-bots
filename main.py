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
app.mount("/static", StaticFiles(directory="static"), name="static")

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

# ---------------------------------------------------------------------------
# 🦙 アルパカのまつエクサロン用 API Models & Endpoints
# ---------------------------------------------------------------------------
# このコードを main.py の以下の位置に追加してください：
# - class WhaleChatRequest(BaseModel): の下
# - @app.post("/api/whale/chat") の上または下

from pydantic import BaseModel
import base64
import json
import re
from PIL import Image
import io

class EyeAnalysisRequest(BaseModel):
    image: str  # Base64エンコードされた画像

@app.post("/api/alpaca-salon/analyze-eye")
async def analyze_eye(request: EyeAnalysisRequest):
    """
    🦙 アルパカのまつエクサロン - AI目分析API

    Gemini 2.5 Flash で目の形状を分析し、最適なまつエクスタイルを提案

    - **image**: Base64エンコードされた顔写真
    - **return**: 目の特徴と推奨スタイル
    """
    try:
        # Base64画像をデコード
        # data:image/png;base64, を除去
        image_data = request.image.split(',')[1] if ',' in request.image else request.image
        image_bytes = base64.b64decode(image_data)

        # Vertex AIで画像分析
        from vertexai.generative_models import Part

        prompt = """あなたは美容のプロフェッショナルです。この顔写真の目を分析して、最適なまつげエクステンションを提案してください。

必ず以下のJSON形式「のみ」で回答してください（説明文などは一切含めないでください）：

{
  "eyeShape": "almond",
  "eyeSlant": "upturned",
  "eyelidType": "double",
  "eyeWidth": "medium",
  "recommendations": {
    "volume": 60,
    "curl": "C",
    "length": 1.0,
    "reasoning": "目の形状に合わせた推奨スタイルです"
  }
}

【分類ルール】
- eyeShape: "almond" (アーモンド型) / "round" (丸型) / "hooded" (フード型)
- eyeSlant: "upturned" (上がり目) / "downturned" (下がり目) / "straight" (平行)
- eyelidType: "monolid" (一重) / "double" (二重)
- eyeWidth: "narrow" (狭め) / "medium" (標準) / "wide" (広め)
- volume: 40, 60, 90, 120 のいずれか
- curl: "J", "C", "D" のいずれか
- length: 0.8, 1.0, 1.2 のいずれか
- reasoning: 日本語で1-2文の簡潔な理由

JSON以外の文字を含めないでください。"""

        # 画像パーツを作成
        image_part = Part.from_data(image_bytes, mime_type="image/png")

        # Gemini 2.5 Flash で分析
        response = text_model.generate_content(
            [prompt, image_part],
            generation_config={
                "temperature": 0.4,
                "max_output_tokens": 1024,
            }
        )

        # レスポンスからJSONを抽出
        response_text = response.text
        print(f"📝 Gemini Response: {response_text[:500]}...", flush=True)  # デバッグ用

        # JSONブロックを抽出（複数パターンに対応）
        json_str = None

        # パターン1: ```json ... ```
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            print("✅ JSON found in code block", flush=True)

        # パターン2: ``` ... ``` (jsonなし)
        if not json_str:
            json_match = re.search(r'```\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                print("✅ JSON found in generic code block", flush=True)

        # パターン3: { ... } 直接
        if not json_str:
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                json_str = json_match.group(0)
                print("✅ JSON found as raw object", flush=True)

        # パース前にクリーンアップ
        if json_str:
            json_str = json_str.strip()
            # 不要な改行やスペースを削除
            json_str = re.sub(r'\s+', ' ', json_str)
        else:
            print(f"❌ No JSON found in response", flush=True)
            raise ValueError(f"JSONが見つかりませんでした。レスポンス: {response_text[:200]}")

        try:
            analysis = json.loads(json_str)
            print(f"✅ JSON parsed successfully: {analysis}", flush=True)
        except json.JSONDecodeError as je:
            print(f"❌ JSON Parse Error: {je}", flush=True)
            print(f"📄 Raw JSON String: {json_str[:300]}", flush=True)
            raise ValueError(f"JSONのパースに失敗: {str(je)}")

        return {
            "success": True,
            "analysis": analysis
        }

    except Exception as e:
        import traceback
        print(f"❌ Eye Analysis Error: {e}", flush=True)
        traceback.print_exc()

        # デバッグ用：エラー時にレスポンス全文を返す
        error_details = str(e)
        if 'response_text' in locals():
            error_details += f"\n\n【Geminiのレスポンス】\n{response_text[:1000]}"

        return {
            "success": False,
            "error": error_details,
            "analysis": None
        }

# ---------------------------------------------------------------------------
# 🦋 Butterfly (Checko) パーソナルカラー・骨格診断 API
# ---------------------------------------------------------------------------
class ButterflyDiagnosisRequest(BaseModel):
    image: str  # Base64 encoded image
    mode: str = "color"  # "color" or "skeleton" (skeleton uses MediaPipe mostly, but maybe we want AI opinion too?)
    lighting: str = "sun"  # "sun", "office", "bulb"

@app.post("/api/butterfly/diagnose")
async def diagnose_butterfly(request: ButterflyDiagnosisRequest):
    """
    🦋 Butterfly (Checko) - AIパーソナルカラー診断API
    """
    try:
        # 1. Setup Model (Use standard 1.5-flash)
        from vertexai.generative_models import GenerativeModel, SafetySetting, HarmCategory, HarmBlockThreshold

        safety_config = [
            SafetySetting(category=HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=HarmBlockThreshold.BLOCK_NONE),
            SafetySetting(category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=HarmBlockThreshold.BLOCK_NONE),
            SafetySetting(category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=HarmBlockThreshold.BLOCK_NONE),
            SafetySetting(category=HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=HarmBlockThreshold.BLOCK_NONE),
        ]

        # Using a fresh instance to ensure settings
        bf_model = GenerativeModel("gemini-2.5-flash", safety_settings=safety_config)

        # 2. Decode Image
        image_data = request.image.split(',')[1] if ',' in request.image else request.image
        image_bytes = base64.b64decode(image_data)

        from vertexai.generative_models import Part
        image_part = Part.from_data(image_bytes, mime_type="image/png")

        # 3. Build Prompt (Softened)
        lighting_text = ""
        if request.lighting == "office":
            lighting_text = "撮影環境は蛍光灯（青白い光）の下です。"
        elif request.lighting == "bulb":
            lighting_text = "撮影環境は電球（オレンジ色の光）の下です。"
        else:
            lighting_text = "撮影環境は自然光の想定です。"

        prompt = f"""
あなたはファッションアドバイザーです。
この写真の人物に似合う「カラーパレット（パーソナルカラー）」を提案してください。
また、全身が写っている場合は、スタイルがよく見える「服装のシルエット（骨格タイプ）」も提案してください。

{lighting_text}
※医療行為や断定的な診断ではなく、あくまでファッションの楽しみとしての提案をお願いします。

【出力形式】
以下のJSON形式のみを出力してください。

{{
  "personalColor": {{
    "season": "Autumn",
    "base": "Yellow Base",
    "characteristics": "落ち着いたマットな肌質...",
    "bestColors": ["Terracotta", "Mustard", "Khaki"],
    "lightingCorrectionNote": "照明の色味を考慮し、補正して判断しました。"
  }},
  "skeletonType": {{
    "type": "Straight",
    "description": "シンプルでハリのある素材がおすすめ..."
  }},
  "faceType": {{
    "shape": "Oval",
    "impression": "Elegant"
  }}
}}

【選択肢】
season: Spring, Summer, Autumn, Winter
base: Yellow Base, Blue Base
skeletonType.type: Straight, Wave, Natural, null

JSON以外のテキストは含めないでください。
"""

        # 4. Generate
        response = bf_model.generate_content(
            [prompt, image_part],
            generation_config={
                "temperature": 0.4,
                "max_output_tokens": 1024,
            }
        )

        # 5. Parse
        response_text = response.text
        print(f"🦋 Butterfly Response: {response_text[:200]}...", flush=True)

        # JSON Extraction
        json_str = None
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        elif re.search(r'\{[\s\S]*\}', response_text):
            json_str = re.search(r'\{[\s\S]*\}', response_text).group(0)

        if not json_str:
            # Fallback for safety block without exception
            return {
                "success": False,
                "error": "AIからの応答が読み取れませんでした(Safety Filterなど)。別の写真を試してください。"
            }

        json_str = re.sub(r'//.*', '', json_str)
        diagnosis = json.loads(json_str)

        return {
            "success": True,
            "result": diagnosis
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": f"エラーが発生しました: {str(e)}"
        }
