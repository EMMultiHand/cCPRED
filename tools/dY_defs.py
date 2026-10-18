# -*- coding: utf-8 -*-
r"""Определения B.aaE и списков-значений B.dY, а также конструктора A.h.
Отчёт: $TEMP/dY_defs.txt
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, 'app', 'main.dart.js')
TMP = os.environ.get('TEMP', '.')

SYMS = ['B.aaE=', 'B.a2_=', 'B.a24=', 'B.a21=', 'B.a1Z=', 'B.a22=', 'B.a20=',
        'B.a1Y=', 'B.a1X=', 'B.a1W=', 'B.a23=', 'B.a1V=', 'B.jT=', 'B.VC=',
        'B.Za=', 'B.Sx=', 'B.MG=', 'B.TV=', 'B.Vb=', 'B.VZ=']


def read_js_string(t, i):
    q = t[i]
    i += 1
    while i < len(t):
        c = t[i]
        if c == '\\':
            i += 2
            continue
        if c == q:
            return i + 1
        i += 1
    raise ValueError('unterminated')


def find_array_end(t, i):
    depth = 0
    while i < len(t):
        c = t[i]
        if c in '"\'`':
            i = read_js_string(t, i)
            continue
        if c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError('unterminated array')


def get_def(t, sym):
    i = t.find(sym)
    if i < 0:
        return None, -1
    # если это =s([ — до конца массива; иначе просто 400 символов
    j = t.find('=s([', i)
    if j == i + len(sym) - 2:  # символ сразу за ним
        arr_start = j + 3
        arr_end = find_array_end(t, arr_start)
        return t[i:arr_end + 8], i
    return t[i:i + 400], i


def main():
    t = open(APP, encoding='utf-8', errors='replace').read()
    lines = []
    for sym in SYMS:
        d, pos = get_def(t, sym)
        lines.append('===== %s @%d' % (sym, pos))
        lines.append(d if d else 'НЕ НАЙДЕНО')
        lines.append('')
    open(os.path.join(TMP, 'dY_defs.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
    print('report -> $TEMP/dY_defs.txt')


if __name__ == '__main__':
    main()
