# -*- coding: utf-8 -*-
r"""Выгрузка таблиц боеприпасов/гранат/модификаций data-pool: $TEMP/cmp_dp_ammo.txt"""
import json
import os

TMP = os.environ.get('TEMP', '.')


def main():
    data = json.load(open(os.path.join(TMP, 'dp_tables_equipment_weapons.json'), encoding='utf-8'))
    lines = []
    for ti in [6, 7, 8, 20, 21, 23, 24]:
        tb = data[ti]
        lines.append('##### [%d] %s | %d строк' % (ti, tb['section'], len(tb['rows'])))
        lines.append('   колонки: ' + ' | '.join(tb['headers']))
        for ri, row in enumerate(tb['rows'], 1):
            cells = [c.replace('\n', ' ')[:700] for c in row]
            lines.append('%3d. %s' % (ri, ' | '.join(cells)))
        lines.append('')
    out = os.path.join(TMP, 'cmp_dp_ammo.txt')
    open(out, 'w', encoding='utf-8').write('\n'.join(lines))
    print('->', out)


if __name__ == '__main__':
    main()
