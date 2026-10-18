"""Mirror https://redcharacters.com into D:\\Desktop\\cCPRED\\app (static files only)."""
import os, sys, time, json, base64, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, 'app')
BASE = 'https://redcharacters.com/'
CK_BASE = 'https://www.gstatic.com/flutter-canvaskit/59aa584fdf100e6c78c785d8a5b565d1de4b48ab/'

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')


def fetch(url, attempts=6, timeout=60):
    last = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*'})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read()
                # transparent gzip handling if server ignored Accept-Encoding
                if data[:2] == b'\x1f\x8b' and not url.endswith('.gz'):
                    import gzip
                    try:
                        data = gzip.decompress(data)
                    except Exception:
                        pass
                return data
        except Exception as e:  # noqa
            last = e
            sys.stderr.write('retry %d/%d %s (%s)\n' % (i + 1, attempts, url, e))
            time.sleep(2 + 2 * i)
    # curl fallback (some hosts drop the TLS session for urllib)
    try:
        import subprocess, tempfile
        fd, tmp = tempfile.mkstemp()
        os.close(fd)
        try:
            r = subprocess.run(
                ['curl.exe', '-sL', '--http1.1', '--retry', '4', '--retry-all-errors',
                 '--retry-delay', '3', '-A', UA, url, '-o', tmp, '-w', '%{http_code}'],
                capture_output=True, text=True, timeout=180)
            if r.returncode == 0 and r.stdout.strip() == '200':
                with open(tmp, 'rb') as f:
                    return f.read()
        finally:
            try:
                os.remove(tmp)
            except OSError:
                pass
    except Exception as e:  # noqa
        last = e
    raise RuntimeError('failed: %s (%s)' % (url, last))


def save(rel, data, force=False):
    path = os.path.join(APP, rel.replace('/', os.sep))
    if not force and os.path.exists(path) and os.path.getsize(path) == len(data):
        return -1
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(data)
    return len(data)


def parse_smc(b):
    """Decode a Dart StandardMessageCodec message (asset manifest)."""
    i = 0

    def rdtype():
        nonlocal i
        t = b[i]; i += 1
        return t

    def rdint32():
        nonlocal i
        v = int.from_bytes(b[i:i + 4], 'little', signed=True); i += 4
        return v

    def rdvarint():
        nonlocal i
        v = 0; s = 0
        while True:
            x = b[i]; i += 1
            v |= (x & 0x7f) << s
            if not (x & 0x80):
                break
            s += 7
        return v

    def value():
        nonlocal i
        t = rdtype()
        if t == 0: return None
        if t == 1: return True
        if t == 2: return False
        if t == 3: return rdint32()
        if t == 4:
            v = int.from_bytes(b[i:i + 8], 'little', signed=True); i += 8
            return v
        if t == 5:
            length = rdvarint(); neg = b[i]; i += 1
            n = int.from_bytes(b[i:i + length], 'big'); i += length
            return -n if neg else n
        if t == 6:
            import struct
            v = struct.unpack_from('<d', b, i)[0]; i += 8
            return v
        if t == 7:
            l = rdvarint(); s = b[i:i + l].decode('utf-8'); i += l
            return s
        if t == 8:
            l = rdvarint(); v = bytes(b[i:i + l]); i += l
            return v
        if t in (9, 10, 11, 14):
            import struct
            n = rdvarint()
            fmt = {9: 'i', 10: 'q', 11: 'd', 14: 'f'}[t]
            size = {9: 4, 10: 8, 11: 8, 14: 4}[t]
            v = list(struct.unpack_from('<%d%s' % (n, fmt), b, i)); i += size * n
            return v
        if t == 12:
            n = rdvarint()
            return [value() for _ in range(n)]
        if t == 13:
            n = rdvarint()
            d = {}
            for _ in range(n):
                k = value(); v = value()
                d[k] = v
            return d
        raise ValueError('smc type %d at %d' % (t, i - 1))

    v = value()
    return v


def main():
    os.makedirs(APP, exist_ok=True)
    print('mirror ->', APP)

    root_files = [
        'index.html', 'flutter_bootstrap.js', 'main.dart.js',
        'flutter_service_worker.js', 'manifest.json', 'favicon.png',
        'icons/Icon-192.png', 'icons/Icon-512.png',
        'icons/Icon-maskable-192.png', 'icons/Icon-maskable-512.png',
        'assets/AssetManifest.bin', 'assets/AssetManifest.bin.json',
        'assets/FontManifest.json', 'assets/fonts/MaterialIcons-Regular.otf',
    ]
    for rel in root_files:
        data = fetch(BASE + rel)
        n = save(rel, data)
        print('%7s  %s' % (n if n >= 0 else 'skip', rel))

    # asset list from binary manifest
    manifest_raw = fetch(BASE + 'assets/AssetManifest.bin.json')
    raw = base64.b64decode(json.loads(manifest_raw.decode('utf-8')))
    manifest = parse_smc(raw)
    for key in sorted(manifest):
        rel = 'assets/' + key
        data = fetch(BASE + rel)
        n = save(rel, data)
        print('%7s  %s' % (n if n >= 0 else 'skip', rel))

    # optional extras
    for rel in ['NOTICES', 'version.json', 'icons/Icon-192-maskable.png']:
        try:
            data = fetch(BASE + rel, attempts=1)
            n = save(rel, data)
            print('%7s  %s' % (n if n >= 0 else 'skip', rel))
        except Exception:
            print('      -  %s (absent)' % rel)

    # CanvasKit from gstatic -> local ./canvaskit/ (plus the chromium variant used by Chrome)
    for rel in ['canvaskit.js', 'canvaskit.wasm', 'canvaskit.symbols',
                'chromium/canvaskit.js', 'chromium/canvaskit.wasm']:
        try:
            data = fetch(CK_BASE + rel, attempts=3)
            n = save('canvaskit/' + rel, data)
            print('%7s  canvaskit/%s' % (n if n >= 0 else 'skip', rel))
        except Exception:
            print('      -  canvaskit/%s (absent)' % rel)

    print('done.')


if __name__ == '__main__':
    main()
