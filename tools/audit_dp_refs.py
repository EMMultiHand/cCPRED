# Audit of reference paths in data-pool (and a few app checks).
# Prints: counts by extension, forms of absolute paths, samples from non-HTML
# files, <base> tags, external data-pool URLs, and "/data-pool" without slash.
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DP = os.path.join(ROOT, "data-pool")

EXTS = {".html", ".css", ".js", ".json", ".svg", ".xml", ".webmanifest"}

count_by_ext = Counter()
files_by_ext = defaultdict(set)
abs_other = Counter()      # absolute refs not starting with /data-pool
abs_other_samples = {}
n_noslash = 0              # "/data-pool" not followed by "/"
noslash_samples = []
n_external = 0             # "data-pool" inside http(s):// links
base_tags = []
js_css_samples = defaultdict(list)
external_samples = []

re_noslash = re.compile(r"/data-pool(?![-\w/])")
re_ext = re.compile(r"(https?:)?//[A-Za-z0-9.-]*(?:github\.io)?[^\"'\s]*data-pool[^\"'\s]*")
re_absurl = re.compile(r"[\"'(=\s](/[^\"'\s)>,]{2,})")

for dirpath, dirnames, filenames in os.walk(DP):
    dirnames[:] = [d for d in dirnames if d != "vendor" or True]
    for fn in filenames:
        ext = os.path.splitext(fn)[1].lower()
        if ext not in EXTS:
            continue
        path = os.path.join(dirpath, fn)
        rel = os.path.relpath(path, ROOT)
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
            continue
        n = text.count("/data-pool/")
        if n:
            count_by_ext[ext] += n
            files_by_ext[ext].add(rel)
        n_check = len(re_noslash.findall(text))
        if n_check:
            n_noslash += n_check
            for m in re_noslash.finditer(text):
                s = text[max(0, m.start() - 50):m.end() + 40].replace("\n", " ")
                if len(noslash_samples) < 8:
                    noslash_samples.append(rel + " :: " + s)
        for m in re_absurl.finditer(text):
            u = m.group(1)
            if not u.startswith("/data-pool/"):
                abs_other[u] += 1
                if u not in abs_other_samples:
                    abs_other_samples[u] = rel
        for m in re_ext.finditer(text):
            u = m.group(0)
            if "github.io" in u or u.startswith("http"):
                n_external += 1
                if len(external_samples) < 6:
                    external_samples.append(rel + " :: " + u[:110])
        if "<base" in text:
            for m in re.finditer(r"<base[^>]*>", text, re.I):
                base_tags.append(rel + " :: " + m.group(0)[:120])
        if ext in (".js", ".css", ".svg", ".xml", ".json") and "/data-pool/" in text:
            for m in re.finditer(r".{0,60}/data-pool/.{0,60}", text):
                if len(js_css_samples[rel]) < 8:
                    js_css_samples[rel].append(m.group(0).replace("\n", " ")[:160])

print("== /data-pool/ по расширениям ==")
for ext, c in count_by_ext.most_common():
    print(f"  {ext}: {c} вхождений в {len(files_by_ext[ext])} файлах")
print("== /data-pool без слеша:", n_noslash)
for s in noslash_samples:
    print("   ", s)
print("== внешние ссылки с data-pool:", n_external)
for s in external_samples:
    print("   ", s)
print("== <base> теги:", len(base_tags))
for s in base_tags[:10]:
    print("   ", s)
print("== другие абсолютные пути (топ-30) ==")
for u, c in abs_other.most_common(30):
    print(f"  {c:5d}  {u[:110]}   ({abs_other_samples[u][:70]})")
print("== контексты в .js/.css/.json/.svg ==")
for rel, samples in list(js_css_samples.items())[:14]:
    print("  --", rel)
    for s in samples[:6]:
        print("     ", s)

# App checks: absolute paths in main.dart.js
main_js = os.path.join(ROOT, "app", "main.dart.js")
if os.path.exists(main_js):
    with open(main_js, "r", encoding="utf-8", errors="replace") as fh:
        t = fh.read()
    print("== main.dart.js: data-pool mentions ==", t.count("data-pool"))
    seen = 0
    for m in re.finditer(r".{0,50}data-pool.{0,50}", t):
        seen += 1
        if seen <= 12:
            print("   ", m.group(0).replace("\n", " ")[:130])
    print("== main.dart.js: absolute-path refs =\"\\/ ==")
    seen = 0
    for m in re.finditer(r".{0,50}=\"/[^/\"]{1,80}", t):
        seen += 1
        if seen <= 12:
            print("   ", m.group(0).replace("\n", " ")[:130])
    print("   всего:", seen)
