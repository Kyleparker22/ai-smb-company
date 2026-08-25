#!/usr/bin/env python3
"""Prior-period snapshots — what the CRM actually said N days ago.

A KPI without a reference point is decoration. "$24,000 pipeline" tells you nothing;
"$24,000, up from $9,000 a month ago" is a fact you can act on. Every analytics product
gets this from a warehouse with dated rows. We don't have one — but we have something
better for this purpose: data.json is git-tracked, so **every past state of the CRM is
already on disk**, exactly as it was, with no backfill and no reconstruction.

This module hands the UI the raw blob from the newest commit on or before a target date.
It deliberately does NOT compute any metrics. The UI owns one definition of each KPI and
runs that same function over `now` and over `prior` — so a metric can never drift from
its own history, which is precisely what a second Python implementation would guarantee.

Two honesty rules, both load-bearing:

  1. STAGE KEYS ARE NORMALIZED, NOTHING ELSE IS. The ladder was renamed 2026-08-11
     (sitdown/audit -> discovery, proposal -> demo-proposal, ...). A raw July blob scored
     against today's keys reads 0 qualified deals, which would render as a triumphant
     "+300%" when nothing happened at all. ghost.LEGACY is the one mapping; we reuse it
     rather than restate it.

  2. EVERY OTHER SCHEMA CHANGE IS DECLARED, NOT PAPERED OVER. The blob carries the date
     it came from; each KPI in the UI declares the date its inputs became trustworthy
     (`since`). Where the prior predates that, the UI shows "no comparable prior" instead
     of a number. Contact `status`, for one, was re-derived from recency on 2026-08-12 —
     comparing it to the hand-seeded June values would be comparing two different
     questions and calling the difference a trend.

Run:
    python3 crm/history.py                 # what's available, and the 30-day prior
    python3 crm/history.py --days 7
    python3 crm/history.py --json
"""
import json, os, sys, datetime, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
# Playground switch: data files resolve under DATA_DIR, never HERE. HERE is CODE.
DATA_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm") if os.environ.get("YOURCO_DATA_ROOT") else HERE
REPO = os.path.dirname(HERE)
DATA = os.path.join(DATA_DIR, "data.json")
REL = "crm/data.json"

MAX_REVS = 400

# The one schema-era boundary the UI needs to reason about. Anything a KPI depends on that
# was reshaped on a date goes here, and the KPI names the key in its `since`.
SCHEMA_EPOCHS = {
    "stages": "2026-06-10",        # normalized forward by ghost.LEGACY, so comparable throughout
    "contactStatus": "2026-08-12",  # re-derived from recency; older values answer a different question
    "contactRole": "2026-08-11",    # `relationship` free text -> `role` enum
    "dealValue": "2026-06-10",
}


def _git(*args):
    try:
        return subprocess.run(("git",) + args, cwd=REPO, capture_output=True, text=True,
                              timeout=45).stdout
    except Exception:
        return ""


def _norm_stage(raw):
    """Reuse ghost's legacy map — one mapping, not two."""
    try:
        from ghost import norm
        return norm(raw)
    except Exception:
        return str(raw or "").strip().lower()


def revisions():
    """[(sha, YYYY-MM-DD)] for data.json, newest first."""
    out = _git("log", f"-{MAX_REVS}", "--format=%H %ad", "--date=short", "--", REL)
    rows = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            rows.append((parts[0], parts[1]))
    return rows


def blob_at(sha):
    raw = _git("show", f"{sha}:{REL}")
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None


def normalize(data):
    """Bring a past blob onto today's stage vocabulary. Stages only — see rule 2 in the docstring."""
    for coll in ("deals", "closed"):
        for d in data.get(coll, []) or []:
            if d.get("stage"):
                d["stage"] = _norm_stage(d["stage"])
    return data


def snapshot(days=30):
    """The newest committed state on or before `days` ago. Never interpolates: if the oldest
    revision is newer than the target, it says so rather than substituting the oldest one —
    'the earliest thing we have' is not 'a month ago' and must not be labelled as such."""
    revs = revisions()
    if not revs:
        return {"found": False, "why": "no git history for crm/data.json"}
    target = datetime.date.today() - datetime.timedelta(days=days)
    oldest_date = revs[-1][1]
    hit = next(((s, d) for s, d in revs if d <= target.isoformat()), None)
    if not hit:
        return {"found": False, "requested": target.isoformat(), "oldest": oldest_date,
                "why": (f"the CRM's history starts {oldest_date}; there is no state from "
                        f"{target.isoformat()} to compare against.")}
    sha, date = hit
    data = blob_at(sha)
    if data is None:
        return {"found": False, "requested": target.isoformat(),
                "why": f"revision {sha[:10]} could not be read"}
    return {
        "found": True, "requested": target.isoformat(), "date": date, "sha": sha[:10],
        "days": days, "revisions": len(revs), "oldest": oldest_date,
        "epochs": SCHEMA_EPOCHS,
        "normalized": ["stage keys via ghost.LEGACY"],
        "data": normalize(data),
    }


def compute(days=30):
    s = snapshot(days)
    if s.get("found"):
        d = s["data"]
        s["shape"] = {k: len(d.get(k) or []) for k in
                      ("deals", "closed", "companies", "contacts", "activities", "tasks")}
    return s


def main():
    days = 30
    if "--days" in sys.argv:
        try:
            days = int(sys.argv[sys.argv.index("--days") + 1])
        except Exception:
            pass
    r = compute(days)
    if "--json" in sys.argv:
        # the blob is large and the CLI is for eyeballing — summarise unless asked
        if "--full" not in sys.argv:
            r.pop("data", None)
        print(json.dumps(r, indent=2)); return
    if not r.get("found"):
        print(f"No prior state {days}d back — {r.get('why')}"); return
    print(f"Prior state {days}d back: {r['date']} @ {r['sha']}  "
          f"(asked for {r['requested']}, {r['revisions']} revisions since {r['oldest']})")
    for k, v in r["shape"].items():
        print(f"  {k:<12} {v}")
    print(f"\nNormalized: {', '.join(r['normalized'])}. Everything else is compared as-is, and "
          f"each KPI declares the date its own inputs became trustworthy.")


if __name__ == "__main__":
    main()
