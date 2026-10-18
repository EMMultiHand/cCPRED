# -*- coding: utf-8 -*-
"""Поиск записей с уроном вида 'XdY ZdW' в dp_additions.json и стиль урона в app_catalog.json."""
import io
import json
import os
import re

tmp = os.environ['TEMP']
d = json.load(io.open(r'D:\Desktop\cCPRED\tools\dp_additions.json', encoding='utf-8'))
pat = re.compile(r'^\d+d\d+\s+\d+d\d+$')
hits = []
for w in d['weapons']:
    dmg = str(w[6])
    if pat.match(dmg.strip()):
        hits.append((w[0], dmg))
    elif re.search(r'\d+d\d+\s+\d+d\d+', dmg):
        hits.append((w[0], dmg + '  [частично]'))

out = ['== Оружие с двойным уроном через пробел: %d ==' % len(hits)]
for n, dmg in hits:
    out.append('%s | %s' % (n, dmg))

# стиль оригинала
cat = json.load(io.open(os.path.join(tmp, 'app_catalog.json'), encoding='utf-8'))
slashes = []
def walk(o, path=''):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, path + '/' + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, path + '[%d]' % i)
walk(cat)
out.append('')
out.append('== (проверка) ключи app_catalog: %s' % ', '.join(list(cat.keys())[:10]))
io.open(os.path.join(tmp, 'dmg_check.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('ok', len(hits))
