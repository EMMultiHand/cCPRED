# -*- coding: utf-8 -*-
r"""Поиск источника каталога магазина (ga28), каталога брони и боеприпасов.
Отчёт: $TEMP/rb_armor.txt (UTF-8).
"""
import os
import re

DEC = os.path.join(os.environ.get('TEMP', '.'), 'rb_main_decoded.txt')
OUT = os.path.join(os.environ.get('TEMP', '.'), 'rb_armor.txt')

TOKENS = [
    'ga28', 'a28(', 'a27(', 'p3', 'Кевлар', 'Бронекуртка', 'Бронежилет',
    'b94', 'b9F', 'b9q', 'bbs', 'baY', 'b8t',
    'B.jT', 'B.VC', 'B.Za', 'B.Sx', 'B.MG', 'B.TV', 'B.Vb',
    'armorLoadout', 'Броня', 'Щит',
]


def main():
    dec = open(DEC, encoding='utf-8').read()
    lines = []
    for tok in TOKENS:
        idxs = [m.start() for m in re.finditer(re.escape(tok), dec)]
        lines.append('===== %s : %d вхождений' % (tok, len(idxs)))
        for i in idxs[:10]:
            snippet = dec[max(0, i - 300):i + 420].replace('\n', ' ')
            lines.append('   ...%s...' % snippet)
        lines.append('')
    open(OUT, 'w', encoding='utf-8').write('\n'.join(lines))
    print('report ->', OUT)


if __name__ == '__main__':
    main()
