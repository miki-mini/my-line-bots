
import sys
import os

print(f"Current CWD: {os.getcwd()}")
print(f"System Path: {sys.path}")

try:
    print("Attempting to import linebot...")
    import linebot.v3.webhooks
    print("Success: linebot.v3.webhooks")
    # from linebot.v3.webhooks import MessageEvent, TextMessageContent, LocationMessageContent, SourceUser
    import linebot.v3.webhooks
    print(dir(linebot.v3.webhooks))
except Exception as e:
    print(f"FAILED linebot: {e}")

try:
    print("Attempting to import animals.frog...")
    sys.path.append(os.getcwd()) # Ensure root is in path
    import animals.frog
    print("Success: animals.frog")
except Exception as e:
    print(f"FAILED animals.frog: {e}")
