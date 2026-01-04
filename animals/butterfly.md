# 🦋 美の蝶々パーソナル (Butterfly)

**「あなたに似合う色とカタチを。」**

AI（Gemini 2.5 Flash）を活用した、パーソナルカラー診断 & 顔タイプ診断アプリです。

<img src="images/butterfly.png" width="300">

## ✨ 主な機能

### 1. 🎨 パーソナルカラー診断
カメラで撮影した顔写真をAIが分析し、あなたに似合う「シーズンカラー」を診断します。

| シーズン | ベース | 特徴 |
|----------|--------|------|
| 🌸 Spring | Yellow Base | 明るく鮮やかな暖色 |
| 🌊 Summer | Blue Base | 柔らかく涼しげな色 |
| 🍂 Autumn | Yellow Base | 深みのある暖色 |
| ❄️ Winter | Blue Base | コントラストの強い色 |

### 2. 👤 顔タイプ診断
顔の輪郭やパーツの配置から、顔のタイプを分析します。

- 丸顔 / 面長 / ベース型 / 逆三角 / 卵型
- あなたの顔型に最もマッチするヘアスタイルを提案

### 3. ⚪ ホワイトバランス補正
白い紙を映してクリックするだけで、照明の色味を補正し、正確な診断を実現します。

### 4. 💡 照明モード
環境に合わせて照明モードを選択できます。

- ☀️ Sun（太陽光）
- 🏢 Office（蛍光灯）
- 💡 Bulb（電球色）

## ⚠️ 骨格診断について

以前搭載されていた「骨格診断機能」は、**「姿勢のフラミンゴ先生」** アプリへ移動しました。

**理由：** 顔分析（インカメラ・接写）と骨格分析（全身・離れて撮影）では、カメラの使い方が大きく異なるため、機能を分離しました。

## 🛠 技術スタック

| カテゴリ | 技術 |
|----------|------|
| Frontend | HTML / CSS / JavaScript |
| カメラ | MediaPipe Camera Utils |
| 画像処理 | Canvas API |
| AI分析 | Google Gemini 2.5 Flash |
| Backend | Python / FastAPI |
| Platform | Google Cloud Run |

## 📁 ファイル構成

```
butterfly/
├── main.py              # FastAPI エントリーポイント
├── api/
│   └── butterfly.py     # 診断APIエンドポイント
├── static/
│   ├── butterfly.html   # メインHTML
│   └── images/
├── requirements.txt
└── Dockerfile
```

## 🚀 セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/miki-mini/butterfly.git
cd butterfly
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

ブラウザで http://localhost:8000/butterfly にアクセス

## 📱 対応環境

- ✅ PC（Chrome, Firefox, Safari, Edge）
- ✅ iPhone（Safari）
- ✅ Android（Chrome）

※ カメラへのアクセス許可が必要です

## 🎮 使い方

### パーソナルカラー診断

1. 顔をカメラに映す
2. 照明モードを選択（☀️ Sun / 🏢 Office / 💡 Bulb）
3. （オプション）ホワイトバランス補正
   - 「📝 WB Pick」をタップ
   - 白い紙を画面に映してクリック
4. 「✨ Analyze」ボタンをタップ
5. 結果を確認！

## 🔧 API

### POST /api/butterfly/diagnose

顔画像を分析し、パーソナルカラーと顔タイプを診断します。

<img src="https://storage.googleapis.com/zenn-user-upload/da7e54ccfe82-20260103.png" width="300">

**リクエスト:**
```json
{
  "image": "data:image/png;base64,...",
  "mode": "color",
  "lighting": "sun"
}
```

**レスポンス:**
```json
{
  "success": true,
  "result": {
    "personalColor": {
      "season": "Spring",
      "base": "Yellow Base",
      "characteristics": "明るく鮮やかな色が似合います",
      "bestColors": ["Coral", "Peach", "Ivory", "Warm Pink", "Golden Yellow"],
      "lightingCorrectionNote": "自然光での撮影のため、色味は正確です"
    },
    "faceType": {
      "shape": "卵型",
      "description": "理想的なバランスの顔型です",
      "bestHairstyles": ["ロングヘア", "ボブ", "ショートボブ"]
    },
    "skeletonType": null
  }
}
```

## 🎨 ホワイトバランス補正の仕組み

```javascript
// 白い紙をクリックした時のRGB値を取得
const pixel = ctx.getImageData(x, y, 1, 1).data;
const r = pixel[0], g = pixel[1], b = pixel[2];

// 補正係数を計算（白=255に近づける）
wbCorrection = {
    r: 255 / r,  // 例: R=200 → 1.275
    g: 255 / g,  // 例: G=180 → 1.417
    b: 255 / b   // 例: B=220 → 1.159
};

// 画像全体に補正を適用
for (let i = 0; i < data.length; i += 4) {
    data[i] = Math.min(255, data[i] * wbCorrection.r);
    data[i + 1] = Math.min(255, data[i + 1] * wbCorrection.g);
    data[i + 2] = Math.min(255, data[i + 2] * wbCorrection.b);
}
```

## 📄 ライセンス

MIT License

## 👩‍💻 Author

**miki-mini**

- GitHub: [@miki-mini](https://github.com/miki-mini)
- LAPRAS: [miki-mini](https://lapras.com/public/EUPKMNZ)