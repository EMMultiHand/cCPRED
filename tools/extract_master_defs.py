# -*- coding: utf-8 -*-
r"""Извлекает из main.dart.js точные тексты определений символов B.xxx=s([...],t.X).
Сохранение: $TEMP/master_defs.json
Печать превью: $TEMP/master_defs_preview.txt
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, 'app', 'main.dart.js')
TMP = os.environ.get('TEMP', '.')

SYMS = [
    'B.Pl', 'B.S7', 'B.Wc', 'B.Q2', 'B.Ox', 'B.O5', 'B.RG',
    'B.dY', 'B.jT', 'B.VC', 'B.Za', 'B.Sx', 'B.MG', 'B.TV', 'B.Vb', 'B.VZ',
    'B.Od', 'B.bLY',
]


def read_js_string(t, i):
    """i указывает на открывающую кавычку; возвращает индекс после закрывающей."""
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
    raise ValueError('unterminated string')


def find_array_end(t, i):
    """i указывает на '['; возвращает индекс сразу после парной ']'."""
    assert t[i] == '['
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


def main():
    t = open(APP, encoding='utf-8', errors='replace').read()
    defs = {}
    preview = []
    for sym in SYMS:
        pat = sym + '=s(['
        idx = t.find(pat)
        if idx < 0:
            preview.append('%s: НЕ НАЙДЕНО' % sym)
            continue
        arr_start = idx + len(sym) + len('=s(')
        arr_end = find_array_end(t, arr_start)
        # после массива ожидаем ,t.X)
        tail = t[arr_end:arr_end + 12]
        m = re.match(r',t\.[A-Za-z0-9_$]+\)', tail)
        full_end = arr_end + (m.end() if m else 1)
        text = t[idx:full_end]
        defs[sym] = {'start': idx, 'end': full_end, 'text': text, 'tail': tail}
        preview.append('%s: длина %d, хвост %r' % (sym, len(text), tail[:14]))
        preview.append('   ' + text[:220].replace('\n', ' '))
    with open(os.path.join(TMP, 'master_defs.json'), 'w', encoding='utf-8') as f:
        json.dump(defs, f, ensure_ascii=False, indent=1)
    open(os.path.join(TMP, 'master_defs_preview.txt'), 'w', encoding='utf-8').write(
        '\n'.join(preview))
    print('defs:', len(defs), '-> $TEMP/master_defs.json')


if __name__ == '__main__':
    main()
