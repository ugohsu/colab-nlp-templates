# 語頻度（Term Frequency）

本ドキュメントでは、形態素解析済みの **tokens DataFrame**（「1行 = 1トークン」）から、  
**語頻度（単語 × 出現回数）** を作る最小構成を示します。

- まず **pandas** だけで語頻度を出す（最小）
- 次に **scikit-learn** に接続する（最小）

> ここでは「見栄えのための追加メソッド」は極力省略し、  
> **学生が “必須の行” を迷わない** ことを優先します。

---

## 前提：入力（tokens DataFrame）

このドキュメントは、すでに形態素解析が完了している前提です。  
入力は次の列を持つ DataFrame（例：`tokens`）です。

- `article_id`：文書ID（必須）
- `word`：トークン
- `pos`：品詞（大分類）
- （任意）`token_info`

形態素解析の作り方は、こちらを参照してください。

- 形態素解析（Janome / SudachiPy）：[`../tokenization.md`](../tokenization.md)  
- BoW 章トップ：[`README.md`](README.md)

---

## 0. 最小の準備（Colab）

> この章は **tokens DataFrame から開始**するので、追加のライブラリは基本不要です。

```python
import pandas as pd
```

---

## 1. pandas で語頻度（最小）

### 1-A. 全体の語頻度（単語 × 回数）

```python
# tokens: [article_id, word, pos] を持つ DataFrame
freq = tokens["word"].value_counts()
freq.head()
```

- **必須**：`value_counts()`（これだけで頻度が出ます）
- `head()` は表示用（なくても動きます）

---

### 1-B. 品詞で絞って語頻度（最小）

例：名詞だけ

```python
freq_noun = tokens.loc[tokens["pos"] == "名詞", "word"].value_counts()
freq_noun.head()
```

- **必須**：`loc[...]` で絞る + `value_counts()`

---

### 1-C. DataFrame 形式で持つ（最小）

後で join したり、保存したりするなら DataFrame にします。

```python
freq_df = tokens["word"].value_counts().reset_index()
freq_df.columns = ["word", "count"]
freq_df.head()
```

- **必須**：`value_counts()` → `reset_index()`
- 列名を付ける（これも後続作業のための最小限）

---

## 2. scikit-learn に接続（最小）

ここでは **scikit-learn に形態素解析はさせません**。  
すでに tokens（縦持ち）になっているものを、**文書ごとに結合して**から渡します。

> 以降は、`article_id` ごとに `word` をスペース区切りで連結した  
> 「文書＝文字列」を作り、CountVectorizer / TfidfVectorizer に渡します。

---

## 2-A. まず “文書＝文字列” を作る（最小）

```python
docs = (
    tokens
    .groupby("article_id")["word"]
    .apply(lambda s: " ".join(s.astype(str)))
)
```

- **必須**：`groupby(...).apply(" ".join)` の発想
- `docs` は pandas の Series（index が article_id）

---

## 2-B. CountVectorizer（BoW 行列）に接続（最小）

> すでに空白区切りの「分かち書き」なので、  
> `token_pattern` を空白で拾うデフォルトのまま使えます。

```python
from sklearn.feature_extraction.text import CountVectorizer

cv = CountVectorizer()
X = cv.fit_transform(docs.values)   # (文書数 × 語彙数) の疎行列
vocab = cv.get_feature_names_out()
```

- **必須**：`CountVectorizer()` と `fit_transform(...)`
- `docs.values`（文字列配列）を渡すだけ

### “全体の語頻度” を sklearn 側で出す（最小）

```python
word_counts = X.sum(axis=0)                 # 語彙方向に合計
freq_sklearn = pd.Series(word_counts.A1, index=vocab).sort_values(ascending=False)
freq_sklearn.head()
```

- **必須**：`X.sum(axis=0)` と `pd.Series(..., index=vocab)`

---

## 2-C. TF-IDF に接続（最小）

```python
from sklearn.feature_extraction.text import TfidfVectorizer

tv = TfidfVectorizer()
X_tfidf = tv.fit_transform(docs.values)
vocab_tfidf = tv.get_feature_names_out()
```

- **必須**：`TfidfVectorizer()` と `fit_transform(...)`
- TF-IDF の「全体ランキング」を作りたい場合は、平均などを取ります（ここは用途次第）

---

## よくある注意（最小）

### tokens に欠損がある
```python
tokens = tokens.dropna(subset=["word"])
```

### docs が空になる（全部 stopwords で消えた等）
```python
docs = docs[docs.str.len() > 0]
```

---

## 次に進む

- WordCloud：[`wordcloud.md`](wordcloud.md)  
- BoW の位置づけ：[`README.md`](README.md)
