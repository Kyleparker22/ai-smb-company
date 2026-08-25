#!/usr/bin/env python3
"""Documents that declare their own checks.

    python3 runtime/doc_claims.py            # verify every annotated claim
    python3 runtime/doc_claims.py --list     # show them all with their computed values
    python3 runtime/doc_claims.py --json

WHY THIS EXISTS
Eleven folder reviews on 2026-08-24 found the same shape every time: the CONTENT was good and the
INDEX describing it was stale. "34 entries" when there were 33, "ten doors" when there were eleven,
"71 prototypes" when there were 76. Each was fixed by hand and then guarded by adding a tuple to a
hardcoded table inside runtime/consistency-check.py.

That table works and it does not scale. Guarding the 28th claim costs a Python edit, so coverage
only grows when somebody notices drift by eye — which is the loop this is supposed to end. Worse,
the guard lives in a different file from the claim, so the person writing "76 prototypes" has to
know the table exists.

So the claim carries its own check, on the same line, in the same edit:

    **76** working prototypes <!--#count: files Pre Build Ideas/*/BUILD.md-->
    HQ's **11** doors <!--#count: match dashboard/index.html /data-v="([a-z-]+)"/-->

An HTML comment is invisible in rendered markdown and in a browser, so the annotation costs the
reader nothing.

THE GRAMMAR — four verbs, deliberately few

    files <glob>                 files matching the glob
    dirs  <glob>                 directories matching the glob
    match <path> /<regex>/       UNIQUE capture-group-1 matches in that file (or group 0 if none)
    suite <path>                 assertions a test file reports: "N passed, M failed" -> N+M

A claim is the number immediately before the annotation — digits (`76`) or a written word
(`eleven`), so prose does not have to be contorted to be checkable.

WHAT THIS DELIBERATELY DOES NOT DO
It never edits a document. A wrong number is reported, never silently corrected: the number might
be right and the glob wrong, and a self-healing doc would hide that. Everything here is read-only.
"""
import os, re, sys, json, glob, argparse, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", "_archive", "loops", "daily-logs", "node_modules", "__pycache__", "data"}
# Append-only records. Their citations were accurate the day they were written; rewriting one to
# keep a checker quiet would falsify the record, so they are not scanned as CITERS. (They are still
# valid TARGETS — a live doc may cite a decision, and that citation must resolve.)
RECORD_DIRS = {"decisions", "loops", "daily-logs", "_archive"}
SCAN_EXT = (".md", ".html", ".txt")

ANNOT = re.compile(r"<!--\s*#count:\s*(.+?)\s*-->", re.S)

# A path in backticks: `processes/loops/watchdog.md`. Only paths with a slash — a bare filename is
# ambiguous (there are four README.md) and would produce noise, which is how a check gets ignored.
CITE = re.compile(r"`([A-Za-z0-9_][A-Za-z0-9_./ -]*\.(?:md|py|json|sh|html|js|css|txt|xlsx|service|timer))`")
# Legitimate non-paths that look like paths:
#   placeholders  `clients/<client>/weekly/YYYY-MM-DD.md`   — a shape, not a file
#   commands      `python3 runtime/test_evidence.py`        — an instruction
#   globs         `loops/*/artifact.md`
CITE_SKIP = re.compile(r"YYYY|MM-DD|<[a-z]|\*|\s")
# A doc may cite a file that does not exist YET and be right to: an unchecked deliverable, a test
# fixture describing an adversarial scenario, a pricing doc Polo still owes. The checker cannot tell
# those from rot, so the DOCUMENT says so — `<!--#planned-->` anywhere on the same line. Explicit,
# greppable, and it lets this check reach zero, which is the only state a check is trusted in.
PLANNED = re.compile(r"<!--\s*#planned\s*-->")
# A backticked path TRUNCATED with an ellipsis: `learnings/ops/2026-06-11_...`. CITE cannot see these —
# it requires a real extension — so they are invisible to the dead-citation check while reading to a
# human exactly like provenance. Added 2026-08-24 after one was written into a new skill and caught by
# chance rather than by the checker. Records are exempt as citers like everything else here: a
# truncated path in a dated artifact was accurate the day it was written.
ELLIPSIS_CITE = re.compile(r"`([A-Za-z0-9_][A-Za-z0-9_./-]*/[A-Za-z0-9_.-]*\.\.\.)`")
WORDS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
    "fifteen sixteen seventeen eighteen nineteen twenty".split())}


def _claimed_number(text_before):
    """The number this annotation is attached to: the last digits or number-word before it."""
    tail = text_before[-160:]
    m = list(re.finditer(r"(\d{1,6})|\b([A-Za-z]+)\b", tail))
    for tok in reversed(m):
        if tok.group(1):
            return int(tok.group(1)), tok.group(1)
        w = tok.group(2).lower()
        if w in WORDS:
            return WORDS[w], tok.group(2)
    return None, None


def compute(spec):
    """(value, error). A spec that cannot be evaluated is an ERROR, never a silent zero —
    a broken glob returning 0 would read as 'the folder emptied', which is a different fact."""
    parts = spec.split(None, 1)
    if not parts:
        return None, "empty spec"
    verb, rest = parts[0], (parts[1] if len(parts) > 1 else "")
    try:
        if verb == "files":
            hits = [p for p in glob.glob(os.path.join(ROOT, rest), recursive=True) if os.path.isfile(p)]
            return len(hits), None
        if verb == "dirs":
            hits = [p for p in glob.glob(os.path.join(ROOT, rest), recursive=True) if os.path.isdir(p)]
            return len(hits), None
        if verb == "match":
            m = re.match(r"(\S+)\s+/(.+)/\s*$", rest, re.S)
            if not m:
                return None, "match needs: <path> /<regex>/"
            path, rx = m.group(1), m.group(2)
            fp = os.path.join(ROOT, path)
            if not os.path.exists(fp):
                return None, f"no such file: {path}"
            body = open(fp, encoding="utf-8", errors="replace").read()
            found = re.findall(rx, body, re.M)
            if found and isinstance(found[0], tuple):
                found = [f[0] for f in found]
            return len(set(found)), None
        if verb == "suite":
            fp = os.path.join(ROOT, rest)
            if not os.path.exists(fp):
                return None, f"no such file: {rest}"
            out = subprocess.run([sys.executable, fp], capture_output=True, text=True,
                                 timeout=180, cwd=ROOT).stdout
            m = re.search(r"(\d+) passed, (\d+) failed", out)
            if not m:
                return None, "suite printed no 'N passed, M failed' line"
            return int(m.group(1)) + int(m.group(2)), None
        return None, f"unknown verb '{verb}' (files | dirs | match | suite)"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def _toplevel(root=ROOT):
    return {d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))} | {".claude"}


_TOPLEVEL = _toplevel()


def citations(root=ROOT):
    """Every `path/to/file.ext` in backticks that resolves to nothing.

    Added 2026-08-24 after a repo-wide scan: 2,748 such citations across 956 markdown files, of
    which 49 pointed at nothing. A dead citation is worse than no citation — it reads as provenance,
    so the next reader trusts a reason they cannot open. Resolution is tried from the repo root AND
    from the citing file's own directory, because both are how people write them.
    """
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".git")]
        _top = os.path.relpath(dirpath, root).split(os.sep)[0]
        if _top in SKIP_DIRS or _top in RECORD_DIRS:
            continue
        for fn in filenames:
            if not fn.endswith(SCAN_EXT):
                continue
            fp = os.path.join(dirpath, fn)
            try:
                body = open(fp, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            for cited in set(CITE.findall(body)):
                if "/" not in cited or CITE_SKIP.search(cited):
                    continue
                # Only repo-rooted citations are checkable. `demo/end.html` written inside a
                # Sample Client production note is relative to the SUBJECT, not to the file or the
                # root — a human reads it correctly in context and no resolver can. Requiring the
                # first segment to be a real top-level folder drops ~32 such cases that were pure
                # noise, and noise is how a check gets ignored.
                if cited.split("/")[0] not in _TOPLEVEL:
                    continue
                if os.path.exists(os.path.join(root, cited)):
                    continue
                if os.path.exists(os.path.join(dirpath, cited)):
                    continue
                # is every line citing it marked #planned?
                lines = [ln for ln in body.splitlines() if "`" + cited + "`" in ln]
                if lines and all(PLANNED.search(ln) for ln in lines):
                    continue
                out.append({"file": os.path.relpath(fp, root), "cited": cited})
            for trunc in set(ELLIPSIS_CITE.findall(body)):
                out.append({"file": os.path.relpath(fp, root), "cited": trunc,
                            "truncated": True})
    return sorted(out, key=lambda r: (r["cited"], r["file"]))


def scan(root=ROOT):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Record dirs are entered but only their `_README.md` is read (see below); everything else in
        # SKIP_DIRS is pruned here and never walked.
        _keep = SKIP_DIRS - RECORD_DIRS
        dirnames[:] = [d for d in dirnames if d not in _keep and not d.startswith(".git")]
        rel_top = os.path.relpath(dirpath, root).split(os.sep)[0]
        if rel_top in SKIP_DIRS:
            # ONE narrow exception, added 2026-08-24: a `_README.md` inside a record folder is
            # documentation ABOUT the records, not a record. `loops/_README.md` describes 44 live
            # subfolders and had gone months out of date; annotating its counts is exactly right, and
            # skipping the whole tree meant those annotations silently did nothing — which is worse
            # than a plain number, because an annotation implies it was checked. The dated artifacts
            # beside it are still skipped, and still must never be rewritten.
            filenames = [f for f in filenames if f == "_README.md"]
            if not filenames:
                continue
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for fn in filenames:
            if not fn.endswith(SCAN_EXT):
                continue
            fp = os.path.join(dirpath, fn)
            try:
                body = open(fp, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            if "#count:" not in body:
                continue
            for m in ANNOT.finditer(body):
                spec = " ".join(m.group(1).split())
                claimed, raw = _claimed_number(body[:m.start()])
                value, err = compute(spec)
                out.append({
                    "file": os.path.relpath(fp, root),
                    "line": body[:m.start()].count("\n") + 1,
                    "spec": spec,
                    "claimed": claimed,
                    "claimed_raw": raw,
                    "actual": value,
                    "error": err,
                    "ok": (err is None and claimed is not None and claimed == value),
                })
    return sorted(out, key=lambda r: (r["file"], r["line"]))


def report(rows):
    bad = [r for r in rows if not r["ok"]]
    return {
        "total": len(rows),
        "ok": len(rows) - len(bad),
        "problems": [
            {**r, "why": (r["error"] if r["error"]
                          else "no number found before the annotation" if r["claimed"] is None
                          else f"says {r['claimed_raw']}, actual {r['actual']}")}
            for r in bad
        ],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--cites", action="store_true", help="only the dead-citation report")
    a = ap.parse_args()
    rows = scan()
    rep = report(rows)
    cites = citations()
    rep["dead_citations"] = cites
    if a.json:
        print(json.dumps(rep, indent=2)); return
    print(f"DOC CLAIMS — {rep['ok']}/{rep['total']} verified")
    if a.list:
        for r in rows:
            mark = "ok " if r["ok"] else "✗  "
            print(f"  {mark} {r['file']}:{r['line']}  {r['claimed_raw']} "
                  f"(actual {r['actual']})  ← {r['spec']}")
    for p in rep["problems"]:
        print(f"  ✗ {p['file']}:{p['line']} — {p['why']}   [{p['spec']}]")
    print(f"\nDEAD CITATIONS — {len(cites)}")
    from collections import Counter
    for cited, n in Counter(c["cited"] for c in cites).most_common(15 if a.list else 8):
        who = [c["file"] for c in cites if c["cited"] == cited]
        print(f"  ✗ {cited}   cited by {n}: {', '.join(who[:3])}{' …' if n > 3 else ''}")
    sys.exit(1 if (rep["problems"] or cites) else 0)


if __name__ == "__main__":
    main()
