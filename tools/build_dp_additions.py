# -*- coding: utf-8 -*-
"""
Сборка готовых записей дополнений из данных ДатаПула в формат каталога приложения.

Читает JSON-таблицы ДатаПула из %TEMP% (dp_tables_*.json), применяет курированные
конфиги (списки названий и параметров) и пишет tools/dp_additions.json:
    {
      "weapons":   [ [13 полей] ],
      "armor":     [ [8 полей] ],
      "implants":  [ [9 полей] ],
      "equipment": [ [6 полей] ],
      "corps":     [ [7 полей] ],
      "ammo":      { "B.jT": [строки], ... }
    }
"""
import json
import os
import re
import sys

TMP = os.environ.get('TEMP', '.')
OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def load(name):
    path = os.path.join(TMP, 'dp_tables_%s.json' % name)
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def norm(s):
    s = str(s)
    for a, b in [('’', "'"), ('‘', "'"), ('“', '"'), ('”', '"'), ('«', '"'), ('»', '"')]:
        s = s.replace(a, b)
    s = s.lower()
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def find_row(section, name):
    """Найти строку по названию (нормализованно). Бросает, если не найдено."""
    for row in section.get('rows', []):
        if norm(row[0]) == norm(name):
            return row
    raise KeyError('row not found: %s' % name)


def clean_text(s):
    s = str(s).replace('\r', '')
    return s.strip()


def clean_price(s):
    s = str(s).replace('\r', '').replace('\n', ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    s = s.replace('еЬ', 'eb').replace('еb', 'eb').replace('еВ', 'eb')
    s = s.replace('eb(', 'eb (')
    repl = [
        ('(О.дорогое)', '(О. дорогое)'), ('(О.Дорогое)', '(О. дорогое)'),
        ('(О. Дорогое)', '(О. дорогое)'), ('(0. дорогое)', '(О. дорогое)'),
        ('(0.Дорогое)', '(О. дорогое)'), ('(О Дорогое)', '(О. дорогое)'),
        ('(О.дорогое)', '(О. дорогое)'), ('(Оч.Дорогое)', '(О. дорогое)'),
        ('(Оч. дорогое)', '(О. дорогое)'),
        ('(Очень Дорогое)', '(Очень дорогое)'), ('(Очень Дорого)', '(Очень дорогое)'),
        ('(Очень дорого)', '(Очень дорогое)'),
        ('(Супер Роскошь)', '(Супер роскошь)'),
        ('(Дорогой)', '(Дорогое)'), ('(дорогой)', '(Дорогое)'), ('(Дорого)', '(Дорогое)'),
        ('(Дорогое)', '(Дорогое)'), ('(дорогое)', '(Дорогое)'),
        ('(Дёшево)', '(Дешёвка)'), ('(Дешево)', '(Дешёвка)'), ('(Дешевка)', '(Дешёвка)'),
        ('(дешево)', '(Дешёвка)'), ('(дешёвка)', '(Дешёвка)'),
        ('(премиум)', '(Премиум)'), ('(ценное)', '(Ценное)'), ('(обычное)', '(Обычное)'),
        ('  ', ' '),
    ]
    for a, b in repl:
        s = s.replace(a, b)
    if s.count('(') > s.count(')') and s.rstrip().endswith('Роскошь'):
        s = s.rstrip() + ')'
        s = s.replace('(Супер Роскошь)', '(Супер роскошь)')
    return s


def clean_humanity(s):
    s = str(s).replace('\r', '').replace('\n', ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    s = s.replace('к6', 'd6')
    s = s.replace('[2d6/2 round up]', '2d6/2, округление вверх')
    s = s.replace('[', '(').replace(']', ')')
    return s


def paragraphs(txt):
    txt = str(txt).replace('\r', '')
    parts = [re.sub(r'\s*\n\s*', ' ', p).strip() for p in re.split(r'\n\s*\n', txt)]
    return [p for p in parts if p]


def split_desc(txt):
    ps = paragraphs(txt)
    if not ps:
        return '', ''
    if len(ps) == 1:
        return ps[0], ''
    return ps[0], '\n\n'.join(ps[1:])


def fix_name(s):
    s = str(s)
    for a, b in [('“', '"'), ('”', '"'), ('„', '"'), ('«', '"'), ('»', '"')]:
        s = s.replace(a, b)
    return re.sub(r'\s+', ' ', s.replace('\n', ' ')).strip()


def strip_source(s):
    """Убрать хвост «Источник: ...» из текста."""
    s = re.sub(r'\s*Источник:[^\n]*', '', str(s))
    return s.strip()


def compose_rules(feats, desc_ps):
    ps = [strip_source(p) for p in desc_ps]
    ps = [p for p in ps if p]
    parts = ([feats] if feats else []) + (ps[-1:] if ps else [])
    return '\n'.join(parts)


def first_int(s, default=1):
    m = re.search(r'\d+', str(s))
    return int(m.group(0)) if m else default


# ---------------------------------------------------------------- источники

SRC_WEAPON = {
    'корбук': 'Cyberpunk RED',
    'кор бук': 'Cyberpunk RED',
    'книга правил': 'Cyberpunk RED',
    'corebook': 'Cyberpunk RED',
    '12днейкибероруждества': '12 дней оруждества',
    '12 дней кибероруждества': '12 дней оруждества',
    '12днейкиберкутячества': '12 дней улётных няшек',
    '12 дней киберкутячества': '12 дней улётных няшек',
    '12днейкиберутячества': '12 дней улётных няшек',
    '12днейкиберрождества': '12 дней Киберрождества',
    '12 дней киберрождества': '12 дней Киберрождества',
    '12днейредмаса': '12 дней киберждества',
    'the 12 days of redmas': '12 дней киберждества',
    'черный хром': 'Чёрный хром',
    'чёрный хром': 'Чёрный хром',
    'черный хром+': 'Чёрный хром',
    'чёрный хром+': 'Чёрный хром',
    'черныйхром': 'Чёрный хром',
    'black chrome': 'Чёрный хром',
    'микрохром': 'Микрохром',
    'оружие 2070-х': 'Оружие 2070-х',
}

SRC_IMPLANT = {
    '“корбук”': 'Cyberpunk RED',
    'корбук': 'Cyberpunk RED',
    'книга правил': 'Cyberpunk RED',
    'черныйхром': 'Чёрный хром',
    'чёрныйхром': 'Чёрный хром',
    'чёрный хром': 'Чёрный хром',
    'черный хром': 'Чёрный хром',
    'black chrome': 'Чёрный хром',
    'the 12 days of redmas': '12 дней Киберждества',
    '12 дней редмаса': '12 дней Киберждества',
    '12днейкиберрождества': '12 дней Киберрождества',
    '12 дней киберрождества': '12 дней Киберрождества',
    '12днейкибероруждества': '12 дней оруждества',
    '12 дней кибероруждества': '12 дней оруждества',
    'все об агентах': 'Все Об Агентах',
    'переходи на металл': 'Переходи на Металл',
    'пнм': 'Переходи на Металл',
    'the 12 days of cutiemas': '12 дней улётных няшек',
    'новый хром! покупай': 'Новый Хром! Покупай',
    'аптека хорнета': 'Аптека Хорнета',
    'мешай напитки': 'Мешая Напитки - Верши Судьбы',
    'мешая напитки - верши судьбы': 'Мешая Напитки - Верши Судьбы',
    'бодискульптинг': 'Бодискульптинг',
    'китиган': 'КитиГан',
    'микрохром': 'Микрохром',
    'edgerunners mission kit': 'Edgerunners Mission Kit',
}


def map_source(raw, table):
    key = norm(raw).strip('"').strip()
    key2 = key.replace('"', '').strip()
    for k in (key, key2):
        if k in table:
            return table[k]
    return str(raw).strip()


def weapon_source(table_idx, row):
    name = norm(str(row[0]))
    if table_idx in (2, 3, 4, 5):
        if 'hello cutie' in name or 'sanroo' in name:
            return '12 дней улётных няшек'
        return 'Храм Тоггла'
    if table_idx in (19, 22):
        return 'Оружие 2070-х'
    raw = _istochnik(row)
    if raw:
        return map_source(raw, SRC_WEAPON)
    if table_idx == 14:
        return '12 дней киберждества'
    if 'hello cutie' in name or 'sanroo' in name:
        return '12 дней улётных няшек'
    return 'Чёрный хром'


def _istochnik(row):
    """Достать «Источник: X» из ячеек строки (если есть)."""
    for cell in row:
        s = str(cell)
        if 'Источник:' in s:
            tail = s.split('Источник:')[-1]
            tail = tail.split('\n')[0]
            tail = tail.strip().strip('.,;').strip()
            if tail:
                return tail
    return ''


# ---------------------------------------------------------------- оружие

WEAPON_TABLES = {
    2: [
        'Dai Lung Streetmaster', 'Faisal’s Escape Plan', 'Federated Arms X-9mm', 'Militech Avenger',
        'Nomad .357 Magnum', 'Towa Type-12 Police Pistol', 'Pursuit Security E-TACK Rapid Responder',
        'Dai Lung Magnum', 'GunMart Midnight Defender', 'Militech Sheriff', 'Mustang Arms Mark II',
        'Mustang Arms Mark III', 'Nova Cityhunter X', 'Faisal’s Convenience',
        'Federated Arms Super Chief Plus', 'Militech Boomer Buster', 'Nomad Big Gulp', 'Sternmeyer P-35',
        'Sternmeyer P-35 Covert', 'Длинноствольный Пистолет Нэт', 'Arasaka Minami 10',
        'Arasaka Minami 10 P/M/S', 'Dai Lung Cybermag 20', 'Federated Arms Tech-Assault III',
        'Militech Mini-Gat', 'Mustang Arms Rodeo', 'Chadran Arms City Reaper', 'IMI UZ 2045 Pro',
        'Militech Viper', 'Sternmeyer SMG-21', 'Sanroo Hello Cutie Hidden Cougar',
        'Sanroo Hello Cutie Happy Dancer',
    ],
    3: [
        'Arasaka Rapid Assault', 'Faisal’s OnlyChance', 'GunMart Home Defender', 'Militech Bulldog',
        'Mustang Arms Deathstalker', 'SlamDance ElectroMag', 'Chadran Arms Jungle Reaper',
        'Darra Polytechnic Binary', 'Militech Dragon', 'Militech Ronin',
        'Militech Ronin Hyperlight Assault', 'Sternmeyer M-95A4 Assault Weapon',
        'Everest VentureWare SportMaster', 'Arasaka WSS Sniper System',
        'Everest VentureWare Kodiak Hunter', 'GunMart Snipe-Starr', 'Militech Ninja Sniper',
        'Nomad Long Rifle', 'Towa Type-00-Kai',
    ],
    4: [
        'Arasaka Origami', 'Eagletech Bearcat', 'Eagletech Tigercat', 'Eagletech Tomcat',
        'GunMart Hawk’s Eye', 'GunMart Sherwood', 'Eagletech Arbelest', 'Eagletech Scorpion',
        'Eagletech Stryker', 'Everest VentureWare Mountaineer', 'GunMart Hunter',
        'GunMart Midnight Hunter',
    ],
    5: [
        'GunMart Porta-Morta', 'Militech Mini-Grenade', 'Towa Manufacturing Type-G',
        'Towa Manufacturing Type-G*2', 'Tsunami Arms Type-18', 'Tsunami Arms Type-18-S',
        'MetaCorp Hela Smart Launcher', 'Militech Hotshot L-ATGM', 'Militech Starshot L-ATGM-N',
        'Militech Urban', 'Towa Manufacturing Type-R', 'Towa Manufacturing Type-R*2',
    ],
    9: ['Микромилашка от Hello Cutie', 'Обрез ПМВ Винтовки в Пистолет', 'Big Dreem'],
    10: ['Воздушка Кочевников', 'Everest VentureWare SurvivalMaster', 'Sanroo Hello Cutie 1TruLuv'],
    11: [
        'Разлагающаяся ПУ Биотехника', 'Тройное Удовольствие от БлюджетАрмс', 'Сигнальная Ракетница',
        'SDF-45 Минднайт Армс', 'Милитех Эгида', 'Милитех Архимед',
        'Балистический Гарпун от СлэмДэнс', 'Pursuit Security Inc Tearjerker',
        'Тяжелая Винтовка Sternmeyer M-02', 'Карманная Ракетница Това',
    ],
    14: ['Термальный Клинок Centurion essentials'],
    19: [
        'ПП Arasaka Takanami', 'Штурмовая Arasaka Neo Rapid 16', 'Пулемёт MetaCorp «Victoria»',
        'СВК Midnight Arms Dawnmaker', 'Штурмовой Midnight Arms Midnight HB',
        'Лёгкий пулемёт Militech MK.27', 'Винтовка Militech Mountain Goat', 'Scatter Ratter',
        'Рельсотрон Tsunami Arms «Deathwind»', 'ПУ липких бомб Highland Defense', 'Militech Big Boomer',
    ],
    22: [
        'Arasaka HJKE-11 Yukimura', 'Arasaka HJSH-18 Masamune', 'Arasaka TKI-20 Shingen',
        'Budget Arms Carnage', 'Constitutional Arms Unity', 'Kang Tao L-69 Zhuo',
        'Militech Crusher (периода 207X)', 'Militech M-10AF Lexington', 'Militech M-76e Omaha',
        'Rostović DB-2 Satara Shotgun', 'Техтроника РТ-46 Буря', 'Техтроника СПТ32 Град',
        'Tsunami Arms Nekomata',
    ],
}

BRANDS = [
    'Arasaka', 'Militech', 'GunMart', 'Faisal', 'Dai Lung', 'Towa', 'Federated Arms', 'Nomad',
    'Mustang Arms', 'Nova', 'Sternmeyer', 'Eagletech', 'Everest VentureWare', 'Chadran Arms',
    'Darra Polytechnic', 'SlamDance', 'Sanroo', 'Hello Cutie', 'Tsunami Arms', 'MetaCorp',
    'Highland Defense', 'Kang Tao', 'Budget Arms', 'Constitutional Arms', 'Rostović',
    'Техтроника', 'IMI', 'Pursuit Security', 'Centurion Essentials', 'Midnight Arms', 'Rheinmetall',
]

SKILL_MAP = {
    'пистолет': 'Пистолеты',
    'тактическое': 'Тактическое оружие',
    'ор.кр.калибра': 'Оружие крупного калибра',
    'ор. кр. калибра': 'Оружие крупного калибра',
    'оружие крупного калибра': 'Оружие крупного калибра',
    'автоогонь': 'Автоматический огонь',
    'лук': 'Стрельба из лука',
    'короткоствольное оружие': 'Пистолеты',
    'длинноствольное оружие': 'Тактическое оружие',
    'тяжёлое оружие': 'Оружие крупного калибра',
    'тяжелое оружие': 'Оружие крупного калибра',
}


def map_skill(raw):
    s = re.sub(r'\s+', ' ', str(raw).replace('\n', ' ')).strip()
    low = norm(s)
    if low in SKILL_MAP:
        return SKILL_MAP[low]
    if 'автоогонь' in low and 'пистолет' in low:
        return 'Пистолеты / Автоматический огонь'
    if 'автоогонь' in low and ('тактическ' in low or 'винтовк' in low):
        return 'Тактическое оружие / Автоматический огонь'
    if 'пистолет' in low:
        return 'Пистолеты'
    if 'тактическ' in low or 'дробовик' in low or 'винтовк' in low:
        return 'Тактическое оружие'
    return s


def map_ammo_str(raw):
    s = re.sub(r'\s+', ' ', str(raw).replace('\n', ' ')).strip()
    m = re.match(r'^(\d+(?:-\d+)?)\s+(.+)$', s)
    if m:
        n, rest = m.group(1), m.group(2).strip()
        eq = {
            'С.Пистолет': 'Пистолет', 'С Пистолет': 'Пистолет',
            'Т.Пистолет': 'Тяжёлый пистолет', 'Т Пистолет': 'Тяжёлый пистолет',
            'ОТ.Пистолет': 'Очень тяжёлый пистолет', 'ОТ Пистолет': 'Очень тяжёлый пистолет',
        }
        rest = eq.get(rest, rest)
        return '%s (%s)' % (n, rest)
    return s


def norm_conceal(raw):
    s = norm(raw)
    if s.startswith('да'):
        return 'да'
    if s.startswith('нет'):
        return 'нет'
    return str(raw).strip()


def brand_of(name):
    low = norm(name)
    for b in BRANDS:
        if low.startswith(norm(b)):
            return b
    return '—'


def build_weapons(wsec):
    out = []
    unmatched = []
    for t, names in sorted(WEAPON_TABLES.items()):
        for nm in names:
            try:
                row = find_row(wsec[t], nm)
            except KeyError:
                unmatched.append('[#%d] %s' % (t, nm))
                continue
            name = fix_name(row[0])
            src = weapon_source(t, row)
            if t in (2, 3, 4, 5):
                skill = map_skill(row[1])
                dmg = re.sub(r'\s+', ' ', str(row[2]).replace('\n', '/')).strip()
                ammo = map_ammo_str(row[3])
                rof = first_int(row[4])
                hands = str(row[5]).strip()
                conceal = norm_conceal(row[7])
                price = clean_price(row[9])
                special = compose_rules('', paragraphs(row[8]))
            elif t in (9, 10, 11, 12):
                skill = map_skill(row[1])
                dmg = re.sub(r'\s+', ' ', str(row[2]).replace('\n', '/')).strip()
                ammo = map_ammo_str(row[3])
                rof = first_int(row[4])
                hands = str(row[5]).strip()
                conceal = norm_conceal(row[6])
                price = clean_price(row[9])
                feats = re.sub(r'\s+', ' ', str(row[7]).replace('\n', ' ')).strip()
                special = compose_rules(feats, paragraphs(row[8]))
            elif t == 14:
                skill = 'Оружие ближнего боя'
                dmg = re.sub(r'\s+', ' ', str(row[2]).replace('\n', '/')).strip()
                ammo = '—'
                rof = first_int(row[3])
                hands = str(row[4]).strip()
                conceal = norm_conceal(row[5])
                price = clean_price(row[7])
                special = strip_source(
                    re.sub(r'\s+', ' ', str(row[6]).replace('\n', ' ')).strip())
            elif t in (19, 22):
                skill = map_skill(row[1])
                dmg = re.sub(r'\s+', ' ', str(row[2]).replace('\n', '/')).strip()
                ammo = map_ammo_str(row[3])
                rof = first_int(row[4])
                hands = str(row[5]).strip()
                conceal = norm_conceal(row[6])
                price = clean_price(row[9])
                feats = re.sub(r'\s+', ' ', str(row[7]).replace('\n', ' ')).strip()
                special = compose_rules(feats, paragraphs(row[8]))
            else:
                continue
            # "3d6 5d6" (два режима) -> "3d6/5d6"
            dmg = re.sub(r'^(\d+d\d+)\s+(\d+d\d+)$', r'\1/\2', dmg)
            category = 'Ближний бой' if t == 14 else 'Дальний бой'
            rec = [name, brand_of(name), src, 0, category, skill, dmg, ammo, rof, hands, conceal, price, special]
            out.append(rec)
    return out, unmatched


# ---------------------------------------------------------------- броня

ARMOR_NAMES = [
    'Корпоративный Остров', 'Боевая Куртка Кортик', 'Броня Корпората', 'Бункерное Снаряжение',
    'Уличная Куртка Лазерный Свет', 'Сетевой Костюм Лотос', 'Воздушный Наездник', 'Голо-Одежда',
    'МехаМэн мотоциклетный шлем', 'МехаМэн Умная Перчатка', 'Комплект Мимиковской Одежды',
    'Линия Изменяющейся Одежды Монтаж', 'Шоковая Броня', 'СкидРоу Тренч',
    'Ездовой костюм “Уличная Гадюка”', 'Тактическая Умная Броня', 'Куртка Супервспышка',
    'Костюм РХБЗ от Esporma', 'Кустарная броня, броня из хлама', 'Тяжёлый Metalgear®',
    'Гибридный Metalgear®',
]

ARMOR_CAT = {
    'тело/голова': 'Броня тела и головы',
    'тело': 'Броня тела',
    'голова': 'Броня головы',
    'щит': 'Щит',
}


def build_armor(asec):
    out = []
    unmatched = []
    for nm in ARMOR_NAMES:
        try:
            row = find_row(asec[0], nm)
        except KeyError:
            unmatched.append(nm)
            continue
        name = fix_name(row[0])
        sp_s = str(row[1]).strip()
        m = re.match(r'^(\d+)', sp_s)
        sp = int(m.group(1)) if m else 0
        part = norm(row[2])
        cat = ARMOR_CAT.get(part, 'Броня тела')
        pen_s = norm(row[3])
        if pen_s.startswith('нет') or pen_s in ('', '----------'):
            pen = 0
        else:
            mp = re.search(r'(-?\d+)', pen_s)
            pen = int(mp.group(1)) if mp else 0
        price = clean_price(row[4])
        details = strip_source(re.sub(r'\s*\n\s*', ' ', str(row[5])).strip())
        rec = [name, 'Чёрный хром', cat, sp, pen, price, details, '@@RAW:u.x@@']
        out.append(rec)
    return out, unmatched


# ---------------------------------------------------------------- импланты

# (таблица, индекс секции, имя, type, category, прим.)
IMPLANTS = [
    ('implants', 1, 'Керензиков', 'neural', 'Опция Нейролинка', ''),
    ('implants', 1, 'Сандевистан', 'neural', 'Опция Нейролинка', ''),
    ('implants', 1, 'Управление Дронами', 'neural', 'Опция Нейролинка', ''),
    ('implants', 1, 'Щепка навыка', 'neural', 'Щепка', ''),
    ('implants', 1, 'Чип переводчик', 'neural', 'Щепка', ''),
    ('implants', 2, 'Хранилище щепок', 'optics', 'Опция Киберглаза', ''),
    ('implants', 2, 'Hello Cutie sparkle-ize', 'optics', 'Опция Киберглаза', ''),
    ('implants', 4, 'Киберчереп', 'head', 'Внутренний киберимплант', ''),
    ('implants', 4, 'Хотсвап крепление Лицевой Панели', 'head', 'Внутренний киберимплант', ''),
    ('implants', 4, 'Sycust Киберпозвоночник', 'torso|internal', 'Внутренний киберимплант', ''),
    ('implants', 4, 'КиберПроводник Zetatech, Встроенный', 'torso|borg', 'Боргирование', ''),
    ('implants', 6, 'Интегрированный КиберСканер', 'arm', 'Опция Киберруки', ''),
    ('implants', 6, 'Быстрые Пальцы Rocklin Augmentics', 'arm', 'Опция Киберруки', ''),
    ('implants', 7, 'Rocklin Augmentics Skydrivers', 'leg', 'Кибернога', ''),
    ('implants', 7, 'Устройство нулевой гравитации', 'leg', 'Опция киберноги', ''),
    ('implants', 7, 'Стопа-Трансформер', 'leg', 'Опция киберноги', ''),
    ('implants', 10, 'Берсерк', 'neural', 'Опция Нейролинка', ''),
    ('implants', 10, 'ИнтраЛЕД', 'neural', 'Опция Нейропорта', ''),
    ('implants', 10, 'Клинок Богомола', 'arm', 'Опция Киберруки', ''),
    ('implants', 10, 'Мега-Диск', 'neural', 'Опция Нейролинка', ''),
    ('implants', 10, 'Моноструна', 'arm', 'Опция Киберруки', ''),
    ('implants', 10, 'Нейропорт', 'neural', 'Нейроимплант', ''),
    ('implants', 10, 'Рука Гориллы', 'arm', 'Опция Киберруки', ''),
    ('implants', 10, 'Система запуска снарядов', 'arm', 'Опция Киберруки', ''),
    ('implants', 10, 'Слот Нейропорта для Кибердеки', 'neural', 'Опция Нейропорта', ''),
    ('implants', 10, 'Эксперементальный Сандевистан Девида', 'neural', 'Опция Нейролинка', ''),
    ('implants', 11, 'Гидравлический Таран', 'arm', 'Улучшение киберимпланта', ''),
    ('implants', 11, 'Пневматические приводы', 'arm', 'Улучшение киберимпланта', ''),
    ('implants', 11, 'Вольфрамовое укрепление', 'arm', 'Улучшение киберимпланта', ''),
    ('implants', 11, 'Двухсторонняя заточка', 'arm', 'Улучшение киберимпланта', ''),
    ('implants', 11, 'Мономолекулярное лезвие', 'arm', 'Улучшение киберимпланта', ''),
    ('implants', 11, 'Обтекаемость', 'arm', 'Улучшение киберимпланта', ''),
    ('implants', 11, 'Колючая проволока', 'arm', 'Улучшение киберимпланта', ''),
    ('implants', 11, 'Электрошокер', 'arm', 'Улучшение киберимпланта', ''),
    ('implants', 11, 'Раскалённые лезвия', 'arm', 'Улучшение киберимпланта', ''),
    ('borgs', 0, 'Cкелет ЛФ-001 SWAT', 'torso|borg', 'Боргирование', ''),
    ('borgs', 0, 'Cкелет Фūма Котарō', 'torso|borg', 'Боргирование', ''),
    ('borgs', 0, 'Cкелет Вермилион', 'torso|borg', 'Боргирование', ''),
    ('borgs', 0, 'Экзоскелет ЭЛ-Ф4-НТ', 'torso|borg', 'Боргирование', ''),
    ('borgs', 1, 'БИОСИСТЕМА', 'torso|borg', 'Боргирование', ''),
    ('borgs', 1, 'Броня Драгуна', 'torso|borg', 'Боргирование', ''),
    ('borgs', 1, 'Броня Драгуна (МЕТАЛГИР)', 'torso|borg', 'Боргирование', ''),
    ('borgs', 1, 'Имплантированный Эндоскелет Ω (ОМЕГА)', 'torso|borg', 'Боргирование', ''),
    ('pkt_implants', 0, 'ПОКРЫТИЕ "СЕРА”', 'torso|borg', 'ПКТ имплант', ''),
    ('pkt_implants', 0, 'ПОКРЫТИЕ "ХАМЕЛЕОН”', 'torso|borg', 'ПКТ имплант', ''),
    ('pkt_implants', 0, 'АНТИЭМИ ПОКРЫТИЕ', 'torso|borg', 'ПКТ имплант', ''),
    ('pkt_implants', 0, 'БОДИСКУЛЬПТИНГ "БЛИЗНЕЦЫ”', 'torso|borg', 'ПКТ имплант', ''),
    ('pkt_implants', 0, 'ПОКРЫТИЕ "БОДИВЕЙТ”', 'torso|borg', 'ПКТ имплант', ''),
    ('pkt_implants', 0, 'МОДЕРНИЗАЦИЯ ВНУТРЕННЕЙ ГИДРАВЛИКИ', 'torso|borg', 'ПКТ имплант', ''),
    ('pkt_implants', 0, 'ТЮНИНГ ВЕР. МОДЕРНИЗАЦИЯ ВНУТРЕННЕЙ ГИДРАВЛИКИ', 'torso|borg', 'ПКТ имплант', ''),
    ('pkt_implants', 0, 'СОВЕРШЕННАЯ МОДЕРНИЗАЦИЯ ВНУТРЕННЕЙ ГИДРАВЛИКИ', 'torso|borg', 'ПКТ имплант', ''),
]

EXOTIC_NAMES = [
    'ДЕМОН™', 'ОБЪЯТИЯ РОДЕНТИИ®', 'КОТИЙКУСЬ®', 'ЗАЙЦЕФОРМА®', 'ПЁСЬЯФОРМА®', 'СЕРПЕНТИЗИРУЙ CЕБЯ®',
    'АКВАФОРМА®', 'БОЛЬШЕКОТ®', 'ЖучийДом®', 'НЮВЫЙЧЕЛОВЕК™', 'МЕДВЕДОФОРМА®',
    'ФАНТАФОРМА™ ДРАКОН', 'ФАНТАФОРМА™ ДВОРФ', 'ФАНТАФОРМА™ ЭЛЬФ', 'ФАНТАФОРМА™ МЕРИШ',
    'ФАНТАФОРМА™ ОГР', 'ФАНТАФОРМ™ ОРК',
]

PKT_PACK_NAMES = [
    'КИБЕРМАТРИКС INC. "КОПЕРНИК”', 'ДИНАЛАР "ВОДОЛЕЙ”', 'ДИНАЛАР "СЕРА”',
    'МИЛИТЕХ "ДРАГУН" ИЗМ. ВОЕН. ПЛАТФОРМА', 'МИЛИТЕХ "ЗАТМЕНИЕ”', 'МИЛИТЕХ "СТРАЖ ПОРЯДКА”',
    'МИЛИТЕХ "ПАУК 2.0”', 'МУР ТЕХНОЛОДЖИС "ЯМА”', 'НОВЭЛТЕК "САМСОН”',
    'РЕЙВЕН МИКРОКИБЕРНЕТИКС "БЛИЗНЕЦЫ”', 'РЕЙВЕН МИКРОКИБЕРНЕТИКС "МУДРЕЦ”',
    'РОКЛИН АУГМЕНТИКС "КЛАСС АЛЬФА”', 'ТРАУМА ТИМ "КИЛЬ-ДАРА”',
]


def build_implants(tables):
    out = []
    unmatched = []

    def doc_source(raw, default='Чёрный хром'):
        key = norm(raw).strip('"').strip()
        if not key:
            return default
        return map_source(raw, SRC_IMPLANT) if (key in SRC_IMPLANT) else str(raw).strip().strip('"')

    for tab, idx, nm, typ, cat, _ in IMPLANTS:
        try:
            row = find_row(tables[tab][idx], nm)
        except KeyError:
            unmatched.append('[%s#%d] %s' % (tab, idx, nm))
            continue
        name = fix_name(row[0])
        if tab == 'implants' and idx == 11:
            # [name, описание, цена, документ]
            _, desc, price, doc = row[0], row[1], row[2], row[3]
            install = 'Госпиталь'
            hum = '3 (1d6)'
        elif tab == 'pkt_implants':
            # [Название, Цена, Установка, ПЧ, Описание]
            price = row[1]
            install = re.sub(r'\s+', ' ', str(row[2]).replace('\n', ' ')).strip() or 'Госпиталь'
            hum = row[3]
            desc = row[4] if len(row) > 4 else ''
            doc = 'Переходи на Металл'
        else:
            install = re.sub(r'\s+', ' ', str(row[1]).replace('\n', ' ')).strip() or 'Клиника'
            if norm(install) == 'нет':
                install = 'нет'
            desc = row[2]
            price = row[3]
            hum = row[4]
            doc = row[5] if len(row) > 5 else ''
        d, r = split_desc(desc)
        if norm(install) == 'нет':
            install = 'нет'
        src = doc_source(doc)
        rec = [name, typ, cat, src, clean_price(price), clean_humanity(hum), install, d, r]
        out.append(rec)

    # локальные правки текстов для приложения (в ДатаПуле формулировки иначе):
    # приводим ссылки на имплант к имени, под которым он есть в каталоге приложения
    TEXT_FIXES = {
        'Имплантированный Эндоскелет Ω (ОМЕГА)': [
            ('""Искусственные Мышцы и Усиленные Кости""',
             '“Усиленные мышцы и усиленные кости”')],
        'Cкелет ЛФ-001 SWAT': [
            ('две установки Искусственных мышц и усиленных костей',
             '2 импланта “Усиленные мышцы и усиленные кости”')],
        'Cкелет Фūма Котарō': [
            ('две установки Искусственных мышц и усиленных костей',
             '2 импланта “Усиленные мышцы и усиленные кости”')],
        'Cкелет Вермилион': [
            ('две установки Искусственных мышц и усиленных костей',
             '2 импланта “Усиленные мышцы и усиленные кости”')],
        'Управление Дронами': [('Gозволяет', 'Позволяет')],
        'Хранилище щепок': [('Отдел может', 'Отсек может')],
    }
    for rec in out:
        for a, b in TEXT_FIXES.get(rec[0], []):
            rec[7] = rec[7].replace(a, b)
            rec[8] = rec[8].replace(a, b)

    # биоэкзотика
    for nm in EXOTIC_NAMES:
        found = None
        for sec in tables['exotic']:
            for row in sec.get('rows', []):
                if norm(row[0]) == norm(nm):
                    found = row
                    break
            if found:
                break
        if not found:
            unmatched.append('[exotic] %s' % nm)
            continue
        name = fix_name(found[0])
        price = clean_price(found[1])
        hum = clean_humanity(found[2])
        comp = re.sub(r'[ \t]+', ' ', str(found[3]).replace('\r', '')).strip() if len(found) > 3 else ''
        desc_raw = found[4] if len(found) > 4 else ''
        d, r = split_desc(desc_raw)
        rules = ('Состав пакета: ' + comp + ('\n\n' + r if r else '')).strip()
        rec = [name, 'body|external', 'Биоэкзотика', 'Чёрный хром', price, hum, 'Клиника', d, rules]
        out.append(rec)

    # пкт-корпусы
    for nm in PKT_PACK_NAMES:
        try:
            row = find_row(tables['pkt_packs'][0], nm)
        except KeyError:
            unmatched.append('[pkt_packs] %s' % nm)
            continue
        name = fix_name(row[0])
        price = clean_price(row[1])
        hum = clean_humanity(row[2])
        comp_a = re.sub(r'[ \t]+', ' ', str(row[3]).replace('\r', '')).strip() if len(row) > 3 else ''
        comp_b = re.sub(r'[ \t]+', ' ', str(row[4]).replace('\r', '')).strip() if len(row) > 4 else ''
        extra = re.sub(r'\s+', ' ', str(row[5])).strip() if len(row) > 5 else ''
        desc_raw = row[6] if len(row) > 6 else ''
        d, r = split_desc(desc_raw)
        rules = []
        if comp_a:
            rules.append('Без ПЧ: ' + comp_a)
        if comp_b:
            rules.append('С ПЧ: ' + comp_b)
        if r:
            rules.append(r)
        install = extra if extra and 'оспитал' in extra else 'Госпиталь'
        rec = [name, 'torso|borg', 'Корпус ПКТ', 'Переходи на Металл', price, hum, install, d,
               '\n\n'.join(rules)]
        out.append(rec)

    return out, unmatched


# ---------------------------------------------------------------- снаряжение

EQ = [
    # (секция, имя_в_датапуле, категория, источник, переопределение_имени)
    ('items', 'Активные наушники', 'Связь и электроника', 'ДатаПул', ''),
    ('items', 'Анализатор Green Light от Hammered Industries', 'Инструменты', 'ДатаПул', ''),
    ('items', 'Антирадиационный костюм', 'Одежда', 'ДатаПул', ''),
    ('items', 'АэроСфера от ВорлдСат', 'Связь и электроника', 'ДатаПул', ''),
    ('items', 'Барабанный синтезатор', 'Развлечения', 'ДатаПул', ''),
    ('items', 'Боевая перчатка', 'Одежда', 'ДатаПул', ''),
    ('items', 'Фирменный комбенизон/Униформа', 'Одежда', 'ДатаПул', 'Фирменный комбинезон / Униформа'),
    ('items', 'Внешний экзоскелет (Сигма)', 'Силовая броня', 'ДатаПул', ''),
    ('items', 'Внешний экзоскелет (Бета)', 'Силовая броня', 'ДатаПул', ''),
    ('items', 'Внешний экзоскелет Ω (ОМЕГА)', 'Силовая броня', 'ДатаПул', ''),
    ('items', 'Воздушный Колодец 50 от Everest VentureWare', 'Инструменты', 'ДатаПул', ''),
    ('items', 'Гидравлическая Подкладка Húsafell', 'Одежда', 'ДатаПул', ''),
    ('items', 'Гарнитура Zetatech Tank Commander', 'Связь и электроника', 'ДатаПул', ''),
    ('items', 'Дальномер MagViewver от Optitech', 'Инструменты', 'ДатаПул', 'Дальномер MagViewer от Optitech'),
    ('items', 'Диктофон', 'Связь и электроника', 'ДатаПул', ''),
    ('items', 'Душ В Банке', 'Еда и быт', 'ДатаПул', ''),
    ('items', 'Духи "Нимфа"', 'Одежда', 'ДатаПул', ''),
    ('items', 'Двухкопонентный состав', 'Инструменты', 'ДатаПул', 'Двухкомпонентный состав'),
    ('items', 'Жилище в одно касание от Everest VentureWare', 'Жильё и услуги', 'ДатаПул', ''),
    ('items', 'Зетатех Порта-Принтер', 'Инструменты', 'ДатаПул', ''),
    ('items', 'Зонт', 'Одежда', 'ДатаПул', ''),
    ('items', 'Зонт тактический от Милитех', 'Одежда', 'ДатаПул', ''),
    ('items', 'Изолента', 'Инструменты', 'ДатаПул', ''),
    ('items', 'Карманный усилитель', 'Связь и электроника', 'ДатаПул', ''),
    ('items', 'Колонки Minimag от Teletronics', 'Развлечения', 'ДатаПул', ''),
    ('items', 'КомпактЩит от SkidRow', 'Инструменты', 'ДатаПул', ''),
    ('items', 'Компьютер', 'Связь и электроника', 'ДатаПул', ''),
    ('items', 'КиберКамера EX-1', 'Связь и электроника', 'ДатаПул', ''),
    ('items', 'КиберСканер', 'Инструменты', 'ДатаПул', ''),
    ('items', 'КиберПроводник Zetatech', 'Связь и электроника', 'ДатаПул', ''),
    ('items', 'КиллСтром Колонка “Тифоид”', 'Развлечения', 'ДатаПул', ''),
    ('items', 'КиллСтром Микрофон Банши', 'Развлечения', 'ДатаПул', ''),
    ('items', 'КиллСтром Усилитель Звукового Удара', 'Развлечения', 'ДатаПул', ''),
    ('items', 'Лазерный Микрофон', 'Инструменты', 'ДатаПул', ''),
    ('items', 'Линза с Сетчаткой', 'Инструменты', 'ДатаПул', ''),
    ('items', 'Маска-противогаз', 'Одежда', 'ДатаПул', ''),
    ('items', 'Маскировочный рукав', 'Инструменты', 'ДатаПул', ''),
    ('items', 'Мистер Бисквит Мультипищевой комбайн', 'Еда и быт', 'ДатаПул', ''),
    ('items', 'Мастер Напитков 3000', 'Еда и быт', 'ДатаПул', ''),
    ('items', 'Мастер Напитков 5000', 'Еда и быт', 'ДатаПул', ''),
    ('items', 'Милитех М97 Костюм-Призрак', 'Одежда', 'ДатаПул', ''),
    ('items', 'Набор взломщика', 'Инструменты', 'ДатаПул', ''),
    ('items', 'Набор инструментов “Мастер-Механик”', 'Инструменты', 'ДатаПул', ''),
    ('items', 'Набор личной гигиены', 'Еда и быт', 'ДатаПул', ''),
    ('items', 'Параболический микрофон', 'Инструменты', 'ДатаПул', ''),
    ('items', 'Пачка киббла', 'Еда и быт', 'ДатаПул', ''),
    ('items', 'Пищевая палочка', 'Еда и быт', 'ДатаПул', ''),
    ('items', 'Пистолет-крюк', 'Инструменты', 'ДатаПул', ''),
    ('items', 'Переходная гильза “Пуля в жакан”', 'Оружие и боеприпасы', 'ДатаПул', ''),
    ('items', 'Перчатка с Отпечатком', 'Одежда', 'ДатаПул', ''),
    ('items', 'Петрохем Нитро Ультра9', 'Транспорт', 'ДатаПул', ''),
    ('items', 'Подкладка для куртки “Водостойкая”', 'Одежда', 'ДатаПул', ''),
    ('items', 'Подкладка для куртки “Охлаждающая”', 'Одежда', 'ДатаПул', ''),
    ('items', 'Подкладка для куртки “Тёплая”', 'Одежда', 'ДатаПул', ''),
    ('items', 'Профессиональный маскировочный набор', 'Инструменты', 'ДатаПул', ''),
    ('items', 'Радар-детектор', 'Инструменты', 'ДатаПул', ''),
    ('items', 'Радио сканер/Муз. проигрыватель', 'Связь и электроника', 'ДатаПул', ''),
    ('items', 'Светящаяся краска', 'Инструменты', 'ДатаПул', ''),
    ('items', 'СвобоДоступные Ножны', 'Оружие и боеприпасы', 'ДатаПул', ''),
    ('items', 'Сигнальная ракета', 'Оружие и боеприпасы', 'ДатаПул', ''),
    ('items', 'Смарт-Палочки от DPI', 'Инструменты', 'ДатаПул', ''),
    ('items', 'Смарт-Перчатка Xtra-DEX от Dynalar', 'Одежда', 'ДатаПул', ''),
    ('items', 'Смарт-Перчатка CyberDude', 'Одежда', 'ДатаПул', ''),
    ('items', 'СовОил Лубрикант', 'Инструменты', 'ДатаПул', ''),
    ('items', 'Сумка Техника', 'Инструменты', 'ДатаПул', ''),
    ('items', 'Трити-Физз', 'Еда и быт', 'ДатаПул', ''),
    ('items', 'Техсканер', 'Инструменты', 'ДатаПул', ''),
    ('items', 'Трекер (Маячок)', 'Связь и электроника', 'ДатаПул', ''),
    ('items', 'Уличный Кейс', 'Инструменты', 'ДатаПул', ''),
    ('items', 'Умная Линза', 'Инструменты', 'ДатаПул', ''),
    ('items', 'Умные очки', 'Инструменты', 'ДатаПул', ''),
    ('items', 'Умные уши', 'Инструменты', 'ДатаПул', ''),
    ('items', 'УниверсальныйАкваланг от Hydrosubsidium', 'Инструменты', 'ДатаПул',
     'Универсальный Акваланг от Hydrosubsidium'),
    ('items', 'Флакон биотоксина', 'Оружие и боеприпасы', 'ДатаПул', ''),
    ('items', 'Флакон с ядом', 'Оружие и боеприпасы', 'ДатаПул', ''),
    ('items', 'Химический анализатор', 'Инструменты', 'ДатаПул', ''),
    ('items', 'Химический источник света (ХИС, глоустик)', 'Инструменты', 'ДатаПул', ''),
    ('items', 'Чехол для Одежды “Корпорат Дживс”', 'Одежда', 'ДатаПул', ''),
    ('items', 'ЩепкоХранилище', 'Связь и электроника', 'ДатаПул', ''),
    ('items', 'Электрогитара от Лазерный Свет', 'Развлечения', 'ДатаПул', ''),
    ('items', 'Электрогитара KillStrom Power Chord', 'Развлечения', 'ДатаПул', ''),
    ('items', 'Segotari RUSH (Б/У)', 'Развлечения', 'ДатаПул', ''),
    ('items', 'Segotari RUSH Revolution', 'Развлечения', 'ДатаПул', ''),
    ('items', 'Segotari VRIcade Cabinet', 'Развлечения', 'ДатаПул', ''),
    ('items', 'Игра для Segotari RUSH Revolution', 'Развлечения', 'ДатаПул', ''),
    ('items', 'Игра для Segotari Agent', 'Развлечения', 'ДатаПул', ''),
    ('items', 'Щепка для Segotari Mindgames', 'Развлечения', 'ДатаПул', ''),
    ('items', 'Игра Segotari RUSH (Б/У)', 'Развлечения', 'ДатаПул', ''),
    ('items', 'Мультигиппо', 'Транспорт', 'ДатаПул', ''),
    ('items', 'Порт для авторизации', 'Связь и электроника', 'ДатаПул', ''),
    ('items', 'Тепловая приманка', 'Инструменты', 'ДатаПул', ''),
    # расходники (таблица 1)
    ('items1', 'Батарейка', 'Инструменты', 'ДатаПул', ''),
    ('items1', 'Баллон воздуха', 'Инструменты', 'ДатаПул', ''),
    ('items1', 'Картриджи “Мастер Напитков”', 'Еда и быт', 'ДатаПул', ''),
    ('items1', 'Сеть', 'Оружие и боеприпасы', 'ДатаПул', ''),
    ('items1', 'Заряд крионасоса', 'Медицина', 'ДатаПул', ''),
    ('items1', 'Дополнительный жучок для трекера', 'Связь и электроника', 'ДатаПул', ''),
    ('items1', 'Аварийный выключатель C9', 'Инструменты', 'ДатаПул', ''),
    # агенты (аксессуары)
    ('agents', 'Взломщик', 'Агент и софт', 'Всё об агентах', ''),
    ('agents', 'Свисток для Обработки', 'Агент и софт', 'Всё об агентах', ''),
    ('agents', 'Wyzard Technologies Merlyn', 'Агент и софт', 'Всё об агентах', ''),
    ('agents', 'Zetatech Grade A-Plus', 'Агент и софт', 'Всё об агентах', ''),
    ('agents', 'Zetatech Grade A', 'Агент и софт', 'Всё об агентах', ''),
    ('agents', 'Segotari Double Agent', 'Агент и софт', 'Всё об агентах', ''),
]

SOFT_NAMES = [
    'Z-Почта', 'Garden', 'Вавилон Чат', 'Сразу Спроси Сашу', 'КиньМне!', 'Шевелись, Плотва!',
    'HusTool', 'Trauma Team МедСкан', 'Цифровой Гладиатор', 'Сияющий Палец', 'Охранный Бокс',
    'Elflines Online Эльф-трекер', 'Вдохновитель', 'Больше САИИ', 'Городская База Данных', '4Тифай',
    'NCPD База Преступлений', 'Сканер отпечатков рук', 'Сканер сетчатки глаза', 'CBK',
]


def availability_of(price):
    m = re.search(r'\(([^)]+)\)', price)
    if not m:
        return ''
    tier = norm(m.group(1))
    table = {
        'премиум': 'Премиум', 'ценное': 'Ценное', 'обычное': 'Обычное', 'дешёвка': 'Дешёвка',
        'дешевка': 'Дешёвка', 'дешево': 'Дешёвка', 'дешёво': 'Дешёвка', 'дорогое': 'Дорогое',
        'дорого': 'Дорогое', 'о. дорогое': 'Очень дорогое', 'о.дорогое': 'Очень дорогое',
        'очень дорогое': 'Очень дорогое', 'роскошь': 'Роскошь', 'супер роскошь': 'Супер роскошь',
        'недешево': 'Дорогое', 'недёшево': 'Дорогое',
        'дорогой': 'Дорогое', 'очень дорого': 'Очень дорогое', 'дёшево': 'Дешёвка',
        'бесплатно': 'Бесплатно',
    }
    return table.get(tier, m.group(1).strip().capitalize())


def row_fields(row):
    return [str(x) for x in row]


def build_equipment(tables):
    out = []
    unmatched = []
    report = []

    def add(name, category, source, price, desc):
        price_c = clean_price(price)
        rec = [name, category, source, price_c, availability_of(price_c),
               strip_source(re.sub(r'\s*\n\s*', ' ', str(desc)).strip())]
        out.append(rec)

    for sec_key, nm, cat, src, nm_override in EQ:
        secs = []
        if sec_key == 'items':
            secs = [tables['items'][0], tables['items'][1]]
        elif sec_key == 'items1':
            secs = [tables['items'][1]]
        elif sec_key == 'agents':
            secs = list(tables['agents'])
        elif sec_key == 'soft':
            secs = list(tables['soft'])
        found = None
        for sec in secs:
            for row in sec.get('rows', []):
                if norm(row[0]) == norm(nm):
                    found = row
                    break
            if found:
                break
        if not found:
            unmatched.append('[%s] %s' % (sec_key, nm))
            continue
        fields = row_fields(found)
        if sec_key == 'agents':
            # [Наименование, Описание, Цена, ...]
            desc = fields[1] if len(fields) > 1 else ''
            price = fields[2] if len(fields) > 2 else ''
        else:
            desc = fields[1] if len(fields) > 1 else ''
            price = fields[2] if len(fields) > 2 else ''
        name = nm_override or fix_name(fields[0])
        report.append('%s | %s | %s' % (name, price, desc[:60]))
        add(name, cat, src, price, desc)

    # софт агента
    for nm in SOFT_NAMES:
        found = None
        for sec in tables['soft']:
            for row in sec.get('rows', []):
                if norm(row[0]) == norm(nm):
                    found = row
                    break
            if found:
                break
        if not found:
            unmatched.append('[soft] %s' % nm)
            continue
        fields = row_fields(found)
        desc = fields[2] if len(fields) > 2 else (fields[1] if len(fields) > 1 else '')
        price = fields[3] if len(fields) > 3 else (fields[2] if len(fields) > 2 else '')
        name = fix_name(fields[0])
        report.append('%s | %s | %s' % (name, price, desc[:60]))
        add(name, 'Агент и софт', 'Всё об агентах', price, desc)

    # жидкости Плачущего Разбойника (таблица 17)
    for nm in ['Кислота Арасаки', 'Огонь Арасаки', 'Соль на Рану Арасаки']:
        try:
            row = find_row(tables['weapons'][17], nm)
        except KeyError:
            unmatched.append('[weapons#17] %s' % nm)
            continue
        name = fix_name(row[0])
        note = re.sub(r'\s*\n\s*', ' ', str(row[6])).strip()
        note = re.sub(r'Источник:.*$', '', note).strip()
        price = clean_price(row[7])
        report.append('%s | %s | %s' % (name, price, note[:60]))
        add(name, 'Оружие и боеприпасы', 'Чёрный хром', price, note)

    # Мародерский экзоскелет (из таблицы ACPA)
    add('Мародерский экзоскелет', 'Силовая броня', 'ДатаПул', '1,000eb (О. дорогое)',
        'Тяжёлый экзоскелет кустарной сборки: требуется ТЕЛО 10, даёт 14 ПЗ, без бонусов и штрафов.')

    return out, unmatched, report


# ---------------------------------------------------------------- корпорации

CORPS = [
    ['Техтроника', 58, 'Оружие, техника, советский экспорт', 'Оружейная корпорация', 'ДатаПул',
     'Советский оружейный и технический гигант, чьи изделия встречаются от Варшавы до Найт-Сити. '
     'Техтроника делает крепкие, простые и жестокие вещи для рынков, где важнее надёжность, чем изящество.',
     'Используй Техтронику как источник нео-советского оружия, тяжёлых винтовок, техники, серых поставок '
     'и персонажей с восточноевропейскими связями.'],
    ['Баджет Армс', 40, 'Дешёвое оружие, массовый рынок', 'Оружейная компания', 'ДатаПул',
     'Производитель самого дешёвого и грубого оружия на рынке. Баджет Армс продаёт пушки как бытовой товар: '
     'дёшево, много, без вопросов к качеству и последствиям.',
     'Хорошо работает для уличных банд, вендинговых автоматов с оружием, криминальных распродаж и сцен, '
     'где важна не репутация, а цена.'],
    ['Нокота Мануфэкчуринг', 38, 'Огнестрельное оружие, дробовики', 'Оружейная компания', 'ДатаПул',
     'Оружейный бренд расширенных каталогов, известный практичными дробовиками и моделями для дороги. '
     'Оружие Нокоты ценят за простоту и предсказуемость.',
     'Подходит для кочевников, охотников, дорожных схваток, складов и поставок, где нужна рабочая пушка '
     'без корпоративной легенды.'],
    ['Ростович', 44, 'Экзотическое оружие, клинки, Восточная Европа', 'Оружейная компания', 'ДатаПул',
     'Производитель экзотического и агрессивного оружия с восточноевропейским характером: от кливеров '
     'до тяжёлых уличных моделей. Имя Ростович звучит как угроза сама по себе.',
     'Используй для редких заказов, арен, коллекционеров холодного оружия, восточноевропейских поставок '
     'и вещей, которые персонажи узнают с первого взгляда.'],
    ['Дарра Политехник', 36, 'Экзотическое оружие, кочевники', 'Оружейная компания', 'ДатаПул',
     'Технический производитель из пустошей, делающий необычное оружие для тех, кто живёт вне городов. '
     'Изделия Дарра Политехник сочетают инженерную смекалку и грубую практичность.',
     'Подходит для кочевничьих мастерских, пустошей, самодельных модификаций и редких моделей, которые '
     'не найти в городском магазине.'],
    ['Арчер', 34, 'Транспорт, доступные автомобили', 'Производитель транспорта', 'ДатаПул',
     'Производитель доступных и распространённых автомобилей. Машины Арчера — это транспорт для тех, '
     'кому нужно ехать, а не красоваться.',
     'Используй для уличных погонь, угонов, такси, парковок и сцен, где важен не бренд, а лошадиные силы '
     'под капотом.'],
    ['Кавказ', 36, 'Транспорт, грузовики, тяжёлая техника', 'Производитель транспорта', 'ДатаПул',
     'Производитель грузовиков и тяжёлой техники, знакомый каждому, кто выезжал за пределы Найт-Сити. '
     'Машины Кавказа переживают дороги, погоду и водителей.',
     'Хорош для кочевничьих караванов, грузов, конвоев, пустошей и транспорта, который должен доехать '
     'во что бы то ни стало.'],
    ['Квадра', 40, 'Транспорт, спортивные автомобили', 'Производитель транспорта', 'ДатаПул',
     'Производитель спортивных и стильных автомобилей, чьё имя стало синонимом скорости в Найт-Сити. '
     'Квадра — выбор тех, кто хочет, чтобы их замечали.',
     'Подходит для корпоративных гонок, показных выездов, угонов элитных машин и сцен, где скорость — '
     'это статус.'],
    ['Мидзутани', 32, 'Транспорт, мотоциклы', 'Производитель транспорта', 'ДатаПул',
     'Производитель мотоциклов и лёгкого транспорта, ценимый за манёвренность и характер. Багай-гейны '
     'и уличные гонщики любят Мидзутани за скорость в узких кварталах.',
     'Используй для уличных гонок, погонь по ночным улицам, банд и транспорта, который важнее владельца.'],
    ['Тортон', 34, 'Транспорт, грузовики, фургоны', 'Производитель транспорта', 'ДатаПул',
     'Производитель грузовиков, фургонов и рабочего транспорта. Машины Тортона — это инструменты, '
     'которые делают работу, а не автомобили для души.',
     'Хорош для грузоперевозок, складов, криминальной логистики и транспорта, который не должен '
     'привлекать внимания.'],
    ['Яйба', 38, 'Транспорт, мотоциклы, спорт', 'Производитель транспорта', 'ДатаПул',
     'Производитель агрессивных спортивных мотоциклов с японским характером и репутацией. Яйба — это '
     'скорость, шум и опасность в одном корпусе.',
     'Подходит для гонщиков, бандбастеров, арен и сцен, где мотоцикл — продолжение характера персонажа.'],
    ['Абидос', 30, 'Еда, массовый рынок', 'Пищевая корпорация', 'ДатаПул',
     'Пищевая корпорация, чья продукция заполняет полки дешёвых магазинов и автоматы с едой. Абидос — '
     'это синт-еда, киббл и бесконечные вариации одного вкуса.',
     'Используй для сцен о бедности, уличной еде, поставках в автоматы, рекламных кампаний и корпораций, '
     'которые наживаются на самом необходимом.'],
    ['Ни-Кола', 28, 'Напитки, стимуляторы', 'Потребительская корпорация', 'ДатаПул',
     'Производитель напитков и стимуляторов, знакомый каждому жителю Найт-Сити. Ни-Кола — это вкус '
     'детства, бодрость на смене и вечный рекламный логотип на каждом углу.',
     'Хороша для клубных сцен, энергетиков, зависимости, рекламы и корпоративных вечеринок с сомнительным '
     'меню.'],
    ['Циррус-Кола', 30, 'Напитки, массовый рынок', 'Потребительская корпорация', 'ДатаПул',
     'Крупный производитель напитков и один из самых узнаваемых брендов Найт-Сити. Циррус-Кола — это '
     'газировка, которая пережила войны, эпидемии и падения корпораций.',
     'Подходит для сюжетов о рекламе, франшизах, воде и сахаре как оружии, а также для символа '
     'корпоративного присутствия повсюду.'],
    ['Зетатех', 46, 'Компьютеры, кибердеки, портативные устройства', 'Технологическая компания', 'ДатаПул',
     'Технологическая корпорация, известная портативными компьютерами, кибердеками и устройствами для '
     'нетраннеров. Зетатех делает инструменты, от которых зависит Сеть.',
     'Используй для историй о кибердеках, утечках данных, нетраннерских рынках, бэкдорах и технологиях, '
     'которые слишком хороши, чтобы быть безопасными.'],
    ['Майкротех', 48, 'Компьютеры, кибердеки, робототехника', 'Технологическая компания', 'ДатаПул',
     'Один из старейших и уважаемых производителей компьютерной техники, кибердек и робототехники. '
     'Майкротех — это качество, которое помнят ещё до Красного времени.',
     'Хорош для сюжетов о старых системах, наследии, промышленной автоматизации, военных подрядах и '
     'технологиях, которые пережили своих создателей.'],
    ['WNS Дабл-ю-эн-эс', 44, 'Медиа, новости, вещание', 'Медиакорпорация', 'ДатаПул',
     'Медиаконцерн, который держит в руках новости, развлечения и общественное мнение. WNS решает, '
     'что увидит Найт-Сити — и что он никогда не узнает.',
     'Используй для сюжетов о журналистике, цензуре, медиавойнах, рейтингах и информации как оружии.'],
    ['Корпорация «Найт»', 52, 'Инфраструктура, правление, услуги', 'Корпорация инфраструктуры', 'ДатаПул',
     'Корпорация, связанная с самим городом: инфраструктура, услуги, контракты и тени власти над '
     'Найт-Сити. Её имя — синоним городской администрации, которая больше бизнес, чем власть.',
     'Хороша для сюжетов о контрактах, бюрократии, городских службах, коррупции и том, кто на самом деле '
     'управляет улицами.'],
    ['Деламейн', 38, 'Такси, транспортные ИИ, услуги', 'Сервисная корпорация', 'ДатаПул',
     'Сервис автоматических такси и транспортных ИИ, ставший частью повседневной жизни города. '
     'Деламейн — это голос из динамика, который везёт тебя туда, куда ты сказал.',
     'Используй для сюжетов об искусственном интеллекте, пропавших пассажирах, странных маршрутах и '
     'услугах, которые слишком внимательно слушают.'],
    ['Меррилл, Асукага и Финч', 50, 'Финансы, банки, страхование', 'Финансовая корпорация', 'ДатаПул',
     'Финансовый гигант, стоящий за банками, страховками и корпоративными сделками. Деньги мира '
     'Cyberpunk проходят через руки вроде Меррилл, Асукага и Финч.',
     'Подходит для сюжетов о долгах, кражах данных, биржевых манипуляциях, страховых аферах и власти, '
     'которая считает всё в евробаксах.'],
    ['Hammered Industries', 42, 'Химикаты, анализаторы, оборудование', 'Химическая корпорация', 'ДатаПул',
     'Производитель химикатов и специализированного оборудования: анализаторы, составы, всё то, что '
     'проверяет и меняет реальность на молекулярном уровне.',
     'Используй для лабораторий, тестов, отравлений, контроля веществ и сцен, где один анализ решает '
     'судьбу персонажа.'],
]


def build_corps():
    out = []
    for c in CORPS:
        rec = [c[0], int(c[1]), c[2], c[3], c[4], c[5], c[6]]
        out.append(rec)
    return out


# ---------------------------------------------------------------- боеприпасы

AMMO = {
    'B.jT': ['С ядом', 'Дешевые боеприпасы', 'Мелкокалиберный боеприпас', 'Проникающие', 'Разрывные',
             'Высокоточные', 'Высокоскоростные', 'Гиперэкспансивные', 'Пули с полым наконечником',
             'Трассирующие', 'Улучшенный умный боеприпас'],
    'B.VC': ['С ядом', 'Дешевые боеприпасы', 'Проникающие', 'Разрывные', 'Высокоточные',
             'Гиперэкспансивные', 'Пули с полым наконечником', 'Улучшенный умный боеприпас'],
    'B.Za': ['Дешевые боеприпасы', 'Проникающие', 'Разрывные', 'Высокоточные', 'Гиперэкспансивные',
             'Зазубренные стрелы', 'Стрела-Аэрогипо', 'Улучшенный умный боеприпас'],
    'B.Sx': ['Аэрозольные боеприпасы', 'Улучшенный умный боеприпас'],
    'B.VZ': ['Граната Арахнид', 'ГанМарт Дверной Взломщик', 'Микро-Бомба Убивающая Щепка 100',
             'КТех Охранная граната', 'Граната с CO2', 'Молотов', 'Граната Торнадо Сюрикенов',
             'Водородный Микро-Компрессор', 'Взрывной АДаптер', 'Детонационная Жидкость TR-4',
             'Хроматическая Рейв-Граната Hello Cutie', 'С9', 'Мини-заряд C9', 'Аэрозольные боеприпасы',
             'Улучшенный умный боеприпас'],
}


def main():
    tables = {
        'weapons': load('equipment_weapons'),
        'armor': load('equipment_armor'),
        'items': load('equipment_items'),
        'soft': load('equipment_soft'),
        'agents': load('equipment_agents_accessories'),
        'implants': load('chrome_implants'),
        'exotic': load('chrome_exotic'),
        'borgs': load('chrome_borgs'),
        'pkt_implants': load('chrome_pkt_implants'),
        'pkt_packs': load('chrome_pkt_packs'),
    }

    weapons, w_un = build_weapons(tables['weapons'])
    armor, a_un = build_armor(tables['armor'])
    implants, i_un = build_implants(tables)
    equipment, e_un, e_rep = build_equipment(tables)
    corps = build_corps()

    result = {
        'weapons': weapons,
        'armor': armor,
        'implants': implants,
        'equipment': equipment,
        'corps': corps,
        'ammo': AMMO,
    }
    out_path = os.path.join(OUT_DIR, 'dp_additions.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=1)

    # --- отчёт
    rep = []
    rep.append('weapons: %d' % len(weapons))
    rep.append('armor: %d' % len(armor))
    rep.append('implants: %d' % len(implants))
    rep.append('equipment: %d' % len(equipment))
    rep.append('corps: %d' % len(corps))
    rep.append('')
    rep.append('=== НЕ НАЙДЕНЫ (%d) ===' % (len(w_un) + len(a_un) + len(i_un) + len(e_un)))
    rep.extend(w_un)
    rep.extend(a_un)
    rep.extend(i_un)
    rep.extend(e_un)
    rep.append('')
    rep.append('=== источники оружия ===')
    for w in weapons:
        rep.append('%-45s | %s' % (w[0][:44], w[2]))
    rep.append('')
    rep.append('=== источники имплантов ===')
    for i in implants:
        rep.append('%-45s | %s | %s' % (i[0][:44], i[3], i[2]))
    rep.append('')
    rep.append('=== снаряжение (проверка) ===')
    rep.extend(e_rep)
    rep.append('')
    rep.append('=== таблица 21: имена ===')
    for row in tables['weapons'][21].get('rows', []):
        rep.append('  %s' % row[0])
    rep.append('=== таблица 24: имена ===')
    for row in tables['weapons'][24].get('rows', []):
        rep.append('  %s' % row[0])
    rep.append('=== таблица 20: имена ===')
    for row in tables['weapons'][20].get('rows', []):
        rep.append('  %s' % row[0])

    rep_path = os.path.join(TMP, 'additions_report.txt')
    with open(rep_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(rep))
    print('-> %s' % out_path)
    print('-> %s' % rep_path)
    print('weapons %d | armor %d | implants %d | equipment %d | corps %d' % (
        len(weapons), len(armor), len(implants), len(equipment), len(corps)))

    if w_un or a_un or i_un or e_un:
        print('WARNING: unmatched %d' % (len(w_un) + len(a_un) + len(i_un) + len(e_un)))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
