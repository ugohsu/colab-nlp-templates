# Google スプレッドシートへ DataFrame を書き込む（上書き保存）

本ドキュメントでは、本リポジトリ内の  
[`libs/gsheet_io.py`](../libs/gsheet_io.py)  
で提供している **Google スプレッドシート書き込み用関数**について説明します。

この関数は、Google Colaboratory 上で作成・加工した  
**Pandas DataFrame を Google スプレッドシートへ安全に書き戻す**ための  
定型処理をライブラリ化したものです。

---

## 前提（重要）

本関数を使用するには、**事前に gspread クライアント（`gc`）が準備されている必要があります。**

### gc の準備方法

通常は、以下のテンプレートを **事前に実行**してください。

- 読み込みテンプレ（認証・gc 作成を含む）  
  - [`templates/load_google_spreadsheet.py`](../templates/load_google_spreadsheet.py)
- 解説ドキュメント  
  - [`docs/load_google_spreadsheet.md`](./load_google_spreadsheet.md)

👉 上記テンプレートを実行すると、  
**Google アカウント認証 + `gc` の作成**までが完了します。

書き込み関数は、**この `gc` をそのまま再利用**します。

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

## 引数の詳細

### df

- 書き込み対象の Pandas DataFrame
- **元の DataFrame は破壊されません**（内部でコピーを作成）

---

### gc（必須）

- 認証済みの `gspread` クライアント
- Google Colab 上では、  
  [`templates/load_google_spreadsheet.py`](../templates/load_google_spreadsheet.py)  
  を実行することで取得できます

---

### sheet_url（必須）

- 書き込み先となる Google スプレッドシートの URL
- **「編集可」権限**が必要です

---

### sheet_name（必須）

- 書き込み先のワークシート（タブ）名
- 存在しない場合は **自動的に新規作成**されます

---

### include_index（任意）

- `True`：DataFrame の index を 1 列目として書き込む  
- `False`（既定）：index は書き込まない

---

### clear_sheet（任意）

- `True`（既定）：書き込み前にワークシートを **完全にクリア**
- `False`：既存データを残したまま書き込み

⚠️ **`True` の場合、既存データはすべて削除されます。**

---

### fillna（任意）

- `True`（既定）：`NaN` を空文字に変換してから書き込み
- `False`：`NaN` をそのまま書き込む

Google Sheets では `NaN` の扱いが不安定なため、  
通常は `True` のまま使用することを推奨します。

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
