# 🐺 WOLF SHADOWING

**英語嫌いのための独り言シャドーイングアプリ**

文法ゼロ・音で覚える。自分の本心を英語にするから、脳への定着率が段違い。

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[🌟 今すぐ試す](https://your-site-url.com) | [📖 技術記事](https://zenn.dev/your-article)

![WOLF SHADOWING Demo](images/demo.gif)

## 🎯 特徴

- **独り言→超訳**: 日本語の愚痴を、Gemini AIが超クールなネイティブ英語に変換
- **3回リピート再生**: 耳で覚えるまで自動ループ
- **あいまいシャドーイング判定**: 85%以上の類似度でOK！完璧じゃなくても合格
- **Firestoreキャッシュ**: 同じ言葉なら2回目以降は爆速＆無料
- **シンプルな操作**: たった3ステップで誰でも使える

## 🚀 デモ

### 使い方（3ステップ）

1. **マイクボタンをタップ** → 独り言を話す
2. **TRANSLATEボタンをタップ** → 英語に変換＆3回リピート
3. **マイクボタンをタップ** → 一緒に遠吠え！

```
ユーザー: 「今日のプレゼン、めっちゃうまくいった！最高の気分！」
　　↓
AI: "Today's presentation went incredibly well! I'm feeling absolutely amazing!"
　　↓
🔈 3回リピート再生
　　↓
ユーザー: 「トゥデイズ プレゼンテーション...」
　　↓
判定: 🎉 Perfect Howling! (Similarity: 92%)
```

## 🛠️ 技術スタック

### フロントエンド
- Vanilla JavaScript
- Web Speech API（音声認識）
- CSS3（ダークモードUI）

### バックエンド
- FastAPI (Python 3.9+)
- Google Cloud Text-to-Speech (Journey Voice)
- Vertex AI Gemini 2.5 Flash
- Firestore（キャッシュ）

### 主要アルゴリズム
- レーベンシュタイン距離（あいまい検索）
- SHA-256ハッシュ（キャッシュキー）

## 📦 セットアップ

### 前提条件

- Python 3.9以上
- Google Cloud Platform アカウント
- 以下のGCP APIが有効化されていること：
  - Cloud Text-to-Speech API
  - Vertex AI API
  - Firestore API

### 1. リポジトリをクローン

```bash
git clone https://github.com/your-username/wolf-shadowing.git
cd wolf-shadowing
```

### 2. 仮想環境を作成

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 依存関係をインストール

```bash
pip install -r requirements.txt
```

### 4. Google Cloud認証

```bash
# サービスアカウントキーをダウンロードして設定
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your-service-account-key.json"

# または、gcloud CLIを使用
gcloud auth application-default login
```

### 5. 環境変数を設定

`.env.example`をコピーして`.env`を作成し、必要な値を設定してください。

```bash
cp .env.example .env
```

```.env
# Google Cloud Project
GCP_PROJECT_ID=your-project-id

# Firestore Collection Names
FIRESTORE_TRANSLATIONS_COLLECTION=wolf_translations
FIRESTORE_TTS_COLLECTION=wolf_tts
```

### 6. サーバーを起動

```bash
uvicorn main:app --reload
```

ブラウザで `http://localhost:8000` を開きます。

## 📁 ディレクトリ構造

```
wolf-shadowing/
├── main.py                 # FastAPIメインアプリケーション
├── routers/
│   └── butsubutsu.py      # 翻訳・TTS APIエンドポイント
├── static/
│   ├── index.html         # フロントエンド UI
│   └── images/
│       └── wolf_howl.jpg  # 背景画像
├── requirements.txt       # Python依存関係
├── .env.example          # 環境変数テンプレート
├── .gitignore
└── README.md
```

## 🔧 主要APIエンドポイント

### POST /api/butsubutsu/translate

日本語の独り言を英語に翻訳します。

**リクエスト:**
```json
{
  "text": "今日のプレゼン、めっちゃうまくいった！"
}
```

**レスポンス:**
```json
{
  "english_text": "Today's presentation went incredibly well! I'm feeling absolutely amazing!"
}
```

### POST /api/butsubutsu/speak

英語テキストを音声（MP3）に変換します。

**リクエスト:**
```json
{
  "text": "Today's presentation went incredibly well!"
}
```

**レスポンス:**
```json
{
  "audio_content": "BASE64_ENCODED_MP3_DATA..."
}
```

## 🎨 技術的な工夫

### 1. あいまいシャドーイング判定

レーベンシュタイン距離を用いた類似度判定により、完璧じゃなくても85%以上の類似度で合格判定。

```javascript
function getSimilarity(str1, str2) {
    const maxLength = Math.max(str1.length, str2.length);
    if (maxLength === 0) return 1.0;
    const distance = levenshtein(str1, str2);
    return 1.0 - (distance / maxLength);
}

// 85%以上で合格
if (similarity >= 0.85) {
    // Perfect Howling! 🎉
}
```

**効果:**
- 「meeting」を「meetin」と発音しても合格（類似度92%）
- 初心者でも挫折しない優しい判定

**翻訳例:**
- 「めっちゃ疲れた」→ "I'm so done."（"very tired" より自然）
- 「やばい、遅刻する」→ "Crap, I'm gonna be late."（ネイティブが実際に使う）
- 「今日のプレゼンうまくいった！」→ "Nailed it today!"（達成感が伝わる）

### 2. Firestoreキャッシュ

同じ入力は2回目以降、キャッシュから即座に返却。

```python
# SHA-256でハッシュ化
doc_id = hashlib.sha256(request.text.encode("utf-8")).hexdigest()
doc_ref = db.collection("wolf_translations").document(doc_id)

# キャッシュHIT時は即返却（エラーハンドリング付き）
try:
    doc = doc_ref.get()
    if doc.exists:
        return {"english_text": doc.to_dict()["english_text"]}
except Exception as e:
    print(f"[WARNING] Firestore Read Error (Proceeding without cache): {e}")
```

**効果:**
- 1回目: Gemini API呼び出し（0.5〜1秒）
- 2回目以降: Firestoreから即返却（0.1秒以下）
- コスト: 同じ表現なら2回目以降は完全無料

### 3. Geminiプロンプト設計

「正確性」と「自然さ」の両立を実現。

```python
prompt = f"""
あなたは日本語ネイティブが独り言で言いそうなフレーズを、ネイティブ英語話者が同じシチュエーションで自然に言う英語に変換する翻訳者です。

重要なルール:
- 直訳ではなく、英語話者が同じ感情・状況で実際に口にする表現にする
- 日本語の感情やニュアンス（喜び、イライラ、疲れ、達成感など）をそのまま英語で表現する
- カジュアルな独り言なので、堅い表現は避ける
- 短く、自然に口から出る表現にする
- 説明や文法解説は一切不要。英語のみ出力

例:
- 「めっちゃ疲れた」→ "I'm so done."
- 「やばい、遅刻する」→ "Crap, I'm gonna be late."
- 「今日のプレゼンうまくいった！」→ "Nailed it today!"
"""
```

**ポイント:**
- `temperature: 0.7` → クリエイティブすぎず、正確性を保つ
- 具体例を提示してAIの理解を助ける
- 直訳ではなく、ネイティブが実際に使う表現に変換

## 💰 コストについて

個人利用の範囲であれば、**ほぼ無料（0円）**で運用可能です。

### 無料枠

| サービス | 無料枠 |
|---------|--------|
| Gemini 2.5 Flash | 15 Request/分、1日1,500 Request |
| Text-to-Speech (Journey) | 毎月50万文字 |
| Firestore | 読み取り: 50,000回/日<br>書き込み: 20,000回/日 |

**Firestoreキャッシュの効果:**
- 同じ表現なら2回目以降は完全無料
- 1日100回遠吠えしても無料枠に収まる

## 🚢 デプロイ

### Google Cloud Run へのデプロイ

```bash
# Dockerイメージをビルド
gcloud builds submit --tag gcr.io/[PROJECT-ID]/wolf-shadowing

# Cloud Runにデプロイ
gcloud run deploy wolf-shadowing \
  --image gcr.io/[PROJECT-ID]/wolf-shadowing \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated
```

## 📝 開発ロードマップ

- [ ] 履歴機能（過去に遠吠えした英語を復習）
- [ ] スピーキングレベル判定
- [ ] PWA化（アプリとしてインストール可能に）
- [ ] 多言語対応（英語以外の言語も学習可能に）

## 🤝 コントリビューション

プルリクエストを歓迎します！大きな変更の場合は、まずissueを開いて変更内容を議論してください。

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを開く

## 📄 ライセンス

このプロジェクトは[MIT License](LICENSE)の下で公開されています。



## 👤 作者

**miki-mini**

