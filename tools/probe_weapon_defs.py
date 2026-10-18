# -*- coding: utf-8 -*-
"""Тексты записей оружия и словарь доступности снаряжения."""
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
    return js[i:j + len(closing)]


for v in ['B.RY', 'B.RV', 'B.Po', 'B.NT', 'B.Wy']:
    out.append(def_text(v))
    out.append('')

v2 = os.path.join(TMP, 'vocab2.txt')
if os.path.exists(v2):
    lines = open(v2, encoding='utf-8').read().splitlines()
    keep = False
    for ln in lines:
        if '=== B.Ox' in ln or 'доступност' in ln.lower():
            keep = True
            out.append('>> ' + ln)
            continue
        if keep:
            if ln.startswith('==='):
                keep = False
                out.append('>> ' + ln)
            elif ln.strip():
                out.append('>> ' + ln)

with open(os.path.join(TMP, 'weapon_defs.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('ok')
