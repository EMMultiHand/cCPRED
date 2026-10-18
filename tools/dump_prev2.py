# -*- coding: utf-8 -*-
"""Превью: строки брони 12-31, борги, pkt_implants, pkt_packs, exotic."""
import json
import os

TMP = os.environ.get('TEMP', '.')


def main():
    out = []

    dpa = json.load(open(os.path.join(TMP, 'dp_tables_equipment_armor.json'), encoding='utf-8'))
    out.append('=== ARMOR rows 11-31 (0-based) ===')
    for r in dpa[0]['rows'][11:]:
        out.append(' | '.join([str(x).replace('\n', ' ')[:110] for x in r[:5]]))
    out.append('')

    dbb = json.load(open(os.path.join(TMP, 'dp_tables_chrome_borgs.json'), encoding='utf-8'))
    out.append('=== BORGS sections ===')
    for i, sec in enumerate(dbb):
        out.append('[%d] %s | headers: %s' % (i, sec.get('section'), ' | '.join(map(str, sec.get('headers', [])))))
        for r in sec.get('rows', []):
            out.append('   ' + json.dumps(r, ensure_ascii=False)[:500])
    out.append('')

    dpi = json.load(open(os.path.join(TMP, 'dp_tables_chrome_pkt_implants.json'), encoding='utf-8'))
    out.append('=== PKT_IMPLANTS ===')
    for i, sec in enumerate(dpi):
        out.append('[%d] %s | headers: %s' % (i, sec.get('section'), ' | '.join(map(str, sec.get('headers', [])))))
        for r in sec.get('rows', []):
            out.append('   ' + json.dumps(r, ensure_ascii=False)[:500])
    out.append('')

    dpp = json.load(open(os.path.join(TMP, 'dp_tables_chrome_pkt_packs.json'), encoding='utf-8'))
    out.append('=== PKT_PACKS ===')
    for i, sec in enumerate(dpp):
        out.append('[%d] %s | headers: %s' % (i, sec.get('section'), ' | '.join(map(str, sec.get('headers', [])))))
        for r in sec.get('rows', []):
            out.append('   ' + json.dumps(r, ensure_ascii=False)[:400])
    out.append('')

    dex = json.load(open(os.path.join(TMP, 'dp_tables_chrome_exotic.json'), encoding='utf-8'))
    out.append('=== EXOTIC summary ===')
    for i, sec in enumerate(dex):
        out.append('[%d] %s | headers: %s' % (i, sec.get('section'), ' | '.join(map(str, sec.get('headers', [])))))
        for r in sec.get('rows', []):
            out.append('   ' + json.dumps(r[:3], ensure_ascii=False)[:260])
    out.append('')

    # implants [9]..[11] raw rows + [0..4] special rows
    dpi2 = json.load(open(os.path.join(TMP, 'dp_tables_chrome_implants.json'), encoding='utf-8'))
    need = ['Управление Дронами', 'Щепка навыка', 'Чип переводчик', 'Хранилище щепок', 'sparkle-ize', 'Киберчереп',
            'Хотсвап', 'Sycust', 'КиберПроводник', 'Интегрированный КиберСканер', 'Быстрые Пальцы',
            'Skydrivers', 'нулевой гравитации', 'Стопа-Трансформер']
    out.append('=== IMPLANT rows (select) ===')
    for sec in dpi2:
        for r in sec.get('rows', []):
            nm = str(r[0])
            for n in need:
                if n.lower() in nm.lower():
                    out.append('   ' + json.dumps(r, ensure_ascii=False)[:420])
    out.append('')
    out.append('=== IMPLANT sect 10 & 11 rows ===')
    for i in (10, 11):
        if i < len(dpi2):
            out.append('[%d] %s' % (i, dpi2[i].get('section')))
            for r in dpi2[i].get('rows', []):
                out.append('   ' + json.dumps(r, ensure_ascii=False)[:420])

    open(os.path.join(TMP, 'prev2.txt'), 'w', encoding='utf-8').write('\n'.join(out))
    print('->', os.path.join(TMP, 'prev2.txt'))


if __name__ == '__main__':
    main()
