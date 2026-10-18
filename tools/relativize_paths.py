# Makes data-pool paths portable for GitHub Pages project sites
# (https://<user>.github.io/cCPRED/...) while keeping the local server working.
#
# What it does (only inside data-pool/):
#   1) Replaces the per-page constant
#        <script>window.__BASE_PATH__ = "/data-pool/";</script>
#      with a runtime-computed base path that works under any deployment prefix.
#   2) Rewrites every absolute reference "/data-pool/..." into a relative one,
#      taking the file's depth into account (so it works under /data-pool/ and
#      under /cCPRED/data-pool/ at the same time).
#   3) Fixes the favicon line in app/app.js to use __BASE_PATH__.
#
# Modes:  python tools/relativize_paths.py            (dry run, default)
#         python tools/relativize_paths.py --apply    (writes files)
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DP = os.path.join(ROOT, "data-pool")
APPLY = "--apply" in sys.argv

EXTS = {".html", ".css", ".js", ".json", ".svg", ".xml", ".webmanifest"}

# Inline base-path script (flexible about whitespace).
RE_BASE_SCRIPT = re.compile(
    r'<script>[^<]*?window\.__BASE_PATH__\s*=\s*"/data-pool/"[^<]*?</script>'
)
# The replacement intentionally contains no "/data-pool/" literal with quotes
# around, so this script stays idempotent when re-run.
BASE_SNIPPET = (
    "<script>window.__BASE_PATH__=(function(){var p=location.pathname,"
    "i=p.indexOf('/data-pool'),s='/';return p.slice(0,i>=0?i:0)+'/data-pool'+s;})();</script>"
)

# favicon line in data-pool/app/app.js
RE_FAVICON = re.compile(r"const faviconHref = '/data-pool/images/favicon\.png';")
FAVICON_NEW = (
    "const faviconHref = (window.__BASE_PATH__ || '/data-pool' + '/') + 'images/favicon.png';"
)

# Any "/data-pool/" reference when not preceded by url/identifier characters.
RE_ABS = re.compile(r'(?<![A-Za-z0-9_:/.\-])/data-pool/')

ledger = {}
total_base = 0
total_abs = 0
samples = []

for dirpath, dirnames, filenames in os.walk(DP):
    for fn in filenames:
        ext = os.path.splitext(fn)[1].lower()
        if ext not in EXTS:
            continue
        path = os.path.join(dirpath, fn)
        rel_from_dp = os.path.relpath(path, DP)
        rel = os.path.relpath(path, ROOT)
        depth = rel_from_dp.replace("\\", "/").count("/")
        prefix = "./" if depth == 0 else "../" * depth

        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
        original = text

        n_abs = len(RE_ABS.findall(text))
        n_base = 0

        if ext == ".html":
            res = RE_BASE_SCRIPT.subn(BASE_SNIPPET, text)
            n_base = res[1]
            text = res[0]

        if rel.endswith("app.js".replace("/", os.sep)) or rel.endswith("app.js"):
            res = RE_FAVICON.subn(FAVICON_NEW, text)
            n_base += res[1]
            text = res[0]

        if n_abs:
            text = RE_ABS.sub(prefix, text)
            if len(samples) < 8:
                m = RE_ABS.findall(original)
                samples.append((rel, depth, prefix, n_abs))

        if text != original:
            ledger[rel.replace("\\", "/")] = {"absolute": n_abs, "base_script": n_base, "depth": depth}
            total_abs += n_abs
            total_base += n_base
            if APPLY:
                with open(path, "w", encoding="utf-8", newline="") as fh:
                    fh.write(text)

mode = "APPLIED" if APPLY else "DRY-RUN"
print(f"mode: {mode}")
print(f"files changed: {len(ledger)}")
print(f"absolute refs rewritten: {total_abs}")
print(f"base-path scripts replaced: {total_base}")
print("samples:")
for rel, depth, prefix, n in samples:
    print(f"   depth={depth} prefix={prefix!r} refs={n}  {rel}")

if APPLY:
    with open(os.path.join(ROOT, "tools", "relativize_ledger.json"), "w", encoding="utf-8") as fh:
        json.dump(ledger, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print("ledger: tools/relativize_ledger.json")
