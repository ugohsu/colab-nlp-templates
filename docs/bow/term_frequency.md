# 語頻度（Term Frequency）

本ドキュメントでは、形態素解析済みの **tokens DataFrame**  
（「1行 = 1トークン」の縦持ち形式）から、  
**語頻度（単語 × 出現回数）** を求める最小構成を示します。

ここでは、

- **文字列に戻さない**
- **形態素解析を再実行しない**
- **必須の操作だけを書く**

ことを重視します。

---

## 前提：入力（tokens DataFrame）

入力は、すでに形態素解析が完了した DataFrame です。

最低限、次の列を含んでいる必要があります。

- `article_id`：文書ID  
- `word`：トークン  
- `pos`：品詞（大分類）

形態素解析の作成方法は、以下を参照してください。

- 形態素解析（Janome / SudachiPy）：[`../tokenization.md`](../tokenization.md)  
- BoW 章トップ：[`README.md`](README.md)

---

## 0. 準備（最小）

```python
import pandas as pd
```

---

## 1. pandas で語頻度（最小）

### 1-A. 全体の語頻度（単語 × 回数）

```python
freq = tokens["word"].value_counts()
freq.head()
```

- **必須**：`value_counts()`  
- `head()` は表示用（省略可）

---

### 1-B. 品詞で絞った語頻度（最小）

例：名詞のみ

```python
freq_noun = tokens.loc[tokens["pos"] == "名詞", "word"].value_counts()
freq_noun.head()
```

- **必須**：`loc[...]` + `value_counts()`

---

### 1-C. DataFrame として保持（最小）

後続処理や保存を考える場合、DataFrame にします。

```python
freq_df = tokens["word"].value_counts().reset_index()
freq_df.columns = ["word", "count"]
freq_df.head()
```

- **必須**：`value_counts()` → `reset_index()`
- 列名付与は最小限

---

## 2. scikit-learn で語頻度（最小・推奨）

ここでは、**sklearn に形態素解析はさせません**。  
tokens DataFrame から、

- 文書ごとにトークンの **list**
- それをそのまま `CountVectorizer` に渡す

という、最も素直な方法を用います。

---

### 2-A. 文書ごとに「トークンの list」を作る

```python
docs_tokens = (
    tokens
    .groupby("article_id")["word"]
    .apply(list)
)
```

- 各要素は `["株価", "上昇", "する", ...]` のような list
- **文字列への結合は行いません**

---

### 2-B. CountVectorizer に直接渡す

```python
from sklearn.feature_extraction.text import CountVectorizer

cv = CountVectorizer(
    tokenizer=lambda x: x,
    preprocessor=lambda x: x,
    token_pattern=None,
)

X = cv.fit_transform(docs_tokens)
vocab = cv.get_feature_names_out()
```

- **必須設定**
  - `tokenizer=lambda x: x`
  - `preprocessor=lambda x: x`
  - `token_pattern=None`
- これにより、**事前トークン化済み入力**をそのまま使用

---

### 2-C. 全体の語頻度を求める

```python
word_counts = X.sum(axis=0)
freq_sklearn = pd.Series(word_counts.A1, index=vocab)
freq_sklearn = freq_sklearn.sort_values(ascending=False)
freq_sklearn.head()
```

- **必須**：`X.sum(axis=0)`
- `A1` は numpy 配列への変換

---

## 注意（最小）

### tokens に欠損がある場合

```python
tokens = tokens.dropna(subset=["word"])
```

---

この方法により、

- pandas でも
- scikit-learn でも

**同じ tokens DataFrame** を起点として、  
語頻度を一貫した形で扱うことができます。
