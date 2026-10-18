# -*- coding: utf-8 -*-
r"""Полные тексты 4 записей имплантов + поиск def u.* и вариаций имён."""
import os
import re

TMP = os.environ.get('TEMP', '.')
JS = r'D:\Desktop\cCPRED\app\main.dart.js'


def u_decode(s):
    return re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), s)


def main():
    src = open(JS, encoding='utf-8', errors='replace').read()
    out = []

    # full texts of key entries
    for sym in ['B.Sl', 'B.QE', 'B.OD', 'B.YF', 'B.XJ', 'B.Pn']:
        m = re.search(re.escape(sym) + r'=s\(\[', src)
        if not m:
            out.append('%s: NOT FOUND' % sym)
            continue
        seg = src[m.start():m.start() + 2600]
        end = seg.find('],t.')
        if end > 0:
            seg = seg[:end + 3]
        out.append('=== %s ===' % sym)
        out.append(u_decode(seg))
        out.append('')

    # search for def of u (var u=)
    out.append('=== u= definitions ===')
    for m in re.finditer(r'(?<![\w.$])u\s*=\s*', src):
        s = max(0, m.start() - 30)
        e = min(len(src), m.end() + 120)
        out.append('@%d: %s' % (m.start(), u_decode(src[s:e].replace('\n', ' '))))
        if m.start() > 5000000:
            pass
    out.append('')

    # find where u.l could be assigned via array/obj anywhere
    out.append('=== search literal names ===')
    for cand in ['Энтузиаста', 'Киберпальцы', 'Киберпалец-', 'Хотите узнать секрет']:
        esc = ''.join('\\u%04x' % ord(ch) if ord(ch) > 127 else ch for ch in cand)
        idxs = [m.start() for m in re.finditer(re.escape(esc), src)][:8]
        out.append('%s -> %s' % (cand, idxs))

    path = os.path.join(TMP, 'app_refs3.txt')
    open(path, 'w', encoding='utf-8').write('\n'.join(out))
    print('->', path)


if __name__ == '__main__':
    main()
