# Colab NLP Templates

このリポジトリは、**Google Colaboratory 上で自然言語処理（NLP）を学ぶための
テンプレート・関数・ドキュメント**をまとめた教材用リポジトリです。

ゼミ・演習での利用を主目的とし、

- Colab に **貼り付けてすぐ動くテンプレート**
- **import して使える前処理関数群**
- それらの背景・理由を説明する **ドキュメント**

を明確に分離して整理しています。

README では全体像と導線のみを示し、  
**具体的な使い方・注意点は docs 以下に委ねます。**

---

## ディレクトリ構成と役割

- **templates/**  
  Colab のコードセルに  
  👉 *そのまま貼り付けて実行するテンプレート*

- **libs/**  
  GitHub から clone した後、  
  👉 *import して使う共通関数群*

- **docs/**  
  各テンプレ・関数について、  
  👉 *なぜ必要か / どう使うかを説明するドキュメント*

---

## テンプレート一覧（貼り付けて使う）

| 内容 | ファイル | 解説 |
|---|---|---|
| matplotlib 日本語表示 | `templates/matplotlib_japanese_font.py` | [docs/matplotlib_japanese_font.md](./docs/matplotlib_japanese_font.md) |

---

## 関数群一覧（import して使う）

### 前処理：形態素解析（Janome / SudachiPy）

- 実装ファイル  
  - `libs/preprocess.py`

- 提供関数  
  - `tokenize_janome`  
  - `tokenize_sudachi`

- 解説ドキュメント  
  - 👉 [docs/tokenization.md](./docs/tokenization.md)

---

## どこから読めばよいか（初学者向け）

1. **README（このページ）**  
   → 全体像と構成を把握
2. **docs/tokenization.md**  
   → Colab での import 方法、Janome / Sudachi の選び方
3. **templates/** または **libs/**  
   → 実際にコードを使う

---

## 想定利用シーン

- ゼミ・演習での NLP 前処理
- 教育用 Google Colab ノートブック
- BoW / TF-IDF / トピックモデル（LDA / NMF）の前段処理
