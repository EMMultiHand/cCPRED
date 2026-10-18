# -*- coding: utf-8 -*-
"""Проверка записей dp_additions.json после правок."""
import io
import json
import os

P = r'D:\Desktop\cCPRED\tools\dp_additions.json'
d = json.load(io.open(P, encoding='utf-8'))

out = []
out.append('weapons=%d armor=%d implants=%d equipment=%d corps=%d' % (
    len(d['weapons']), len(d['armor']), len(d['implants']), len(d['equipment']), len(d['corps'])))

out.append('=== weapons (выборочно) ===')
show_w = ['Микромилашка от Hello Cutie', 'Обрез ПМВ Винтовки в Пистолет', 'Милитех Эгида',
          'Термальный Клинок Centurion essentials', 'Пулемёт MetaCorp «Victoria»']
for w in d['weapons']:
    if w[0] in show_w:
        out.append(json.dumps(w, ensure_ascii=False))

out.append('=== armor (все) ===')
for a in d['armor']:
    out.append(json.dumps(a, ensure_ascii=False))

out.append('=== implants: pkt/экзотика/ПКТ (выборочно) ===')
for i in d['implants']:
    if i[0] in ('ПОКРЫТИЕ "СЕРА"', 'ПОКРЫТИЕ "ХАМЕЛЕОН"', 'КИБЕРМАТРИКС INC. "КОПЕРНИК"',
                'ДЕМОН™', 'Керензиков', 'Hello Cutie sparkle-ize', 'БИОСИСТЕМА',
                'Имплантированный Эндоскелет Ω (ОМЕГА)', 'Cкелет ЛФ-001 SWAT', 'Киберчереп'):
        out.append(json.dumps(i, ensure_ascii=False))

out.append('=== equipment (выборочно) ===')
show_e = ['Радар-детектор', 'Внешний экзоскелет Ω (ОМЕГА)', 'Мультигиппо', 'Wyzard Technologies Merlyn',
          'КиллСтром Колонка "Тифоид"', 'Segotari RUSH Revolution', 'Умные очки', 'Тяжёлый Metalgear®',
          'СкидРоу Тренч', 'МехаМэн Умная Перчатка', 'Фирменный комбинезон / Униформа']
for e in d['equipment']:
    if e[0] in show_e:
        out.append(json.dumps(e, ensure_ascii=False))

io.open(os.path.join(os.environ['TEMP'], 'check_additions2.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('ok, lines=%d' % len(out))
