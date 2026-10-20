# -*- coding: utf-8 -*-
"""Патч: создание своих имплантов в любой зоне («как с оружием и бронёй»).

Что делает патч (идемпотентно, маркеры /*CPSIMP1*/ и /*CPSIMP2*/):
  1) В ленивую инициализацию каталога имплантов ($.aKX) добавляет записи,
     сохранённые в localStorage("cpref_custom_implants") — чтобы свои импланты
     переживали перезагрузку и резолвились через A.mG(name).
  2) В диалог зоны (A.bb4) добавляет кнопку «СОЗДАТЬ ИМПЛАНТ», открывающую
     форму (название, категория, ячейки, цена, ПЧ, установка, эффект, описание).
     По сохранению запись попадает в каталог, в localStorage и сразу
     устанавливается в текущую зону (через тот же колбэк z3, что и каталог).

Запуск:  python tools/patch_custom_implants.py
"""
import io
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, 'app', 'main.dart.js')
BAK = os.path.join(ROOT, 'tools', '_main.dart.js.before_custom_implants')

ANCHOR_ACTIONS = 'A.a([A.Y(A.eX(B.DP,new A.aIb(o,f,a),null),1)],t.p)'
ANCHOR_AKX = ',"skillChipBonus",3],t.N,t.z))\nreturn q})'


def esc(s):
    """Экранируем не-ASCII в \\uXXXX (файл сборки чисто ASCII)."""
    return ''.join(ch if ord(ch) < 0x80 else '\\u%04x' % ord(ch) for ch in s)


def ru(s):
    return esc(s)


# ---------------------------------------------------------------- patch 1: aKX
AKX_INJECT = (
    ',"skillChipBonus",3],t.N,t.z))\n'
    '/*CPSIMP1*/try{var IMP=window.localStorage.getItem("cpref_custom_implants");'
    'if(IMP){var IMPA=JSON.parse(IMP);'
    'if(IMPA&&IMPA.length)for(var IMPI=0;IMPI<IMPA.length;IMPI++){'
    'var IMPM=IMPA[IMPI];'
    'if(IMPM&&IMPM.name)q.push(A.B(["name",A.r(IMPM.name),'
    '"slots",A.a(IMPM.slots||[],t.s),'
    '"category",A.r(IMPM.category||""),'
    '"source",A.r(IMPM.source||"' + ru('Свой имплант') + '"),'
    '"price",A.r(IMPM.price||""),'
    '"humanityLoss",A.r(IMPM.humanityLoss||""),'
    '"install",A.r(IMPM.install||""),'
    '"effects",A.r(IMPM.effects||""),'
    '"details",A.r(IMPM.details||"")],t.N,t.z))}}}catch(IMPE){}/*CPSIMP2*/\n'
    'return q})'
)

# ---------------------------------------------------------------- patch 2: bb4
CREATE_BTN = r'''B.bO,A.Y(A.fK(A.p("__LBL__",null,null,null,null,null,null,null,null,null),function(){
var ZC=a,ZZ=h,ZO=o,ZF=f;
var mkC=function(v){return new A.bv(new A.aV(v,B.a4,B.X),$.aE())};
var fN=mkC(""),fC=mkC("__CAT__"),fP=mkC(""),fH=mkC(""),fI=mkC(""),fS=mkC("1"),fE=mkC(""),fD=mkC("");
var fErr=new A.ci("",$.aE());
var FB=new A.aH2();
var body=function(cx,cs){return new A.e3(B.lw,A.DE(A.L(A.a([
FB.$2("__NAME_LBL__",fN),B.a2,
A.aa(A.a([A.Y(FB.$2("__CAT_LBL__",fC),1),B.a1,A.Y(FB.$3$keyboardType("__CELLS_LBL__",fS,B.c3),1)],t.p),B.q,B.e,B.f,0),B.a2,
A.aa(A.a([A.Y(FB.$2("__PRICE_LBL__",fP),1),B.a1,A.Y(FB.$2("__HUM_LBL__",fH),1)],t.p),B.q,B.e,B.f,0),B.a2,
FB.$2("__INSTALL_LBL__",fI),B.a2,
FB.$3$maxLines("__EFFECT_LBL__",fE,4),B.a2,
FB.$3$maxLines("__DETAILS_LBL__",fD,3),B.J,
new A.i9(fErr,new A.aGX(),null,null,t.x_)],t.p),B.ay,null,B.e,B.f),null),null)};
var doSave=function(){
var nm=B.c.G(fN.a.a);
if(nm.length===0){fErr.st("__ERR_NAME__");return}
var key=A.jV(nm),LK="cpref_custom_implants",arr=[],ii;
try{arr=JSON.parse(window.localStorage.getItem(LK)||"[]")||[]}catch(e){arr=[]}
var ex=-1;
for(ii=0;ii<arr.length;ii++){if(arr[ii]&&arr[ii].name===key){ex=ii;break}}
if(ex<0&&$.aZ8().h(0,key)!=null){fErr.st("__ERR_DUP__");return}
var sl=A.dK(B.c.G(fS.a.a),null);if(sl==null)sl=1;sl=A.aM(sl,0,99);
var ef=B.c.G(fE.a.a),dt=B.c.G(fD.a.a),ct=B.c.G(fC.a.a);
if(sl<=0){if(!B.c.n(ef.toLowerCase(),"__NO_SLOT__"))ef=(ef.length!==0?ef+" ":"")+"__NO_SLOT_TXT__"}
else{ef=(ef.length!==0?ef+" ":"")+"__SLOT_TXT1__"+sl+"__SLOT_TXT2__"}
var pr=B.c.G(fP.a.a),hu=B.c.G(fH.a.a),ins=B.c.G(fI.a.a);
var sla=[ZZ];
if(ex>=0){var osl=arr[ex].slots||[];for(var si=0;si<osl.length;si++){if(sla.indexOf(osl[si])<0)sla.push(osl[si])}}
var rec=A.B(["name",key,"slots",A.a(sla,t.s),"category",ct,"source","__SRC__","price",pr,"humanityLoss",hu,"install",ins,"effects",ef,"details",dt],t.N,t.z);
var obj={"name":key,"slots":sla,"category":ct,"source":"__SRC__","price":pr,"humanityLoss":hu,"install":ins,"effects":ef,"details":dt};
if(ex>=0){arr[ex]=obj;var al=$.aKX();for(ii=0;ii<al.length;ii++){if(J.f(al[ii].h(0,"name"))===key){al[ii]=rec;break}}}
else{arr.push(obj);$.aKX().push(rec)}
$.aZ8().j(0,key,rec);
try{window.localStorage.setItem(LK,JSON.stringify(arr))}catch(e){}
if(ZO.indexOf(key)<0)ZO.push(key);ZF.$1(ZO);
A.bL(ZC,false).bD(null);
setTimeout(function(){try{A.bL(ZC,false).bD(null)}catch(e){}},260);
};
A.cc(ZC,A.a([A.Y(A.eX(B.cV,function(){A.bL(ZC,false).bD(null)},null),1),B.bO,A.Y(A.fK(A.p("__SAVE_LBL__",null,null,null,null,null,null,null,null,null),doSave,null),1)],t.p),new A.dP(body,null),null,null,B.am,640,null,true,null,"__TITLE__",t.H);
},null),1)],t.p)'''

# подстановки русских текстов (экранируются целиком)
SUBS = {
    '__LBL__': 'СОЗДАТЬ ИМПЛАНТ',
    '__CAT__': 'Модуль',
    '__NAME_LBL__': 'Название',
    '__CAT_LBL__': 'Категория',
    '__CELLS_LBL__': 'Ячейки',
    '__PRICE_LBL__': 'Цена',
    '__HUM_LBL__': 'ПЧ',
    '__INSTALL_LBL__': 'Установка',
    '__EFFECT_LBL__': 'Эффект',
    '__DETAILS_LBL__': 'Описание',
    '__ERR_NAME__': 'Введи название импланта.',
    '__ERR_DUP__': 'Имплант с таким названием уже есть.',
    '__NO_SLOT__': 'не занимает слот',
    '__NO_SLOT_TXT__': 'Не занимает слот.',
    '__SLOT_TXT1__': 'Занимает ',
    '__SLOT_TXT2__': ' слота.',
    '__SRC__': 'Свой имплант',
    '__SAVE_LBL__': 'СОЗДАТЬ',
    '__TITLE__': 'Создать имплант',
}


def build_create_btn():
    s = CREATE_BTN
    # сначала длинные маркеры, чтобы __NO_SLOT__ не съел __NO_SLOT_TXT__
    for k in sorted(SUBS, key=len, reverse=True):
        s = s.replace(k, ru(SUBS[k]))
    return s


def main():
    js = io.open(APP, encoding='utf-8').read()

    if '/*CPSIMP1*/' in js or '/*CPSIMP2*/' in js:
        print('SKIP: patch already applied')
        return 0

    n1 = js.count(ANCHOR_ACTIONS)
    n2 = js.count(ANCHOR_AKX)
    print('anchors:', n1, n2)
    if n1 != 1 or n2 != 1:
        print('ERROR: anchors not unique')
        return 1

    io.open(BAK, 'w', encoding='utf-8', newline='').write(js)

    js = js.replace(ANCHOR_AKX, AKX_INJECT)
    js = js.replace(ANCHOR_ACTIONS, 'A.a([A.Y(A.eX(B.DP,new A.aIb(o,f,a),null),1),' + build_create_btn())

    assert js.count('/*CPSIMP1*/') == 1 and js.count('/*CPSIMP2*/') == 1
    assert js.count('__LBL__') == 0 and js.count('__SRC__') == 0

    io.open(APP, 'w', encoding='utf-8', newline='').write(js)
    print('written bytes:', len(js.encode('utf-8')))

    r = subprocess.run(['node', '--check', APP], capture_output=True, text=True)
    print('node --check rc=', r.returncode)
    if r.stdout:
        print(r.stdout)
    if r.stderr:
        print(r.stderr)
    return r.returncode


if __name__ == '__main__':
    sys.exit(main())
