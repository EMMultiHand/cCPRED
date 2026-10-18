# Quick HTTP checks for the local server and the GitHub-Pages simulation.
import urllib.request
import urllib.error

LOCAL = [
    "http://127.0.0.1:8000/",
    "http://127.0.0.1:8000/app/",
    "http://127.0.0.1:8000/data-pool/",
    "http://127.0.0.1:8000/data-pool/chrome/borgs/",
    "http://127.0.0.1:8000/data-pool/css/main.css",
]

SIM = [
    "http://127.0.0.1:8002/cCPRED/",
    "http://127.0.0.1:8002/cCPRED/app/",
    "http://127.0.0.1:8002/cCPRED/app/manifest.json",
    "http://127.0.0.1:8002/cCPRED/data-pool/",
    "http://127.0.0.1:8002/cCPRED/data-pool/chrome/borgs/",
    "http://127.0.0.1:8002/cCPRED/data-pool/css/main.css",
    "http://127.0.0.1:8002/cCPRED/data-pool/css/footer.css",
    "http://127.0.0.1:8002/cCPRED/data-pool/fonts/Cyberpunk_RUS_BY_LYAJKA.ttf",
    "http://127.0.0.1:8002/cCPRED/data-pool/images/favicon.png",
    "http://127.0.0.1:8002/cCPRED/data-pool/app/app.js",
    "http://127.0.0.1:8002/cCPRED/data-pool/search-index.json",
    "http://127.0.0.1:8002/cCPRED/data-pool/vendor/lunr/lunr.js",
]

SIZES = {
    "http://127.0.0.1:8002/cCPRED/app/main.dart.js": 5642455,
    "http://127.0.0.1:8002/cCPRED/app/canvaskit/chromium/canvaskit.wasm": 5686880,
}


def check(url):
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            data = r.read()
            return r.status, len(data)
    except urllib.error.HTTPError as e:
        return e.code, 0
    except Exception as e:  # noqa: BLE001
        return "ERR", str(e)[:80]


def main():
    print("== LOCAL (port 8000) ==")
    for u in LOCAL:
        s, info = check(u)
        print(" ", s, u)
    print("== PAGES SIM (port 8002, /cCPRED/...) ==")
    for u in SIM:
        s, info = check(u)
        print(" ", s, u)
    print("== full sizes ==")
    for u, want in SIZES.items():
        s, n = check(u)
        ok = "OK" if n == want else "!!"
        print(" ", ok, s, n, "из", want)


if __name__ == "__main__":
    main()
