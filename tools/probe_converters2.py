# -*- coding: utf-8 -*-
r"""Полные тела функций-конвертеров записей каталогов. Отчёт: $TEMP/rb_conv2.txt
"""
import os
import re

DEC = os.path.join(os.environ.get('TEMP', '.'), 'rb_main_decoded.txt')
OUT = os.path.join(os.environ.get('TEMP', '.'), 'rb_conv2.txt')

NAMES = ['b6t(a){', 'b6v(a){', 'b6R(a){', 'b7Z(a){', 'b8_(a){', 'b8k(a){',
         'b8t(a){', 'baY(a){', 'bbs(a){', 'b8s(a){', 'b62(a){', 'b9F(a){',
         'b9q(a){']


def main():
    dec = open(DEC, encoding='utf-8').read()
    lines = []
    for nm in NAMES:
        idxs = [m.start() for m in re.finditer(re.escape(nm), dec)]
        lines.append('===== %s : %d' % (nm, len(idxs)))
        for i in idxs[:2]:
            lines.append(dec[i:i + 1400].replace('\n', ' '))
            lines.append('---')
        lines.append('')
    open(OUT, 'w', encoding='utf-8').write('\n'.join(lines))
    print('report ->', OUT)


if __name__ == '__main__':
    main()
