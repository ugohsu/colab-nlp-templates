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
#   - pos フィルタ（pos_keep / pos_exclude）のロジックは内部関数に集約します
# ============================================================

from __future__ import annotations

from typing import Any, Callable, Iterable, Literal, Optional

import math
import pandas as pd

__all__ = [
    "tokenize_text_janome",
    "tokenize_text_sudachi",
    "tokenize_df",
    "filter_tokens_df",
    "tokens_to_text",
]

# tokenize_text_* が返すトークンレコードの型：
#   (word, pos, info)
TokenRecord = tuple[str, str, Optional[dict[str, Any]]]


# ============================================================
# 内部ユーティリティ
# ============================================================

def _is_nan(x: Any) -> bool:
    try:
        return x is None or (isinstance(x, float) and math.isnan(x))
    except Exception:
        return x is None


def _normalize_stopwords(stopwords: Optional[Iterable[str]]) -> set[str]:
    """
    stopwords を set[str] に正規化します。
    - None -> empty set
    - 文字列単体 -> {that}
    - list/tuple/set -> set(...)
    """
    if stopwords is None:
        return set()
    if isinstance(stopwords, str):
        return {stopwords}
    return set(stopwords)


def _normalize_pos_list(pos_list: Optional[Iterable[str]]) -> Optional[set[str]]:
    """
    品詞リスト（pos_keep / pos_exclude）を set[str] に正規化します。
    - None -> None
    - 文字列単体 -> {that}
    - list/tuple/set -> set(...)
    """
    if pos_list is None:
        return None
    if isinstance(pos_list, str):
        return {pos_list}
    return set(pos_list)


def _compile_pos_filter(
    *,
    pos_keep: Optional[Iterable[str]],
    pos_exclude: Optional[Iterable[str]],
    strict: bool = True,
) -> tuple[Optional[set[str]], Optional[set[str]]]:
    """
    pos_keep / pos_exclude を正規化し、矛盾・無意味な指定を検知します。

    仕様
    ----
    - 判定順は keep -> exclude（併用可）
    - ただし、pos_keep と pos_exclude が両方指定されていて
      かつ pos_keep と pos_exclude が「完全に無関係（交差が空）」の場合は、
      exclude が絶対に効かないため、strict=True では ValueError を投げます。

      例:
        keep = {"名詞"} / exclude = {"空白", "補助記号"}
        -> exclude は keep の後には絶対に現れないので、指定ミスの可能性が高い
    """
    keep_set = _normalize_pos_list(pos_keep)
    excl_set = _normalize_pos_list(pos_exclude)

    if strict and keep_set is not None and excl_set is not None:
        if keep_set.isdisjoint(excl_set):
            raise ValueError(
                "pos_keep と pos_exclude が同時指定されていますが、交差が空です。"
                "（pos_exclude はこの設定では一切効きません）\n"
                f"pos_keep={sorted(keep_set)}\n"
                f"pos_exclude={sorted(excl_set)}"
            )

    return keep_set, excl_set


def _pos_allowed(pos: str, keep_set: Optional[set[str]], excl_set: Optional[set[str]]) -> bool:
    """
    品詞フィルタ判定（keep -> exclude）。
    """
    if keep_set is not None and pos not in keep_set:
        return False
    if excl_set is not None and pos in excl_set:
        return False
    return True


def filter_tokens_df(
    df: pd.DataFrame,
    *,
    pos_keep: Optional[Iterable[str]] = None,
    pos_exclude: Optional[Iterable[str]] = None,
    strict: bool = True,
) -> pd.DataFrame:
    """
    トークン DataFrame（'pos' 列を持つ）に対して、pos_keep / pos_exclude を適用して返します。

    使いどころ
    ----------
    tokenize_df で一度トークン DataFrame を作った後に、
    品詞フィルタを試行錯誤しながら適用したい場合に便利です。

    仕様
    ----
    - 判定順は keep -> exclude
    - strict=True（既定）の場合、pos_keep と pos_exclude を同時指定していて
      かつ交差が空（exclude が絶対に効かない）なら ValueError を投げます。
      探索的に試したい場合は strict=False を指定してください。
    """
    if "pos" not in df.columns:
        raise KeyError("df must have 'pos' column")

    keep_set, excl_set = _compile_pos_filter(pos_keep=pos_keep, pos_exclude=pos_exclude, strict=strict)

    s = df
    if keep_set is not None:
        s = s[s["pos"].isin(keep_set)]
    if excl_set is not None:
        s = s[~s["pos"].isin(excl_set)]
    return s


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
    stopwords: Optional[Iterable[str]] = None,
    extra_info: bool = True,
) -> list[TokenRecord]:
    """
    Janome で「1つのテキスト」をトークナイズします（高速経路）。

    Parameters
    ----------
    text:
        入力テキスト。str 以外は str に変換します。None/NaN は [] を返します。
    tokenizer:
        Janome の Tokenizer インスタンス（任意）。
        大規模処理では、外部で tokenizer を初期化して使い回すことを推奨します。
    use_base_form:
        True の場合、原型（基本形）を word として採用します。
    pos_keep:
        品詞フィルタ（任意）。指定した品詞（大分類）のみを残します。
    pos_exclude:
        品詞フィルタ（任意）。指定した品詞（大分類）を除外します。
        pos_keep と併用する場合は「keep -> exclude」の順で適用されます。
    stopwords:
        除外したい語の集合（任意）。word が stopwords に含まれる場合は除外します。
    extra_info:
        True の場合、token_info（辞書）を各トークンに付与します。
        False の場合は token_info を None にします（軽量）。

    Returns
    -------
    list[TokenRecord]
        (word, pos, token_info) のリスト
    """
    if _is_nan(text):
        return []

    s = str(text).strip()
    if s == "":
        return []

    keep_set, excl_set = _compile_pos_filter(pos_keep=pos_keep, pos_exclude=pos_exclude)
    sw = _normalize_stopwords(stopwords)

    if tokenizer is None:
        from janome.tokenizer import Tokenizer
        tokenizer = Tokenizer()

    out: list[TokenRecord] = []
    for t in tokenizer.tokenize(s):
        # Janome: part_of_speech = "名詞,一般,*,*"
        pos_major = (t.part_of_speech.split(",")[0] if t.part_of_speech else "")

        if not _pos_allowed(pos_major, keep_set, excl_set):
            continue

        word = t.base_form if use_base_form else t.surface
        if not word:
            continue
        if word in sw:
            continue

        info = None
        if extra_info:
            info = {
                "surface": t.surface,
                "base_form": t.base_form,
                "pos": t.part_of_speech,
                "reading": t.reading,
                "phonetic": t.phonetic,
            }

        out.append((word, pos_major, info))

    return out


def tokenize_text_sudachi(
    text: Any,
    *,
    tokenizer=None,
    split_mode: str = "C",
    use_base_form: bool = True,
    pos_keep: Optional[Iterable[str]] = None,
    pos_exclude: Optional[Iterable[str]] = None,
    stopwords: Optional[Iterable[str]] = None,
    extra_info: bool = True,
) -> list[TokenRecord]:
    """
    SudachiPy で「1つのテキスト」をトークナイズします（高速経路）。

    Parameters
    ----------
    text:
        入力テキスト。str 以外は str に変換します。None/NaN は [] を返します。
    tokenizer:
        SudachiPy の Tokenizer インスタンス（任意）。
        大規模処理では、外部で tokenizer を初期化して使い回すことを推奨します。
    split_mode:
        分割モード。"A" / "B" / "C"（既定 "C"）。
    use_base_form:
        True の場合、原型（辞書形）を word として採用します。
    pos_keep / pos_exclude / stopwords / extra_info:
        tokenize_text_janome と同様。

    Returns
    -------
    list[TokenRecord]
        (word, pos, token_info) のリスト
    """
    if _is_nan(text):
        return []

    s = str(text).strip()
    if s == "":
        return []

    keep_set, excl_set = _compile_pos_filter(pos_keep=pos_keep, pos_exclude=pos_exclude)
    sw = _normalize_stopwords(stopwords)

    if tokenizer is None:
        from sudachipy import dictionary
        tokenizer = dictionary.Dictionary().create()

    # split_mode
    from sudachipy import tokenizer as sudachi_tokenizer
    mode = {
        "A": sudachi_tokenizer.Tokenizer.SplitMode.A,
        "B": sudachi_tokenizer.Tokenizer.SplitMode.B,
        "C": sudachi_tokenizer.Tokenizer.SplitMode.C,
    }.get(str(split_mode).upper(), sudachi_tokenizer.Tokenizer.SplitMode.C)

    out: list[TokenRecord] = []
    for m in tokenizer.tokenize(s, mode):
        pos = m.part_of_speech()
        # Sudachi: ("名詞","普通名詞","一般","*","*","*")
        pos_major = pos[0] if pos else ""

        if not _pos_allowed(pos_major, keep_set, excl_set):
            continue

        word = m.dictionary_form() if use_base_form else m.surface()
        if not word:
            continue
        if word in sw:
            continue

        info = None
        if extra_info:
            info = {
                "surface": m.surface(),
                "dictionary_form": m.dictionary_form(),
                "normalized_form": m.normalized_form(),
                "pos": pos,
                "reading_form": m.reading_form(),
            }

        out.append((word, pos_major, info))

    return out


# ============================================================
# DataFrame 用（入口）
# ============================================================

def tokenize_df(
    df: pd.DataFrame,
    *,
    id_col: str = "article_id",
    text_col: str = "article",
    engine: Literal["sudachi", "janome"] = "sudachi",
    tokenize_text_fn: Optional[Callable[[Any], list[TokenRecord]]] = None,
    # 共通オプション
    stopwords: Optional[Iterable[str]] = None,
    pos_keep: Optional[Iterable[str]] = None,
    pos_exclude: Optional[Iterable[str]] = None,
    extra_col: Optional[str] = "token_info",
    # Janome 固有オプション（tokenizer 注入は tokenize_text_fn に寄せる）
    use_base_form: bool = True,
    # Sudachi 固有オプション（tokenizer 注入は tokenize_text_fn に寄せる）
    split_mode: str = "C",
) -> pd.DataFrame:
    """
    DataFrame をトークナイズして、「1行=1トークン」の縦持ち DataFrame を返します。

    Parameters
    ----------
    df:
        入力 DataFrame。
    id_col:
        文書ID列名（既定 "article_id"）。
    text_col:
        文書テキスト列名（既定 "article"）。
    engine:
        "sudachi" または "janome"。
    tokenize_text_fn:
        「1テキスト -> list[TokenRecord]」の関数。
        指定した場合は engine より優先して使用します。
        tokenizer の使い回し（高速化）をしたい場合は、外部で tokenizer を作り、
        それを閉じ込めた tokenize_text_fn を渡してください。

    stopwords:
        除外したい語の集合（任意）。
    pos_keep:
        品詞フィルタ（任意）。指定した品詞（大分類）のみを残します。
    pos_exclude:
        品詞フィルタ（任意）。指定した品詞（大分類）を除外します。
        pos_keep と併用する場合は「keep -> exclude」の順で適用されます。
        ただし、pos_keep と pos_exclude の交差が空（exclude が絶対に効かない）場合は
        指定ミスの可能性が高いため ValueError を投げます。
    extra_col:
        token_info を格納する列名。None の場合は token_info を出力しません。

    use_base_form:
        Janome / Sudachi で原型を使うかどうか（既定 True）。
    split_mode:
        Sudachi の分割モード（既定 "C"）。

    Returns
    -------
    pd.DataFrame
        columns: [id_col, "word", "pos", extra_col?]
    """
    for col in (id_col, text_col):
        if col not in df.columns:
            raise KeyError(f"required column '{col}' not found in df")

    # compile filters once (also validates settings)
    keep_set, excl_set = _compile_pos_filter(pos_keep=pos_keep, pos_exclude=pos_exclude)
    sw = _normalize_stopwords(stopwords)

    # テキスト1本のトークナイズ関数を決定
    if tokenize_text_fn is None:
        if engine == "janome":
            def tokenize_text_fn(x: Any) -> list[TokenRecord]:
                return tokenize_text_janome(
                    x,
                    tokenizer=None,
                    use_base_form=use_base_form,
                    pos_keep=keep_set,
                    pos_exclude=excl_set,
                    stopwords=sw,
                    extra_info=(extra_col is not None),
                )
        elif engine == "sudachi":
            def tokenize_text_fn(x: Any) -> list[TokenRecord]:
                return tokenize_text_sudachi(
                    x,
                    tokenizer=None,
                    split_mode=split_mode,
                    use_base_form=use_base_form,
                    pos_keep=keep_set,
                    pos_exclude=excl_set,
                    stopwords=sw,
                    extra_info=(extra_col is not None),
                )
        else:
            raise ValueError(f"unknown engine: {engine}")

    # 展開して縦持ちへ
    rows: list[dict[str, Any]] = []
    for _, r in df[[id_col, text_col]].iterrows():
        doc_id = r[id_col]
        toks = tokenize_text_fn(r[text_col])

        for (word, pos, info) in toks:
            rec: dict[str, Any] = {
                id_col: doc_id,
                "word": word,
                "pos": pos,
            }
            if extra_col is not None:
                rec[extra_col] = info
            rows.append(rec)

    return pd.DataFrame(rows)


def tokens_to_text(
    df: pd.DataFrame,
    *,
    pos_keep: Optional[Iterable[str]] = None,
    pos_exclude: Optional[Iterable[str]] = None,
) -> str:
    """
    「1行=1トークン」の DataFrame から、スペース区切りのテキストを作ります。

    - df には 'word' と 'pos' 列が必要です
    - pos_keep / pos_exclude が指定された場合はフィルタを適用します

    Returns
    -------
    str
        "word1 word2 ..." 形式
    """
    if "word" not in df.columns or "pos" not in df.columns:
        raise KeyError("df must have 'word' and 'pos' columns")

    s = filter_tokens_df(df, pos_keep=pos_keep, pos_exclude=pos_exclude, strict=True)

    return " ".join(s["word"].dropna().astype(str))
