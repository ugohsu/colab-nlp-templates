# WordCloud を作成する（Bag of Words 可視化）

本ドキュメントでは、本リポジトリの  
[`libs/bow.py`](../libs/bow.py)  
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
**事前に日本語フォント設定テンプレを実行する必要があります。**

- テンプレート  
  - [`templates/matplotlib_japanese_font.py`](../templates/matplotlib_japanese_font.py)
- 解説ドキュメント  
  - [`docs/matplotlib_japanese_font.md`](./matplotlib_japanese_font.md)

👉 上記テンプレを実行すると、  
`font_path` が **グローバル変数として定義**され、  
WordCloud 関数から参照できるようになります。

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
  - 日本語フォント設定テンプレを先に実行してください

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

- 日本語フォント設定テンプレが **未実行**の可能性があります  
- `font_path` が定義されているか確認してください

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
  - [`docs/tokenization.md`](./tokenization.md)
- 日本語フォント設定  
  - [`docs/matplotlib_japanese_font.md`](./matplotlib_japanese_font.md)
