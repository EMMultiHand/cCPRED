# -*- coding: utf-8 -*-
"""Точные тексты отдельных записей каталога приложения (поля и хвосты)."""
import os

TMP = os.environ.get('TEMP', '.')
app_path = r'D:\Desktop\cCPRED\app\main.dart.js'
js = open(app_path, encoding='utf-8').read()

out = []


def def_text(var, closing='],t.b)'):
    i = js.find(var + '=s([')
    if i < 0:
        return '%s: NOT FOUND' % var
    j = js.find(closing, i)
    if j < 0:
        return '%s: no %s after idx %d' % (var, closing, i)
    return js[i:j + len(closing)]


for v in ['B.P1', 'B.Tl', 'B.X4', 'B.MH', 'B.LR', 'B.Lg', 'B.Ze', 'B.V0', 'B.PS']:
    out.append(def_text(v))
    out.append('')

out.append('--- equipment ---')
for v in ['B.Xv', 'B.X9', 'B.Ov', 'B.Ww']:
    out.append(def_text(v, '],t.s)'))
    out.append('')

out.append('--- corps ---')
for v in ['B.Nr', 'B.Wb', 'B.Nm']:
    out.append(def_text(v))
    out.append('')

out.append('--- implants ---')
for v in ['B.Yp', 'B.Ws', 'B.VL']:
    out.append(def_text(v))
    out.append('')

with open(os.path.join(TMP, 'def_texts.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('ok')
