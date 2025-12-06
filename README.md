# 🤖 My LINE Bots Collection (どうぶつAIボット集)

Python と Google Gemini API を活用した、多機能なLINEボットたちのコード集です。
それぞれのボットが異なる個性と機能を持っています。

## 🐾 ボット一覧 (Bot List)

| アイコン | 名前 | 機能 | ファイル |
| :---: | :--- | :--- | :--- |
| <img src="images/fox.png" width="40"> | **キツネくん**<br>(Fox Teacher) | **YouTube動画要約 & 検索**<br>動画の内容をAIが解説し、Google検索で補足情報を教えてくれます。 | [fox.py](fox.py)<br>[説明書を読む](fox.md) |
| <img src="images/frog.png" width="40"> | **お天気ケロくん**<br>(Weather Frog) | **天気予報 & Googleマップ**<br>毎朝のお天気と服装情報通知＋位置情報から天気や周辺情報を教えてくれます。 | *Coming Soon...* |
| <img src="images/penguin.jpg" width="40"> | **秘書ペンギン**<br>(Secretary Penguin) | **メール送信 & 予定管理**<br>宛先と本文を送るとメールを代行送信します。 | *Coming Soon...* |

## 🛠 全体で使用している技術

* **言語**: Python 3.10+
* **AI**: Google Gemini 2.5 Pro / Flash
* **基盤**: Google Cloud Run / FastAPI
* **PF**: LINE Messaging API

---
Creator: miki-mini