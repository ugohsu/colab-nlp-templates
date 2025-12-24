# colab-nlp-templates

このリポジトリは、Google Colab 上で自然言語処理（NLP）を行うための
最小構成テンプレート集です。
教育用途・研究用途のいずれでも、そのまま利用できることを目的としています。

---

## トークナイズ設計について（重要）

本テンプレートでは、用途に応じて以下の2段階の API を用意しています。

### 1. DataFrame 全体を処理する場合（基本）

```python
from libs import tokenize_df

df = tokenize_df(df, text_col="text", engine="sudachi")
```

### 2. 大規模データ・逐次処理の場合（推奨）

```python
from libs import tokenize_text_sudachi

tokens = tokenize_text_sudachi(text)
```

後者は tokenizer の初期化コストを抑え、
大量のテキストを高速に処理するための内部関数です。
`corpus_pass1` ではこの形式を前提としています。
