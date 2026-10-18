#!/usr/bin/env python3
"""Fallback pusher: upload the repository to GitHub in small chunks.

A single big `git push` (~200 MB) can time out with HTTP 408 on a slow
uplink.  This script builds an orphan branch `pages-staging` as a chain of
small commits (one chunk of files per commit) and pushes them one by one,
so every HTTP request stays small.  Re-running resumes where it stopped.

Usage:
    python tools/push_chunks.py                # dry run: show the plan
    python tools/push_chunks.py --apply        # execute (default 10 MB/chunk)
    python tools/push_chunks.py --apply --chunk-mb=6
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGE = "pages-staging"
PLAN_FILE = os.path.join(ROOT, "tools", "_chunk_plan.json")
APPLY = "--apply" in sys.argv
CHUNK_MB = 10
for _a in sys.argv:
    if _a.startswith("--chunk-mb="):
        CHUNK_MB = int(_a.split("=", 1)[1])
CHUNK = CHUNK_MB * 1024 * 1024
SMALL = 400 * 1024  # files up to this size go to the base chunk


def run(args, timeout=3600, check=False):
    try:
        r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        print("!! timeout:", " ".join(args))
        sys.exit(1)
    if check and r.returncode != 0:
        print("!! command failed:", " ".join(args))
        print(r.stdout[-500:])
        print(r.stderr[-800:])
        sys.exit(1)
    return r


def git(*args, **kw):
    return run(["git", *args], **kw)


def branch():
    return git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()


def file_size(f):
    try:
        return os.path.getsize(os.path.join(ROOT, f))
    except OSError:
        return 0


def make_plan():
    out = git("ls-tree", "-r", "--name-only", "main", check=True).stdout.splitlines()
    files = [f for f in out if f.strip()]
    small = [f for f in files if file_size(f) <= SMALL]
    big = sorted((f for f in files if file_size(f) > SMALL), key=lambda f: -file_size(f))
    chunks = [small]
    cur, cur_size = [], 0
    for f in big:
        s = file_size(f)
        if cur and cur_size + s > CHUNK:
            chunks.append(cur)
            cur, cur_size = [], 0
        cur.append(f)
        cur_size += s
    if cur:
        chunks.append(cur)
    plan = {"chunk_mb": CHUNK_MB, "chunks": chunks}
    with open(PLAN_FILE, "w", encoding="utf-8") as fh:
        json.dump(plan, fh, ensure_ascii=False)
    return plan


def load_plan():
    if os.path.exists(PLAN_FILE):
        with open(PLAN_FILE, encoding="utf-8") as fh:
            return json.load(fh)
    return None


def staged_files():
    if branch() != STAGE:
        return set()
    r = git("ls-tree", "-r", "--name-only", "HEAD")
    if r.returncode != 0:
        return set()
    return set(r.stdout.splitlines())


def push_main():
    for attempt in range(1, 4):
        print(f"    push attempt {attempt} ...", flush=True)
        r = git("push", "origin", "HEAD:main")
        if r.returncode == 0:
            print("    push OK")
            return True
        tail = (r.stderr or r.stdout).strip().splitlines()
        print("    failed:", tail[-2:] if tail else "?")
    return False


def main():
    # safety: never overwrite an existing remote main
    r = git("ls-remote", "origin", "refs/heads/main")
    if r.stdout.strip():
        print("remote main already exists:", r.stdout.strip()[:100])
        print("chunk push is not needed (or use force manually).")
        return

    plan = load_plan() or make_plan()
    chunks = plan["chunks"]
    total = sum(file_size(f) for c in chunks for f in c)

    if not APPLY:
        print(f"dry-run: branch={branch()}, chunks={len(chunks)}, total={total/1e6:.1f} MB")
        for i, c in enumerate(chunks, 1):
            s = sum(file_size(f) for f in c)
            print(f"  chunk {i:03d}: {len(c):4d} files, {s/1e6:6.1f} MB, first: {c[0]}")
        print("run with --apply to execute")
        return

    cur = branch()
    if cur != STAGE:
        dirty = git("status", "--porcelain").stdout.strip()
        if dirty:
            print("working tree is not clean; commit or stash first:")
            print(dirty[:400])
            sys.exit(1)
        exists = git("show-ref", "--verify", "--quiet", f"refs/heads/{STAGE}").returncode == 0
        if exists:
            git("checkout", STAGE, check=True)
        else:
            git("checkout", "--orphan", STAGE, check=True)
            git("read-tree", "--empty", check=True)
        print(f"on branch {STAGE}")

    done = staged_files()
    if done:
        print(f"resuming: {len(done)} files already committed")
        if not push_main():
            print("could not push existing commits; aborting")
            sys.exit(1)

    for idx, chunk in enumerate(chunks, 1):
        todo = [f for f in chunk if f not in done]
        if not todo:
            continue
        s = sum(file_size(f) for f in todo)
        print(f"chunk {idx}/{len(chunks)}: +{len(todo)} files, {s/1e6:.1f} MB", flush=True)
        pfile = os.path.join(ROOT, "tools", "_chunk_paths.tmp")
        with open(pfile, "w", encoding="utf-8", newline="") as fh:
            fh.write("\0".join(todo))
        git("add", "--pathspec-from-file=" + pfile, "--pathspec-file-nul", check=True)
        git("commit", "-q", "-m", f"site part {idx}/{len(chunks)}", check=True)
        if not push_main():
            print("giving up; re-run the script to resume")
            sys.exit(1)
        done = staged_files()

    print("ALL CHUNKS PUSHED")
    print("next:")
    print(f"  git branch -M {STAGE} main")
    print("  git branch --set-upstream-to=origin/main main")


if __name__ == "__main__":
    main()
