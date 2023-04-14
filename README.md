# lightbluePy

Daisuke Bekki氏の日本語CCGパーザであるlightblueをPythonに移植するものです。現在開発中です。

元のソースコードに忠実に移植するため、機能や実装はほとんど変更はしていません。

また、現在以下は未実装です。

* DTSの処理
* Visualizerの処理

## Environment

* Python 3.10 or later
* lark 1.1.5 or later (`pip install lark`)

## Usage
Default `beam` for lightblue is `24`.

```python
from chartParser import simpleParse, output_node

res = simpleParse(24, "文を処理する")
for r in res:
    print(output_node(r))
```

## LICENSE
`mylexicon_hs.py`の著作権はDaisuke Bekki氏に帰属し、BSD 3-Clause "New" or "Revised" Licenseの元で利用されています。また、`Juman.dic.tsv`は元レポジトリより同ライセンスのもとで取得したものです。
