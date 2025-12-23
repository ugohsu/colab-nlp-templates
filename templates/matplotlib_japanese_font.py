# ============================================================
# Google Colab 上で matplotlib に日本語を正しく表示する設定
# ============================================================

# ------------------------------------------------------------
# 1. 日本語フォントのインストール（Colab 専用）
# ------------------------------------------------------------
# Colab 環境には、日本語フォントがデフォルトでは入っていません。
# そのため、日本語を含むグラフを描くと
# 「□（豆腐）」や文字化けが発生します。
#
# ここでは、Google が提供している Noto CJK フォントを使用します。
# CJK = Chinese / Japanese / Korean
!apt-get -y install fonts-noto-cjk


# ------------------------------------------------------------
# 2. 使用する日本語フォントのパスを指定
# ------------------------------------------------------------
# NotoSansCJK-Regular.ttc は、汎用的でクセの少ない日本語フォントです。
# 論文・教材・スライド用途でも安心して使えます。
font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"


# ------------------------------------------------------------
# 3. matplotlib にフォントを登録・既定化
# ------------------------------------------------------------
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties, fontManager

# matplotlib にフォントファイルを認識させる
fontManager.addfont(font_path)

# フォントプロパティを作成
fp = FontProperties(fname=font_path)

# matplotlib 全体のデフォルトフォントとして設定
# これを設定しておくと、以降の plt.title(), plt.xlabel() などで
# 日本語をそのまま書いても文字化けしなくなります。
plt.rcParams["font.family"] = fp.get_name()
