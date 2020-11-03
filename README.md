# Pokemon Rankbattle Data Transformer

## 概要

ポケモン剣盾のランクバトルの集計データをウェブ上から取得し、表示しやすいように整形するプログラムです。

詳細については[こちら](https://qiita.com/b_aka/items/7d2b768dfa7817f34fc2)の記事をお読みください。

## 使い方

プログラムの動作に必要となるパッケージをインストールします。

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

以下を実行すると整形されたcsvファイルが`resources`と`output`に出力されます。

```bash
$ python main.py [-d Boolean]
```

コマンドライン引数`-d`に`False`を指定すると、ファイルのダウンロードを行わないようにできます。デフォルトで`True`となっていいるのでダウンロードを行いたくない場合のみ指定してください。

## 出力されたファイルの利用法

![gif](.\docs\images\gif2.gif)

[ポケモン剣盾のランクバトルデータを解析してTableau上で可視化してみた - Qiita](https://qiita.com/b_aka/items/7d2b768dfa7817f34fc2) をご覧ください。

## License

MIT 

--------

moxak Github [@moxak](https://github.com/moxak) Twitter [@moxab_](https://twitter.com/moxab_)

