# -*- coding: utf-8 -*-
r"""Дамп полных записей массивов приложения + расшифровка u.* refs.
Отчёты в $TEMP: app_dump_<name>.txt, app_refs2.txt
"""
import json
import os
import re

TMP = os.environ.get('TEMP', '.')
JS = r'D:\Desktop\cCPRED\app\main.dart.js'


def main():
    # 0. structure of app_catalog.json
    cat = json.load(open(os.path.join(TMP, 'app_catalog.json'), encoding='utf-8'))
    out = []
    out.append('type: %s' % type(cat).__name__)
    if isinstance(cat, dict):
        keys = list(cat.keys())
        out.append('keys[%d]: %s' % (len(keys), keys[:20]))
        k0 = keys[0]
        out.append('sample %s: %s' % (k0, json.dumps(cat[k0], ensure_ascii=False)[:600]))

        # dump full entries per array
        for name in cat:
            block = cat[name]
            if not isinstance(block, dict):
                continue
            entries = block.get('entries')
            if entries is None:
                continue
            lines = ['### %s (%d entries)' % (name, len(entries))]
            for i, ent in enumerate(entries, 1):
                lines.append('%3d. %s' % (i, json.dumps(ent, ensure_ascii=False)))
            open(os.path.join(TMP, 'app_dump_%s.txt' % name.replace('$', '_')), 'w', encoding='utf-8').write('\n'.join(lines))

    # 1. resolve u.* refs from JS
    src = open(JS, encoding='utf-8', errors='replace').read()
    out.append('')
    out.append('=== windows around u.* usage ===')
    for off in [3658014, 3676760, 3814173, 4194820, 4276487, 4280271, 210611]:
        s = max(0, off - 200)
        e = min(len(src), off + 500)
        out.append('--- @%d: %s' % (off, src[s:e].replace('\n', ' ')))
        out.append('')

    out.append('=== assignment-style defs u.l= / u.h= / u.a= ===')
    for key in ['u.l', 'u.h', 'u.a']:
        pat = re.compile(re.escape(key) + r'\s*=')
        for m in pat.finditer(src):
            s = max(0, m.start() - 60)
            e = min(len(src), m.end() + 200)
            out.append('--- %s: %s' % (key, src[s:e].replace('\n', ' ')))
    out.append('')

    # 2. search for candidate strings
    out.append('=== search candidate names ===')
    for cand in ['КиберКисть с модульными пальцами', 'КиберКисть Энтузиаста', 'Киберрука с модульными пальцами', 'Киберчереп', 'КиберКисть']:
        esc = ''.join('\\u%04x' % ord(ch) if ord(ch) > 127 else ch for ch in cand)
        idxs = [m.start() for m in re.finditer(re.escape(esc), src)][:6]
        out.append('%s -> %s' % (cand, idxs))
        for off in idxs[:2]:
            s = max(0, off - 150)
            e = min(len(src), off + 250)
            out.append('    ctx: %s' % src[s:e].replace('\n', ' '))
        # also raw
        idxs2 = [m.start() for m in re.finditer(re.escape(cand), src)][:6]
        if idxs2:
            out.append('    raw -> %s' % idxs2)

    path = os.path.join(TMP, 'app_refs2.txt')
    open(path, 'w', encoding='utf-8').write('\n'.join(out))
    print('->', path)


if __name__ == '__main__':
    main()
