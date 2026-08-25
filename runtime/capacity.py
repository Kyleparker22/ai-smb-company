#!/usr/bin/env python3
"""The capacity board — the next onboarding slot, or an honest refusal.

Every consultancy claims scarcity. Almost none can compute it, which is why
"we're pretty booked" is the most common lie in professional services and why
buyers have learned to ignore it entirely.

We can compute it: `loops/_build-journal/sessions.jsonl` records how long real
builds actually took. Median build hours + weekly build capacity + what is
already committed = a slot date that is either true or not stated at all.

THE REFUSAL IS THE PRODUCT. A slot date invented from n=0 is the same lie with
extra steps, and it is worse for us than saying "we don't know yet" — because the
whole reason a prospect believes the date is that we showed our work. This module
inherits the build journal's own rule (`loops/_build-journal/_README.md`): below
three MEASURED sessions there is no median, and backfills never count toward one.
A stated-from-memory number is a recollection, not a measurement.

Run:
    python3 runtime/capacity.py
    python3 runtime/capacity.py --hours-per-week 24
    python3 runtime/capacity.py --json
"""
import json, os, sys, argparse, datetime, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("YOURCO_DATA_ROOT") or os.path.dirname(HERE)
JOURNAL = os.path.join(ROOT, "loops", "_build-journal", "sessions.jsonl")
CRM = os.path.join(ROOT, "crm", "data.json")
TODAY = datetime.date.today()

MIN_TIMED = 3          # inherited from the build journal's own refusal threshold
DEFAULT_HPW = 20       # ASSUMPTION — see assumptions[] in the output; the Founder confirms
IN_BUILD = {"build", "signed"}      # engagements consuming build capacity right now


def load_sessions():
    """Sessions with corrections applied. Corrections reference a session id and set fields."""
    if not os.path.exists(JOURNAL):
        return []
    rows, corrections = [], []
    with open(JOURNAL) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            (corrections if r.get("event") == "session.correction" else rows).append(r)
    by_session = {}
    for r in rows:
        if r.get("event") in ("session.started", "session.step"):
            continue
        by_session[r.get("session") or r.get("id")] = dict(r)
    for c in corrections:
        tgt = by_session.get(c.get("session"))
        if tgt:
            tgt.update(c.get("set") or {})
            tgt.setdefault("_corrected", True)
    return list(by_session.values())


def classify(s):
    """measured | stated | backfill — only `measured` may feed a median."""
    flags = " ".join(s.get("flags") or []).upper()
    if s.get("event") == "session.backfill" or "BACKFILL" in flags:
        return "backfill"
    if s.get("hours") is None:
        return "unknown"
    return "measured" if s.get("hours_precision") == "measured" else "stated"


def committed():
    """Engagements already consuming build capacity, from the live CRM."""
    if not os.path.exists(CRM):
        return []
    with open(CRM) as f:
        data = json.load(f)
    cos = {c["id"]: c.get("name") for c in data.get("companies", []) or []}
    return [cos.get(d.get("companyId")) or d.get("name")
            for d in data.get("deals", []) or [] if d.get("stage") in IN_BUILD]


def compute(hours_per_week, hpw_source):
    sessions = load_sessions()
    buckets = {}
    for s in sessions:
        buckets.setdefault(classify(s), []).append(s)
    measured = buckets.get("measured", [])
    hrs = sorted(float(s["hours"]) for s in measured if s.get("hours") is not None)

    inbuild = committed()
    assumptions = [
        f"Build capacity is {hours_per_week} h/week ({hpw_source}). the Founder is solo and also sells; "
        f"this is the build half of the week, not the working week.",
        "One engagement is assumed to consume its build hours contiguously — no parallel-build discount.",
    ]

    out = {
        "generated": TODAY.isoformat(),
        "hoursPerWeek": hours_per_week,
        "sessionsTotal": len(sessions),
        "measured": len(measured),
        "stated": len(buckets.get("stated", [])),
        "backfill": len(buckets.get("backfill", [])),
        "unknown": len(buckets.get("unknown", [])),
        "committed": inbuild,
        "assumptions": assumptions,
    }

    if len(hrs) < MIN_TIMED:
        need = MIN_TIMED - len(hrs)
        why = []
        if buckets.get("backfill"):
            why.append(f"{len(buckets['backfill'])} session(s) are backfills — reconstructed after the "
                       f"fact, so they record what someone remembered, not what was measured")
        if buckets.get("stated"):
            why.append(f"{len(buckets['stated'])} session(s) have stated hours rather than measured ones")
        out.update({
            "refused": True,
            "slot": None,
            "reason": (f"No slot date. {len(hrs)} measured build session(s) on record; {MIN_TIMED} is the "
                       f"minimum this instrument will quote from."),
            "missing": (f"{need} more build session(s) timed with "
                        f"`python3 runtime/build_journal.py --start` … `--stop` — started and stopped in "
                        f"real time, not reconstructed afterwards."),
            "why": why,
            "honesty": ("A capacity board exists to make scarcity checkable. Quoting a date from a sample "
                        "this thin would make it exactly the claim it was built to replace."),
        })
        return out

    median_h = statistics.median(hrs)
    lo, hi = hrs[0], hrs[-1]
    weeks_each = median_h / hours_per_week if hours_per_week else None
    backlog_weeks = (len(inbuild) * weeks_each) if weeks_each else None
    slot = TODAY + datetime.timedelta(days=round((backlog_weeks or 0) * 7))
    # Slots land on a Monday — an onboarding date mid-week isn't a real one.
    slot += datetime.timedelta(days=(7 - slot.weekday()) % 7)
    out.update({
        "refused": False,
        "medianBuildHours": median_h,
        "rangeBuildHours": [lo, hi],
        "weeksPerEngagement": round(weeks_each, 2) if weeks_each else None,
        "slot": slot.isoformat(),
        "concurrentCapacityPerMonth": round((hours_per_week * 4.33) / median_h, 2) if median_h else None,
        "honesty": (f"Computed from {len(hrs)} measured build session(s) (median {median_h:g} h, range "
                    f"{lo:g}–{hi:g} h) against {len(inbuild)} engagement(s) already in build. "
                    f"Small sample: the range is the honest signal, the median is the planning number."),
    })
    return out


def main():
    ap = argparse.ArgumentParser(description="Compute the next honest onboarding slot.")
    ap.add_argument("--hours-per-week", type=float, default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    hpw = a.hours_per_week if a.hours_per_week is not None else DEFAULT_HPW
    src = "passed on the command line" if a.hours_per_week is not None else \
          "DEFAULT ASSUMPTION in runtime/capacity.py — not measured, the Founder confirms"
    r = compute(hpw, src)

    if a.json:
        print(json.dumps(r, indent=2)); return 0

    print(f"Capacity board — {r['generated']}\n")
    print(f"  build sessions on record : {r['sessionsTotal']} "
          f"(measured {r['measured']} · stated {r['stated']} · backfill {r['backfill']} · "
          f"unknown {r['unknown']})")
    print(f"  engagements in build     : {len(r['committed'])}"
          + (f" — {', '.join(x for x in r['committed'] if x)}" if r["committed"] else ""))
    print()
    if r["refused"]:
        print("  NEXT SLOT: not stated.")
        print(f"  {r['reason']}")
        for w in r["why"]:
            print(f"    - {w}")
        print(f"\n  To make this instrument work: {r['missing']}")
    else:
        print(f"  NEXT SLOT: {r['slot']}")
        print(f"  median build {r['medianBuildHours']:g} h "
              f"(range {r['rangeBuildHours'][0]:g}–{r['rangeBuildHours'][1]:g}) "
              f"≈ {r['weeksPerEngagement']} weeks per engagement")
        print(f"  sustainable intake ≈ {r['concurrentCapacityPerMonth']} engagement(s)/month")
    print("\n  Assumptions:")
    for x in r["assumptions"]:
        print(f"    · {x}")
    print(f"\n  {r['honesty']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
