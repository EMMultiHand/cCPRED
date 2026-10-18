# -*- coding: utf-8 -*-
r"""
Вставка дополнений ДатаПула в каталог приложения (app/main.dart.js).

Читает tools/dp_additions.json (результат build_dp_additions.py) и дописывает
записи в концевые литералы мастер-массивов каталога:

  оружие    -> перед закрытием  B.NT],t.X6)   (массив B.Pl)
  броня     -> перед закрытием  B.V0],t.X6)   (массив B.S7)
  снаряжение-> перед закрытием  B.Ww],A.aN(   (массив B.Ox)
  корпорации-> перед закрытием  B.Nm],t.X6)   (массив B.O5)
  импланты  -> перед закрытием  B.VL],t.X6)   (массив B.Q2)
  боеприпасы-> дополнение списков B.jT/B.VC/B.Za/B.Sx/B.VZ перед ],t.s)

Идемпотентность: точный вставленный чанк запоминается в tools/catalog_ledger.json;
при повторном запуске он сначала удаляется точным совпадением, затем вставляется
заново (обновление). Новые строки — только ASCII (\uXXXX), строки записей — в
формате JS-литералов: s([...],t.b) для записей, s([...],t.s) для снаряжения.
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, 'app')
JS_PATH = os.path.join(APP, 'main.dart.js')
LEDGER_PATH = os.path.join(ROOT, 'tools', 'catalog_ledger.json')
ADD_PATH = os.path.join(ROOT, 'tools', 'dp_additions.json')


def js_str(s):
    return json.dumps(str(s), ensure_ascii=True)


def js_val(v):
    if isinstance(v, str) and v.startswith('@@RAW:') and v.endswith('@@'):
        return v[6:-2]
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        return js_str(v)
    raise TypeError('unsupported value type: %r' % (v,))


def rec_literal(fields, conv):
    return 's([%s],%s)' % (','.join(js_val(f) for f in fields), conv)


def build_chunks(adds):
    chunks = {}
    chunks['weapons'] = ',' + ','.join(rec_literal(f, 't.b') for f in adds['weapons'])
    chunks['armor'] = ',' + ','.join(rec_literal(f, 't.b') for f in adds['armor'])
    chunks['implants'] = ',' + ','.join(rec_literal(f, 't.b') for f in adds['implants'])
    chunks['equipment'] = ',' + ','.join(rec_literal(f, 't.s') for f in adds['equipment'])
    chunks['corps'] = ',' + ','.join(rec_literal(f, 't.b') for f in adds['corps'])
    return chunks


ARRAY_ANCHORS = {
    'weapons': ('B.NT', '],t.X6)'),
    'armor': ('B.V0', '],t.X6)'),
    'equipment': ('B.Ww', '],A.aN('),
    'corps': ('B.Nm', '],t.X6)'),
    'implants': ('B.VL', '],t.X6)'),
}


def load_ledger():
    if os.path.exists(LEDGER_PATH):
        with io.open(LEDGER_PATH, encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_ledger(led):
    with io.open(LEDGER_PATH, 'w', encoding='utf-8') as f:
        json.dump(led, f, ensure_ascii=True, indent=1, sort_keys=True)


def remove_old(js, key, ledger):
    """Удалить ранее вставленный чанк (если был). Возвращает (js, found)."""
    chunk = ledger.get(key)
    if not chunk:
        return js, False
    if key.startswith('ammo:'):
        name = key[5:]
        start = js.find(name + '=s([')
        if start < 0:
            raise SystemExit('ammo %s: definition not found' % name)
        end = js.find('],t.s)', start)
        if end < 0:
            raise SystemExit('ammo %s: closing ],t.s) not found' % name)
        if end >= len(chunk) and js[end - len(chunk):end] == chunk:
            js = js[:end - len(chunk)] + js[end:]
            return js, True
        return js, False
    pre, post = ARRAY_ANCHORS[key]
    full = pre + chunk + post
    n = js.count(full)
    if n == 1:
        js = js.replace(full, pre + post, 1)
        return js, True
    if n == 0:
        return js, False
    raise SystemExit('%s: chunk found %d times' % (key, n))


def insert_new(js, key, chunk):
    if key.startswith('ammo:'):
        name = key[5:]
        start = js.find(name + '=s([')
        if start < 0:
            raise SystemExit('ammo %s: definition not found' % name)
        end = js.find('],t.s)', start)
        if end < 0:
            raise SystemExit('ammo %s: closing ],t.s) not found' % name)
        return js[:end] + chunk + js[end:]
    pre, post = ARRAY_ANCHORS[key]
    anchor = pre + post
    n = js.count(anchor)
    if n != 1:
        raise SystemExit('%s: anchor %r found %d times (expected 1)' % (key, anchor, n))
    return js.replace(anchor, pre + chunk + post, 1)


def ammo_current_items(js, name):
    start = js.find(name + '=s([')
    end = js.find('],t.s)', start)
    if start < 0 or end < 0:
        raise SystemExit('ammo %s: definition not found' % name)
    inner = js[start + len(name + '=s(['):end]
    try:
        return json.loads('[' + inner + ']')
    except ValueError:
        return None


def main():
    with io.open(ADD_PATH, encoding='utf-8') as f:
        adds = json.load(f)

    js = io.open(JS_PATH, encoding='utf-8').read()
    size0 = len(js)
    ledger = load_ledger()

    report = []
    chunks = build_chunks(adds)
    report.append('чанки: ' + ', '.join('%s=%d' % (k, len(v)) for k, v in chunks.items()))

    # 1) удаление старых вставок
    for key in list(ARRAY_ANCHORS) + sorted(k for k in ledger if k.startswith('ammo:')):
        js, found = remove_old(js, key, ledger)
        report.append('удаление %-10s: %s' % (key, 'найден и удалён' if found else 'нет (чисто)'))

    # 2) пополнение боеприпасов (с дедупликацией)
    new_ledger = {}
    for key in sorted(adds.get('ammo', {})):
        name = key[5:] if key.startswith('ammo:') else key
        items = adds['ammo'][key]
        cur = ammo_current_items(js, name)
        if cur is None:
            report.append('боеприпасы %s: НЕ УДАЛОСЬ разобрать список, пропущено' % key)
            continue
        fresh = [i for i in items if i not in cur]
        dup = [i for i in items if i in cur]
        if dup:
            report.append('боеприпасы %s: уже есть %s' % (key, ', '.join(dup)))
        if not fresh:
            continue
        lkey = 'ammo:%s' % name
        chunk = ',' + ','.join(js_str(i) for i in fresh)
        js = insert_new(js, lkey, chunk)
        new_ledger[lkey] = chunk
        report.append('боеприпасы %s: +%d вариантов' % (key, len(fresh)))

    # 3) вставка записей
    for key, chunk in chunks.items():
        if not chunk or chunk == ',':
            continue
        js = insert_new(js, key, chunk)
        new_ledger[key] = chunk
        report.append('вставка %-10s: %d симв.' % (key, len(chunk)))

    save_ledger(new_ledger)

    with io.open(JS_PATH, 'w', encoding='utf-8', newline='') as f:
        f.write(js)

    report.append('размер main.dart.js: %d -> %d (+%d)' % (size0, len(js), len(js) - size0))
    out = os.path.join(os.environ.get('TEMP', '.'), 'patch_catalog_report.txt')
    with io.open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    print('ok: main.dart.js %d -> %d' % (size0, len(js)))
    print('-> %s' % out)


if __name__ == '__main__':
    main()
