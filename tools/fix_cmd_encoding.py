# Re-encodes the launcher .cmd files to CP866 with CRLF line endings and adds
# "chcp 866" so Russian text renders correctly in the Windows console.
# Usage: python tools/fix_cmd_encoding.py
import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
FILES = [
    ROOT / "start.cmd",
    ROOT / "tunnel.cmd",
    ROOT / "tools" / "tunnel-run.cmd",
    ROOT / "tools" / "server-run.cmd",
]


def convert(path: pathlib.Path) -> None:
    data = path.read_bytes()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        print(path.name + ": already non-UTF8, skipped")
        return
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Normalize any chcp line to 866.
    text = re.sub(r"(?m)^\s*chcp\b.*$", "chcp 866 >nul", text)
    if "chcp 866" not in text:
        lines = text.split("\n")
        idx = 0
        for i, line in enumerate(lines):
            if line.strip().lower().startswith("@echo off"):
                idx = i + 1
                break
        lines.insert(idx, "chcp 866 >nul")
        text = "\n".join(lines)
    out = text.replace("\n", "\r\n")
    try:
        encoded = out.encode("cp866")
    except UnicodeEncodeError as exc:
        print(path.name + ": NOT convertible to cp866: " + repr(exc.object[exc.start:exc.end]))
        return
    path.write_bytes(encoded)
    print(path.name + ": written cp866+CRLF, " + str(len(encoded)) + " bytes")


def main() -> None:
    for f in FILES:
        if f.exists():
            convert(f)
        else:
            print(f.name + ": not found")


if __name__ == "__main__":
    main()
