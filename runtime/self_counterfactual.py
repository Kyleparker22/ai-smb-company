#!/usr/bin/env python3
"""The public counterfactual — yourco as it would run without the thing yourco sells.

Every software company claims it uses its own product. Nobody publishes the half that would
actually persuade: *what would this company look like if it didn't?* Almost nobody can compute it.
yourco can, because the work its OS does is recorded — so this runs the counterfactual on yourco
itself and publishes the result.

    This is the company with the system. This is the modelled company without it.

WHY THIS IS THE ONLY PROOF AVAILABLE. At n=0 clients there are no case studies, no logos, and no
outcome metrics that aren't zero. The one dataset yourco owns outright is its own operations. That
makes this the strongest honest artifact on the site and the endgame of the glass-box page: that
page says *we run our company on this*; this one says *and here is the company we'd be without it*
— which is the question the buyer is actually asking about their own business.

THE LABEL THAT NEVER COMES OFF — inherited verbatim from `runtime/counterfactual.py`, because a
second, laxer standard for the version we publish would be exactly backwards:
  **A counterfactual is a model, not a measurement.** Nobody observed the company that didn't
  happen. Every row carries `isModel: true` and the assumption it rests on.

WHAT IT REFUSES, AND WHY THE REFUSALS ARE THE POINT
- **Hours saved: excluded.** `dashboard/trust.py` already refuses to convert recorded actions into
  hours without a time study, and no time study exists. So the single number this page would most
  like to print is the one it cannot have. It says so instead of estimating — an invented hours
  figure here would discredit every real number around it.
- **Money saved: excluded.** No pre-OS baseline was captured. You cannot reconstruct a baseline
  after the fact, which is precisely why yourco captures a client's at discovery.
- **Anything volume-shaped: excluded.** Clients, revenue, pipeline. Pre-revenue is pre-revenue.
- A metric with no measured actual is **named and excluded**, never assumed flat.

WHAT IT WILL STATE. Work that demonstrably happened without a human, counted from the record: loop
artifacts produced, actions logged, scheduled jobs, the span they cover. The counterfactual for
each is not "this much money" — it is *this work would not exist, or a solo founder would be doing
it by hand at a cadence a person can actually sustain.* That cadence is an assumption, and it is
stated on the row rather than buried.

  python3 runtime/self_counterfactual.py            # write without.json
  python3 runtime/self_counterfactual.py --print    # stdout, write nothing
"""
import os, re, sys, json, subprocess, datetime, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = os.path.join(ROOT, "agents", "webb", "pages", "yourco-site-v2")
OUT = os.path.join(SITE, "without.json")

LOOPS = os.path.join(ROOT, "loops")
ACTIONS = os.path.join(LOOPS, "_trust", "actions.jsonl")
REGISTRY = os.path.join(HERE, "agent-registry.json")

# The one assumption the whole model rests on, stated once, in public, in plain words.
# A solo founder does not run a weekly review cadence across thirty domains. The honest
# counterfactual for a scheduled review is not "slower" — it is "did not happen".
SOLO_CADENCE_NOTE = (
    "A solo founder does not run this many separate review cadences by hand. The model does not "
    "assume the same work happening slower; it assumes most of it does not happen at all, which "
    "is what actually occurs in a one-person company. That is an assumption about human behaviour, "
    "not a measurement, and it is the load-bearing one on this page."
)


def _read_actions():
    rows, bad = [], 0
    try:
        with open(ACTIONS, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    bad += 1
    except OSError as e:
        raise RuntimeError(f"the action ledger could not be read: {e}")
    return rows, bad


def _loop_artifacts():
    """Dated artifacts under loops/ — one per run, per loop. The physical record of work done."""
    found = []
    for dirpath, _dirs, files in os.walk(LOOPS):
        for n in files:
            if re.match(r"^\d{4}-\d{2}-\d{2}", n) and n.endswith(".md"):
                found.append((os.path.basename(dirpath), n[:10]))
    return found


def _timers():
    with open(REGISTRY, encoding="utf-8") as f:
        return json.load(f).get("sanctioned_timers") or []


def row(metric, actual, without, assumption, unit="", lower_is_better=False):
    return {"metric": metric, "actual": actual, "without": without, "unit": unit,
            "assumption": assumption, "isModel": True, "lowerIsBetter": lower_is_better}


def build(today=None):
    today = today or datetime.date.today()
    rows, excluded, notes = [], [], []

    # ── what actually happened, counted from the record ─────────────────────────────────────
    try:
        acts, bad = _read_actions()
        if bad:
            notes.append(f"{bad} unreadable line(s) in the action ledger — counted as unreadable, "
                         f"not as successes.")
        days = sorted({a.get("on") for a in acts if a.get("on")})
        loops_seen = {a.get("loop") for a in acts if a.get("loop")}
        rows.append(row(
            "Actions taken with no human present", len(acts), 0,
            "Every one is an action a scheduled job took on its own, recorded at the time. Without "
            "the OS the count is zero by definition — there is nothing to take them. This row is "
            "the least modelled thing on the page.",
            unit="actions"))
        if days:
            notes.append(f"The action record runs {days[0]} to {days[-1]} across "
                         f"{len(loops_seen)} distinct loops.")
    except Exception as e:
        excluded.append({"metric": "Actions taken with no human present",
                         "why": f"the action ledger could not be read ({e})"})

    arts = _loop_artifacts()
    if arts:
        first = min(d for _l, d in arts)
        rows.append(row(
            "Recurring reviews actually produced", len(arts), 0,
            "Each is a dated artifact written by a scheduled run — a review that happened and left "
            "a document. The counterfactual is zero rather than 'fewer': " + SOLO_CADENCE_NOTE,
            unit="artifacts"))
        notes.append(f"The oldest surviving loop artifact is dated {first}.")
    else:
        excluded.append({"metric": "Recurring reviews actually produced",
                         "why": "no dated loop artifacts found on disk"})

    try:
        t = _timers()
        rows.append(row(
            "Review cadences running on a schedule", len(t), 0,
            "Read from the sanctioned registry. Without the OS a solo founder keeps some of these "
            "in their head and drops the rest; the model does not pretend to know which, so it "
            "states zero scheduled and says the difference is judgement, not arithmetic.",
            unit="scheduled jobs"))
    except Exception as e:
        excluded.append({"metric": "Review cadences running on a schedule",
                         "why": f"the registry could not be read ({e})"})

    # ── the refusals. These are not omissions; printing them is the point. ──────────────────
    excluded.append({
        "metric": "Hours of founder time saved",
        "why": "No time study exists, so there is no measured minutes-per-action to multiply by. "
               "yourco's own trust ledger already refuses to convert recorded actions into hours "
               "for this reason, and this page will not do quietly what that module refuses to do "
               "openly. It is the number we would most like to show you and the one we have least "
               "right to."})
    excluded.append({
        "metric": "Money saved",
        "why": "No pre-OS baseline was captured. A baseline cannot be reconstructed after the "
               "fact — which is exactly why a client's is captured at discovery, before anything "
               "is built."})
    excluded.append({
        "metric": "Clients, revenue, pipeline",
        "why": "yourco is pre-revenue. There is no version of this comparison that is not zero on "
               "both sides, so it is left off rather than dressed up."})

    return {
        "generatedAt": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "generatedOn": today.isoformat(),
        "isModel": True,
        # Sentence case on purpose: the page already carries the uppercase label in its own pill,
        # and DESIGN.md §2 forbids all-caps body copy. Shouting it twice reads as anxiety, not rigour.
        "label": ("Nobody observed the version of yourco that did not build this. Every row below "
                  "states the assumption it rests on, and the ones we refuse to model are listed too."),
        "subject": "yourco",
        "rows": rows,
        "excluded": excluded,
        "notes": notes,
        "keyAssumption": SOLO_CADENCE_NOTE,
        "honestLimit": ("What this can show is work that demonstrably happened without a person. "
                        "What it cannot show is what that work was worth — and the gap between "
                        "those two is not a gap we are allowed to fill with an estimate."),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--print", dest="show", action="store_true")
    a = ap.parse_args()
    d = build()
    if a.show:
        print(json.dumps(d, indent=2))
        return 0
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)
    print(f"wrote {os.path.relpath(OUT, ROOT)} — {len(d['rows'])} modelled row(s), "
          f"{len(d['excluded'])} excluded")
    for r in d["rows"]:
        print(f"  {r['metric']}: {r['actual']} {r['unit']} vs {r['without']} modelled")
    for x in d["excluded"]:
        print(f"  EXCLUDED  {x['metric']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
