
import sys
import os

print("--- DEBUG: Starting Import Check ---")
print(f"Current Working Directory: {os.getcwd()}")
print(f"Python Path: {sys.path}")

try:
    print("Checking core imports...")
    import pytest
    import fastapi
    from linebot.v3 import WebhookHandler
    print("Core imports OK.")

    print("Checking Google Cloud imports...")
    import google.cloud.firestore
    import google.cloud.storage
    import vertexai
    from vertexai.generative_models import GenerativeModel
    print("Google Cloud imports OK.")

    print("Checking local modules...")
    # Add root to sys.path just in case (though usually implicit)
    sys.path.append(os.getcwd())

    import animals.frog
    print("animals.frog imported OK")
    import animals.voidoll
    print("animals.voidoll imported OK")
    import core.voidoll_service
    print("core.voidoll_service imported OK")
    import animals.mole
    print("animals.mole imported OK")
    import animals.bat
    print("animals.bat imported OK")
    import animals.beaver
    print("animals.beaver imported OK")
    import animals.capybara
    print("animals.capybara imported OK")
    import animals.fox
    print("animals.fox imported OK")
    import animals.penguin
    print("animals.penguin imported OK")
    import animals.rabbit
    print("animals.rabbit imported OK")
    import animals.whale
    print("animals.whale imported OK")
    import animals.owl
    print("animals.owl imported OK")

    print("--- DEBUG: All Checks Passed ---")

except Exception as e:
    print(f"!!! IMPORT ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
