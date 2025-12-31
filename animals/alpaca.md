# 🦙 アルパカのまつエクサロン

**まつエクの仕上がりをAIでシミュレーション**

<img src="images/alpaca.jpg" width="100">

写真を撮るだけで、まつエクの仕上がりをリアルタイムでプレビューできるWebアプリです。
Gemini 2.5 Flash が目の形を分析し、最適なスタイルを提案します。

| 選択画面 | 比較画面 |
|:--:|:--:|
| <img src="https://storage.googleapis.com/zenn-user-upload/eeedbc69598e-20251231.png"   width="300"> | <img src="https://storage.googleapis.com/zenn-user-upload/a585ca475661-20251231.png" width="280"> |
| <img src="https://storage.googleapis.com/zenn-user-upload/8fc7a749268d-20251231.png" width="300"> | <img src="https://storage.googleapis.com/zenn-user-upload/4c153e5d64d4-20251231.png" width="280"> |


## ✨ 特徴

- 📸 **カメラ撮影 / 写真アップロード** - お好きな方法で
- 🤖 **AI分析** - 目の形状を自動判定し、最適なスタイルを提案
- 🎨 **リアルタイム調整** - 本数・カール・長さをその場で変更
- 👁️ **下まつげ対応** - ON/OFF切り替え可能
- 📍 **位置微調整** - ピッタリの位置に合わせられる
- 💾 **パターン比較** - 複数パターンを保存して比較

## 🛠️ 技術スタック

| カテゴリ | 技術 |
|----------|------|
| Frontend | HTML / CSS / JavaScript |
| 顔検出 | MediaPipe Face Mesh |
| 描画 | Canvas API（ベジェ曲線） |
| AI分析 | Google Gemini 2.5 Flash |
| Backend | Python / FastAPI |
| Platform | Google Cloud Run |

## 📁 ファイル構成

```
alpaca-lash-salon/
├── main.py              # FastAPI エントリーポイント
├── api/
│   └── alpaca.py        # AI分析APIエンドポイント
├── static/
│   ├── alpaca_salon.html    # メインHTML
│   ├── background_actress.png
│   └── demo.png
├── requirements.txt
└── Dockerfile
```

## 🚀 セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/miki-mini/alpaca-lash-salon.git
cd alpaca-lash-salon
```

### 2. 依存関係をインストール

```bash
pip install -r requirements.txt
```

### 3. 環境変数を設定

```bash
export GEMINI_API_KEY="your-gemini-api-key"
```

### 4. 起動

```bash
uvicorn main:app --reload
```

ブラウザで http://localhost:8000 にアクセス

## 🔧 API

### POST /api/alpaca-salon/analyze-eye

目の画像を分析し、最適なまつエクスタイルを提案します。

**リクエスト:**
```json
{
  "image": "data:image/png;base64,..."
}
```

**レスポンス:**
```json
{
  "success": true,
  "analysis": {
    "eyeShape": "almond",
    "eyeSlant": "upturned",
    "eyelidType": "double",
    "eyeWidth": "medium",
    "recommendations": {
      "volume": 60,
      "curl": "C",
      "length": 1.0,
      "reasoning": "アーモンド型の目には、Cカールで自然な仕上がりがおすすめです。"
    }
  }
}
```

## 📱 対応環境

- ✅ PC（Chrome, Firefox, Safari, Edge）
- ✅ iPhone（Safari）
- ✅ Android（Chrome）

## 🎨 こだわりポイント

### 自然なまつげの表現

Canvas APIのベジェ曲線とグラデーションを使用し、本物のまつげのような質感を実現しました。

```javascript
// グラデーション（根元は濃く、毛先は薄く）
const gradient = ctx.createLinearGradient(0, 0, 0, -length);
gradient.addColorStop(0, 'rgba(20, 20, 20, 0.95)');
gradient.addColorStop(1, 'rgba(60, 60, 60, 0)');
```

### MediaPipe Face Mesh

468個のランドマークから目の輪郭を取得し、正確な位置にまつげを配置します。

## 📝 開発背景

サロンで働く中で、お客様から「つける前にどんな感じになるか見たい」という声を多くいただきました。

まつエクは数週間取れないので、「思ってたのと違う...」となるとお客様も悲しい。
そんな不安を解消するために、このアプリを作りました。

## 📄 ライセンス

MIT License

## 👩‍💻 Author

**miki-mini**

- GitHub: [@miki-mini](https://github.com/miki-mini)
- LAPRAS: [miki-mini](https://lapras.com/public/EUPKMNZ)

## 🛠 技術スタック

*   **Frontend**: HTML5, CSS3, Vanilla JavaScript
*   **Backend**: FastAPI (Python)
    *   `static/alpaca.html` を `routers/web_apps.py` で配信
*   **Design**:
    *   高級感のある「女優ミラー」デザイン
    *   Web Camera API (`navigator.mediaDevices.getUserMedia`)
    *   Canvas API (画像合成・保存)

## 📖 使い方

1.  [ポータルサイト](https://usagi-oekaki-service-1032484155743.asia-northeast1.run.app/) にアクセスします。
2.  「Alpaca」のカードをタップします。
3.  カメラの利用を許可してください。
4.  画面上のまつげを指で動かして、目の位置に合わせます。
5.  下のボタンで本数やカールを切り替えて、似合うデザインを探してみてください！
