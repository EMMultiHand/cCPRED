# -*- coding: utf-8 -*-
r"""Печатает содержимое мастер-массивов из app_catalog.json.
Использование: python tools/dump_app_lists.py B.Pl B.Q2 ... 
Отчёт: $TEMP/app_lists.txt
"""
import json
import os
import sys

CAT = os.path.join(os.environ.get('TEMP', '.'), 'app_catalog.json')
OUT = os.path.join(os.environ.get('TEMP', '.'), 'app_lists.txt')


def sval(v):
    if isinstance(v, dict):
        if '$ref' in v:
            return '<' + v['$ref'] + '>'
        if '$raw' in v:
            return v['$raw']
        return '{%s}' % ','.join('%s=%s' % (k, sval(x)) for k, x in v.items())
    if isinstance(v, list):
        return '[%s]' % '; '.join(sval(x) for x in v[:4])
    return str(v)


def main():
    ids = sys.argv[1:]
    data = json.load(open(CAT, encoding='utf-8'))
    entries = data['entries']
    masters = data['master_arrays']
    lines = []
    for mid in ids:
        refs = masters.get(mid)
        if refs is None:
            lines.append('== %s: НЕ мастер-массив, содержимое:' % mid)
            lines.append('   ' + sval(entries.get(mid))[:500])
            continue
        lines.append('== %s (%d элементов)' % (mid, len(refs)))
        for r in refs:
            e = entries.get(r)
            if e is None:
                lines.append('   %s: ?' % r)
            elif isinstance(e, list):
                lines.append('   %s: %s' % (r, ' | '.join(str(x) for x in e[:6])[:220]))
            else:
                lines.append('   %s: %s' % (r, sval(e)[:150]))
        lines.append('')
    open(OUT, 'w', encoding='utf-8').write('\n'.join(lines))
    print('report ->', OUT)


if __name__ == '__main__':
    sys.exit(main())
