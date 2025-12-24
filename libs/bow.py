# ============================================================
# Bag-of-Words utilities (WordCloud etc.)
# ============================================================

import matplotlib.pyplot as plt
from wordcloud import WordCloud


def create_wordcloud(
    sentence,
    stopwords=None,
    outfile="img.png",
    figsize=(10, 6),
    background_color="white",
    width=1200,
    height=800,
    random_state=42,
):
    """
    分かち書き済みテキストから WordCloud を生成する。

    Notes
    -----
    - font_path はグローバル変数として定義済みであること
      （matplotlib 日本語フォント設定テンプレを事前に実行）
    """

    if stopwords is None:
        stopwords = set()
    else:
        stopwords = set(stopwords)

    if not sentence or not sentence.strip():
        raise ValueError("sentence が空です。tokens_to_text の結果を確認してください。")

    wcloud = WordCloud(
        background_color=background_color,
        font_path=font_path,
        stopwords=stopwords,
        width=width,
        height=height,
        random_state=random_state,
        collocations=False,
    ).generate(sentence)

    plt.figure(figsize=figsize)
    plt.imshow(wcloud)
    plt.axis("off")

    if outfile:
        plt.savefig(outfile, bbox_inches="tight")

    plt.show()

    return wcloud
