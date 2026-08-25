#!/usr/bin/env python3
"""yourco — the seven numbers that existed only as prose, made readable.

On 2026-08-25 every agent was given one number to own (`dashboard/northstar.py`). Twenty-one came
back unmeasured, and the largest cluster — **seven** — shared one cause: *the loop already produces
the number and then writes it into a memo nothing can read.* This module closes that cluster.

TWO MECHANISMS, AND THE LINE BETWEEN THEM MATTERS
- **Derived** — the number is a fact about files that already exist, computed here from scratch.
  Nothing has to run first and nothing can go stale. Three of the seven turned out to be this, which
  means the original diagnosis was partly wrong: the data was already machine-readable and nobody
  had pointed at it.
- **Extracted** — only the loop's own run knows the number, so it is read back out of the artifact
  that run wrote. This is only safe because the structures parsed here are **SOP-mandated**, not
  free prose: the eval scoreboard's header is byte-identical across all six runs, and the AEO score
  has sat under the same `## Citation-presence score` heading since the first one. The same pattern
  `dashboard/board.py` already uses on `processes/counsel-gates.md`.

THE RULE THAT MAKES EXTRACTION HONEST. **A structure that does not parse reports a parse failure —
never a zero.** A metric that silently reads 0 when a heading gets renamed is worse than one that
reads blank, because 0 looks like an answer. Every function here returns `(None, unit, why)` on any
doubt, and every value it does return names the file and the date it came from, so a number from a
six-week-old artifact cannot pass as current.

WHAT THIS DELIBERATELY DOES NOT DO
- **No backfilling.** Nothing invents a score for a run that did not state one.
- **No writing.** There is no store, no schedule and no second copy: every value is computed on read
  from the artifact the loop already commits. A store would have needed a writer, a cadence, and a
  staleness policy to hold numbers that are already sitting in git.
- **No prose parsing.** Luka's is the one that stays blank, because the brand audit records a verdict
  and no review *volume* — and inferring a count from a sentence is exactly the fragility this
  module exists to avoid. That one is fixed where it belongs: a required line in the SOP and prompt,
  read here the moment a run writes it.

Read-only. Consumed by `dashboard/northstar.py`. CLI: `python3 dashboard/loop_metrics.py`
"""
import os, re, sys, glob, json, datetime, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
ROOT = os.environ.get("YOURCO_DATA_ROOT") or REPO

# An artifact older than this is still reported, but the note says how old it is. A monthly loop's
# number is not stale at 40 days; the reader decides, and the reader can only decide if told.
DATED = re.compile(r"(\d{4}-\d{2}-\d{2})")


def _read(rel, base=None):
    try:
        with open(os.path.join(base or REPO, rel), encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def _latest(dirrel, pattern=r"\d{4}-\d{2}(-\d{2})?\.md"):
    """Newest dated artifact in a loop folder, by filename. Returns (relpath, date-ish) or (None, None).
    Filename order is the source of truth, not mtime — a git checkout rewrites every mtime."""
    d = os.path.join(REPO, dirrel)
    try:
        names = sorted(n for n in os.listdir(d) if re.fullmatch(pattern, n))
    except OSError:
        return None, None
    if not names:
        return None, None
    return os.path.join(dirrel, names[-1]), names[-1][:-3]


def _age(datestr):
    m = DATED.search(datestr or "")
    if not m:
        return None
    try:
        return (datetime.date.today() - datetime.date.fromisoformat(m.group(1))).days
    except ValueError:
        return None


def _seen(rel, when):
    """`file (Nd ago)` — plus a STALE warning when the artifact is past twice its own cadence.

    The warning is baked into the note rather than returned separately, so it travels with the
    number to every surface that renders it. A 44-day-old figure from a weekly loop is not wrong;
    it is *old*, and those are different words that a bare value cannot say. Cadences come from
    `dashboard/board.py` — the same table that decides whether a loop has gone dark, never a second
    copy that could disagree with it."""
    a = _age(when)
    if a is None:
        return os.path.basename(rel)
    import board
    cad = board._cadence_for(os.path.basename(os.path.dirname(rel)).lstrip("_"))
    warn = f" ⚠ STALE — cadence is {cad}d" if a > cad * 2 else ""
    return f"{os.path.basename(rel)} ({a}d ago){warn}"


# ── DERIVED ─────────────────────────────────────────────────────────────────────────────────
def counsel_gates_open():
    """Ray. Gates that are not cleared.

    Not extracted and not new: `processes/counsel-gates.md` is a table that BOTH
    `dashboard/refresh.py` and `dashboard/board.py` already parse. The number was machine-readable
    all along and no metric pointed at it — which is why "blocked by prose" was the wrong diagnosis
    here, and worth saying plainly rather than quietly fixing."""
    import refresh
    g = (refresh._gates() or {}).get("counsel") or {}
    total, cleared = g.get("total") or 0, g.get("cleared") or 0
    if not total:
        return None, "open", "processes/counsel-gates.md has no gate table — nothing to count"
    return total - cleared, "open", (f"{cleared} of {total} cleared · {g.get('blockedHard', 0)} hard-blocked"
                                    f" · {g.get('awaitingCounsel', 0)} awaiting counsel")


def _citation_body():
    """Everything in decisions/ and rejections/ concatenated — the corpus a memo is 'adopted' into."""
    body = []
    for pat in ("decisions/*.md", "rejections/*.md"):
        for p in glob.glob(os.path.join(REPO, pat)):
            body.append(_read(os.path.relpath(p, REPO)))
    return "\n".join(body)


def _adoption(dirs, body):
    """Memos cited by at least one decision or rejection, over memos written.

    This is the precedent-graph pattern — the one idea worth stealing from Semantica without
    installing it (`decisions/2026-08-25_one-number-and-agent-metrics.md`). Citing the *file* is
    already how this repo records that a recommendation became a call, so adoption is countable
    from history rather than from a new habit nobody would keep."""
    memos = []
    for d in dirs:
        for p in sorted(glob.glob(os.path.join(REPO, d, "*.md"))):
            if not os.path.basename(p).startswith("_"):
                memos.append(os.path.relpath(p, REPO))
    cited = [m for m in memos if m in body]
    return memos, cited


def recommendations_adopted():
    """Brett. An advisor who is never acted on is an expensive newsletter."""
    memos, cited = _adoption(("loops/advisor", "loops/brett-ideas", "loops/_advisory"),
                             _citation_body())
    if not memos:
        return None, "%", "no advisor memos on disk"
    return (round(len(cited) / len(memos) * 100), "%",
            f"{len(cited)} of {len(memos)} memos cited by a decision or rejection")


def initiatives_adopted():
    """Melanie. Deliberately a COUNT and deliberately a FLOOR.

    The conductor may propose and may never self-adopt, so adoption is the only evidence her
    judgment is converging on the Founder's. But a move the Founder simply *did*, without writing a decision that
    cites the run, is invisible here — so this is a floor, not a rate, and it is reported as one.
    The contrast with Brett is the useful part: the same mechanism finds 9 of his memos, so a 0 here
    is more likely real than instrumental."""
    memos, cited = _adoption(("loops/initiative",), _citation_body())
    if not memos:
        return None, "adopted", "no initiative artifacts on disk"
    return (len(cited), "adopted",
            f"FLOOR — {len(cited)} of {len(memos)} runs cited by a decision; a move the Founder acted on "
            f"without writing one is invisible here")


# ── EXTRACTED ───────────────────────────────────────────────────────────────────────────────
def registry_drift_open():
    """Rafi. Read from the watchdog's own report rather than re-run here, deliberately.

    `runtime/agent-registry-check.py --live` sees the host: installed units, the ACTIVE approval
    gate, crontab. Re-deriving the number inside HQ would silently drop every host finding and
    report a smaller, friendlier number from a machine that cannot see the VPS."""
    rel, when = _latest("loops/_governance")
    if not rel:
        return None, "open", "no governance report has ever been written"
    md = _read(rel)
    if "✅ clean" in md:
        return 0, "open", f"clean — {_seen(rel, when)}"
    if "⚠️ DRIFT" not in md:
        return None, "open", (f"{os.path.basename(rel)} states neither a clean nor a drift result — "
                              f"the report format changed; not guessing")
    rows = re.findall(r"^\|\s*(DRIFT|MISSING)\s*\|", md, re.M)
    if not rows:
        return None, "open", (f"{os.path.basename(rel)} reports DRIFT but its finding table did not "
                              f"parse — a count of 0 here would contradict the report's own verdict")
    return len(rows), "open", f"{len(rows)} finding(s) — {_seen(rel, when)}"


def eval_pass_rate():
    """Kolby. Outputs scored with no zero on any rubric dimension, over outputs scored.

    The rubric is six dimensions at 2/1/0 and **any 0 is a fail** (`processes/eval-rubric.md`) — so
    a pass is 'no zero', not 'a perfect 12'. Reading the Total column instead would quietly
    reclassify every honest 11 as a failure."""
    rel, when = _latest("loops/eval-review")
    if not rel:
        return None, "%", "no eval review has ever been written"
    import board
    rows = board._tables(_read(rel), r"^scoreboard")
    scored = [r for r in rows if len(r) >= 8 and r[0].strip()]
    if not scored:
        return None, "%", (f"the scoreboard table in {os.path.basename(rel)} did not parse — the "
                           f"format moved. A rate of 0 here would read as total failure.")
    passed = 0
    for r in scored:
        dims = [re.sub(r"\D", "", c) for c in r[1:7]]
        if any(d == "" for d in dims):
            return None, "%", (f"a scoreboard row in {os.path.basename(rel)} has non-numeric rubric "
                               f"cells — refusing a rate computed off a partly-read table")
        if "0" not in dims:
            passed += 1
    return (round(passed / len(scored) * 100), "%",
            f"{passed} of {len(scored)} outputs clean on all six dimensions — {_seen(rel, when)}")


def citation_presence():
    """Mario. The score his own SOP already computes and already writes under a fixed heading."""
    rel, when = _latest("loops/aeo-geo")
    if not rel:
        return None, "%", "no AEO/GEO run has ever been written"
    md = _read(rel)
    m = re.search(r"^##\s*Citation-presence score\s*$\n+\**\s*(\d+(?:\.\d+)?)\s*%", md, re.M)
    if not m:
        return None, "%", (f"{os.path.basename(rel)} carries no parseable score under "
                           f"'## Citation-presence score' — the SOP requires one; not inferring it")
    return float(m.group(1)), "%", f"{_seen(rel, when)} — 0% is correct while nothing is published"


def brand_first_pass():
    """Luka. The one that stays blank, and the reason is the finding.

    A first-time-pass RATE needs a denominator, and the brand audit records a verdict but never a
    review *volume* — its own 2026-08 run says zero assets were queued for pre-ship review, two
    months running, which means Luka is catching drift after the fact rather than at ship. Inferring
    that count from a sentence is exactly the fragility this module refuses. The fix is a required
    `## Review volume` line in the SOP and the prompt; this reads it the moment a run writes one."""
    rel, when = _latest("loops/brand-audit")
    if not rel:
        return None, "%", "no brand audit has ever been written"
    md = _read(rel)
    m = re.search(r"^##\s*Review volume\s*$\n+\**\s*(\d+)\s*\**\s*reviewed\D+(\d+)\s*\**\s*cleared",
                  md, re.M | re.I)
    if not m:
        return None, "%", (f"{os.path.basename(rel)} records a verdict but no '## Review volume' "
                           f"line — required by the SOP since 2026-08-25; the next monthly run "
                           f"writes the first one")
    reviewed, cleared = int(m.group(1)), int(m.group(2))
    if not reviewed:
        return None, "%", (f"0 assets reviewed pre-ship — {_seen(rel, when)}. A first-pass rate over "
                           f"zero reviews is undefined, and the zero is the finding: drift is being "
                           f"caught after ship, not at it.")
    return round(cleared / reviewed * 100), "%", f"{cleared} of {reviewed} — {_seen(rel, when)}"


METRICS = {
    "counselGatesOpen": counsel_gates_open,
    "recommendationsAdopted": recommendations_adopted,
    "initiativesAdopted": initiatives_adopted,
    "registryDriftOpen": registry_drift_open,
    "evalPassRate": eval_pass_rate,
    "citationPresence": citation_presence,
    "brandFirstPass": brand_first_pass,
}
# Which mechanism each one uses — rendered on HQ, because "computed from files that already exist"
# and "read back out of what a run wrote" have very different failure modes and the reader of a
# number deserves to know which one they are looking at.
MECHANISM = {
    "counselGatesOpen": "derived", "recommendationsAdopted": "derived", "initiativesAdopted": "derived",
    "registryDriftOpen": "extracted", "evalPassRate": "extracted", "citationPresence": "extracted",
    "brandFirstPass": "extracted",
}


def main():
    print("\n=== the seven that were prose ==================================================")
    for k, fn in METRICS.items():
        v, unit, note = fn()
        shown = "—" if v is None else f"{v}{'%' if unit == '%' else ' ' + unit}"
        print(f"  {k:<26} {MECHANISM[k]:<10} {shown:>10}   {note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
