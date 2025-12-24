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

### 引数一覧（全体像）

`tokenize_df` は「**共通オプション**」と「**エンジン固有オプション**」を同時に受け取れます。

#### A. 共通オプション（Janome / Sudachi どちらでも使える）

| 引数 | 既定値 | 何をするか | いつ触るか |
|---|---:|---|---|
| `id_col` | `"article_id"` | 文書ID列名 | 入力列名が違うとき |
| `text_col` | `"article"` | テキスト列名 | 入力列名が違うとき |
| `engine` | `"sudachi"` | 解析エンジン選択 | Janome を使いたいとき |
| `stopwords` | `None` | 除外語集合（例：`{"する","なる"}`） | ノイズが多いとき |
| `pos_keep` | `None` | 残す品詞（大分類）の集合（例：`{"名詞","動詞"}`） | 品詞で絞りたいとき |
| `extra_col` | `"token_info"` | 追加情報列名。`None` で列自体を作らない | 軽量化したいとき |

#### B. Janome オプション（`engine="janome"` のとき意味を持つ）

| 引数 | 既定値 | 何をするか | 補足 |
|---|---:|---|---|
| `tokenizer` | `None` | Janome の Tokenizer を外から渡す | 大規模時に「使い回し」可能 |
| `use_base_form` | `True` | 原形（base_form）を使う | `False` なら表層形 |

#### C. SudachiPy オプション（`engine="sudachi"` のとき意味を持つ）

| 引数 | 既定値 | 何をするか | 補足 |
|---|---:|---|---|
| `split_mode` | `None` | 分割粒度（A/B/C） | `None` は **C** 相当として扱われます |
| `dict_type` | `"core"` | 使用辞書（`"core"` など） | Colab では `sudachidict_core` が定番 |
| `word_form` | `"dictionary"` | 語形（`surface`/`dictionary`/`normalized`） | 語彙数と安定性に影響 |

#### D. 追加挙動（共通）

| 引数 | 既定値 | 何をするか | 注意 |
|---|---:|---|---|
| `extra_info` | `False` | `token_info` に **詳細属性 dict** を入れる | 便利だが重くなる |

---

### `tokenize_text_fn`（上級：1テキスト関数の注入）

`tokenize_text_fn` は「**1つのテキスト → TokenRecord の list**」を返す関数を渡すための引数です。

- これを渡した場合、`engine` やエンジン固有引数（`split_mode` 等）は **基本的に使われません**  
  （どの関数をどう呼ぶかは `tokenize_text_fn` 側で決まるため）
- 大規模処理で tokenizer を **外で初期化して使い回す** ときに有効です  
  （`corpus_pass1` の高速化方針がこれです）

例（Sudachi tokenizer を使い回す）：

```python
from sudachipy import Dictionary, SplitMode
from libs import tokenize_df, tokenize_text_sudachi

tok = Dictionary(dict="core").create(mode=SplitMode.C)

df_tok = tokenize_df(
    df,
    id_col="article_id",
    text_col="article",
    tokenize_text_fn=lambda t: tokenize_text_sudachi(
        t,
        tokenizer=tok,
        word_form="normalized",
    ),
    extra_col=None,   # 追加情報列を作らない（軽量化）
    extra_info=False, # token_info の dict も作らない（軽量化）
)
```

---

### `stopwords` と `pos_keep` の使い方

#### 1) stopwords（除外語）
`stopwords` は **集合（set）**で渡します。

```python
stop = {"する", "なる", "ある"}
df_tok = tokenize_df(df, engine="sudachi", stopwords=stop)
```

- 迷ったら、まずは **明らかな機能語**・口癖・ノイズ語から除外します
- 除外語が増えすぎると、文書の特徴が薄くなるので注意

#### 2) pos_keep（残す品詞）
`pos_keep` は「品詞（大分類）」で残すものを指定します。

```python
df_tok = tokenize_df(df, engine="sudachi", pos_keep={"名詞", "動詞", "形容詞"})
```

- **名詞だけ**にすると、トピックは作りやすいが、文のニュアンスが落ちやすい
- 動詞・形容詞も残すと、語彙が増えますが解釈は豊かになります

---

### `extra_col` と `extra_info`（軽量化のコツ）

- `extra_col=None`  
  → `token_info` 列を作らず、出力を軽くします（おすすめの軽量化）
- `extra_info=True`  
  → `token_info` に「詳細属性 dict」を入れます（便利だが重い）

目安：
- **授業・演習**：`extra_col="token_info"` のままでOK
- **研究・大規模**：まず `extra_col=None` を検討（必要になったら戻す）

---

### `tokenizer` を渡す（速度が必要なとき）

Janome / Sudachi いずれも tokenizer 初期化にはコストがあります。  
何度も同じ tokenizer を使う場合は、外で作って渡すと速くなります。

- `tokenize_df` で tokenizer を渡す  
- さらに大規模なら `tokenize_text_fn` で注入する

という段階的な選び方ができます。

## SudachiPy における語形の違い

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
