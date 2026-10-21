"""Prepare the mirrored DataPool site for the mobile version.

Two idempotent changes are applied to every DataPool HTML page:

* add the missing ``<meta name="viewport" ...>`` tag;
* add a cache-busting ``?v=`` query to the shared ``css/main.css`` and
  ``app/app.js`` assets, so a previously cached desktop copy is replaced
  after deployment.

Run from any directory; paths are resolved relative to this script.
"""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
DATA_POOL = ROOT / "data-pool"
ASSET_VERSION = "20261021-5"

META = '<meta name="viewport" content="width=device-width, initial-scale=1">'
VIEWPORT_RE = re.compile(r"""name\s*=\s*["']viewport["']""", re.IGNORECASE)
CHARSET_RE = re.compile(
    r"""<meta\s+charset\s*=\s*["']?utf-8["']?\s*/?>""", re.IGNORECASE
)
HEAD_RE = re.compile(r"<head[^>]*>", re.IGNORECASE)
CSS_RE = re.compile(
    r"""(href\s*=\s*["'][^"']*css/main\.css)(?:\?v=[^"']*)?(["'])""",
    re.IGNORECASE,
)
APP_JS_RE = re.compile(
    r"""(src\s*=\s*["'][^"']*app/app\.js)(?:\?v=[^"']*)?(["'])""",
    re.IGNORECASE,
)


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text

    if not VIEWPORT_RE.search(text):
        eol = "\r\n" if "\r\n" in text else "\n"
        insertion = eol + "    " + META
        match = CHARSET_RE.search(text)
        if match:
            text = text[: match.end()] + insertion + text[match.end() :]
        else:
            match = HEAD_RE.search(text)
            if match:
                text = text[: match.end()] + insertion + text[match.end() :]
            else:
                print(f"skipped (no <head>): {path.relative_to(ROOT)}")

    text = CSS_RE.sub(rf"\g<1>?v={ASSET_VERSION}\g<2>", text)
    text = APP_JS_RE.sub(rf"\g<1>?v={ASSET_VERSION}\g<2>", text)

    if text == original:
        return False

    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(text)
    return True


def main() -> None:
    files = sorted(DATA_POOL.rglob("*.html"))
    changed = 0
    for path in files:
        if patch_file(path):
            changed += 1
            print(f"patched {path.relative_to(ROOT)}")
    print(f"Done: {changed} of {len(files)} HTML files updated.")


if __name__ == "__main__":
    main()
