"""Apply the dark-brown theme to the mirrored redcharacters.com app.

1. main.dart.js  - remaps the app's AppPalette colour literals to warm brown tones.
2. flutter_bootstrap.js - loads CanvasKit from ./canvaskit/ instead of the gstatic CDN.
3. index.html - brown pre-boot loader, forced default "dark" theme (brown),
   and an integrated "Data Pool" side panel (reference data from data-pool).
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, 'app')

# ---------------------------------------------------------------- palette ---
# old hex -> new hex (dark-brown theme)
MAP = {
    # dark theme
    '0C0D0E': '1A110B',  # background
    '17181A': '251A11',  # surface / cards
    '1E1F21': '2F2016',  # elevated surface
    '2C2E30': '3E2B1D',  # borders
    '45494C': '4C3727',  # strong border (dark)
    'D7D8D7': 'E3CDAF',  # light outline on dark
    '8B8F8F': 'A28A6D',  # muted text
    'F5F6F6': 'F2E5D0',  # main text
    '0E8FA3': 'C68B49',  # primary accent
    '29B6CF': 'E8B87B',  # bright accent
    'E02A22': 'C96A2C',  # splash glitch band a
    'B90F0A': '8F4318',  # splash glitch band b
    '3A3E40': '453122',  # alt border (dark)
    # light theme (warm parchment)
    'ECEDED': 'F1E6D4',  # background
    'FFFFFF': 'FFFCF5',  # white
    '4E5152': '57452F',  # borders
    '7E8281': '8B7963',  # muted text
    'CE160E': 'A94A20',  # accent
    'B4B8B8': 'C6B298',  # tertiary
}


def num(x):
    """Format an int 0..255 the way dart2js prints channel/255 doubles."""
    v = x / 255
    if v == int(v):
        return str(int(v))
    return repr(v)


def anum(a):
    """Format an alpha double the way dart2js prints it."""
    if a == int(a):
        return str(int(a))
    return repr(a)


def hex_to_triple(h):
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def patch_main_js():
    path = os.path.join(APP, 'main.dart.js')
    src = open(path, encoding='utf-8').read()

    pat = re.compile(r'new A\.X\(([0-9.]+),([0-9.]+),([0-9.]+),([0-9.]+),B\.z\)')
    hits = []
    changes = {}

    def repl(m):
        a = float(m.group(1))
        r = round(float(m.group(2)) * 255)
        g = round(float(m.group(3)) * 255)
        b = round(float(m.group(4)) * 255)
        hx = '%02X%02X%02X' % (r, g, b)
        hits.append((hx, a))
        new = MAP.get(hx)
        if new is None:
            if hx not in ('000000',) and hx not in MAP.values():
                changes.setdefault('unmapped:' + hx, 0)
                changes['unmapped:' + hx] += 1
            return m.group(0)
        nr, ng, nb = hex_to_triple(new)
        changes[hx] = changes.get(hx, 0) + 1
        return 'new A.X(%s,%s,%s,%s,B.z)' % (anum(a), num(nr), num(ng), num(nb))

    out = pat.sub(repl, src)

    rewritten = sum(v for k, v in changes.items() if not k.startswith('unmapped:'))
    if rewritten == 0:
        # idempotency: already themed?
        if hex_to_triple(MAP['0C0D0E']) and 'new A.X(1,%s,%s,%s,B.z)' % tuple(
                num(c) for c in hex_to_triple(MAP['0C0D0E'])) in src:
            print('main.dart.js: already themed, skipping')
            return
        print('main.dart.js: no palette entries found - unthemed original? aborting')
        sys.exit(1)

    # report
    for h in MAP:
        if h not in changes:
            print('  !! palette entry %s not present in main.dart.js' % h)

    open(path, 'w', encoding='utf-8', newline='').write(out)
    print('main.dart.js patched: %d colour literals rewritten' % rewritten)


def patch_bootstrap():
    path = os.path.join(APP, 'flutter_bootstrap.js')
    s = open(path, encoding='utf-8').read()
    if 'canvasKitBaseUrl: "canvaskit/"' in s:
        print('flutter_bootstrap.js: already patched, skipping')
        return
    old = '_flutter.loader.load({\n  onEntrypointLoaded: async (engineInitializer) => {'
    new = ('_flutter.loader.load({\n'
           '  config: { canvasKitBaseUrl: "canvaskit/" },\n'
           '  onEntrypointLoaded: async (engineInitializer) => {')
    if old not in s:
        print('bootstrap: pattern not found')
        sys.exit(1)
    s = s.replace(old, new, 1)
    open(path, 'w', encoding='utf-8', newline='').write(s)
    print('flutter_bootstrap.js patched: local CanvasKit')


PANEL_CSS = '''
    /* ---- Dark-brown additions: Data Pool integration ---- */
    #dp-fab {
      position: fixed;
      right: 16px;
      bottom: 16px;
      z-index: 9000;
      display: flex;
      align-items: center;
      gap: 8px;
      background: #2f2016;
      color: #e8b87b;
      border: 1.5px solid #c68b49;
      border-radius: 10px;
      padding: 10px 14px;
      font: 700 13px/1 system-ui, Arial, sans-serif;
      letter-spacing: .04em;
      text-transform: uppercase;
      cursor: pointer;
      box-shadow: 0 4px 18px rgba(0, 0, 0, .55);
    }

    #dp-fab:hover {
      background: #3e2b1d;
      color: #f2e5d0;
    }

    #dp-panel {
      position: fixed;
      inset: 0 0 0 auto;
      width: min(760px, 96vw);
      z-index: 9001;
      display: flex;
      flex-direction: column;
      background: #1a110b;
      border-left: 2px solid #c68b49;
      box-shadow: -12px 0 40px rgba(0, 0, 0, .6);
    }

    #dp-panel.hidden {
      display: none;
    }

    #dp-panel-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 10px 14px;
      background: #251a11;
      border-bottom: 1px solid #3e2b1d;
      color: #f2e5d0;
      font: 600 14px/1.3 system-ui, Arial, sans-serif;
    }

    #dp-panel-actions {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    #dp-panel-actions a {
      color: #e8b87b;
      font: 600 12px/1 system-ui, Arial, sans-serif;
      text-decoration: none;
      white-space: nowrap;
    }

    #dp-panel-actions a:hover {
      color: #f2e5d0;
    }

    #dp-panel-close {
      background: transparent;
      color: #c68b49;
      border: 1px solid #3e2b1d;
      border-radius: 6px;
      width: 30px;
      height: 28px;
      cursor: pointer;
      font-size: 14px;
    }

    #dp-panel-close:hover {
      color: #f2e5d0;
      border-color: #c68b49;
    }

    #dp-panel-quick {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      padding: 8px 12px;
      background: #201509;
      border-bottom: 1px solid #3e2b1d;
    }

    #dp-panel-quick a {
      color: #d8c7b2;
      background: #2f2016;
      border: 1px solid #3e2b1d;
      border-radius: 999px;
      padding: 4px 10px;
      font: 600 12px/1.2 system-ui, Arial, sans-serif;
      text-decoration: none;
    }

    #dp-panel-quick a:hover {
      color: #1a110b;
      background: #c68b49;
      border-color: #c68b49;
    }

    #dp-frame {
      flex: 1;
      width: 100%;
      border: 0;
      background: #1a110b;
    }

'''

PANEL_HTML = '''  <button id="dp-fab" title="ДатаПул — справочник по Cyberpunk RED">
    <span aria-hidden="true">📚</span> ДатаПул
  </button>
  <div id="dp-panel" class="hidden" aria-hidden="true">
    <div id="dp-panel-head">
      <div id="dp-panel-title">ДатаПул — база знаний Cyberpunk RED</div>
      <div id="dp-panel-actions">
        <a id="dp-panel-external" href="../data-pool/" target="_blank" rel="noopener">Открыть в новой вкладке ↗</a>
        <button id="dp-panel-close" title="Закрыть" aria-label="Закрыть">✕</button>
      </div>
    </div>
    <div id="dp-panel-quick">
      <a href="#" data-dp="../data-pool/equipment/">Снаряжение</a>
      <a href="#" data-dp="../data-pool/equipment/weapons/">Оружие</a>
      <a href="#" data-dp="../data-pool/equipment/armor/">Броня</a>
      <a href="#" data-dp="../data-pool/equipment/acpa/">Силовая броня</a>
      <a href="#" data-dp="../data-pool/chrome/implants/">Импланты</a>
      <a href="#" data-dp="../data-pool/health/drugs_medicine/">Наркотики</a>
      <a href="#" data-dp="../data-pool/health/wounds/">Травмы</a>
      <a href="#" data-dp="../data-pool/job/">Роли</a>
      <a href="#" data-dp="../data-pool/net/quick_hacks/">Взломы</a>
      <a href="#" data-dp="../data-pool/other/martial_arts/">Боевые искусства</a>
      <a href="#" data-dp="../data-pool/" data-dp-tab="enemies">Противники</a>
      <a href="#" data-dp="../data-pool/" data-dp-tab="gm-screen">Ширма Мастера</a>
      <a href="#" data-dp="../data-pool/rules/">Книги правил</a>
      <a href="#" data-dp="../data-pool/faq/">FAQ</a>
    </div>
    <iframe id="dp-frame" title="ДатаПул" loading="lazy"></iframe>
  </div>
'''

PANEL_JS = '''  <script>
    (function () {
      var fab = document.getElementById('dp-fab');
      var panel = document.getElementById('dp-panel');
      var frame = document.getElementById('dp-frame');
      var closeBtn = document.getElementById('dp-panel-close');
      var initialized = false;

      function openPanel(url, tab) {
        panel.classList.remove('hidden');
        panel.setAttribute('aria-hidden', 'false');
        var target = url || '../data-pool/';
        if (frame.getAttribute('src') !== target) {
          frame.setAttribute('src', target);
        }
        frame.onload = function () {
          if (!tab) return;
          try {
            var doc = frame.contentDocument;
            var el = doc && doc.getElementById(tab);
            if (el) { el.click(); }
          } catch (error) {}
        };
        initialized = true;
      }

      function closePanel() {
        if (!initialized) return;
        panel.classList.add('hidden');
        panel.setAttribute('aria-hidden', 'true');
      }

      fab.addEventListener('click', function () {
        if (initialized && !panel.classList.contains('hidden')) {
          closePanel();
        } else {
          openPanel();
        }
      });
      closeBtn.addEventListener('click', closePanel);
      panel.querySelectorAll('[data-dp]').forEach(function (link) {
        link.addEventListener('click', function (ev) {
          ev.preventDefault();
          openPanel(link.getAttribute('data-dp'), link.getAttribute('data-dp-tab'));
        });
      });
      document.addEventListener('keydown', function (ev) {
        if (ev.key === 'Escape') { closePanel(); }
      });
    })();
  </script>
'''


def patch_index():
    path = os.path.join(APP, 'index.html')
    s = open(path, encoding='utf-8').read()

    if 'id="dp-panel"' in s:
        print('index.html: already patched, skipping')
        return

    def rep(old, new, count=1):
        nonlocal s
        found = s.count(old)
        if found != count:
            print('index.html: pattern %r found %d times (expected %d)' % (old[:60], found, count))
            sys.exit(1)
        s = s.replace(old, new)

    rep('  <base href="/">', '  <base href="./">')
    rep('<meta name="theme-color" content="#ECEDED">', '<meta name="theme-color" content="#1A110B">')

    # warm loader colours (light)
    rep('background: #eceded;', 'background: #f1e6d4;', 2)
    rep('color: #ce160e;', 'color: #a94a20;')
    rep('background: #ce160e;', 'background: #a94a20;')
    rep('border: 3px solid #4e5152;', 'border: 3px solid #57452f;')
    rep('background: #fff;', 'background: #fffcf5;')
    rep('background: #e02a22;', 'background: #c96a2c;')
    rep('background: #b90f0a;', 'background: #8f4318;')

    # warm loader colours (dark)
    rep('background: #0c0d0e;', 'background: #1a110b;', 2)
    rep('color: #0e8fa3;', 'color: #c68b49;')
    rep('border-color: #d7d8d7;', 'border-color: #e3cdaf;')
    rep('background: #17181a;', 'background: #251a11;')
    rep('html.app-loader-dark #app-loader-mark {\n      background: #0e8fa3;\n    }',
        'html.app-loader-dark #app-loader-mark {\n      background: #c68b49;\n    }')
    rep('html.app-loader-dark #app-loader-mark::before {\n      background: #29b6cf;\n    }',
        'html.app-loader-dark #app-loader-mark::before {\n      background: #e8b87b;\n    }')
    rep('html.app-loader-dark #app-loader-mark::after {\n      background: #0a6f80;\n    }',
        'html.app-loader-dark #app-loader-mark::after {\n      background: #8a5a2a;\n    }')

    # default to the (brown) dark theme on first visit
    rep("""    (function () {
      try {
        var raw = localStorage.getItem('flutter.app_theme_mode');""",
        """    (function () {
      // Default to the dark (brown) theme unless the user already picked one.
      try {
        if (!localStorage.getItem('flutter.app_theme_mode')) {
          localStorage.setItem('flutter.app_theme_mode', '"dark"');
        }
      } catch (error) {}
      try {
        var raw = localStorage.getItem('flutter.app_theme_mode');""")

    # panel css
    rep('  </style>', PANEL_CSS + '  </style>')

    # panel markup (right after the pre-boot loader element)
    anchor = """  <script>
    (function () {
      var titleEl = document.getElementById('app-loader-title');"""
    rep(anchor, PANEL_HTML + anchor)

    # panel behaviour
    rep('  <script src="flutter_bootstrap.js" async></script>',
        PANEL_JS + '  <script src="flutter_bootstrap.js" async></script>')

    open(path, 'w', encoding='utf-8', newline='').write(s)
    print('index.html patched: brown loader + Data Pool panel')


def recolor_icons():
    """Warm up the brand icons (red mark -> copper, white -> parchment)."""
    try:
        from PIL import Image
    except ImportError:
        print('icons: Pillow not installed, skipped')
        return
    import colorsys

    targets = ['favicon.png', 'icons/Icon-192.png', 'icons/Icon-512.png',
               'icons/Icon-maskable-192.png', 'icons/Icon-maskable-512.png']
    for rel in targets:
        path = os.path.join(APP, rel.replace('/', os.sep))
        if not os.path.exists(path):
            continue
        im = Image.open(path).convert('RGBA')
        w, h = im.size
        px = im.load()

        # detect an accent pixel to see whether it is already amber
        sample = None
        for y in range(h):
            for x in range(w):
                r, g, b, a = px[x, y]
                if a > 200 and r > 180 and g < 120 and b < 120:
                    sample = (r, g, b)
                    break
            if sample:
                break
        if sample:
            hh, ss, vv = colorsys.rgb_to_hsv(*(c / 255 for c in sample))
            if abs(hh * 360 - 32) < 6:
                print('icons: %s already amber, skipped' % rel)
                continue

        for y in range(h):
            for x in range(w):
                r, g, b, a = px[x, y]
                if a == 0:
                    continue
                rf, gf, bf = r / 255, g / 255, b / 255
                hh, ss, vv = colorsys.rgb_to_hsv(rf, gf, bf)
                if ss < 0.12:
                    nr, ng, nb = min(1.0, rf), gf * 0.985, bf * 0.94
                else:
                    nr, ng, nb = colorsys.hsv_to_rgb(32 / 360, min(0.62, ss), vv)
                px[x, y] = (round(nr * 255), round(ng * 255), round(nb * 255), a)
        im.save(path)
        print('icons: %s recoloured' % rel)


def main():
    patch_main_js()
    patch_bootstrap()
    patch_index()
    recolor_icons()


if __name__ == '__main__':
    main()
