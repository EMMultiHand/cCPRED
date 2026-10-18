"""Re-theme the mirrored data-pool site to a dark-brown palette.

- recolours colour literals in .css files and in HTML <style> blocks / style="" attrs,
- rewrites the unpkg lunr script tags to the locally vendored copies,
- leaves JS logic untouched (the site keeps colours in CSS).
"""
import os, re, sys, colorsys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DP = os.path.join(ROOT, 'data-pool')

# explicit mapping of the site's known palette (lower-case hex without '#')
KNOWN = {
    # neutrals -> warm brown-greys
    '000': '140D07', '000000': '140D07',
    '0d0d0d': '150E08', '0a0a0a': '130C06', '121212': '190F08',
    '1a1a1a': '1E140C', '1b1b1b': '1F150D', '1c1c1c': '20160E',
    '1e1e1e': '211710', '1f1f1f': '221810', '202020': '231910',
    '212121': '241910', '222222': '251A11', '232323': '261B12',
    '242424': '271C12', '252525': '281D13', '262626': '291E14',
    '282828': '2A1E13', '2a2a2a': '2B1D12', '2b2b2b': '2C1E13',
    '2c2c2c': '2D1F14', '2e2e2e': '2F2016', '303030': '312117',
    '333333': '342317', '343434': '352418', '3a3a3a': '3B2A1C',
    '3b3b3b': '3C2B1D', '404040': '412F1F', '444444': '453222',
    '4a4a4a': '4B3726', '4d4d4d': '4E3928', '505050': '513B29',
    '555': '55=0',  # placeholder, will be ignored below
    '555555': '553F2B', '5a5a5a': '5A442E', '666': '6A5138',
    '666666': '6A5138', '777': '8A765F', '777777': '8A765F',
    '888': '9A8770', '888888': '9A8770', '999': 'A28A6D',
    '999999': 'A28A6D', 'aaa': 'B09A80', 'aaaaaa': 'B09A80',
    'bbb': 'BCA68B', 'bbbbbb': 'BCA68B', 'ccc': 'CBB79C',
    'cccccc': 'CBB79C', 'ddd': 'DAC7AB', 'dddddd': 'DAC7AB',
    'eee': 'E7D8C0', 'eeeeee': 'E7D8C0', 'efefef': 'E8D9C1',
    'f0f0f0': 'EFE3D0', 'f2f2f2': 'F0E4D1', 'f5f5f5': 'F2E7D5',
    'fafafa': 'F6ECDB', 'fff': 'FBF3E6', 'ffffff': 'FBF3E6',
    # accent red -> amber copper
    'ff0040': 'CE8B45', 'e6003a': 'B97E3E', 'cc0033': 'A66F37',
    'e00038': 'B57C3D', 'f0003c': 'C08341', 'd90433': 'AA7238',
    'ff1a55': 'D89651', 'ff3366': 'DD9E5C', 'ff6b91': 'E4AF74',
    # blues/cyans occasionally used -> copper/bronze
    '00bcd4': 'CE8B45', '2196f3': 'C08749', '1976d2': 'B27B41',
    '00aaff': 'C08749', '00d4ff': 'CE8B45', '0e8fa3': 'C68B49',
    # greens -> olive brown
    '4caf50': '8F8F4A', '00c853': '96934C', '2e7d32': '7C7A40',
    '00ff00': '9AA050', '0f0': '9AA050',
    # yellows/oranges -> amber
    'ffcc00': 'D3A45A', 'ffd200': 'D6A85C', 'ff9900': 'CE8B45',
    'ffaa00': 'D19A55', 'ffc107': 'D3A45A',
    # purples -> taupe
    '9c27b0': '9A7B57', '7b1fa2': '8A6E4E',
}
KNOWN.pop('555', None)

COLOR_RE = re.compile(r'#[0-9a-fA-F]{3,8}\b|\brgba?\(\s*[0-9]+\s*,\s*[0-9]+\s*,\s*[0-9]+\s*(?:,\s*[0-9.]+\s*)?\)')


def brownize(rgb):
    r, g, b = [c / 255 for c in rgb]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    if s < 0.08:
        # warm neutral
        out = (min(255, r * 255 * 1.06 + 6), g * 255 * 0.97, b * 255 * 0.86)
    else:
        target = 30 / 360
        dh = ((target - h + 0.5) % 1) - 0.5
        nh = (h + dh * 0.9) % 1
        ns = min(s, 0.5) * 0.9
        nl = min(0.97, l * 1.02)
        nr, ng, nb = colorsys.hls_to_rgb(nh, nl, ns)
        out = (nr * 255, ng * 255, nb * 255)
    return tuple(max(0, min(255, round(c))) for c in out)


def parse_rgb(s):
    m = re.match(r'\brgba?\(\s*([0-9]+)\s*,\s*([0-9]+)\s*,\s*([0-9]+)\s*(,\s*[0-9.]+\s*)?\)', s)
    r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return r, g, b, (m.group(4) or '').strip()


def map_hex(hx):
    key = hx.lower()
    alpha = ''
    if len(key) == 8:
        alpha = key[6:8].upper()
        key = key[:6]
    if len(key) == 4:
        alpha = key[3].upper() * 2
        key = key[:3]
    m = KNOWN.get(key)
    if m:
        return '#' + m.upper() + alpha
    # generic
    if len(key) == 3:
        rgb = tuple(int(c * 2, 16) for c in key)
    elif len(key) == 6:
        rgb = (int(key[0:2], 16), int(key[2:4], 16), int(key[4:6], 16))
    else:
        return None
    nr, ng, nb = brownize(rgb)
    return '#%02X%02X%02X%s' % (nr, ng, nb, alpha)


def recolor_text(text, stats):
    def repl(m):
        tok = m.group(0)
        if tok.startswith('#'):
            new = map_hex(tok[1:])
            if new is None:
                return tok
            stats[tok.lower()] = new
            return new
        r, g, b, alpha = parse_rgb(tok)
        nr, ng, nb = brownize((r, g, b))
        new = 'rgba(%d, %d, %d%s)' % (nr, ng, nb, (', ' + alpha.lstrip(', ')) if alpha else '')
        if alpha:
            new = 'rgba(%d, %d, %d, %s)' % (nr, ng, nb, alpha.lstrip(', '))
        else:
            new = 'rgb(%d, %d, %d)' % (nr, ng, nb)
        stats[tok.lower()] = new
        return new

    return COLOR_RE.sub(repl, text)


STYLE_BLOCK_RE = re.compile(r'(<style[^>]*>)(.*?)(</style>)', re.S | re.I)
STYLE_ATTR_RE = re.compile(r'(style\s*=\s*")([^"]*)(")', re.I)
META_THEME_RE = re.compile(r'(<meta\s+name="theme-color"\s+content=")([^"]*)(")', re.I)
UNPKG_RE = re.compile(r'https://unpkg\.com/(lunr[^"\']*)')


def patch_html(path, stats):
    s = open(path, encoding='utf-8').read()
    orig = s
    s = STYLE_BLOCK_RE.sub(lambda m: m.group(1) + recolor_text(m.group(2), stats) + m.group(3), s)
    s = STYLE_ATTR_RE.sub(lambda m: m.group(1) + recolor_text(m.group(2), stats) + m.group(3), s)

    def meta(m):
        c = m.group(2).strip()
        if c.startswith('#'):
            new = map_hex(c[1:])
            return m.group(1) + (new or c) + m.group(3)
        return m.group(0)

    s = META_THEME_RE.sub(meta, s)

    def unpkg(m):
        rest = m.group(1)
        name = rest.split('/')[-1]
        if not name.endswith('.js'):
            name = rest
        return '/data-pool/vendor/lunr/' + name

    s = UNPKG_RE.sub(unpkg, s)

    if s != orig:
        open(path, 'w', encoding='utf-8', newline='').write(s)
        return True
    return False


def patch_css(path, stats):
    s = open(path, encoding='utf-8').read()
    new = recolor_text(s, stats)
    if new != s:
        open(path, 'w', encoding='utf-8', newline='').write(new)
        return True
    return False


def main():
    stats = {}
    n_html = n_css = 0
    only = sys.argv[1:]
    if only:
        for rel in only:
            p = os.path.join(DP, rel.replace('/', os.sep))
            if p.endswith('.css'):
                if patch_css(p, stats):
                    n_css += 1
            elif p.endswith('.html'):
                if patch_html(p, stats):
                    n_html += 1
    else:
        for dirpath, dirnames, filenames in os.walk(DP):
            if 'vendor' in dirpath:
                continue
            for fn in filenames:
                p = os.path.join(dirpath, fn)
                if fn.endswith('.css'):
                    if patch_css(p, stats):
                        n_css += 1
                elif fn.endswith('.html'):
                    if patch_html(p, stats):
                        n_html += 1
    print('patched css: %d  html: %d' % (n_css, n_html))
    print('distinct colour tokens replaced: %d' % len(stats))
    for k in sorted(stats):
        print('  %-28s -> %s' % (k, stats[k]))


if __name__ == '__main__':
    main()
