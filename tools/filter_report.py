# -*- coding: utf-8 -*-
"""Фильтр отчёта сборки по ключевым строкам."""
import io
import os

TMP = os.environ['TEMP']
lines = io.open(os.path.join(TMP, 'additions_report.txt'), encoding='utf-8').read().splitlines()

keys = ['Взломщик', 'Свисток', 'Merlyn', 'Grade', 'Double Agent', 'АэроСфера', 'Супер Роскошь',
        'Segotari RUSH Revolution', 'Барабанный', 'Флакон биотоксина', 'ОМЕГА)', 'Дорожный',
        'Мультигиппо', 'Заряд крионасоса', 'Картриджи', 'Радар-детектор', 'Духи', 'Боевая перчатка',
        'Зонт', 'КиллСтром', 'Мастер Напитков 3000', 'Универсальный']

out = [l for l in lines if any(k in l for k in keys)]
io.open(os.path.join(TMP, 'report_filter.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('lines:', len(out))
