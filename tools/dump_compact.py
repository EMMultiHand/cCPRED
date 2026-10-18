# -*- coding: utf-8 -*-
r"""Компактные дампы записей приложения: Name | Type | Category | Source | Price | Humanity
Файлы: $TEMP/compact_<sym>.txt
"""
import json
import os

TMP = os.environ.get('TEMP', '.')

SYMS = ['B.Q2', 'B.Ox', 'B.O5', 'B.RG', 'B.S7', 'B.Wc', 'B.Pl', 'B.dY']


def main():
    cat = json.load(open(os.path.join(TMP, 'app_catalog.json'), encoding='utf-8'))
    entries = cat['entries']
    masters = cat['master_arrays']

    for name in SYMS:
        refs = masters.get(name)
        if refs is None:
            print('missing master', name)
            continue
        lines = []
        for i, r in enumerate(refs, 1):
            sym = r if isinstance(r, str) else (r.get('ref') or r.get('$ref'))
            ent = entries.get(sym)
            if ent is None:
                lines.append('%4d. %s = ??? %s' % (i, sym, r))
                continue
            if isinstance(ent, dict):
                # nested map (e.g. ammo families)
                lines.append('%4d. %s = %s' % (i, sym, json.dumps(ent, ensure_ascii=False)[:400]))
                continue
            parts = []
            for x in ent:
                if isinstance(x, dict) and '$ref' in x:
                    sx = '{%s}' % x['$ref']
                elif isinstance(x, list):
                    sx = json.dumps(x, ensure_ascii=False)
                else:
                    sx = str(x)
                parts.append(sx)
            line = ' | '.join(parts)
            if len(line) > 330:
                line = line[:330] + '…'
            lines.append('%4d. %s = %s' % (i, sym, line))
        open(os.path.join(TMP, 'compact_%s.txt' % name.replace('$', '_')), 'w', encoding='utf-8').write('\n'.join(lines))
        print('->', name, len(refs))


if __name__ == '__main__':
    main()
