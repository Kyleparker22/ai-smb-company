#!/usr/bin/env python3
"""Prove the playground cannot write to live. Run after touching any crm/ or dashboard/ module.

    python3 playground/check_isolation.py

WHY THIS EXISTS
On 2026-08-07 the playground seeder wrote synthetic connectors into the REAL crm/data.json.
The cause was a split brain: `connector_training.py` had been pointed at the sandbox, but the
module it delegates its writes to — `connector_writes.py`, the single locked write path — still
resolved `os.path.join(HERE, "data.json")`. So reads came from the sandbox and writes went to
production, which is strictly worse than no sandbox at all.

Nine crm/ modules had that same pattern. Fixing the one that bit us would have left eight
loaded guns, so this check enforces the rule instead of trusting the next author to remember:

    HERE is CODE. Data files resolve under DATA_DIR.

Checks:
  1. No crm/ or dashboard/ module resolves a .json/.jsonl/.js data file off HERE.
  2. Every module that touches CRM data defines the DATA_DIR resolver.
  3. Live data is byte-identical after a full playground seed (the empirical test — this is
     the one that would actually have caught the 08-07 leak).
"""
import os, re, sys, glob, json, shutil, hashlib, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA_RE = re.compile(r'os\.path\.join\(HERE,\s*"[^"]*\.(?:json|jsonl|js)"\)')
RESOLVER = 'DATA_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm")'
# Files whose live state must be untouched by any playground activity.
GUARDED = ["crm/data.json", "crm/data.js", "crm/_attribution-log.jsonl",
           "dashboard/data.json", "dashboard/goals.json", "dashboard/todo.json"]

fails = []


def check_no_here_data_paths():
    for p in sorted(glob.glob(os.path.join(REPO, "crm", "*.py"))
                    + glob.glob(os.path.join(REPO, "dashboard", "*.py"))):
        rel = os.path.relpath(p, REPO)
        for i, line in enumerate(open(p, encoding="utf-8"), 1):
            if DATA_RE.search(line):
                fails.append(f"{rel}:{i} resolves a data file off HERE — it will WRITE LIVE "
                             f"while the playground reads the sandbox.\n      {line.strip()}")


def check_resolver_present():
    for p in sorted(glob.glob(os.path.join(REPO, "crm", "*.py"))):
        s = open(p, encoding="utf-8").read()
        rel = os.path.relpath(p, REPO)
        if "DATA_DIR" in s and RESOLVER not in s and "YOURCO_DATA_ROOT" not in s:
            fails.append(f"{rel} uses DATA_DIR but never defines the env-aware resolver.")


def sha(p):
    try:
        return hashlib.sha256(open(p, "rb").read()).hexdigest()
    except OSError:
        return "<absent>"


def check_seed_leaves_live_alone():
    """The empirical test: snapshot every guarded live file, run a full seed (which drives the
    real mark_lesson/confirm_lesson write paths), and re-hash."""
    before = {p: sha(os.path.join(REPO, p)) for p in GUARDED}
    r = subprocess.run([sys.executable, os.path.join(HERE, "seed.py"), "--clients", "4",
                        "--motion", "2", "--bench", "2"],
                       cwd=REPO, capture_output=True, text=True)
    if r.returncode != 0:
        fails.append(f"seed.py failed: {(r.stderr or r.stdout).strip()[:300]}")
        return
    for p in GUARDED:
        if sha(os.path.join(REPO, p)) != before[p]:
            fails.append(f"LIVE FILE MUTATED BY A SEED RUN: {p}")


if __name__ == "__main__":
    check_no_here_data_paths()
    check_resolver_present()
    check_seed_leaves_live_alone()
    if fails:
        print(f"ISOLATION CHECK FAILED — {len(fails)} problem(s)\n")
        for f in fails:
            print(f"  ✗ {f}")
        sys.exit(1)
    print("isolation OK")
    print(f"  no HERE-relative data paths in crm/ or dashboard/")
    print(f"  {len(GUARDED)} guarded live files byte-identical after a full seed")
