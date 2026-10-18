# -*- coding: utf-8 -*-
r"""Поиск названий фракций/банд по всему дереву data-pool. Отчёт: $TEMP/dp_factions.txt
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DP = os.path.join(ROOT, 'data-pool')
OUT = os.path.join(os.environ.get('TEMP', '.'), 'dp_factions.txt')

TERMS = [
    'Валентино', 'Мальстрём', 'Тигриные', 'Мокс', 'Альдекальдо', 'Джоуд', 'Вудуист',
    'Бозо', 'Инквизитор', 'Животные', 'Стальные вакеро', 'банды', 'Банды', 'банда',
    'фракци', 'Фракци', 'ганг', 'Ганг', 'Пираньи', 'Расплатчики', 'Мозговики',
    'Змеиная', 'Раффен Шив', 'Восстановители', 'Последняя надежда', 'Кровавые бритвы',
    'Железные прицелы', 'Филармонические', 'Легион', '6-я улица', 'Нейт', 'бойцы',
    'городская банда', 'Городская банда', 'уличная банда', 'Уличная банда',
]


def main():
    lines = []
    for term in TERMS:
        pat = re.compile(re.escape(term), re.IGNORECASE)
        hits = []
        for dp, dn, fn in os.walk(DP):
            if 'images' in dp or 'vendor' in dp or 'pagefind' in dp:
                continue
            for f in fn:
                if not f.endswith(('.html', '.json')):
                    continue
                p = os.path.join(dp, f)
                try:
                    t = open(p, encoding='utf-8', errors='replace').read()
                except Exception:
                    continue
                n = len(pat.findall(t))
                if n:
                    hits.append((os.path.relpath(p, DP), n))
        hits.sort(key=lambda x: -x[1])
        lines.append('== %s : %d файлов' % (term, len(hits)))
        for h, n in hits[:8]:
            lines.append('   %-58s %d' % (h, n))
        lines.append('')
    open(OUT, 'w', encoding='utf-8').write('\n'.join(lines))
    print('report ->', OUT)


if __name__ == '__main__':
    main()
