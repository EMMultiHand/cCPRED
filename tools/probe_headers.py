# -*- coding: utf-8 -*-
"""Заголовки секций ДатаПула: броня, ПКТ, экзотика, импланты."""
import io
import json
import os

TMP = os.environ.get('TEMP', '.')
out = []


def load(name):
    with io.open(os.path.join(TMP, 'dp_tables_%s.json' % name), encoding='utf-8') as f:
        return json.load(f)


for name in ['equipment_armor', 'chrome_pkt_packs', 'chrome_pkt_implants', 'chrome_exotic', 'chrome_borgs',
             'equipment_agents_accessories']:
    out.append('##### %s' % name)
    for i, sec in enumerate(load(name)):
        out.append('[%d] title=%s headers=%s rows=%d' % (
            i, sec.get('title'), sec.get('headers'), len(sec.get('rows', []))))
        if sec.get('rows'):
            out.append('   sample: %s' % json.dumps(sec['rows'][0], ensure_ascii=False)[:400])
    out.append('')

# пример сырой строки брони (СкидРоу Тренч) и ПКТ-пака
A = load('equipment_armor')
for row in A[0]['rows']:
    if row[0] in ('СкидРоу Тренч', 'МехаМэн Умная Перчатка', 'Тяжёлый Metalgear®', 'Боевая Куртка Кортик'):
        out.append('ARMOR ROW: %s' % json.dumps(row, ensure_ascii=False)[:500])

P = load('chrome_pkt_packs')
for row in P[0]['rows'][:2]:
    out.append('PKT ROW: %s' % json.dumps(row, ensure_ascii=False)[:600])

E = load('chrome_exotic')
out.append('EXOTIC ROW: %s' % json.dumps(E[0]['rows'][0], ensure_ascii=False)[:600])

io.open(os.path.join(TMP, 'dp_headers.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
