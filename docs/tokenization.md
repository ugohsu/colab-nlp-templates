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
```

---

### 1-B. SudachiPy を使う場合（研究用途・精度重視）

```python
!pip install sudachipy sudachidict_core
!git clone https://github.com/ugohsu/colab-nlp-templates.git

import sys
sys.path.append("/content/colab-nlp-templates")

from libs import tokenize_df
```

---

※ **Google Colab では、ライブラリのインストールは必ず `!pip install ...` の形式で実行してください。**  
※ `pip install ...`（!なし）は Colab では動作しません。

---

# 1. まず全体像を理解する（重要）

## 1.1 なぜ「形態素解析」が必要なのか

日本語の文章は、英語のように単語ごとに空白で区切られていません。

例：
> 今日は良い天気でした。

この文をそのままコンピュータに渡しても、
- 「今日は」
- 「良い」
- 「天気」
- 「でした」

といった **意味のある単位（語）** を自動で理解することはできません。

そこで必要になるのが **形態素解析** です。

形態素解析とは、
> 文を「これ以上分解すると意味を失う最小単位（形態素）」に分割し、  
> それぞれに品詞などの情報を付与する処理

です。

---

## 1.2 なぜ「縦持ち DataFrame」にするのか

本ライブラリでは、形態素解析の結果を次のような形で扱います。

| article_id | word | pos |
|-----------|------|-----|
| 1 | 今日 | 名詞 |
| 1 | 良い | 形容詞 |
| 1 | 天気 | 名詞 |
| 1 | だ | 助動詞 |

このように  
**「1行 = 1トークン（語）」**  
という形式を「縦持ち」と呼びます。

### なぜ縦持ちがよいのか？

- 語の出現頻度を数えやすい
- 品詞フィルタが簡単
- LDA / TF-IDF / WordCloud に直接つながる
- pandas の groupby / value_counts がそのまま使える

という利点があるためです。

---

## 1.3 tokenize_df は「入口関数」

このライブラリでは、

- tokenize_text_janome
- tokenize_text_sudachi
- filter_tokens_df

といった複数の関数がありますが、  
**通常は tokenize_df だけを使えば十分**です。

tokenize_df は、

> 「DataFrame を受け取り、  
>  形態素解析から後処理までをまとめて行う入口」

として設計されています。

---

# 2. tokenize_df を段階的に理解する

## 2.1 最小構成（まずはこれ）

```python
df_tok = tokenize_df(df)
```

これだけで、

- engine = "sudachi"
- use_base_form = True
- 品詞フィルタなし
- stopwords なし

という **最小構成** の前処理が行われます。

初学者の方は、まずこの形をそのまま使ってください。

---

## 2.2 engine を切り替える

```python
df_tok = tokenize_df(df, engine="janome")
```

とすると、Janome が使われます。

### Janome と Sudachi の違い（考え方）

| 観点 | Janome | Sudachi |
|----|----|----|
| 導入 | 簡単 | やや手間 |
| 精度 | 十分 | 高い |
| 用途 | 授業・演習 | 研究・実務 |
| 正規化 | ほぼ無し | 可能 |

👉 **授業では Janome、研究では Sudachi**  
と考えて問題ありません。

---

## 2.3 use_base_form とは何か

```python
df_tok = tokenize_df(df, use_base_form=True)
```

### 何が変わるのか？

- True（既定）：基本形（辞書形）を使う
- False：表層形を使う

例：

| 設定 | 得られる word |
|----|----|
| True | 食べる |
| False | 食べた |

### なぜ基本形を使うのか？

- 「食べる」「食べた」「食べない」を同一語として扱える
- 語彙数が爆発しにくい
- LDA や TF-IDF で安定する

👉 **基本的には True のまま**で構いません。

---

# 3. 品詞フィルタという考え方

## 3.1 なぜ品詞を落とすのか

分析では、

- 助詞（は、が、を）
- 記号
- 空白

などは、意味的に重要でないことが多いです。

そのため、**品詞で語を選別**します。

---

## 3.2 pos_exclude の例

```python
df_tok = tokenize_df(
    df,
    pos_exclude={"助詞", "補助記号", "空白"}
)
```

### 注意点（重要）

- いきなり厳しく落としすぎない
- まずは結果を見てから調整する

👉 **最初は何も指定しない**のが安全です。

---

# 4. tokenize_text_janome / sudachi の役割

## 4.1 なぜ tokenize_text_* があるのか

tokenize_df の内部では、

- Janome 用
- Sudachi 用

に分かれた **1テキスト処理関数**が使われています。

これらは主に、

- 高速化したい
- tokenizer を使い回したい
- 特殊な処理を入れたい

ときに使います。

---

## 4.2 Sudachi の word_form（重要）

Sudachi では、次のような語形を選べます。

| word_form | 意味 |
|----|----|
| dictionary | 辞書形 |
| surface | 表層形 |
| normalized | 正規化形 |

```python
tokenize_text_sudachi(
    text,
    tokenizer=tok,
    word_form="normalized"
)
```

### 正規化形とは？

- 全角・半角の統一
- 表記ゆれの吸収

例：
- ｺﾝﾋﾟｭｰﾀ
- コンピューター

→ 同じ語として扱われる

👉 **表記ゆれが問題になる研究では非常に重要**です。

---

# 5. tokenize_text_fn は「最後の逃げ道」

## 5.1 なぜ用意されているのか

すべてを共通 API にすると、

- 柔軟性が失われる
- 特殊な研究に対応できない

そこで、

> 「どうしても必要な人のための出口」

として tokenize_text_fn が用意されています。

---

## 5.2 使うべきでないケース

- 初学者
- 授業課題
- 標準的な分析

👉 **まずは使わないでください。**

---

## 5.3 使うべきケース

- MeCab を使いたい
- 独自辞書を使う
- 特殊な正規化をしたい

---

# 6. まとめ（重要）

- tokenize_df は「入口関数」
- 最初は **最小構成** で使う
- Janome / Sudachi の違いは「用途」
- 正規化や拡張は段階的に

---

このドキュメントは、
**「なぜそう設計されているのか」**
を理解することを最優先に書かれています。

コードを写す前に、ぜひ一度、全体を通して読んでください。
