# ============================================================
# 前処理ユーティリティ（日本語トークナイズ）
# ------------------------------------------------------------
# 本モジュールが提供するもの
#   - tokenize_text_* : 1つのテキストをトークナイズ（高速経路。corpus_pass1 から直接呼べる）
#   - tokenize_df     : DataFrame をトークナイズ（engine 選択または callable 指定）
#
# 対応エンジン（いずれも任意）
#   - Janome
#   - SudachiPy
# ============================================================

from __future__ import annotations

from typing import Any, Callable, Iterable, Iterator, Literal, Optional, Union

import pandas as pd

WordForm = Literal["surface", "dictionary", "normalized"]

# tokenize_text_* が返すトークンレコードの型：
#   (word, pos, info)
TokenRecord = tuple[str, str, Optional[dict[str, Any]]]


# ============================================================
# 1テキスト用トークナイザ（高速経路）
# ============================================================

def tokenize_text_janome(
    text: Any,
    *,
    tokenizer=None,
    use_base_form: bool = True,
    pos_keep: Optional[Iterable[str]] = None,
    stopwords: Optional[set[str]] = None,
    extra_info: bool = False,
) -> list[TokenRecord]:
    """
    Janome で「1つのテキスト」をトークナイズします（高速経路）。

    Parameters
    ----------
    text:
        入力テキスト。str 以外は str に変換します。None/NaN は [] を返します。
    tokenizer:
        Janome Tokenizer（任意）。未指定なら内部で 1回だけ生成して使います。
    use_base_form:
        True の場合、原形（基本形）を使用します。
    pos_keep:
        品詞フィルタ（任意）。指定した品詞だけを残します（例: {"名詞","動詞"}）。
    stopwords:
        除外語（任意）。一致したトークンは除外します。
    extra_info:
        True の場合、(word, pos, info) の info に詳細（辞書）を入れます。
        False の場合は info=None になります（軽量）。

    Returns
    -------
    list[TokenRecord]
        (word, pos, info_or_None) のリスト。
    """
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return []
    if not isinstance(text, str):
        text = str(text)

    # 遅延 import（必要なときだけ読み込む）
    try:
        from janome.tokenizer import Tokenizer as JanomeTokenizer
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            "Janome が未インストールです。Janome を使う場合は Colab で `!pip install janome` を実行してください。"
        ) from e

    t = tokenizer or JanomeTokenizer()
    stopwords = stopwords or set()
    pos_keep_set = set(pos_keep) if pos_keep is not None else None

    out: list[TokenRecord] = []
    for tok in t.tokenize(text):
        pos = tok.part_of_speech.split(",")[0]
        if pos_keep_set is not None and pos not in pos_keep_set:
            continue

        word = tok.base_form if use_base_form else tok.surface
        if not word or word in stopwords:
            continue

        if extra_info:
            info = {
                "surface": tok.surface,
                "base_form": tok.base_form,
                "reading": tok.reading,
                "phonetic": tok.phonetic,
                "pos_detail": tok.part_of_speech,
                "infl_type": tok.infl_type,
                "infl_form": tok.infl_form,
            }
        else:
            info = None

        out.append((word, pos, info))
    return out


def tokenize_text_sudachi(
    text: Any,
    *,
    split_mode=None,
    dict_type: Optional[Union[str, "pathlib.Path"]] = "core",
    tokenizer=None,
    word_form: WordForm = "dictionary",
    pos_keep: Optional[Iterable[str]] = None,
    stopwords: Optional[set[str]] = None,
    extra_info: bool = False,
) -> list[TokenRecord]:
    """
    SudachiPy で「1つのテキスト」をトークナイズします（高速経路）。

    Parameters
    ----------
    text:
        入力テキスト。str 以外は str に変換します。None/NaN は [] を返します。
    tokenizer:
        Sudachi tokenizer（任意）。未指定なら内部で作成しますが、
        大規模処理では tokenizer を外から渡して「使い回す」ことを推奨します。
    mode:
        分割モード ("A"|"B"|"C")。デフォルトは "C"。
    use_dictionary_form:
        True の場合、辞書形（原形）を使用します。False の場合は表層形です。
    pos_keep:
        品詞フィルタ（任意）。指定した品詞だけを残します。
    stopwords:
        除外語（任意）。
    extra_info:
        True の場合、(word, pos, info) の info に詳細（辞書）を入れます。
        False の場合は info=None になります（軽量）。

    Returns
    -------
    list[TokenRecord]
        (word, pos, info_or_None) のリスト。
    """
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return []
    if not isinstance(text, str):
        text = str(text)

    # 遅延 import（必要なときだけ読み込む）
    try:
        from sudachipy import Dictionary, SplitMode
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            "SudachiPy が未インストールです。Sudachi を使う場合は Colab で `!pip install sudachipy sudachidict_core` を実行してください。"
        ) from e

    if split_mode is None:
        split_mode = SplitMode.C

    stopwords = stopwords or set()
    pos_keep_set = set(pos_keep) if pos_keep is not None else None

    if tokenizer is None:
        dic = Dictionary(dict=dict_type)
        tokenizer = dic.create(mode=split_mode)

    def _word(m) -> str:
        if word_form == "surface":
            return m.surface()
        if word_form == "normalized":
            return m.normalized_form()
        return m.dictionary_form()

    out: list[TokenRecord] = []
    for m in tokenizer.tokenize(text):
        pos_tuple = m.part_of_speech()
        pos = pos_tuple[0]
        if pos_keep_set is not None and pos not in pos_keep_set:
            continue

        w = _word(m)
        if not w or w in stopwords:
            continue

        if extra_info:
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
        else:
            info = None

        out.append((w, pos, info))
    return out


# ============================================================
# DataFrame tokenizer (strategy selector)
# ============================================================

def tokenize_df(
    df: pd.DataFrame,
    *,
    id_col: str = "article_id",
    text_col: str = "article",
    engine: Literal["sudachi", "janome"] = "sudachi",
    tokenize_text_fn: Optional[Callable[[Any], list[TokenRecord]]] = None,
    # 共通オプション
    stopwords: Optional[set[str]] = None,
    pos_keep: Optional[Iterable[str]] = None,
    extra_col: Optional[str] = "token_info",
    # Janome 固有オプション
    tokenizer=None,
    use_base_form: bool = True,
    # Sudachi 固有オプション
    split_mode=None,
    dict_type: Optional[Union[str, "pathlib.Path"]] = "core",
    word_form: WordForm = "dictionary",
    # 追加の挙動
    extra_info: bool = False,
) -> pd.DataFrame:
    """
    DataFrame の特定列（text_col）をトークナイズし、結果を out_col に追加して返します。

    - tokenize_text_fn を渡した場合：その callable をそのまま使用（最も柔軟）
    - tokenize_text_fn が None の場合：engine で "sudachi" / "janome" を選びます

    Parameters
    ----------
    df:
        入力 DataFrame。
    id_col:
        文書ID列（出力の整形に使う場合があります。基本は存在チェックのみ）。
    text_col:
        トークナイズ対象のテキスト列名。
    out_col:
        追加する列名（トークン列）。
    engine:
        "sudachi" または "janome"。tokenize_text_fn が None のときのみ有効。
    tokenize_text_fn:
        1テキスト → TokenRecord のリスト（または str のリスト）を返す関数。
        例: lambda t: [w for (w, _, _) in tokenize_text_sudachi(t, tokenizer=tok)]
    return_records:
        True の場合、out_col には TokenRecord（タプル）を入れます。
        False の場合、out_col には word（文字列）だけの list を入れます。
    kwargs:
        tokenize_text_fn / エンジン側の設定を渡します。

    Returns
    -------
    pd.DataFrame
        out_col を追加した DataFrame（コピーを返します）。
    """
    for col in (id_col, text_col):
        if col not in df.columns:
            raise KeyError(f"required column '{col}' not found in df")

    # tokenize_text_fn が未指定なら engine からデフォルトを組み立てる
    if tokenize_text_fn is None:
        if engine == "janome":
            tokenize_text_fn = lambda x: tokenize_text_janome(
                x,
                tokenizer=tokenizer,
                use_base_form=use_base_form,
                pos_keep=pos_keep,
                stopwords=stopwords,
                extra_info=extra_info if extra_col is not None else False,
            )
        elif engine == "sudachi":
            tokenize_text_fn = lambda x: tokenize_text_sudachi(
                x,
                split_mode=split_mode,
                dict_type=dict_type,
                tokenizer=tokenizer,
                word_form=word_form,
                pos_keep=pos_keep,
                stopwords=stopwords,
                extra_info=extra_info if extra_col is not None else False,
            )
        else:
            raise ValueError("engine must be 'sudachi' or 'janome'")

    records: list[tuple[Any, str, str, Optional[dict[str, Any]]]] = []
    for doc_id, text in df[[id_col, text_col]].itertuples(index=False, name=None):
        if pd.isna(text):
            continue
        for word, pos, info in tokenize_text_fn(text):
            if extra_col is None:
                records.append((doc_id, word, pos, None))
            else:
                records.append((doc_id, word, pos, info))

    if extra_col is None:
        columns = [id_col, "word", "pos"]
        out = [(a, b, c) for (a, b, c, _) in records]
        return pd.DataFrame.from_records(out, columns=columns)

    columns = [id_col, "word", "pos", extra_col]
    return pd.DataFrame.from_records(records, columns=columns)


# ============================================================
# 互換ラッパ（従来 API）
# ============================================================

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
    """
    （互換ラッパ）Janome による df トークナイズ。

    従来の API を保つためのラッパです。内部では tokenize_df を呼びます。
    """
    return tokenize_df(
        df,
        id_col=id_col,
        text_col=text_col,
        engine="janome",
        tokenizer=tokenizer,
        use_base_form=use_base_form,
        pos_keep=pos_keep,
        stopwords=stopwords,
        extra_col=extra_col,
        extra_info=True if extra_col is not None else False,
    )


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
    """
    （互換ラッパ）SudachiPy による df トークナイズ。

    従来の API を保つためのラッパです。内部では tokenize_df を呼びます。
    """
    return tokenize_df(
        df,
        id_col=id_col,
        text_col=text_col,
        engine="sudachi",
        tokenizer=tokenizer,
        split_mode=split_mode,
        dict_type=dict_type,
        word_form=word_form,
        pos_keep=pos_keep,
        stopwords=stopwords,
        extra_col=extra_col,
        extra_info=True if extra_col is not None else False,
    )


# ============================================================
# ヘルパー
# ============================================================

def tokens_to_text(
    df: pd.DataFrame,
    *,
    pos_keep: Optional[Iterable[str]] = None,
) -> str:
    """
    形態素解析結果（tokens 列）を、スペース区切りの文字列に戻します。

    wordcloud 等で「トークン列→文字列」が必要なときに使います。
    """
    if pos_keep is None:
        return " ".join(df["word"].dropna().astype(str))
    if isinstance(pos_keep, str):
        pos_keep = (pos_keep,)
    return " ".join(df.query("pos in @pos_keep")["word"].dropna().astype(str))
