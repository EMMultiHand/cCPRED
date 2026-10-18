# -*- coding: utf-8 -*-
r"""Контексты упоминаний имён функций-фильтров в декодированном JS.
Отчёт: $TEMP/rb_fnmap.txt
"""
import os
import re

DEC = os.path.join(os.environ.get('TEMP', '.'), 'rb_main_decoded.txt')
OUT = os.path.join(os.environ.get('TEMP', '.'), 'rb_fnmap.txt')

NAMES = ['"bbs"', '"b94"', '"b8s"', '"b8t"', '"baY"', '"b9q"', '"b9F"',
         '"b6t"', '"b6v"', '"b6R"', '"b7Z"', '"b62"', '"b8_"', '"b8k"']


def main():
    dec = open(DEC, encoding='utf-8', errors='replace').read()
    out = []
    for name in NAMES:
        out.append('===== ' + name)
        for m in list(re.finditer(re.escape(name), dec))[:4]:
            out.append('   @%d: %s' % (m.start(),
                                       dec[max(0, m.start() - 250):m.start() + 250].replace('\n', ' ')))
        out.append('')
    open(OUT, 'w', encoding='utf-8').write('\n'.join(out))
    print('ok ->', OUT)


if __name__ == '__main__':
    main()
