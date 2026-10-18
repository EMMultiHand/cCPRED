"""Mirror https://alec-leon.github.io/data-pool into D:\\Desktop\\cCPRED\\data-pool.

- crawls every HTML page (recursively, same /data-pool/ prefix),
- downloads every deployed asset listed in the repository tree
  (css/, app/, data/, fonts/, images/, dist/) - node_modules and sources are skipped,
- vendors the unpkg.com lunr scripts locally,
- fetches runtime JSON files that pages request via fetch().
"""
import os, sys, re, time, json, urllib.request, gzip, subprocess, tempfile
from urllib.parse import urljoin, urlsplit, urlunsplit
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DP = os.path.join(ROOT, 'data-pool')
ORIGIN = 'https://alec-leon.github.io'
PREFIX = '/data-pool/'
START = ORIGIN + PREFIX

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')

SKIP_TREE_PREFIXES = ('node_modules/', '.github/', 'content/', 'templates/')
SKIP_TREE_FILES = ('.eleventy.js', '.eleventy.dev.js', 'package.json',
                   'package-lock.json', 'package.dev.json', 'README.md')


def fetch(url, attempts=5, timeout=90, allow_404=True):
    last = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*'})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read()
                if data[:2] == b'\x1f\x8b':
                    try:
                        data = gzip.decompress(data)
                    except Exception:
                        pass
                return data
        except urllib.error.HTTPError as e:
            if e.code == 404 and allow_404:
                return None
            last = e
            time.sleep(1.5 + 1.5 * i)
        except Exception as e:  # noqa
            last = e
            time.sleep(1.5 + 1.5 * i)
    # curl fallback
    try:
        fd, tmp = tempfile.mkstemp(); os.close(fd)
        try:
            r = subprocess.run(['curl.exe', '-sL', '--http1.1', '--retry', '4',
                                '--retry-all-errors', '--retry-delay', '2',
                                '-A', UA, url, '-o', tmp, '-w', '%{http_code}'],
                               capture_output=True, text=True, timeout=240)
            code = r.stdout.strip()
            if r.returncode == 0 and code == '200':
                with open(tmp, 'rb') as f:
                    return f.read()
            if code == '404' and allow_404:
                return None
        finally:
            try:
                os.remove(tmp)
            except OSError:
                pass
    except Exception as e:  # noqa
        last = e
    raise RuntimeError('failed: %s (%s)' % (url, last))


def url_to_rel(url):
    """Map a site URL to a local relative path (relative to data-pool/)."""
    p = urlsplit(url)
    path = p.path
    assert path.startswith(PREFIX), path
    rel = path[len(PREFIX):]
    rel = rel.split('?')[0].split('#')[0]
    if rel == '' or rel.endswith('/'):
        rel += 'index.html'
    elif '.' not in os.path.basename(rel):
        rel += '/index.html'
    return rel.replace('/', os.sep)


def save(rel, data):
    path = os.path.join(DP, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(data)
    return len(data)


LINK_RE = re.compile(r'(?:href|src)\s*=\s*["\']([^"\']+)["\']', re.I)
URLDATA_RE = re.compile(r'data-(?:screen-url|enemies-url|open-url)\s*=\s*["\']([^"\']+)["\']', re.I)


def normalize_link(href, base):
    if href.startswith(('#', 'mailto:', 'javascript:', 'data:', 'tel:')):
        return None
    absu = urljoin(base, href)
    sp = urlsplit(absu)
    if sp.netloc not in ('', 'alec-leon.github.io'):
        return None
    if not sp.path.startswith(PREFIX):
        return None
    return urlunsplit((sp.scheme or 'https', sp.netloc or 'alec-leon.github.io', sp.path, sp.query, ''))


def crawl_pages():
    seen, todo, pages = set(), [START,
                                ORIGIN + PREFIX + 'gm-screen/screen/index.html'], {}
    while todo:
        url = todo.pop(0)
        if url in seen:
            continue
        seen.add(url)
        data = fetch(url)
        if data is None:
            print('      -  %s (404)' % url)
            continue
        pages[url] = data
        rel = url_to_rel(url)
        print('%7d  %s  ->  %s' % (len(data), url, rel))
        save(rel, data)
        text = data.decode('utf-8', 'replace')
        base = url
        for m in LINK_RE.finditer(text):
            u = normalize_link(m.group(1), base)
            if u and u not in seen:
                todo.append(u)
        for m in URLDATA_RE.finditer(text):
            u = normalize_link(m.group(1), base)
            if u and u not in seen:
                todo.append(u)
    return pages


def download_tree_assets(tree):
    files = []
    for t in tree:
        if t.get('type') != 'blob':
            continue
        p = t['path']
        if p.startswith(SKIP_TREE_PREFIXES) or p in SKIP_TREE_FILES:
            continue
        if not p.startswith(('css/', 'app/', 'data/', 'fonts/', 'images/', 'dist/')):
            continue
        files.append(p)
    print('tree assets to fetch:', len(files))

    done = 0

    def work(p):
        nonlocal done
        url = ORIGIN + PREFIX + p
        data = fetch(url)
        done += 1
        if data is None:
            return (p, None)
        return (p, data)

    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(work, p): p for p in files}
        for fut in as_completed(futs):
            p, data = fut.result()
            if data is None:
                print('%8s  %s (404)' % ('-', p))
                continue
            n = save(p.replace('/', os.sep), data)
            print('%8d  %s' % (n, p))


def main():
    os.makedirs(DP, exist_ok=True)
    print('== fetching repository tree ==')
    tree_raw = fetch('https://api.github.com/repos/alec-leon/data-pool/git/trees/master?recursive=1')
    tree = json.loads(tree_raw.decode('utf-8'))['tree']

    print('== crawling pages ==')
    pages = crawl_pages()

    print('== fetching tree assets ==')
    download_tree_assets(tree)

    print('== runtime extras ==')
    extras = [
        'search-index.json',
        'data/enemies/enemies-list.json',
    ]
    for rel in extras:
        url = ORIGIN + PREFIX + rel
        data = fetch(url)
        if data is None:
            print('%8s  %s (404)' % ('-', rel))
            continue
        n = save(rel.replace('/', os.sep), data)
        print('%8d  %s' % (n, rel))

    print('== vendoring lunr ==')
    for rel, url in [
        ('vendor/lunr/lunr.js', 'https://unpkg.com/lunr/lunr.js'),
        ('vendor/lunr/lunr.min.js', 'https://unpkg.com/lunr/lunr.min.js'),
        ('vendor/lunr/lunr.stemmer.support.js', 'https://unpkg.com/lunr-languages/lunr.stemmer.support.js'),
        ('vendor/lunr/lunr.ru.js', 'https://unpkg.com/lunr-languages/lunr.ru.js'),
    ]:
        data = fetch(url, allow_404=False)
        n = save(rel.replace('/', os.sep), data)
        print('%8d  %s' % (n, rel))

    print('done.')


if __name__ == '__main__':
    main()
