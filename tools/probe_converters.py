# -*- coding: utf-8 -*-
r"""Печатает тела функций-конвертеров каталогов (b6t, b6v, b6R, b7Z, b8k и др.).
Отчёт: $TEMP/rb_conv.txt
"""
import os
import re

DEC = os.path.join(os.environ.get('TEMP', '.'), 'rb_main_decoded.txt')
OUT = os.path.join(os.environ.get('TEMP', '.'), 'rb_conv.txt')

# имена: A.b6t (броня?), A.b6v, A.b6R, A.b7Z, A.b8k и функции вокруг
NAMES = ['b6t(', 'b6v(', 'b6R(', 'b7Z(', 'b8k(', 'b94(', 'b9F(', 'b9q(',
         'b7s(', 'b8_(', 'b8N(', 'b6p(', 'b6q(', 'b6r(']


def main():
    dec = open(DEC, encoding='utf-8').read()
    lines = []
    for nm in NAMES:
        idxs = [m.start() for m in re.finditer(re.escape(nm), dec)]
        lines.append('===== %s : %d' % (nm, len(idxs)))
        for i in idxs[:4]:
            lines.append(dec[i:i + 700].replace('\n', ' '))
            lines.append('---')
        lines.append('')
    open(OUT, 'w', encoding='utf-8').write('\n'.join(lines))
    print('report ->', OUT)


if __name__ == '__main__':
    main()
