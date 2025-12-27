import requests
import random
import os

def test_mars_api_manifest():
    print("🚀 Mars API Debug (Manifest Method)")

    api_key = os.getenv("NASA_API_KEY", "DEMO_KEY")
    print(f"🔑 Using API Key: {api_key}")

    target_rovers = ["curiosity", "perseverance"]

    for rover in target_rovers:
        print(f"\n📡 Testing rover: {rover} (via Manifest)...")

        # 1. Manifestを取得して最新のSol（火星日）を調べる
        manifest_url = f"https://api.nasa.gov/mars-photos/api/v1/manifests/{rover}"
        params = {"api_key": api_key}

        try:
            print(f"   Fetching manifest...")
            resp_m = requests.get(manifest_url, params=params, timeout=10)

            if resp_m.status_code != 200:
                print(f"   ❌ Manifest Error: {resp_m.status_code} {resp_m.text}")
                continue

            manifest_data = resp_m.json()
            max_sol = manifest_data["photo_manifest"]["max_sol"]
            print(f"   ✅ Max Sol: {max_sol}")

            # 2. そのSolの写真を取得
            photos_url = f"https://api.nasa.gov/mars-photos/api/v1/rovers/{rover}/photos"
            photo_params = {
                "sol": max_sol,
                "api_key": api_key,
                "page": 1
            }

            print(f"   Fetching photos for Sol {max_sol}...")
            resp_p = requests.get(photos_url, params=photo_params, timeout=10)

            if resp_p.status_code == 200:
                photo_data = resp_p.json()
                photos = photo_data.get("photos", [])
                print(f"   ✅ Photos found: {len(photos)}")
                if photos:
                    print(f"   Sample: {photos[0]['img_src']}")
            else:
                print(f"   ❌ Photo Error: {resp_p.status_code} {resp_p.text}")

        except Exception as e:
            print(f"   Exception: {e}")

    print("\n✅ Debug End")

if __name__ == "__main__":
    test_mars_api_manifest()
