#!/usr/bin/env python3
"""
Outcome learning loop — the moat. Reads field outcomes (doors → jobs → revenue,
outcomes.json) and learns which storm profiles actually convert, then writes
feed-forward priority multipliers (learned_priorities.json) that canvass/dispatch
use to rank future storms. The system gets more profitable every storm — exactly
what a no-code map can't do.

Usage:  python3 learning.py
"""
import json


def band(s):
    """Storm profile key the system learns on."""
    if s["hazard"] == "tornado":
        return "tornado"
    if s["hazard"] == "hail":
        return "hail 1.25\"+" if s["magnitude"] >= 1.25 else "hail <1.25\""
    return "wind 60+" if s["magnitude"] >= 60 else "wind <60"


def main():
    d = json.load(open("outcomes.json"))
    rows = d["storms"]

    # aggregate by profile
    prof = {}
    for s in rows:
        k = band(s)
        p = prof.setdefault(k, {"doors": 0, "jobs": 0, "revenue": 0, "n": 0})
        p["doors"] += s["doors"]; p["jobs"] += s["jobs"]; p["revenue"] += s["revenue"]; p["n"] += 1
    for k, p in prof.items():
        p["conv"] = round(100 * p["jobs"] / p["doors"], 1) if p["doors"] else 0
        p["rev_per_door"] = round(p["revenue"] / p["doors"]) if p["doors"] else 0

    # feed-forward: priority multiplier = profile's revenue/door vs the average
    avg_rpd = sum(p["rev_per_door"] for p in prof.values()) / len(prof)
    priorities = {k: round(p["rev_per_door"] / avg_rpd, 2) for k, p in prof.items()}

    ranked = sorted(prof.items(), key=lambda kv: -kv[1]["rev_per_door"])
    print("=" * 62)
    print("  yourco · WHAT CONVERTS — learned from field outcomes")
    print("=" * 62)
    print(f"  {'profile':16} {'storms':>6} {'doors':>6} {'jobs':>5} {'conv%':>6} {'$/door':>8} {'priority':>9}")
    for k, p in ranked:
        print(f"  {k:16} {p['n']:>6} {p['doors']:>6} {p['jobs']:>5} {p['conv']:>6} {p['rev_per_door']:>8} {priorities[k]:>9}")

    best, worst = ranked[0], ranked[-1]
    print(f"\n  → {best[0]} converts best (${best[1]['rev_per_door']}/door, {best[1]['conv']}%). "
          f"Prioritize these dispatches.")
    print(f"  → {worst[0]} is the weakest (${worst[1]['rev_per_door']}/door). Send fewer crews, or none.")
    print(f"  → Multipliers written to learned_priorities.json — canvass/dispatch rank storms by these next run.")

    json.dump({"generated_from": len(rows), "priorities": priorities,
               "detail": prof}, open("learned_priorities.json", "w"), indent=2)

    data = {"from_storms": len(rows), "best": best[0], "worst": worst[0],
            "profiles": [{"profile": k, "n": p["n"], "doors": p["doors"], "jobs": p["jobs"],
                          "conv": p["conv"], "rev_per_door": p["rev_per_door"], "priority": priorities[k]}
                         for k, p in ranked]}
    open("learned_data.js", "w").write("window.LEARNED = " + json.dumps(data, indent=2) + ";\n")


if __name__ == "__main__":
    main()
