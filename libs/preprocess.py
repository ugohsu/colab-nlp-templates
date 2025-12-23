# ============================================================
# Preprocessing utilities (Japanese tokenization)
# - Janome
# - SudachiPy
# ============================================================

from __future__ import annotations

from typing import Iterable, Optional, Literal, Union

import pandas as pd

from janome.tokenizer import Tokenizer as JanomeTokenizer
from sudachipy import Dictionary, SplitMode


# ------------------------------------------------------------
# Sudachi: word_form の選択肢（トークンとしてどの「語形」を使うか）
# ------------------------------------------------------------
# "surface"     : 表層形（文章に実際に出てきた形）
# "dictionary"  : 辞書形（基本形に寄せる。動詞などで揺れが減る）
# "normalized"  : 正規化形（表記ゆれ吸収に強い）
WordForm = Literal["surface", "dictionary", "normalized"]


def tokenize_janome(
    df: pd.DataFrame,
    *,
    id_col: str = "article_id",
    text_col: str = "article",
    tokenizer: Optional[JanomeTokenizer] = None,
    use_base_form: bool = True,
    pos_keep: Optional[Iterable[str]] = None,
    stopwords: Optional[set[str]] = None,
    extra_col: Optional[str] = "token_info",
) -> pd.DataFrame:
    """
    DataFrame に含まれる日本語テキストを Janome で形態素解析し、
    「1行 = 1トークン」の縦持ち DataFrame を返す関数。

    【前提】
    - df は id_col（文書ID）と text_col（本文）を必ず含む
    - 文書単位の分析（LDA / tf-idf 等）を想定し、ID 列は必須とする

    【出力形式】
    columns = [id_col, "word", "pos"] (+ extra_col)

    extra_col が指定されている場合、
    Janome Token が持つ補足情報を dict として格納する。
    """

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

            word = (
                tok.base_form
                if (use_base_form and tok.base_form != "*")
                else tok.surface
            )

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

    columns = [id_col, "word", "pos"] + (
        [] if extra_col is None else [extra_col]
    )

    return pd.DataFrame.from_records(records, columns=columns)


def tokenize_sudachi(
    df: pd.DataFrame,
    *,
    id_col: str = "article_id",
    text_col: str = "article",
    split_mode: Union[SplitMode, str] = SplitMode.C,
    dict_type: Optional[Union[str, "pathlib.Path"]] = "core",
    tokenizer=None,
    word_form: WordForm = "dictionary",
    pos_keep: Optional[Iterable[str]] = None,
    stopwords: Optional[set[str]] = None,
    extra_col: Optional[str] = "token_info",
) -> pd.DataFrame:
    """
    DataFrame に含まれる日本語テキストを SudachiPy で形態素解析し、
    「1行 = 1トークン」の縦持ち DataFrame を返す関数（文書ID必須）。

    【前提】
    - df は id_col（文書ID）と text_col（本文）を必ず含む
    - 文書単位の分析（LDA / tf-idf 等）を想定し、ID 列は必須とする

    【出力形式】
    columns = [id_col, "word", "pos"] (+ extra_col)

    【Sudachi 特有のポイント】
    - split_mode（A/B/C）で分割粒度を指定できる
        A: 最も細かい
        B: 中間
        C: 最も粗い（複合語をまとめやすい）
    - word_form（surface / dictionary / normalized）を選べる
    - extra_col には Morpheme 由来の補足情報を dict で格納できる
    """

    for col in (id_col, text_col):
        if col not in df.columns:
            raise KeyError(f"required column '{col}' not found in df")

    stopwords = stopwords or set()
    pos_keep_set = set(pos_keep) if pos_keep is not None else None

    if tokenizer is None:
        dic = Dictionary(dict=dict_type)
        tokenizer = dic.create(mode=split_mode)
    else:
        pass

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

        morphemes = tokenizer.tokenize(text)

        for m in morphemes:
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
