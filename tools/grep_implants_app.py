# -*- coding: utf-8 -*-
"""Проверка имён имплантов приложения (поиск ложных пропусков)."""
import os

TMP = os.environ.get('TEMP', '.')
lines = open(os.path.join(TMP, 'compact_B.Q2.txt'), encoding='utf-8').read().splitlines()

pats = ['Керензиков', 'Сандевистан', 'Техноволос', 'Ноготоч', 'Комплекс Кибераудио', 'Комплект Кибераудио',
        'Трекер', 'мышц', 'Связывател', 'Радар', 'осох', 'Псайбер', 'Валдо', 'роектор', 'Шредер', 'Газомет',
        'ono-Paw', 'Моно-Лап', 'Стопа', 'Стоп', 'Цепк', 'Скейт', 'Эндоскелет', 'Внутренний Агент', 'Химическ',
        'Мускул', 'Тканекожа', 'Арм-Стрела', 'МикроВидео', 'Агент']

out = []
for p in pats:
    ms = [l[:160] for l in lines if p in l]
    out.append('### %s' % p)
    out.extend(ms)
    out.append('')

open(os.path.join(TMP, 'implant_grep.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
