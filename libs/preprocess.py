"""
前処理（形態素解析）ユーティリティ

- Janome / SudachiPy を共通 API で扱う
- use_base_form を共通オプションとして提供
    - Janome  : 表層形 / 原形
    - Sudachi : 表層形 / 辞書形
- Sudachi の normalized_form を使いたい場合は tokenize_text_fn で拡張
- 品詞フィルタは tokenize 後に filter_tokens_df で探索的に調整可能
"""

from typing import Callable, Iterable, Optional, Sequence, Tuple, List, Dict, Any
import pandas as pd


# ----------------------------------------------------------------------
# 内部ユーティリティ
# ----------------------------------------------------------------------

def _compile_pos_filter(
    pos_keep: Optional[Iterable[str]],
    pos_exclude: Optional[Iterable[str]],
    *,
    strict: bool = True,
) -> Tuple[Optional[set], Optional[set]]:
    """
    pos_keep / pos_exclude を set に正規化し、矛盾を検査する
    """
    keep_set = set(pos_keep) if pos_keep else None
    excl_set = set(pos_exclude) if pos_exclude else None

    if strict and keep_set and excl_set:
        if keep_set.isdisjoint(excl_set):
            raise ValueError(
                "pos_keep と pos_exclude が同時指定されていますが、"
                "両者に交差がありません。指定ミスの可能性があります。"
            )

    return keep_set, excl_set


# ----------------------------------------------------------------------
# 公開ユーティリティ（tokenize 後の操作）
# ----------------------------------------------------------------------

def filter_tokens_df(
    df: pd.DataFrame,
    *,
    pos_keep: Optional[Iterable[str]] = None,
    pos_exclude: Optional[Iterable[str]] = None,
    strict: bool = True,
) -> pd.DataFrame:
    """
    tokenize 後の DataFrame に対して品詞フィルタを適用する

    Parameters
    ----------
    df : pandas.DataFrame
        tokenize_df の出力（pos 列を含む）
    pos_keep : iterable[str], optional
        残す品詞（大分類）
    pos_exclude : iterable[str], optional
        除外する品詞（大分類）
    strict : bool, default True
        keep / exclude の同時指定時に矛盾を検出するか

    Returns
    -------
    pandas.DataFrame
    """
    if "pos" not in df.columns:
        raise KeyError("filter_tokens_df: DataFrame に 'pos' 列がありません")

    keep_set, excl_set = _compile_pos_filter(
        pos_keep=pos_keep,
        pos_exclude=pos_exclude,
        strict=strict,
    )

    s = df
    if keep_set is not None:
        s = s[s["pos"].isin(keep_set)]
    if excl_set is not None:
        s = s[~s["pos"].isin(excl_set)]

    return s.reset_index(drop=True)


# ----------------------------------------------------------------------
# 1 テキスト用 tokenizer（Janome）
# ----------------------------------------------------------------------

def tokenize_text_janome(
    text: str,
    *,
    tokenizer,
    use_base_form: bool = True,
    extra_col: Optional[str] = "token_info",
) -> List[Tuple[str, str, Optional[Dict[str, Any]]]]:
    """
    Janome による 1 テキスト分のトークナイズ
    """
    if text is None:
        return []

    s = str(text).strip()
    if s == "":
        return []

    records = []
    for token in tokenizer.tokenize(s):
        word = token.base_form if use_base_form else token.surface
        pos = token.part_of_speech.split(",")[0]

        token_info = None
        if extra_col is not None:
            token_info = {
                "surface": token.surface,
                "base_form": token.base_form,
                "reading": token.reading,
            }

        records.append((word, pos, token_info))

    return records


# ----------------------------------------------------------------------
# 1 テキスト用 tokenizer（Sudachi）
# ----------------------------------------------------------------------

def tokenize_text_sudachi(
    text: str,
    *,
    tokenizer,
    split_mode: str = "C",
    use_base_form: bool = True,
    extra_col: Optional[str] = "token_info",
) -> List[Tuple[str, str, Optional[Dict[str, Any]]]]:
    """
    SudachiPy による 1 テキスト分のトークナイズ
    """
    if text is None:
        return []

    s = str(text).strip()
    if s == "":
        return []

    mode_map = {
        "A": tokenizer.SplitMode.A,
        "B": tokenizer.SplitMode.B,
        "C": tokenizer.SplitMode.C,
    }
    mode = mode_map.get(split_mode, tokenizer.SplitMode.C)

    records = []
    for m in tokenizer.tokenize(s, mode):
        word = m.dictionary_form() if use_base_form else m.surface()
        pos = m.part_of_speech()[0]

        token_info = None
        if extra_col is not None:
            token_info = {
                "surface": m.surface(),
                "dictionary_form": m.dictionary_form(),
                "normalized_form": m.normalized_form(),
            }

        records.append((word, pos, token_info))

    return records


# ----------------------------------------------------------------------
# DataFrame 用 tokenizer（入口）
# ----------------------------------------------------------------------

def tokenize_df(
    df: pd.DataFrame,
    *,
    id_col: str = "article_id",
    text_col: str = "article",
    engine: str = "sudachi",
    tokenizer=None,
    tokenize_text_fn: Optional[Callable[[str], List[Tuple[str, str, Any]]]] = None,
    split_mode: str = "C",
    use_base_form: bool = True,
    pos_keep: Optional[Iterable[str]] = None,
    pos_exclude: Optional[Iterable[str]] = None,
    stopwords: Optional[Iterable[str]] = None,
    extra_col: Optional[str] = "token_info",
) -> pd.DataFrame:
    """
    テキスト DataFrame を縦持ち token DataFrame に変換する
    """
    records = []

    # 入力チェック（列名ミスを早期に検出）
    if id_col not in df.columns:
        raise KeyError(
            f"tokenize_df: DataFrame に id_col={id_col!r} 列がありません。"
            f"存在する列: {list(df.columns)}"
        )
    if text_col not in df.columns:
        raise KeyError(
            f"tokenize_df: DataFrame に text_col={text_col!r} 列がありません。"
            f"存在する列: {list(df.columns)}"
        )

    # tokenize_text_fn が与えられていればそれを最優先
    if tokenize_text_fn is None:
        if engine == "janome":
            if tokenizer is None:
                from janome.tokenizer import Tokenizer
                tokenizer = Tokenizer()
            tokenize_text_fn = lambda t: tokenize_text_janome(
                t,
                tokenizer=tokenizer,
                use_base_form=use_base_form,
                extra_col=extra_col,
            )

        elif engine == "sudachi":
            if tokenizer is None:
                from sudachipy import dictionary
                tokenizer = dictionary.Dictionary().create()
            tokenize_text_fn = lambda t: tokenize_text_sudachi(
                t,
                tokenizer=tokenizer,
                split_mode=split_mode,
                use_base_form=use_base_form,
                extra_col=extra_col,
            )
        else:
            raise ValueError(f"Unknown engine: {engine}")

    for _, row in df.iterrows():
        doc_id = row[id_col]
        text = row[text_col]

        tokens = tokenize_text_fn(text)
        for word, pos, token_info in tokens:
            records.append(
                {
                    id_col: doc_id,
                    "word": word,
                    "pos": pos,
                    extra_col: token_info if extra_col else None,
                }
            )

    out = pd.DataFrame(records)

    # stopwords
    if stopwords is not None:
        out = out[~out["word"].isin(set(stopwords))]

    # pos filter
    out = filter_tokens_df(
        out,
        pos_keep=pos_keep,
        pos_exclude=pos_exclude,
        strict=True,
    )

    return out.reset_index(drop=True)


# ----------------------------------------------------------------------
# token -> text（再結合）
# ----------------------------------------------------------------------

def tokens_to_text(
    df: pd.DataFrame,
    *,
    id_col: str = "article_id",
    word_col: str = "word",
    sep: str = " ",
    pos_keep: Optional[Iterable[str]] = None,
    pos_exclude: Optional[Iterable[str]] = None,
    strict: bool = True,
) -> pd.DataFrame:
    """
    token DataFrame を文書単位の text に戻す
    """
    s = filter_tokens_df(
        df,
        pos_keep=pos_keep,
        pos_exclude=pos_exclude,
        strict=strict,
    )

    text_df = (
        s.groupby(id_col)[word_col]
        .apply(lambda xs: sep.join(xs))
        .reset_index(name="text")
    )

    return text_df


__all__ = [
    "tokenize_df",
    "tokenize_text_janome",
    "tokenize_text_sudachi",
    "filter_tokens_df",
    "tokens_to_text",
]
