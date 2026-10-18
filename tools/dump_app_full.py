# -*- coding: utf-8 -*-
r"""Дамп полных записей мастер-массивов приложения из app_catalog.json.
Файлы: $TEMP/appfull_<symbol>.txt
"""
import json
import os

TMP = os.environ.get('TEMP', '.')


def main():
    cat = json.load(open(os.path.join(TMP, 'app_catalog.json'), encoding='utf-8'))
    entries = cat['entries']
    masters = cat['master_arrays']

    out = ['entries: %d' % len(entries), 'master_arrays: %d' % len(masters)]
    k0 = next(iter(masters))
    out.append('sample masters[%s]: %s' % (k0, json.dumps(masters[k0], ensure_ascii=False)[:500]))

    for name, mdef in masters.items():
        if isinstance(mdef, list):
            refs = mdef
        elif isinstance(mdef, dict):
            refs = mdef.get('refs') or mdef.get('elements') or []
        else:
            refs = []
        lines = ['### %s (%d refs)' % (name, len(refs))]
        for i, r in enumerate(refs, 1):
            sym = r
            if isinstance(r, dict):
                sym = r.get('ref') or r.get('$ref') or ''
            ent = entries.get(sym)
            if ent is None:
                lines.append('%3d. %s = ???' % (i, r))
            else:
                lines.append('%3d. %s = %s' % (i, sym, json.dumps(ent, ensure_ascii=False)))
        open(os.path.join(TMP, 'appfull_%s.txt' % name.replace('$', '_')), 'w', encoding='utf-8').write('\n'.join(lines))

    open(os.path.join(TMP, 'appfull_index.txt'), 'w', encoding='utf-8').write('\n'.join(out))
    print('->', os.path.join(TMP, 'appfull_index.txt'))


if __name__ == '__main__':
    main()
