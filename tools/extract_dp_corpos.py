# -*- coding: utf-8 -*-
r"""Разбирает city/corpos страницы data-pool: категории (summary) + ссылки-корпорации,
а также все якоря/заголовки, чтобы найти тексты описаний.
Отчёт: $TEMP/dp_corpos.txt (UTF-8).
"""
import html as html_mod
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DP = os.path.join(ROOT, 'data-pool')
OUT = os.path.join(os.environ.get('TEMP', '.'), 'dp_corpos.txt')


def strip_tags(s):
    s = re.sub(r'<br\s*/?>', '\n', s, flags=re.I)
    s = re.sub(r'<[^>]+>', '', s)
    s = html_mod.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()


def main():
    t = open(os.path.join(DP, 'city', 'corpos', 'index.html'), encoding='utf-8', errors='replace').read()
    lines = []

    # 1. Все summary + содержимое после summary до </details>
    lines.append('===== DETAILS (%d):' % len(re.findall(r'<details', t, re.I)))
    for i, m in enumerate(re.finditer(r'<details[^>]*>(.*?)</details>', t, re.S | re.I)):
        inner = m.group(1)
        sm = re.search(r'<summary[^>]*>(.*?)</summary>', inner, re.S | re.I)
        title = strip_tags(sm.group(1)) if sm else '?'
        rest = inner[sm.end():] if sm else inner
        # соберём ссылки внутри details
        links = re.findall(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', rest, re.S)
        lines.append('[%d] %s | ссылок: %d' % (i, title[:120], len(links)))
        for href, txt in links[:60]:
            lines.append('    %-40s %s' % (href[:40], strip_tags(txt)[:70]))
        if not links:
            lines.append('    (без ссылок) текст: %s' % strip_tags(rest)[:200])
        lines.append('')

    # 2. Все заголовки h2-h6 с текстом (кроме навигации)
    lines.append('===== ЗАГОЛОВКИ:')
    for m in re.finditer(r'<(h[2-6])([^>]*)>(.*?)</\1>', t, re.S):
        txt = strip_tags(m.group(3))
        if txt and txt not in ('',):
            lines.append('  %s %s | %s' % (m.group(1), m.group(2)[:60], txt[:100]))
    open(OUT, 'w', encoding='utf-8').write('\n'.join(lines))
    print('report ->', OUT)


if __name__ == '__main__':
    main()
