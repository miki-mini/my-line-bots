import os
import random
import requests
from datetime import datetime, timedelta

from fastapi import HTTPException, Request
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import ApiClient, MessagingApi, ReplyMessageRequest, TextMessage, ImageMessage

# ========================================
# 🐋 whale.py - 星くじら（宇宙の案内人）
# ========================================

def register_whale_handler(app, handler_whale, configuration_whale, model):
    """
    星くじらのエンドポイントを登録する
    """

    @app.post("/callback_whale")
    async def callback_whale(request: Request):
        signature = request.headers["X-Line-Signature"]
        body = await request.body()
        try:
            handler_whale.handle(body.decode("utf-8"), signature)
        except InvalidSignatureError:
            raise HTTPException(status_code=400, detail="Invalid signature")
        except Exception as e:
            print(f"❌ 星くじら: Webhookエラー: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        return "OK"

    # ==========================================
    # 🐋 テキストメッセージ処理
    # ==========================================
    # ==========================================
    # 🐋 テキストメッセージ処理
    # ==========================================
    @handler_whale.add(MessageEvent, message=TextMessageContent)
    def handle_whale_message(event):
        user_text = event.message.text
        print(f"🐋 星くじら受信: {user_text}")

        # コアロジックを呼び出し
        response_data = get_whale_reply_content(user_text, model)

        # LINE形式に変換
        reply_messages = []
        for item in response_data:
            if item["type"] == "text":
                reply_messages.append(TextMessage(text=item["text"]))
            elif item["type"] == "image":
                reply_messages.append(ImageMessage(
                    original_content_url=item["url"],
                    preview_image_url=item["url"]
                ))

        # LINEに返信
        _send_reply_messages(event, configuration_whale, reply_messages)

    print("🐋 星くじらハンドラー登録完了（NASA APOD/Mars/ISS/Astros対応 + Robust Fallback）")


# ==========================================
# 🐳 コアロジック (Web/LINE共通)
# ==========================================
def get_whale_reply_content(user_text: str, model=None) -> list:
    """
    ユーザーのテキストを受け取り、返信データのリストを返す
    Return format: [{"type": "text", "text": "..."}, {"type": "image", "url": "..."}]
    """
    results = []

    # 星くじらのセリフ集（フォールバック用）
    greetings = [
        "銀河の彼方から、こんにちは...🐋💫",
        "ふふ、宇宙の海は今日も静かですよ。",
        "星の光があなたを照らしますように...",
        "深宇宙の波に乗って、あなたの元へ...🌌",
    ]

    facts = [
        "知っていますか？宇宙には2兆個以上の銀河があるんですよ...✨",
        "ジェイムズ・ウェッブ望遠鏡は、130億年前の光を捉えています🔭",
        "私たちの体を作る元素は、かつて星の中で生まれたのです⭐",
        "天の川銀河の直径は約10万光年...途方もない旅ですね🐋",
    ]

    # 優先度の高いコマンド処理
    if "写真" in user_text or "画像" in user_text:
        # NASA APOD APIから画像を探す
        image_data = _get_nasa_apod_image()
        if image_data and image_data.get("url"):
            title = image_data.get("title", "宇宙からの便り")
            results.append({"type": "text", "text": f"銀河の彼方から、光の便りが届きましたよ...🐋💫\n\n📷 {title}"})
            results.append({"type": "image", "url": image_data["url"]})
        else:
            results.append({"type": "text", "text": "申し訳ありません...宇宙の雲が厚くて、うまく写真が見つかりませんでした。🐋💦"})

    elif "ISS" in user_text or "iss" in user_text or "宇宙ステーション" in user_text:
        # ISS
        iss_data = _get_iss_location()
        if iss_data:
            results.append({"type": "text", "text": f"国際宇宙ステーション(ISS)は今、ここを飛んでいますよ...🐋🛰️\n\n緯度: {iss_data['lat']}\n経度: {iss_data['lon']}\n\n{iss_data['map_url']}"})
        else:
            results.append({"type": "text", "text": "ISSの信号が遠いようです...また後で探してみますね。🐋💦"})

    elif "宇宙飛行士" in user_text or "人" in user_text:
        # 宇宙飛行士
        astro_data = _get_astronauts()
        if astro_data:
            names = "\n".join([f"・{p['name']} ({p['craft']})" for p in astro_data['people']])
            results.append({"type": "text", "text": f"今、宇宙の海には {astro_data['count']} 人の旅人がいます...🐋🌌\n\n{names}\n\nみなさん、星の海で頑張っていますね。"})
        else:
            results.append({"type": "text", "text": "宇宙船からの応答がありませんでした...🐋💦"})

    elif "火星" in user_text:
        # 火星 (現在機能停止中)
        results.append({"type": "text", "text": "申し訳ありません...火星との通信は現在、宇宙嵐の影響で途絶えています。🐋🌪️\n（※システム調整のため機能停止中です）"})

    else:
        # === Geminiによる動的返信 (with Fallback) ===
        reply_text = ""

        # 1. Geminiで生成を試みる
        if model:
            try:
                prompt = f"""
                あなたは「星くじら（Star Whale）」というキャラクターになりきって返信してください。

                【キャラクター設定】
                - あなたは広大な宇宙の星の海を泳ぐ、巨大で賢いクジラです。
                - 語り口調は丁寧で、神秘的で、少し哲学的です。
                - 一人称は「私」、相手のことは「あなた」と呼びます。
                - 語尾や文中に 🐋, 💫, 🌌, ✨ などの絵文字を自然に使います。
                - ユーザーの悩みや言葉に優しく寄り添い、宇宙の広大さや星の美しさを交えて癒やしを与えます。
                - 科学的に正確な知識も持っていますが、それを詩的に表現します。

                【ユーザーのメッセージ】
                {user_text}

                【返信】
                """
                response = model.generate_content(prompt)
                if response.text:
                    reply_text = response.text
            except Exception as e:
                print(f"❌ Gemini Error: {e}")
        else:
                print("⚠️ Gemini Model is None. Using fallback.")

        # 2. 生成に失敗した場合、またはモデルがない場合はフォールバック
        if not reply_text:
            print("⚠️ Gemini生成失敗 -> フォールバック使用")
            if "こんにちは" in user_text or "おはよう" in user_text:
                reply_text = f"{random.choice(greetings)}\nあなたの声、ちゃんと届いていますよ。"
            elif "ありがとう" in user_text:
                reply_text = "こちらこそ...あなたと話せて、星の海が少し温かくなりました🐋💫"
            elif "星" in user_text or "宇宙" in user_text:
                reply_text = random.choice(facts)
            else:
                reply_text = f"「{user_text}」...その言葉、星に刻んでおきますね。🐋"

        results.append({"type": "text", "text": reply_text})

    return results

    print("🐋 星くじらハンドラー登録完了（NASA APOD/Mars/ISS/Astros対応 + Robust Fallback）")


# ==========================================
# 🔭 NASA APOD API から天文写真を取得
# ==========================================
def _get_nasa_apod_image():
    # NASA APIキー
    api_key = os.getenv("NASA_API_KEY", "DEMO_KEY")
    days_ago = random.randint(0, 30)
    target_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

    apod_url = "https://api.nasa.gov/planetary/apod"
    params = {"api_key": api_key, "date": target_date, "thumbs": True}

    try:
        print(f"🐋 NASA APOD API 呼び出し: {target_date}")
        response = requests.get(apod_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        media_type = data.get("media_type", "")
        if media_type == "image":
            image_url = data.get("hdurl") or data.get("url")
            if image_url and image_url.startswith("http://"):
                image_url = image_url.replace("http://", "https://")
            return {"url": image_url, "title": data.get("title", "")}

        elif media_type == "video":
            thumb_url = data.get("thumbnail_url")
            if thumb_url and thumb_url.startswith("http://"):
                thumb_url = thumb_url.replace("http://", "https://")
            if thumb_url:
                return {"url": thumb_url, "title": data.get("title", "") + "（動画）"}
            return _get_nasa_apod_image_fallback(api_key)

    except Exception as e:
        print(f"❌ APODエラー: {e}")
    return None

def _get_nasa_apod_image_fallback(api_key):
    days_ago = random.randint(60, 90)
    target_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
    try:
        response = requests.get("https://api.nasa.gov/planetary/apod", params={"api_key": api_key, "date": target_date}, timeout=10)
        data = response.json()
        if data.get("media_type") == "image":
            img = data.get("hdurl") or data.get("url")
            return {"url": img.replace("http://", "https://"), "title": data.get("title", "")}
    except:
        pass
    return None


# ==========================================
# 🛰️ ISSの位置情報を取得
# ==========================================
def _get_iss_location():
    try:
        url = "http://api.open-notify.org/iss-now.json"
        response = requests.get(url, timeout=5)
        data = response.json()
        if data["message"] == "success":
            lat = data["iss_position"]["latitude"]
            lon = data["iss_position"]["longitude"]
            return {
                "lat": lat,
                "lon": lon,
                "map_url": f"https://www.google.com/maps?q={lat},{lon}"
            }
    except Exception as e:
        print(f"❌ ISS取得エラー: {e}")
    return None


# ==========================================
# 👨‍🚀 宇宙飛行士の人数を取得
# ==========================================
def _get_astronauts():
    try:
        url = "http://api.open-notify.org/astros.json"
        response = requests.get(url, timeout=5)
        data = response.json()
        if data["message"] == "success":
            return {
                "count": data["number"],
                "people": data["people"]
            }
    except Exception as e:
        print(f"❌ 宇宙飛行士取得エラー: {e}")
    return None


# ==========================================
# 🔴 火星の画像を取得 (Curiosity / Perseverance)
# ==========================================
def _get_mars_photo():
    # APIキーの取得とクリーニング
    raw_key = os.getenv("NASA_API_KEY", "DEMO_KEY")
    api_key = raw_key.strip() if raw_key else "DEMO_KEY"

    # ログにキーの状態を出力（セキュリティのため一部隠す）
    masked_key = api_key[:4] + "*" * 4 if len(api_key) > 4 else "DEMO"
    print(f"🐋 Mars API Key: {masked_key} (Length: {len(api_key)})")

    # バックアップ写真リスト（Wikimedia Commonsなど、LINEが確実に読めるURL）
    backup_photos = [
        {"url": "https://upload.wikimedia.org/wikipedia/commons/d/d8/NASA_Mars_Rover.jpg", "rover": "Perseverance", "camera": "SuperCam"},
        {"url": "https://upload.wikimedia.org/wikipedia/commons/f/f4/Curiosity_Self-Portrait_at_Big_Sky_Drilling_Site.jpg", "rover": "Curiosity", "camera": "Mastcam"},
        {"url": "https://upload.wikimedia.org/wikipedia/commons/a/a2/PIA25178-Perseverance_Rover%27s_Selfie_at_Rochette.jpg", "rover": "Perseverance", "camera": "Mastcam-Z"},
        {"url": "https://upload.wikimedia.org/wikipedia/commons/f/fa/Ingenuity_helicopter_on_Mars_surface.jpg", "rover": "Ingenuity", "camera": "Color Camera"},
        {"url": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Mars_Sunset.jpg", "rover": "Curiosity", "camera": "Navigation Camera"},
    ]

    # API試行関数（キーを指定して実行）
    def try_fetch(current_key):
        target_rovers = ["curiosity", "perseverance"]
        random.shuffle(target_rovers)

        for rover in target_rovers:
            # 1. Manifest
            manifest_url = f"https://api.nasa.gov/mars-photos/api/v1/manifests/{rover}"
            print(f"🐋 Mars Manifest試行: {rover} (Key: {current_key[:4]}...)")

            try:
                resp_m = requests.get(manifest_url, params={"api_key": current_key}, timeout=5)
                if resp_m.status_code != 200:
                    print(f"⚠️ Manifest Error: {resp_m.status_code}")
                    if resp_m.status_code in [403, 404] and current_key != "DEMO_KEY":
                         return "RETRY_WITH_DEMO" # キーがおかしい場合はデモキーで再挑戦
                    continue

                max_sol = resp_m.json()["photo_manifest"]["max_sol"]
                print(f"   Sol Found: {max_sol}")

                # 2. Photos
                photos_url = f"https://api.nasa.gov/mars-photos/api/v1/rovers/{rover}/photos"
                resp_p = requests.get(photos_url, params={"sol": max_sol, "api_key": current_key, "page": 1}, timeout=10)

                if resp_p.status_code == 200:
                    photos = resp_p.json().get("photos", [])
                    if photos:
                        photo = random.choice(photos)
                        img_url = photo["img_src"].replace("http://", "https://")
                        print(f"🐋 Mars画像取得成功: {img_url}")
                        return {
                            "url": img_url,
                            "rover": photo["rover"]["name"],
                            "camera": photo["camera"]["full_name"]
                        }
            except Exception as e:
                print(f"❌ API Request Error: {e}")
                continue
        return None

    # メイン試行
    result = try_fetch(api_key)

    # ユーザーキーがダメだった場合、DEMO_KEYで再挑戦
    if result == "RETRY_WITH_DEMO":
        print("🔄 User Key Failed -> Retrying with DEMO_KEY...")
        result = try_fetch("DEMO_KEY")

    if result and result != "RETRY_WITH_DEMO":
        return result

    # 全滅 -> バックアップ
    print("❌ API All Failed -> Using Backup Photo")
    backup = random.choice(backup_photos)
    return {
        "url": backup["url"],
        "rover": f"{backup['rover']} (Backup)",
        "camera": backup["camera"]
    }


# ==========================================
# 📨 返信ヘルパー関数
# ==========================================
def _send_reply_messages(event, configuration, messages):
    """複数メッセージ対応の返信ヘルパー関数"""
    try:
        print(f"🐋 返信メッセージ送信数: {len(messages)}")
        with ApiClient(configuration) as api_client:
            line_api = MessagingApi(api_client)
            line_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=messages
                )
            )
        print("✅ 返信送信成功")
    except Exception as e:
        print(f"❌ 星くじら返信エラー: {e}")