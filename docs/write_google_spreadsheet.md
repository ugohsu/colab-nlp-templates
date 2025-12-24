# Google スプレッドシートへ DataFrame を書き込む（上書き保存）

本ドキュメントでは、本リポジトリ内の  
[`libs/gsheet_io.py`](../libs/gsheet_io.py)  
で提供している **Google スプレッドシート書き込み用関数**について説明します。

この関数は、Google Colaboratory 上で作成・加工した  
**Pandas DataFrame を Google スプレッドシートへ安全に書き戻す**ための  
定型処理をライブラリ化したものです。

---

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

本関数を使用するには、**事前に gspread クライアント（`gc`）が準備されている必要があります。**

（※ 上記「最小構成での使い方」を参照してください）

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

## 使用例（Colab）

```python
from libs import write_df_to_gsheet

write_df_to_gsheet(
    df_result,
    gc=gc,
    sheet_url="https://docs.google.com/spreadsheets/d/xxxxxxxxxx",
    sheet_name="analysis_result",
)
```

---

## 関連ドキュメント

- 読み込み（認証・gc 作成）  
  - [`docs/load_google_spreadsheet.md`](./load_google_spreadsheet.md)
- 形態素解析（前処理）  
  - [`docs/tokenization.md`](./tokenization.md)
