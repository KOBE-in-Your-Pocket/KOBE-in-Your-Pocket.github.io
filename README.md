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

## 検索インデックスについて

事業者名・所在地・連絡先が確定し本文から `【要確定】` が解消されたため、2026-09-16 に
`<meta name="robots" content="noindex">` を削除した。以後このサイトは検索エンジンに
インデックスされる。

改定作業中などに一時的にインデックスを避けたい場合は、`scripts/md2html.py` の
`TEMPLATE` の `<head>` 内へ同じメタタグを戻すこと。
