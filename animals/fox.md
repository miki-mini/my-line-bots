# 🦊 キツネくんの動画要約BOT (Fox YouTube Bot)

YouTubeの動画URLを送るだけで、AIが内容を瞬時に要約し、さらにGoogle検索で補足情報を教えてくれるLINE BOTです。
単なる要約ではなく、Google検索と連携することで「動画外の最新情報」や「世間の反応（コメント数など）」も統合した、多角的な解説を提供します。
<img src="images/fox.png" width="100">


## 🚀 主な機能

1. **インテリジェント動画要約**
    * 動画の字幕データを解析し、重要なポイントを抽出。忙しい時でも「3行でわかる」レベルから「詳細な解説」まで対応します。
    * Gemini APIの高度な文脈理解により、専門用語も噛み砕いて解説。
2. **ハイブリッド検索システム**
    * **YouTube × Google検索**: 動画内の情報だけでなく、関連するキーワードを自動でGoogle検索。動画内では語られていない背景知識や最新ニュースを補足します。
3. **メタデータ自動取得**
    * 動画タイトル、チャンネル名に加え、Google検索結果から**「視聴回数」や「コメント数」**などの反響データを独自ロジックで取得。
4. **ペルソナ「キツネ先生」**
    * 「〜だコン！」という親しみやすい語尾のキャラクター設定により、無機質なAIではなく、頼れるパートナーとしてのUXを実現。
    * 動画の長さに応じて、48秒の動画なら「サクッと」、20分の動画なら「ガッツリ」と解説の長さを自動調整します。

## 🛠 技術スタック (Tech Stack)

モダンなサーバーレスアーキテクチャを採用し、スケーラビリティと運用コストの最適化を図っています。

* **Language**: Python 3.10+
* **Framework**: FastAPI
* **Infrastructure**: Google Cloud Run (Serverless)
* **AI Model**: Google Gemini 1.5 Flash (高速・長文対応)
* **Interface**: LINE Messaging API
* **Search Engine**: Google Custom Search API / Scraping logic
* **Library**: youtube-transcript-api, beautifulsoup4, etc.

## 🏗 アーキテクチャ (データの流れ)

1. **User**: LINEでYouTubeのURLを送信
2. **LINE API**: WebhookでCloud Runへ通知
3. **Python (FastAPI)**:
    * YouTubeから字幕・メタデータを取得
    * Google検索で補足情報を収集
4. **Gemini AI**: すべての情報を統合して要約を作成
5. **LINE API**: ユーザーに返信

## 💡 こだわったポイント

* **情報の網羅性と精度の両立**:
    * 字幕がない動画や情報が古い動画でも、Google検索機能を併用することで、ユーザーに「今」役立つ情報を提供できるようにしました。
* **トークン制限の克服**:
    * 長時間の動画でも要約が途切れないよう、Geminiの出力トークン設計を最適化（Max 8192 token）し、最後までしっかり解説しきるチューニングを行っています。
* **セキュリティ**:
    * APIキーなどの機密情報は環境変数（Environment Variables）で厳重に管理し、コード上には一切ハードコーディングしていません。
* **UX（ユーザー体験）の向上**:
    * 動画のタイトル、視聴回数、コメント数などのメタ情報をヘッダーとして固定表示し、ひと目で動画の概要が分かる視認性の高いレイアウトを採用しました。

## 📸 スクリーンショット

| 要約画面・短いver. | 要約画面・長いver.  |
|:---:|:---:|
| <img src="https://github.com/user-attachments/assets/3391ffbb-3f4d-4168-b447-71d79dea83b6" width="300"> | <img src="https://github.com/user-attachments/assets/671dfef0-3788-4d7c-9228-de5668f13321" width="300"> <img src="https://github.com/user-attachments/assets/a9686cb3-2e32-40c0-bb57-e7dc378fddb2" width="300">|


---
Developed by miki-mini