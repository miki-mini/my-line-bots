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
import re

# ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼

# 【絶対に落ちないインポート】
import vertexai
from vertexai.generative_models import GenerativeModel, Part, Image, Tool, grounding
from vertexai.vision_models import ImageGenerationModel
from vertexai.generative_models import grounding
from vertexai.preview.vision_models import ImageGenerationModel

# ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲

from google import genai
from google.genai.types import GenerateContentConfig, GoogleSearch, Tool
import google.generativeai as genai
from google.genai import types
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
import japanize_matplotlib  # 日本語化
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
import pandas as pd
from datetime import datetime

# --- グローバル変数 ---
# モデルたち
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
YOUR_CHANNEL_ACCESS_TOKEN = os.environ.get("YOUR_CHANNEL_ACCESS_TOKEN")
YOUR_CHANNEL_SECRET = os.environ.get("YOUR_CHANNEL_SECRET")

# Google Mapsの設定
GMAPS_API_KEY = os.environ.get("GMAPS_API_KEY")
gmaps = googlemaps.Client(key=GMAPS_API_KEY)

# --- 🤖 各ボットの設定 ---
configuration = Configuration(access_token=YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

configuration_train = Configuration(access_token=os.getenv("TRAIN_ACCESS_TOKEN"))
handler_train = WebhookHandler(os.getenv("TRAIN_CHANNEL_SECRET"))

configuration_voidoll = Configuration(access_token=os.getenv("VOIDOLL_ACCESS_TOKEN"))
handler_voidoll = WebhookHandler(os.getenv("VOIDOLL_CHANNEL_SECRET"))

configuration_frog = Configuration(access_token=os.getenv("FROG_ACCESS_TOKEN"))
handler_frog = WebhookHandler(os.getenv("FROG_CHANNEL_SECRET"))

configuration_fox = Configuration(access_token=os.getenv("FOX_ACCESS_TOKEN"))
handler_fox = WebhookHandler(os.getenv("FOX_CHANNEL_SECRET"))

configuration_capybara = Configuration(access_token=os.getenv("CAPYBARA_ACCESS_TOKEN"))
handler_capybara = WebhookHandler(os.getenv("CAPYBARA_CHANNEL_SECRET"))

# --- 共通クライアント ---
api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)
line_bot_blob_api = MessagingApiBlob(api_client)

api_client_voidoll = ApiClient(configuration_voidoll)
line_bot_api_voidoll = MessagingApi(api_client_voidoll)
line_bot_blob_api_voidoll = MessagingApiBlob(api_client_voidoll)

# Gemini API設定
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


@app.on_event("startup")
def startup_event():
    global db, storage_client, GCS_BUCKET_NAME
    global image_model, text_model, vision_model, search_model
    global startup_errors

    startup_errors.clear()  # エラーリストをクリア

    print("🚀 起動プロセス開始 (Gemini 2.5 Flash - Vertex AI)...")

    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
    GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

    # 1. DB & Storage 接続
    try:
        db = firestore.Client(project=GCP_PROJECT_ID)
        storage_client = storage.Client(project=GCP_PROJECT_ID)
        print("✅ Firestore & Storage 接続OK")
    except Exception as e:
        print(f"⚠️ DB接続エラー: {e}")

    # 2. Vertex AI 初期化
    try:
        vertexai.init(project=GCP_PROJECT_ID, location="asia-northeast1")
        print("✅ Vertex AI 初期化OK")
    except Exception as e:
        print(f"❌ Vertex AI 初期化エラー: {e}")
        return

    # 3. モデルの準備
    try:
        # (A) 基本の会話 & 画像認識
        text_model = GenerativeModel("gemini-2.5-flash")
        vision_model = GenerativeModel("gemini-2.5-flash")

        # (B) 画像生成
        try:
            image_model = ImageGenerationModel.from_pretrained(
                "imagen-3.0-fast-generate-001"
            )
            print("✅ 基本モデル (2.5 Flash & Imagen) 準備完了")
        except:
            image_model = None
            print("✅ 基本モデル (2.5 Flash) 準備完了")

    except Exception as e:
        print(f"❌ 基本モデル設定エラー: {e}")

    # (C) ★検索機能 - 2025年最新の正しい書き方★
    try:
        print("👉 Google Search 機能を設定中...")

        # まず grounding が使えるか確認
        print(f"   grounding モジュール: {grounding}")
        print(
            f"   GoogleSearchRetrieval: {hasattr(grounding, 'GoogleSearchRetrieval')}"
        )

        # ✅ 正しいインポートと使い方
        search_retrieval = grounding.GoogleSearchRetrieval()
        print(
            f"   GoogleSearchRetrieval インスタンス作成成功: {type(search_retrieval)}"
        )

        search_tool = Tool.from_google_search_retrieval(search_retrieval)
        print(f"   Tool 作成成功: {type(search_tool)}")

        # 検索対応モデルの作成
        search_model = GenerativeModel("gemini-2.5-flash", tools=[search_tool])

        print("🎉 Gemini 2.5 Flash + Google Search 設定完了！")
        print(f"   search_model._tools: {len(search_model._tools)} tools")

    except AttributeError as e:
        error_msg = f"AttributeError: {str(e)}"
        print(f"❌ 検索モデル設定エラー: {error_msg}")
        startup_errors.append(error_msg)
        search_model = text_model
        print("⚠️ 検索機能なしで起動します（通常モデルで代替）")

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"❌ 検索モデル設定エラー: {error_msg}")
        startup_errors.append(error_msg)
        # フォールバック：検索なしで動作
        search_model = text_model
        print("⚠️ 検索機能なしで起動します（通常モデルで代替）")

    print("🚀 サーバー起動完了！ Super Capybara (2.5) is Ready.")


# ========================================


@app.get("/")
def read_root():
    return {"status": "All Bots Operational 🤖✨"}


# ========================================
# デバッグ：起動後にモデル確認
# ========================================


@app.get("/health")
def health_check():
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
        # エラーが起きても最低限の情報を返す
        return {"status": "error", "error": str(e), "error_type": type(e).__name__}


# ==========================================
# 1. メインボット (ペンギン・ビーバー)
# ==========================================
@app.post("/callback")
async def callback(request: Request):
    try:
        signature = request.headers["X-Line-Signature"]
        body = await request.body()
        body = body.decode()
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("❌ 署名エラー")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        print(f"❌ /callback エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    return "OK"


# ★★★ ビーバー画像解析機能 ★★★
@handler.add(MessageEvent, message=ImageMessageContent)
def handle_image_message(event):
    print(f"📸 【START】画像を受信 ID: {event.message.id}")
    message_id = event.message.id
    user_id = event.source.user_id

    try:
        print("📥 1. 画像ダウンロード中...")
        image_content = line_bot_blob_api.get_message_content(message_id)
        print(f"✅ 1. ダウンロード完了！ ({len(image_content)} bytes)")

        mime_type = "image/jpeg"
        if image_content.startswith(b"\x89PNG"):
            mime_type = "image/png"
            print("🔍 画像タイプ: PNG")
        else:
            print("🔍 画像タイプ: JPEG")

        model_name = "gemini-2.5-flash"
        print(f"🤖 2. {model_name} に送信...")
        model_flash = genai.GenerativeModel(model_name)

        today_str = datetime.now().strftime("%Y-%m-%d")

        prompt = f"""
        この画像を分析し、学校や地域のプリントに書かれている「重要なイベント」や「提出期限」を抽出してください。

        【重要なルール】
        1. 本日（{today_str}）より過去の日付は、たとえ記載があっても絶対に除外してください。
        2. 「印刷日」「発行日」「作成日」などの事務的な日付は除外してください。
        3. 年が省略されている場合は、適切な年（今年または来年）を補完してください。

        【出力形式】JSON形式のみ（Markdown記号なし）:
        [
          {{"date": "YYYY-MM-DD", "content": "イベント内容"}}
        ]
        """

        image_data = {"mime_type": mime_type, "data": image_content}

        response = model_flash.generate_content([prompt, image_data])

        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        try:
            events_list = json.loads(cleaned_text)
        except:
            match = re.search(r"\[.*\]", cleaned_text, re.DOTALL)
            if match:
                events_list = json.loads(match.group())
            else:
                print("⚠️ JSONパース失敗")
                events_list = []

        if not events_list:
            reply_text = (
                "プリントを読んだけど、これからの予定は見つからなかったっぴ...🐧"
            )
        else:
            saved_count = 0
            reply_lines = ["📸 これからの予定を整理したでヤンス！🪵\n"]

            for item in events_list:
                event_date = item.get("date")
                content = item.get("content")

                if event_date and content:
                    doc_data = {
                        "user_id": user_id,
                        "text": f"【プリント】{content}",
                        "reminder_time": f"{event_date} 08:00",
                        "timestamp": firestore.SERVER_TIMESTAMP,
                    }
                    if db:
                        db.collection("memos").add(doc_data)
                    saved_count += 1
                    reply_lines.append(f"📅 {event_date}: {content}")

            if saved_count > 0:
                reply_lines.append(f"\n計{saved_count}件を登録したでヤンス！")
                reply_text = "\n".join(reply_lines)
            else:
                reply_text = "有効な予定が見つからなかったっぴ...🐧"

    except Exception as e:
        print(f"❌ エラー発生: {e}")
        reply_text = "画像の読み取りに失敗したっぴ...🐧💦"

    try:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text)],
                )
            )
    except Exception as e:
        print(f"❌ 返信エラー: {e}")


# ★★★ 通常メッセージ処理（ここにメモ一覧機能を追加！）★★★
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_text = event.message.text.strip()  # 空白削除
    user_id = event.source.user_id

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        reply_text = ""

        try:
            # 📝 1. メモ一覧・予定一覧
            if user_text in ["メモ一覧", "予定一覧", "スケジュール"]:
                if not db:
                    reply_text = "データベースに接続できないっぴ...💦"
                else:
                    # タイムスタンプ順に取得
                    docs = (
                        db.collection("memos")
                        .where("user_id", "==", user_id)
                        .order_by("timestamp")
                        .stream()
                    )

                    memos = []
                    for i, doc in enumerate(docs):
                        data = doc.to_dict()
                        text = data.get("text", "")
                        # 長い文字は省略
                        display_text = text[:20] + "..." if len(text) > 20 else text
                        date_info = data.get("reminder_time", "日時なし")
                        # ユーザーには1から始まる番号を見せる
                        memos.append(f"{i+1}. [{date_info}] {display_text}")

                    if memos:
                        reply_text = (
                            "🦫 予定一覧だヤンス！\n\n"
                            + "\n".join(memos)
                            + "\n\n削除したい時は「メモ削除 1」のように番号で教えてヤンス！"
                        )
                    else:
                        reply_text = "予定は空っぽだヤンス！🦫"

            # 🗑️ 2. メモ削除
            # 🗑️ 2. メモ削除（まとめて削除対応版）
            elif user_text.startswith("メモ削除"):
                # "メモ削除 1 3" や "メモ削除 1, 2" の数字部分を取り出す
                try:
                    # 「メモ削除」の文字を消して、コンマや読点「、」もスペースに変換
                    input_str = (
                        user_text.replace("メモ削除", "")
                        .replace(",", " ")
                        .replace("、", " ")
                    )

                    # スペースで区切って、数字だけのリストを作る
                    target_indices = []
                    for s in input_str.split():
                        if s.strip().isdigit():
                            # 1引いて0始まりの番号にする
                            target_indices.append(int(s) - 1)

                    if not target_indices:
                        raise ValueError("数字が見つかりません")

                    # データベースから今のメモ一覧を取得（番号とIDを紐付けるため）
                    docs = list(
                        db.collection("memos")
                        .where("user_id", "==", user_id)
                        .order_by("timestamp")
                        .stream()
                    )

                    deleted_numbers = []

                    # 指定された番号を順番に処理
                    for index in target_indices:
                        if 0 <= index < len(docs):
                            # 実際に削除
                            docs[index].reference.delete()
                            # ユーザーに見せる番号（+1）を記録
                            deleted_numbers.append(str(index + 1))

                    if deleted_numbers:
                        # 数字のリストを「1, 3, 5」のような文字列にする
                        deleted_str = ", ".join(deleted_numbers)
                        reply_text = (
                            f"🗑️ {deleted_str}番のメモをまとめて削除したでヤンス！"
                        )
                    else:
                        reply_text = "指定された番号のメモは見つからなかったっぴ...🐧"

                except:
                    reply_text = (
                        "削除したい番号を「メモ削除 1 3」のように教えてほしいっぴ！"
                    )

            # 🌤️ 3. 天気予報（カエル）
            elif "天気" in user_text or "てんき" in user_text:
                try:
                    chat_model = genai.GenerativeModel("gemini-2.5-flash")
                    prompt = f"次の内容について楽しく答えて: {user_text}\n役割: カエルのケロくん。天気と服装のアドバイス。語尾はケロ。"
                    res = chat_model.generate_content(prompt)
                    reply_text = res.text
                except:
                    reply_text = "カエル呼び出しエラーケロ..."

            # 📰 4. ニュース（カピバラ）
            elif "ニュース" in user_text:
                try:
                    chat_model = genai.GenerativeModel("gemini-2.5-flash")
                    prompt = f"次の話題について教えて: {user_text}\n役割: カピバラさん。3行要約。語尾はだっぴ。"
                    res = chat_model.generate_content(prompt)
                    reply_text = res.text
                except:
                    reply_text = "カピバラ呼び出しエラーだっぴ..."

            # 📧 5. メール送信
            elif user_text.startswith("メール："):
                parts = user_text.split("\n")
                if len(parts) < 3:
                    reply_text = "ペン...？入力形式が違うペン。\n1行目: アドレス\n2行目: 件名\n3行目: 本文"
                else:
                    target_email = parts[0].replace("メール：", "").strip()
                    raw_subject = parts[1].strip()
                    raw_body = "\n".join(parts[2:])
                    subject, body = call_gemini_to_clean_email(raw_subject, raw_body)
                    success, msg = send_email_via_gas(target_email, subject, body)
                    reply_text = (
                        f"送信完了だペン！🐧\n\n{body}"
                        if success
                        else f"失敗だペン...💦\n{msg}"
                    )

            # 📝 6. メモ追加 (テキスト)

            # （↑上には天気やニュースの処理があるはずです）

            # ★★★ ここから下を書き換え（メモも雑談もAIが自動判断！） ★★★
            else:
                print(f"🤖 AI自動判断を実行: {user_text}")

                # 今の時間をAIに教える準備
                # 9時間足して、日本時間(JST)にする！
                now_str = (datetime.now() + timedelta(hours=9)).strftime(
                    "%Y-%m-%d %H:%M"
                )

                # Geminiへの命令（ここが一番大事！）
                prompt = f"""
                現在日時: {now_str}
                ユーザーの入力: {user_text}

                あなたは「まめなビーバー」です。
                ユーザーの入力が「予定」なのか「雑談」なのかを判断し、以下のJSON形式のみで答えてください。Markdown記号は不要です。

                【ルール】
                1. 「5分後」「明日12時」などの時間表現があれば、現在日時から計算して "reminder_time" に "YYYY-MM-DD HH:MM" 形式で入れてください。
                2. 時間指定がない予定やメモの場合は、"reminder_time" を "NO_TIME" にしてください。
                3. 予定ではなく、ただの挨拶や雑談の場合は "is_memo" を false にしてください。
                4. "content" には、予定の内容（または雑談の返事）を入れてください。

                【出力JSON形式】
                {{
                    "is_memo": true または false,
                    "reminder_time": "YYYY-MM-DD HH:MM" または "NO_TIME",
                    "content": "予定の内容、または雑談の返信テキスト"
                }}
                """

                model = genai.GenerativeModel("gemini-2.5-flash")
                response = model.generate_content(prompt)
                cleaned_text = (
                    response.text.replace("```json", "").replace("```", "").strip()
                )

                try:
                    data = json.loads(cleaned_text)
                    is_memo = data.get("is_memo", False)
                    reminder_time = data.get("reminder_time", "NO_TIME")
                    content = data.get("content", "")

                    # 📅 1. 予定として登録する場合
                    if is_memo:
                        doc_data = {
                            "user_id": user_id,
                            "text": content,
                            "reminder_time": (
                                "" if reminder_time == "NO_TIME" else reminder_time
                            ),
                            "timestamp": firestore.SERVER_TIMESTAMP,
                        }
                        if db:
                            db.collection("memos").add(doc_data)

                        if reminder_time != "NO_TIME":
                            reply_text = f"🦫 ガッテンだ！\n「{content}」を【{reminder_time}】に通知するでヤンス！⏰"
                        else:
                            reply_text = f"🦫 メモしたでヤンス！\n「{content}」"

                    # 🗣️ 2. ただの雑談の場合
                    else:
                        reply_text = content  # AIが考えた返事をそのまま返す

                except Exception as e:
                    print(f"JSONパース失敗: {e}")
                    reply_text = "うまく聞き取れなかったっぴ...🐧💦"

        # （↓エラー処理と返信処理はそのまま残す）
        except Exception as e:
            print(f"エラー: {e}")
            reply_text = f"エラーだっぴ...💦 {str(e)}"

        if reply_text:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text)],
                )
            )


def call_gemini_to_clean_email(raw_subject, raw_body):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = f"ビジネスメールに修正して。JSON形式 {{'subject': '...', 'body': '...'}} で出力。\n件名:{raw_subject}\n本文:{raw_body}"
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        return data["subject"], data["body"]
    except:
        return raw_subject, raw_body


def send_email_via_gas(to_email, subject, body):
    payload = {"to": to_email, "subject": subject, "body": body}
    try:
        res = requests.post(GAS_MAIL_WEB_APP_URL, json=payload)
        if res.status_code == 200 or res.status_code == 302:
            return True, "成功"
        return False, res.text
    except Exception as e:
        return False, str(e)


@app.get("/trigger-check-reminders")
def trigger_check_reminders():
    if not db:
        raise HTTPException(status_code=500, detail="No DB")
    try:
        jst = datetime.timezone(datetime.timedelta(hours=+9), "JST")
        now = datetime.datetime.now(jst)
        today = now.strftime("%Y-%m-%d")
        tomorrow = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        notifications = {}
        docs = db.collection("memos").stream()

        for doc in docs:
            data = doc.to_dict()
            uid = data.get("user_id")
            r_time = data.get("reminder_time", "")
            text = data.get("text", "")

            if not uid or not r_time:
                continue

            date_part = r_time.split(" ")[0]
            if date_part == today:
                notifications.setdefault(uid, []).append(f"🔴【今日】: {text}")
            elif date_part == tomorrow:
                notifications.setdefault(uid, []).append(f"🟡【明日】: {text}")

        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            for uid, msgs in notifications.items():
                push_text = "🦫 ビーバー通知でヤンス！\n\n" + "\n".join(msgs)
                try:
                    line_bot_api.push_message(
                        PushMessageRequest(
                            to=uid, messages=[TextMessage(text=push_text)]
                        )
                    )
                except:
                    pass
        return {"status": "ok", "count": len(notifications)}
    except Exception as e:
        print(f"Check Error: {e}")
        return {"error": str(e)}


# モグラ、Voidoll、カエル、キツネ、カピバラのエンドポイント
@app.post("/callback_train")
async def callback_train(request: Request):
    signature = request.headers["X-Line-Signature"]
    body = await request.body()
    try:
        handler_train.handle(body.decode("utf-8"), signature)
    except:
        raise HTTPException(status_code=400)
    return "OK"


try:
    from station_data import STATIONS
except:
    STATIONS = []
STATIONS.append(
    {
        "name": "吉祥寺",
        "id": "odpt.Station:Keio.Inokashira.Kichijoji",
        "railway": "Keio",
    }
)


def get_current_calendar():
    jst = datetime.timezone(datetime.timedelta(hours=+9), "JST")
    weekday = datetime.datetime.now(jst).weekday()
    if weekday == 5:
        return "odpt.Calendar:Saturday"
    elif weekday == 6:
        return "odpt.Calendar:Holiday"
    else:
        return "odpt.Calendar:Weekday"


@handler_train.add(MessageEvent, message=TextMessageContent)
def handle_train_message(event):
    user_text = event.message.text
    try:
        res = genai.GenerativeModel("gemini-2.5-flash").generate_content(
            f"駅名だけ抜き出して。「{user_text}」 -> 出力:"
        )
        extracted = (
            res.text.strip().replace("駅", "").replace("「", "").replace("」", "")
        )
    except:
        extracted = user_text

    found_data = None
    for s in STATIONS:
        if s["name"] == extracted:
            found_data = s
            break
    if not found_data:
        for s in STATIONS:
            if extracted in s["name"]:
                found_data = s
                break

    if not found_data:
        msg = f"駅が見つからないモグ...「{extracted}」？"
    else:
        try:
            params = {
                # os.getenvを使う
                "acl:consumerKey": os.getenv("ODPT_API_KEY"),
                "odpt:station": found_data["id"],
                "odpt:calendar": get_current_calendar(),
            }
            res = requests.get(
                "https://api.odpt.org/api/v4/odpt:StationTimetable", params=params
            )
            timetables = res.json()
            if not timetables:
                msg = f"【{found_data['name']}】データなしモグ..."
            else:
                jst = datetime.timezone(datetime.timedelta(hours=+9), "JST")
                now_hm = datetime.datetime.now(jst).strftime("%H:%M")
                upcoming = []
                for t in timetables:
                    d = t.get("odpt:railwayDirection", "").split(":")[-1]
                    for tr in t.get("odpt:stationTimetableObject", []):
                        dept = tr.get("odpt:departureTime")
                        dest = tr.get("odpt:destinationStation", ["?"])[0].split(".")[
                            -1
                        ]
                        if dept and dept > now_hm:
                            upcoming.append({"time": dept, "dest": dest, "dir": d})
                upcoming.sort(key=lambda x: x["time"])
                top5 = upcoming[:5]
                msg = (
                    f"【{found_data['name']}】\n"
                    + "\n".join([f"🕒 {t['time']} ({t['dest']})" for t in top5])
                    if top5
                    else "もう電車ないモグ..."
                )
        except Exception as e:
            msg = f"エラーモグ: {e}"
    with ApiClient(configuration_train) as c:
        MessagingApi(c).reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[TextMessage(text=msg)]
            )
        )


@handler_train.add(MessageEvent, message=LocationMessageContent)
def handle_location_message(event):
    try:
        res = gmaps.places_nearby(
            location=(event.message.latitude, event.message.longitude),
            rank_by="distance",
            type="train_station",
            language="ja",
        )
        msg = (
            f"最寄りは「{res['results'][0]['name']}」だモグ！"
            if res.get("results")
            else "駅がないモグ..."
        )
    except:
        msg = "検索失敗モグ..."
    with ApiClient(configuration_train) as c:
        MessagingApi(c).reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[TextMessage(text=msg)]
            )
        )


@app.post("/callback_voidoll")
async def callback_voidoll(request: Request):
    signature = request.headers["X-Line-Signature"]
    body = await request.body()
    try:
        handler_voidoll.handle(body.decode("utf-8"), signature)
    except:
        raise HTTPException(status_code=400)
    return "OK"


@handler_voidoll.add(MessageEvent, message=AudioMessageContent)
def handle_voidoll_audio(event):
    try:
        content = line_bot_blob_api_voidoll.get_message_content(event.message.id)
        res = genai.GenerativeModel("gemini-2.5-flash").generate_content(
            [
                "文字起こしして返答。性格:知的女性AI。",
                {"mime_type": "audio/mp4", "data": content},
            ]
        )

        q = requests.post(
            "https://voicevox-engine-1032484155743.asia-northeast1.run.app/audio_query",
            params={"text": res.text, "speaker": 89},
        ).json()
        syn = requests.post(
            "https://voicevox-engine-1032484155743.asia-northeast1.run.app/synthesis",
            params={"speaker": 89},
            json=q,
        )

        client = storage.Client()
        blob = client.bucket(os.getenv("GCS_BUCKET_NAME")).blob(
            f"voice_{uuid.uuid4()}.wav"
        )
        blob.upload_from_string(syn.content, content_type="audio/wav")
        blob.make_public()

        msg = AudioMessage(original_content_url=blob.public_url, duration=2000)
        line_bot_api_voidoll.reply_message(
            ReplyMessageRequest(reply_token=event.reply_token, messages=[msg])
        )
    except Exception as e:
        line_bot_api_voidoll.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[TextMessage(text=str(e))]
            )
        )


@app.post("/callback_frog")
async def callback_frog(request: Request):
    print("🐸🐸🐸 カエルWebhook受信！！！")

    signature = request.headers.get("X-Line-Signature")
    body = await request.body()

    print(f"🐸 Body: {body.decode('utf-8')[:200]}...")

    try:
        handler_frog.handle(body.decode("utf-8"), signature)
        print("🐸 handler_frog.handle() 完了")
    except Exception as e:
        print(f"🐸❌ handler エラー: {e}")
        import traceback

        print(traceback.format_exc())

    return {"status": "ok"}


# ========================================
# カエルのメッセージハンドラー
# ========================================


@handler_frog.add(MessageEvent, message=TextMessageContent)
def handle_frog_message(event):
    print(f"🐸 カエル受信: {event.message.text}")
    print(
        f"🐸 ユーザーID: {event.source.user_id if hasattr(event.source, 'user_id') else 'unknown'}"
    )
    print(f"🐸 reply_token: {event.reply_token}")

    # グローバル変数を呼び出す
    global search_model, text_model

    # ★ モデルの状態チェック
    print(f"🧐 search_model の状態: {search_model is not None}")
    print(f"🧐 text_model の状態: {text_model is not None}")

    today = date.today().strftime("%Y年%m月%d日")
    msg = ""

    try:
        print("🐸 ステップ1: 検索判定開始")

        # 検索が必要か判定
        search_keywords = ["天気", "最新", "今", "現在", "ニュース", "調べて"]
        needs_search = any(keyword in event.message.text for keyword in search_keywords)

        print(f"🐸 ステップ2: 検索必要? {needs_search}")

        # 使用するモデルを選択
        if needs_search and search_model:
            print("🔍 検索モードで実行中...")
            model = search_model
        elif text_model:
            print("💬 通常モードで実行中...")
            model = text_model
        else:
            print("❌ 使えるモデルがありません！")
            msg = "今は答えられないケロ...（システムエラー）"
            raise Exception("モデルが初期化されていません")

        print(f"🐸 ステップ3: 使用モデル = {type(model).__name__}")

        # プロンプト作成
        prompt = f"""
現在日時: {today}
ユーザーの質問: {event.message.text}

あなたは明るく元気な天気予報カエルです。
必要に応じて最新情報を検索して、簡潔に答えてください。
語尾に「ケロ」をつけて親しみやすく回答してください。
"""

        print("🐸 ステップ4: プロンプト作成完了")
        print(f"   プロンプト長: {len(prompt)} 文字")

        # 生成実行
        print(f"⏳ 生成開始...")
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 1024,
            },
        )

        print("🐸 ステップ5: 生成完了")

        # レスポンス取得
        if response and hasattr(response, "text") and response.text:
            msg = response.text.strip()
            print(f"✅ 生成成功！ (文字数: {len(msg)})")
            print(f"   返信内容プレビュー: {msg[:100]}...")
        else:
            print("⚠️ 空の応答を受信")
            msg = "答えが見つからなかったケロ..."

    except Exception as e:
        print(f"❌ カエル生成エラー: {e}")
        print(f"   エラータイプ: {type(e).__name__}")
        import traceback

        print(f"   スタックトレース:\n{traceback.format_exc()}")
        msg = f"エラーが起きたケロ...💦"

    # LINEに返信
    try:
        print("🐸 ステップ6: LINE返信開始")
        print(f"   返信先token: {event.reply_token}")
        print(f"   メッセージ: {msg[:50]}...")

        with ApiClient(configuration_frog) as c:
            api = MessagingApi(c)
            api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token, messages=[TextMessage(text=msg)]
                )
            )
        print("📨 カエル返信送信完了！")

    except Exception as e:
        print(f"❌ 返信送信エラー: {e}")
        print(f"   エラータイプ: {type(e).__name__}")
        import traceback

        print(f"   スタックトレース:\n{traceback.format_exc()}")


# ========================================
# きつね🦊のメッセージハンドラー
# ========================================


@app.post("/callback_fox")
async def callback_fox(request: Request):
    signature = request.headers["X-Line-Signature"]
    body = await request.body()
    try:
        handler_fox.handle(body.decode("utf-8"), signature)
    except:
        raise HTTPException(status_code=400)
    return "OK"


@handler_fox.add(MessageEvent, message=TextMessageContent)
def handle_fox_message(event):
    try:
        res = genai.GenerativeModel("gemini-2.5-flash").generate_content(
            f"動画情報: {event.message.text}\n役割:キツネ先生。語尾コン。"
        )
        msg = res.text
    except:
        msg = "エラーコン..."
    with ApiClient(configuration_fox) as c:
        MessagingApi(c).reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[TextMessage(text=msg)]
            )
        )


@app.post("/callback_capybara")
async def callback_capybara(request: Request):
    # ヘッダーから署名を取得
    signature = request.headers["X-Line-Signature"]
    # ボディを取得
    body = await request.body()
    body_str = body.decode("utf-8")

    try:
        # 署名検証を実行 (ここでパスワードが合っているかチェックされます)
        handler_capybara.handle(body_str, signature)
    except Exception as e:
        # ★ここでエラーの正体をログに出す！
        print(f"❌ LINE Webhook エラー: {e}")
        # InvalidSignatureError なら環境変数の間違いです
        raise HTTPException(status_code=400, detail=str(e))

    return "OK"


# ==========================================
# 🐹 カピバラさん (日付エラー完全修正・最終版)
# ==========================================
@handler_capybara.add(MessageEvent, message=TextMessageContent)
def handle_capybara_message(event):
    print(f"🐹 カピバラ受信: {event.message.text}")
    global search_model

    # ★重要！ここで「dt」というあだ名でインポートします
    # これなら外でどんな設定になっていても絶対に干渉しません！
    import datetime as dt

    try:
        # dt.date.today() なら確実に動きます
        today = dt.date.today().strftime("%Y年%m月%d日")
    except Exception as e:
        print(f"⚠️ 日付取得エラー: {e}")
        today = "今日"

    msg = ""
    try:
        # 検索モデルがあるか確認
        if search_model:
            prompt = f"""
            現在日時: {today}
            ユーザーの質問: {event.message.text}

            役割: あなたはニュース解説が得意なカピバラです。
            ルール:
            1. 上記の「現在日時」を基準にして、Google検索で最新情報を調べてください。
            2. 「昨日」と聞かれたら、現在日時の1日前を検索してください。
            3. 語尾は「っぴ」をつけてください。
            """
            response = search_model.generate_content(prompt)
            msg = response.text
        else:
            msg = "検索機能がちょっと調子悪いっぴ...ごめんっぴ。"

    except Exception as e:
        print(f"❌ カピバラ生成エラー: {e}")
        msg = "エラーが出ちゃったっぴ。もう一回言ってほしいっぴ。"

    # LINEに返信
    try:
        with ApiClient(configuration_capybara) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token, messages=[TextMessage(text=msg)]
                )
            )
    except Exception as e:
        print(f"❌ LINE返信エラー: {e}")


# --- ☀️ 朝のニュース配信 (検索機能付き) ---
@app.post("/trigger_morning_news")
def trigger_morning_news():
    print("☀️ 朝のニュース配信を開始します...")
    global search_model

    try:
        if search_model:
            # ★ここで「今日のニュース」を検索させる！
            prompt = """
            今の日本や世界のAIニュースを3つピックアップして検索してください。
            それをカピバラの口調（語尾っぴ）で、分かりやすく解説してください。
            最後に「今日も一日がんばるっぴ！」と元気づけてください。
            """
            res = search_model.generate_content(prompt)
            news_text = res.text
        else:
            news_text = "今はニュースが見られないっぴ...ごめんっぴ。"

        # 全員に送信 (Broadcast)
        with ApiClient(configuration_capybara) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.broadcast(
                BroadcastRequest(messages=[TextMessage(text=news_text)])
            )
        return {"status": "ok", "message": "ニュース配信完了っぴ！"}

    except Exception as e:
        print(f"❌ ニュース配信エラー: {e}")
        return {"status": "error", "message": str(e)}


# --- この下に class GenerateRequest(BaseModel): があってもOKです ---


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
        # Vertex AI
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


# --- グラフ生成のエンドポイント ---11/23
@app.get("/graph/weight")
async def get_weight_graph():
    # 1. Firestoreからデータを取得
    db = firestore.Client()

    # ★ここを修正しました！ (.stream() を .get() に変えました)
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

    return StreamingResponse(buf, media_type="image/png")


# ==========================================
# ★追加：カロリーグラフ機能 (棒グラフ)
# ==========================================
@app.get("/graph/calories")
async def get_calories_graph():
    db = firestore.Client()
    # 最新の食事データを取得（30件くらい）
    docs = db.collection("calories").order_by("timestamp").limit_to_last(30).get()

    # 日付ごとにカロリーを足し算する（集計）
    daily_data = {}
    for doc in docs:
        data = doc.to_dict()
        date_str = data.get("date")[5:]  # "2025-11-23" → "11/23" に短縮
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
    plt.legend()

    # 画像保存
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    plt.close()

    return StreamingResponse(buf, media_type="image/png")


# ==========================================
# ★追加：体重記録用のコード
# ==========================================
from pydantic import BaseModel
from datetime import datetime


class WeightRequest(BaseModel):
    weight: float


@app.post("/record/weight")
def record_weight(req: WeightRequest):
    try:
        db = firestore.Client()
        now = datetime.now()

        # 今日の日付 (例: "11/23")
        date_str = now.strftime("%m/%d")
        # 記録用のID (例: "2025-11-23") ※同じ日は上書きされます
        doc_id = now.strftime("%Y-%m-%d")

        # Firestoreに保存
        doc_ref = db.collection("weights").document(doc_id)
        doc_ref.set(
            {
                "date": date_str,
                "kg": req.weight,
                "timestamp": firestore.SERVER_TIMESTAMP,
            }
        )

        return {"message": f"📅 {date_str}\n⚖️ {req.weight}kg で記録しました！"}
    except Exception as e:
        raise HTTPException(500, detail=str(e))


# 既存のAPIも残しておきます（GASのタイマー用）
class MemoRequest(BaseModel):
    user_id: str
    memo_text: str
    reminder_time: Optional[str] = None


@app.post("/add-memo")
async def add_memo(r: MemoRequest):
    if db:
        db.collection("memos").add(
            {
                "user_id": r.user_id,
                "text": r.memo_text,
                "reminder_time": r.reminder_time,
                "timestamp": firestore.SERVER_TIMESTAMP,
            }
        )
    return {"status": "success"}


@app.get("/get-memos/{user_id}")
async def get_memos(user_id: str):
    if not db:
        return {}
    docs = db.collection("memos").where("user_id", "==", user_id).stream()
    return {
        "memos": [
            {
                "memo_id": d.id,
                "text": d.to_dict().get("text"),
                "reminder_time": d.to_dict().get("reminder_time"),
            }
            for d in docs
        ]
    }


@app.delete("/delete-memo/{memo_id}")
async def delete_memo(memo_id: str):
    if db:
        db.collection("memos").document(memo_id).delete()
    return {"status": "success"}


# ★★★ 時間になったメモを取り出す機能（日本時間対応版） ★★★
# ★★★ 時間になったメモを取り出す機能（取りこぼし防止・最強版） ★★★
@app.get("/get-due-memos")
def get_due_memos():
    # 1. 日本時間にする
    now = datetime.now() + timedelta(hours=9)
    current_time = now.strftime("%Y-%m-%d %H:%M")

    print(f"⏰ チェック中... 現在 {current_time} 以前の予定を探します")

    if not db:
        return {"due_memos": []}

    try:
        # メモを全件取得して、Python側でチェックする
        # (Firestoreの複雑な検索エラーを避けるための安全策です)
        docs = db.collection("memos").stream()

        due_memos = []
        for doc in docs:
            data = doc.to_dict()
            reminder_time = data.get("reminder_time", "")

            # 【重要】時間がセットされていて、かつ「現在時刻を過ぎている」なら通知対象！
            # 文字列比較で "2025-11-25 20:29" <= "2025-11-25 20:30" となるので判定できます
            if (
                reminder_time
                and reminder_time != "NO_TIME"
                and reminder_time <= current_time
            ):
                due_memos.append(
                    {
                        "memo_id": doc.id,
                        "user_id": data.get("user_id"),
                        "text": data.get("text"),
                    }
                )

        if due_memos:
            print(f"🔔 {len(due_memos)}件の通知を見つけました！送信します！")

        return {"due_memos": due_memos}

    except Exception as e:
        print(f"❌ エラー: {e}")
        return {"due_memos": []}


@app.get("/get-daily-summary-memos")
async def get_daily_summary_memos():
    if not db:
        return {"memos_by_user": {}}
    docs = db.collection("memos").where("reminder_time", "in", ["", None]).stream()
    memos = {}
    for d in docs:
        uid = d.to_dict().get("user_id")
        if uid:
            memos.setdefault(uid, []).append(
                {"memo_id": d.id, "text": d.to_dict().get("text")}
            )
    return {"memos_by_user": memos}


# ==========================================
# ★改良版：画像分析 ＆ カロリー自動保存 (頑丈バージョン)
# ==========================================
@app.post("/analyze_image/")
async def analyze_image(image_file: UploadFile = File(...)):
    try:
        # 1. 画像の読み込み
        content = await image_file.read()
        image_part = Part.from_data(data=content, mime_type="image/jpeg")

        # 2. AIへの命令
        prompt = """
        この料理の画像を分析してください。
        以下の情報をJSON形式で出力してください。
        必ず { で始まり } で終わる正しいJSONデータのみを出力し、前後の挨拶文やマークダウン記号（```json など）は含めないでください。
        ```json
        {
            "food_name": "料理名",
            "calories": 0,  // 推定カロリー（整数値だけで。幅がある場合は平均値で）
            "message": "ユーザーへの解説メッセージ（料理の特定、カロリーの根拠、ねぎらいの言葉など。温かみのある口調で）"
        }
        ```
        """

        # 3. Gemini (Flash) で分析
        model = GenerativeModel("gemini-2.5-flash")
        response = model.generate_content([image_part, prompt])
        text_response = response.text
        print(f"AI Response Raw: {text_response}")  # ログで確認用

        # 4. AIの返事からJSON部分だけを強力に抜き出す (正規表現)
        match = re.search(r"\{.*\}", text_response, re.DOTALL)
        if match:
            json_str = match.group(0)
            result = json.loads(json_str)  # 変換
        else:
            raise ValueError("AIの返答からJSONが見つかりませんでした。")

        # 5. Firestoreにカロリーを「貯金」する
        db = firestore.Client()
        now = datetime.now()

        doc_ref = db.collection("calories").document()
        doc_ref.set(
            {
                "date": now.strftime("%Y-%m-%d"),
                "timestamp": firestore.SERVER_TIMESTAMP,
                "food_name": result["food_name"],
                "kcal": result["calories"],
            }
        )

        # 6. LINEにメッセージを返す
        return {"analysis": result["message"]}

    except Exception as e:
        print(f"Error in analyze_image: {e}")
        # エラー内容を少し詳しく出すように変更（デバッグ用）
        return {
            "analysis": f"ごめんなさい、分析に失敗しました... (エラー: {str(e)}) もう一度試してみてください🦉"
        }


# ★★★ 追加：明日の予定をチェックして通知する機能 ★★★
@app.get("/check_reminders")
def check_reminders():
    print("⏰ リマインダーチェック開始...")

    # 明日の日付を作る（例：2025-11-26）
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")

    # データベースに保存されている形式（YYYY-MM-DD 08:00）に合わせる
    target_time = f"{tomorrow_str} 08:00"
    print(f"🔍 検索対象の日時: {target_time}")

    if not db:
        return {"status": "error", "message": "DB未接続"}

    try:
        # 「明日 08:00」のメモを検索
        docs = db.collection("memos").where("reminder_time", "==", target_time).stream()

        count = 0
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)

            for doc in docs:
                data = doc.to_dict()
                user_id = data.get("user_id")
                text = data.get("text")

                if user_id and text:
                    print(f"📩 送信中: {user_id} -> {text}")
                    # プッシュ通知を送る
                    line_bot_api.push_message(
                        PushMessageRequest(
                            to=user_id,
                            messages=[
                                TextMessage(text=f"明日の予定だっぴ！🦫\n\n{text}")
                            ],
                        )
                    )
                    count += 1

        return {"status": "success", "sent_count": count}

    except Exception as e:
        print(f"❌ リマインダーエラー: {e}")
        return {"status": "error", "message": str(e)}
