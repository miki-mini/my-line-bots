# レッサーパンダ (Lesser Panda) モジュール

> **きのたけ聖戦 〜改行バトルの審判〜**
> たけのこ派 vs きのこ派の票を競わせるコミュニティ投票ゲーム。
> 隠しコマンドを入れると特別なモードが発動する。

---

## アーキテクチャ概要

```
  GCS (rabbit-bot-images)
  gs://rabbit-bot-images/kinotake/*
  (画像・音声ファイル / git非管理)
          │
          │ gcloud storage cp (CI/CDのみ)
          ▼
  GitHub Actions (deploy job)
  ─────────────────────────────
  git checkout + GCS assets DL
          │
          │ docker build & push
          ▼
┌──────────────────────────────────────────┐
│          Cloud Run コンテナ               │
│                                          │
│  FastAPI (uvicorn)                       │
│                                          │
│  GET  /kinotake        → index.html      │
│  GET  /api/kinotake/state                │
│  POST /api/kinotake/vote                 │
│                                          │
│  routers/lesser_panda.py                 │
│   ├─ StateCache (1秒 TTL)                │
│   ├─ SHA256 チートコード検証              │
│   └─ Firestore 読み書き                  │
│                                         │
│  /static/kinotake/ (コンテナ内に展開)     │
│   ├─ *.html / *.js / *.css  (git管理)    │
│   └─ *.png / *.jpg / *.mp3  (GCS由来)    │
└──────────────┬───────────────────────────┘
               │  Google Cloud SDK
               ▼
       Firestore (NoSQL)
       games / kinotake ドキュメント
       ├─ bamboo / mushroom / prettier (票数)
       ├─ cultprits[]  (行動ログ)
       └─ discovered_cheats[]  (発見済みモード)
```

> **ポイント:** 画像・音声は git に含まれず GCS に保管。デプロイ時に
> `gcloud storage cp gs://rabbit-bot-images/kinotake/*` でフラットに取得し
> コンテナに焼き込む。サブディレクトリは取得されないため **ファイルはすべて
> `kinotake/` 直下** に置くこと。

---

## ファイル構成

```
routers/
└── lesser_panda.py          # FastAPI ルーター (バックエンド)

static/kinotake/             # git管理ファイルのみ記載
├── index.html               # ゲーム HTML
├── kinotake.js              # ゲームロジック (~2500行)
├── kinotake.css             # スタイル
└── coord-checker.html       # 証明書座標チェック用 (開発ツール)

# 以下は .gitignore 対象 / GCS (rabbit-bot-images) で管理
# static/kinotake/*.png  *.jpg  *.mp3
# → デプロイ時に CI/CD が GCS からダウンロード
```

---

## バックエンド (`routers/lesser_panda.py`)

### エンドポイント

| メソッド | パス | 説明 |
|--------|------|------|
| `GET` | `/kinotake` | ゲームページ (HTML) を返す |
| `GET` | `/api/kinotake/state` | 現在のスコア・ログを取得 |
| `POST` | `/api/kinotake/vote` | 投票 / チートコード送信 |

### `/api/kinotake/state` レスポンス

```json
{
  "bamboo":   1234,
  "mushroom": 5678,
  "prettier": 42,
  "culprits": ["12:34:56 - とある名人 が 隠しコマンド を発動！", "..."],
  "discovered_count": 3,
  "total_cheats": 8
}
```

> ⚠️ `culprits` はレスポンスのキー名。Firestore 上のフィールド名は `cultprits`（実装上の typo）なので注意。

### `/api/kinotake/vote` リクエスト

```json
{
  "team":        "bamboo | mushroom | prettier",
  "count":       1,
  "cheat_code":  "チートコード文字列 (省略可)",
  "helper_name": "表示名 (省略可)"
}
```

### Firestore スキーマ

コレクション: `games` / ドキュメント: `kinotake`

```
{
  bamboo:            number,   // たけのこ票数
  mushroom:          number,   // きのこ票数
  prettier:          number,   // Prettier票数
  cultprits:         string[], // 行動ログ (最新20件を返す) ※フィールド名はtypo
  discovered_cheats: string[]  // 発見済みモード名 (ArrayUnion で重複なし)
}
```

### StateCache

Firestore への読み込みを抑制するため、1秒間のインメモリキャッシュを持つ。

```python
class StateCache:
    TTL = 1.0  # 秒
    # TTL 内はキャッシュを返す / 期限切れで Firestore から再取得
```

### チートコード検証 (SHA256)

コード本体をソースに書かず、SHA256ハッシュで比較する。

```python
CHEAT_HASHES = {
    "<sha256_hash>": "VIM_DUNGEON_MODE",
    "<sha256_hash>": "OTOKO_FESTIVAL_MODE",
    "<sha256_hash>": "KAGYOHA_MODE",
    "<sha256_hash>": "TEIOU_MODE",
    "<sha256_hash>": "TIME_SLIP_MODE",
    "<sha256_hash>": "NOT_FOUND_MODE",
}

h = hashlib.sha256(request.cheat_code.encode()).hexdigest()
if h in CHEAT_HASHES:
    mode_msg = CHEAT_HASHES[h]
    # discovered_cheats に ArrayUnion で追記
    return {"success": True, "message": mode_msg}
```

---

## フロントエンド (`kinotake.js`)

### 主要な処理フロー

```


投票系
├── sendVote(team, count, cheatCode, helperName)
│   └── POST /api/kinotake/vote → updateUI() / updateLogsOnly()
├── updateUI(data)            スコアバー・ログ・発見カウント更新
└── updateLogsOnly(data)      ログ・発見カウントのみ更新 (通常投票時)



VIM ダンジョン
├── vimAction(action)         たたかう / にげる / 手動改行を極める
├── startQTE()                QTE (Quick Time Event) 開始
├── handleQteInput(key)       キー入力を検証・進捗更新
├── updateQteDisplay()        QTE UI 更新
├── winQTE()                  QTE クリア → shatter 演出 → 証明書
└── failQTE()                 タイムアウト → 迷宮リセット

証明書生成 (Canvas API)
├── showCertificateEntry(mode)  名前入力モーダル表示
├── generateCertificate()       モードに応じた証明書画像を選択
├── showPositioningUI()         ドラッグで名前位置を決める UI
├── finalizeCertificate()       Canvas に描画・白+シアン グロー文字
├── downloadCertificate()       JPG として保存
└── shareOnX()                  X (Twitter) で共有
```



---

## デプロイフロー

```
git push main
      │
      ▼
GitHub Actions (ci.yml)
      │
      ├─ [test job] pytest
      │
      └─ [deploy job] (main ブランチのみ)
            │
            ├─ 1. Workload Identity Federation で GCP 認証
            │       (キーファイル不要・OIDC トークン方式)
            │
            ├─ 2. GCS から画像・音声を取得
            │       gcloud storage cp \
            │         "gs://rabbit-bot-images/kinotake/*" \
            │         static/kinotake/
            │       ※ フラットコピー。サブディレクトリは取得不可
            │
            └─ 3. Cloud Run へソースデプロイ
                    (Dockerfile ビルド → asia-northeast1)
```

**ファイル管理の分担:**

| 種別 | 管理場所 | 理由 |
|------|----------|------|
| `*.html / *.js / *.css` | git | コードレビュー・差分管理 |
| `*.png / *.jpg / *.mp3` | GCS | バイナリ・容量・非公開アセット |

---

## ローカル開発

```bash
# サーバー起動
uvicorn main:app --reload

# ブラウザで確認
open http://localhost:8000/kinotake

# JS/CSS を変更したらバージョン番号を上げてキャッシュを回避
# index.html: kinotake.js?v=131  /  kinotake.css?v=28
```

---

## Firestore アクセス制御

- サービスアカウントには `roles/datastore.user` のみ付与 (最小権限)
- 本番環境では Workload Identity Federation によりキーファイル不要
- ローカルでは `GOOGLE_APPLICATION_CREDENTIALS` 環境変数でキーを指定

---

## 関連ファイル

| ファイル | 役割 |
|--------|------|
| `main.py` | FastAPI エントリポイント。`lesser_panda.py` ルーターをインクルード |
| `terraform/cloud_run.tf` | Cloud Run サービス定義 |
| `.github/workflows/ci.yml` | CI/CD パイプライン |
| `.gitignore` | 画像・音声・kakusi/ を除外 |

---
*Created by miki-mini with Gemini & Claude.*