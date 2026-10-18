# -*- coding: utf-8 -*-
"""Есть ли указанные имена в наших дополнениях (оружие)."""
import io
import json
import os

d = json.load(io.open(r'D:\Desktop\cCPRED\tools\dp_additions.json', encoding='utf-8'))
names = [w[0] for w in d['weapons']]
tgt = ['Боевой Бумеранг Рейнджер', 'Кендаши Моно-Звезда', 'Утилитарный Томагавк',
       'Боевой Бумеранг', 'Моно-Звезда', 'Dai Lung Streetmaster']
out = []
for t in tgt:
    hits = [n for n in names if t.lower() in n.lower()]
    out.append('%s -> %s' % (t, hits if hits else 'НЕТ'))
io.open(os.path.join(os.environ['TEMP'], 'check_names2.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
