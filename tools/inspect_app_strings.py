# -*- coding: utf-8 -*-
r"""Декодирует \uXXXX-строки из main.dart.js в читаемый текст для анализа."""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'app', 'main.dart.js')
OUT = os.path.join(os.environ.get('TEMP', '.'), 'rb_main_decoded.txt')


def main():
    s = open(SRC, encoding='utf-8', errors='replace').read()
    # \uXXXX -> символ
    dec = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), s)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(dec)
    print('decoded ->', OUT, len(dec), 'chars')

    keywords = sys.argv[1:] or [
        'agentShop', 'agentCorporations', 'agentGangs', 'agentContacts',
        'МАГАЗИН', 'КОРПОРАЦ', 'ФРАКЦ', 'БАНД', 'ПАТРОН', 'БОЕЗАПАС',
        'ИМПЛАНТ', 'ХРОМ', 'КИБЕР', 'ОРУЖИЕ', 'БРОНЯ', 'СНАРЯЖ',
        'consumables', 'customWeapons', 'armorLoadout', 'cyberware',
    ]
    for kw in keywords:
        idxs = [m.start() for m in re.finditer(re.escape(kw), dec)]
        print('\n== %s: %d' % (kw, len(idxs)))
        for i in idxs[:6]:
            snippet = dec[max(0, i - 90):i + 130].replace('\n', ' ')
            print('   ...' + snippet + '...')


if __name__ == '__main__':
    sys.exit(main())
