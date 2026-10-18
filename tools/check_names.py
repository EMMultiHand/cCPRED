# -*- coding: utf-8 -*-
"""Проверка присутствия конкретных имён в dp_additions.json + последние записи."""
import io
import json
import os

d = json.load(io.open(r'D:\Desktop\cCPRED\tools\dp_additions.json', encoding='utf-8'))
names = [w[0] for w in d['weapons']]
tgt = ['Цепной Потрошитель', 'Киберматрикс Гэнг Джаззлер', 'Радлайн Киберрука-Дугомет',
       'Визард Технолоджис Киберноги Романовой', 'Dai Lung Streetmaster',
       'Микромилашка от Hello Cutie', 'Обрез ПМВ Винтовки в Пистолет', 'Crusher 207X']
out = []
for t in tgt:
    out.append(('ДА  ' if t in names else 'НЕТ ') + t)
out.append('всего в доб.: %d' % len(names))
out.append('первые 5: ' + '; '.join(names[:5]))
out.append('последние 5: ' + '; '.join(names[-5:]))
io.open(os.path.join(os.environ['TEMP'], 'check_names.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
