# WordCloud を作成する（Bag of Words 可視化）

本ドキュメントでは、本リポジトリの  
[`libs/bow.py`](../../libs/bow.py)  
で提供している **WordCloud 作成用ユーティリティ**について説明します。

WordCloud は、形態素解析後の **Bag of Words（BoW）表現**を可視化する代表的な手法であり、  
文書集合の特徴語を直感的に把握するのに適しています。

---

## 最小構成での使い方（Colab・ワンコピペ）

以下のセルを **上から順に実行**してください。

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
**日本語フォントファイルのパスを `font_path` として用意し、`create_wordcloud` に渡す必要があります。**

- テンプレート（貼り付けて使う）  
  - [`templates/matplotlib_japanese_font.py`](../../templates/matplotlib_japanese_font.py)
- 解説ドキュメント  
  - [`docs/matplotlib_japanese_font.md`](../matplotlib_japanese_font.md)

👉 上記テンプレは、日本語フォントのパスを取得するための補助です。  
ただし、環境によってはフォントパスの調整が必要になるため、

- `font_path` が「日本語対応フォント」を指しているか
- そのパスが実在するか

を **必ず確認**してください。

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

---

### create_wordcloud

```python
create_wordcloud(
    sentence,
    font_path=None,
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
- 分かち書き済みテキストから WordCloud を生成し、
- **表示（matplotlib）**
- **画像ファイルとして保存（任意）**
を行います。

#### 重要な前提
- `font_path`（日本語フォントファイルのパス）を **引数として渡すこと**
  - `font_path` を未指定のまま実行するとエラーになります

---

#### 引数詳細

- `sentence`（必須）  
  分かち書き済みテキスト（`tokens_to_text` の出力）  
  - 空文字列や空白のみの場合はエラーになります

- `font_path`（必須）  
  日本語フォントファイルのパス（例：`/usr/share/fonts/.../NotoSansCJK-Regular.ttc`）  
  - WordCloud は matplotlib のフォント設定とは独立して  
    **フォントファイルパスを直接指定する必要があります**

- `stopwords`（任意）  
  WordCloud から除外したい語の集合  
  - `set` / `list` を指定可能  
  - `None` の場合は除外語なし

- `outfile`（任意）  
  出力画像ファイル名  
  - 例：`"wordcloud.png"`  
  - `None` を指定すると **保存しません（表示のみ）**

- `figsize`  
  表示サイズ（matplotlib の `figure(figsize=...)`）

- `background_color`  
  背景色  
  - 既定：`"white"`

- `width`, `height`  
  生成する WordCloud 画像サイズ（ピクセル単位）  
  - 表示サイズ（`figsize`）とは独立

- `random_state`  
  レイアウトの再現性確保用乱数シード  
  - 同じ値を指定すると、毎回ほぼ同じ配置になります

---

#### 使用例

```python
sentence = tokens_to_text(tokens_df, pos_keep="名詞")

# 事前に font_path を用意しておく（テンプレ等で取得したパス）
print(font_path)

create_wordcloud(
    sentence,
    font_path=font_path,
    stopwords={"する", "ある", "いる"},
    outfile="wordcloud.png",
    background_color="white",
    width=1200,
    height=800,
)
```

---

## よくある注意点

### 日本語が表示されない

- `font_path` が日本語対応フォントを指していない可能性があります  
  - `print(font_path)` で確認してください
- パスが存在していても、日本語非対応フォントの場合は □（豆腐）になります

---

### WordCloud が空になる

- `pos_keep` を絞りすぎていないか確認してください
- トークン数が極端に少ない場合、描画されません

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
