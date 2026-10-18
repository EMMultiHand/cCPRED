# -*- coding: utf-8 -*-
r"""Контексты использования мастер-списков и полей агента в декодированном JS.
Отчёт: $TEMP/rb_usage.txt (UTF-8).
"""
import os
import re

DEC = os.path.join(os.environ.get('TEMP', '.'), 'rb_main_decoded.txt')
OUT = os.path.join(os.environ.get('TEMP', '.'), 'rb_usage.txt')

TOKENS = [
    'B.Ox', 'B.Pl', 'B.Q2', 'B.O5', 'B.RG', 'B.dY', 'B.Od',
    'agentShop', 'agentCorporations', 'agentGangs', 'agentMap',
    'aKX', 'aZc', 'b9F', 'a7F', 'a8l',
]


def main():
    dec = open(DEC, encoding='utf-8').read()
    lines = []
    for tok in TOKENS:
        idxs = [m.start() for m in re.finditer(re.escape(tok), dec)]
        lines.append('===== %s : %d вхождений' % (tok, len(idxs)))
        for i in idxs[:14]:
            snippet = dec[max(0, i - 260):i + 320].replace('\n', ' ')
            lines.append('   ...%s...' % snippet)
        lines.append('')
    open(OUT, 'w', encoding='utf-8').write('\n'.join(lines))
    print('report ->', OUT)


if __name__ == '__main__':
    main()
