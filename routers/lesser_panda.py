from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import random
import hashlib
from datetime import datetime
from dataclasses import dataclass, field
import os
import time
from google.cloud import firestore

router = APIRouter()

CHEAT_HASHES = {
    "3db31dea83e45a634525336ff7c1242283fd2447bb6d9a71739ec601ffba227b": "VIM_DUNGEON_MODE",
    "3f9b554c360599a70a97a3f6c89c7738b1b8f42d0b179cffa8c3467edc132000": "OTOKO_FESTIVAL_MODE",
    "c5b5bd8614520330c97677744e674a30d05f149d1eb1fe960a8cb2bacb726ee8": "KAGYOHA_MODE",
    "62f37d466394c79936684e82d7716de0737e01d72cfdeaedf9f86bc16c0b26e5": "TEIOU_MODE",
    "15df0939948bdfc8ce7baf2139510b663179e3c43d59d04533aec2ff1a10e1d2": "TIME_SLIP_MODE",
    "cd1544c07be13937744560caccf91064cd68654cf95ffcbd15d1f100f9faf69d": "NOT_FOUND_MODE",
}
# ハッシュ化ヘルパー（コードからネタバレしないよう発見キーをすべてハッシュ化）
def _h(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

# 全隠し要素のハッシュセット（CHEAT_HASHES 6個 + その他 4個 = 計10個）
ALL_DISCOVERY_HASHES = {_h(v) for v in CHEAT_HASHES.values()} | {
    _h("konami_code"),
    _h("チャージショット"),
    _h("root-access"),
    _h(":wq_success"),
}

# Firestore Configuration
# Assumes GOOGLE_APPLICATION_CREDENTIALS is set or environment is authenticated
db = None
try:
    db = firestore.Client()
    print("Firestore Client Initialized")
except Exception as e:
    print(f"Firestore Init Failed: {e}. Falling back to memory/json (not safe for concurrency).")

DOC_REF = db.collection("games").document("kinotake") if db else None

# Local Cache for Read Optimization
class StateCache:
    data = None
    last_fetched = 0
    TTL = 5.0 # 5 second cache (reduce Firestore reads)

    def get(self):
        if self.data and (time.time() - self.last_fetched < self.TTL):
            return self.data

        # Fetch from Firestore
        if DOC_REF:
            try:
                doc = DOC_REF.get()
                if doc.exists:
                    self.data = doc.to_dict()
                else:
                    # Init doc
                    initial_state = {
                        "bamboo": 0, "mushroom": 0, "prettier": 0,
                        "cultprits": [], "discovered_cheats": []
                    }
                    DOC_REF.set(initial_state)
                    self.data = initial_state
                self.last_fetched = time.time()
                return self.data
            except Exception as e:
                print(f"Firestore Read Error: {e}")
                return self.data or {}
        return {} # Fallback

cache = StateCache()

class VoteRequest(BaseModel):
    team: str  # "bamboo", "mushroom", "prettier"
    count: int = 1
    cheat_code: Optional[str] = None
    helper_name: Optional[str] = None # e.g. "Anonymous Vimmer"

@router.get("/api/kinotake/state")
async def get_state():
    data = cache.get()
    # 全10個の隠し要素のうち発見済みのものだけカウント（ハッシュ比較）
    discovered_cheats = data.get("discovered_cheats", [])
    discovered_count = len([x for x in discovered_cheats if x in ALL_DISCOVERY_HASHES])
    return {
        "bamboo": data.get("bamboo", 0),
        "mushroom": data.get("mushroom", 0),
        "prettier": data.get("prettier", 0),
        "culprits": data.get("cultprits", [])[-20:],
        "discovered_count": discovered_count,
        "total_cheats": len(ALL_DISCOVERY_HASHES)  # 自動的に10
    }

# Secret Codes Configuration
SECRET_CODES = {
    "上上下下左右左右BA": {"team": "bamboo", "count": 8, "helper": "とある名人"},
    "↑↑↓↓←→←→BA": {"team": "bamboo", "count": 8, "helper": "とある名人"},
    "uuddlrlrba": {"team": "bamboo", "count": 8, "helper": "とある名人"},
    "uuddlrlrba": {"team": "bamboo", "count": 16, "helper": "とある名人"},
    "チャージ": {"team": "any", "count": 100, "helper": "チャージマン"}, # Special case
    ":wq": {"team": "vim", "count": 0, "helper": "VimUser"}, # Special mode
    ":q!": {"team": "vim", "count": 0, "helper": "Quitter"},
    ":wq_success": {"team": "vim_win", "count": 0, "helper": "Survivor"}, # Log only
    "任侠道": {"team": "otoko", "count": 0, "helper": "MatsuriMaster"}, # Otoko Festival
    "CRLF": {"team": "kagyoha", "count": 0, "helper": "NewLineMaster"}, # Kagyoha Mode
    "53万": {"team": "teiou", "count": 0, "helper": "SpaceEmperor"}, # Universe Emperor Mode
    "TimeTraveler": {"team": "timeslip", "count": 0, "helper": "TimeTraveler"}, # Time Slip Mode
}

@router.post("/api/kinotake/vote")
async def vote(request: VoteRequest):
    # Fake API Limit Check
    if request.count > 10 and request.count != 65535 and request.count != 9001 and request.count != 530000 and random.random() < 0.02:
         return {"success": False, "error": "RATE_LIMIT", "message": "API利用制限: 呼び出しが多すぎます"}

    # Cheat handling (ハッシュ比較 - コードを直接書かない)
    if request.cheat_code:
        h = hashlib.sha256(request.cheat_code.encode()).hexdigest()
        if h in CHEAT_HASHES:
            mode_msg = CHEAT_HASHES[h]
            # 発見カウント更新
            if DOC_REF:
                try:
                    DOC_REF.update({"discovered_cheats": firestore.ArrayUnion([_h(mode_msg)])})
                    cache.last_fetched = 0  # キャッシュ無効化（次の fetchState で最新値を返す）
                except Exception as e:
                    print(f"Discovery update error: {e}")
            return {"success": True, "message": mode_msg}

    # Firestore Updates
    updates = {}

    # 1. Update Votes
    if request.team == "bamboo":
        updates["bamboo"] = firestore.Increment(request.count)
    elif request.team == "mushroom":
        updates["mushroom"] = firestore.Increment(request.count)
    elif request.team == "prettier":
        updates["prettier"] = firestore.Increment(request.count)

    # 2. Update Logs
    if request.cheat_code:
        helper = request.helper_name or "名無し"
        action_msg = f"{request.cheat_code} を発動！"

        # Custom Messages
        if request.helper_name == "手入力ハッカー" and request.cheat_code not in SECRET_CODES:
             action_msg = f"謎のコマンド '{request.cheat_code}' を試行"
        elif request.cheat_code == "kagyoha_cert":
             action_msg = "伝説の一撃免許 を取得！"
        elif request.cheat_code == "otoko_cert":
             action_msg = "漢(おとこ)の証明書 を取得！"
        elif request.cheat_code == ":wq_success":
             action_msg = "VIMの迷宮から脱出！"
        elif request.cheat_code == "20380119":
             action_msg = "時空の歪みが発生！"
        elif request.cheat_code == "404_mode":
             action_msg = "Not Found Mode: 全員 -404点！"
             updates["bamboo"] = firestore.Increment(-404)
             updates["mushroom"] = firestore.Increment(-404)
             updates["prettier"] = firestore.Increment(-404)

        points_str = f" (+{request.count:,}点)" if request.count > 0 else ""
        log_entry = f"{datetime.now().strftime('%H:%M:%S')} - {helper} が {action_msg}{points_str}"
        updates["cultprits"] = firestore.ArrayUnion([log_entry])

        # Discovery Logic
        discovery_key = request.cheat_code
        if "BA" in discovery_key or "ba" in discovery_key:
             discovery_key = "konami_code"

        if request.helper_name != "手入力ハッカー":
            updates["discovered_cheats"] = firestore.ArrayUnion([_h(discovery_key)])

    # Log non-cheat votes with helper_name (e.g. otoko/kagyoha team picks)
    elif request.helper_name and request.count > 0:
        team_name = {"bamboo": "たけのこ", "mushroom": "きのこ", "prettier": "Prettier"}.get(request.team, request.team)
        log_entry = f"{datetime.now().strftime('%H:%M:%S')} - {request.helper_name} が {team_name} に +{request.count:,}点！"
        updates["cultprits"] = firestore.ArrayUnion([log_entry])

    # Execute Update
    if DOC_REF and updates:
        try:
            DOC_REF.update(updates)
        except Exception as e:
            print(f"Firestore Update Error: {e}")

    return {"success": True, "state": await get_state()}

@router.get("/kinotake", response_class=HTMLResponse)
async def kinotake_page():
     with open("static/kinotake/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
