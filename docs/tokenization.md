# 形態素解析を行う関数（Janome / SudachiPy）

本ドキュメントでは、Pandas DataFrame に格納された日本語テキストを対象として、  
**Janome** または **SudachiPy** を用いた形態素解析を行い、  
「**1行 = 1トークン**」の縦持ち DataFrame に変換する関数群について説明します。

これらの関数は **ライブラリ化**されており、  
Google Colaboratory 上では本リポジトリを clone したうえで **import して使用**します。

いずれも **文書ID列を必須**とする設計であり、  
LDA / NMF / TF-IDF / WordCloud / 語頻度集計などの分析処理に  
そのまま接続できることを重視しています。

---

## Google Colab での使い方（重要）

### 0. どちらを使うか決める

本リポジトリでは、以下の **2 種類の形態素解析関数**を提供しています。

- **Janome 版**：軽量・導入が簡単（授業・演習向け）
- **SudachiPy 版**：高精度・高機能（研究用途向け）

👉 **通常はどちらか一方だけを使えば十分です。**  
Janome と SudachiPy を **同時にインストールする必要はありません。**

---

### 1-A. Janome を使う場合（おすすめ：授業・演習）

```python
!pip install janome
```

```python
!git clone https://github.com/ugohsu/colab-nlp-templates.git

import sys
sys.path.append("/content/colab-nlp-templates")

from libs import tokenize_janome
```

---

### 1-B. SudachiPy を使う場合（研究用途・精度重視）

```python
!pip install sudachipy sudachidict_core
```

```python
!git clone https://github.com/ugohsu/colab-nlp-templates.git

import sys
sys.path.append("/content/colab-nlp-templates")

from libs import tokenize_sudachi
```

---

※ **Google Colab では、ライブラリのインストールは必ず `!pip install ...` の形式で実行してください。**  
※ `pip install ...`（!なし）は Colab では動作しません。

---

## 共通設計思想

- **文書ID列を必須とする**  
  文書単位の集計・分析を前提とするため、ID の有無による分岐は設けていません。
- **出力列構造を固定**  
  基本構成：`article_id`, `word`, `pos`（＋必要に応じて `token_info`）
- **Janome / Sudachi で列構造と思想を統一**  
  後続処理（BoW / TF-IDF / LDA など）を差し替え可能にするためです。
- **教育用途と研究用途の両立**  
  初学者にも説明しやすく、研究用途にもそのまま使える設計です。

---

## Janome バージョン

### 概要

`tokenize_janome` は、Pandas DataFrame に格納された日本語テキストを  
**Janome** で形態素解析し、「1行 = 1トークン」の縦持ち DataFrame に変換する関数です。

軽量で導入が簡単なため、**教育用途や小規模分析**に向いています。

### 使用例（Janome）

```python
tokens = tokenize_janome(df)

tokens = tokenize_janome(
    df,
    pos_keep={"名詞", "動詞", "形容詞"}
)

tokens = tokenize_janome(
    df,
    extra_col=None
)
```

---

## SudachiPy バージョン

### 概要

`tokenize_sudachi` は、Pandas DataFrame に格納された日本語テキストを  
**SudachiPy** で形態素解析し、「1行 = 1トークン」の縦持ち DataFrame に変換する関数です。

分割粒度（A / B / C）や正規化形を扱えるため、  
**中〜大規模データや研究用途**に向いています。

### 使用例（SudachiPy）

```python
from sudachipy import SplitMode

tokens = tokenize_sudachi(df)

tokens = tokenize_sudachi(
    df,
    split_mode=SplitMode.A
)

tokens = tokenize_sudachi(
    df,
    extra_col=None
)
```

---

## Janome と SudachiPy の違い（要点）

| 観点 | Janome | SudachiPy |
|---|---|---|
| 分割粒度 | 固定 | A / B / C |
| 正規化形 | なし | あり |
| 軽量性 | 高い | やや重い |
| 精度 | 十分 | 高い |
| 教育用途 | ◎ | ○ |
| 研究用途 | △ | ◎ |

---

## 選択指針

- **Janome**  
  授業・演習 / 小規模データ / 導入の簡単さ重視  

- **SudachiPy**  
  研究用途 / 中〜大規模データ / 分析精度・再現性重視
