from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import json
import base64
from vertexai.generative_models import GenerativeModel, Part, SafetySetting, HarmCategory, HarmBlockThreshold
from google.cloud import firestore

router = APIRouter()

# --- Gemini Model Setup ---
# Initialize inside functions or globally in main.py if shared.
# For now, we'll assume a shared text_model is passed or initialized here.
# We will initialize a specific instance for Raccoon to ensure precise system instructions.

def get_gemini_model():
    # Helper to get a fresh model instance with specific settings
    safety_config = [
        SafetySetting(category=HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=HarmBlockThreshold.BLOCK_NONE),
        SafetySetting(category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=HarmBlockThreshold.BLOCK_NONE),
        SafetySetting(category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=HarmBlockThreshold.BLOCK_NONE),
        SafetySetting(category=HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=HarmBlockThreshold.BLOCK_NONE),
    ]
    return GenerativeModel("gemini-2.5-flash", safety_settings=safety_config)

# --- Pydantic Models ---

class ImageRequest(BaseModel):
    image: str # Base64 encoded

class BattleStartResponse(BaseModel):
    monster_name: str
    monster_level: int
    monster_hp: int
    monster_max_hp: int
    description: str
    monster_image_prompt: str # To generate an image or pick a preset

class BattleAttackRequest(BaseModel):
    before_image: Optional[str] = None # Base64
    after_image: str # Base64
    current_hp: int

class BattleAttackResponse(BaseModel):
    damage: int
    remaining_hp: int
    message: str
    advice: str
    is_defeated: bool

class GachaResponse(BaseModel):
    tasks: List[str]

class TaskCompleteRequest(BaseModel):
    task_id: int
    image: Optional[str] = None # Proof (optional)

class ManiaResponse(BaseModel):
    fit_score: int
    advice: str
    visual_overlay: Optional[str] = None

class PushSubscription(BaseModel):
    endpoint: str
    keys: dict

# --- Endpoints ---

@router.post("/api/raccoon/battle/start", response_model=BattleStartResponse)
async def start_battle(req: ImageRequest):
    """子供モード：部屋の画像からモンスターを生成"""
    try:
        model = get_gemini_model()

        # Decode image
        image_data = req.image.split(',')[1] if ',' in req.image else req.image
        image_bytes = base64.b64decode(image_data)
        image_part = Part.from_data(image_bytes, mime_type="image/jpeg")

        prompt = """
        あなたは子供向けの片付けRPGのゲームマスターです。
        送られてきた部屋の画像（散らかり具合）を分析して、その汚さを具現化した「ゴミゴミ・モンスター」を生成してください。

        以下のJSON形式のみで出力してください:
        {
          "monster_name": "散らかりの王・クツシタ",
          "monster_level": 15,
          "monster_hp": 300,
          "monster_max_hp": 300,
          "description": "脱ぎっぱなしの靴下が原因で生まれた。かなり臭いぞ！",
          "monster_image_prompt": "A cute cartoon monster made of pile of dirty colorful socks, rpg style, white background"
        }

        レベルとHPは散らかり具合に応じて変えてください（少し散らかってる=Lv5, 激ヤバ=Lv50など）。
        """

        response = model.generate_content(
            [prompt, image_part],
            generation_config={"response_mime_type": "application/json"}
        )

        return json.loads(response.text)

    except Exception as e:
        print(f"Error in start_battle: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/raccoon/battle/attack", response_model=BattleAttackResponse)
async def attack_monster(req: BattleAttackRequest):
    """子供モード：片付け後の画像でダメージ計算"""
    try:
        if not req.before_image:
             # If no before image, just give a generic small damage or error.
             # For simplicity, let's assume valid play.
             pass

        model = get_gemini_model()

        # Decode images
        # NOTE: In a real app, before_image might be a URL or ID. Here we expect base64 for simplicity of prototype.
        # However, sending 2 images might be heavy. Let's assume frontend sends both for now.

        after_data = req.after_image.split(',')[1] if ',' in req.after_image else req.after_image
        after_bytes = base64.b64decode(after_data)
        after_part = Part.from_data(after_bytes, mime_type="image/jpeg")

        # Optional: Compare with before image if provided
        inputs = ["""
        あなたは子供向けの片付けRPGのゲームマスターです。
        「片付け後の部屋」の写真を分析して、モンスターへのダメージを計算してください。

        判定基準：
        - 床が見えてきたか？
        - モノが減ったか？
        - 整理整頓されたか？

        以下のJSON形式のみで出力してください:
        {
            "damage": 50,
            "remaining_hp": 0,
            "message": "すごい！床が見えてきた！50ダメージ！アタック成功！",
            "advice": "まだ机の上に本が散らばっているよ。次は本を本棚に戻そう！",
            "is_defeated": false
        }

        ※ remaining_hp は current_hp から damage を引いた値にしてください。0以下なら is_defeated=true。
        ※ advice には、まだ散らかっている部分や、次に何を片付ければいいかを具体的に「子供にもわかる言葉」で書いてください。これ以上片付ける場所がない場合は空文字でOK。
        """]

        inputs.append(f"現在のモンスターHP: {req.current_hp}")
        inputs.append(after_part)

        if req.before_image:
            before_data = req.before_image.split(',')[1] if ',' in req.before_image else req.before_image
            before_bytes = base64.b64decode(before_data)
            before_part = Part.from_data(before_bytes, mime_type="image/jpeg")
            inputs.insert(1, "【Before: 片付け前】")
            inputs.insert(2, before_part)
            inputs.insert(3, "【After: 片付け後】")
        else:
             inputs.insert(1, "【After: 片付け後（Before画像なし）】")

        response = model.generate_content(
            inputs,
            generation_config={"response_mime_type": "application/json"}
        )

        return json.loads(response.text)

    except Exception as e:
        print(f"Error in attack_monster: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/raccoon/adult/gacha", response_model=GachaResponse)
async def adult_gacha(req: ImageRequest):
    """大人モード：15分タスクを3つ提案"""
    try:
        model = get_gemini_model()

        image_data = req.image.split(',')[1] if ',' in req.image else req.image
        image_bytes = base64.b64decode(image_data)
        image_part = Part.from_data(image_bytes, mime_type="image/jpeg")

        prompt = """
        あなたは「忙しい大人のためのお片付けコンサルタント」です。
        送られてきた部屋の画像を分析し、「15分以内で完了できそうな小さなお片付けタスク」を3つ提案してください。

        条件：
        - 具体的であること（例：「机の上」ではなく「机の上のレシートを捨てる」）
        - 心理的ハードルが低いこと
        - 「それをやるだけで少し部屋がマシに見える」効果的な場所を選ぶこと

        以下のJSON形式のみで出力してください:
        {
          "tasks": [
            "ダイニングテーブルの上のDMを分別して捨てる",
            "ソファに脱ぎ捨てられた服をランドリーバスケットに入れる",
            "床に落ちているペットボトルを拾う"
          ]
        }
        """

        response = model.generate_content(
            [prompt, image_part],
            generation_config={"response_mime_type": "application/json"}
        )

        return json.loads(response.text)
    except Exception as e:
        print(f"Error in adult_gacha: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/raccoon/adult/complete")
async def adult_complete(req: TaskCompleteRequest):
    """大人モード：完了報告で褒める"""
    try:
        model = get_gemini_model()

        prompt = "ユーザーが15分のお片付けタスクを完了しました。風水や心理学的な観点、あるいは単に労いの言葉として、心が温まる「褒めメッセージ」を1つ作成してください。短めでお願いします。"

        if req.image:
             # If they sent a proof photo, incorporate it? For now, text only is fine or simple analysis.
             pass

        response = model.generate_content(prompt)

        return {"message": response.text.strip()}
    except Exception as e:
        print(f"Error in adult_complete: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/raccoon/mania/analyze", response_model=ManiaResponse)
async def mania_analyze(req: ImageRequest):
    """マニアモード：シンデレラフィット判定"""
    try:
        model = get_gemini_model()

        image_data = req.image.split(',')[1] if ',' in req.image else req.image
        image_bytes = base64.b64decode(image_data)
        image_part = Part.from_data(image_bytes, mime_type="image/jpeg")

        prompt = """
        あなたは収納の変態...いえ、収納マニアの採点員です。
        送られてきた棚や引き出しの画像を分析し、「シンデレラフィット率（隙間なく美しく収まっているか）」を採点してください。

        評価項目：
        - 隙間のなさ
        - 色や高さの統一感
        - カテゴリ分けの美しさ

        アドバイスは、「あとこれがあれば完璧」や「ここをこうするともっと美しい」など、マニアックな視点でお願いします。

        以下のJSON形式のみで出力してください:
        {
           "fit_score": 85,
           "advice": "素晴らしい！ファイルボックスの高さが揃っていて美しいです。あとはラベルをテプラで統一すれば100点満点です！"
        }
        """

        response = model.generate_content(
            [prompt, image_part],
            generation_config={"response_mime_type": "application/json"}
        )

        return json.loads(response.text)

    except Exception as e:
        print(f"Error in mania_analyze: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/raccoon/push/subscribe")
async def push_subscribe(sub: PushSubscription):
    """Web Push購読保存"""
    try:
        # Save to Firestore
        db = firestore.Client()
        # Use endpoint as document ID to prevent duplicates
        # Hash it or just clean it? Firestore IDs can't have slashes.
        # Just add to collection
        doc_ref = db.collection("raccoon_notifications").document()
        doc_ref.set({
            "endpoint": sub.endpoint,
            "keys": sub.keys,
            "created_at": firestore.SERVER_TIMESTAMP
        })
        return {"status": "success"}
    except Exception as e:
        print(f"Error subscribing: {e}")
        # For now return success to not block UI if DB fails
        return {"status": "error", "detail": str(e)}

@router.post("/api/raccoon/push/send")
async def push_send(message: str = "片付けの時間だよ！"):
    """(Test) 全員にプッシュ通知を送信"""
    try:
        from pywebpush import webpush, WebPushException

        # Load keys from env
        VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")
        VAPID_CLAIMS = {"sub": "mailto:test@example.com"}

        if not VAPID_PRIVATE_KEY:
            return {"status": "error", "message": "VAPID_PRIVATE_KEY not set in .env"}

        db = firestore.Client()
        docs = db.collection("raccoon_notifications").stream()

        count = 0
        for doc in docs:
            sub_data = doc.to_dict()
            try:
                webpush(
                    subscription_info=sub_data,
                    data=json.dumps({"body": message}),
                    vapid_private_key=VAPID_PRIVATE_KEY,
                    vapid_claims=VAPID_CLAIMS
                )
                count += 1
            except WebPushException as ex:
                print(f"Push failed for {doc.id}: {ex}")
                # Optional: Delete invalid subscription

        return {"status": "success", "sent_count": count}

    except ImportError:
        return {"status": "error", "message": "pywebpush not installed"}
    except Exception as e:
        print(f"Error sending push: {e}")
        raise HTTPException(status_code=500, detail=str(e))
