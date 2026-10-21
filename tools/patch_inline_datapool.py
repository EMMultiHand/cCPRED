# -*- coding: utf-8 -*-
"""Turns the "Датапул" agent tab into a normal selectable section.

The previous patch (patch_agent_datapool.py) only added the tile and made it
open the floating HTML panel.  This patch:

  * makes the tile set the agent section to "Датапул" (like every other tile)
    and notifies the HTML layer through window.__cprefDPSection(name);
  * renders an empty Flutter section for "Датапул" (the HTML iframe is placed
    in that area by app/index.html);
  * reports page changes (rail / bottom bar) through window.__cprefDPPage(),
    the current agent section through window.__cprefDPState(), and the
    character sheet being closed through window.__cprefDPHide().

Idempotent.  The compiled bundle stores non-ASCII as lowercase \\uXXXX
escapes, so all Russian literals go through esc().
"""
import io
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLE = os.path.join(ROOT, 'app', 'main.dart.js')
BACKUP = os.path.join(ROOT, 'tools', '_main.dart.js.before_inline_datapool')


def esc(text):
    out = []
    for ch in text:
        if ord(ch) < 128:
            out.append(ch)
        else:
            out.append('\\u%04x' % ord(ch))
    return ''.join(out)


src = io.open(BUNDLE, encoding='utf-8').read()

MARK = 'window.__cprefDPSection'
if MARK in src:
    print('already patched')
    sys.exit(0)

if not os.path.exists(BACKUP):
    shutil.copyfile(BUNDLE, BACKUP)
    print('backup:', BACKUP)

changes = 0


def rep(old, new, tag, count=1):
    global src, changes
    n = src.count(old)
    if n != count:
        raise SystemExit('FAIL %s: expected %d occurrence(s), got %d' % (tag, count, n))
    src = src.replace(old, new, count)
    changes += 1
    print('ok', tag)


DP = esc('Датапул')
FR = esc('Фракции')

# 1. Tile tap handlers: select "Датапул" instead of opening the floating panel.
#    Both the wide and the portrait handler share the same $0 body, so replace
#    all occurrences.
OLD_TAP = ('$0(){var t=this.b;if(t==="%s"){try{if(typeof window!=="undefined"&&'
           'window.__cprefOpenDataPool)window.__cprefOpenDataPool()}catch(e){}return null}'
           'return this.a.y=this.b},' % DP)
NEW_TAP = ('$0(){var t=this.b;try{if(typeof window!=="undefined"&&'
           'window.__cprefDPSection)window.__cprefDPSection(t)}catch(e){}'
           'return this.a.y=t},')
rep(OLD_TAP, NEW_TAP, 'tile tap handlers', count=2)

# 2. Empty section body for "Датапул" (otherwise the notes editor is shown).
rep(
    'else if(n==="%s")o.push(g.a7F())\nelse{n=g.d\n' % FR,
    'else if(n==="%s")o.push(g.a7F())\nelse if(n!=="%s"){n=g.d\n' % (FR, DP),
    'empty section',
)

# 3. Tell the HTML layer which agent section is being built.
rep(
    '}return A.L(o,B.r,c,B.e,B.f)},',
    '}try{if(typeof window!=="undefined"&&window.__cprefDPState)'
    'window.__cprefDPState(g.y)}catch(e){}\nreturn A.L(o,B.r,c,B.e,B.f)},',
    'agent build sync',
)

# 4. Rail / bottom navigation page changes.
rep(
    'H_(a){var s=this\nif(s.f===a)return',
    'H_(a){var s=this\ntry{if(typeof window!=="undefined"&&window.__cprefDPPage)'
    'window.__cprefDPPage(a)}catch(e){}\nif(s.f===a)return',
    'page change hook',
)

# 5. Character sheet back button and dispose (hide the panel).
OLD_CLOSE = ('acp(){this.hA()\nthis.a.auZ()},\n'
             'm(){var s=this\ns.hA()\n$.ai.hs(s)\ns.e.m()\ns.aH()},')
NEW_CLOSE = ('acp(){try{if(typeof window!=="undefined"&&window.__cprefDPHide)'
             'window.__cprefDPHide()}catch(e){}this.hA()\nthis.a.auZ()},\n'
             'm(){try{if(typeof window!=="undefined"&&window.__cprefDPHide)'
             'window.__cprefDPHide()}catch(e){}var s=this\ns.hA()\n$.ai.hs(s)\ns.e.m()\ns.aH()},')
rep(OLD_CLOSE, NEW_CLOSE, 'close hooks')

io.open(BUNDLE, 'w', encoding='utf-8', newline='').write(src)
print('patched:', changes, 'edits')
