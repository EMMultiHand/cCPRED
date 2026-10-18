# -*- coding: utf-8 -*-
r"""Отчёт по JSON таблиц data-pool: секции, колонки, первые строки.
Использование: python tools/dp_report.py dp_tables_equipment_weapons
Отчёт: $TEMP/dp_view.txt (UTF-8)
"""
import json
import os
import sys

TMP = os.environ.get('TEMP', '.')
OUT = os.path.join(TMP, 'dp_view.txt')


def main():
    name = sys.argv[1]
    nrows = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    data = json.load(open(os.path.join(TMP, name + '.json'), encoding='utf-8'))
    lines = []
    for i, tb in enumerate(data):
        lines.append('===== таблица %d: %s | строк: %d' % (i, tb['section'], len(tb['rows'])))
        lines.append('   колонки: ' + ' | '.join(tb['headers']))
        for r in tb['rows'][:nrows]:
            cells = [c.replace('\n', ' ⏎ ')[:90] for c in r]
            lines.append('   - ' + ' || '.join(cells))
        lines.append('')
        # все названия из первой колонки
        names = [r[0][:60] if r else '' for r in tb['rows']]
        lines.append('   НАЗВАНИЯ: ' + '; '.join(names[:60]))
        if len(names) > 60:
            lines.append('   ... ещё %d' % (len(names) - 60))
        lines.append('')
    open(OUT, 'w', encoding='utf-8').write('\n'.join(lines))
    print('report ->', OUT)


if __name__ == '__main__':
    main()
