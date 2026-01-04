# ========================================
# 🦉 owl.py - フクロウ教授（健康管理アシスタント）
# 料理画像分析、カロリー記録、体重記録、グラフ生成
# ========================================

import os
import re
import json
import io
from datetime import datetime

from fastapi import UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from vertexai.generative_models import GenerativeModel, Part
from google.cloud import firestore

import matplotlib.pyplot as plt
# import japanize_matplotlib  # 日本語化 (Debug: Disable for deployment check)
import pandas as pd


# --- リクエストモデル ---
class WeightRequest(BaseModel):
    weight: float



# ==========================================
# 🧠 Core Logic Functions (Reusable)
# ==========================================
async def _process_image_analysis(image_file: UploadFile):
    print(f"🦉 フクロウ: 画像分析開始 - {image_file.filename}")
    try:
        # 1. 画像の読み込み
        content = await image_file.read()
        image_part = Part.from_data(data=content, mime_type="image/jpeg")

        # 2. AIへの命令
        prompt = """
        この料理の画像を分析してください。
        以下の情報をJSON形式で出力してください。
        必ず { で始まり } で終わる正しいJSONデータのみを出力し、前後の挨拶文やマークダウン記号（```json など）は含めないでください。

        {
            "food_name": "料理名",
            "calories": 0,
            "message": "ユーザーへの解説メッセージ（料理の特定、カロリーの根拠、ねぎらいの言葉など。温かみのある口調で）"
        }

        注意:
        - calories は推定カロリー（整数値だけで。幅がある場合は平均値で）
        - message は温かみのある口調で、料理についての解説を含めてください
        """

        # 3. Gemini (Flash) で分析
        model = GenerativeModel("gemini-2.5-flash")
        response = model.generate_content([image_part, prompt])
        text_response = response.text
        print(f"🦉 AI Response: {text_response[:100]}...")

        # 4. AIの返事からJSON部分だけを抽出
        match = re.search(r"\{.*\}", text_response, re.DOTALL)
        if match:
            json_str = match.group(0)
            result = json.loads(json_str)
        else:
            raise ValueError("AIの返答からJSONが見つかりませんでした。")

        # 5. Firestoreにカロリーを記録
        db = firestore.Client()
        now = datetime.now()

        doc_ref = db.collection("calories").document()
        doc_ref.set({
            "date": now.strftime("%Y-%m-%d"),
            "timestamp": firestore.SERVER_TIMESTAMP,
            "food_name": result["food_name"],
            "kcal": result["calories"],
        })
        print(f"🦉 記録完了: {result['food_name']} = {result['calories']}kcal")

        return {"analysis": result["message"]}

    except json.JSONDecodeError as e:
        print(f"❌ フクロウ JSONパースエラー: {e}")
        return {
            "analysis": "ごめんなさい、分析結果の解析に失敗しました...🦉 もう一度試してみてください"
        }

    except Exception as e:
        print(f"❌ フクロウ エラー: {e}")
        return {
            "analysis": f"ごめんなさい、分析に失敗しました... (エラー: {str(e)}) もう一度試してみてください🦉"
        }

async def _process_weight_recording(req: WeightRequest):
    print(f"🦉 フクロウ: 体重記録 - {req.weight}kg")
    try:
        db = firestore.Client()
        now = datetime.now()
        date_str = now.strftime("%m/%d")
        doc_id = now.strftime("%Y-%m-%d")

        doc_ref = db.collection("weights").document(doc_id)
        doc_ref.set({
            "date": date_str,
            "kg": req.weight,
            "timestamp": firestore.SERVER_TIMESTAMP,
        })

        print(f"🦉 体重記録完了: {date_str} = {req.weight}kg")
        return {"message": f"📅 {date_str}\n⚖️ {req.weight}kg で記録しました！"}
    except Exception as e:
        print(f"❌ フクロウ 体重記録エラー: {e}")
        from fastapi import HTTPException
        raise HTTPException(500, detail=str(e))

async def _generate_weight_graph():
    print("🦉 フクロウ: 体重グラフ生成中...")
    try:
        db = firestore.Client()
        docs = db.collection("weights").order_by("date").limit_to_last(7).get()

        dates = []
        weights = []
        for doc in docs:
            data = doc.to_dict()
            dates.append(data.get("date"))
            weights.append(data.get("kg"))

        df = pd.DataFrame({"日付": dates, "体重": weights})

        plt.figure(figsize=(6, 4))
        if not df.empty:
            # plt.plot(df["日付"], df["体重"], marker="o", color="#ff7f0e", label="体重(kg)")
            pass

        # plt.title("体重の推移", fontsize=14)
        # plt.xlabel("日付")
        # plt.ylabel("体重 (kg)")
        # plt.grid(True, linestyle="--", alpha=0.6)
        if not df.empty:
            # plt.legend()
            pass

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        plt.close()
        return StreamingResponse(buf, media_type="image/png")
    except Exception as e:
        print(f"❌ フクロウ 体重グラフエラー: {e}")
        plt.figure(figsize=(6, 4))
        plt.text(0.5, 0.5, "データがありません", ha='center', va='center', fontsize=14)
        plt.axis('off')
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        plt.close()
        return StreamingResponse(buf, media_type="image/png")

async def _generate_calories_graph():
    print("🦉 フクロウ: カロリーグラフ生成中...")
    try:
        db = firestore.Client()
        docs = db.collection("calories").order_by("timestamp").limit_to_last(30).get()

        daily_data = {}
        for doc in docs:
            data = doc.to_dict()
            date_val = data.get("date", "")
            if date_val and len(date_val) >= 5:
                date_str = date_val[5:]
            else:
                continue
            kcal = data.get("kcal", 0)

            if date_str in daily_data:
                daily_data[date_str] += kcal
            else:
                daily_data[date_str] = kcal

        dates = sorted(daily_data.keys())
        kcals = [daily_data[d] for d in dates]

        plt.figure(figsize=(6, 4))
        if dates:
            # plt.bar(dates, kcals, color="#2ca02c", label="摂取カロリー")
            pass

        # plt.title("日々の摂取カロリー", fontsize=14)
        # plt.xlabel("日付")
        # plt.ylabel("kcal")
        # plt.grid(axis="y", linestyle="--", alpha=0.6)
        if dates:
            # plt.legend()
            pass

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        plt.close()
        return StreamingResponse(buf, media_type="image/png")
    except Exception as e:
        print(f"❌ フクロウ カロリーグラフエラー: {e}")
        plt.figure(figsize=(6, 4))
        plt.text(0.5, 0.5, "データがありません", ha='center', va='center', fontsize=14)
        plt.axis('off')
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        plt.close()
        return StreamingResponse(buf, media_type="image/png")

def register_owl_handler(app, auth_dependency=None):
    """
    Deprecated: Use router instead.
    """
    pass

# ==========================================
# 🌍 Web API (Router)
# ==========================================
from fastapi import APIRouter
router = APIRouter()

# 1. Legacy Endpoints (Keep for compatibility if needed)
@router.post("/analyze_image/")
async def analyze_image_legacy(image_file: UploadFile = File(...)):
    return await _process_image_analysis(image_file)

@router.post("/record/weight")
async def record_weight_legacy(req: WeightRequest):
    return await _process_weight_recording(req)

@router.get("/graph/weight")
async def get_weight_graph_legacy():
    return await _generate_weight_graph()

@router.get("/graph/calories")
async def get_calories_graph_legacy():
    return await _generate_calories_graph()

# 2. Web App Endpoints (Now Public / Unlocked)
@router.post("/api/owl/analyze_image")
async def analyze_image_secure(image_file: UploadFile = File(...)):
    return await _process_image_analysis(image_file)

@router.post("/api/owl/record_weight")
async def record_weight_secure(req: WeightRequest):
    return await _process_weight_recording(req)

@router.get("/api/owl/graph/weight")
async def get_weight_graph_secure():
    return await _generate_weight_graph()

@router.get("/api/owl/graph/calories")
async def get_calories_graph_secure():
    return await _generate_calories_graph()

print("🦉 フクロウハンドラー登録完了（Router版）")
