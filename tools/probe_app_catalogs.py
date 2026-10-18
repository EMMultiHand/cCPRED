# -*- coding: utf-8 -*-
r"""Поиск каталогов приложения (оружие, броня, импланты, корпорации, банды)
в декодированном main.dart.js. Отчёт пишется в UTF-8-файл."""
import os
import re
import sys

DEC = os.path.join(os.environ.get('TEMP', '.'), 'rb_main_decoded.txt')
OUT = os.path.join(os.environ.get('TEMP', '.'), 'rb_probe.txt')

PATTERNS = [
    'aZc',
    '2d6', '3d6', '4d6', '5d6', '6d6',
    'Мощный пистолет', 'Тяжелый пистолет', 'Тяжёлый пистолет', 'Средний пистолет',
    'Очень тяжелый пистолет', 'Очень тяжёлый пистолет',
    'дробовик', 'Дробовик', 'винтовк', 'Винтовк',
    'гранатомет', 'гранатомёт', 'Ракетниц',
    'Арасака', 'Милитех', 'Militech', 'Кан-Тао', 'Биотех', 'Петра',
    'нейропорт', 'Нейропорт', 'Нейролинк', 'нейролинк',
    'Киберирука', 'киберирука', 'кибероптика', 'Кибероптика',
    'патрон', 'Патрон', 'боеприпас',
    'банд', 'ганг', 'фракц',
]

IGNORE = [r'банд', r'ганг', r'фракц']


def main():
    if not os.path.exists(DEC):
        print('нет декодированного файла:', DEC)
        return 1
    dec = open(DEC, encoding='utf-8').read()
    with open(OUT, 'w', encoding='utf-8') as f:
        for p in PATTERNS:
            if p in IGNORE:
                idxs = [m.start() for m in re.finditer(p, dec, re.IGNORECASE)]
            else:
                idxs = [m.start() for m in re.finditer(re.escape(p), dec)]
            f.write('===== %s  count=%d\n' % (p, len(idxs)))
            shown = 0
            for i in idxs:
                if shown >= 8:
                    break
                snippet = dec[max(0, i - 170):i + 240].replace('\n', ' ')
                f.write('   ...%s...\n' % snippet)
                shown += 1
            f.write('\n')
    print('report ->', OUT)
    return 0


if __name__ == '__main__':
    sys.exit(main())
