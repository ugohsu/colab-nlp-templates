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

といった **意味のある単位（語）** を自動で切り出すことができません。

そこで必要になるのが **形態素解析** です。

形態素解析とは、
> 文を「これ以上分解すると意味を失う最小単位（形態素）」に分割し、  
> それぞれに品詞などの情報を付与する処理

です。

---

## 1.2 「表層（ひょうそう）」とは何か（初学者がつまずく点）

形態素解析では、1つの語（トークン）に対して、複数の「語の表し方」があります。

例：
> 食べた

このとき、

- **表層形（surface）**：文章に実際に現れている文字列（この例では「食べた」）
- **基本形（原形 / 辞書形）**：辞書に載っている形（この例では「食べる」）

という2つを区別します。

- 「表層」は **文章の表面に見えている形**（そのままの文字列）
- 「基本形」は **活用などを元に戻した形**

です。

---

## 1.3 なぜ「縦持ち DataFrame」にするのか

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

- 語の出現頻度（count）を数えやすい
- 品詞フィルタが簡単（`df[df["pos"]=="名詞"]` のように書ける）
- LDA / TF-IDF / WordCloud につながる前処理が作りやすい
- pandas の `groupby`, `value_counts` がそのまま使える

---

# 2. “ステップアップ”の考え方：まず全部出して、あとで絞る

初学者がやりがちな失敗は、

> いきなり「名詞だけ」などに限定してしまい、  
> 何が消えたのか／何が残ったのかが分からなくなる

ことです。

そこで本ライブラリでは、次のステップアップを推奨します。

## Step 1：まずは品詞を限定せず tokenize する（全トークン）
```python
df_tok_all = tokenize_df(df)
```

## Step 2：結果を観察する（頻出語・品詞）
```python
df_tok_all["pos"].value_counts().head(20)
df_tok_all["word"].value_counts().head(20)
```

## Step 3：あとから filter していく（品詞を落とす）
```python
from libs.preprocess import filter_tokens_df

df_tok = filter_tokens_df(
    df_tok_all,
    pos_exclude={"助詞", "補助記号", "空白"}
)
```

この流れだと、
- 何を落としたのかが明確
- 品詞設計を試行錯誤しやすい

という利点があります。

---

# 3. 関数リファレンス（学部生向け・丁寧版）

ここからは、以下の4関数について

- **完全な引数一覧（網羅）**
- **各引数の意味**
- **よくある使い方のレシピ**
- **つまずきポイント**

をまとめます。

対象関数：
- `tokenize_df`
- `filter_tokens_df`
- `tokenize_text_janome`
- `tokenize_text_sudachi`

（※本説明は `preprocess.py` 清書版の仕様に合わせています。）

---

# 4. tokenize_df（入口関数）

## 4.1 何をする関数か

`tokenize_df` は **DataFrame（文書単位）** を受け取り、  
形態素解析して **DataFrame（トークン単位）** に変換します。

- 入力：1行=1文書（または1記事）の DataFrame
- 出力：1行=1トークンの DataFrame

---

## 4.2 シグネチャ（概念）

```python
tokenize_df(
    df,
    *,
    id_col="article_id",
    text_col="article",
    engine="sudachi",
    tokenizer=None,
    tokenize_text_fn=None,
    split_mode="C",
    use_base_form=True,
    pos_keep=None,
    pos_exclude=None,
    stopwords=None,
    extra_col="token_info",
) -> pandas.DataFrame
```

`*` が付いているのは「キーワード引数として渡す」想定だと思ってください。  
（例：`tokenize_df(df, id_col="id")` のように書く。）

---

## 4.3 引数（完全網羅）

### df（必須）
- 型：`pandas.DataFrame`
- 意味：入力（文書単位）の表
- 必要な列：`id_col` と `text_col` が必ず存在すること

---

### id_col
- 型：`str`
- 既定：`"article_id"`
- 意味：文書ID列名（例：記事ID、ファイルID、行ID）
- 例：`id_col="id"`

---

### text_col
- 型：`str`
- 既定：`"article"`
- 意味：解析対象の本文列名
- 例：`text_col="text"`

---

### engine
- 型：`str`
- 既定：`"sudachi"`
- 取りうる値：`"sudachi"` / `"janome"`
- 意味：どちらの形態素解析エンジンを使うか

---

### tokenizer
- 型：エンジン依存（Janome Tokenizer / Sudachi Tokenizer）
- 既定：`None`（関数内で自動生成）
- 意味：外で生成した tokenizer を渡したいときに指定

#### いつ使う？
- tokenize を何回も繰り返す（速度改善）
- `tokenize_text_fn` を作るときに、tokenizer をクロージャに閉じ込めたい

---

### tokenize_text_fn（最重要：拡張ポイント）
- 型：`callable` または `None`
- 既定：`None`

意味：
- 1テキスト（1文書）をトークナイズする処理を「丸ごと差し替える」ための引数。

**指定した場合は、原則として tokenize_text_fn が最優先です。**  
（engine や split_mode を tokenize_df 側で指定しても、tokenize_text_fn の中で別のことをしていればそちらが勝ちます。）

#### tokenize_text_fn の仕様（必ず守る）

`tokenize_text_fn(text)` は次の形式を返します：

- 戻り値：`list[tuple[word, pos, token_info]]`

1トークンを表すタプル：
- `word`：`str`（下流の分析で使う語）
- `pos`：`str`（品詞の大分類）
- `token_info`：`dict` または `None`（追加情報。要らなければ None でOK）

例：
```python
[
  ("今日", "名詞", {"surface": "今日", "base_form": "今日"}),
  ("良い", "形容詞", {"surface": "良い", "base_form": "良い"}),
]
```

---

### split_mode（Sudachi 用）
- 型：`str`
- 既定：`"C"`
- 取りうる値：`"A"`, `"B"`, `"C"`
- 意味：Sudachi の分割粒度
- 注意：
  - `engine="janome"` のときは無視されます
  - `tokenize_text_fn` を自作する場合は、tokenize_text_fn 側で split_mode を扱うのが普通です

---

### use_base_form（共通オプション）
- 型：`bool`
- 既定：`True`
- 意味：「word として基本形を使うか／表層形を使うか」

| エンジン | True（既定） | False |
|---|---|---|
| Janome | 原形（base_form） | 表層形（surface） |
| Sudachi | 辞書形（dictionary_form） | 表層形（surface） |

---

### pos_keep
- 型：`iterable[str]` または `None`
- 既定：`None`（限定しない）
- 意味：指定した品詞（大分類）のトークンだけ残す
- 例：`pos_keep={"名詞","動詞","形容詞"}`

---

### pos_exclude
- 型：`iterable[str]` または `None`
- 既定：`None`（除外しない）
- 意味：指定した品詞（大分類）を除外
- 例：`pos_exclude={"助詞","補助記号","空白"}`

---

### stopwords
- 型：`iterable[str]` または `None`
- 既定：`None`
- 意味：word が stopwords に含まれるトークンを除外
- 例：`stopwords={"する","ある","なる"}`

---

### extra_col
- 型：`str` または `None`
- 既定：`"token_info"`
- 意味：
  - `None`：追加情報列を作らない（軽量化）
  - 文字列：その列名で token_info を格納

---

## 4.4 出力 DataFrame の仕様

tokenize_df の出力には次の列が含まれます。

- `id_col`（例：`article_id`）
- `word`
- `pos`
- `token_info`（extra_col が None のときは作られない／または全て None）

---

## 4.5 レシピ

### レシピ1：まず全部 tokenize（推奨）
```python
df_tok_all = tokenize_df(df, id_col="article_id", text_col="article")
```

### レシピ2：Janome を明示
```python
df_tok_all = tokenize_df(df, engine="janome")
```

### レシピ3：品詞フィルタを“後で”やる（推奨）
```python
df_tok_all = tokenize_df(df, extra_col=None)
df_tok = filter_tokens_df(df_tok_all, pos_exclude={"助詞","補助記号","空白"})
```

### レシピ4：stopwords
```python
df_tok = tokenize_df(df, stopwords={"する","ある","なる"})
```

---

# 5. filter_tokens_df（品詞フィルタ専用）

## 5.1 何をする関数か

`filter_tokens_df` は token DataFrame を受け取り、  
品詞（pos）でフィルタします。

「まず tokenize してから後で落とす」という運用の中心関数です。

---

## 5.2 シグネチャ（概念）

```python
filter_tokens_df(
    df,
    *,
    pos_keep=None,
    pos_exclude=None,
    strict=True,
) -> pandas.DataFrame
```

---

## 5.3 引数（完全網羅）

### df（必須）
- 型：`pandas.DataFrame`
- 必須列：`pos`

### pos_keep / pos_exclude
- tokenize_df と同じ意味

### strict
- 型：`bool`
- 既定：`True`
- 意味：pos_keep と pos_exclude を同時指定した場合に矛盾チェックを行う
- 授業では True 推奨（指定ミスが見つかる）

---

## 5.4 レシピ：段階的に削る（推奨）
```python
df_tok_all = tokenize_df(df)

# まず記号・空白だけ消す
df_tok_1 = filter_tokens_df(df_tok_all, pos_exclude={"補助記号","空白"})

# 次に助詞も消す（研究目的による）
df_tok_2 = filter_tokens_df(df_tok_1, pos_exclude={"助詞"})
```

---

# 6. tokenize_text_janome（1テキスト用・Janome）

## 6.1 何をする関数か

Janome で 1つの文字列をトークナイズし、  
`(word, pos, token_info)` の配列を返します。

通常は tokenize_df から呼ばれますが、  
tokenize_text_fn を作るときの「部品」として使います。

---

## 6.2 シグネチャ（概念）

```python
tokenize_text_janome(
    text,
    *,
    tokenizer,
    use_base_form=True,
    extra_col="token_info",
) -> list[tuple[word, pos, token_info]]
```

---

## 6.3 引数（完全網羅）

### text
- 型：`str`（None/空文字の場合もありえる）
- 挙動：None/空は `[]` を返す

### tokenizer（必須）
- 型：`janome.tokenizer.Tokenizer`
- 意味：Janome の tokenizer

### use_base_form
- 型：`bool`
- 既定：`True`
- 意味：word を base_form（基本形）にするか surface（表層）にするか

### extra_col
- 型：`str` または `None`
- 既定：`"token_info"`
- 意味：
  - None：token_info を作らない
  - それ以外：token_info dict（surface/base_form/reading）を作る

---

## 6.4 レシピ：tokenize_text_fn として使う（tokenizer 使い回し）
```python
from janome.tokenizer import Tokenizer
from libs import tokenize_df
from libs.preprocess import tokenize_text_janome

tok = Tokenizer()

df_tok = tokenize_df(
    df,
    tokenize_text_fn=lambda t: tokenize_text_janome(
        t,
        tokenizer=tok,
        use_base_form=True,
        extra_col=None,
    ),
    extra_col=None,
)
```

---

# 7. tokenize_text_sudachi（1テキスト用・Sudachi）

## 7.1 何をする関数か

Sudachi で 1つの文字列をトークナイズし、  
`(word, pos, token_info)` の配列を返します。

Sudachi の強み（分割モード、正規化形）を  
**ユーザーが低レベル API を書かずに使える**ようにしています。

---

## 7.2 シグネチャ（概念）

```python
tokenize_text_sudachi(
    text,
    *,
    tokenizer,
    split_mode="C",
    word_form=None,
    use_base_form=True,
    extra_col="token_info",
) -> list[tuple[word, pos, token_info]]
```

---

## 7.3 引数（完全網羅）

### text
- 型：`str`（None/空文字の場合もありえる）
- 挙動：None/空は `[]` を返す

### tokenizer（必須）
- 型：Sudachi tokenizer（`dictionary.Dictionary().create()` の戻り値）
- 意味：Sudachi の tokenizer

### split_mode
- 型：`str`
- 既定：`"C"`
- 取りうる値：`"A"`, `"B"`, `"C"`
- 意味：分割粒度（Aが細かい、Cが粗い…というイメージでOK）
- 重要：**tokenize_df の split_mode を使うより、tokenize_text_fn 経由で明示する方が分かりやすい**（後述）

### word_form（Sudachi の語形指定）
- 型：`str` または `None`
- 既定：`None`
- 意味：最終的に word として採用する語形を指定
- 取りうる値：
  - None：use_base_form に従う（True→dictionary_form / False→surface）
  - `"dictionary"`：辞書形
  - `"surface"`：表層形
  - `"normalized"`：正規化形

### use_base_form（共通）
- 型：`bool`
- 既定：`True`
- 意味：word_form が None のときだけ参照

### extra_col
- 型：`str` または `None`
- 既定：`"token_info"`
- 意味：
  - None：token_info を作らない
  - それ以外：token_info dict（surface/dictionary_form/normalized_form）を作る

---

## 7.4 レシピ1：Sudachi で正規化形（normalized）を使う（推奨）
「表記ゆれ」を吸収したいときの典型例です。

```python
from sudachipy import dictionary
from libs import tokenize_df
from libs.preprocess import tokenize_text_sudachi

tok = dictionary.Dictionary().create()

df_tok = tokenize_df(
    df,
    tokenize_text_fn=lambda t: tokenize_text_sudachi(
        t,
        tokenizer=tok,
        split_mode="C",
        word_form="normalized",
        extra_col=None,
    ),
    extra_col=None,
)
```

---

## 7.5 レシピ2：split_mode を指定したい（fn を使うレシピ）

split_mode を変えると token の切れ方が変わります。  
本ライブラリでは **tokenize_text_fn を使って明示する**のが分かりやすいです。

```python
from sudachipy import dictionary
from libs import tokenize_df
from libs.preprocess import tokenize_text_sudachi

tok = dictionary.Dictionary().create()

df_tok_A = tokenize_df(
    df,
    tokenize_text_fn=lambda t: tokenize_text_sudachi(
        t, tokenizer=tok, split_mode="A", word_form=None, extra_col=None
    ),
    extra_col=None,
)

df_tok_C = tokenize_df(
    df,
    tokenize_text_fn=lambda t: tokenize_text_sudachi(
        t, tokenizer=tok, split_mode="C", word_form=None, extra_col=None
    ),
    extra_col=None,
)
```

「A と C でどう違うか」を観察するのは良い演習になります。

---

# 8. tokenize_text_fn を完全自作する（MeCab など）

## 8.1 目的

MeCab など別エンジンを使いたい場合でも、  
tokenize_df の下流（BoW / LDA / WordCloud）に接続したい。

そのために tokenize_text_fn を「仕様どおりに」自作します。

---

## 8.2 tokenize_text_fn の入力仕様

- 入力：`text`（1文書分の文字列）
- 可能性：None / 空文字が来ることがある
- 推奨：None/空なら `[]` を返す（他関数と合わせる）

---

## 8.3 tokenize_text_fn の出力仕様（最重要）

戻り値は **list** で、要素は **3要素タプル**です。

```python
[
  (word, pos, token_info),
  ...
]
```

各要素の意味：

### (1) word（必須）
- 型：`str`
- 意味：下流の分析に使う語
- 例：表層形でも基本形でもよい（研究目的で決める）

### (2) pos（必須）
- 型：`str`
- 意味：品詞「大分類」（名詞、動詞、形容詞…）
- 注意：細分類まで入れてもよいが、filter_tokens_df が想定するのは大分類

### (3) token_info（任意）
- 型：`dict` または `None`
- 意味：追加情報（表層形や読みなど）
- 使わないなら None でOK
- extra_col=None にするなら、token_info を常に None にしてよい

---

## 8.4 MeCab の例（雛形）

以下は「形」を示すだけの雛形です（実行には MeCab の導入が必要）。

```python
def tokenize_text_mecab(text):
    if text is None:
        return []
    s = str(text).strip()
    if s == "":
        return []

    records = []
    # ここで MeCab 解析し、各形態素について：
    #   word = ...
    #   pos  = ...
    #   token_info = {...} または None
    # を作って records.append((word, pos, token_info)) する
    return records

df_tok = tokenize_df(
    df,
    tokenize_text_fn=tokenize_text_mecab,
    extra_col=None,  # token_info を不要にする場合
)
```

---

# 9. まとめ（この順で学ぶと安全）

1) まず tokenize_df で **全部 tokenize**（品詞は限定しない）  
2) `value_counts` で **品詞・頻出語を観察**  
3) `filter_tokens_df` で **段階的に落とす**  
4) 研究用途では Sudachi の  
   - `word_form="normalized"`（表記ゆれ吸収）  
   - `split_mode="A/B/C"`（粒度調整）  
   を tokenize_text_fn 経由で使う  
5) さらに必要なら MeCab 等で tokenize_text_fn を自作し、  
   **(word, pos, token_info)** 形式で返す

この順番なら、初学者でも「何が起きているか」を見失いにくいです。
