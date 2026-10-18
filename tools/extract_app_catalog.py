# -*- coding: utf-8 -*-
r"""Извлекает каталожные записи из декодированного main.dart.js в JSON.

Ищет конструкции:
    B.xxx=s([...],t.X)
    B.xxx=new A.h(B.key,[...],t.X)
и «мастер-массивы» из одних ссылок:
    B.xxx=s([B.a,B.b,...],A.aN("Q<...>"))

Результат: $TEMP/app_catalog.json + $TEMP/app_catalog_report.txt
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEC = os.path.join(os.environ.get('TEMP', '.'), 'rb_main_decoded.txt')
OUT_JSON = os.path.join(os.environ.get('TEMP', '.'), 'app_catalog.json')
OUT_REP = os.path.join(os.environ.get('TEMP', '.'), 'app_catalog_report.txt')


def find_close(s, i):
    """i указывает на '[' или '{' — вернуть индекс закрывающей скобки."""
    open_ch = s[i]
    close_ch = ']' if open_ch == '[' else '}'
    depth = 0
    in_str = None
    j = i
    while j < len(s):
        c = s[j]
        if in_str:
            if c == '\\':
                j += 2
                continue
            if c == in_str:
                in_str = None
        else:
            if c in '"\'`':
                in_str = c
            elif c in '[{':
                depth += 1
            elif c in ']}':
                depth -= 1
                if depth == 0:
                    return j
        j += 1
    return -1


def split_top(s):
    out = []
    depth = 0
    in_str = None
    cur = []
    i = 0
    while i < len(s):
        c = s[i]
        if in_str:
            cur.append(c)
            if c == '\\':
                if i + 1 < len(s):
                    cur.append(s[i + 1])
                    i += 1
            elif c == in_str:
                in_str = None
        else:
            if c in '"\'`':
                in_str = c
                cur.append(c)
            elif c in '[{':
                depth += 1
                cur.append(c)
            elif c in ']}':
                depth -= 1
                cur.append(c)
            elif c == ',' and depth == 0:
                out.append(''.join(cur).strip())
                cur = []
            else:
                cur.append(c)
        i += 1
    if cur:
        out.append(''.join(cur).strip())
    return out


def parse_elem(tok):
    tok = tok.strip()
    if not tok:
        return None
    if tok[0] in '"\'':
        q = tok[0]
        body = tok[1:-1] if tok[-1] == q else tok[1:]
        body = body.replace('\\' + q, q).replace('\\n', '\n').replace('\\t', '\t')
        return body
    if re.fullmatch(r'-?\d+(\.\d+)?', tok):
        return float(tok) if '.' in tok else int(tok)
    if tok.startswith('['):
        inner = tok[1:-1]
        return [parse_elem(x) for x in split_top(inner)]
    if tok.startswith('{'):
        d = {}
        for kv in split_top(tok[1:-1]):
            if ':' in kv:
                k, v = kv.split(':', 1)
                d[k.strip()] = parse_elem(v)
        return d
    if re.fullmatch(r'[A-Za-z_$][\w$]*\.[\w$]+', tok):
        return {'$ref': tok}
    return {'$raw': tok}


def main():
    dec = open(DEC, encoding='utf-8').read()
    entries = {}
    master_arrays = {}

    # 1) B.xxx=new A.h(KEY,[...],t.Y)  или  B.xxx=s([...],t.Y)
    pat1 = re.compile(r'([A-Za-z_$][\w$]*\.[\w$]+)=new A\.h\((.+?),\s*(\[)', re.S)
    pat2 = re.compile(r'([A-Za-z_$][\w$]*\.[\w$]+)=s\((\[)', re.S)

    def add_entry(mid, start_bracket):
        end = find_close(dec, start_bracket)
        if end < 0:
            return
        arr = dec[start_bracket:end + 1]
        try:
            fields = parse_elem(arr)
        except Exception:
            return
        entries[mid] = fields

    count1 = count2 = 0
    for m in pat1.finditer(dec):
        add_entry(m.group(1), m.start(3))
        count1 += 1
    for m in pat2.finditer(dec):
        add_entry(m.group(1), m.start(2))
        count2 += 1

    # 2) мастер-массивы ссылок: B.xxx=s([B.a,B.b,...],
    for mid, fields in entries.items():
        if isinstance(fields, list) and fields and all(
                isinstance(x, dict) and '$ref' in x for x in fields):
            master_arrays[mid] = [x['$ref'] for x in fields]

    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump({'entries': entries, 'master_arrays': master_arrays}, f,
                  ensure_ascii=False, indent=1)

    # отчёт по формам
    shapes = {}
    for mid, fields in entries.items():
        if not isinstance(fields, list):
            continue
        key = len(fields)
        shapes.setdefault(key, []).append(mid)

    with open(OUT_REP, 'w', encoding='utf-8') as f:
        f.write('entries: %d (pat1=%d pat2=%d), master arrays: %d\n\n'
                % (len(entries), count1, count2, len(master_arrays)))
        f.write('-- распределение по числу полей --\n')
        for k in sorted(shapes):
            f.write('len=%d: %d записей, напр.: %s\n'
                    % (k, len(shapes[k]), ', '.join(sorted(shapes[k])[:8])))
        f.write('\n-- мастер-массивы (>3 элементов) --\n')
        for mid, refs in sorted(master_arrays.items(), key=lambda x: -len(x[1])):
            if len(refs) > 3:
                f.write('%s: %d refs, первые: %s\n' % (mid, len(refs), ', '.join(refs[:6])))
    print('json ->', OUT_JSON)
    print('report ->', OUT_REP)
    return 0


if __name__ == '__main__':
    sys.exit(main())
