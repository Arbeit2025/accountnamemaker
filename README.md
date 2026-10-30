# Account Name Maker

ランダムなアカウント名の候補を提案する、小さな Web ツールです。

テーマ（かわいい／かっこいい／自然・和風ローマ字／おしゃれ／ゲーム風／食べ物・カフェ／宇宙・星／おまかせ）と、好きな言葉（キーワード）を選ぶと、アカウント名の候補をまとめて表示します。数字や区切り（アンダースコア／ドット）の有無も選べます。候補をタップするとコピーできます。

Random account name candidate generator. Pick a theme and an optional keyword, and it proposes a batch of names.

## Features
- テーマ7種＋おまかせから単語を組み合わせて候補を生成（重複なし）
- キーワード（好きな言葉・英数字）を候補に含められる
- 候補数 5／10／20／30件、数字の有無、区切り（おまかせ／_／.／なし）を選択可
- 候補をタップ／クリックでコピー
- API: `GET /api/generate?theme=cute&keyword=cocoa&count=10&numbers=1&separator=auto&seed=1`
  - `seed` を渡すと同じ条件で同じ候補が返る（再現性あり）
- ヘルスチェック: `GET /healthz`

※ 候補が各サービスで実際に使えるか（空き状況）は確認していません。登録前にサービス側で確認してください。

## Run (local)
```
pip install -r requirements.txt
python app.py
```

## Test
```
python -m unittest discover -s tests -v
```

## Deploy (Render)
Render でこのリポジトリから Web Service を作り、Start Command を `gunicorn app:app` にすると公開できます。データベースは使わないので、再デプロイで消えるデータはありません。
