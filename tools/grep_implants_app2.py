# -*- coding: utf-8 -*-
"""Второй проход поиска имён в дампе имплантов приложения."""
import os

TMP = os.environ.get('TEMP', '.')
lines = open(os.path.join(TMP, 'compact_B.Q2.txt'), encoding='utf-8').read().splitlines()

pats = ['токсин', 'Токсин', 'нога', 'Нога', 'ноги', 'кейт', 'Моно', 'Лапа', 'Стандарт', 'стандарт',
        'Экранирован', 'Укреплен', 'Изменчив', 'Кисть', 'рука', 'ступн', 'Пятк', 'подошв']

out = []
for p in pats:
    ms = [l[:140] for l in lines if p in l]
    out.append('### %s (%d)' % (p, len(ms)))
    out.extend(ms)
    out.append('')

open(os.path.join(TMP, 'implant_grep2.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
