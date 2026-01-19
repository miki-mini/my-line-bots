try:
    from pywebpush import webpush

    # Generate keys
    vapid_keys = webpush.generate_vapid_keys()

    print("="*60)
    print("🦝 Raccoon App VAPID Keys Generated")
    print("="*60)
    print(f"Public Key:\n{vapid_keys['public_key']}")
    print("-" * 20)
    print(f"Private Key:\n{vapid_keys['private_key']}")
    print("="*60)
    print("\nINSTRUCTIONS:")
    print("1. Copy 'Public Key' and paste it in `static/raccoon.html` (replace the placeholder in applicationServerKey).")
    print("2. Copy 'Private Key' and add it to your `.env` file as:")
    print("   VAPID_PRIVATE_KEY=<your_private_key>")
    print("3. Add `VAPID_CLAIMS_SUB=mailto:your@email.com` to `.env` as well.")

except ImportError:
    print("❌ pywebpush is not installed. Please run:")
    print("pip install -r requirements.txt")
