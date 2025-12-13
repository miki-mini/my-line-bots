🦡 もぐら駅長の時刻表BOT (Mole Station Master Bot)

# 🦡 もぐら駅長の時刻表BOT (Mole Station Master Bot)

| 一般的な乗換アプリ | もぐら駅長 |
| :--- | :--- |
| アプリ起動→入力→検索 | **LINEで一言「新宿」と送るだけ！** |
| 現在地周辺を地図で確認 | **位置情報を送れば最寄り駅を即答！** |

「次の電車、何時だっけ？」を瞬時に解決。地下に詳しい「もぐら駅長」が、あなたの代わりにリアルタイムな時刻表を案内してくれるLINE BOTです。
曖昧な入力でもGeminiが駅名を推測し、ODPT（公共交通オープンデータ）APIを通じて正確な発車時刻をお知らせします。

## 📎 🚀 主な機能

1. **AI駅名検索アシスタント 🧠**
   - 「吉祥寺駅の時間を教えて」や「新宿！」と雑に送っても、Geminiが文脈から駅名だけを抽出。
   - 正確な駅名を入力しなくても、AIが意図を汲み取って検索します。
2. **現在地から最寄り駅検索 📍**
   - LINEの「位置情報」ボタンから現在地を送るだけで、Google Maps APIを使って一番近い駅を特定。
   - 「ここどこ？」と思った時でも、すぐに最寄りの電車時間を調べられます。
3. **リアルタイム時刻表取得 🕒**
   - ODPT（公共交通オープンデータセンター）の公式APIと連携。
   - 平日・土曜・休日のダイヤを自動判定し、現在時刻以降の直近5本の電車をリストアップします。

## 🖼️ 実際の動作イメージ

| 駅名検索 | 位置情報検索 |
| :--- | :--- |
| **User:** 吉祥寺の電車！<br><br>**もぐら:**<br>🦡 【吉祥寺 (JR-East)】の時刻表だモグ！<br>🕒 14:05 → 東京<br>🕒 14:08 → 千葉<br>... | **User:** (位置情報を送信)<br><br>**もぐら:**<br>🦡 最寄りは「新宿駅」だモグ！<br><br>駅名を送ってくれたら時刻表を見せるモグ！ |

## 🛠️ 技術スタック (Tech Stack)

- **Language:** Python 3.10+
- **Framework:** FastAPI
- **AI Model:** Google Gemini (Text extraction)
- **Data Source:** ODPT API (Association for Open Data of Public Transportation)
- **Location Service:** Google Maps API (Places Nearby)
- **Interface:** LINE Messaging API

## 🏗️ アーキテクチャ (Architecture)

```mermaid
graph TD
    User((User)) -->|Text / Location| LINE[LINE Messaging API]
    LINE -->|Webhook| CloudRun[Google Cloud Run]
    CloudRun -->|Extract Station| Gemini[Google Gemini API]
    CloudRun -->|Reverse Geocoding| GMaps[Google Maps API]
    CloudRun -->|Get Timetable| ODPT[ODPT API]
    CloudRun -->|時刻表| LINE
    LINE -->|Reply| User

```
---
Developed by miki-mini