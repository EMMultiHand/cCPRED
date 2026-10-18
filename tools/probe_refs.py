# -*- coding: utf-8 -*-
r"""Поиск ссылок вида u.* в main.dart.js и $ref в app_catalog.json.
Отчёт: $TEMP/probe_refs.txt (UTF-8).
"""
import json
import os
import re

TMP = os.environ.get('TEMP', '.')
JS = r'D:\Desktop\cCPRED\app\main.dart.js'


def main():
    src = open(JS, encoding='utf-8', errors='replace').read()
    out = []

    # 1. Definitions of the u object / u.l, u.h, u.a usages
    out.append('=== occurrences of u.l / u.h / u.a in main.dart.js ===')
    for key in ['u.l', 'u.h', 'u.a']:
        pat = re.compile(re.escape(key) + r'(?![A-Za-z0-9_$])')
        for m in pat.finditer(src):
            s = max(0, m.start() - 60)
            e = min(len(src), m.end() + 80)
            ctx = src[s:e].replace('\n', ' ')
            out.append('--- %s @%d: %s' % (key, m.start(), ctx))
    out.append('')

    # 2. Look for the u object literal definition
    out.append('=== search for "u=" object with keys l/h/a ===')
    for m in re.finditer(r'\bu\s*=\s*\{', src):
        s = m.start()
        e = min(len(src), m.start() + 400)
        ctx = src[s:e].replace('\n', ' ')
        out.append('--- u={ @%d: %s' % (m.start(), ctx))
    out.append('')

    # 3. $ref occurrences in app_catalog.json
    out.append('=== $ref entries in app_catalog.json ===')
    cat = json.load(open(os.path.join(TMP, 'app_catalog.json'), encoding='utf-8'))
    if isinstance(cat, dict):
        items = cat.items()
    else:
        items = [(str(i), c) for i, c in enumerate(cat)]
    n = 0
    for name, block in items:
        if not isinstance(block, dict):
            continue
        entries = block.get('entries', block if isinstance(block, list) else [])
        if not isinstance(entries, list):
            continue
        for ent in entries:
            txt = json.dumps(ent, ensure_ascii=False)
            if '$ref' in txt:
                out.append('%s: %s' % (name, txt[:400]))
                n += 1
    out.append('total ref entries: %d' % n)

    path = os.path.join(TMP, 'probe_refs.txt')
    open(path, 'w', encoding='utf-8').write('\n'.join(out))
    print('->', path)


if __name__ == '__main__':
    main()
