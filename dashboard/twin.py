#!/usr/bin/env python3
"""Twin — the read side of the DRI twin scoreboard.

Answers, on evidence: **how much of the Founder's judgment has the OS actually learned, and in
which kinds of decision?** Per class — hit rate, calibration, current streak — plus an
explicit verdict on whether that class would qualify for the twin to decide it.

FOUR RULES THAT KEEP THE NUMBER HONEST

1. **Empty is the correct starting state.** A prediction counts only if it was recorded
   before the Founder's call. Nothing is backfilled from `decisions/`, so the board opens at zero
   and says so, rather than manufacturing a record out of hindsight.
2. **Refuse small samples.** Below the shared floor (`runtime/ledger.py` MIN_FORECASTS) no
   hit rate or Brier is published for a class — the raw record is shown instead.
3. **Qualifying is not promoting.** A class that clears every threshold is reported as
   "would qualify — the Founder's call". Nothing here grants the twin authority; the standing rule
   is that goals and org decisions stay the Founder's, and this follows it.
4. **Some classes can never qualify.** legal-gate, publish-send, spend and client-commitment
   are category exclusions, not thresholds — mirroring the autonomy matrix's "what stays
   gated regardless of evidence". A perfect record on them still earns nothing.

Read-only. Exposed as GET /api/twin. Writers live in `runtime/dri_twin.py`.
"""
import os, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "runtime"))
sys.path.insert(0, HERE)

from ledger import Ledger, brier, calibration_bins, refuse_reason, MIN_FORECASTS  # noqa: E402
import dri_twin as DT  # classes, thresholds, exclusions, queue — one definition  # noqa: E402

PRED = Ledger("loops/_twin/predictions.jsonl")


def _streak(rows):
    """Consecutive correct calls, most recent first. Any miss resets to zero — same rule as
    the autonomy streak ledger, where an incident zeroes the count rather than averaging out."""
    n = 0
    for r in sorted(rows, key=lambda r: r["seq"], reverse=True):
        if r["hit"]:
            n += 1
        else:
            break
    return n


def _earn(cls, n, hit_rate, br, streak):
    """Would this class qualify for the twin to decide it? Reports; never promotes."""
    if cls in DT.NEVER_EARNS:
        return {"verdict": "never — category exclusion", "why": DT.NEVER_EARNS[cls],
                "eligible": False}
    unmet = []
    if n < DT.EARN_MIN_RESOLVED:
        unmet.append(f"{n}/{DT.EARN_MIN_RESOLVED} resolved")
    if hit_rate is None or hit_rate < DT.EARN_MIN_HITRATE * 100:
        unmet.append(f"hit rate {hit_rate if hit_rate is not None else '—'}% "
                     f"< {int(DT.EARN_MIN_HITRATE * 100)}%")
    if br is None or br > DT.EARN_MAX_BRIER:
        unmet.append(f"Brier {br if br is not None else '—'} > {DT.EARN_MAX_BRIER}")
    if streak < DT.EARN_MIN_STREAK:
        unmet.append(f"streak {streak}/{DT.EARN_MIN_STREAK}")
    if unmet:
        return {"verdict": "not yet", "why": "; ".join(unmet), "eligible": True}
    return {"verdict": "would qualify — the Founder's call",
            "why": "every threshold met; promotion is still a human decision, never automatic",
            "eligible": True}


def build():
    raw = PRED.project()
    evs = raw["events"]
    preds = {e["seq"]: e for e in evs if e.get("kind") == "prediction"}
    outcomes = [e for e in evs if e.get("kind") == "outcome"]

    rows, by_cls = [], {}
    for o in outcomes:
        p = preds.get(o.get("prediction"))
        if not p:
            continue
        r = {"seq": p["seq"], "cls": p.get("cls") or "process", "says": p.get("says"),
             "actual": o.get("actual"), "hit": bool(o.get("hit")), "p": p.get("p"),
             "on": o.get("on"), "because": p.get("because")}
        rows.append(r)
        by_cls.setdefault(r["cls"], []).append(r)

    resolved_ids = {o.get("prediction") for o in outcomes}
    openp = [{"seq": p["seq"], "cls": p.get("cls"), "says": p.get("says"), "p": p.get("p"),
              "item": p.get("item"), "question": p.get("question"), "on": p.get("on")}
             for s, p in preds.items() if s not in resolved_ids]

    def stats(rs):
        n = len(rs)
        hits = sum(1 for r in rs if r["hit"])
        hr = round(hits / n * 100) if n else None
        br = brier([(r["p"], r["hit"]) for r in rs if isinstance(r["p"], (int, float))])
        return n, hits, hr, br

    n_all, hits_all, hr_all, br_all = stats(rows)
    cls_rows = []
    for cls in DT.CLASSES:
        rs = by_cls.get(cls, [])
        n, hits, hr, br = stats(rs)
        st = _streak(rs)
        cls_rows.append({
            "cls": cls, "n": n, "hits": hits,
            "hitRate": hr if not refuse_reason(n) else None,
            "brier": br if not refuse_reason(n) else None,
            "refusal": refuse_reason(n), "streak": st,
            "earned": _earn(cls, n, hr, br, st),
            "neverEarns": cls in DT.NEVER_EARNS,
        })
    cls_rows.sort(key=lambda c: (-c["n"], c["cls"]))

    try:
        q = DT.queue()
    except Exception:
        q = []

    return {
        "generatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total": len(preds),
        "resolved": len(rows),
        "open": len(openp),
        "overall": {
            "n": n_all, "hits": hits_all,
            "hitRate": hr_all if not refuse_reason(n_all) else None,
            "brier": br_all if not refuse_reason(n_all) else None,
            "refusal": refuse_reason(n_all),
            "bins": calibration_bins([(r["p"], r["hit"]) for r in rows
                                      if isinstance(r["p"], (int, float))]),
        },
        "byClass": cls_rows,
        "recent": sorted(rows, key=lambda r: r["seq"], reverse=True)[:12],
        "openPredictions": sorted(openp, key=lambda r: r["seq"], reverse=True)[:12],
        "queue": q,
        "unpredicted": sum(1 for i in q if not i.get("hasPrediction")),
        "thresholds": {"resolved": DT.EARN_MIN_RESOLVED,
                       "hitRatePct": int(DT.EARN_MIN_HITRATE * 100),
                       "brier": DT.EARN_MAX_BRIER, "streak": DT.EARN_MIN_STREAK,
                       "sampleFloor": MIN_FORECASTS},
        "neverEarns": DT.NEVER_EARNS,
        "zeroState": ("No predictions recorded yet — and that is the correct starting state, "
                      "not a gap. A prediction counts only if it was written down before the Founder "
                      "decided; backfilling from decisions/ would score the twin on hindsight. "
                      "The queue below is real open decision points waiting for one.")
                     if not preds else None,
        "note": ("This measures the one thing the autonomy matrix never could: how much of the "
                 "founder's judgment the OS has actually learned. Qualifying is reported, never "
                 "acted on — promotion stays the Founder's, and four classes can never qualify at all."),
        "bad": raw["bad"],
    }


if __name__ == "__main__":
    import json
    d = build()
    print(json.dumps({k: v for k, v in d.items() if k not in ("queue",)}, indent=2)[:2500])
    print(f"\nqueue: {len(d['queue'])} open decision points, {d['unpredicted']} unpredicted")
    for i in d["queue"][:8]:
        print(f"  {i['id']} [{i['suggestedClass']}] {i['text'][:80]}")
