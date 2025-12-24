# Google Colab でテキストファイルを読む（最小構成）

このドキュメントでは、Google Colab 上で  
**Google Drive に保存されたテキストファイル（.txt）を読み込む**
ための最小構成の手順を説明します。

大量の文書データを扱う前提として、  
まずは **1つのテキストファイルを確実に読む** ことを目標にします。

---

## 1. Google Drive を Colab にマウントする

Google Drive 上のファイルを Colab から扱うためには、
最初に Drive をマウントします。

```python
from google.colab import drive
drive.mount("/content/drive")
```

実行すると、Google アカウントへのログインが求められます。  
認証が完了すると、Drive の中身が Colab から見えるようになります。

---

## 2. テキストファイルの場所を確認する

Drive をマウントすると、  
`/content/drive/MyDrive/` 以下が Google Drive のルートになります。

例：

```text
/content/drive/MyDrive/data/sample.txt
```

ここでは、この `sample.txt` を読み込むとします。

---

## 3. with open を使ってテキストを読む

Python では、`with open` を使ってテキストファイルを読みます。

```python
file_path = "/content/drive/MyDrive/data/sample.txt"

with open(file_path, encoding="utf-8") as f:
    text = f.read()
```

### 各行の意味

- `file_path`  
  読み込みたいテキストファイルのパス

- `encoding="utf-8"`  
  日本語テキストを正しく読むために指定します

- `f.read()`  
  ファイル全体を **1つの文字列** として読み込みます

---

## 4. 読み込んだ内容を確認する

```python
print(text[:300])
```

先頭の一部を表示して、  
正しく読み込めているかを確認します。

---

## 5. よくある注意点

### 文字化けする場合

- `encoding="utf-8"` が指定されているか確認してください
- 古いテキストでは `"shift_jis"` が使われている場合もあります

```python
with open(file_path, encoding="shift_jis") as f:
    text = f.read()
```

---

### FileNotFoundError が出る場合

- パスが正しいか確認してください
- Drive のマウントが完了しているか確認してください

---

## まとめ

このドキュメントでは、以下を行いました。

- Google Drive を Colab にマウントする
- Drive 上のテキストファイルの場所を指定する
- `with open` を使ってテキストを読む

この手順ができれば、  
複数ファイルの読み込みや、大量文書の処理に進む準備が整います。
