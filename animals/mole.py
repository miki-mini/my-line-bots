"""
mole.py - 🦡 もぐら駅長の時刻表BOT
"""

import os
import requests
import datetime
import google.generativeai as genai
import googlemaps
from linebot.v3.messaging import (
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhook import MessageEvent
from linebot.v3.webhooks import TextMessageContent, LocationMessageContent
from linebot.v3.exceptions import InvalidSignatureError
from fastapi import Request, HTTPException


# 駅データをインポート
try:
    from station_data import STATIONS
except ImportError:
    STATIONS = []

# 吉祥寺は複数路線に対応
if not any(s.get("name") == "吉祥寺" for s in STATIONS):
    # JR中央線と京王井の頭線の両方を登録
    STATIONS.extend([
        {
            "name": "吉祥寺",
            "id": "odpt.Station:JR-East.ChuoRapid.Kichijoji",  # 中央線快速
            "railway": "JR-East"
        },
        {
            "name": "吉祥寺",
            "id": "odpt.Station:Keio.Inokashira.Kichijoji",  # 京王井の頭線
            "railway": "Keio"
        }
    ])


def get_current_calendar():
    """現在の曜日に応じたカレンダーを返す"""
    jst = datetime.timezone(datetime.timedelta(hours=+9), "JST")
    weekday = datetime.datetime.now(jst).weekday()

    if weekday == 5:  # 土曜日
        return "odpt.Calendar:Saturday"
    elif weekday == 6:  # 日曜日
        return "odpt.Calendar:Holiday"
    else:  # 平日
        return "odpt.Calendar:Weekday"


def register_mole_handler(app, handler_mole, configuration_mole, text_model):
    """
    もぐら駅長のハンドラーを登録
    """

    # Google Maps クライアント
    GMAPS_API_KEY = os.getenv("GMAPS_API_KEY")
    gmaps = googlemaps.Client(key=GMAPS_API_KEY) if GMAPS_API_KEY else None

    @app.post("/callback_train")
    async def callback_train(request: Request):
        """もぐら駅長用Webhook"""
        print("🦡🦡🦡 もぐら駅長Webhook受信！")

        signature = request.headers.get("X-Line-Signature")
        body = await request.body()

        try:
            handler_mole.handle(body.decode("utf-8"), signature)
            print("🦡 handler_mole.handle() 完了")
        except InvalidSignatureError:
            print(f"🦡❌ 署名検証エラー")
            raise HTTPException(status_code=400, detail="Invalid signature")
        except Exception as e:
            print(f"🦡❌ handler エラー: {e}")
            import traceback
            print(traceback.format_exc())

        return {"status": "ok"}

    @handler_mole.add(MessageEvent, message=TextMessageContent)
    def handle_train_message(event):
        """駅名テキストで時刻表を検索"""
        user_text = event.message.text
        print(f"🦡 もぐら受信: {user_text}")

        try:
            # Geminiで駅名だけ抽出
            if text_model:
                res = text_model.generate_content(
                    f"駅名だけ抜き出して。「{user_text}」 -> 出力:"
                )
                # マルチパートレスポンス（思考プロセス含む）への対応
                try:
                    raw_text = res.text
                except ValueError:
                    # partsが複数ある場合（Thinking outputなど）、最後のパートが回答
                    if res.candidates and res.candidates[0].content.parts:
                        raw_text = res.candidates[0].content.parts[-1].text
                    else:
                        raw_text = ""

                extracted = (
                    raw_text.strip()
                    .replace("駅", "")
                    .replace("「", "")
                    .replace("」", "")
                )
            else:
                # Geminiが使えない場合はそのまま
                extracted = user_text.replace("駅", "").strip()

            print(f"🔍 抽出された駅名: {extracted}")

            # 駅データから検索（同じ駅名で複数路線がある場合は全て試す）
            found_stations = []

            # 完全一致で検索
            for s in STATIONS:
                if s["name"] == extracted:
                    found_stations.append(s)

            # 部分一致で検索（完全一致がない場合のみ）
            if not found_stations:
                for s in STATIONS:
                    if extracted in s["name"]:
                        found_stations.append(s)

            if not found_stations:
                msg = f"🦡 駅が見つからないモグ...「{extracted}」？\n\n駅名を教えてほしいモグ！"
            else:
                # 複数路線がある場合は全て試す
                all_timetables = []
                for station in found_stations:
                    timetable = get_timetable(station)
                    if timetable and "もう電車がないモグ" not in timetable and "データがないモグ" not in timetable:
                        all_timetables.append(timetable)

                if all_timetables:
                    msg = "\n\n".join(all_timetables)
                else:
                    # 全部失敗した場合は最後のエラーメッセージ
                    msg = get_timetable(found_stations[0])

        except Exception as e:
            print(f"❌ もぐらエラー: {e}")
            import traceback
            print(traceback.format_exc())
            msg = f"🦡 エラーが起きたモグ...💦\n{str(e)}"

        # LINEに返信
        try:
            with ApiClient(configuration_mole) as c:
                api = MessagingApi(c)
                api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=msg)]
                    )
                )
            print("📨 もぐら返信送信完了！")

        except Exception as e:
            print(f"❌ 返信送信エラー: {e}")

    @handler_mole.add(MessageEvent, message=LocationMessageContent)
    def handle_location_message(event):
        """位置情報から最寄り駅を検索"""
        print(f"📍 位置情報受信: ({event.message.latitude}, {event.message.longitude})")

        try:
            if not gmaps:
                msg = "🦡 Google Maps APIが設定されてないモグ...💦"
            else:
                # 最寄り駅を検索
                res = gmaps.places_nearby(
                    location=(event.message.latitude, event.message.longitude),
                    rank_by="distance",
                    type="train_station",
                    language="ja",
                )

                if res.get("results"):
                    station_name = res["results"][0]["name"]
                    msg = f"🦡 最寄りは「{station_name}」だモグ！\n\n駅名を送ってくれたら時刻表を見せるモグ！"
                else:
                    msg = "🦡 近くに駅が見つからないモグ...💦"

        except Exception as e:
            print(f"❌ 位置情報エラー: {e}")
            msg = f"🦡 検索失敗したモグ...💦"

        # LINEに返信
        try:
            with ApiClient(configuration_mole) as c:
                api = MessagingApi(c)
                api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=msg)]
                    )
                )

        except Exception as e:
            print(f"❌ 返信送信エラー: {e}")


def get_timetable(station_data: dict) -> str:
    """
    ODPT APIで時刻表を取得

    Args:
        station_data: 駅情報（name, id, railway）

    Returns:
        時刻表メッセージ
    """
    ODPT_API_KEY = os.getenv("ODPT_API_KEY")

    if not ODPT_API_KEY:
        return "🦡 ODPT_API_KEYが設定されてないモグ...💦"

    try:
        params = {
            "acl:consumerKey": ODPT_API_KEY,
            "odpt:station": station_data["id"],
            "odpt:calendar": get_current_calendar(),
        }

        print(f"🔍 API呼び出し: {params}")

        res = requests.get(
            "https://api.odpt.org/api/v4/odpt:StationTimetable",
            params=params,
            timeout=10
        )

        print(f"📡 API Status: {res.status_code}")
        print(f"📡 API Raw: {res.text[:500]}")  # 先頭500文字だけログに出す

        try:
            timetables = res.json()
        except:
            print("❌ JSON Decode Error")
            timetables = []

        # エラーレスポンスの場合（リストではなく辞書で返ってくる場合エラーかも）
        if isinstance(timetables, dict) and "error" in timetables:
             print(f"❌ API Error: {timetables}")
             # エラーでもフォールバック試す価値ある？ いや、403ならAPIキーの問題
             if res.status_code in [401, 403]:
                 return "🦡 APIキーが間違ってるか期限切れだモグ...💦"
             timetables = []  # リセットしてフォールバックへ

        print(f"📊 APIレスポンス(Parsed): {len(timetables)}件")

        # フォールバック: データがなく、特定の休日カレンダーだった場合は統合カレンダー(SaturdayHoliday)で再検索
        if not timetables and params["odpt:calendar"] in ["odpt.Calendar:Saturday", "odpt.Calendar:Holiday"]:
            print("🔄 データなし、土休日ダイヤ(SaturdayHoliday)で再検索中...")
            params["odpt:calendar"] = "odpt.Calendar:SaturdayHoliday"
            res = requests.get(
                "https://api.odpt.org/api/v4/odpt:StationTimetable",
                params=params,
                timeout=10
            )
            timetables = res.json()
            print(f"📊 再検索結果: {len(timetables)}件のデータ")

        if not timetables:
            return f"🦡 【{station_data['name']}】のデータがないモグ...💦\n(ID: {station_data['id']})\n(Cal: {params['odpt:calendar']})"

        # 現在時刻を取得（日本時間）
        jst = datetime.timezone(datetime.timedelta(hours=+9), "JST")
        now_hm = datetime.datetime.now(jst).strftime("%H:%M")

        print(f"⏰ 現在時刻: {now_hm}")

        # 今後の電車を抽出
        upcoming = []
        for t in timetables:
            direction = t.get("odpt:railwayDirection", "").split(":")[-1]

            for tr in t.get("odpt:stationTimetableObject", []):
                dept_time = tr.get("odpt:departureTime")
                dest = tr.get("odpt:destinationStation", ["?"])[0].split(".")[-1]

                if dept_time and dept_time > now_hm:
                    upcoming.append({
                        "time": dept_time,
                        "dest": dest,
                        "dir": direction
                    })

        # 時刻順にソート
        upcoming.sort(key=lambda x: x["time"])

        # 上位5件を取得
        top5 = upcoming[:5]

        if top5:
            railway_info = f"({station_data['railway']})" if len([s for s in STATIONS if s['name'] == station_data['name']]) > 1 else ""
            lines = [f"🕒 {t['time']} → {t['dest']}" for t in top5]
            msg = f"🦡 【{station_data['name']} {railway_info}】の時刻表だモグ！\n\n" + "\n".join(lines)
        else:
            msg = f"🦡 【{station_data['name']}】\nもう電車がないモグ...💤"

        return msg

    except requests.exceptions.Timeout:
        return "🦡 APIがタイムアウトしたモグ...💦"
    except Exception as e:
        print(f"❌ 時刻表取得エラー: {e}")
        import traceback
        print(traceback.format_exc())
        return f"🦡 エラーが起きたモグ...💦\n{str(e)}"

    # ==========================================
    # 🦡 Web App API
    # ==========================================
    from pydantic import BaseModel
    class MoleRequest(BaseModel):
        station: str

    @app.post("/api/mole/timetable")
    async def mole_web_timetable(req: MoleRequest):
        """Webからの時刻表リクエスト処理"""
        print(f"🦡 Web Request: {req.station}")

        extracted = req.station.replace("駅", "").strip()

        # 駅検索ロジック（既存再利用）
        found_stations = []
        for s in STATIONS:
            if s["name"] == extracted:
                found_stations.append(s)

        if not found_stations:
            for s in STATIONS:
                if extracted in s["name"]:
                    found_stations.append(s)

        if not found_stations:
            return {"status": "error", "message": f"「{extracted}」は見つからないモグ...💦"}

        all_timetables = []
        for station in found_stations:
            timetable = get_timetable(station)
            if timetable and "もう電車がないモグ" not in timetable and "データがないモグ" not in timetable:
                all_timetables.append(timetable)

        if all_timetables:
            return {"status": "success", "message": "\n\n".join(all_timetables)}
        else:
            # 見つかったけどデータがない場合
            msg = get_timetable(found_stations[0])
            return {"status": "success", "message": msg}
```