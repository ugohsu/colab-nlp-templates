# Colab NLP Templates

このリポジトリは、**Google Colaboratory 上で自然言語処理（NLP）を学ぶための  
テンプレートおよび関数群**をまとめた教材用リポジトリです。

ゼミ・演習での利用を主目的とし、

- **コードセルに貼り付けて使うテンプレート**
- **import して使う共通関数群**
- それらの背景・理由・注意点を説明する **ドキュメント**

を明確に分離して整理しています。

---

## 基本方針

### templates（貼り付けて使う）

- Google Colab の **コードセルにそのまま貼り付けて実行**
- import はしない
- 認証・初期設定・定型処理向け

### libs（import して使う）

- リポジトリを clone した後、**import して使用**
- ゼミ内で共通利用する前処理・関数群

### docs（解説）

- 各テンプレ・関数の **背景・理由・注意点**
- 「なぜこの設定が必要か」を説明する man / README 相当

---

## テンプレート一覧（貼り付けて使う）

| 内容 | テンプレート | 解説ドキュメント |
|---|---|---|
| Google スプレッドシート読み込み | [`templates/load_google_spreadsheet.py`](./templates/load_google_spreadsheet.py) | [`docs/load_google_spreadsheet.md`](./docs/load_google_spreadsheet.md) |
| matplotlib 日本語表示設定 | [`templates/matplotlib_japanese_font.py`](./templates/matplotlib_japanese_font.py) | [`docs/matplotlib_japanese_font.md`](./docs/matplotlib_japanese_font.md) |

---

## 関数群（import して使う）

| 内容 | 実装ファイル | 解説ドキュメント |
|---|---|---|
| 形態素解析（Janome / SudachiPy） | [`libs/preprocess.py`](./libs/preprocess.py) | [`docs/tokenization.md`](./docs/tokenization.md) |

### 提供関数

- `tokenize_janome`
- `tokenize_sudachi`

---

## Google Colab での基本的な使い方（libs）

```python
!git clone https://github.com/ugohsu/colab-nlp-templates.git

import sys
sys.path.append("/content/colab-nlp-templates")

from libs import tokenize_janome, tokenize_sudachi
```

※ 必要なライブラリ（Janome / SudachiPy）の install 方法や  
　どちらを選ぶべきかは [`docs/tokenization.md`](./docs/tokenization.md) を参照してください。

---

## 想定ユースケース

- ゼミ・演習での日本語 NLP 入門
- Google スプレッドシートを起点としたデータ分析
- 形態素解析 → BoW / TF-IDF / トピックモデル
- 教育用途を意識した再現性のある Colab ノートブック作成

---

## ライセンス・利用について

- 教育・研究目的での利用を想定しています
- 講義資料・演習ノートへの組み込みも自由です
