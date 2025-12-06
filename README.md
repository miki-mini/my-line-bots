# 🤖 My LINE Bots Collection (どうぶつAIボット集)

Python と Google Gemini API を活用した、多機能なLINEボットたちのコード集です。
それぞれのボットが異なる個性と機能を持っています。

## 🐾 ボット一覧 (Bot List)

| アイコン | 名前 | 機能 | ファイル |
| :---: | :--- | :--- | :--- |
| <img src="images/fox.png" width="40"> | **キツネくん**<br>(Fox Teacher) | **YouTube動画要約 & 検索**<br>動画の内容をAIが解説し、Google検索で補足情報を教えてくれます。 | [fox.py](fox.py)<br>[説明書を読む](fox.md) |
| <img src="images/frog.jpg" width="40"> | **お天気ケロくん**<br>(Weather Frog) | **天気予報 & Googleマップ**<br>毎朝のお天気と服装情報通知＋位置情報から天気や周辺情報を教えてくれます。 | *Coming Soon...* |
| <img src="images/penguin.jpg" width="40"> | **秘書ペンギン**<br>(Secretary Penguin) | **メール送信 & 予定管理**<br>宛先と本文を送るとメールを代行送信します。 | *Coming Soon...* |
| <img src="images/rabbit.jpg" width="40"> | 月うさぎからのおくりもの🐇🌝<br>(Moon Rabbit) | **生活習慣記録 & 育成**<br>「おはよう」でポイントが貯まる育成ゲーム機能付き。 | [moon-rabbit](moon-rabbit)<br>[説明書を読む](moon-rabbit) |
| 🦫 | **ビーバーメモ**<br>(Beaver Memo) | **リマインダー & 予定抽出**<br>決まった時間の通知や、画像から予定を読み取って通知します。 | *Coming Soon...* |
| 🦦 | **カピバラ解説**<br>(Capybara News) | **AIニュース要約**<br>毎朝、最新のAIニュースを要約して届けてくれます。 | *Coming Soon...* |
| 🦉 | **フクロウ教授**<br>(Professor Owl) | **画像生成 & 健康管理**<br>画像生成や、カロリー計算・体重管理のグラフ化を行います。 | *Coming Soon...* |
| 🤖 | **おしゃべりVoidoll**<br>(Chat Voidoll) | **音声会話**<br>テキストだけでなく、音声での自然な会話が楽しめます。 | *Coming Soon...* |
| 🦔 | **もぐら駅長**<br>(Station Master Mole) | **時刻表 & 駅検索**<br>駅名の時刻表や、Googleマップでの場所案内をします。 | *Coming Soon...* |


## 🛠 全体で使用している技術

* **言語**: Python 3.10+
* **AI**: Google Gemini 2.5 Pro / Flash
* **基盤**: Google Cloud Run / FastAPI
* **PF**: LINE Messaging API

---
Creator: miki-mini