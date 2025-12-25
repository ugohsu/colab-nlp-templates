# ============================================================
# 前処理ユーティリティ（日本語トークナイズ）
# ------------------------------------------------------------
# 本モジュールが提供するもの
#   - tokenize_text_* : 1つのテキストをトークナイズ（高速経路。corpus_pass1 から直接呼べる）
#   - tokenize_df     : DataFrame をトークナイズ（engine 選択または callable 指定）
#
# 設計方針（重要）
#   - tokenize_df は「使いやすい入口」です（授業・小〜中規模向け）
#   - tokenizer の「使い回し（高速化）」は tokenize_text_fn に寄せます
#       -> Janome / Sudachi ともに、外部で tokenizer を作って tokenize_text_fn で注入できます
#   - 旧来 API の互換ラッパ（tokenize_janome / tokenize_sudachi）は廃止しました
# ============================================================

from __future__ import annotations

from typing import Any, Callable, Iterable, Literal, Optional, Union

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
    pos_exclude: Optional[Iterable[str]] = None,
    stopwords: Optional[set[str]] = None,
    extra_info: bool = True,
) -> list[TokenRecord]:
    """
    Janome で「1つのテキスト」をトークナイズします（高速経路）。

    大規模処理では、tokenizer を外で初期化して使い回すことを推奨します。

    Parameters
    ----------
    text:
        入力テキスト。str 以外は str に変換します。None/NaN は [] を返します。
    tokenizer:
        Janome Tokenizer（任意）。
        未指定なら内部で生成します（少量データ向け）。
    use_base_form:
        True の場合、原形（基本形）を使用します。
        False の場合、表層形（surface）を使用します。
    pos_keep:
        品詞フィルタ（任意）。指定した品詞（大分類）だけを残します（例: {"名詞","動詞"}）。
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
    pos_exclude_set = set(pos_exclude) if pos_exclude is not None else None

    out: list[TokenRecord] = []
    for tok in t.tokenize(text):
        pos = tok.part_of_speech.split(",")[0]
        if pos_keep_set is not None and pos not in pos_keep_set:
            continue
        if pos_exclude_set is not None and pos in pos_exclude_set:
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
    pos_exclude: Optional[Iterable[str]] = None,
    stopwords: Optional[set[str]] = None,
    extra_info: bool = True,
) -> list[TokenRecord]:
    """
    SudachiPy で「1つのテキスト」をトークナイズします（高速経路）。

    大規模処理では、tokenizer を外で初期化して使い回すことを推奨します。

    Parameters
    ----------
    text:
        入力テキスト。str 以外は str に変換します。None/NaN は [] を返します。
    tokenizer:
        Sudachi tokenizer（任意）。
        未指定なら内部で作成します（少量データ向け）。
    split_mode:
        分割モード（SplitMode.A / B / C）。未指定なら C。
    dict_type:
        Sudachi 辞書の種類。Colab では "core"（sudachidict_core）が定番です。
    word_form:
        トークンとして使用する語形（"surface" / "dictionary" / "normalized"）。
    pos_keep:
        品詞フィルタ（任意）。指定した品詞（大分類）だけを残します。
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
    pos_exclude_set = set(pos_exclude) if pos_exclude is not None else None

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
        if pos_exclude_set is not None and pos in pos_exclude_set:
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
# DataFrame tokenizer (入口)
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
    pos_exclude: Optional[Iterable[str]] = None,
    extra_col: Optional[str] = "token_info",
    # Janome 固有オプション（※tokenizer 注入は tokenize_text_fn に寄せる）
    use_base_form: bool = True,
    # Sudachi 固有オプション（※tokenizer 注入は tokenize_text_fn に寄せる）
    split_mode=None,
    dict_type: Optional[Union[str, "pathlib.Path"]] = "core",
    word_form: WordForm = "dictionary",
    # 追加の挙動
    extra_info: bool = True,
) -> pd.DataFrame:
    """
    DataFrame の特定列（text_col）をトークナイズし、「1行=1トークン」の縦持ち DataFrame を返します。

    - tokenize_text_fn を渡した場合：その callable を使用（tokenizer の使い回し等はここで実現）
    - tokenize_text_fn が None の場合：engine で "sudachi" / "janome" を選び、内部で tokenizer を 1回だけ初期化して使います

    Parameters
    ----------
    df:
        入力 DataFrame。
    id_col:
        文書ID列名（必須）。
    text_col:
        トークナイズ対象テキスト列名（必須）。
    engine:
        "sudachi" または "janome"。tokenize_text_fn が None のときのみ有効。
    tokenize_text_fn:
        1テキスト → TokenRecord のリストを返す関数。
        大規模処理で tokenizer を使い回したい場合は、ここで注入してください。
    stopwords:
        除外語（任意）。
    pos_keep:
        品詞フィルタ（任意）。
    extra_col:
        追加情報列名。None の場合、追加情報列を作りません（軽量化）。
    use_base_form:
        Janome の場合に原形（基本形）を使うかどうか。
    split_mode, dict_type, word_form:
        SudachiPy の設定。
    extra_info:
        True の場合、追加情報列に詳細 dict を入れます（便利だが重い）。
        extra_col=None の場合は自動的に無効化されます。

    Returns
    -------
    pd.DataFrame
        「1行=1トークン」の縦持ち DataFrame。
    """
    for col in (id_col, text_col):
        if col not in df.columns:
            raise KeyError(f"required column '{col}' not found in df")

    stopwords = stopwords or set()
    pos_keep_set = set(pos_keep) if pos_keep is not None else None
    pos_exclude_set = set(pos_exclude) if pos_exclude is not None else None
    # extra_col が無いなら info を作らない（無駄なので）
    want_info = bool(extra_info) and (extra_col is not None)

    # tokenize_text_fn が未指定なら engine からデフォルトを組み立てる（tokenizer は 1回だけ初期化して使い回す）
    if tokenize_text_fn is None:
        if engine == "janome":
            # JanomeTokenizer を 1回だけ作る
            try:
                from janome.tokenizer import Tokenizer as JanomeTokenizer
            except ModuleNotFoundError as e:
                raise ModuleNotFoundError(
                    "Janome が未インストールです。Janome を使う場合は Colab で `!pip install janome` を実行してください。"
                ) from e
            janome_tok = JanomeTokenizer()

            tokenize_text_fn = lambda x: tokenize_text_janome(
                x,
                tokenizer=janome_tok,
                use_base_form=use_base_form,
                pos_keep=pos_keep_set,
                pos_exclude=pos_exclude_set,
                stopwords=stopwords,
                extra_info=want_info,
            )
        elif engine == "sudachi":
            # Sudachi tokenizer を 1回だけ作る
            try:
                from sudachipy import Dictionary, SplitMode
            except ModuleNotFoundError as e:
                raise ModuleNotFoundError(
                    "SudachiPy が未インストールです。Sudachi を使う場合は Colab で `!pip install sudachipy sudachidict_core` を実行してください。"
                ) from e

            if split_mode is None:
                split_mode_eff = SplitMode.C
            else:
                split_mode_eff = split_mode

            dic = Dictionary(dict=dict_type)
            sudachi_tok = dic.create(mode=split_mode_eff)

            tokenize_text_fn = lambda x: tokenize_text_sudachi(
                x,
                tokenizer=sudachi_tok,
                split_mode=split_mode_eff,  # tokenize_text_sudachi 内部で使わないが、意味の一貫性のため渡す
                dict_type=dict_type,
                word_form=word_form,
                pos_keep=pos_keep_set,
                pos_exclude=pos_exclude_set,
                stopwords=stopwords,
                extra_info=want_info,
            )
        else:
            raise ValueError("engine must be 'sudachi' or 'janome'")

    records: list[tuple[Any, str, str, Optional[dict[str, Any]]]] = []
    for doc_id, text in df[[id_col, text_col]].itertuples(index=False, name=None):
        if text is None or (isinstance(text, float) and pd.isna(text)):
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
# ヘルパー
# ============================================================

def tokens_to_text(
    df: pd.DataFrame,
    *,
    pos_keep: Optional[Iterable[str]] = None,
    pos_exclude: Optional[Iterable[str]] = None,
) -> str:
    """
    形態素解析結果（縦持ち DataFrame）を、スペース区切りの文字列に戻します。

    WordCloud 等で「トークン列→文字列」が必要なときに使います。
    """
    if "word" not in df.columns or "pos" not in df.columns:
        raise KeyError("df must have 'word' and 'pos' columns")

    s = df

    # 先に pos_keep（許可リスト）を適用
    if pos_keep is not None:
        if isinstance(pos_keep, str):
            pos_keep = (pos_keep,)
        s = s[s["pos"].isin(list(pos_keep))]

    # 次に pos_exclude（拒否リスト）を適用（pos_keep と併用可）
    if pos_exclude is not None:
        if isinstance(pos_exclude, str):
            pos_exclude = (pos_exclude,)
        s = s[~s["pos"].isin(list(pos_exclude))]

    return " ".join(s["word"].dropna().astype(str))
