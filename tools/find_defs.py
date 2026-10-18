# -*- coding: utf-8 -*-
r"""Ищет определения B.dY, B.Od и примеров записей в main.dart.js.
Отчёт: $TEMP/find_defs.txt
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, 'app', 'main.dart.js')
TMP = os.environ.get('TEMP', '.')


def main():
    t = open(APP, encoding='utf-8', errors='replace').read()
    lines = []
    for pat in ['B.dY', 'B.Od=', 'B.Uz=', 'B.Ox=', 'B.Q2=', 'B.hP=']:
        lines.append('===== %s' % pat)
        for m in list(re.finditer(re.escape(pat), t))[:4]:
            lines.append('   @%d: %s' % (m.start(), t[m.start():m.start() + 260]))
        lines.append('')
    open(os.path.join(TMP, 'find_defs.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
    print('report -> $TEMP/find_defs.txt')


if __name__ == '__main__':
    main()
