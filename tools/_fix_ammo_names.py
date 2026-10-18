# -*- coding: utf-8 -*-
"""Выравнивание названий боеприпасов по ДатаПулу."""
import io

P = r'D:\Desktop\cCPRED\tools\build_dp_additions.py'
s = io.open(P, encoding='utf-8').read()

pairs = [
    ("'\u0414\u0435\u0448\u0451\u0432\u044b\u0435 \u0431\u043e\u0435\u043f\u0440\u0438\u043f\u0430\u0441\u044b'", "'\u0414\u0435\u0448\u0435\u0432\u044b\u0435 \u0431\u043e\u0435\u043f\u0440\u0438\u043f\u0430\u0441\u044b'"),
    ("'\u0423\u043b\u0443\u0447\u0448\u0435\u043d\u043d\u044b\u0435 \u0443\u043c\u043d\u044b\u0435 \u0431\u043e\u0435\u043f\u0440\u0438\u043f\u0430\u0441\u044b'",
     "'\u0423\u043b\u0443\u0447\u0448\u0435\u043d\u043d\u044b\u0439 \u0443\u043c\u043d\u044b\u0439 \u0431\u043e\u0435\u043f\u0440\u0438\u043f\u0430\u0441'"),
]
for a, b in pairs:
    n = s.count(a)
    s = s.replace(a, b)
    print('replaced %d x %s' % (n, a.encode('ascii', 'backslashreplace').decode()))

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done')
