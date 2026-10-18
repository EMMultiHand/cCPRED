# -*- coding: utf-8 -*-
r"""Сопоставление каталогов приложения (app_catalog.json) со таблицами data-pool.

Использование:
  python tools/diff_catalogs.py <категория>
Категории: weapons, armor, implants, equipment
Отчёт: $TEMP/diff_<категория>.txt (UTF-8): списки app, сопоставления, MISSING.
"""
import json
import os
import re
import sys

TMP = os.environ.get('TEMP', '.')

# категория: (app массив(ы), dp файлы, доп. режим)
CONFIG = {
    'weapons': {
        'app': ['B.Pl'],
        'dp': ['dp_tables_equipment_weapons'],
        'tables': [0, 1, 2, 3, 4, 5, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 22],
    },
    'armor': {
        'app': ['B.S7', 'B.Wc'],
        'dp': ['dp_tables_equipment_armor'],
    },
    'implants': {
        'app': ['B.Q2'],
        'dp': ['dp_tables_chrome_implants', 'dp_tables_chrome_exotic',
               'dp_tables_chrome_borgs', 'dp_tables_chrome_pkt_implants'],
    },
    'equipment': {
        'app': ['B.Ox'],
        'dp': ['dp_tables_equipment_items', 'dp_tables_equipment_agents_accessories',
               'dp_tables_equipment_soft'],
    },
}

# ручные алиасы: dp-имя (norm) -> app-имя (norm), вводим по мере надобности
ALIASES = {
    'weapons': {
        'средний пистолет': 'средний пистолет',
    },
    'armor': {},
    'implants': {},
    'equipment': {},
}


def norm(s):
    s = s.lower().replace('ё', 'е')
    s = s.replace('®', '').replace('™', '')
    for ch in '«»"“”\'':
        s = s.replace(ch, ' ')
    s = re.sub(r'\([^)]*\)', ' ', s)
    s = re.sub(r'[^0-9a-zа-я+]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def match(a, b):
    if a == b:
        return True
    if len(a) >= 5 and len(b) >= 5 and (a in b or b in a):
        return True
    return False


def main():
    cat = sys.argv[1]
    cfg = CONFIG[cat]
    data = json.load(open(os.path.join(TMP, 'app_catalog.json'), encoding='utf-8'))
    entries = data['entries']
    masters = data['master_arrays']

    app_names = []
    for mid in cfg['app']:
        refs = masters.get(mid, [])
        for r in refs:
            e = entries.get(r)
            if isinstance(e, list) and e:
                app_names.append((r, str(e[0])))
            elif isinstance(e, str):
                app_names.append((r, e))
    app_norms = [(rid, nm, norm(nm)) for rid, nm in app_names]

    lines = []
    lines.append('===== %s: приложение %d записей' % (cat, len(app_names)))
    for i, (rid, nm, _) in enumerate(app_norms, 1):
        lines.append('  %3d. %-55s [%s]' % (i, nm[:55], rid))
    lines.append('')

    missing = []
    matched = []
    for dpf in cfg['dp']:
        p = os.path.join(TMP, dpf + '.json')
        if not os.path.exists(p):
            lines.append('!! нет файла %s' % p)
            continue
        tables = json.load(open(p, encoding='utf-8'))
        for ti, tb in enumerate(tables):
            if 'tables' in cfg and ti not in cfg['tables']:
                continue
            for row in tb['rows']:
                if not row:
                    continue
                dp_name = row[0].replace('\n', ' ')
                if not dp_name.strip():
                    continue
                dn = norm(dp_name)
                if not dn:
                    continue
                # алиасы
                ali = ALIASES.get(cat, {}).get(dn)
                hit = None
                for rid, nm, an in app_norms:
                    if ali and an == ali:
                        hit = (rid, nm)
                        break
                    if match(dn, an):
                        hit = (rid, nm)
                        break
                if hit:
                    matched.append((dp_name, hit[1]))
                else:
                    missing.append((dpf, ti, dp_name))

    lines.append('===== СОПОСТАВЛЕНО: %d' % len(matched))
    for d, a in matched:
        if norm(d) != norm(a):
            lines.append('   dp: %-52s -> app: %s' % (d[:52], a[:60]))
    lines.append('')
    lines.append('===== ОТСУТСТВУЕТ В ПРИЛОЖЕНИИ: %d' % len(missing))
    for dpf, ti, nm in missing:
        lines.append('   [%s#%d] %s' % (dpf.replace('dp_tables_', ''), ti, nm[:100]))
    out = os.path.join(TMP, 'diff_%s.txt' % cat)
    open(out, 'w', encoding='utf-8').write('\n'.join(lines))
    print('report ->', out, '| missing:', len(missing))


if __name__ == '__main__':
    main()
