# Google スプレッドシートへ DataFrame を書き込む（上書き保存）

本ドキュメントでは、本リポジトリ内の  
[`libs/gsheet_io.py`](../libs/gsheet_io.py)  
で提供している **Google スプレッドシート書き込み用関数**について説明します。

この関数は、Google Colaboratory 上で作成・加工した  
**Pandas DataFrame を Google スプレッドシートへ安全に書き戻す**ための  
定型処理をライブラリ化したものです。

---

---

## クイックスタート（gc を 1 行で準備）
> ✅ `write_df_to_gsheet` は `gc` を省略できます（Colab 前提で自動認証します）。
> 何度も書き込む場合は、`gc = get_gspread_client_colab()` で一度だけ用意して渡すのがおすすめです。


`gc`（認証済み gspread client）を毎回コピペで用意するのが面倒な場合は、  
次の 1 行で準備できます（Colab 前提）。

```python
%run /content/colab-nlp-templates/tools/gsheet_quickstart.py
```

実行後は次が利用できます。

- `gc` : 認証済み gspread client
- `write_df(df, sheet_url, sheet_name="temporary")` : 簡易書き込みラッパ

> `write_df` は内部で `write_df_to_gsheet` を呼び出しています。

---

## シート名（sheet_name）の既定値

「とりあえず df の中身を確認したい」用途を想定し、  
`write_df_to_gsheet` の `sheet_name` は既定で `"temporary"` になっています。

```python
from libs import write_df_to_gsheet

write_df_to_gsheet(
    sheet_url=SHEET_URL,
    df=df,
    # gc は省略可（Colab 前提で自動認証）
    # sheet_name は省略可（既定 "temporary"）
)

# 何度も書くなら、gc を 1 回だけ作って渡す
from libs.gsheet_io import get_gspread_client_colab

gc = get_gspread_client_colab()
write_df_to_gsheet(gc=gc, sheet_url=SHEET_URL, df=df)
```

---

## value_counts() の結果（Series）もそのまま書けます

`df["pos"].value_counts()` のような **Series** を書き込むときに、  
`reset_index()` を忘れてエラーになることがあります。

本リポジトリの `write_df_to_gsheet` は、既定で **自動整形（normalize=True）** を行うため、  
Series をそのまま渡しても書き込みできます。

```python
pos_counts = df_tok["pos"].value_counts()

write_df_to_gsheet(
    gc=gc,
    sheet_url=SHEET_URL,
    df=pos_counts,  # Series OK
)
```

- Series → DataFrame への変換
- reset_index の自動適用（include_index=False のとき）
- 列名の補完（重複解消・MultiIndex のフラット化を含む）

を行ってから書き込みます。


## 最小構成での使い方（Colab）

この関数を使うために **最低限必要な手順**は次のとおりです。

### 1. リポジトリを取得し、import 設定を行う

```python
!git clone https://github.com/ugohsu/colab-nlp-templates.git

import sys
sys.path.append("/content/colab-nlp-templates")

from libs import write_df_to_gsheet
```

### 2. 事前に `gc`（gspread クライアント）を準備する

本関数は **認証済みの gspread クライアント（`gc`）を外部から受け取る設計**です。  
そのため、事前に以下のテンプレートを **一度だけ実行**してください。

- 読み込みテンプレ（認証・gc 作成を含む）  
  - [`templates/load_google_spreadsheet.py`](../templates/load_google_spreadsheet.py)
- 解説ドキュメント  
  - [`docs/load_google_spreadsheet.md`](./load_google_spreadsheet.md)

👉 このテンプレートを実行すると、  
**Google アカウント認証 + `gc` の作成**までが完了します。

以降は、同じ Colab セッション内で `gc` をそのまま再利用できます。

---

## 前提（重要）

- `sheet_url` は **編集権限**を持つスプレッドシートの URL であること
- `gc` は **認証済みの gspread クライアント**であること（上記テンプレで準備）

---

## 関数の概要

### 関数名

```text
write_df_to_gsheet
```

### 役割

- Pandas DataFrame を Google スプレッドシートへ書き込む
- 既存のワークシート（タブ）を **安全に上書き**
- ワークシートが存在しない場合は **自動で新規作成**
- DataFrame の列名（ヘッダー）も書き込む（常に `include_column_header=True`）

---

## 関数定義（概要）

```python
write_df_to_gsheet(
    df: pd.DataFrame,
    *,
    gc,
    sheet_url: str,
    sheet_name: str,
    include_index: bool = False,
    clear_sheet: bool = True,
    fillna: bool = True,
) -> None
```

---

## 引数（オプション）を詳細に解説

### `df`（必須）

- 書き込み対象の `pandas.DataFrame`
- 関数内部で `df.copy()` を作るため、**元の DataFrame は破壊されません**
- 典型例：集計結果、前処理後データ、分析結果など

---

### `gc`（必須）

- 認証済みの `gspread` クライアント
- Google Colab では以下のテンプレートを実行して作成します  
  - [`templates/load_google_spreadsheet.py`](../templates/load_google_spreadsheet.py)

**なぜ外から受け取るのか？**  
- 認証は環境依存（Colab 固有）なのでテンプレに切り出し  
- 書き込み関数は「書く」責務だけに集中させるため

---

### `sheet_url`（必須）

- 書き込み先スプレッドシートの URL
- **「編集可」以上の権限**が必要です

**よくある失敗**
- 閲覧権限しかない URL を指定すると、書き込み時にエラーになります

---

### `sheet_name`（必須）

- 書き込み先ワークシート（タブ）の名前
- 存在しない場合は **自動作成**されます

**授業で便利な運用例**
- `"tokens"`、`"bow"`、`"tfidf"`、`"lda_result"` のように  
  処理の段階ごとにタブを分けると混乱しにくいです

---

### `include_index`（任意、既定 `False`）

- `True`：DataFrame の index を 1 列目として書き込みます  
- `False`：index は書き込みません（既定）

**いつ `True` にする？**
- index に意味がある場合（例：日付 index、銘柄コード index、ランキング順位など）
- `df.reset_index()` せずに index を保持したまま書きたい場合

**注意**
- `include_index=True` にすると列数が 1 つ増えるため、  
  Google Sheets 側で「想定より1列ずれた」と感じることがあります

---

### `clear_sheet`（任意、既定 `True`）

- `True`：書き込み前に `ws.clear()` を実行し、**既存の内容を完全に消去**してから書き込みます  
- `False`：既存内容を消さずに書き込みます（ただし後述の注意あり）

**なぜ既定が `True` なのか？（教育用途で重要）**
- 以前の出力が残ると、行数が短くなったときに「古い行が残って見える」などの混乱が起きやすい  
- そのため、「常にこの関数を呼べばタブの内容が DataFrame と一致する」ことを優先しています

**`False` にするケース**
- 既存のセル装飾（色、罫線、コメント等）を残したいとき  
  ※ ただし、`set_with_dataframe(..., resize=True)` によりシートサイズは変わる点に注意

**強い注意**
- `clear_sheet=True` の場合、既存データは消えます  
  意図しない上書きを避けるため、授業では `sheet_name` を固定せず  
  `"result_YYYYMMDD"` のように分ける運用も有効です

---

### `fillna`（任意、既定 `True`）

- `True`：`NaN`（欠損値）を空文字 `""` に置き換えてから書き込みます  
- `False`：`NaN` をそのまま書き込みます

**なぜ既定が `True` なのか？**
- Google Sheets は `NaN` を扱うと、セルが `"nan"` になったり空白になったりして見た目が不安定なことがあります  
- 教育用途では「欠損は空欄として見せる」方が混乱が少ないため、既定を `True` にしています

**`False` にするケース**
- 欠損の有無を明示したい（例：欠損を後で検出したい）
- `NaN` をそのまま残して別処理に回したい（ただし Sheets 上の見え方は不安定になり得ます）

---

## 使い方（Colab）

### 最小例

```python
from libs import write_df_to_gsheet

write_df_to_gsheet(
    df_result,
    gc=gc,
    sheet_url="https://docs.google.com/spreadsheets/d/xxxxxxxxxx",
    sheet_name="analysis_result",
)
```

### index を書き込みたい場合

```python
write_df_to_gsheet(
    df_result,
    gc=gc,
    sheet_url=sheet_url,
    sheet_name="analysis_result",
    include_index=True,
)
```

### 上書きを避けたい（タブ名を変える）例

```python
write_df_to_gsheet(
    df_result,
    gc=gc,
    sheet_url=sheet_url,
    sheet_name="analysis_result_v2",
)
```

---

## よくある注意点

### 書き込み権限エラー

- スプレッドシートの共有設定を確認してください
- **「編集可」権限**が必要です

---

### データが消えたように見える

- `clear_sheet=True` が既定値です
- 上書き保存を前提とした設計のため、**意図した挙動**です

---

## 想定ユースケース

- 分析結果の保存
- 学生への結果配布
- Google Sheets 上での集計・可視化
- Colab 完結型の分析パイプライン

---

## 関連ドキュメント

- 読み込み（認証・gc 作成）  
  - [`docs/load_google_spreadsheet.md`](./load_google_spreadsheet.md)
- 形態素解析（前処理）  
  - [`docs/tokenization.md`](./tokenization.md)

---

この関数は、  
**「Colab → 分析 → Google Sheets へ保存」**  
という流れを安全かつ明確に実現するための、最小構成の I/O 関数です。
