# -*- coding: utf-8 -*-
"""Точечные правки build_dp_additions.py (уникальные/повторяющиеся строки)."""
import io
import sys

P = r'D:\Desktop\cCPRED\tools\build_dp_additions.py'
s = io.open(P, encoding='utf-8').read()

fixes = []


def rep(old, new, count=None):
    global s
    n = s.count(old)
    if n == 0:
        fixes.append('SKIP (0): %r' % old[:60])
        return
    if count is not None and n != count:
        fixes.append('WARN count=%d expected=%d: %r' % (n, count, old[:60]))
    s = s.replace(old, new)
    fixes.append('ok x%d: %r' % (n, old[:60]))


# имена записей
rep("name = re.sub(r'\\s+', ' ', str(row[0]).replace('\\n', ' ')).strip()",
    "name = fix_name(row[0])")
rep("name = re.sub(r'\\s+', ' ', str(found[0]).replace('\\n', ' ')).strip()",
    "name = fix_name(found[0])")
rep("name = nm_override or re.sub(r'\\s+', ' ', fields[0].replace('\\n', ' ')).strip()",
    "name = nm_override or fix_name(fields[0])")
rep("name = re.sub(r'\\s+', ' ', fields[0].replace('\\n', ' ')).strip()",
    "name = fix_name(fields[0])")

# ROF
rep("rof = int(re.sub(r'\\D', '', str(row[4])) or 1)", "rof = first_int(row[4])")
rep("rof = int(re.sub(r'\\D', '', str(row[3])) or 1)", "rof = first_int(row[3])")

# урон: перевод строки -> '/'
rep("dmg = re.sub(r'\\s+', ' ', str(row[2]).replace('\\n', ' ')).strip()",
    "dmg = re.sub(r'\\s+', ' ', str(row[2]).replace('\\n', '/')).strip()")

# агенты: [name, desc, price, ...]
rep("""        if sec_key == 'agents':
            # [Наименование, Описание, Цена, ...]
            desc = fields[2] if len(fields) > 2 else ''
            price = fields[3] if len(fields) > 3 else ''""",
    """        if sec_key == 'agents':
            # [Наименование, Описание, Цена, ...]
            desc = fields[1] if len(fields) > 1 else ''
            price = fields[2] if len(fields) > 2 else ''""")

# установка 'нет'
rep("""            install = re.sub(r'\\s+', ' ', str(row[1]).replace('\\n', ' ')).strip() or 'Клиника'
            desc = row[2]""",
    """            install = re.sub(r'\\s+', ' ', str(row[1]).replace('\\n', ' ')).strip() or 'Клиника'
            if norm(install) == 'нет':
                install = 'нет'
            desc = row[2]""")

# доступность: доп. варианты
rep("""        'роскошь': 'Роскошь', 'супер роскошь': 'Супер роскошь',
        'недешево': 'Дорогое', 'недёшево': 'Дорогое',
    }""",
    """        'роскошь': 'Роскошь', 'супер роскошь': 'Супер роскошь',
        'недешево': 'Дорогое', 'недёшево': 'Дорогое',
        'дорогой': 'Дорогое', 'дорого': 'Дорогое', 'очень дорого': 'Очень дорогое',
        'дёшево': 'Дешёвка', 'бесплатно': 'Бесплатно', 'о. дорогое': 'Очень дорогое',
    }""")

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n'.join(fixes))
