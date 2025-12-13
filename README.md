## 🏢 main.py の役割

`main.py` は**管理人室**のような存在です。
各動物のコードは `animals/` フォルダに分離されており、main.py はそれらを起動時に読み込んで登録します。

```
my-line-bots/
├── main.py              # 🏢 管理人室（エントリーポイント）
├── animals/             # 🐾 動物たちの部屋
│   ├── fox.py           # 🦊
│   ├── frog.py          # 🐸
│   ├── penguin.py       # 🐧
│   ├── beaver.py        # 🦫
│   ├── capybara.py      # 🐹
│   ├── owl.py           # 🦉
│   ├── voidoll.py       # 🤖
│   ├── mole.py          # 🦡
│   └── whale.py         # 🐋
├── gas/                 # 🚀 GASファイル
├── images/              # 🖼 画像素材
└── .env                 # 🔐 環境変数（非公開）
```

### なぜ分割したのか？

最初は全員 main.py に住んでいましたが、**1500行を超えて**カオスになりました。

- カピバラを直すとペンギンが消える 🐧💨
- キツネのバグを直すとビーバーが爆発 🦫💥

詳しくはこちら 👉 [【個人開発】巨大化したmain.pyでビーバーが爆発するからモジュール分割した話]*Coming Soon...*

---

## 🛠 全体で使用している技術

| カテゴリ | 技術 |
| --- | --- |
| **言語** | Python 3.10+ |
| **AI** | Google Gemini 2.5 Pro / Flash |
| **検索** | Google GenAI SDK (Grounding with Google Search) |
| **DB** | Google Cloud Firestore |
| **基盤** | Google Cloud Run / FastAPI |
| **PF** | LINE Messaging API |
| **定期実行** | Google Apps Script (GAS) |

---


# [ 🤖 My LINE Bots Collection (どうぶつAIボット集一覧へ)](https://github.com/miki-mini/my-line-bots/tree/main/animals)


---
Creator: miki-mini