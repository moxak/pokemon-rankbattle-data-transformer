# Pokemon Rankbattle Data Transformer

<img alt="GitHub" src="https://img.shields.io/github/license/moxak/pokemon-rankbattle-data-transformer"> <img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/moxak/pokemon-rankbattle-data-transformer">

## 概要

ポケモン剣盾のランクバトルの集計データをウェブ上から取得し、表示しやすいように整形するプログラムです。

詳細については[こちら](https://qiita.com/b_aka/items/7d2b768dfa7817f34fc2)の記事をお読みください。

## 使い方

**0. Python(version >= 3.7)が入っていない場合、**

```bash
$ sudo apt-get install python3.7
```

もしくは、[Python.org](https://www.python.org/)から落としてインストールしてください。また`pip`のpathが通っている状態にしてください。

**1. プログラムの動作に必要となるパッケージをインストールします。**

```bash
$ pip install -r requirements.txt
```

`requirements.txt`に記載されているファイルは以下の通りです。バージョンは問いませんので、既にインストールされている場合はスキップしてください。

```bash
###### Requirements without Version Specifiers ######
pandas
scikit-learn
tqdm
urllib3
```

**2. 以下を実行して整形されたcsvファイルを`resources`と`output`に出力します**

```bash
$ python main.py [-d Boolean]
```

コマンドライン引数`-d`に`False`を指定すると、ファイルのダウンロードを行わないようにできます。デフォルトで`True`となっていいるのでダウンロードを行いたくない場合のみ指定してください。

## 出力されたファイルの利用法

![gif](docs/images/gif2.gif)

[ポケモン剣盾のランクバトルデータを解析してTableau上で可視化してみた - Qiita](https://qiita.com/b_aka/items/7d2b768dfa7817f34fc2) をご覧ください。

## License

MIT

--------

moxak Github [@moxak](https://github.com/moxak) Twitter [@moxab_](https://twitter.com/moxab_)

