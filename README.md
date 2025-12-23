# Colab NLP Templates

このリポジトリは、**Google Colaboratory 上で自然言語処理（NLP）を学ぶための
テンプレートおよび関数群**をまとめた教材用リポジトリです。

ゼミ・演習での利用を主目的とし、

- コードセルに **貼り付けて使うテンプレ**
- **import して使う関数群**
- それらの背景・理由を説明する **ドキュメント**

を明確に分離して整理しています。

---

## 基本方針

- **templates**  
  - Colab のコードセルに **コピペして実行**
  - import はしない  
  - 環境構築・初期設定・定型スニペット向け

- **libs**  
  - GitHub から clone したあと **import して使用**
  - ゼミ内で共通利用する前処理・関数群

- **docs**  
  - 各テンプレ・関数の背景、理由、注意点
  - 「なぜその設定が必要か」を説明する man / README 相当

---

## テンプレート（貼り付けて使う）

### 作図時の日本語表記（matplotlib）

- 実行用テンプレ  
  - [`templates/matplotlib_japanese_font.py`](./templates/matplotlib_japanese_font.py)

- 解説ドキュメント  
  - [`docs/matplotlib_japanese_font.md`](./docs/matplotlib_japanese_font.md)

#### 内容
Google Colab 上で matplotlib を使用する際に、
日本語ラベルやタイトルが

- □（豆腐）になる  
- 文字化けする  
- 一部の漢字だけ表示されない  

といった問題を防ぐための **初期設定**です。

#### 使い方
1. テンプレファイルを開く  
2. 中身を **Colab のコードセルにそのまま貼り付けて実行**  
3. 以降の matplotlib 作図で、日本語がそのまま使用可能

> ※ このテンプレートは **import しません**。

---

## 関数群（import して使う）

### 前処理：形態素解析（Janome / Sudachi）

- 実装ファイル  
  - [`libs/preprocess.py`](./libs/preprocess.py)

- 提供関数  
  - `tokenize_janome`  
  - `tokenize_sudachi`

#### 使い方（Colab 例）

```python
!pip -q install janome sudachipy sudachidict_core
!git clone https://github.com/ugohsu/colab-nlp-templates.git

import sys
sys.path.append("/content/colab-nlp-templates")

from libs import tokenize_janome, tokenize_sudachi
