# ============================================================
# Google スプレッドシート I/O（書き込み）
#   - Google Colab 用（認証済み gspread client を受け取る）
#   - gspread_dataframe.set_with_dataframe を使用
#   - 既存シートを安全に上書きするための定型関数
# ============================================================

from __future__ import annotations

from typing import Any

import pandas as pd
from gspread_dataframe import set_with_dataframe


def write_df_to_gsheet(
    df: pd.DataFrame,
    *,
    gc: Any,
    sheet_url: str,
    sheet_name: str,
    include_index: bool = False,
    clear_sheet: bool = True,
    fillna: bool = True,
) -> None:
    """
    Pandas DataFrame を Google スプレッドシートに書き込む（上書き保存）。

    【用途】
    - 分析結果を Google スプレッドシートに保存したいとき
    - 学生配布・提出用データを出力したいとき
    - Colab 上で完結する分析パイプラインの最終出力

    【前提】
    - gc は認証済みの gspread クライアント
    - sheet_url は「書き込み権限」を持つスプレッドシートの URL

    【注意】
    - clear_sheet=True の場合、既存データはすべて消去されます（上書き用途向け）
    """

    # --------------------------------------------------------
    # 1. 書き込み用 DataFrame の準備（元 df を壊さない）
    # --------------------------------------------------------
    df_out = df.copy()

    # Google Sheets は NaN を扱うと意図しない挙動になることがあるため、
    # 必要に応じて空文字に変換する（見た目も安定しやすい）
    if fillna:
        df_out = df_out.fillna("")

    # --------------------------------------------------------
    # 2. スプレッドシート／ワークシートの取得
    # --------------------------------------------------------
    sh = gc.open_by_url(sheet_url)

    try:
        # 指定したワークシート（タブ）が存在する場合
        ws = sh.worksheet(sheet_name)
    except Exception:
        # 存在しない場合は新規作成（行列数は後で resize されるので仮でOK）
        ws = sh.add_worksheet(title=sheet_name, rows=100, cols=26)

    # --------------------------------------------------------
    # 3. 既存内容のクリア（上書き保存）
    # --------------------------------------------------------
    if clear_sheet:
        ws.clear()

    # --------------------------------------------------------
    # 4. DataFrame → Google スプレッドシート
    # --------------------------------------------------------
    # set_with_dataframe は以下を自動で行ってくれる：
    # - 列名の書き込み
    # - 行数・列数に応じたシートサイズ調整（resize=True）
    set_with_dataframe(
        ws,
        df_out,
        include_index=include_index,
        include_column_header=True,
        resize=True,
    )

    # 完了メッセージ（ログ確認用）
    print("✅ DataFrame written to Google Sheets:", sheet_url, "/", sheet_name)
