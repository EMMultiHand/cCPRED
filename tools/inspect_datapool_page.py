# -*- coding: utf-8 -*-
"""Осмотр структуры страницы data-pool: заголовки, таблицы, строки таблиц.
Использование: python tools/inspect_datapool_page.py equipment/weapons [max_lines]
Отчёт: $TEMP/dp_report.txt (UTF-8).
"""
import os
import re
import sys
import html as html_mod

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DP = os.path.join(ROOT, 'data-pool')
OUT = os.path.join(os.environ.get('TEMP', '.'), 'dp_report.txt')


def strip_tags(s):
    s = re.sub(r'<script.*?</script>', ' ', s, flags=re.S | re.I)
    s = re.sub(r'<style.*?</style>', ' ', s, flags=re.S | re.I)
    s = re.sub(r'<br\s*/?>', ' ', s, flags=re.I)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html_mod.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()


def main():
    page = sys.argv[1] if len(sys.argv) > 1 else 'index'
    max_lines = int(sys.argv[2]) if len(sys.argv) > 2 else 400
    p = os.path.join(DP, page.replace('/', os.sep))
    if os.path.isdir(p):
        p = os.path.join(p, 'index.html')
    if not p.endswith('.html'):
        p += '.html'
    t = open(p, encoding='utf-8', errors='replace').read()
    lines = []
    lines.append('PAGE %s  (%d chars)' % (os.path.relpath(p, DP), len(t)))

    for m in re.finditer(r'<h([1-4])[^>]*>(.*?)</h\1>', t, re.S):
        lines.append('h%s: %s' % (m.group(1), strip_tags(m.group(2))[:120]))

    lines.append('')
    tables = list(re.finditer(r'<table[^>]*>.*?</table>', t, re.S | re.I))
    lines.append('TABLES: %d' % len(tables))
    for ti, tb in enumerate(tables[:10]):
        body = tb.group(0)
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', body, re.S | re.I)
        lines.append('-- table %d: rows=%d' % (ti, len(rows)))
        for r in rows[:4]:
            cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.S | re.I)
            lines.append('   | ' + ' | '.join(strip_tags(c)[:40] for c in cells))
        if len(rows) > 4:
            lines.append('   ... (%d more rows)' % (len(rows) - 4))

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines[:max_lines]))
    print('report ->', OUT, 'lines:', min(len(lines), max_lines))


if __name__ == '__main__':
    sys.exit(main())
