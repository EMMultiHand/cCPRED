# -*- coding: utf-8 -*-
r"""Показывает разметку вокруг первой таблицы страницы data-pool:
заголовочные блоки, классы секций. Отчёт: $TEMP/dp_markup.txt
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DP = os.path.join(ROOT, 'data-pool')
OUT = os.path.join(os.environ.get('TEMP', '.'), 'dp_markup.txt')


def main():
    p = os.path.join(DP, 'equipment', 'weapons', 'index.html')
    t = open(p, encoding='utf-8', errors='replace').read()
    lines = []
    # найдём все таблицы и покажем 400 символов ПЕРЕД каждой таблицей
    for i, m in enumerate(re.finditer(r'<table', t)):
        seg = t[max(0, m.start() - 500):m.start()]
        lines.append('==== table %d, перед ней:' % i)
        lines.append(seg)
        lines.append('')
        if i >= 7:
            break
    # покажем классы заголовков, встречающиеся между таблицами
    open(OUT, 'w', encoding='utf-8').write('\n'.join(lines))
    print('report ->', OUT)


if __name__ == '__main__':
    main()
