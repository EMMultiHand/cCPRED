# -*- coding: utf-8 -*-
"""Перекраска «своих» бренд-картинок Data Pool: красные тона -> медные.

Затрагивает только пиксели, у которых hue попадает в красный диапазон
(315°..360° и 0°..30°) и насыщенность достаточная, чтобы не трогать серые,
чёрные и бежевые участки. Светлота (V) и насыщенность (S) сохраняются.

Файлы (относительно data-pool/):
  images/data-pool_header.png  — баннер шапки на всех страницах
  images/logo.png              — логотип «DATAPOOL» в сайдбаре
  images/favicon.png           — иконка вкладки/фавикон

Логотипы сторонних брендов (R. Talsorian Games, CD Projekt RED) и
художественные иллюстрации в images/content/** НЕ трогаются.
"""
import os
import sys

from PIL import Image, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DP = os.path.join(ROOT, 'data-pool')

FILES = [
    'images/data-pool_header.png',
    'images/logo.png',
    'images/favicon.png',
]

# Красный диапазон (градусы) и точка перехода в медь.
BAND_START = 315.0   # начало захвата (розово-красный)
BAND_END = 30.0      # конец захвата (оранжево-красный)
TARGET_START = 21.0  # куда уходит BAND_START
SLOPE = 0.40         # сдвиг градусов на градус внутри диапазона
SAT_MIN = 46         # минимальная насыщенность (0..255), ниже — не трогаем


def build_lut():
    lut = []
    for hv in range(256):
        deg = hv * 360.0 / 255.0
        if deg >= BAND_START or deg <= BAND_END:
            pos = (deg - BAND_START) % 360.0
            newdeg = TARGET_START + pos * SLOPE
            lut.append(min(255, max(0, int(round(newdeg * 255.0 / 360.0)))))
        else:
            lut.append(hv)
    return lut


def build_mask(h, s):
    hue_sel = h.point(
        lambda hv: 255 if (hv * 360.0 / 255.0 >= BAND_START or hv * 360.0 / 255.0 <= BAND_END) else 0
    )
    sat_sel = s.point(lambda sv: 255 if sv >= SAT_MIN else 0)
    return ImageChops.multiply(hue_sel, sat_sel)


def recolor(path):
    im = Image.open(path)
    has_alpha = im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info)
    rgb = im.convert('RGB')
    alpha = im.convert('RGBA').getchannel('A') if has_alpha else None

    hsv = rgb.convert('HSV')
    h, s, v = hsv.split()
    lut = build_lut()
    h2 = h.point(lut)
    new_rgb = Image.merge('HSV', (h2, s, v)).convert('RGB')
    mask = build_mask(h, s)
    out = Image.composite(new_rgb, rgb, mask)
    if alpha is not None:
        out = out.convert('RGBA')
        out.putalpha(alpha)
    out.save(path, optimize=True)
    return out.size


def main():
    for rel in FILES:
        p = os.path.join(DP, rel.replace('/', os.sep))
        if not os.path.exists(p):
            print('skip (нет файла): %s' % rel)
            continue
        size = recolor(p)
        print('recolored: %-28s %sx%s' % (rel, size[0], size[1]))
    print('done.')


if __name__ == '__main__':
    sys.exit(main())
