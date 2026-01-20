from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
import base64

def generate_vapid_keys():
    # 1. Generate P-256 (SECP256R1) Key Pair
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    # 2. Export Private Key (Raw 32 bytes scalar)
    private_val = private_key.private_numbers().private_value
    private_bytes = private_val.to_bytes(32, byteorder='big')

    # 3. Export Public Key (Uncompressed Point: 0x04 + x + y)
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )

    # 4. Helper for Base64URL encoding (no padding)
    def b64url(data):
        return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

    print("="*60)
    print("🦝 Raccoon App VAPID Keys Generated (via cryptography)")
    print("="*60)
    print(f"Public Key:\n{b64url(public_bytes)}")
    print("-" * 20)
    print(f"Private Key:\n{b64url(private_bytes)}")
    print("="*60)
    print("\nINSTRUCTIONS:")
    print("1. Copy 'Public Key' -> `static/raccoon.html` (applicationServerKey)")
    print("2. Copy 'Private Key' -> `.env` (VAPID_PRIVATE_KEY)")
    print("3. Add `VAPID_CLAIMS_SUB=mailto:your@email.com` to `.env`")

if __name__ == "__main__":
    try:
        generate_vapid_keys()
    except Exception as e:
        print(f"Error: {e}")
        print("Please ensure 'cryptography' is installed: pip install cryptography")
