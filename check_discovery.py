import hashlib

def h(s): return hashlib.sha256(s.encode()).hexdigest()

CHEAT_HASHES = {
    "3db31dea83e45a634525336ff7c1242283fd2447bb6d9a71739ec601ffba227b": "VIM_DUNGEON_MODE",
    "3f9b554c360599a70a97a3f6c89c7738b1b8f42d0b179cffa8c3467edc132000": "OTOKO_FESTIVAL_MODE",
    "c5b5bd8614520330c97677744e674a30d05f149d1eb1fe960a8cb2bacb726ee8": "KAGYOHA_MODE",
    "62f37d466394c79936684e82d7716de0737e01d72cfdeaedf9f86bc16c0b26e5": "TEIOU_MODE",
    "15df0939948bdfc8ce7baf2139510b663179e3c43d59d04533aec2ff1a10e1d2": "TIME_SLIP_MODE",
    "cd1544c07be13937744560caccf91064cd68654cf95ffcbd15d1f100f9faf69d": "NOT_FOUND_MODE",
}

ALL_DISCOVERY_HASHES = {h(v) for v in CHEAT_HASHES.values()} | {
    h("konami_code"),
    h("チャージショット"),
    h("root-access"),
    h(":wq_success"),
}

print("ALL_DISCOVERY_HASHES count:", len(ALL_DISCOVERY_HASHES))
print()

# Simulate all sendVote calls
sends = [
    ("チャージショット", "チャージマン"),
    ("uuddlrlrba",      "とある名人"),
    ("root-access",     "ハッカー"),
    (":wq_success",     "testuser"),
    ("404_mode",        "NotFoundUser"),
    ("otoko_cert",      "testuser"),
    ("kagyoha_cert",    "testuser"),
    ("53man_cert",      "testuser"),
    ("game_clear",      "宇宙の帝王"),
    ("0x81650",         "宇宙の帝王"),
    ("osii",            "惜しい人"),
]

print("--- sendVote discovery simulation ---")
for code, helper in sends:
    code_hash = hashlib.sha256(code.encode()).hexdigest()
    if code_hash in CHEAT_HASHES:
        mode = CHEAT_HASHES[code_hash]
        stored = h(mode)
        counts = stored in ALL_DISCOVERY_HASHES
        print(f"  {code!r:20} -> CHEAT_HASHES({mode}) -> counts: {counts}")
        continue
    if helper == "手入力ハッカー":
        print(f"  {code!r:20} -> skip (手入力ハッカー)")
        continue
    dk = "konami_code" if ("BA" in code or "ba" in code) else code
    stored = h(dk)
    counts = stored in ALL_DISCOVERY_HASHES
    print(f"  {code!r:20} -> _h({dk!r}) -> counts: {counts}")

print()
print("--- CHEAT_HASHES path (manual input, all 6 modes) ---")
for mode in CHEAT_HASHES.values():
    stored = h(mode)
    counts = stored in ALL_DISCOVERY_HASHES
    print(f"  {mode:25} -> counts: {counts}")
