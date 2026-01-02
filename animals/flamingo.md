# 🦩 姿勢のフラミンゴ先生 (Flamingo Sensei)

**「あなたの姿勢、美しく保てていますか？」**

カメラだけであなたの姿勢をチェックし、改善のためのアドバイスやゲームを提供するAIトレーナーです。

<img src="images/flamingo.jpg" width="400">

## ✨ 主な機能

### 1. 📐 リアルタイム姿勢チェック（正面）
カメラに映るだけで、**首・肩・腰・膝**の位置をAIが解析。傾きを検知するとアニメーションで警告します。

### 2. 📏 側面チェックモード
横を向くだけで、理想の重心ライン（足首からの垂直線）とのズレを診断。
- ストレートネック判定
- 猫背・巻き肩判定
- 反り腰判定

| ツボマップ | 側面チェック |
|:--------:|:--------:|
| <img src="https://storage.googleapis.com/zenn-user-upload/9cf7a17b5835-20260101.png" width="300"> | <img src="https://storage.googleapis.com/zenn-user-upload/df7a55b770a9-20260101.png" width="300"> |

### 3. 🔴 ツボ（経穴）マップ
画面上の自分の体にそのまま「ツボ」が表示されます。タップすると効能が見れます。

| ツボ名 | 効果 |
|--------|------|
| 肩井（けんせい） | 肩こり、頭痛 |
| 合谷（ごうこく） | 万能な手のツボ |
| 足三里（あしさんり） | 胃腸、むくみ |
| 三陰交（さんいんこう） | 冷え性改善 |

<img src="https://storage.googleapis.com/zenn-user-upload/199de3524efd-20260101.png" width="200">

### 4. 🦵 フラミンゴ片足チャレンジ
「片足立ち、何秒できるかな？」

バランス感覚を鍛えるゲーム機能。片足を上げると自動でカウントダウンが始まり、記録を測定。過去最高記録も保存されます。

<img src="https://storage.googleapis.com/zenn-user-upload/2b3f9386ecb3-20260101.png" width="200">

### 5. 🔰 かんたんモード（NEW!）
片足チャレンジの判定を甘くした初心者向けモード。
- **Normal**: 足首の高さの差が8%以上で判定
- **Easy**: 足首の高さの差が4%以上でOK

ハイスコアは難易度別に保存されます。

### 6. 📸 写真撮影機能（NEW!）
ワンタップで計測結果入りの画面を保存できます。
- カメラ映像とオーバーレイを合成
- タイムスタンプ付きファイル名
- フラッシュエフェクト付き

### 7. ⏱️ タイマー撮影
5秒後に画面を静止して、じっくり姿勢を確認できます。

## 🔒 プライバシー安全

このアプリは **クライアントサイドAI（エッジAI）** を使用しています。

| 項目 | 説明 |
|------|------|
| 映像の送信 | ❌ サーバーに送信しない |
| 処理場所 | ✅ すべてブラウザ内で完結 |
| 料金 | ✅ 完全無料 |

撮影された**カメラ映像が外部サーバーに送信されることは一切ありません**。

## 🛠 技術スタック

| カテゴリ | 技術 |
|----------|------|
| 姿勢検出 | MediaPipe Pose |
| Frontend | HTML / CSS / JavaScript / Canvas |
| Backend | Python / FastAPI |
| Platform | Google Cloud Run |

## 📁 ファイル構成

```
flamingo-sensei/
├── main.py              # FastAPI エントリーポイント
├── static/
│   ├── flamingo.html    # メインHTML
│   └── images/
│       └── flamingo.jpg
├── requirements.txt
└── Dockerfile
```

## 🚀 セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/miki-mini/flamingo-sensei.git
cd flamingo-sensei
```

### 2. 依存関係をインストール

```bash
pip install -r requirements.txt
```

### 3. 起動

```bash
uvicorn main:app --reload
```

ブラウザで http://localhost:8000/flamingo にアクセス

## 📱 対応環境

- ✅ PC（Chrome, Firefox, Safari, Edge）
- ✅ iPhone（Safari）
- ✅ Android（Chrome）

※ カメラへのアクセス許可が必要です

## 🎮 使い方

### 正面チェック
1. カメラに全身または上半身を映す
2. 肩・腰・膝の傾きが自動で検出される
3. ピンクの●（ツボ）をタップすると効能が見れる

### 側面チェック
1. 「側面チェック」ボタンをタップ
2. 横を向いて全身を映す
3. 緑の理想ラインとのズレが表示される

### 片足チャレンジ
1. 「🦵 片足挑戦」ボタンをタップ
2. 片足を上げるとカウントダウン開始
3. そのままキープ！足を下ろすと終了
4. 過去最高記録に挑戦！

## 🔧 MediaPipe Pose ランドマーク

```
0: 鼻
7, 8: 左右の耳
11, 12: 左右の肩
13, 14: 左右の肘
15, 16: 左右の手首
23, 24: 左右の腰
25, 26: 左右の膝
27, 28: 左右の足首
```

## 📄 ライセンス

MIT License

## 👩‍💻 Author

**miki-mini**

- GitHub: [@miki-mini](https://github.com/miki-mini)
- LAPRAS: [miki-mini](https://lapras.com/public/EUPKMNZ)

---

## 🛠 技術スタック
*   **MediaPipe Pose**: 高精度な姿勢推定AI
*   **HTML5 / Canvas**: リアルタイム描画
*   **FastAPI**: 配信サーバー

## 🔗 リンク
*   [Webアプリを開く](https://usagi-oekaki-service-1032484155743.asia-northeast1.run.app/flamingo)
