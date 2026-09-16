"""docs/legal/*.md を GitHub Pages 用の静的 HTML へ変換する。

対応する記法は原文で実際に使っている範囲（見出し・段落・表・箇条書き・
引用・水平線・強調・リンク）に限定する。
"""

import html
import re
import sys
from pathlib import Path

# 言語切替リンクの行き先。パスは出力先の `privacy/` ディレクトリを基準にした相対で持ち、
# ページ側の階層に応じた接頭辞（build の prefix）を付けて最終的な href にする。
#
# en だけ `privacy/index.html`、他は `privacy/<lang>/index.html` と階層が 1 つ違う。
# 全ページで同じ `../lang/` を使うと en ページだけ `privacy/` の外を指し 404 になるため、
# ここに `../` を直接書かないこと。
LANGS = [('en', 'English', ''), ('ja', '日本語', 'ja/'), ('ko', '한국어', 'ko/'), ('zh', '中文', 'zh/')]


def inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text


def starts_block(line: str) -> bool:
    """段落ではなくブロック要素の開始行かどうか。"""
    return bool(
        line.startswith('> ')
        or line.startswith('---')
        or line.startswith('|')
        or re.match(r'^#{1,4} ', line)
        or re.match(r'^[-*] ', line)
        or re.match(r'^\d+\. ', line)
    )


def convert(md: str) -> str:
    out, lines, i = [], md.split('\n'), 0
    while i < len(lines):
        line = lines[i].rstrip()

        if not line:
            i += 1
            continue

        if line.startswith('> '):
            block = []
            while i < len(lines) and lines[i].startswith('> '):
                block.append(inline(lines[i][2:]))
                i += 1
            out.append('<blockquote><p>' + ' '.join(block) + '</p></blockquote>')
            continue

        if line.startswith('---'):
            out.append('<hr>')
            i += 1
            continue

        heading = re.match(r'^(#{1,4}) (.*)', line)
        if heading:
            level = len(heading.group(1))
            out.append(f'<h{level}>{inline(heading.group(2))}</h{level}>')
            i += 1
            continue

        if line.startswith('| '):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            header, body = rows[0], rows[2:]
            out.append('<div class="table-wrap"><table><thead><tr>'
                       + ''.join(f'<th>{inline(c)}</th>' for c in header)
                       + '</tr></thead><tbody>'
                       + ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>' for r in body)
                       + '</tbody></table></div>')
            continue

        if re.match(r'^[-*] ', line):
            items = []
            while i < len(lines) and re.match(r'^[-*] ', lines[i]):
                items.append(f'<li>{inline(lines[i][2:])}</li>')
                i += 1
            out.append('<ul>' + ''.join(items) + '</ul>')
            continue

        if re.match(r'^\d+\. ', line):
            items = []
            while i < len(lines) and re.match(r'^\d+\. ', lines[i]):
                items.append(f'<li>{inline(re.sub(r"^\d+\. ", "", lines[i]))}</li>')
                i += 1
            out.append('<ol>' + ''.join(items) + '</ol>')
            continue

        # ここまでのどのブロックにも該当しない行は段落として扱う。
        # 空行または次のブロック開始まで読み進める。para は必ず 1 行以上を含むため
        # i は毎周回で前進し、ループが止まらなくなることはない。
        para = [inline(line)]
        i += 1
        while i < len(lines) and lines[i].strip() and not starts_block(lines[i]):
            para.append(inline(lines[i].strip()))
            i += 1
        out.append('<p>' + '<br>'.join(para) + '</p>')

    return '\n'.join(out)


TEMPLATE = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- 本文に【要確定】が残っている間は検索インデックスを避ける。確定後にこの行を削除すること。 -->
<meta name="robots" content="noindex">
<title>{title} | KOBE in Your Pocket</title>
<style>
  :root {{ color-scheme: light dark; --fg: #1a1a1a; --muted: #5a5f66; --bg: #ffffff; --line: #e2e4e8; --accent: #C67B4A; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --fg: #e8e8e8; --muted: #a0a5ad; --bg: #16181c; --line: #2c2f35; }}
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; padding: 2rem 1.25rem 5rem; background: var(--bg); color: var(--fg);
         font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Noto Sans JP", sans-serif;
         line-height: 1.8; -webkit-text-size-adjust: 100%; }}
  main {{ max-width: 46rem; margin: 0 auto; }}
  h1 {{ font-size: 1.8rem; line-height: 1.4; margin: 0 0 1.5rem; }}
  h2 {{ font-size: 1.25rem; margin: 2.5rem 0 0.75rem; padding-bottom: 0.4rem; border-bottom: 1px solid var(--line); }}
  h3 {{ font-size: 1.05rem; margin: 1.75rem 0 0.5rem; }}
  p, li {{ font-size: 1rem; }}
  hr {{ border: 0; border-top: 1px solid var(--line); margin: 2rem 0; }}
  blockquote {{ margin: 1.25rem 0; padding: 0.75rem 1rem; border-left: 3px solid var(--accent);
                background: color-mix(in srgb, var(--accent) 8%, transparent); }}
  blockquote p {{ margin: 0; color: var(--muted); font-size: 0.92rem; }}
  .table-wrap {{ overflow-x: auto; margin: 1.25rem 0; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 0.95rem; }}
  th, td {{ border: 1px solid var(--line); padding: 0.5rem 0.75rem; text-align: left; vertical-align: top; }}
  th {{ background: color-mix(in srgb, var(--fg) 5%, transparent); }}
  code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.9em;
          background: color-mix(in srgb, var(--fg) 7%, transparent); padding: 0.1em 0.35em; border-radius: 3px; }}
  a {{ color: var(--accent); }}
  nav.langs {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 2rem;
               padding-bottom: 1.25rem; border-bottom: 1px solid var(--line); }}
  nav.langs a, nav.langs span {{ font-size: 0.9rem; padding: 0.3rem 0.7rem; border: 1px solid var(--line); border-radius: 999px; text-decoration: none; }}
  nav.langs span {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
  .notice {{ margin-bottom: 2rem; padding: 0.9rem 1rem; border: 1px solid var(--accent); border-radius: 6px;
             color: var(--muted); font-size: 0.92rem; }}
  footer {{ margin-top: 4rem; padding-top: 1.25rem; border-top: 1px solid var(--line); color: var(--muted); font-size: 0.85rem; }}
</style>
</head>
<body>
<main>
<nav class="langs">{langnav}</nav>
{notice}
{body}
<footer>KOBE in Your Pocket</footer>
</main>
</body>
</html>
"""


def build(lang: str, title: str, md_path: Path, notice: str = '', prefix: str = '') -> str:
    """1 ページ分の HTML を組み立てる。

    `prefix` は出力先から `privacy/` へ戻るための相対パス。`privacy/index.html`
    （en）は '' 、`privacy/<lang>/index.html` は '../' を渡す。
    """
    md = md_path.read_text()
    md = md.split('## 確定が必要な項目')[0].rstrip()
    # 版数運用の注記はリポジトリ内向けであり、公開ページには載せない。
    md = '\n'.join(l for l in md.split('\n') if not (l.startswith('> ') and 'README.md' in l))
    # 自分自身の言語はリンクにしないため、prefix + subpath が空になる組み合わせ
    # （en ページから en へ）は href として出力されない。
    nav = ''.join(
        (f'<span>{label}</span>' if code == lang else f'<a href="{prefix}{subpath}">{label}</a>')
        for code, label, subpath in LANGS
    )
    return TEMPLATE.format(
        lang=lang,
        title=title,
        langnav=nav,
        notice=f'<p class="notice">{notice}</p>' if notice else '',
        body=convert(md),
    )


if __name__ == '__main__':
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])

    # 末尾は出力先から privacy/ へ戻る相対パス。en だけ privacy/ 直下に置くため空文字。
    pages = [
        ('en', 'Privacy Policy', 'privacy-policy.en.md', dst / 'privacy' / 'index.html', '', ''),
        ('ja', 'プライバシーポリシー', 'privacy-policy.ja.md', dst / 'privacy' / 'ja' / 'index.html', '', '../'),
        ('ko', 'Privacy Policy', 'privacy-policy.en.md', dst / 'privacy' / 'ko' / 'index.html',
         '한국어 번역을 준비 중입니다. 현재는 영어 원문을 표시합니다.', '../'),
        ('zh', 'Privacy Policy', 'privacy-policy.en.md', dst / 'privacy' / 'zh' / 'index.html',
         '中文版正在准备中，当前显示英文原文。', '../'),
    ]

    for lang, title, md_name, out_path, notice, prefix in pages:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(build(lang, title, src / md_name, notice, prefix))
        print(f'built {out_path.relative_to(dst)}')
