# ============================================================
# 大規模テキスト（1パス目）
#   - rglob で再帰走査して対象ファイル台帳を作る
#   - pending/failed だけ処理して tokens.jsonl に追記
#   - 台帳CSVを更新し、途中停止しても再開できる
# ============================================================

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Callable, Optional, Union

import pandas as pd


TokenizeFunc = Callable[..., pd.DataFrame]


# ------------------------------------------------------------
# 台帳（ジョブ台帳）作成
# ------------------------------------------------------------
def build_file_manifest(
    root_dir: Union[str, Path],
    *,
    ext: str = ".txt",
) -> pd.DataFrame:
    """
    root_dir 配下を再帰走査し、対象ファイル一覧（台帳）を作成する。
    ※ここではファイル本文は読み込まない。

    Returns
    -------
    pd.DataFrame
        columns:
          - doc_id: 1..N の連番
          - path: root_dir からの相対パス
          - filename
          - ext
          - status: pending/done/failed
          - error: 失敗時メッセージ
          - n_chars: 成功時に埋める
          - n_tokens: 成功時に埋める
          - preview: 成功時に埋める（先頭N文字）
          - updated_at: 更新時刻（epoch秒）
    """
    root_dir = Path(root_dir)
    if not root_dir.exists():
        raise FileNotFoundError(f"root_dir not found: {root_dir}")
    if not root_dir.is_dir():
        raise NotADirectoryError(f"root_dir is not a directory: {root_dir}")

    ext = ext if ext.startswith(".") else f".{ext}"

    files = sorted(root_dir.rglob(f"*{ext}"))
    records = []
    doc_id = 0

    for p in files:
        doc_id += 1
        rel = str(p.relative_to(root_dir))
        records.append(
            {
                "doc_id": doc_id,
                "path": rel,
                "filename": p.name,
                "ext": p.suffix,
                "status": "pending",
                "error": "",
                "n_chars": pd.NA,
                "n_tokens": pd.NA,
                "preview": "",
                "updated_at": int(time.time()),
            }
        )

    return pd.DataFrame.from_records(records)


def load_or_create_manifest(
    root_dir: Union[str, Path],
    *,
    manifest_csv: Union[str, Path],
    ext: str = ".txt",
) -> pd.DataFrame:
    """
    既存の台帳CSVがあれば読み込み、なければ新規作成して保存する。
    """
    root_dir = Path(root_dir)
    manifest_csv = Path(manifest_csv)

    if manifest_csv.exists():
        df = pd.read_csv(manifest_csv)
        # 必要列がない場合はエラー（破損対策）
        required = {"doc_id", "path", "status"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"manifest_csv is missing columns: {missing}")
        return df

    df = build_file_manifest(root_dir, ext=ext)
    manifest_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(manifest_csv, index=False)
    return df


# ------------------------------------------------------------
# tokens.jsonl 追記用の小関数
# ------------------------------------------------------------
def append_tokens_jsonl(
    jsonl_fp,
    *,
    doc_id: int,
    path: str,
    tokens: list[str],
) -> None:
    """
    1文書分を 1行JSON として jsonl に追記する。
    """
    out = {"doc_id": doc_id, "path": path, "tokens": tokens}
    jsonl_fp.write(json.dumps(out, ensure_ascii=False) + "\n")


# ------------------------------------------------------------
# Phase 1：pending/failed のみ処理して、jsonl + 台帳更新
# ------------------------------------------------------------
def process_manifest_to_jsonl(
    root_dir: Union[str, Path],
    *,
    manifest_csv: Union[str, Path],
    jsonl_path: Union[str, Path],
    tokenize_func: TokenizeFunc,
    ext: str = ".txt",
    # tokenize_func が期待する列名
    id_col: str = "article_id",
    text_col: str = "article",
    # 読み込み設定
    encoding: str = "utf-8",
    errors: str = "replace",
    # 台帳に入れるプレビュー
    preview_chars: int = 120,
    # どれを処理するか
    statuses_to_process: tuple[str, ...] = ("pending", "failed"),
    # tokenize_func 追加引数（Sudachiのword_form等）
    tokenize_kwargs: Optional[dict] = None,
    # 台帳をどれくらいの頻度で保存するか（安全側：毎回）
    save_every: int = 1,
) -> pd.DataFrame:
    """
    台帳CSVを読み込み（なければ作成）、
    status が pending/failed の行だけを処理して tokens.jsonl に追記する。
    処理結果は台帳CSVへ反映されるため、途中で落ちても再開できる。

    Returns
    -------
    pd.DataFrame
        更新後の台帳（メモリ上）。
    """
    root_dir = Path(root_dir)
    manifest_csv = Path(manifest_csv)
    jsonl_path = Path(jsonl_path)

    tokenize_kwargs = tokenize_kwargs or {}
    # 1パス目は軽量が基本：token_info を切る（必要なら呼び出し側で上書き）
    tokenize_kwargs.setdefault("extra_col", None)

    df = load_or_create_manifest(root_dir, manifest_csv=manifest_csv, ext=ext)

    # ファイルが増減した場合にどうするかは設計次第だが、
    # まずは「台帳にあるものだけ処理する」最小運用に固定する。

    jsonl_path.parent.mkdir(parents=True, exist_ok=True)

    processed = 0

    with open(jsonl_path, "a", encoding="utf-8") as f_jsonl:
        for i, row in df.iterrows():
            status = str(row.get("status", "pending"))
            if status not in statuses_to_process:
                continue

            doc_id = int(row["doc_id"])
            rel_path = str(row["path"])
            p = root_dir / rel_path

            # 存在しない場合は failed 扱いで台帳更新
            if not p.exists():
                df.at[i, "status"] = "failed"
                df.at[i, "error"] = f"file not found: {rel_path}"
                df.at[i, "updated_at"] = int(time.time())
                processed += 1
                if processed % save_every == 0:
                    df.to_csv(manifest_csv, index=False)
                continue

            try:
                # 1) read
                text = p.read_text(encoding=encoding, errors=errors)
                n_chars = len(text)
                preview = text[:preview_chars].replace("\n", "\\n")

                # 2) tokenize（既存 tokenize_* を流用：1文書DataFrameで呼ぶ）
                df_one = pd.DataFrame({id_col: [doc_id], text_col: [text]})
                tok_df = tokenize_func(
                    df_one,
                    id_col=id_col,
                    text_col=text_col,
                    **tokenize_kwargs,
                )
                if "word" not in tok_df.columns:
                    raise KeyError("tokenize_func output must contain 'word' column")

                tokens = tok_df["word"].dropna().astype(str).tolist()
                n_tokens = len(tokens)

                # 3) jsonl 追記（成功したものだけ積む）
                append_tokens_jsonl(
                    f_jsonl,
                    doc_id=doc_id,
                    path=rel_path,
                    tokens=tokens,
                )

                # 4) 台帳更新
                df.at[i, "status"] = "done"
                df.at[i, "error"] = ""
                df.at[i, "n_chars"] = n_chars
                df.at[i, "n_tokens"] = n_tokens
                df.at[i, "preview"] = preview
                df.at[i, "updated_at"] = int(time.time())

            except Exception as e:
                df.at[i, "status"] = "failed"
                df.at[i, "error"] = f"{type(e).__name__}: {e}"
                df.at[i, "updated_at"] = int(time.time())

            processed += 1
            if processed % save_every == 0:
                df.to_csv(manifest_csv, index=False)

    # 最後に確実に保存
    df.to_csv(manifest_csv, index=False)
    return df
