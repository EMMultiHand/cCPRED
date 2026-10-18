# -*- coding: utf-8 -*-
r"""Извлекает все таблицы страницы data-pool в JSON.

Использование: python tools/extract_dp_tables.py chrome/implants [out_suffix]
Результат: $TEMP/dp_tables_<slug>.json

Для каждой таблицы сохраняются:
  section  — ближайший предшествующий заголовок h1-h6 (вне навигации)
  headers  — список заголовков столбцов
  rows     — список строк, каждая строка — список текстов ячеек
"""
import html as html_mod
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DP = os.path.join(ROOT, 'data-pool')
TMP = os.environ.get('TEMP', '.')

# заголовки навигации, которые надо игнорировать как «секции»
NAV_SKIP = [
    'Снаряжение', 'Твоё Здоровье', 'Город', 'Мастерская', 'Твой Хром',
    'Где ты живешь', 'Твои контакты', 'Сеть', 'Твоя работа', 'Остальное',
    'FAQ по CPRed', 'Книги Правил', 'Последние Новости',
    'Поддержка и Обратная Связь', 'Благодарим за поддержку!',
]


def strip_tags(s):
    s = re.sub(r'<br\s*/?>', '\n', s, flags=re.I)
    s = re.sub(r'<[^>]+>', '', s)
    s = html_mod.unescape(s)
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r'\n{3,}', '\n\n', s)
    return s.strip()


def main():
    page = sys.argv[1]
    p = os.path.join(DP, page.replace('/', os.sep))
    if os.path.isdir(p):
        p = os.path.join(p, 'index.html')
    if not p.endswith('.html'):
        p += '.html'
    t = open(p, encoding='utf-8', errors='replace').read()

    # все заголовки с позициями
    headings = []
    for m in re.finditer(r'<h([1-6])[^>]*>(.*?)</h\1>', t, re.S):
        txt = strip_tags(m.group(2))
        if txt in NAV_SKIP:
            continue
        headings.append((m.start(), 'h%s' % m.group(1), txt))

    tables = []
    for m in re.finditer(r'<table[^>]*>(.*?)</table>', t, re.S | re.I):
        pos = m.start()
        sec = ''
        for hp, htag, htxt in headings:
            if hp < pos:
                sec = htxt + (' [%s]' % htag if htxt else '')
            else:
                break
        body = m.group(1)
        rows = []
        for r in re.finditer(r'<tr[^>]*>(.*?)</tr>', body, re.S | re.I):
            cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r.group(1), re.S | re.I)
            rows.append([strip_tags(c) for c in cells])
        if not rows:
            continue
        headers = rows[0]
        data_rows = rows[1:]
        tables.append({'section': sec, 'headers': headers, 'rows': data_rows})

    slug = page.replace('/', '_')
    out = os.path.join(TMP, 'dp_tables_%s.json' % slug)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(tables, f, ensure_ascii=False, indent=1)
    total = sum(len(x['rows']) for x in tables)
    print('tables: %d, rows: %d -> %s' % (len(tables), total, out))
    for i, tb in enumerate(tables):
        print('  [%d] %s | %d rows | %s' % (i, tb['section'][:60], len(tb['rows']),
                                            ' / '.join(h[:16] for h in tb['headers'])))
    return 0


if __name__ == '__main__':
    sys.exit(main())
