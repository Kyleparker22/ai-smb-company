#!/usr/bin/env python3
"""kb — search everything yourco knows, and say how much to trust each answer.

    python3 runtime/kb.py "connector override"
    python3 runtime/kb.py "what did we decide about self-serve" --limit 15
    python3 runtime/kb.py "trust ledger" --level real       # only REAL-tier sources
    python3 runtime/kb.py "audit" --json

WHY THIS EXISTS
The repo is the company's brain — 1,250 text files, ~7.4 MB — and until 2026-08-24 there was no way
to search it. Retrieval was `grep`, plus two deliberately narrow matchers (learning_triggers,
rejections) that only see their own folders. Asking "what do we know about X" meant guessing which
folder X lived in.

WHY NOT EMBEDDINGS
7.4 MB is small. A deterministic index answers in well under a second, costs nothing, and returns
the same result twice — which a model call does not. `learnings/ops/2026-08-09_inference-only-where-
judgment-is-needed.md` is explicit: deterministic work wrapped in an LLM call costs tokens AND is
less reliable. Search is retrieval, not judgment. If semantic recall is ever genuinely needed, that
is a separate decision with its own trip-wire — not a default.

THE THING THIS DOES THAT GREP CANNOT: REALITY LEVELS
`00_README.md` opens with the warning that several folders look alike and mean completely different
things — "get this wrong and you will treat a prototype as a product." A flat search makes that
mistake *easier*, because a confident hit in `Pre Build Ideas/` reads exactly like a confident hit in
`clients/`. So every result is TAGGED and RANKED by what it actually is:

    REAL       clients/, crm/, finance/          an engagement, a number, a real record
    DOCTRINE   00-07 spine, CLAUDE.md, processes/, .claude/skills/
    DECIDED    decisions/, rejections/, learnings/   settled calls, refusals, observed patterns
    BUILT      Pre Build Ideas/, app/, dashboard/    built, unsold
    DESCRIBED  offerings/                        argued, never built
    RECORD     loops/, daily-logs/               dated artifacts — true when written
    DEAD       _archive/                         history only; never cite for current state

A DEAD hit is never promoted above a live one, and the level is printed next to every result. The
ranking is a stated opinion about trust, not relevance alone — which is the honest thing for a
company whose reality levels are the first thing its own front door warns about.
"""
import os, re, sys, json, math, argparse, subprocess
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".obsidian", "venv", ".venv"}
EXT = (".md", ".txt")

# (level, weight, prefixes). Weight multiplies the text score — it encodes how much a hit here
# should be trusted, which is a different question from how well it matches.
LEVELS = [
    ("REAL",      1.35, ("clients/", "crm/", "finance/")),
    ("DOCTRINE",  1.30, ("00_README.md", "01_", "02_", "03_", "04_", "05_", "06_", "07_",
                         "CLAUDE.md", "processes/", ".claude/skills/")),
    ("DECIDED",   1.20, ("decisions/", "rejections/", "learnings/")),
    ("BUILT",     1.00, ("Pre Build Ideas/", "app/", "dashboard/", "runtime/", "playground/")),
    ("DESCRIBED", 0.85, ("offerings/",)),
    ("RECORD",    0.70, ("loops/", "daily-logs/")),
    ("DEAD",      0.25, ("_archive/",)),
]
LEVEL_ORDER = [l[0] for l in LEVELS]

# Words that match half the repo and rank nothing. A query made only of these is refused rather than
# answered with noise — the same posture every HQ panel takes.
STOP = set("""the a an and or of to in is it for on with that this these those as at by be are was
were from not no we our us you your yourco the Founder if then than so but can will would should may
one two all any each per via into out up down more most other some such only own same then""".split())

WORD = re.compile(r"[a-z0-9][a-z0-9\-_.']*")


def level_of(rel):
    for name, weight, prefixes in LEVELS:
        if any(rel.startswith(p) for p in prefixes):
            return name, weight
    return "BUILT", 0.9          # unclassified top-level file: neutral, slightly below BUILT


def corpus():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".git")]
        for fn in filenames:
            if not fn.endswith(EXT):
                continue
            fp = os.path.join(dirpath, fn)
            rel = os.path.relpath(fp, ROOT)
            try:
                yield rel, open(fp, encoding="utf-8", errors="replace").read()
            except OSError:
                continue


def _headings(body):
    return " ".join(re.findall(r"^#{1,4}\s+(.+)$", body, re.M)[:40]).lower()


def search(query, limit=10, level=None, min_score=0.0):
    terms = [t for t in WORD.findall(query.lower()) if t not in STOP and len(t) > 1]
    if not terms:
        return {"query": query, "refused": True,
                "why": "every word in that query is a stop-word or too short — it would match "
                       "most of the repo. Add a distinguishing term.", "hits": []}
    want = level.upper() if level else None
    hits = []
    for rel, body in corpus():
        low = body.lower()
        counts = {t: low.count(t) for t in terms}
        present = [t for t, c in counts.items() if c]
        if not present:
            continue
        # every term present is worth far more than one term many times — that is the difference
        # between a document about the topic and one that mentions a word.
        coverage = len(present) / len(terms)
        if coverage < (1.0 if len(terms) == 1 else 0.5):
            continue
        lvl, weight = level_of(rel)
        if want and lvl != want:
            continue
        head = _headings(body)
        name = rel.lower()
        raw = sum(1 + math.log(c) for c in counts.values() if c)
        bonus = 1.0
        if any(t in name for t in present):
            bonus += 0.9            # the filename is about this
        if any(t in head for t in present):
            bonus += 0.5            # a heading is about this
        score = raw * coverage * bonus * weight
        if score < min_score:
            continue
        hits.append({"path": rel, "level": lvl, "score": round(score, 2),
                     "coverage": round(coverage, 2), "hits": sum(counts.values()),
                     "line": _first_line(body, present)})
    hits.sort(key=lambda h: (-h["score"], LEVEL_ORDER.index(h["level"]), h["path"]))
    return {"query": query, "terms": terms, "refused": False,
            "total": len(hits), "hits": hits[:limit]}


def _first_line(body, terms):
    """The most informative line containing a term — the one with the most of them."""
    best, best_n = "", 0
    for ln in body.splitlines():
        low = ln.lower()
        n = sum(1 for t in terms if t in low)
        if n > best_n and len(ln.strip()) > 25:
            best, best_n = ln.strip(), n
            if n == len(terms):
                break
    return re.sub(r"\s+", " ", best)[:220]


def main():
    ap = argparse.ArgumentParser(description="Search everything yourco knows.")
    ap.add_argument("query", nargs="+")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--level", help="restrict to one reality level: " + " ".join(LEVEL_ORDER))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    res = search(" ".join(a.query), limit=a.limit, level=a.level)
    if a.json:
        print(json.dumps(res, indent=2)); return
    if res["refused"]:
        print(f'REFUSED — {res["why"]}'); sys.exit(2)
    print(f'{res["total"]} match(es) for {res["terms"]}  — showing {len(res["hits"])}\n')
    for h in res["hits"]:
        print(f'  [{h["level"]:<9}] {h["path"]}   ({h["hits"]} hits, score {h["score"]})')
        if h["line"]:
            print(f'              {h["line"]}')
    if not res["hits"]:
        print("  nothing. That is a real answer — the repo may simply not know.")
    dead = [h for h in res["hits"] if h["level"] == "DEAD"]
    if dead:
        print(f'\n  ⚠️  {len(dead)} result(s) are in _archive/ — history only, never cite for current state.')


if __name__ == "__main__":
    main()
