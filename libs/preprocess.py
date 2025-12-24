# ============================================================
# Preprocessing utilities (Japanese tokenization)
# - Janome (optional)
# - SudachiPy (optional)
# ============================================================

from __future__ import annotations

from typing import Iterable, Optional, Literal, Union

import pandas as pd


WordForm = Literal["surface", "dictionary", "normalized"]


def tokenize_janome(
    df: pd.DataFrame,
    *,
    id_col: str = "article_id",
    text_col: str = "article",
    tokenizer=None,
    use_base_form: bool = True,
    pos_keep: Optional[Iterable[str]] = None,
    stopwords: Optional[set[str]] = None,
    extra_col: Optional[str] = "token_info",
) -> pd.DataFrame:
    # ★ここで Janome を遅延 import
    try:
        from janome.tokenizer import Tokenizer as JanomeTokenizer
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            "Janome が未インストールです。Janome を使う場合は Colab で `!pip install janome` を実行してください。"
        ) from e

    for col in (id_col, text_col):
        if col not in df.columns:
            raise KeyError(f"required column '{col}' not found in df")

    t = tokenizer or JanomeTokenizer()
    stopwords = stopwords or set()
    pos_keep_set = set(pos_keep) if pos_keep is not None else None

    records = []
    for doc_id, text in df[[id_col, text_col]].itertuples(index=False, name=None):
        if pd.isna(text):
            continue
        if not isinstance(text, str):
            text = str(text)

        for tok in t.tokenize(text):
            pos = tok.part_of_speech.split(",")[0]
            if pos_keep_set is not None and pos not in pos_keep_set:
                continue

            word = tok.base_form if (use_base_form and tok.base_form != "*") else tok.surface
            if not word or word in stopwords:
                continue

            if extra_col is None:
                records.append((doc_id, word, pos))
            else:
                info = {
                    "surface": tok.surface,
                    "base_form": tok.base_form,
                    "reading": tok.reading,
                    "phonetic": tok.phonetic,
                    "pos_detail": tok.part_of_speech,
                    "infl_type": tok.infl_type,
                    "infl_form": tok.infl_form,
                }
                records.append((doc_id, word, pos, info))

    columns = [id_col, "word", "pos"] + ([] if extra_col is None else [extra_col])
    return pd.DataFrame.from_records(records, columns=columns)


def tokenize_sudachi(
    df: pd.DataFrame,
    *,
    id_col: str = "article_id",
    text_col: str = "article",
    split_mode=None,
    dict_type: Optional[Union[str, "pathlib.Path"]] = "core",
    tokenizer=None,
    word_form: WordForm = "dictionary",
    pos_keep: Optional[Iterable[str]] = None,
    stopwords: Optional[set[str]] = None,
    extra_col: Optional[str] = "token_info",
) -> pd.DataFrame:
    # ★ここで Sudachi を遅延 import
    try:
        from sudachipy import Dictionary, SplitMode
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            "SudachiPy が未インストールです。Sudachi を使う場合は Colab で `!pip install sudachipy sudachidict_core` を実行してください。"
        ) from e

    if split_mode is None:
        split_mode = SplitMode.C

    for col in (id_col, text_col):
        if col not in df.columns:
            raise KeyError(f"required column '{col}' not found in df")

    stopwords = stopwords or set()
    pos_keep_set = set(pos_keep) if pos_keep is not None else None

    if tokenizer is None:
        dic = Dictionary(dict=dict_type)
        tokenizer = dic.create(mode=split_mode)

    def _word(m):
        if word_form == "surface":
            return m.surface()
        if word_form == "normalized":
            return m.normalized_form()
        return m.dictionary_form()

    records = []
    for doc_id, text in df[[id_col, text_col]].itertuples(index=False, name=None):
        if pd.isna(text):
            continue
        if not isinstance(text, str):
            text = str(text)

        for m in tokenizer.tokenize(text):
            pos_tuple = m.part_of_speech()
            pos = pos_tuple[0]
            if pos_keep_set is not None and pos not in pos_keep_set:
                continue

            w = _word(m)
            if not w or w in stopwords:
                continue

            if extra_col is None:
                records.append((doc_id, w, pos))
            else:
                info = {
                    "surface": m.surface(),
                    "dictionary_form": m.dictionary_form(),
                    "normalized_form": m.normalized_form(),
                    "reading_form": m.reading_form(),
                    "pos_detail": pos_tuple,
                    "begin": m.begin(),
                    "end": m.end(),
                    "is_oov": m.is_oov(),
                    "word_id": m.word_id(),
                    "dictionary_id": m.dictionary_id(),
                    "pos_id": m.part_of_speech_id(),
                }
                records.append((doc_id, w, pos, info))

    columns = [id_col, "word", "pos"] + ([] if extra_col is None else [extra_col])
    return pd.DataFrame.from_records(records, columns=columns)


def tokens_to_text(
    df: pd.DataFrame,
    *,
    pos_keep: Optional[Iterable[str]] = None,
) -> str:
    if pos_keep is None:
        return " ".join(df["word"].dropna().astype(str))
    if isinstance(pos_keep, str):
        pos_keep = (pos_keep,)
    return " ".join(df.query("pos in @pos_keep")["word"].dropna().astype(str))
