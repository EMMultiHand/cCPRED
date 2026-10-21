# -*- coding: utf-8 -*-
"""Adds the "Датапул" tile to the Agent screen right after "Фракции".

The tile opens the existing HTML side panel through window.__cprefOpenDataPool(),
which is exposed by app/index.html. Idempotent.

The compiled bundle stores non-ASCII as lowercase \\uXXXX escapes, so all
Russian literals below go through esc() before searching/inserting.
"""
import io
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLE = os.path.join(ROOT, 'app', 'main.dart.js')
BACKUP = os.path.join(ROOT, 'tools', '_main.dart.js.before_agent_datapool')


def esc(text):
    out = []
    for ch in text:
        if ord(ch) < 128:
            out.append(ch)
        else:
            out.append('\\u%04x' % ord(ch))
    return ''.join(out)


src = io.open(BUNDLE, encoding='utf-8').read()

if esc('"Фракции","Датапул"') in src:
    print('already patched')
    sys.exit(0)

if not os.path.exists(BACKUP):
    shutil.copyfile(BUNDLE, BACKUP)
    print('backup:', BACKUP)

changes = 0


def rep(old, new, tag):
    global src, changes
    n = src.count(old)
    if n != 1:
        raise SystemExit('FAIL %s: expected 1 occurrence, got %d' % (tag, n))
    src = src.replace(old, new, 1)
    changes += 1
    print('ok', tag)


DP = esc('Датапул')
FR = esc('Фракции')

# 1. Agent tab list: append "Датапул" after "Фракции".
rep(
    'B.rO=s(["%s","%s","%s","%s","%s","%s"],t.s)' % (
        esc('Контакты'), esc('Карта'), esc('Заметки'),
        esc('Магазин'), esc('Корпорации'), FR),
    'B.rO=s(["%s","%s","%s","%s","%s","%s","%s"],t.s)' % (
        esc('Контакты'), esc('Карта'), esc('Заметки'),
        esc('Магазин'), esc('Корпорации'), FR, DP),
    'tab list',
)

# 2. Icon for the new tab (history_edu_outlined, present in the tree-shaken font).
rep(
    'case"%s":return B.JF\ndefault:return B.Jw}}' % FR,
    'case"%s":return B.JF\ncase"%s":return new A.b7(61697,"MaterialIcons",!1)\ndefault:return B.Jw}}' % (FR, DP),
    'tab icon',
)

# 3. Wide layout: tile width and loop bound follow the tab count.
rep(
    'if(j.a>i){s=i<430?92:112\n'
    'r=Math.min(s,k/6)\n'
    'i=A.a([],t.p)\n'
    'for(q=this.a,p=0;p<6;++p){o=B.rO[p]',
    'if(j.a>i){s=i<430?92:112\n'
    'r=Math.min(s,k/B.rO.length)\n'
    'i=A.a([],t.p)\n'
    'for(q=this.a,p=0;p<B.rO.length;++p){o=B.rO[p]',
    'wide grid',
)

# 4. Portrait grid item count.
rep(
    'new A.amj(this.a),6,B.ey,!0)',
    'new A.amj(this.a),B.rO.length,B.ey,!0)',
    'portrait grid',
)

OPEN = ('var t=this.b;if(t==="%s"){try{if(typeof window!=="undefined"&&'
        'window.__cprefOpenDataPool)window.__cprefOpenDataPool()}catch(e){}return null}'
        'return this.a.y=this.b' % DP)

# 5-6. Tab tap handlers: "Датапул" opens the panel instead of selecting a section.
rep(
    'A.amf.prototype={\n$0(){return this.a.y=this.b},',
    'A.amf.prototype={\n$0(){%s},' % OPEN,
    'wide tap',
)
rep(
    'A.amd.prototype={\n$0(){return this.a.y=this.b},',
    'A.amd.prototype={\n$0(){%s},' % OPEN,
    'portrait tap',
)

io.open(BUNDLE, 'w', encoding='utf-8', newline='').write(src)
print('patched:', changes, 'edits')
