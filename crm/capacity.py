#!/usr/bin/env python3
"""Capacity — the constraint the forecast pretends does not exist.

Every number on the CRM board is a DEMAND number: pipeline value, win probability, weighted
forecast. Not one of them knows that a single person delivers all of it. As built, the board
would cheerfully encourage signing five clients the Founder cannot serve — and because yourco
absorbs the model and infra spend, over-signing is not merely stressful, it is
margin-negative: you pay to serve a client you are failing.

This module makes supply visible. It reports three things, in decreasing order of how much
evidence they need — and it refuses the ones it cannot support instead of estimating.

  1. COLLISION (needs only predicted close dates). If every open deal closed when we say it
     will, how many would be in Build & Implementation at the same time? Two builds in one
     week is a different company than two builds a quarter apart, and the board cannot
     currently tell those apart.
  2. CEILING (needs one human input). How many concurrent builds can yourco actually run?
     Nobody can derive this; the Founder states it in `meta.capacity.maxConcurrentBuilds`. Until he
     does, this module reports the collision and declines to call it over or under capacity.
  3. HOURS (needs build-time evidence that does not exist yet). Weighting pipeline against
     deliverable hours requires hours per build. `clients/<c>/cost.md` tracks DOLLARS and
     SESSIONS, not hours, and every `build` phase row is empty because nothing is signed.
     So the hours model is REFUSED, and this says exactly which file would have to start
     carrying what for it to work.

The refusal is the point. A capacity forecast built on invented hours would be the most
dangerous number in the CRM — it would license exactly the over-signing it claims to prevent.

Run:
    python3 crm/capacity.py
    python3 crm/capacity.py --json
"""
import json, os, sys, datetime, re
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
# Playground switch: data files resolve under DATA_DIR, never HERE. HERE is CODE.
DATA_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm") if os.environ.get("YOURCO_DATA_ROOT") else HERE
REPO = os.path.dirname(HERE)
DATA = os.path.join(DATA_DIR, "data.json")
CLIENTS = os.path.join(REPO, "clients")
TODAY = datetime.date.today()

# The stages that consume DELIVERY capacity (as opposed to sales attention).
BUILD_STAGES = {"signed-onboarding", "build-implementation", "testing"}
# How long a build occupies the bench, in days, once signed. Sourced from the delivery loop's
# 48h go-live target plus the weekly-iteration cadence — NOT measured, so it is declared here
# as an assumption and echoed in the output rather than buried.
ASSUMED_BUILD_DAYS = 30
BUILD_DAYS_BASIS = ("assumption, not measurement — 02_delivery_loop.md targets 48h to a first "
                    "go-live and then weekly iteration; 30 days is the window a build realistically "
                    "occupies attention. Replace with measured build duration once one completes.")


def _d(iso):
    try:
        return datetime.date.fromisoformat(str(iso)[:10])
    except Exception:
        return None


def predicted_close(deal):
    """The most recent prediction's close date, if a human ever made one."""
    preds = deal.get("predictions") or []
    if not preds:
        return None, None
    p = sorted(preds, key=lambda x: str(x.get("at") or ""))[-1]
    return _d(p.get("closeDate")), p


def build_evidence():
    """Is there ANY measured build duration anywhere? Walk the cost ledgers and look."""
    found, scanned = [], 0
    if not os.path.isdir(CLIENTS):
        return found, scanned
    for name in sorted(os.listdir(CLIENTS)):
        p = os.path.join(CLIENTS, name, "cost.md")
        if not os.path.isfile(p):
            continue
        scanned += 1
        try:
            txt = open(p, encoding="utf-8").read()
        except Exception:
            continue
        # a build-phase row that carries an hours figure is the only thing that would count
        for line in txt.splitlines():
            if "| build " in line.lower() and re.search(r"\b\d+(\.\d+)?\s*(h|hr|hrs|hours)\b", line, re.I):
                found.append({"client": name, "row": line.strip()[:120]})
    return found, scanned


def compute(data=None):
    if data is None:
        with open(DATA) as f:
            data = json.load(f)
    cfg = (data.get("meta") or {}).get("capacity") or {}
    ceiling = cfg.get("maxConcurrentBuilds")
    cos = {c["id"]: c for c in data.get("companies", []) or []}

    # ---- who is consuming capacity RIGHT NOW ------------------------------------------
    in_build = [d for d in (data.get("deals") or []) if d.get("stage") in BUILD_STAGES]
    live = [d for d in (data.get("deals") or []) if d.get("stage") == "live"]

    # ---- 1. collision: overlap of predicted build windows ------------------------------
    windows, unpredicted = [], []
    for d in (data.get("deals") or []):
        if d.get("stage") in ("parked", "live") or d.get("stage") in BUILD_STAGES:
            continue
        cd, p = predicted_close(d)
        if not cd:
            unpredicted.append({"dealId": d.get("id"),
                                "company": cos.get(d.get("companyId"), {}).get("name") or d.get("name"),
                                "stage": d.get("stage")})
            continue
        windows.append({"dealId": d.get("id"),
                        "company": cos.get(d.get("companyId"), {}).get("name") or d.get("name"),
                        "start": cd, "end": cd + datetime.timedelta(days=ASSUMED_BUILD_DAYS),
                        "confidence": (p or {}).get("confidence")})
    # add anything already in build, starting today
    for d in in_build:
        since = _d(d.get("stageSince")) or TODAY
        windows.append({"dealId": d.get("id"),
                        "company": cos.get(d.get("companyId"), {}).get("name") or d.get("name"),
                        "start": since, "end": since + datetime.timedelta(days=ASSUMED_BUILD_DAYS),
                        "confidence": None, "inFlight": True})

    peak, peak_when, peak_who = 0, None, []
    if windows:
        edges = sorted({w["start"] for w in windows} | {w["end"] for w in windows})
        for day in edges:
            overlap = [w for w in windows if w["start"] <= day < w["end"]]
            if len(overlap) > peak:
                peak, peak_when, peak_who = len(overlap), day, [w["company"] for w in overlap]

    collisions = []
    for i, a in enumerate(windows):
        for b in windows[i + 1:]:
            if a["start"] < b["end"] and b["start"] < a["end"]:
                collisions.append({"a": a["company"], "b": b["company"],
                                   "from": max(a["start"], b["start"]).isoformat(),
                                   "to": min(a["end"], b["end"]).isoformat()})

    # ---- 3. hours: refused, with the exact gap named ----------------------------------
    ev, scanned = build_evidence()
    hours = {
        "status": "measured" if ev else "refused",
        "evidence": ev,
        "why": None if ev else (
            f"No build has ever been timed. {scanned} client cost ledger(s) scanned; they track "
            f"DOLLARS and SESSIONS, and every `build` phase row is empty because nothing is "
            f"signed. An hours-weighted forecast built on invented numbers would license exactly "
            f"the over-signing it claims to prevent, so it is refused."),
        "toEnable": ("Log an `hours` figure on `build`-phase rows in `clients/<client>/cost.md` "
                     "(the log-build-session skill already journals session time — it just isn't "
                     "written as hours). One completed build turns this on."),
    }

    out = {
        "generated": TODAY.isoformat(),
        "assumedBuildDays": ASSUMED_BUILD_DAYS, "buildDaysBasis": BUILD_DAYS_BASIS,
        "inBuildNow": [{"company": cos.get(d.get("companyId"), {}).get("name") or d.get("name"),
                        "stage": d.get("stage")} for d in in_build],
        "liveNow": len(live),
        "windows": [{**w, "start": w["start"].isoformat(), "end": w["end"].isoformat()} for w in windows],
        "unpredicted": unpredicted,
        "peakConcurrent": peak,
        "peakWhen": peak_when.isoformat() if peak_when else None,
        "peakWho": peak_who,
        "collisions": collisions,
        "ceiling": ceiling,
        "hours": hours,
    }

    # ---- the verdict, and its refusal --------------------------------------------------
    if not windows:
        out["status"] = "nothing to schedule"
        out["reading"] = (
            f"No deal has a predicted close date, and nothing is in build. "
            f"{len(unpredicted)} open deal(s) could carry one — a prediction is captured "
            f"automatically on every stage move, so this fills itself as deals advance. Until "
            f"then there is no schedule to collide.")
    elif ceiling is None:
        out["status"] = "ceiling unset"
        out["reading"] = (
            f"Peak of **{peak} concurrent build(s)**"
            + (f" around {out['peakWhen']} ({', '.join(peak_who)})" if peak_when else "")
            + ". Whether that is over capacity is unanswerable: nobody has stated how many "
              "concurrent builds yourco can run. Set `meta.capacity.maxConcurrentBuilds` — it is "
              "a judgement only the Founder holds, and this module will not invent it.")
    else:
        over = peak > int(ceiling)
        out["status"] = "over" if over else "within"
        out["reading"] = (
            f"Peak {peak} concurrent build(s) against a stated ceiling of {ceiling} — "
            + (f"**OVER by {peak - int(ceiling)}**. Something has to slip, be staffed, or be "
               f"declined; the anti-pipeline (crm/antipipeline.py) is where that decision gets "
               f"recorded." if over else "within capacity."))
    return out


def main():
    r = compute()
    if "--json" in sys.argv:
        print(json.dumps(r, indent=2)); return
    print(f"Capacity — the supply side of the forecast\n")
    print(f"  In build now: {len(r['inBuildNow'])} · live: {r['liveNow']}")
    print(f"  {r['reading']}\n")
    if r["collisions"]:
        print("  Overlapping build windows:")
        for c in r["collisions"][:10]:
            print(f"    · {c['a']} × {c['b']}  ({c['from']} → {c['to']})")
        print()
    if r["unpredicted"]:
        print(f"  {len(r['unpredicted'])} open deal(s) with no predicted close date — invisible to "
              f"this schedule:")
        for u in r["unpredicted"][:8]:
            print(f"    · {u['company']} ({u['stage']})")
        print()
    print(f"  Build window assumption: {r['assumedBuildDays']} days — {r['buildDaysBasis']}")
    h = r["hours"]
    print(f"\n  Hours model: {h['status'].upper()}")
    if h["status"] == "refused":
        print(f"    {h['why']}")
        print(f"    To enable: {h['toEnable']}")


if __name__ == "__main__":
    main()
