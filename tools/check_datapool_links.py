# -*- coding: utf-8 -*-
"""Проверка целостности зеркала data-pool: все локальные ссылки/ресурсы существуют."""
import os
import re
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DP = os.path.join(ROOT, 'data-pool')

ATTR_RE = re.compile(r'(?:src|href)\s*=\s*["\']([^"\']+)["\']', re.I)
URL_RE = re.compile(r'url\(([^)]+)\)')

SKIP_PREFIX = ('http://', 'https://', 'data:', 'mailto:', '#', 'javascript:', 'tel:')


def main():
    missing = {}
    checked = 0
    pages = 0
    for dirpath, dirnames, filenames in os.walk(DP):
        if 'vendor' in dirpath:
            continue
        for fn in filenames:
            if not fn.endswith('.html'):
                continue
            pages += 1
            p = os.path.join(dirpath, fn)
            html = open(p, encoding='utf-8', errors='replace').read()
            urls = ATTR_RE.findall(html) + URL_RE.findall(html)
            for u in urls:
                u = u.strip().strip('"\'')
                if not u or u.startswith(SKIP_PREFIX):
                    continue
                if u.startswith('/data-pool/'):
                    rel = u[len('/data-pool/'):]
                elif u.startswith('/'):
                    continue  # вне дерева data-pool (например, /app/)
                else:
                    rel = u
                rel = urllib.parse.unquote(rel.split('#')[0].split('?')[0])
                if not rel:
                    continue
                if rel.endswith('/') or rel == '':
                    rel += 'index.html'
                target = os.path.join(DP, rel.replace('/', os.sep))
                checked += 1
                if not os.path.exists(target):
                    key = os.path.relpath(p, DP) + ' -> ' + u
                    missing[key] = missing.get(key, 0) + 1
    print('pages:', pages, ' refs checked:', checked, ' missing:', len(missing))
    for k in sorted(missing)[:40]:
        print('  MISSING', k)
    return 0 if not missing else 1


if __name__ == '__main__':
    sys.exit(main())
