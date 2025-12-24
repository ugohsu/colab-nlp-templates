# Colab NLP Templates

このリポジトリは、**Google Colaboratory 上で自然言語処理（NLP）を学ぶための  
テンプレート・関数・解説ドキュメント**をまとめた教材用リポジトリです。

---

## 基本方針

### templates（貼り付けて使う）

- Google Colab の **コードセルにそのまま貼り付けて実行**
- import はしない
- 認証・初期設定・定型処理向け

### libs（import して使う）

- リポジトリを clone した後、**import して使用**
- ゼミ内で共通利用する前処理・可視化・I/O 関数群

### docs（解説）

- 各テンプレ・関数の **背景・理由・注意点**
- README を補完する解説書相当

---

## テンプレート一覧（貼り付けて使う）

| 内容 | テンプレート | 解説ドキュメント |
|---|---|---|
| Google スプレッドシート読み込み | [`templates/load_google_spreadsheet.py`](./templates/load_google_spreadsheet.py) | [`docs/load_google_spreadsheet.md`](./docs/load_google_spreadsheet.md) |
| matplotlib 日本語表示設定 | [`templates/matplotlib_japanese_font.py`](./templates/matplotlib_japanese_font.py) | [`docs/matplotlib_japanese_font.md`](./docs/matplotlib_japanese_font.md) |

---

## 関数群（import して使う）

| 分類 | 内容 | 実装ファイル | 解説ドキュメント |
|---|---|---|---|
| 前処理 | 形態素解析（Janome / SudachiPy） | [`libs/preprocess.py`](./libs/preprocess.py) | [`docs/tokenization.md`](./docs/tokenization.md) |
| BoW / 可視化 | 語頻度・WordCloud | [`libs/bow.py`](./libs/bow.py) | [`docs/bow/README.md`](./docs/bow/README.md) |
| I/O | Google Sheets 書き込み | [`libs/gsheet_io.py`](./libs/gsheet_io.py) | [`docs/write_google_spreadsheet.md`](./docs/write_google_spreadsheet.md) |

---

## 関数群（libs）の基本的な使い方

```python
!git clone https://github.com/ugohsu/colab-nlp-templates.git

import sys
sys.path.append("/content/colab-nlp-templates")

from libs import (
    tokenize_janome,
    tokenize_sudachi,
    tokens_to_text,
    create_wordcloud,
    write_df_to_gsheet,
)
```

※ 各関数に必要な外部ライブラリの install 方法や  
　事前に実行すべきテンプレートについては、  
　**対応する docs を必ず参照してください。**

---

## このリポジトリで学ぶ NLP の全体像

本リポジトリでは、日本語テキスト分析を次の流れで段階的に学びます。

### 1. テキストデータの準備

- Google スプレッドシートからの読み込み  
  → [`docs/load_google_spreadsheet.md`](./docs/load_google_spreadsheet.md)
- ローカル / Drive 上のテキストファイル読み込み  
  → [`docs/io_text_basic.md`](./docs/io_text_basic.md)

---

### 2. 前処理（形態素解析）

- 文書を「語」に分解し、分析可能な形に整える  
- Janome / SudachiPy を用途に応じて使い分ける  

→ [`docs/tokenization.md`](./docs/tokenization.md)

---

### 3. Bag of Words（BoW）

- 文書を「語の集合」として表現する最も基本的な考え方
- 語頻度・WordCloud などの可視化を通じて直感的に理解する  

→ **BoW 総論**  
　[`docs/bow/README.md`](./docs/bow/README.md)

→ **語頻度の計算（pandas / sklearn）**  
　[`docs/bow/term_frequency.md`](./docs/bow/term_frequency.md)

→ **WordCloud**  
　[`docs/bow/wordcloud.md`](./docs/bow/wordcloud.md)

---

## ライセンス・利用について

- 教育・研究目的での利用を想定しています
- 講義資料・演習ノートへの組み込みも自由です