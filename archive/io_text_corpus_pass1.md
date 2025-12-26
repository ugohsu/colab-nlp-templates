# 大規模テキスト処理（1パス目）：ファイル走査 → 形態素解析 → tokens.jsonl（再開可能）

本ドキュメントでは、フォルダ内（サブディレクトリ含む）の大量のテキストファイルを対象に、
次を **1パス目**として実行する方法を説明します。

- `Path(root).rglob()` で再帰走査して **対象ファイル台帳（manifest）** を作成  
- `pending / failed` のファイルだけ処理して **tokens.jsonl** に追記  
- 途中で Colab が落ちても **台帳から再開**できる（再実行で `done` はスキップ）

> この 1パス目は、後続で **語頻度・Nグラム・CountVectorizer・トピックモデル**などに進むための「土台」です。

---

## 生成されるもの（最小）

### 1) manifest（CSV）
- **再開（resume）** のための台帳です。
- 各ファイルの状態（`pending / done / failed`）を持ちます。

例：`/content/manifest.csv`

主な列（例）：
- `doc_id`：連番ID
- `path`：root からの相対パス
- `status`：`pending` / `done` / `failed`
- `error`：失敗時の例外メッセージ（文字列）
- `n_chars`, `n_tokens`, `preview`：処理結果のメタ（軽量）

### 2) tokens.jsonl（成果物）
- **1行 = 1文書** の JSON Lines 形式です（改行区切り）。
- 形態素解析結果を **トークン配列**として保存します。

例：`/content/tokens.jsonl`

```json
{"doc_id": 12, "path": "news/2023/a.txt", "tokens": ["株価", "上昇", "する", "..."]}
```

> JSONL は **1行ずつ読み込める**ので、巨大データでも扱いやすい形式です。

---

## 前提

- 本リポジトリを clone して `libs` を import できる状態であること
- 形態素解析の基本は [`tokenization.md`](./tokenization.md) を参照してください

本 1パス目では、**DataFrame を使わず**
「1テキスト → トークン列」を返す関数を内部的に利用します。
これにより、大規模データでも安定して処理できます。

---

## 最小テスト

以下は「**最小で動くことの確認**」用です。
（SudachiPy を使う例。Janome に切り替える場合は後述）

```python
# --- 0) 依存ライブラリ + リポジトリ ---
!pip -q install sudachipy sudachidict_core
!git clone https://github.com/ugohsu/colab-nlp-templates.git

import sys
sys.path.append("/content/colab-nlp-templates")

# --- 1) 1パス目の関数を import ---
from libs.corpus_pass1 import process_manifest_to_jsonl

# --- 2) 入力フォルダ（★要編集） ---
ROOT_DIR = "/content/texts"

# --- 3) 出力（manifest + jsonl） ---
MANIFEST_CSV = "/content/manifest.csv"
TOKENS_JSONL = "/content/tokens.jsonl"

# --- 4) 実行（pending/failed のみ処理し、jsonl に追記） ---
df_manifest = process_manifest_to_jsonl(
    root_dir=ROOT_DIR,
    manifest_csv=MANIFEST_CSV,
    jsonl_path=TOKENS_JSONL,
    ext=".txt",
    save_every=1,
)

df_manifest.head()
```

> 🔎 既定では **SudachiPy（高速・大規模向け）** が使われます。
> tokenizer は内部で 1 度だけ初期化され、全ファイルで使い回されます。

---

## Janome に切り替える場合（最小）

Janome を使う場合は、
**1テキスト用の関数**を `tokenize_text_fn` として明示的に渡します。

```python
!pip -q install janome
!git clone https://github.com/ugohsu/colab-nlp-templates.git

import sys
sys.path.append("/content/colab-nlp-templates")

from libs import tokenize_text_janome
from libs.corpus_pass1 import process_manifest_to_jsonl

df_manifest = process_manifest_to_jsonl(
    root_dir="/content/texts",
    manifest_csv="/content/manifest.csv",
    jsonl_path="/content/tokens.jsonl",
    tokenize_text_fn=tokenize_text_janome,
    ext=".txt",
    save_every=1,
)
```

---

## 再開（resume）のしかた

- Colab が落ちた / 途中で止めた場合でも、同じ呼び出しをもう一度実行すればOKです。
- `manifest.csv` の `status` が
  - `done` のものはスキップ
  - `pending` / `failed` のものだけ再処理
になります。

> **再開の鍵は `manifest.csv` です。削除しないでください。**

---

## よくある失敗と対処

### 1) 文字コード問題で失敗する
- 既定は `encoding="utf-8"` / `errors="replace"` です。
- 文字化けが気になる場合は、`encoding` を変更してください。

### 2) failed が残る
- `manifest.csv` の `error` 列を確認してください。
- 修正後、同じ関数を再実行すれば `failed` だけ再挑戦されます。

---

## 設計メモ（なぜこの形か）

- ファイル内容をすべてメモリに載せない
- 処理状況を台帳で管理する
- 失敗ファイルだけ再実行できる
- JSONL を後段処理にそのまま流せる

という **大規模テキスト処理の基本原則**を満たすためです。

---

## 関連ドキュメント（相互参照）

- 形態素解析（Janome / SudachiPy）：[`tokenization.md`](./tokenization.md)
