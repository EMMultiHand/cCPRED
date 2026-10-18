# -*- coding: utf-8 -*-
"""Сводка имён дополнений по разделам для UI-проверок."""
import io
import json
import os

d = json.load(io.open(r'D:\Desktop\cCPRED\tools\dp_additions.json', encoding='utf-8'))
out = []
out.append('== AMMO ==')
for k, v in d.get('ammo', {}).items():
    out.append('%s (%d): %s' % (k, len(v), '; '.join(v)))
out.append('')
out.append('== ARMOR (%d) ==' % len(d['armor']))
for a in d['armor']:
    out.append('%s | %s | %s | sppen=%s/%s | %s | rules=%s' % (a[0], a[1], a[2], a[3], a[4], a[5], (a[7] if len(a) > 7 else '-')))
out.append('')
out.append('== IMPLANTS первые 25 ==')
for i in d['implants'][:25]:
    out.append('%s | %s | %s | %s | %s | %s' % (i[0], i[1], i[2], i[3], i[4], i[5]))
out.append('')
out.append('== EQUIPMENT первые 30 ==')
for e in d['equipment'][:30]:
    out.append('%s | %s | %s | %s' % (e[0], e[1], e[2], e[3]))
out.append('')
out.append('== CORPS ==')
for c in d['corps']:
    out.append('%s | рейтинг %s | %s' % (c[0], c[1], c[2]))
io.open(os.path.join(os.environ['TEMP'], 'additions_names.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
