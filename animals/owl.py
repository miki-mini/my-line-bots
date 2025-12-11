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
import japanize_matplotlib  # 日本語化
import pandas as pd


# --- リクエストモデル ---
class WeightRequest(BaseModel):
    weight: float


def register_owl_handler(app):
    """
    フクロウのエンドポイントを登録する

    Parameters:
        app: FastAPIアプリケーション
    """

    # ==========================================
    # 🦉 料理画像分析 & カロリー自動保存
    # ==========================================
    @app.post("/analyze_image/")
    async def analyze_image(image_file: UploadFile = File(...)):
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

            # 6. 結果を返す
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

    # ==========================================
    # ⚖️ 体重記録
    # ==========================================
    @app.post("/record/weight")
    def record_weight(req: WeightRequest):
        print(f"🦉 フクロウ: 体重記録 - {req.weight}kg")

        try:
            db = firestore.Client()
            now = datetime.now()

            # 今日の日付 (例: "11/23")
            date_str = now.strftime("%m/%d")
            # 記録用のID (例: "2025-11-23") ※同じ日は上書きされます
            doc_id = now.strftime("%Y-%m-%d")

            # Firestoreに保存
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

    # ==========================================
    # 📊 体重グラフ生成
    # ==========================================
    @app.get("/graph/weight")
    async def get_weight_graph():
        print("🦉 フクロウ: 体重グラフ生成中...")

        try:
            # 1. Firestoreからデータを取得
            db = firestore.Client()
            docs = db.collection("weights").order_by("date").limit_to_last(7).get()

            dates = []
            weights = []

            for doc in docs:
                data = doc.to_dict()
                dates.append(data.get("date"))
                weights.append(data.get("kg"))

            # 2. データフレーム作成
            df = pd.DataFrame({"日付": dates, "体重": weights})

            # 3. グラフ描画
            plt.figure(figsize=(6, 4))
            if not df.empty:
                plt.plot(df["日付"], df["体重"], marker="o", color="#ff7f0e", label="体重(kg)")

            plt.title("体重の推移", fontsize=14)
            plt.xlabel("日付")
            plt.ylabel("体重 (kg)")
            plt.grid(True, linestyle="--", alpha=0.6)
            if not df.empty:
                plt.legend()

            # 4. 画像保存
            buf = io.BytesIO()
            plt.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)
            plt.close()

            print("🦉 体重グラフ生成完了")
            return StreamingResponse(buf, media_type="image/png")

        except Exception as e:
            print(f"❌ フクロウ 体重グラフエラー: {e}")
            # エラー時は空のグラフを返す
            plt.figure(figsize=(6, 4))
            plt.text(0.5, 0.5, "データがありません", ha='center', va='center', fontsize=14)
            plt.axis('off')
            buf = io.BytesIO()
            plt.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)
            plt.close()
            return StreamingResponse(buf, media_type="image/png")

    # ==========================================
    # 📊 カロリーグラフ生成（棒グラフ）
    # ==========================================
    @app.get("/graph/calories")
    async def get_calories_graph():
        print("🦉 フクロウ: カロリーグラフ生成中...")

        try:
            db = firestore.Client()
            # 最新の食事データを取得（30件くらい）
            docs = db.collection("calories").order_by("timestamp").limit_to_last(30).get()

            # 日付ごとにカロリーを足し算する（集計）
            daily_data = {}
            for doc in docs:
                data = doc.to_dict()
                date_val = data.get("date", "")
                if date_val and len(date_val) >= 5:
                    date_str = date_val[5:]  # "2025-11-23" → "11-23" に短縮
                else:
                    continue
                kcal = data.get("kcal", 0)

                # その日のデータがなければ0からスタート、あれば足す
                if date_str in daily_data:
                    daily_data[date_str] += kcal
                else:
                    daily_data[date_str] = kcal

            # グラフ用にデータを整理
            dates = sorted(daily_data.keys())
            kcals = [daily_data[d] for d in dates]

            # グラフ描画 (Bar Chart = 棒グラフ)
            plt.figure(figsize=(6, 4))
            if dates:
                plt.bar(dates, kcals, color="#2ca02c", label="摂取カロリー")  # 緑色

            plt.title("日々の摂取カロリー", fontsize=14)
            plt.xlabel("日付")
            plt.ylabel("kcal")
            plt.grid(axis="y", linestyle="--", alpha=0.6)  # 横線だけ引く
            if dates:
                plt.legend()

            # 画像保存
            buf = io.BytesIO()
            plt.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)
            plt.close()

            print("🦉 カロリーグラフ生成完了")
            return StreamingResponse(buf, media_type="image/png")

        except Exception as e:
            print(f"❌ フクロウ カロリーグラフエラー: {e}")
            # エラー時は空のグラフを返す
            plt.figure(figsize=(6, 4))
            plt.text(0.5, 0.5, "データがありません", ha='center', va='center', fontsize=14)
            plt.axis('off')
            buf = io.BytesIO()
            plt.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)
            plt.close()
            return StreamingResponse(buf, media_type="image/png")

    print("🦉 フクロウハンドラー登録完了（画像分析・体重記録・グラフ生成）")