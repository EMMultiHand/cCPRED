# -*- coding: utf-8 -*-
r"""Поиск в app_catalog.json: какие мастер-массивы содержат заданные записи;
показ записей по id. Отчёт: $TEMP/find_ids.txt
"""
import json
import os
import sys

CAT = os.path.join(os.environ.get('TEMP', '.'), 'app_catalog.json')
OUT = os.path.join(os.environ.get('TEMP', '.'), 'find_ids.txt')


def main():
    data = json.load(open(CAT, encoding='utf-8'))
    entries = data['entries']
    masters = data['master_arrays']
    targets = sys.argv[1:] or ['B.Tl', 'B.P1', 'B.Sb', 'B.S7', 'B.Wc']
    lines = []
    for t in targets:
        lines.append('== %s' % t)
        if t in entries:
            lines.append('   entry: %s' % json.dumps(entries[t], ensure_ascii=False)[:300])
        else:
            lines.append('   entry: НЕТ в записях')
        owners = [mid for mid, refs in masters.items() if t in refs]
        lines.append('   в мастер-массивах: %s' % owners)
        for mid in owners:
            lines.append('      %s (len %d): первые 5 = %s' % (mid, len(masters[mid]), masters[mid][:5]))
        lines.append('')
    # также перечислим мастер-массивы, содержащие 5+ записей с полем 2 начинающимся на 'Броня'
    lines.append('== мастер-массивы с записями, у которых поле[2] содержит "Броня":')
    for mid, refs in masters.items():
        cnt = 0
        for r in refs[:400]:
            e = entries.get(r)
            if isinstance(e, list) and len(e) > 3 and isinstance(e[2], str) and 'рон' in e[2]:
                cnt += 1
        if cnt >= 3:
            lines.append('   %s: %d таких из %d' % (mid, cnt, len(refs)))
    open(OUT, 'w', encoding='utf-8').write('\n'.join(lines))
    print('report ->', OUT)


if __name__ == '__main__':
    sys.exit(main())
