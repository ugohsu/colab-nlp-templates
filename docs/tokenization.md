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

以下では、前処理モジュール `preprocess.py` に定義されている  
主要関数について、それぞれ **取りうるオプションをすべて**丁寧に説明します。

---

# 1) tokenize_df

## 役割

文書単位の DataFrame を受け取り、  
形態素解析を行って **縦持ち token DataFrame** に変換します。

Janome / Sudachi の切り替え、品詞フィルタ、stopwords 除去などを  
**一括で制御するための入口関数**です。

---

## シグネチャ（概念）

```python
tokenize_df(
    df,
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

---

## 引数一覧

### df（必須）
- **型**：`pandas.DataFrame`
- **意味**：入力（文書単位）の DataFrame
- **注意**：`id_col` と `text_col` を含んでいる必要があります

### id_col
- **型**：`str`
- **既定**：`"article_id"`
- **意味**：文書ID列名

### text_col
- **型**：`str`
- **既定**：`"article"`
- **意味**：解析対象テキスト列名

### engine
- **型**：`str`
- **既定**：`"sudachi"`
- **取りうる値**：`"sudachi"` / `"janome"`
- **意味**：使用する形態素解析エンジン

### tokenizer
- **型**：Janome / Sudachi tokenizer
- **既定**：`None`
- **意味**：外部で初期化した tokenizer を使い回したい場合に指定

### tokenize_text_fn
- **型**：callable または None
- **意味**：1テキストのトークナイズ処理を完全に差し替えるフック

### split_mode（Sudachi 用）
- **型**：`str`
- **既定**：`"C"`
- **意味**：Sudachi の分割モード

### use_base_form（共通）
- **型**：`bool`
- **既定**：`True`
- **意味**：基本形（辞書形）を word として使うか

### pos_keep / pos_exclude
- **型**：iterable[str] または None
- **意味**：品詞（大分類）によるフィルタ

### stopwords
- **型**：iterable[str] または None
- **意味**：語による除外リスト

### extra_col
- **型**：`str` または None
- **意味**：token_info 列を作るかどうか

---

# 2) filter_tokens_df

## 役割
token DataFrame に対して、品詞フィルタのみを適用します。

## シグネチャ

```python
filter_tokens_df(
    df,
    pos_keep=None,
    pos_exclude=None,
    strict=True,
)
```

---

# 3) tokenize_text_janome

## 役割
Janome を用いて 1テキストをトークナイズします。

## シグネチャ

```python
tokenize_text_janome(
    text,
    tokenizer,
    use_base_form=True,
    extra_col="token_info",
)
```

---

# 4) tokenize_text_sudachi

## 役割
Sudachi を用いて 1テキストをトークナイズします。

## シグネチャ

```python
tokenize_text_sudachi(
    text,
    tokenizer,
    split_mode="C",
    word_form=None,
    use_base_form=True,
    extra_col="token_info",
)
```

## word_form オプション

| word_form | 採用される語形 |
|---|---|
| None | use_base_form に従う |
| "dictionary" | 辞書形 |
| "surface" | 表層形 |
| "normalized" | 正規化形 |

---

## 設計方針まとめ

- 共通オプションは tokenize_df で吸収
- エンジン固有の処理は tokenize_text_* 側で吸収
- それでも足りなければ tokenize_text_fn で完全差し替え
