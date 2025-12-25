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

## tokenize_df のオプション（詳細）

ここでは、`tokenize_df` の引数（オプション）を **丁寧に**説明します。  
最初は「最低限の指定」だけで動かし、必要になったときにオプションを追加していく、という使い方が想定です。

---

### まずは最小（必須なのは実質 2 つ）

```python
from libs import tokenize_df

df_tok = tokenize_df(
    df,
    id_col="article_id",
    text_col="article",
    engine="sudachi",  # または "janome"
)
```

- `df`：入力 DataFrame
- `id_col`：文書IDの列名
- `text_col`：解析するテキスト列名

---

## 語形の選択：`use_base_form`（重要）

`use_base_form` は、  
**形態素解析の結果として「どの語形を `word` として使うか」**を決める  
本リポジトリ共通の重要オプションです。

Janome / SudachiPy のどちらを使っても、  
**同じ意味・同じ役割**を持ちます。

---

### `use_base_form` が制御するもの

| エンジン | `use_base_form=True`（既定） | `use_base_form=False` |
|---|---|---|
| **Janome** | 原形（base_form） | 表層形（surface） |
| **SudachiPy** | 辞書形（dictionary_form） | 表層形（surface） |

つまり、

- **True**：活用や表記ゆれを吸収した「基本形」で分析する  
- **False**：文中に現れた形をそのまま使う

という切り替えです。

---

### なぜ共通オプションにしているのか

Janome と SudachiPy では内部構造は異なりますが、

- 「活用をまとめたい」
- 「表現の違いを残したい」

という **分析上の判断は共通**です。

そのため本リポジトリでは、

> **語形選択（表層 vs 基本形）は `use_base_form` で統一的に指定する**

という設計を採っています。

---

### 正規化（normalized form）について

SudachiPy には、さらに強い正規化である  
**normalized_form** が存在しますが、

- これは **共通オプションには含めていません**
- 使用したい場合は、`tokenize_text_fn` を用いて  
  **上級者向けに明示的にカスタマイズ**します

```python
# normalized_form を word として使いたい例（上級）
tokenize_text_fn=lambda t: [
    (m.normalized_form(), m.part_of_speech()[0], None)
    for m in tok.tokenize(t)
]
```

👉 これにより、
- 初学者：`use_base_form` だけ理解すれば十分
- 研究用途：必要な場合のみ拡張

という **二層構造**を保っています。

---

### 引数一覧（全体像）

`tokenize_df` は「**共通オプション**」と「**エンジン固有オプション**」を同時に受け取れます。

#### A. 共通オプション（Janome / Sudachi どちらでも使える）

| 引数 | 既定値 | 何をするか | いつ触るか |
|---|---:|---|---|
| `id_col` | `"article_id"` | 文書ID列名 | 入力列名が違うとき |
| `text_col` | `"article"` | テキスト列名 | 入力列名が違うとき |
| `engine` | `"sudachi"` | 解析エンジン選択 | Janome を使いたいとき |
| `tokenize_text_fn` | `None` | 1テキスト→トークン列の関数を注入（高速化・カスタム） | 大規模処理／tokenizer使い回し／独自ルールを使うとき |
| `stopwords` | `None` | 除外語集合（例：`{"する","なる"}`） | ノイズが多いとき |
| `pos_keep` | `None` | 残す品詞（大分類）の集合（例：`{"名詞","動詞"}`） | 品詞で絞りたいとき |
| `pos_exclude` | `None` | 除外する品詞（大分類）の集合（例：`{"補助記号","空白"}`） | まずは記号・空白だけ落としたいとき |
| `extra_col` | `"token_info"` | 追加情報列名。`None` で列自体を作らない | 軽量化したいとき |
#### B. Janome オプション（`engine="janome"` のとき意味を持つ）

| 引数 | 既定値 | 何をするか | 補足 |
|---|---:|---|---|
| `use_base_form` | `True` | 原形（base_form）を使う（※高速化は tokenize_text_fn 側で行う） | `False` なら表層形 |

#### C. SudachiPy オプション（`engine="sudachi"` のとき意味を持つ）

| 引数 | 既定値 | 何をするか | 補足 |
|---|---:|---|---|
| `split_mode` | `"C"` | 分割粒度（"A"/"B"/"C"） | 迷ったら `"C"` |

> 補足：現行実装では `dict_type` / `word_form` / `extra_info` といった引数は `tokenize_df` にはありません。
> SudachiPy の「正規化形（normalized）」などを使いたい場合は、後述の `tokenize_text_fn` で挙動を差し替える（カスタムする）方式を推奨します。

---

### `tokenize_text_fn`（上級：1テキスト関数の注入）

`tokenize_text_fn` は、`tokenize_df` に「1つのテキストをどうトークナイズするか」を注入するための引数です。  
これを渡すと、`engine` やエンジン固有引数（`split_mode` など）は基本的に使われず、**`tokenize_text_fn` 側の挙動がそのまま採用**されます。

---

#### インタフェース（受け取るもの／返すもの）

`tokenize_text_fn` は、概ね次の形の関数として扱われます。

- **入力**：テキスト（通常は `str`。`None` / `NaN` / 空文字が来る可能性もある）
- **出力**：トークン列（list）

擬似的には次のシグネチャです。

```python
def tokenize_text_fn(text) -> list[tuple[word, pos, token_info]]:
    ...
```

返す list の各要素は次の 3 要素タプルです。

- `word`（str）  
  分析の主対象となる文字列（例：原形／辞書形、または表層形）
- `pos`（str）  
  品詞（**大分類**）。例：`"名詞"`, `"動詞"`, `"形容詞"`, `"補助記号"`, `"空白"` など
- `token_info`（dict または `None`）  
  追加情報（表層形、読み、正規化形など）。必要なら自由に格納できます。  
  `tokenize_df(..., extra_col=None)` の場合は追加情報列を作らないので、`token_info` は `None` にして軽量化できます。

> 重要：自作（例：MeCab 等）でも、**(word, pos, token_info)** の構造で返せば  
> `tokenize_df` 以降の処理（語頻度、WordCloud、n-gram など）へそのまま接続できます。

---

#### いつ使うか（目安）

- 大規模処理で tokenizer を **外で初期化して使い回したい**（高速化）
- Sudachi の **normalized_form を word に採用**したい等、挙動をカスタムしたい
- MeCab など、別の形態素解析器を **自前で組み込みたい**

---

#### 例：Janome tokenizer を使い回す

```python
from janome.tokenizer import Tokenizer
from libs import tokenize_df, tokenize_text_janome

tok = Tokenizer()

df_tok = tokenize_df(
    df,
    id_col="article_id",
    text_col="article",
    tokenize_text_fn=lambda t: tokenize_text_janome(
        t,
        tokenizer=tok,
        use_base_form=True,
    ),
    extra_col=None,   # 軽量化（必要なら戻す）
)
```

#### 例：Sudachi tokenizer を使い回す（辞書形／分割モードC）

```python
from sudachipy import dictionary
from libs import tokenize_df, tokenize_text_sudachi

tok = dictionary.Dictionary().create()

df_tok = tokenize_df(
    df,
    id_col="article_id",
    text_col="article",
    tokenize_text_fn=lambda t: tokenize_text_sudachi(
        t,
        tokenizer=tok,
        split_mode="C",
        use_base_form=True,
        # Sudachi の normalized_form を使いたい場合は、ここをカスタムしてください（後述）
    ),
    extra_col=None,   # 軽量化
)
```

> 目安：授業・小規模なら `engine="janome"` / `engine="sudachi"` だけで十分です。  
> 数万文書以上や繰り返し実行する場合に、`tokenize_text_fn` を検討してください。


## SudachiPy における語形の違い（参考）

> 現行の `tokenize_text_sudachi` は、出力する `word` については `use_base_form`（辞書形か表層形か）で制御します。
> いっぽうで、`token_info`（既定では列名 `token_info`）には `dictionary_form` と `normalized_form` も入ります。
> 「正規化形を分析に使いたい」場合は、`tokenize_text_fn` で `normalized_form` を `word` に採用するカスタムが可能です。


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

## 原形（基本形）と表層形の使い分け（重要）

形態素解析では、「**どの語形を使うか**」によって  
分析結果の性質が大きく変わります。

ここでは、原形（基本形）と表層形の違いと、  
それぞれがどのような分析に向いているかを整理します。

---

### 原形（基本形）を使う場合

**メリット**  
活用や表記のゆれを吸収できるため、  
単語の出現頻度を安定してカウントできます。

例：  
「走る」「走った」「走れば」  
→ すべて「走る」として扱う

**主な用途**
- Bag of Words / TF-IDF などのベクトル化
- トピックモデル（LDA、NMF など）
- テキストマイニング（頻出語・重要語の抽出）

👉 **本リポジトリの BoW・語頻度分析では、原形の使用を基本としています。**

---

### 表層形（surface）を使う場合

**メリット**  
語尾の変化（活用）に含まれるニュアンス  
（過去形・否定・丁寧語など）を保持できます。

**デメリット**  
語彙数が増えやすく、  
データが分散（スパース化）しやすくなります。

**主な用途**
- 文体分析・表現比較
- Nグラム
- 機械翻訳や文章生成  
  （活用が不自然だと文全体が不自然になるため）
- BERT / GPT などの言語モデル  
  （これらは形態素解析を用いず、  
   サブワード単位で処理するため、  
   原形化そのものを前提としません）


#### 例：自作 tokenizer のひな形（MeCab など）

MeCab 等を使って完全に自作する場合も、返り値を **(word, pos, token_info)** に揃えれば OK です。  
以下は「形だけ」示したひな形です（`word` と `pos` を埋めれば動きます）。

```python
from libs import tokenize_df

def my_tokenize_text(text):
    # None/NaN/空文字の扱いはお好みで（空なら [] を返すのが無難）
    if text is None:
        return []

    s = str(text).strip()
    if s == "":
        return []

    records = []
    # ここで MeCab 等で解析して、トークンごとに records.append(...) します
    #
    # records.append((word, pos_major, {"surface": surface, ...}))
    #
    return records

df_tok = tokenize_df(
    df,
    id_col="article_id",
    text_col="article",
    tokenize_text_fn=my_tokenize_text,
    extra_col="token_info",  # 追加情報が不要なら None
)
```

> コツ：まずは `word` と `pos`（大分類）だけ返して動かし、  
> 余裕が出たら `token_info` に表層形や読みなどを足していくのが安全です。

