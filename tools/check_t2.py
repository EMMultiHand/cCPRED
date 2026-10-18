# -*- coding: utf-8 -*-
"""Сырые строки таблиц 2-5 + записи после сборки."""
import io
import json
import os

TMP = os.environ.get('TEMP', '.')
W = json.load(io.open(os.path.join(TMP, 'dp_tables_equipment_weapons.json'), encoding='utf-8'))
d = json.load(io.open(r'D:\Desktop\cCPRED\tools\dp_additions.json', encoding='utf-8'))

out = []
for t in (2, 5):
    out.append('##### weapons[%d] headers=%s' % (t, W[t].get('headers')))
    for row in W[t].get('rows', [])[:3]:
        out.append(json.dumps(row, ensure_ascii=False)[:500])
    out.append('')

out.append('=== сборка: первые 4 записи + записи t5 ===')
for w in d['weapons'][:4]:
    out.append(json.dumps(w, ensure_ascii=False)[:400])
for w in d['weapons']:
    if w[0] in ('SlamDance ElectroMag', 'MetaCorp Hela Smart Launcher', 'Arasaka Rapid Assault'):
        out.append(json.dumps(w, ensure_ascii=False)[:400])

io.open(os.path.join(TMP, 'check_t2.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
