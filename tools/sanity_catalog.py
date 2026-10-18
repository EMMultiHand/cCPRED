# -*- coding: utf-8 -*-
"""Санити-проверка вставок каталога в main.dart.js."""
import io
import json
import os

js = io.open(r'D:\Desktop\cCPRED\app\main.dart.js', encoding='utf-8').read()

out = []
out.append('размер: %d' % len(js))
for pat in ['@@RAW', ':u.x', '\\u04', "t.X6)", "t.s)"]:
    out.append('вхождений %r: %d' % (pat, js.count(pat)))

samples = [
    'B.NT,s([',
    '"Микромилашка от Hello Cutie"',
    '"B.Nm,s([',
    '"B.VL,s([',
    '"B.Ww,s([',
    'B.NT,s(',
    'u.x],t.b)',
]
for s in samples:
    i = js.find(s)
    out.append('--- %r at %d' % (s, i))
    if i >= 0:
        out.append(js[max(0, i - 80):i + 120])

# проверка хостов массивов (последние элементы перед закрытием)
for name, tail in [('weapons', 'B.NT'), ('armor', 'B.V0'), ('corps', 'B.Nm'), ('implants', 'B.VL'),
                   ('equipment', 'B.Ww')]:
    i = js.find(tail + ',s([')
    out.append('%s: хвост до вставки найден at %d' % (name, i))

# массовые проверки количеств
out.append('weapon-записей (t.b) всего: %d' % js.count(',t.b)'))
out.append('equipment-записей (t.s) всего: %d' % js.count(',t.s)'))
out.append('вставок t.b после B.NT: %s' % ('B.NT,s([' in js))
out.append('u.x как голый токен: %d' % js.count(',u.x],t.b)'))

io.open(os.path.join(os.environ['TEMP'], 'sanity_catalog.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
