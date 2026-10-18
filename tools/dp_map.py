# -*- coding: utf-8 -*-
r"""Карта data-pool: список всех страниц; структура страницы корпораций.
Отчёт: $TEMP/dp_map.txt (UTF-8).
"""
import html as html_mod
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DP = os.path.join(ROOT, 'data-pool')
OUT = os.path.join(os.environ.get('TEMP', '.'), 'dp_map.txt')


def strip_tags(s):
    s = re.sub(r'<br\s*/?>', '\n', s, flags=re.I)
    s = re.sub(r'<[^>]+>', '', s)
    s = html_mod.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()


def main():
    lines = []
    lines.append('===== Страницы data-pool:')
    pages = []
    for dp, dn, fn in os.walk(DP):
        if 'index.html' in fn:
            rel = os.path.relpath(os.path.join(dp, 'index.html'), DP).replace(os.sep, '/')
            pages.append(rel)
    for p in sorted(pages):
        lines.append('   ' + p)
    lines.append('')
    lines.append('===== city/corpos: заголовки')
    t = open(os.path.join(DP, 'city', 'corpos', 'index.html'), encoding='utf-8', errors='replace').read()
    for m in re.finditer(r'<(h[1-6])[^>]*>(.*?)</\1>', t, re.S):
        txt = strip_tags(m.group(2))
        if txt:
            lines.append('  %s: %s' % (m.group(1), txt[:120]))
    lines.append('')
    lines.append('===== city/corpos: первые details/summary')
    for i, m in enumerate(re.finditer(r'<details[^>]*>(.*?)</details>', t, re.S)):
        inner = m.group(1)
        sm = re.search(r'<summary[^>]*>(.*?)</summary>', inner, re.S)
        s = strip_tags(sm.group(1)) if sm else '?'
        rest = inner[sm.end():] if sm else inner
        rt = strip_tags(rest)
        lines.append('  [%d] SUMMARY: %s' % (i, s[:150]))
        lines.append('      TEXT: %s' % rt[:300])
        if i >= 9:
            break
    if not re.search(r'<details', t):
        lines.append('  (нет details; покажу крупные блоки текста после заголовков)')
        # карточки?
        for cls in set(re.findall(r'class="([^"]+)"', t)):
            pass
        chunks = re.split(r'<h2[^>]*>', t)
        lines.append('  h2 блоков: %d' % (len(chunks) - 1))
        for i, ch in enumerate(chunks[1:6], 1):
            title = strip_tags(ch.split('</h2>')[0])
            body = strip_tags(ch.split('</h2>', 1)[1] if '</h2>' in ch else ch)
            lines.append('  [%d] H2: %s' % (i, title[:150]))
            lines.append('      %s' % body[:300])
    open(OUT, 'w', encoding='utf-8').write('\n'.join(lines))
    print('report ->', OUT)


if __name__ == '__main__':
    main()
