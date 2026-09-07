# KOBE-in-Your-Pocket.github.io

KOBE in Your Pocket の法務文書を公開する GitHub Pages サイト。

App Store Connect / Google Play Console はアプリ未インストールでも開ける公開 URL を要求するため、
アプリのバンドル内テキストではなくこのサイトを正とする。

## 公開 URL

| URL | 内容 |
| --- | --- |
| `https://kobe-in-your-pocket.github.io/privacy/` | プライバシーポリシー（English・ストア登録用） |
| `https://kobe-in-your-pocket.github.io/privacy/ja/` | 日本語 |
| `https://kobe-in-your-pocket.github.io/privacy/ko/` | 韓国語（翻訳準備中・英語原文を表示） |
| `https://kobe-in-your-pocket.github.io/privacy/zh/` | 中国語（翻訳準備中・英語原文を表示） |

Client アプリの `src/features/legal/domain/privacy-policy.ts` がこの URL 構成を前提にしている。

## 更新手順

本文の正は [Specification リポジトリ](https://github.com/KOBE-in-Your-Pocket/Specification) の
`docs/legal/privacy-policy.*.md`。このリポジトリの HTML は同ファイルから生成する。

```bash
python3 scripts/md2html.py <Specification>/docs/legal .
```

生成対象は `privacy/` 配下のみ。`index.html` は手書き。

改定して版数を上げたときは、Client の `PRIVACY_POLICY_VERSION` も同じ値へ更新すること。
更新しないと改定後のポリシーに対する同意が取得されない。

## noindex について

本文に `【要確定】`（事業者名・所在地・連絡先）が残っている間は検索インデックスを避けるため、
各ページに `<meta name="robots" content="noindex">` を入れている。
記載を確定させたらこの行を削除する。
