# -*- coding: utf-8 -*-
r"""Тела функций-фильтров каталогов: bbs, b94, b8s, b8t, baY, b9q, b9F, и др.
Отчёт: $TEMP/rb_filters.txt
"""
import os
import re

DEC = os.path.join(os.environ.get('TEMP', '.'), 'rb_main_decoded.txt')
OUT = os.path.join(os.environ.get('TEMP', '.'), 'rb_filters.txt')

NAMES = ['bbs(a){', 'b94(a){', 'b8s(a){', 'b8t(a){', 'baY(a){', 'b9q(a){',
         'b9F(a){', 'bbs:function', 'b94:function', 'b8s:function']


def main():
    dec = open(DEC, encoding='utf-8').read()
    lines = []
    for nm in NAMES:
        idxs = [m.start() for m in re.finditer(re.escape(nm), dec)]
        lines.append('===== %s : %d' % (nm, len(idxs)))
        for i in idxs[:3]:
            lines.append(dec[i:i + 900].replace('\n', ' '))
            lines.append('---')
        lines.append('')
    open(OUT, 'w', encoding='utf-8').write('\n'.join(lines))
    print('report ->', OUT)


if __name__ == '__main__':
    main()
