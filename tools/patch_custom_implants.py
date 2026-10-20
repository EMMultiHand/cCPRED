# -*- coding: utf-8 -*-
"""Патч: создание своих имплантов в любой зоне + настройка и удаление
(«как с оружием и бронёй»).

Что делает патч (идемпотентно, маркеры /*CPSIMP1*/, /*CPSDEF1*/, /*CPSIMP3*/):
  1) В ленивую инициализацию каталога имплантов ($.aKX) добавляет записи,
     сохранённые в localStorage("cpref_custom_implants") — чтобы свои импланты
     переживали перезагрузку и резолвились через A.mG(name).
  2) В диалог зоны (A.bb4) добавляет кнопку «СОЗДАТЬ ИМПЛАНТ» и общий редактор
     (создание/редактирование): название, категория, ячейки, цена, ПЧ,
     установка, эффект, описание.
  3) На карточках своих имплантов в списке зоны рисует шестерёнку (как у
     оружия/брони) → диалог «Настройки импланта» с «Редактировать»/«Удалить».
     Удаление убирает запись из каталога, localStorage и из всех зон персонажа.

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
ANCHOR_BB4 = 'o=A.ca(c,!0,t.N)\np.a=""\nq=A.ih(a,1080,560,0.84)'
ANCHOR_AI1 = ('return A.bg(!1,b2,!0,A.P(b2,A.L(b4,B.q,b2,B.e,B.f),B.k,b2,b2,'
              'new A.ab(a4,b2,a5,b2,b2,b2,B.y),b2,b2,b2,B.aF,b2,b2,b2),b2,!0,'
              'b2,b2,b2,b2,b2,b2,b2,a3,b2,b2,b2,b2)},')


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

# ------------------------------------------------- patch 2: bb4 (defs + button)
BB4_DEFS = r'''/*CPSDEF1*/
var LK="cpref_custom_implants";
var ZONES=["neural","optics","audio","leftArm","rightArm","torso","legs","head","fashion"];
var CB=function(fn){try{fn.$0=fn;fn.$S=0}catch(e){}return fn};
var sv=function(rec,k,d){try{if(rec){var v=rec.h(0,k);if(v!=null)return J.f(v)}}catch(e){}return d};
var stripSlot=function(s){
s=s||"";
var low=s.toLowerCase(),p=low.lastIndexOf("__NO_SLOT__");
if(p>=0)return s.slice(0,p).replace(/\s+$/,"");
p=low.lastIndexOf("__SLOT_HAS__ ");
if(p>=0&&low.slice(p).indexOf("__SLOT_WORD__")>=0)return s.slice(0,p).replace(/\s+$/,"");
return s};
var cellsFrom=function(s){
s=s||"";
if(s.toLowerCase().indexOf("__NO_SLOT__")>=0)return "0";
var re=/(\d+)\s+__SLOT_WORD__/ig,m=null,r;
while((r=re.exec(s))!=null)m=r;
return m?m[1]:"1"};
var saveZones=function(cb,oldKey,newKey){
try{
var model=cb?cb.a:null;
if(!model||!model.gdf)return;
var cw=model.gdf();
for(var zi=0;zi<ZONES.length;zi++){
var zm=cw.h(0,ZONES[zi]);
if(!zm)continue;
var names=A.aET(zm),ch=false,nl=[],ni;
for(ni=0;ni<names.length;ni++){
if(names[ni]===oldKey){ch=true;if(newKey!==null)nl.push(newKey)}
else nl.push(names[ni]);
}
if(ch)model.z3(ZONES[zi],A.a(nl,t.s));
}
}catch(e){}
};
var rmName=function(list,key){
try{if(!list)return;for(var i=list.length-1;i>=0;i--){if(list[i]===key)list.splice(i,1)}}catch(e){}
};
var rmRec=function(list,key){
try{if(!list)return;for(var i=list.length-1;i>=0;i--){var r=list[i];if(r&&J.f(r.h(0,"name"))===key)list.splice(i,1)}}catch(e){}
};
var mkC=function(v){return new A.bv(new A.aV(v,B.a4,B.X),$.aE())};
window.__cprefImplantEditor=function(EC,rec,EZ,EO,EF,EB){
var oldName=sv(rec,"name","");
var oldEff=sv(rec,"effects","");
var fN=mkC(oldName);
var fC=mkC(sv(rec,"category","__CAT__")||"__CAT__");
var fP=mkC(sv(rec,"price",""));
var fH=mkC(sv(rec,"humanityLoss",""));
var fI=mkC(sv(rec,"install",""));
var fS=mkC(rec?cellsFrom(oldEff):"1");
var fE=mkC(rec?stripSlot(oldEff):"");
var fD=mkC(sv(rec,"details",""));
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
var key=A.jV(nm),arr=[],ii;
try{arr=JSON.parse(window.localStorage.getItem(LK)||"[]")||[]}catch(e){arr=[]}
var editing=!!rec;
if(editing&&key!==oldName&&$.aZ8().h(0,key)!=null){fErr.st("__ERR_DUP__");return}
var ex=-1;
if(!editing){
for(ii=0;ii<arr.length;ii++){if(arr[ii]&&arr[ii].name===key){ex=ii;break}}
if(ex<0&&$.aZ8().h(0,key)!=null){fErr.st("__ERR_DUP__");return}
}
var sl=A.dK(B.c.G(fS.a.a),null);if(sl==null)sl=1;sl=A.aM(sl,0,99);
var ef=B.c.G(fE.a.a),dt=B.c.G(fD.a.a),ct=B.c.G(fC.a.a);
if(sl<=0){if(!B.c.n(ef.toLowerCase(),"__NO_SLOT__"))ef=(ef.length!==0?ef+" ":"")+"__NO_SLOT_TXT__"}
else{ef=(ef.length!==0?ef+" ":"")+"__SLOT_TXT1__"+sl+"__SLOT_TXT2__"}
var pr=B.c.G(fP.a.a),hu=B.c.G(fH.a.a),ins=B.c.G(fI.a.a);
var sla=[];
if(editing){
var osl=rec.h(0,"slots");
if(osl!=null){for(ii=0;ii<osl.length;ii++)sla.push(osl[ii])}
}else{
sla.push(EZ);
if(ex>=0){var osl2=arr[ex].slots||[];for(ii=0;ii<osl2.length;ii++){if(sla.indexOf(osl2[ii])<0)sla.push(osl2[ii])}}
}
var rec2=A.B(["name",key,"slots",A.a(sla,t.s),"category",ct,"source","__SRC__","price",pr,"humanityLoss",hu,"install",ins,"effects",ef,"details",dt],t.N,t.z);
var obj2={"name":key,"slots":sla,"category":ct,"source":"__SRC__","price":pr,"humanityLoss":hu,"install":ins,"effects":ef,"details":dt};
if(editing){
var arr2=[],jj,found=false;
for(jj=0;jj<arr.length;jj++){if(arr[jj]&&arr[jj].name===oldName){arr2.push(obj2);found=true}else arr2.push(arr[jj])}
if(!found)arr2.push(obj2);
try{window.localStorage.setItem(LK,JSON.stringify(arr2))}catch(e){}
var al=$.aKX(),rep=false;
for(jj=0;jj<al.length;jj++){if(J.f(al[jj].h(0,"name"))===oldName){al[jj]=rec2;rep=true;break}}
if(!rep)al.push(rec2);
try{$.aZ8().H(0,oldName)}catch(e){}
try{$.aZ8().j(0,key,rec2)}catch(e){}
if(key!==oldName){
for(jj=0;jj<EO.length;jj++){if(EO[jj]===oldName)EO[jj]=key}
saveZones(EF,oldName,key);
try{EF.$1(EO)}catch(e){}
}
A.bL(EC,false).bD(null);
setTimeout(function(){try{A.bL(EC,false).bD(null)}catch(e){}},260);
return;
}
if(ex>=0){arr[ex]=obj2;var al2=$.aKX();for(ii=0;ii<al2.length;ii++){if(J.f(al2[ii].h(0,"name"))===key){al2[ii]=rec2;break}}}
else{arr.push(obj2);$.aKX().push(rec2)}
try{$.aZ8().j(0,key,rec2)}catch(e){}
try{window.localStorage.setItem(LK,JSON.stringify(arr))}catch(e){}
var why=A.aVD(EZ,EO,key,EB);
if(why.length===0&&!A.b9h(EZ,EO,key,EB))why="__CAP_MSG__";
if(why.length!==0){fErr.st("__SAVED_NOT_INST__"+why);return}
if(EO.indexOf(key)<0)EO.push(key);
EF.$1(EO);
A.bL(EC,false).bD(null);
setTimeout(function(){try{A.bL(EC,false).bD(null)}catch(e){}},260);
};
A.cc(EC,A.a([A.Y(A.eX(B.cV,function(){A.bL(EC,false).bD(null)},null),1),B.bO,A.Y(A.fK(A.p(rec?"__SAVE_EDIT__":"__SAVE_LBL__",null,null,null,null,null,null,null,null,null),doSave,null),1)],t.p),new A.dP(body,null),null,null,B.am,640,null,true,null,rec?"__TITLE_EDIT__":"__TITLE__",t.H);
};
window.__cprefImplantSettings=function(SC,rec,SZ,SO,SF,SB,SCAT){
var key=sv(rec,"name","");
var mkRow=function(icon,title,isD,cb){
var o=$.e,n=o?B.x:B.h,m=o?B.j:B.i,s,q;
if(isD){if($.k)s=B.p;else s=o?B.o:B.n}else s=o?B.Q:B.S;
if(isD)q=$.k?B.D:B.h;else if($.k)q=B.p;else q=o?B.o:B.n;
var rr=A.am(o?B.j:B.i,2);
var ic=A.P(B.I,A.b6(icon,q,null,20),B.k,null,null,new A.ab(s,null,rr,null,null,null,B.y),null,34,null,null,null,null,34);
return A.cl(B.a9,A.bx(null,m,2,true,A.aa(A.a([ic,B.a1,A.Y(A.p(title.toUpperCase(),null,null,null,null,null,A.o(null,null,o?B.j:B.i,null,null,null,null,null,null,null,null,12,null,null,B.m,null,null,true,null,0.8,null,null,null,null,null,null),null,null,null),1)],t.p),B.r,B.e,B.f,0),n,null,null,null,B.aF,1/0),B.a7,false,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,CB(cb),null,null,null,null,null,null,false,B.aq);
};
var doDelete=function(){
try{var arr=JSON.parse(window.localStorage.getItem(LK)||"[]")||[],nw=[],ii;for(ii=0;ii<arr.length;ii++){if(!arr[ii]||arr[ii].name!==key)nw.push(arr[ii])}window.localStorage.setItem(LK,JSON.stringify(nw))}catch(e){}
try{$.aZ8().H(0,key)}catch(e){}
try{var al=$.aKX();for(var i2=al.length-1;i2>=0;i2--){if(J.f(al[i2].h(0,"name"))===key)al.splice(i2,1)}}catch(e){}
rmName(SO,key);rmRec(SCAT,key);
saveZones(SF,key,null);
try{SF.$1(SO)}catch(e){}
};
A.cc(SC,null,A.L(A.a([
mkRow(B.jG,"__EDIT_LBL__",false,function(){A.bL(SC,false).bD(null);setTimeout(function(){try{window.__cprefImplantEditor(SC,rec,SZ,SO,SF,SB)}catch(e){}},260)}),
B.L,
mkRow(B.ek,"__DEL_LBL__",true,function(){A.bL(SC,false).bD(null);setTimeout(function(){try{doDelete()}catch(e){}try{A.bL(SC,false).bD(null)}catch(e){}},260)})
],t.p),B.r,null,B.e,B.ai),null,null,B.am,640,null,true,null,"__SET_TITLE__",t.H);
};
/*CPSDEF2*/'''

CREATE_BTN = r'''B.bO,A.Y(A.fK(A.p("__LBL__",null,null,null,null,null,null,null,null,null),function(){
try{window.__cprefImplantEditor(a,h,o,f,b)}catch(e0){}
},null),1)],t.p)'''

# ------------------------------------------------------ patch 3: aI1 (шестерёнка)
GEAR = r'''/*CPSIMP3*/try{var gsrc="";try{var gs0=b3.h(0,"source");if(gs0!=null)gsrc=J.f(gs0)}catch(eG0){}
if(gsrc==="__SRC__"){
var gg=$.e,ggbg,ggfg;
if(q)ggbg=gg?B.x:B.h;else ggbg=gg?B.Q:B.S;
if($.k)ggfg=B.p;else ggfg=gg?B.o:B.n;
var ggr=A.am(gg?B.j:B.i,2);
var ggTap=function(){try{window.__cprefImplantSettings(b6,b3,b1.d,b1.b,b1.f,b1.e,b1.a)}catch(eG){}};
ggTap.$0=ggTap;ggTap.$S=0;
var ggA=A.cl(B.a9,A.P(B.I,A.b6(B.jI,ggfg,b2,19),B.k,b2,b2,new A.ab(ggbg,b2,ggr,b2,b2,b2,B.y),b2,34,b2,b2,b2,b2,34),B.a7,false,b2,b2,b2,b2,b2,b2,b2,b2,b2,b2,b2,b2,b2,b2,b2,b2,b2,ggTap,b2,b2,b2,b2,b2,b2,false,B.aq);
b4.push(B.L);
b4.push(new A.dG(B.p4,b2,b2,A.md(ggA,"__GEAR_TIP__"),b2));
}}catch(eGear){}/*CPSIMP4*/'''

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
    '__CAP_MSG__': 'Недостаточно свободных ячеек. Сначала установи базовую систему или освободи слот.',
    '__SAVED_NOT_INST__': 'Имплант сохранён в каталог, но не установлен: ',
    '__NO_SLOT__': 'не занимает слот',
    '__NO_SLOT_TXT__': 'Не занимает слот.',
    '__SLOT_HAS__': 'занимает',
    '__SLOT_WORD__': 'слот',
    '__SLOT_TXT1__': 'Занимает ',
    '__SLOT_TXT2__': ' слота.',
    '__SRC__': 'Свой имплант',
    '__SAVE_LBL__': 'СОЗДАТЬ',
    '__SAVE_EDIT__': 'СОХРАНИТЬ',
    '__TITLE__': 'Создать имплант',
    '__TITLE_EDIT__': 'Настройка импланта',
    '__EDIT_LBL__': 'Редактировать',
    '__DEL_LBL__': 'Удалить',
    '__SET_TITLE__': 'Настройки импланта',
    '__GEAR_TIP__': 'Настройки импланта',
}


def build(s):
    # сначала длинные маркеры, чтобы __NO_SLOT__ не съел __NO_SLOT_TXT__
    for k in sorted(SUBS, key=len, reverse=True):
        s = s.replace(k, ru(SUBS[k]))
    return s


def main():
    js = io.open(APP, encoding='utf-8').read()

    if '/*CPSIMP1*/' in js or '/*CPSIMP2*/' in js or '/*CPSDEF1*/' in js or '/*CPSIMP3*/' in js:
        print('SKIP: patch already applied')
        return 0

    n1 = js.count(ANCHOR_ACTIONS)
    n2 = js.count(ANCHOR_AKX)
    n3 = js.count(ANCHOR_BB4)
    n4 = js.count(ANCHOR_AI1)
    print('anchors:', n1, n2, n3, n4)
    if n1 != 1 or n2 != 1 or n3 != 1 or n4 != 1:
        print('ERROR: anchors not unique')
        return 1

    io.open(BAK, 'w', encoding='utf-8', newline='').write(js)

    js = js.replace(ANCHOR_AKX, AKX_INJECT)
    js = js.replace(ANCHOR_ACTIONS,
                    'A.a([A.Y(A.eX(B.DP,new A.aIb(o,f,a),null),1),' + build(CREATE_BTN))
    js = js.replace(ANCHOR_BB4,
                    'o=A.ca(c,!0,t.N)\np.a=""\n' + build(BB4_DEFS) + '\nq=A.ih(a,1080,560,0.84)')
    js = js.replace(ANCHOR_AI1, build(GEAR) + ANCHOR_AI1)

    assert js.count('/*CPSIMP1*/') == 1 and js.count('/*CPSIMP2*/') == 1
    assert js.count('/*CPSDEF1*/') == 1 and js.count('/*CPSDEF2*/') == 1
    assert js.count('/*CPSIMP3*/') == 1 and js.count('/*CPSIMP4*/') == 1
    assert '__LBL__' not in js and '__SRC__' not in js and '__GEAR_TIP__' not in js

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
