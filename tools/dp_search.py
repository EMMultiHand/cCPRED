# -*- coding: utf-8 -*-
r"""Поиск терминов по всему дереву data-pool (html). Отчёт: $TEMP/dp_search.txt
Использование: python tools/dp_search.py термин1 термин2 ... (UTF-8 argv неважно —
можно передавать латиницей/числа, для кириллицы отредактируйте TERMS в файле)
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DP = os.path.join(ROOT, 'data-pool')
OUT = os.path.join(os.environ.get('TEMP', '.'), 'dp_search.txt')

TERMS = [
    'Валентино', 'Мальстрём', 'Мальстрем', 'Тигриные', 'Мокс', 'Альдекальдо',
    'Джоуды', 'Вудуист', 'Бозо', 'Инквизитор', 'Животные', 'Стальные вакеро',
    'фракци', 'Фракци',
]


def main():
    terms = TERMS
    lines = []
    for term in terms:
        pat = re.compile(re.escape(term), re.IGNORECASE)
        hits = []
        for dp, dn, fn in os.walk(DP):
            if 'images' in dp or 'vendor' in dp:
                continue
            for f in fn:
                if not f.endswith(('.html', '.json', '.js')):
                    continue
                p = os.path.join(dp, f)
                try:
                    t = open(p, encoding='utf-8', errors='replace').read()
                except Exception:
                    continue
                n = len(pat.findall(t))
                if n:
                    hits.append((os.path.relpath(p, DP), n))
        hits.sort(key=lambda x: -x[1])
        lines.append('===== %s : %d файлов' % (term, len(hits)))
        for h, n in hits[:12]:
            lines.append('   %-60s %d' % (h, n))
        lines.append('')
    open(OUT, 'w', encoding='utf-8').write('\n'.join(lines))
    print('report ->', OUT)


if __name__ == '__main__':
    main()
