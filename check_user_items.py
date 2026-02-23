import hashlib, sys
sys.stdout.reconfigure(encoding='utf-8')

def h(s): return hashlib.sha256(s.encode()).hexdigest()

CHEAT_HASHES = {
    "3db31dea83e45a634525336ff7c1242283fd2447bb6d9a71739ec601ffba227b": "VIM_DUNGEON_MODE",
    "3f9b554c360599a70a97a3f6c89c7738b1b8f42d0b179cffa8c3467edc132000": "OTOKO_FESTIVAL_MODE",
    "c5b5bd8614520330c97677744e674a30d05f149d1eb1fe960a8cb2bacb726ee8": "KAGYOHA_MODE",
    "62f37d466394c79936684e82d7716de0737e01d72cfdeaedf9f86bc16c0b26e5": "TEIOU_MODE",
    "15df0939948bdfc8ce7baf2139510b663179e3c43d59d04533aec2ff1a10e1d2": "TIME_SLIP_MODE",
    "cd1544c07be13937744560caccf91064cd68654cf95ffcbd15d1f100f9faf69d": "NOT_FOUND_MODE",
}
ALL = {h(v) for v in CHEAT_HASHES.values()} | {h("konami_code"), h("チャージショット"), h("root-access"), h(":wq_success")}

# ユーザーリストの各項目 (code, trigger, actual_stored_code)
items = [
    (":wq",          "チート入力",          ":wq"),
    ("男は黙って",   "チート入力",          "男は黙って"),
    ("改行波",       "改行波ボタン",        None),          # cheat_code=null
    ("0x81650",      "帝王53万ボタン",      "0x81650"),
    ("20380119",     "チート入力",          "20380119"),
    ("uuddlrlrba",   "コナミコマンド",      "konami_code"), # ba変換
    ("チャージショット", "長押し",           "チャージショット"),
    ("404_mode",     "送信4連打",           "404_mode"),
    (None,           "Prettier32連打",      None),          # cheat_code=null
    ("root-access",  "?gadget=root-access", "root-access"),
    (":wq_success",  "VIM証明書",           ":wq_success"),
]

print("項目                   | トリガー           | カウント?  | 理由")
print("-" * 75)
for code, trigger, stored in items:
    if stored is None:
        ok = "NO "
        reason = "cheat_code=null → 発見なし"
    else:
        sh = h(stored)
        if sh in CHEAT_HASHES:
            ok = "YES"
            reason = "CHEAT_HASHES -> _h(" + CHEAT_HASHES[sh] + ")"
        elif sh in ALL:
            ok = "YES"
            reason = "ALL_DISCOVERY_HASHES に一致"
        else:
            ok = "NO "
            reason = "_h('" + stored + "') はALL_DISCOVERY_HASHESにない"
    label = (code or "Prettier").ljust(16)
    print(f"{label} | {trigger.ljust(18)} | {ok} | {reason}")
