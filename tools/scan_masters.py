# -*- coding: utf-8 -*-
r"""Сканирует app_catalog.json: какие мастер-массивы содержат записи
по форме похожие на оружие/броню/импланты/корпорации/фракции.
Отчёт: $TEMP/scan_masters.txt (UTF-8).
"""
import json
import os

TMP = os.environ.get('TEMP', '.')
OUT = os.path.join(TMP, 'scan_masters.txt')


def is_weapon(e):
    if not (isinstance(e, list) and len(e) >= 13):
        return False
    return isinstance(e[4], str) and e[4] in (
        'Дальний бой', 'Ближний бой', 'Кибероружие', 'Метательное', 'метательное')


def is_armor(e):
    if not (isinstance(e, list) and 7 <= len(e) <= 9):
        return False
    s = e[2] if isinstance(e[2], str) else ''
    return 'роня' in s or 'Щит' in s or 'щит' in s


def is_cyber(e):
    if not (isinstance(e, list) and len(e) >= 9):
        return False
    s = e[1] if isinstance(e[1], str) else ''
    return any(k in s for k in ('neural', 'optics', 'audio', 'arm', 'leg', 'torso',
                                'fashion', 'internal', 'external'))


def is_corp(e):
    if not (isinstance(e, list) and len(e) == 7):
        return False
    s = e[3] if isinstance(e[3], str) else ''
    return 'орпорац' in s or 'компани' in s.lower()


def is_faction(e):
    if not (isinstance(e, list) and len(e) == 7):
        return False
    s = e[2] if isinstance(e[2], str) else ''
    return any(k in s for k in ('банда', 'Банда', 'семья', 'милиция', 'культ',
                                'кочев', 'сообщество', 'группировка'))


def main():
    data = json.load(open(os.path.join(TMP, 'app_catalog.json'), encoding='utf-8'))
    entries = data['entries']
    masters = data['master_arrays']
    lines = []
    kinds = [('WEAPON', is_weapon), ('ARMOR', is_armor), ('CYBER', is_cyber),
             ('CORP', is_corp), ('FACTION', is_faction)]
    for kind, fn in kinds:
        lines.append('===== %s' % kind)
        found = []
        for mid, refs in masters.items():
            cnt = 0
            for r in refs:
                e = entries.get(r)
                if fn(e):
                    cnt += 1
            if cnt >= 2:
                found.append((cnt, mid, len(refs)))
        found.sort(key=lambda x: -x[0])
        for cnt, mid, total in found:
            lines.append('   %s: %d/%d' % (mid, cnt, total))
        lines.append('')
    open(OUT, 'w', encoding='utf-8').write('\n'.join(lines))
    print('report ->', OUT)


if __name__ == '__main__':
    main()
