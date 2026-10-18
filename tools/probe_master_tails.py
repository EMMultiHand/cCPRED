# -*- coding: utf-8 -*-
"""Точные хвосты определений мастер-массивов и списков боеприпасов (для якорей патча)."""
import json
import os

TMP = os.environ.get('TEMP', '.')

md_path = os.path.join(TMP, 'master_defs.json')
with open(md_path, encoding='utf-8') as f:
    md = json.load(f)

out = []
out.append('type: %s' % type(md).__name__)
if isinstance(md, dict):
    out.append('keys: %s' % list(md.keys())[:50])

vars_of_interest = ['B.Pl', 'B.S7', 'B.Wc', 'B.Ox', 'B.O5', 'B.Q2', 'B.dY', 'B.RG',
                    'B.jT', 'B.VC', 'B.Za', 'B.Sx', 'B.VZ', 'B.MG', 'B.TV', 'B.Vb']


def show_entry(key, val):
    if isinstance(val, dict):
        for kk in ('def', 'text', 'doc', 'code'):
            if kk in val:
                val = val[kk]
                break
        else:
            out.append('### %s: dict keys %s' % (key, list(val.keys())[:10]))
            return
    s = str(val)
    out.append('### %s (len=%d)' % (key, len(s)))
    out.append('HEAD: %s' % s[:150])
    out.append('TAIL: %s' % s[-150:])


if isinstance(md, dict):
    for k in vars_of_interest:
        if k in md:
            show_entry(k, md[k])
        else:
            out.append('### %s: NOT FOUND' % k)
elif isinstance(md, list):
    for item in md:
        if isinstance(item, dict):
            key = item.get('name') or item.get('var') or item.get('key')
            if key in vars_of_interest:
                show_entry(key, item)

# occurrences of t.X6 closings in the actual file
app_path = r'D:\Desktop\cCPRED\app\main.dart.js'
js = open(app_path, encoding='utf-8').read()
out.append('')
out.append('=== js size: %d' % len(js))
for pat in ['B.NT],t.X6)', 'B.V0],t.X6)', 'B.Ze],t.X6)', 'B.Ww],A.aN(', '],t.X6)', '],A.aN(']:
    out.append('%-16s count=%d' % (pat, js.count(pat)))

# tails for ammo families: find each var, take 120 chars before '],t.s)'
import re
for var in ['B.jT', 'B.VC', 'B.Za', 'B.Sx', 'B.VZ', 'B.MG', 'B.TV', 'B.Vb']:
    idx = js.find(var + '=s([')
    if idx < 0:
        out.append('%s: def not found' % var)
        continue
    end = js.find('],t.s)', idx)
    out.append('--- %s def tail: %s' % (var, js[max(idx, end - 160):end + 7]))

# armor shields tail, corps tail, implants tail
for var in ['B.Pl', 'B.S7', 'B.Wc', 'B.O5', 'B.Q2']:
    idx = js.find(var + '=')
    if idx < 0:
        out.append('%s: def not found' % var)
        continue
    end = js.find('],t.X6)', idx)
    if end < 0:
        out.append('%s: closing ],t.X6) not found' % var)
        continue
    out.append('--- %s def head: %s' % (var, js[idx:idx + 60]))
    out.append('--- %s def tail: %s' % (var, js[max(idx, end - 120):end + 8]))

with open(os.path.join(TMP, 'master_tails.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('ok')
