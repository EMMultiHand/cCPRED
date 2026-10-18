# -*- coding: utf-8 -*-
r"""Готовит полные выгрузки каталогов приложения и data-pool для ручной сверки.
Файлы: $TEMP/cmp_app_weapons.txt, cmp_dp_weapons.txt, cmp_app_armor.txt,
cmp_dp_armor.txt, cmp_app_cyber.txt, cmp_dp_cyber.txt, cmp_app_equip.txt,
cmp_dp_equip.txt, cmp_app_corps.txt, cmp_dp_corps.txt, cmp_app_factions.txt
"""
import json
import os

TMP = os.environ.get('TEMP', '.')
CAT = json.load(open(os.path.join(TMP, 'app_catalog.json'), encoding='utf-8'))
ENT = CAT['entries']
MAS = CAT['master_arrays']


def dump_app(master, fields, path):
    lines = []
    for i, r in enumerate(MAS.get(master, []), 1):
        e = ENT.get(r)
        if not isinstance(e, list):
            lines.append('%3d. %s = %r' % (i, r, e))
            continue
        cells = []
        for fi in fields:
            v = e[fi] if fi < len(e) else ''
            if isinstance(v, dict):
                v = v.get('$ref', str(v))
            cells.append(str(v).replace('\n', ' '))
        lines.append('%3d. [%s] %s' % (i, r, ' | '.join(cells)))
    open(path, 'w', encoding='utf-8').write('\n'.join(lines))
    print(master, '->', len(lines), 'записей')


def dump_dp(files_tables, path, maxlen=400):
    lines = []
    for dpf, tids in files_tables:
        data = json.load(open(os.path.join(TMP, dpf + '.json'), encoding='utf-8'))
        for ti in tids:
            tb = data[ti]
            lines.append('##### %s [%d] %s | %d строк' % (dpf, ti, tb['section'], len(tb['rows'])))
            lines.append('   колонки: ' + ' | '.join(tb['headers']))
            for ri, row in enumerate(tb['rows'], 1):
                cells = [c.replace('\n', ' ')[:maxlen] for c in row]
                lines.append('%3d. %s' % (ri, ' | '.join(cells)))
            lines.append('')
    open(path, 'w', encoding='utf-8').write('\n'.join(lines))
    print(dpf, '->', len(lines), 'строк')


def main():
    dump_app('B.Pl', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
             os.path.join(TMP, 'cmp_app_weapons.txt'))
    dump_dp([('dp_tables_equipment_weapons', list(range(0, 6)) + list(range(9, 20)) + [22])],
            os.path.join(TMP, 'cmp_dp_weapons.txt'))
    dump_app('B.S7', [0, 1, 2, 3, 4, 5, 6, 7], os.path.join(TMP, 'cmp_app_armor.txt'))
    dump_app('B.Wc', [0, 1, 2, 3, 4, 5, 6, 7], os.path.join(TMP, 'cmp_app_armor.txt2'))
    dump_dp([('dp_tables_equipment_armor', [0]), ('dp_tables_equipment_acpa', [0, 1, 2, 3])],
            os.path.join(TMP, 'cmp_dp_armor.txt'))
    dump_app('B.Q2', [0, 1, 2, 3, 4, 5, 6, 7], os.path.join(TMP, 'cmp_app_cyber.txt'))
    dump_dp([('dp_tables_chrome_implants', list(range(12))),
             ('dp_tables_chrome_pkt_implants', [0]),
             ('dp_tables_chrome_pkt_packs', [0]),
             ('dp_tables_chrome_exotic', [0, 1, 2]),
             ('dp_tables_chrome_borgs', [0, 1])],
            os.path.join(TMP, 'cmp_dp_cyber.txt'))
    dump_app('B.Ox', [0, 1, 2, 3, 4, 5], os.path.join(TMP, 'cmp_app_equip.txt'))
    dump_dp([('dp_tables_equipment_items', [0, 1]),
             ('dp_tables_equipment_agents_accessories', [0]),
             ('dp_tables_equipment_soft', [0]),
             ('dp_tables_equipment_clothes_style', [0, 1, 2])],
            os.path.join(TMP, 'cmp_dp_equip.txt'))
    dump_app('B.O5', [0, 1, 2, 3, 4, 5, 6], os.path.join(TMP, 'cmp_app_corps.txt'))
    dump_app('B.RG', [0, 1, 2, 3, 4, 5, 6], os.path.join(TMP, 'cmp_app_factions.txt'))


if __name__ == '__main__':
    main()
