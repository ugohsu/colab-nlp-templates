# Colab NLP Templates

このリポジトリは、**Google Colaboratory 上で自然言語処理（NLP）を学ぶための  
テンプレート・関数・解説ドキュメント**をまとめた教材用リポジトリです。

ゼミ・演習での利用を主目的とし、

- **コードセルに貼り付けて使うテンプレート**
- **import して使う共通関数群**
- それらの背景・理由・注意点を説明する **ドキュメント**

を明確に分離して整理しています。

---

## このリポジトリで学ぶ NLP の全体像

本リポジトリは、**日本語 NLP 入門**として、  
次のような段階構成を想定しています。

### 1. テキストを「読む」

- Google スプレッドシートから読む  
- Google Drive 上のテキストファイルを読む  

👉 入力データを **Python / Colab で扱える形にする**段階

---

### 2. テキストを「単語」に分解する（前処理）

- 形態素解析（Janome / SudachiPy）
- 文書 ID を保ったままトークン化

👉 文章を **分析可能な最小単位（単語）**に分解

---

### 3. 単語の集まりとして文章を見る（Bag of Words）

- 語頻度
- WordCloud
- BoW に基づく基本的な可視化・集計

👉 **意味モデルに進む前の、最重要な基礎段階**

---

### 4. （今後追加予定）

- TF-IDF
- word2vec / doc2vec
- 文書埋め込み・類似度・クラスタリング など

👉 BoW の限界を理解したうえで、  
**より高度な表現へ進むための足場**

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
- README を補完する man / 解説書相当
- **コードを増やさず理解を補助するための資料**

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
| Bag of Words | 語頻度・WordCloud | [`libs/bow.py`](./libs/bow.py) | [`docs/bow/README.md`](./docs/bow/README.md) |
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

## 大規模テキストへの入口（テキスト I/O）

Google スプレッドシートに載らない規模の文書群を扱うための  
**最小構成のテキスト I/O** を以下で整理しています。

- Google Drive のマウント
- `with open` によるテキスト読み込み

👉 [`docs/io_text_basic.md`](./docs/io_text_basic.md)

---

## 想定ユースケース

- ゼミ・演習での日本語 NLP 入門
- スプレッドシート／テキストファイルを起点とした分析
- 形態素解析 → Bag of Words → 可視化
- Colab 完結型の再現可能な演習ノート作成

---

## ライセンス・利用について

- 教育・研究目的での利用を想定しています
- 講義資料・演習ノートへの組み込みも自由です
