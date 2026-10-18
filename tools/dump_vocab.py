# -*- coding: utf-8 -*-
"""Словарь источников приложения + структура dp-таблиц (оружие/броня/импланты)."""
import json
import os

TMP = os.environ.get('TEMP', '.')


def main():
    cat = json.load(open(os.path.join(TMP, 'app_catalog.json'), encoding='utf-8'))
    entries = cat['entries']
    masters = cat['master_arrays']
    out = []

    # --- sources of app weapons (B.Pl), implants (B.Q2), equipment (B.Ox), corps (B.O5)
    def collect(master, idx):
        vals = {}
        for r in masters.get(master, []):
            sym = r if isinstance(r, str) else (r.get('ref') or r.get('$ref'))
            ent = entries.get(sym)
            if isinstance(ent, list) and len(ent) > idx:
                v = ent[idx]
                if isinstance(v, str):
                    vals[v] = vals.get(v, 0) + 1
        return vals

    out.append('=== B.Pl sources (idx2) ===')
    for k, v in sorted(collect('B.Pl', 2).items(), key=lambda x: -x[1]):
        out.append('  %s  x%d' % (k, v))
    out.append('')
    out.append('=== B.Q2 sources (idx3) ===')
    for k, v in sorted(collect('B.Q2', 3).items(), key=lambda x: -x[1]):
        out.append('  %s  x%d' % (k, v))
    out.append('')
    out.append('=== B.Ox sources (idx2) ===')
    for k, v in sorted(collect('B.Ox', 2).items(), key=lambda x: -x[1]):
        out.append('  %s  x%d' % (k, v))
    out.append('')
    out.append('=== B.Ox categories (idx1) ===')
    for k, v in sorted(collect('B.Ox', 1).items(), key=lambda x: -x[1]):
        out.append('  %s  x%d' % (k, v))
    out.append('')
    out.append('=== B.O5 sources (idx4) ===')
    for k, v in sorted(collect('B.O5', 4).items(), key=lambda x: -x[1]):
        out.append('  %s  x%d' % (k, v))
    out.append('')
    out.append('=== B.O5 types (idx2) ===')
    for k, v in sorted(collect('B.O5', 2).items(), key=lambda x: -x[1]):
        out.append('  %s  x%d' % (k, v))
    out.append('')
    out.append('=== B.Q2 categories (idx2) ===')
    for k, v in sorted(collect('B.Q2', 2).items(), key=lambda x: -x[1]):
        out.append('  %s  x%d' % (k, v))
    out.append('')
    out.append('=== B.Q2 types (idx1) ===')
    for k, v in sorted(collect('B.Q2', 1).items(), key=lambda x: -x[1]):
        out.append('  %s  x%d' % (k, v))
    out.append('')

    # --- dp weapons structure
    dpw = json.load(open(os.path.join(TMP, 'dp_tables_equipment_weapons.json'), encoding='utf-8'))
    out.append('=== dp weapons sections ===')
    for i, sec in enumerate(dpw):
        hdr = sec.get('headers') or sec.get('columns') or []
        rows = sec.get('rows', [])
        out.append('[%d] %s | %d rows | headers: %s' % (i, sec.get('section'), len(rows), ' | '.join(map(str, hdr))))
    out.append('')
    out.append('=== dp weapons sample rows ===')
    for i in [0, 1, 2, 3, 4, 5, 9, 10, 11, 14, 17, 19, 22]:
        if i < len(dpw):
            sec = dpw[i]
            out.append('[%d] %s' % (i, sec.get('section')))
            for r in sec.get('rows', [])[:2]:
                out.append('    %s' % json.dumps(r, ensure_ascii=False))
    out.append('')

    # --- dp armor
    dpa = json.load(open(os.path.join(TMP, 'dp_tables_equipment_armor.json'), encoding='utf-8'))
    out.append('=== dp armor sections ===')
    for i, sec in enumerate(dpa):
        hdr = sec.get('headers') or []
        rows = sec.get('rows', [])
        out.append('[%d] %s | %d rows | headers: %s' % (i, sec.get('section'), len(rows), ' | '.join(map(str, hdr))))
    out.append('')
    out.append('=== dp armor sample rows (0-5) ===')
    for i in range(min(6, len(dpa))):
        sec = dpa[i]
        out.append('[%d] %s' % (i, sec.get('section')))
        for r in sec.get('rows', [])[:2]:
            out.append('    %s' % json.dumps(r, ensure_ascii=False)[:600])
    out.append('')

    # --- dp implants structure
    dpi = json.load(open(os.path.join(TMP, 'dp_tables_chrome_implants.json'), encoding='utf-8'))
    out.append('=== dp implants sections ===')
    for i, sec in enumerate(dpi):
        hdr = sec.get('headers') or []
        rows = sec.get('rows', [])
        out.append('[%d] %s | %d rows | headers: %s' % (i, sec.get('section'), len(rows), ' | '.join(map(str, hdr))))

    open(os.path.join(TMP, 'vocab.txt'), 'w', encoding='utf-8').write('\n'.join(out))
    print('->', os.path.join(TMP, 'vocab.txt'))


if __name__ == '__main__':
    main()
