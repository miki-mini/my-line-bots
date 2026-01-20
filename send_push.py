import requests
import urllib.parse

def send_push():
    print("="*50)
    print("🦝 アライグマ通知送信ツール")
    print("="*50)

    # Check if server is likely running
    base_url = "http://localhost:8080"

    while True:
        message = input("\n送信するメッセージを入力してください (終了するには 'q' を入力): ")
        if message.lower() == 'q':
            break

        if not message:
            message = "片付けの時間だよ！"

        # Encode message for URL
        encoded_message = urllib.parse.quote(message)
        url = f"{base_url}/api/raccoon/push/send?message={encoded_message}"

        try:
            print(f"送信中... {message}")
            response = requests.post(url)

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    print(f"✅ 送信成功！ ({data.get('sent_count')}件)")
                else:
                    print(f"❌ エラー: {data}")
            else:
                print(f"❌ サーバーエラー: {response.status_code}")
                print(response.text)

        except requests.exceptions.ConnectionError:
            print("❌ サーバーに接続できませんでした。")
            print("   `python main.py` でアプリを起動しているか確認してください。")
            break
        except Exception as e:
            print(f"❌ 予期せぬエラー: {e}")

if __name__ == "__main__":
    send_push()
