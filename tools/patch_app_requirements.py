# -*- coding: utf-8 -*-
"""Патч требований установки киберимплантов в app/main.dart.js (идемпотентно).

Что делает:
  1. Ω (эндоскелет) взаимно исключается с Σ и β (как Σ/β между собой).
  2. Блок проверок в конце aVD (между маркерами /*CPSREQ1*/ /*CPSREQ2*/):
     - Ω: ТЕЛ 10 + 3 "Усиленные мышцы и усиленные кости" (+ взаимное исключение);
     - 3 Cкелета: (ТЕЛ 8 + 2 мышц) ИЛИ 2 "Личный Порт";
     - 3 Модернизации: установлен любой Имплантированный Эндоскелет (Σ/β/Ω);
     - Броня Драгуна (+МЕТАЛГИР): ТЕЛ 16 или установленный корпус ПКТ;
     - корпуса ПКТ: требуется БИОСИСТЕМА и только один корпус ПКТ;
     - КиберПроводник Zetatech, Встроенный: требуется БИОСИСТЕМА.
  3. aVE: лимит "Усиленные мышцы и усиленные кости" 2 -> 3 (для Ω).
  4. aaH/B.CQ: добавлены "Керензиков" и "Эксперементальный Сандевистан Девида"
     (правило "только один ускоритель").
  5. Зона "Голова": пара в B.N0 и зона "head" в шаблон персонажа (cyberware).
"""
import io
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, 'app', 'main.dart.js')
ADD = os.path.join(ROOT, 'tools', 'dp_additions.json')

report = []


def log(s):
    report.append(s)


def u(s):
    """Эскейп не-ASCII в \\uXXXX (как в файле приложения)."""
    return ''.join(ch if ord(ch) < 0x7f else '\\u%04x' % ord(ch) for ch in s)


def apply1(js, title, old, new):
    c = js.count(old)
    if c == 0 and new != old and js.count(new) == 1:
        log('SKIP (уже применено): %s' % title)
        return js
    if c != 1:
        raise SystemExit('!! Якорь не уникален (%d): %s\n%s' % (c, title, old[:120]))
    js2 = js.replace(old, new)
    log('OK: %s' % title)
    return js2


# ---------- имена из dp_additions.json (источник истины) ----------
data = json.load(io.open(ADD, encoding='utf-8'))
impl = data['implants']
byname = {}
for rec in impl:
    byname[rec[0]] = rec

OM = '\u0418\u043c\u043f\u043b\u0430\u043d\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u044b\u0439 \u042d\u043d\u0434\u043e\u0441\u043a\u0435\u043b\u0435\u0442 \u03a9 (\u041e\u041c\u0415\u0413\u0410)'
SK = ['C\u043a\u0435\u043b\u0435\u0442 \u041b\u0424-001 SWAT',
      'C\u043a\u0435\u043b\u0435\u0442 \u0424\u016b\u043c\u0430 \u041a\u043e\u0442\u0430\u0440\u014d',
      'C\u043a\u0435\u043b\u0435\u0442 \u0412\u0435\u0440\u043c\u0438\u043b\u0438\u043e\u043d']
MD = ['\u041c\u041e\u0414\u0415\u0420\u041d\u0418\u0417\u0410\u0426\u0418\u042f \u0412\u041d\u0423\u0422\u0420\u0415\u041d\u041d\u0415\u0419 \u0413\u0418\u0414\u0420\u0410\u0412\u041b\u0418\u041a\u0418',
      '\u0422\u042e\u041d\u0418\u041d\u0413 \u0412\u0415\u0420. \u041c\u041e\u0414\u0415\u0420\u041d\u0418\u0417\u0410\u0426\u0418\u042f \u0412\u041d\u0423\u0422\u0420\u0415\u041d\u041d\u0415\u0419 \u0413\u0418\u0414\u0420\u0410\u0412\u041b\u0418\u041a\u0418',
      '\u0421\u041e\u0412\u0415\u0420\u0428\u0415\u041d\u041d\u0410\u042f \u041c\u041e\u0414\u0415\u0420\u041d\u0418\u0417\u0410\u0426\u0418\u042f \u0412\u041d\u0423\u0422\u0420\u0415\u041d\u041d\u0415\u0419 \u0413\u0418\u0414\u0420\u0410\u0412\u041b\u0418\u041a\u0418']
DR = ['\u0411\u0440\u043e\u043d\u044f \u0414\u0440\u0430\u0433\u0443\u043d\u0430',
      '\u0411\u0440\u043e\u043d\u044f \u0414\u0440\u0430\u0433\u0443\u043d\u0430 (\u041c\u0415\u0422\u0410\u041b\u0413\u0418\u0420)']
KP = '\u041a\u0438\u0431\u0435\u0440\u041f\u0440\u043e\u0432\u043e\u0434\u043d\u0438\u043a Zetatech, \u0412\u0441\u0442\u0440\u043e\u0435\u043d\u043d\u044b\u0439'
BS = '\u0411\u0418\u041e\u0421\u0418\u0421\u0422\u0415\u041c\u0410'
CC = '\u041a\u0435\u0440\u0435\u043d\u0437\u0438\u043a\u043e\u0432'
CD = '\u042d\u043a\u0441\u043f\u0435\u0440\u0435\u043c\u0435\u043d\u0442\u0430\u043b\u044c\u043d\u044b\u0439 \u0421\u0430\u043d\u0434\u0435\u0432\u0438\u0441\u0442\u0430\u043d \u0414\u0435\u0432\u0438\u0434\u0430'
MUS = '\u0423\u0441\u0438\u043b\u0435\u043d\u043d\u044b\u0435 \u043c\u044b\u0448\u0446\u044b \u0438 \u0443\u0441\u0438\u043b\u0435\u043d\u043d\u044b\u0435 \u043a\u043e\u0441\u0442\u0438'
CAT_PKT = '\u041a\u043e\u0440\u043f\u0443\u0441 \u041f\u041a\u0422'
LP = '\u041b\u0438\u0447\u043d\u044b\u0439 \u041f\u043e\u0440\u0442'

missing = [n for n in ([OM] + SK + MD + DR + [KP, BS, CC, CD]) if n not in byname]
if missing:
    raise SystemExit('!! Нет имён в dp_additions.json: %r' % missing)
# контроль категорий
for n in [CC, CD]:
    if byname[n][2] != '\u041e\u043f\u0446\u0438\u044f \u041d\u0435\u0439\u0440\u043e\u043b\u0438\u043d\u043a\u0430':
        raise SystemExit('!! Категория %s изменилась: %r' % (n, byname[n][2]))
byname_pkt = [r[0] for r in impl if isinstance(r, list) and len(r) > 2 and r[2] == CAT_PKT]
log('ПКТ-корпусов в источнике: %d' % len(byname_pkt))

# ---------- чтение файла ----------
js = io.open(MAIN, encoding='utf-8').read()
orig_len = len(js)

# ---------- 0. снять старый блок (идемпотентность) ----------
M1 = '/*CPSREQ1*/'
M2 = '/*CPSREQ2*/'
if M1 in js and M2 in js:
    i1 = js.find(M1)
    i2 = js.find(M2) + len(M2)
    a = js[:i1]  # заканчивается на '\n' после '...Кибераудио."'
    b = js[i2:]
    if b.startswith('\n'):
        b = b[1:]
    js = a + b
    log('Старый блок CPSREQ снят')

# ---------- 1. Σ/β: взаимное исключение с Ω ----------
om_lit = u('"%s"' % OM)
sigma_old = 'if(c===p){if(A.jW(m,o)>0)return n'
sigma_new = 'if(c===p){if(A.jW(m,o)>0||A.jW(m,%s)>0)return n' % om_lit
js = apply1(js, '\u03a3: исключение с \u03a9', sigma_old, sigma_new)
beta_old = 'if(c===o){if(A.jW(m,p)>0)return n'
beta_new = 'if(c===o){if(A.jW(m,p)>0||A.jW(m,%s)>0)return n' % om_lit
js = apply1(js, '\u03b2: исключение с \u03a9', beta_old, beta_new)

# ---------- 2. Блок проверок в хвосте aVD ----------
pf = lambda s: '(%s)' % '||'.join('c===%s' % u('"%s"' % s) for s in s)
mus_lit = u('"%s"' % MUS)
lp_lit = u('"%s"' % LP)
om_lit2 = u('"%s"' % OM)
cc_lit = u('"%s"' % CC)
cat_pkt_lit = u('"%s"' % CAT_PKT)
bs_lit = u('"%s"' % BS)
block = (
    'var q2=A.mG(c),q3,q4,j\n'
    'if(c===%s){if(A.jW(m,p)>0||A.jW(m,o)>0)return n\n'
    'if(s<3||r<10)return%s}\n'
    'if(%s){if(!((s>=2&&r>=8)||A.jW(m,%s)>=2))return%s}\n'
    'if(%s){if(A.jW(m,p)+A.jW(m,o)+A.jW(m,%s)<=0)return%s}\n'
    'if(%s){q4=!1\n'
    'for(j=0;j<m.length;j++){q3=A.mG(m[j])\n'
    'if(q3!=null&&q3.h(0,"category")===%s){q4=!0\n'
    'break}}\n'
    'if(!q4&&r<16)return%s}\n'
    'if(q2!=null&&q2.h(0,"category")===%s){if(A.jW(m,%s)<=0)return%s\n'
    'q4=!1\n'
    'for(j=0;j<m.length;j++){q3=A.mG(m[j])\n'
    'if(q3!=null&&q3.h(0,"category")===%s){q4=!0\n'
    'break}}\n'
    'if(q4)return%s}\n'
    'if(c===%s&&A.jW(m,%s)<=0)return%s'
) % (
    om_lit2,
    u('"\u0422\u0440\u0435\u0431\u0443\u0435\u0442\u0441\u044f \u0422\u0415\u041b 10 \u0438 3 \u0443\u0441\u0442\u0430\u043d\u043e\u0432\u043b\u0435\u043d\u043d\u044b\u0445 \u0438\u043c\u043f\u043b\u0430\u043d\u0442\u0430 \u201c%s\u201d."' % MUS),
    pf(SK),
    lp_lit,
    u('"\u0422\u0440\u0435\u0431\u0443\u0435\u0442\u0441\u044f \u0422\u0415\u041b 8 \u0438 2 \u0443\u0441\u0442\u0430\u043d\u043e\u0432\u043b\u0435\u043d\u043d\u044b\u0445 \u0438\u043c\u043f\u043b\u0430\u043d\u0442\u0430 \u201c%s\u201d \u043b\u0438\u0431\u043e 2 \u201c\u041b\u0438\u0447\u043d\u044b\u0445 \u041f\u043e\u0440\u0442\u0430\u201d."' % MUS),
    pf(MD),
    om_lit2,
    u('"\u0422\u0440\u0435\u0431\u0443\u0435\u0442\u0441\u044f \u0443\u0441\u0442\u0430\u043d\u043e\u0432\u043b\u0435\u043d\u043d\u044b\u0439 \u0418\u043c\u043f\u043b\u0430\u043d\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u044b\u0439 \u042d\u043d\u0434\u043e\u0441\u043a\u0435\u043b\u0435\u0442."'),
    pf(DR),
    cat_pkt_lit,
    u('"\u0422\u0440\u0435\u0431\u0443\u0435\u0442\u0441\u044f \u0422\u0415\u041b 16 \u0438\u043b\u0438 \u0443\u0441\u0442\u0430\u043d\u043e\u0432\u043b\u0435\u043d\u043d\u044b\u0439 \u043a\u043e\u0440\u043f\u0443\u0441 \u041f\u041a\u0422."'),
    cat_pkt_lit,
    bs_lit,
    u('"\u0422\u0440\u0435\u0431\u0443\u0435\u0442\u0441\u044f \u0443\u0441\u0442\u0430\u043d\u043e\u0432\u043b\u0435\u043d\u043d\u0430\u044f \u0411\u0418\u041e\u0421\u0418\u0421\u0422\u0415\u041c\u0410 (\u041f\u043e\u043b\u043d\u0430\u044f \u041a\u043e\u043d\u0432\u0435\u0440\u0441\u0438\u044f \u0422\u0435\u043b\u0430)."'),
    cat_pkt_lit,
    u('"\u041e\u0434\u043d\u043e\u0432\u0440\u0435\u043c\u0435\u043d\u043d\u043e \u043c\u043e\u0436\u043d\u043e \u0443\u0441\u0442\u0430\u043d\u043e\u0432\u0438\u0442\u044c \u0442\u043e\u043b\u044c\u043a\u043e \u043e\u0434\u0438\u043d \u043a\u043e\u0440\u043f\u0443\u0441 \u041f\u041a\u0422."'),
    u('"%s"' % KP),
    bs_lit,
    u('"\u0422\u0440\u0435\u0431\u0443\u0435\u0442\u0441\u044f \u0443\u0441\u0442\u0430\u043d\u043e\u0432\u043b\u0435\u043d\u043d\u0430\u044f \u0411\u0418\u041e\u0421\u0418\u0421\u0422\u0415\u041c\u0410 (\u041f\u043e\u043b\u043d\u0430\u044f \u041a\u043e\u043d\u0432\u0435\u0440\u0441\u0438\u044f \u0422\u0435\u043b\u0430)."'),
)
tail_old = u('\u041a\u0438\u0431\u0435\u0440\u0430\u0443\u0434\u0438\u043e."') + '\nreturn""},\nb9l(a,b){var s=J.d3'
tail_new = (u('\u041a\u0438\u0431\u0435\u0440\u0430\u0443\u0434\u0438\u043e."') + '\n' + M1 + '\n'
            + block + '\n' + M2 + '\nreturn""},\nb9l(a,b){var s=J.d3')
js = apply1(js, 'aVD: блок требований (CPSREQ)', tail_old, tail_new)

# ---------- 3. aVE: мышцы 2 -> 3 ----------
mus_old = 'if(s===%s)return 2' % mus_lit
mus_new = 'if(s===%s)return 3' % mus_lit
js = apply1(js, 'aVE: мышцы 2->3', mus_old, mus_new)

# ---------- 4. aaH/B.CQ: ускорители ----------
cq_old = u('B.aaH={"\u041a\u0435\u0440\u0435\u0437\u043d\u0438\u043a\u043e\u0432":0,"\u0421\u0430\u043d\u0434\u0432\u0438\u0441\u0442\u0430\u043d":1}\nB.CQ=new A.cP(B.aaH,2,t.T)')
cq_new = u('B.aaH={"\u041a\u0435\u0440\u0435\u0437\u043d\u0438\u043a\u043e\u0432":0,"\u0421\u0430\u043d\u0434\u0432\u0438\u0441\u0442\u0430\u043d":1,"%s":2,"%s":3}\nB.CQ=new A.cP(B.aaH,4,t.T)' % (CC, CD))
js = apply1(js, 'aaH/CQ: +Керензиков, +Экспериментальный Сандевистан Девида', cq_old, cq_new)

# ---------- 5. зона "Голова" ----------
n0_old = 'B.N0=s([B.a5W,B.a5V,B.a5R],t.o)'
n0_new = 'B.N0=s([B.a5W,B.a5V,B.a5R,new A.h(B.e0,["head",%s],t.w)],t.o)' % u('"\u0413\u043e\u043b\u043e\u0432\u0430"')
js = apply1(js, 'N0: зона Голова', n0_old, n0_new)

tpl_old = '"legs",A.B(["items",A.a([],l)],a1,e),"fashion",A.B(["items",A.a([],l)],a1,e)],a1,t.Sx)'
tpl_new = '"legs",A.B(["items",A.a([],l)],a1,e),"head",A.B(["items",A.a([],l)],a1,e),"fashion",A.B(["items",A.a([],l)],a1,e)],a1,t.Sx)'
js = apply1(js, 'шаблон персонажа: зона head', tpl_old, tpl_new)

# ---------- запись + самопроверка ----------
io.open(MAIN, 'w', encoding='utf-8', newline='').write(js)

checks = [
    ('\u03a9 в \u03a3-ветке', ('A.jW(m,o)>0||A.jW(m,%s)>0' % om_lit) in js),
    ('\u03a9 в \u03b2-ветке', ('A.jW(m,p)>0||A.jW(m,%s)>0' % om_lit) in js),
    ('блок CPSREQ один', js.count(M1) == 1 and js.count(M2) == 1),
    ('aVE: мышцы = 3', ('if(s===%s)return 3' % mus_lit) in js and ('if(s===%s)return 2' % mus_lit) not in js),
    ('CQ: 4 записи, счётчик 4', u('"%s":3}' % CD) in js and 'B.CQ=new A.cP(B.aaH,4,t.T)' in js),
    ('N0: голова', '["head",%s],t.w)],t.o)' % u('"\u0413\u043e\u043b\u043e\u0432\u0430"') in js),
    ('шаблон: head до fashion', '"head",A.B(["items",A.a([],l)],a1,e),"fashion"' in js),
]
for t, ok in checks:
    log(('OK  ' if ok else 'FAIL') + ' ' + t)
if not all(ok for t, ok in checks):
    raise SystemExit('!! Проверка не прошла — см. tools/_patch_req_report.txt')
log('размер: %d -> %d' % (orig_len, len(js)))

with io.open(os.path.join(ROOT, 'tools', '_patch_req_report.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(report) + '\n')
print('done')
