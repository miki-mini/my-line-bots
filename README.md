# 🤖 My LINE Bots Collection (Animal Agents)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109%2B-009688?logo=fastapi&logoColor=white)
![Google Cloud Run](https://img.shields.io/badge/Google_Cloud-Run-4285F4?logo=google-cloud&logoColor=white)
![Gemini](https://img.shields.io/badge/AI-Gemini_2.5_Flash-8E75B2?logo=google-gemini&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

> [!NOTE]
> ✨ <a href="https://usagi-oekaki-service-1032484155743.asia-northeast1.run.app" target="_blank"><strong>Live Demo Portal / デモサイトはこちら</strong></a> ✨
><br>
> BOTたちが集まるポータルサイトを公開しました！(PC / Mobile 対応)

## API Documentation

📖 [Swagger UI](https://usagi-oekaki-service-1032484155743.asia-northeast1.run.app/docs)

※一部のAPIはデモ用にレート制限をかけています

**個性豊かなAIどうぶつたちが、あなたのLINE生活をサポートします。**

このリポジトリは、Google Gemini 2.5 (Flash/Pro) と Google Cloud (Cloud Run, Firestore, Vertex AI) をフル活用した、実用的なLINEボットの集合体です。
リマインダー、画像生成、天気予報、メール代行など、**それぞれの動物が「得意分野」を持ったマイクロモジュール**として実装されています。

---

## 🧩 Design Philosophy (デザイン哲学)
**「無機質な便利ツールではなく、毎日の生活に寄り添うパートナーを」**

*   **なぜ「動物」なのか？**
    *   AIの回答は時に固くなりがちですが、フクロウ教授や星くじらのような「キャラクター」を通すことで、親しみやすく、感情移入しやすいインターフェースを目指しました。
*   **なぜ「LINE」なのか？**
    *   新しいアプリをインストールする必要がなく、誰もが使い慣れたチャット画面で最先端のAI機能にアクセスできる「Accessibility（アクセシビリティ）」を最優先しました。

## 💡 UX Considerations (ユーザー体験へのこだわり)
*   **Mobile First & Immersive UI**:
    *   Webビューでは `100dvh` (Dynamic Viewport Height) を採用し、スマホのアドレスバーによる表示崩れを徹底的に排除。iPhoneのホームバーにも配慮したセーフエリア設計を行っています。
*   **Natural Interaction**:
    *   ボットの返信に「入力中...」のアニメーションを入れることで、機械的な待ち時間を「会話の間」に変える工夫を凝らしました。

## 🔧 Technical Challenges (技術的な挑戦)
*   **NASA API & Hotlink Protection**:
    *   「星くじら」の開発中、NASAやWikimediaの画像を外部表示する際に403エラーが多発。
    *   解決策として、画像をサーバーサイドで安全にダウンロードし、自前の静的ファイルとして配信する「Self-Hosted Proxy」構成を実装し、信頼性100%の表示を実現しました。
*   **Micro-Module Architecture**:
    *   当初のモノリシックな `main.py` (1500行超) を、動物ごとに独立したモジュールとルーターに分割。機能追加が他のボットに影響しない堅牢な設計へリファクタリングしました。

---

## 🐾 ボット一覧 (Agents List)

各ボットは `animals/` ディレクトリ内で個別のモジュールとして管理されています。

| アイコン | 名前 | 役割・機能 | 技術スタック |
| :---: | :--- | :--- | :--- |
| <img src="animals/images/beaver.jpg" width="40"> | **まめなビーバーメモ🦫**<br>[(Beaver)](animals/beaver.md) | **予定管理 & OCR**<br>学校のプリントを写真で送るだけで、AIが予定を抽出してリマインド。 | `Gemini Vision` `Firestore` `GAS` |
| <img src="animals/images/fox.png" width="40"> | **キツネくんの動画要約🦊**<br>[(Fox)](animals/fox.md) | **動画要約 & 検索**<br>YouTube動画の内容を要約し、関連情報を検索して深掘り解説。 | `GenAI SDK` `Grounding with Search` |
| <img src="animals/images/owl.jpg" width="40"> | **フクロウ教授画像生成🦉**<br>[(Owl)](animals/owl.md) | **画像生成 & 健康**<br>「〜の絵を描いて」で即座に画像生成。カロリー計算もお手の物。 | `Imagen 3` `Matplotlib` |
| <img src="animals/images/frog.jpg" width="40"> | **☀️カエルくんのお天気予報🐸**<br>[(Frog)](animals/frog.md) | **天気 & 外出支援**<br>毎朝の天気予報と、位置情報から周辺のおすすめスポットを紹介。 | `Google Maps API` `GAS` |
| <img src="animals/images/penguin.jpg" width="40"> | **スーパー秘書ペンギン🐧**<br>[(Penguin)](animals/penguin.md) | **メール代行 & 接待**<br>用件を送るだけでビジネスメールを作成・送信。接待のお店選びも。 | `Gmail API` `Search` |
| <img src="animals/images/capybara.jpg" width="40"> | **AIトピックのカピバラ解説**<br>[(Capybara)](animals/capybara.md) | **ニュース解説**<br>最新のAIニュースなどを検索し、分かりやすく要約・解説。 | `Google Search` |
| <img src="animals/images/mole.jpg" width="40"> | **もぐら駅長**<br>[(Mole)](animals/mole.md) | **交通案内**<br>駅の時刻表や乗り換え案内をサポート。 | `Train Logic` |
| <img src="animals/images/voidoll.jpg" width="40"> | **🤖おしゃべりVoidollねこ🐱**<br>[(Voidoll)](animals/voidoll.md) | **音声対話**<br>テキストだけでなく、音声ファイルでの自然な会話が可能。 | `Audio Processing` |
| <img src="animals/images/whale.jpg" width="40"> | **星くじらからの光の便り🐋💫**<br>[(Whale)](animals/whale.md) | **癒やし & 宇宙**<br>NASAのAPIを使って、美しい宇宙の写真や情報を届ける。 | `NASA API` |
| <img src="animals/images/bat.jpg" width="40"> | **コウモリの番組お知らせ🦇**<br>[(Bat)](animals/bat.md) | **番組通知**<br>指定したタレントやキーワードのTV出演情報を毎朝通知。 | `Web Scraping` |
| <img src="animals/images/alpaca.jpg" width="40"> | **アルパカのまつエクサロン🦙**<br>[(Alpaca)](animals/alpaca.md) | **まつエクシミュレーション**<br>写真でまつげエクステの仕上がりをAIシミュレーション。 | `Face Mesh` `Canvas` |
| <img src="animals/images/flamingo.jpg" width="40"> | **姿勢のフラミンゴ先生**<br>[(Flamingo)](animals/flamingo.md) | **姿勢矯正 & ゲーム**<br>エッジAIで姿勢の歪みをチェック＆片足バランスゲーム。完全無料・安心設計。 | `MediaPipe` `Client-Side AI` |
| <img src="animals/images/butterfly.png" width="40"> | **美の蝶々パーソナル🦋**<br>[(Butterfly)](animals/butterfly.md) | **パーソナルカラー & 顔タイプ**<br>AIが似合うシーズンカラーと顔型に合う髪型を診断。 | `Gemini 2.5` `FastAPI` |
| <img src="animals/images/squirrel.png" width="40"> | **リスのほっぺたどんぐりゲーム🐿️**<br>(Squirrel Game)<br>![WebApp](https://img.shields.io/badge/WEBアプリ！-brown) | **対戦アクションゲーム**<br>カメラで手を認識し、落ちてくるどんぐりをキャッチしてほっぺたを膨らませる2人対戦ゲーム。 | [🔍 HTML](static/squirrel.html)<br>[📜 説明書](animals/squirrel.md) |
| <img src="animals/images/fish.jpg" width="40"> | **カラフルお魚のお部屋水族館🐠**<br>(Fish Room Aquarium)<br>![WebApp](https://img.shields.io/badge/WEBアプリ！-blue) | **バーチャル水族館**<br>手で魚と触れ合える癒やしの空間。サメやタコも登場します。 | [🔍 HTML](static/fish.html) |

👉 **[詳細ドキュメントとデモはこちら (animals/README.md)](animals/README.md)**

---

## 🏗 アーキテクチャ (Architecture)

**「管理人室 (main.py)」** がLINEからの全リクエストを受け取り、適切な **「動物の部屋 (Modules)」** に振り分けるディスパッチャーパターンを採用しています。これにより、機能追加や修正が他のボットに影響を与えません。

```mermaid
graph TD
    %% ユーザー
    User(("User 👤"))

    %% LINE Platform
    subgraph LINE ["LINE Platform"]
        MessagingAPI["Messaging API<br/>(Webhook)"]
    end

    %% Google Cloud
    subgraph GCP ["Google Cloud Platform"]
        direction TB

        %% Server
        subgraph CloudRun ["Cloud Run (Server)"]
            Main["🏢 main.py<br/>(Dispatcher)"]

            subgraph Modules ["Animals Modules"]
                Beaver["🦫 Beaver"]
                Fox["🦊 Fox"]
                Owl["🦉 Owl"]
                Others["..."]
            end
        end

        %% Data & AI
        Firestore[("Firestore<br/>Data Store")]
        VertexAI["Vertex AI<br/>Gemini 2.5"]
        Imagen["Imagen 3<br/>Image Gen"]
        Search["Google Search<br/>Grounding"]
    end

    %% Flow
    User -->|Message/Image| MessagingAPI
    MessagingAPI -->|"POST /callback"| Main

    Main -->|Routing| Beaver
    Main -->|Routing| Fox
    Main -->|Routing| Owl
    Main -->|Routing| Others

    Beaver <-->|"Read/Write"| Firestore
    Beaver -->|OCR| VertexAI
    Fox -->|Search| Search
    Owl -->|Generate| Imagen

    Modules -->|Response| Main
    Main -->|Reply| MessagingAPI
    MessagingAPI -->|Notification| User
```

### 工夫した点
*   **モジュール分割**: 当初は1つのファイル(`main.py`)でしたが、コードが1500行を超えて保守不能になったため、動物ごとにファイルを分割しました。（[詳細記事: Zenn](https://zenn.dev/miki_mini/articles/30264063ad4b7d)）
*   **Search Grounding**: Vertex AIのGrounding機能を使用し、最新情報に基づいた回答を実現しています（キツネ、カピバラ）。
*   **Vision & OCR**: Geminiの画像認識能力を使い、非構造データ（チラシ）を構造データ（カレンダー予定）に変換しています（ビーバー）。

---

## 🛠 開発環境・セットアップ

このプロジェクトは `FastAPI` で動作しています。

### 必要要件
*   Python 3.10+
*   Google Cloud Project (Vertex AI / Firestore enabled)
*   LINE Messaging API Channels

### インストール

```bash
# リポジトリのクローン
git clone https://github.com/miki-mini/my-line-bots.git
cd my-line-bots

# 依存関係のインストール
pip install -r requirements.txt
```

### 環境変数 (.env)
ルートディレクトリに `.env` ファイルを作成し、以下のキーを設定してください。

```ini
GCP_PROJECT_ID=your-project-id
GCS_BUCKET_NAME=your-bucket-name
GEMINI_API_KEY=your-api-key

# 各ボットのLINE Token
BEAVER_ACCESS_TOKEN=...
BEAVER_CHANNEL_SECRET=...
# (他ボットも同様)
```

### ローカル起動

```bash
uvicorn main:app --reload
```

---

## 🔗 関連リンク

*   **Zenn**: 開発の裏話や技術解説記事を投稿しています。[miki-miniのZenn記事一覧](https://zenn.dev/miki_mini)


---

Developed by **miki-mini**