# WordCloud を作成する（Bag of Words 可視化）

本ドキュメントでは、本リポジトリの  
[`libs/bow.py`](../../libs/bow.py)  
で提供している **WordCloud 作成用ユーティリティ**について説明します。

WordCloud は、形態素解析後の **Bag of Words（BoW）表現**を可視化する代表的な手法であり、  
文書集合の特徴語を直感的に把握するのに適しています。

---

## 最小構成での使い方（Colab・ワンコピペ）

以下のセルを **そのまま 1 回実行**してください。

```python
!pip install wordcloud
!git clone https://github.com/ugohsu/colab-nlp-templates.git

import sys
sys.path.append("/content/colab-nlp-templates")

from libs import tokens_to_text, create_wordcloud
```

---

## 日本語フォント設定（必須）

WordCloud で日本語を正しく表示するには、  
**日本語フォントファイルのパスを `font_path` に指定できている必要があります。**

- テンプレート（貼り付けて使う）  
  - [`templates/matplotlib_japanese_font.py`](../../templates/matplotlib_japanese_font.py)
- 解説ドキュメント  
  - [`docs/matplotlib_japanese_font.md`](../matplotlib_japanese_font.md)

👉 上記テンプレは、（Colab ノートブック上で）`font_path` を **グローバル変数として定義**し、  
`create_wordcloud` 関数から参照される設計です。

> 注意：このテンプレは、環境によってパスの調整が必要になる可能性があります。  
> 「実行すれば必ず動く」とは限らないため、**必ず `font_path` が正しいフォントを指しているか確認**してください。

### `font_path` の確認（強く推奨）

- `font_path` が定義されているか
- そのパスが実在するか
- 指しているフォントで日本語が表示できるか

最低限、次が通ることを確認してください：

```python
print(font_path)
```

---

## 前提条件

- 形態素解析済みの DataFrame が存在すること
- DataFrame には少なくとも以下の列が含まれること：
  - `word`：トークン
  - `pos`：品詞（大分類）

（※ `tokenize_janome` / `tokenize_sudachi` の出力を想定）

---

## 提供関数

### tokens_to_text

```python
tokens_to_text(df, pos_keep=None)
```

#### 役割
- 形態素解析済み DataFrame から単語を抽出し、
- **WordCloud / tf-idf / LDA などで使える分かち書きテキスト**を生成します。

#### 引数

- `df`  
  形態素解析済み DataFrame  
  （`word`, `pos` 列を含むこと）

- `pos_keep`（任意）  
  抽出対象とする品詞
  - `None`：全品詞（既定）
  - `"名詞"`：名詞のみ
  - `("名詞", "動詞")`：複数指定

#### 戻り値

- `str`  
  スペース区切りの分かち書きテキスト

#### 使用例

```python
sentence = tokens_to_text(tokens_df)
sentence = tokens_to_text(tokens_df, pos_keep="名詞")
```

---

### create_wordcloud

```python
create_wordcloud(
    sentence,
    stopwords=None,
    outfile="img.png",
    figsize=(10, 6),
    background_color="white",
    width=1200,
    height=800,
    random_state=42,
)
```

#### 役割
- 分かち書き済みテキストから WordCloud を生成・表示・保存します。

#### 重要な前提
- `font_path` が **事前に定義されていること**
  - 日本語フォント設定テンプレ（または同等の設定）を先に行ってください
  - `print(font_path)` が通ることを確認してください

#### 主な引数

- `sentence`（必須）  
  分かち書き済みテキスト（`tokens_to_text` の出力）

- `stopwords`（任意）  
  除外したい語の集合（`set` / `list`）

- `outfile`（任意）  
  出力画像ファイル名  
  - `None` を指定すると保存しません

- `figsize`  
  表示サイズ（matplotlib）

- `background_color`  
  背景色（既定：`"white"`）

- `width`, `height`  
  生成する画像サイズ（ピクセル）

- `random_state`  
  レイアウトの再現性確保用シード

#### 使用例

```python
sentence = tokens_to_text(tokens_df, pos_keep="名詞")

create_wordcloud(
    sentence,
    stopwords={"する", "ある", "いる"},
    outfile="wordcloud.png"
)
```

---

## よくある注意点

### 日本語が表示されない

- `font_path` が正しく設定されていない可能性があります  
  - まず `print(font_path)` を確認してください
- WordCloud は matplotlib のフォント設定とは独立して  
  **font_path を直接指定する必要があります**
- パスが存在していても、日本語非対応フォントだと □（豆腐）になります

---

### WordCloud が空になる

- `pos_keep` を絞りすぎていないか確認してください
- トークン数が極端に少ないと表示されません

---

## 想定ユースケース

- 文書集合の特徴語の把握
- トピックモデル前の探索的分析
- 授業・演習での可視化デモ
- BoW に基づく直感的な説明資料

---

## 関連ドキュメント

- 形態素解析  
  - [`docs/tokenization.md`](../tokenization.md)
- 日本語フォント設定  
  - [`docs/matplotlib_japanese_font.md`](../matplotlib_japanese_font.md)
