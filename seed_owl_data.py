import argparse
from google.cloud import firestore
from datetime import datetime, timedelta
import random

# ==========================================
# 🦉 フクロウ教授のデータ生成スクリプト
# ==========================================
# 使い方: python seed_owl_data.py
# ※ 事前に gcloud auth application-default login が必要かもしれません

def seed_data():
    project_id = "usagi-oekaki" # デフォルトプロジェクト名（必要なら変更してください）

    # ユーザーの現在のプロジェクトIDを自動取得できればベストですが、
    # 汎用的に動くように client() で環境変数を読みに行かせます
    try:
        db = firestore.Client()
        print(f"✅ Firestoreに接続しました (Project: {db.project})")
    except Exception as e:
        print(f"❌ Firestore接続エラー: {e}")
        print("ヒント: 'gcloud auth application-default login' を実行してみてください。")
        return

    # --- 1. 体重データの生成 (過去14日間) ---
    print("\n⚖️ 体重データを生成中...")
    base_weight = 60.0

    for i in range(14):
        # 過去から現在へ
        days_ago = 13 - i
        target_date = datetime.now() - timedelta(days=days_ago)

        doc_id = target_date.strftime("%Y-%m-%d") # "2025-12-01"
        date_str = target_date.strftime("%m/%d")  # "12/01"

        # 少しランダムに変動させる
        weight = base_weight + random.uniform(-0.5, 0.5)
        # 週末に少し増えるリアリティ
        if target_date.weekday() >= 5:
            weight += 0.3

        doc_ref = db.collection("weights").document(doc_id)
        doc_ref.set({
            "date": date_str,
            "kg": round(weight, 1),
            "timestamp": target_date
        })
        print(f"  - {doc_id}: {round(weight, 1)}kg")

    # --- 2. カロリーデータの生成 (過去5日間) ---
    print("\n🍽️ 食事データを生成中...")
    foods = [
        ("朝食: トーストセット", 450),
        ("昼食: 牛丼", 750),
        ("夕食: サラダチキン", 200),
        ("おやつ: チョコレート", 150),
        ("昼食: パスタ", 800),
        ("夕食: 焼き魚定食", 600),
        ("朝食: スムージー", 120),
        ("飲み会", 1200),
    ]

    # カロリーコレクションはドキュメントID自動生成なので、削除は難しいが、
    # 今回は「追記」にします。

    for i in range(7):
        days_ago = 6 - i
        target_date = datetime.now() - timedelta(days=days_ago)
        date_str_iso = target_date.strftime("%Y-%m-%d")

        # 1日3食〜4食ランダムに
        meals_count = random.randint(3, 4)
        print(f"  [{date_str_iso}] {meals_count}食")

        for _ in range(meals_count):
            food_name, base_kcal = random.choice(foods)
            kcal = base_kcal + random.randint(-50, 50)

            # 時間も適当にバラす
            hour = random.randint(8, 20)
            meal_time = target_date.replace(hour=hour, minute=30)

            db.collection("calories").add({
                "date": date_str_iso,
                "food_name": food_name,
                "kcal": kcal,
                "timestamp": meal_time
            })

    print("\n✨ データ生成完了！")
    print("LINEボットで「グラフ」や「カロリー」と話しかけてみてください🦉")

if __name__ == "__main__":
    seed_data()
