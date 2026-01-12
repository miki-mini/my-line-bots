
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

    modules_to_test = [
        "animals.frog",
        "animals.voidoll",
        "core.voidoll_service",
        "animals.mole",
        "animals.bat",
        "animals.beaver",
        "animals.capybara",
        "animals.fox",
        "animals.penguin",
        "animals.rabbit",
        "animals.whale",
        "animals.owl"
    ]

    import importlib
    failed_modules = []

    for module_name in modules_to_test:
        try:
            print(f"Importing {module_name}...", end=" ")
            importlib.import_module(module_name)
            print("OK")
        except Exception as e:
            print(f"FAILED! Error: {e}")
            failed_modules.append(module_name)

    if failed_modules:
        print(f"!!! CRITICAL: The following modules failed to import: {failed_modules}")
        sys.exit(1)

    print("--- DEBUG: All Checks Passed ---")

except Exception as e:
    print(f"!!! IMPORT ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
