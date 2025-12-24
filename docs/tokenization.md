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

本リポジトリでは、以下の **2 種類の形態素解析エンジン**を提供しています。

- **Janome 版**：軽量・導入が簡単（授業・演習向け）
- **SudachiPy 版**：高精度・高機能（研究用途向け）

👉 **通常はどちらか一方だけを使えば十分です。**  
Janome と SudachiPy を **同時にインストールする必要はありません。**

---

### 1-A. Janome を使う場合（おすすめ：授業・演習）

```python
!pip install janome
!git clone https://github.com/ugohsu/colab-nlp-templates.git

import sys
sys.path.append("/content/colab-nlp-templates")

from libs import tokenize_df

df_tok = tokenize_df(
    df,
    id_col="article_id",
    text_col="article",
    engine="janome"
)
```

---

### 1-B. SudachiPy を使う場合（研究用途・精度重視）

```python
!pip install sudachipy sudachidict_core
!git clone https://github.com/ugohsu/colab-nlp-templates.git

import sys
sys.path.append("/content/colab-nlp-templates")

from libs import tokenize_df

df_tok = tokenize_df(
    df,
    id_col="article_id",
    text_col="article",
    engine="sudachi"
)
```

---

※ **Google Colab では、ライブラリのインストールは必ず `!pip install ...` の形式で実行してください。**  
※ `pip install ...`（!なし）は Colab では動作しません。

---

## 共通設計思想

- **文書ID列を必須とする**  
  文書単位の集計・分析（LDA・文書ベクトル化など）を前提とするため、  
  ID の有無による分岐は設けていません。
- **出力列構造を固定**  
  基本構成は  
  `article_id`, `word`, `pos`（＋必要に応じて `token_info`）です。
- **Janome / Sudachi で思想と列構造を統一**  
  形態素解析器を差し替えても、後続処理が壊れないことを重視しています。
- **教育用途と研究用途の両立**  
  初学者には分かりやすく、研究用途ではそのまま使える設計です。
- **大規模データでは高速化可能**  
  内部では 1 テキスト用の関数を用いており、
  streaming 処理や pass1 への拡張が可能です。

---

## Janome バージョン（engine="janome"）

### 概要

Janome は軽量でセットアップが容易なため、  
**授業・演習・小規模データ分析**に向いています。

`tokenize_df(..., engine="janome")` を指定することで、  
Janome を用いた形態素解析が実行されます。

---

### 主な引数（Janome）

| 引数名 | 説明 |
|---|---|
| `df` | 入力 DataFrame。`id_col` と `text_col` を必ず含む必要があります。 |
| `id_col` | 文書ID列名（既定値：`article_id`）。 |
| `text_col` | 解析対象テキスト列名（既定値：`article`）。 |
| `use_base_form` | `True` の場合、Janome が返す原形（base_form）を使用します。 |
| `pos_keep` | 抽出する品詞集合。`None` の場合は全品詞。 |
| `stopwords` | 除外する語の集合。 |
| `extra_col` | 追加情報列名。`None` を指定すると軽量化されます。 |

※ Janome には Sudachi のような **正規化形（normalized form）はありません**。  
`use_base_form=True` は、SudachiPy の `word_form="dictionary"` に最も近い挙動です。

---

## SudachiPy バージョン（engine="sudachi"）

### 概要

SudachiPy では、**どの語形を分析に使うか**を明示的に選択できます。  
この選択は、語彙数・集計結果・分析の安定性に大きく影響します。

`tokenize_df(..., engine="sudachi")` を指定することで、  
SudachiPy を用いた形態素解析が実行されます。

---

### 主な引数（SudachiPy）

| 引数名 | 説明 |
|---|---|
| `df` | 入力 DataFrame。 |
| `id_col` | 文書ID列名。 |
| `text_col` | 解析対象テキスト列名。 |
| `split_mode` | 分割粒度（A/B/C）。`C` は複合語をまとめやすい設定です。 |
| `word_form` | トークンとして使用する語形（`surface` / `dictionary` / `normalized`）。 |
| `pos_keep` | 抽出する品詞集合。 |
| `stopwords` | 除外語集合。 |
| `extra_col` | 追加情報列名。 |

---

## SudachiPy における語形の違い（重要）

### 1. surface（表層形）
- 文中に **実際に現れた形**をそのまま使用
- 活用形・表記ゆれをすべて区別
- 文体分析・表現比較向け

例：  
上昇した / 上昇して / 上昇する → すべて別トークン

---

### 2. dictionary（辞書形）【デフォルト】
- 活用語を **辞書形（基本形）** に統一
- 多くの NLP 分析で無難な選択

例：  
上昇した / 上昇して / 上昇する → 上昇する

---

### 3. normalized（正規化形）
- 表記ゆれ（全角・半角・長音など）を強く吸収
- 語彙が最も圧縮され、分析が安定

例：  
コンピューター / コンピュータ / ｺﾝﾋﾟｭｰﾀ → コンピュータ

---

### 語形の比較まとめ

| 観点 | surface | dictionary | normalized |
|---|---|---|
| 活用の違い | 区別 | 吸収 | 吸収 |
| 表記ゆれ | 区別 | 一部残る | 強く吸収 |
| 語彙数 | 多い | 中 | 少ない |
| 分析の安定性 | 低 | 高 | 非常に高 |

---

## Janome と SudachiPy の対応関係

| 観点 | Janome | SudachiPy |
|---|---|---|
| 表層形 | surface | surface |
| 原形 | base_form | dictionary |
| 正規化形 | なし | normalized |

---

## 選択指針（まとめ）

- **授業・演習**  
  - Janome：`use_base_form=True`  
  - SudachiPy：`word_form="dictionary"`

- **研究・大規模分析**  
  - SudachiPy：`word_form="normalized"`

- **文体・表現分析**  
  - SudachiPy：`word_form="surface"`
