# -*- coding: utf-8 -*-
"""Пробник сырых строк ДатаПула: источники оружия, агенты, софт, расходники."""
import json
import os

TMP = os.environ.get('TEMP', '.')


def load(name):
    with open(os.path.join(TMP, 'dp_tables_%s.json' % name), encoding='utf-8') as f:
        return json.load(f)


W = load('equipment_weapons')
I = load('chrome_implants')
AG = load('equipment_agents_accessories')
SO = load('equipment_soft')
IT = load('equipment_items')

out = []


def dump(label, sec, names, n=4):
    out.append('##### %s' % label)
    for row in sec.get('rows', []):
        if row[0] in names:
            out.append(json.dumps(row, ensure_ascii=False))
            out.append('')


dump('weapons[9]', W[9], {'Микромилашка от Hello Cutie', 'Обрез ПМВ Винтовки в Пистолет', 'Big Dreem'})
dump('weapons[10]', W[10], {'Воздушка Кочевников', 'Everest VentureWare SurvivalMaster', 'Sanroo Hello Cutie 1TruLuv'})
dump('weapons[11]', W[11], {'Разлагающаяся ПУ Биотехника', 'Милитех Эгида'})
dump('weapons[14]', W[14], {'Термальный Клинок Centurion essentials'})
dump('implants[1]', I[1], {'Чип переводчик', 'Управление Дронами', 'Керензиков'})
dump('implants[2]', I[2], {'Хранилище щепок', 'Hello Cutie sparkle-ize'})

out.append('##### agents: все строки')
for sec in AG:
    out.append('--- section %s keys=%s' % (sec.get('title'), list(sec.keys())))
    for row in sec.get('rows', [])[:6]:
        out.append(json.dumps(row, ensure_ascii=False))
    out.append('')

out.append('##### soft: section keys')
for sec in SO:
    out.append('--- section %s' % sec.get('title'))
    for row in sec.get('rows', [])[:2]:
        out.append(json.dumps(row, ensure_ascii=False))
    out.append('')

out.append('##### items: section keys')
for sec in IT:
    out.append('--- section %s' % sec.get('title'))
    for row in sec.get('rows', [])[:2]:
        out.append(json.dumps(row, ensure_ascii=False))
    out.append('')

with open(os.path.join(TMP, 'probe_rows.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('ok')
