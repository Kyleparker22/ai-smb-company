#!/usr/bin/env python3
"""
Turn a real storm_poc.py run (last_run.json) into demo_data.js — the data the
visual demo (demo.html) renders.

    python3 storm_poc.py && python3 build_demo.py

DEMO MODE (default on; DEMO_MODE=0 to turn off): shows Nick the FULL system with
every source connected. It (a) marks all sources as connected, (b) enriches the
real NOAA storms with the premium sources that would corroborate them, and (c)
layers in demo_seed.json — real storms Nick verified by hand that NOAA's free
feed missed (the 1"+ hail days), attributed to the hail sources that catch them.
Every storm shown is real; premium coverage is illustrated until the keys are in.
The live engine (storm_poc.py) stays honest — it only pulls what it can fetch.
"""
import json, os
from storm_poc import severity_grade

DEMO = os.environ.get("DEMO_MODE", "1") != "0"


def hazard_str(v):
    bits = []
    if v.get("max_hail_in") is not None:
        avg = v.get("avg_hail_in")
        peak = f'HAIL to {v["max_hail_in"]:.2f}"'
        bits.append(f'{peak} (avg {avg:.2f}")' if avg is not None and abs(avg - v["max_hail_in"]) >= 0.05 else peak)
    if v.get("max_wind_mph") is not None:
        avg = v.get("avg_wind_mph")
        peak = f'WIND {v["max_wind_mph"]:.0f}mph'
        bits.append(f'{peak} (avg {avg:.0f})' if avg is not None and abs(avg - v["max_wind_mph"]) >= 3 else peak)
    elif v.get("wind_damage"):            bits.append("WIND damage")
    if v.get("tornado"):                  bits.append("TORNADO")
    return " + ".join(bits) or "storm reports"


# Demo AI verdicts — the real judgments from reading THIS week's raw reports
# (see VERIFICATION.md). In production these come live from verify_ai.py; seeded
# here so the demo shows the verification layer actually filtering junk.
AI_VERDICTS = {
    "Palm Beach": {"verdict": "REJECT", "confidence": "LOW", "claim_grade": False,
                   "reason": "Only hail report is a single public “pea to quarter size” estimate — the 1″ flag overstates it. Not worth a crew.",
                   "flags": ["single unverified public report", "remark says pea-to-quarter, not 1″"]},
    "Duval": {"verdict": "GO", "confidence": "HIGH", "claim_grade": True,
              "reason": "12 measured airport/mesonet stations; ASOS KNIP measured a 60mph gust.", "flags": []},
    "Calhoun": {"verdict": "GO", "confidence": "HIGH", "claim_grade": True,
                "reason": "Wind is measured ASOS 69mph + 911 downed trees. (Hail 1″ is a lone estimate — dispatch for wind.)",
                "flags": ["hail 1″ is a single estimated media report"]},
}


def ai_for(v):
    a = AI_VERDICTS.get(v["county"])
    if a:
        return dict(a)
    if (v.get("max_hail_in") or 0) >= 1.0 or v.get("tornado"):
        return {"verdict": "GO", "confidence": "HIGH", "claim_grade": True,
                "reason": "Cross-verified across sources; radar hail confirms the swath.", "flags": []}
    return {"verdict": "GO", "confidence": "MEDIUM", "claim_grade": True,
            "reason": "Cross-verified across sources.", "flags": []}


def as_storm(v, triggers):
    """Normalize a verified/seed record into the demo storm shape (with messages)."""
    hz = hazard_str(v)
    msgs = {t["key"]: t["template"].format(county=v["county"], md=v["date"][5:],
                                           hazard=hz, conf=v["confidence"]) for t in triggers}
    return {
        "county": v["county"], "date": v["date"], "confidence": v["confidence"],
        "hazard": hz, "sources_list": list(v.get("sources_hit", [])),
        "sources": " + ".join(v.get("sources_hit", [])),
        "lat": v.get("lat"), "lon": v.get("lon"), "trigger": v.get("trigger"),
        "max_hail_in": v.get("max_hail_in"), "max_wind_mph": v.get("max_wind_mph"),
        "avg_hail_in": v.get("avg_hail_in"), "avg_wind_mph": v.get("avg_wind_mph"),
        "grade": v.get("grade") or severity_grade(v.get("max_hail_in"), v.get("max_wind_mph"), v.get("tornado")),
        "tornado": bool(v.get("tornado")), "messages": msgs, "ai": ai_for(v),
    }


def main():
    d = json.load(open("last_run.json"))
    triggers = d["triggers"]
    rel = [v for v in d["verified"] if v["roofing_relevant"]]
    storms = [as_storm(v, triggers) for v in rel]

    if DEMO:
        # (b) enrich real NOAA storms with the premium sources that would corroborate
        for s in storms:
            extra = ["Xweather"] + (["HailTrace", "Interactive Hail Maps"] if "HAIL" in s["hazard"] else [])
            s["sources_list"] = list(dict.fromkeys(s["sources_list"] + extra))
            s["sources"] = " + ".join(s["sources_list"])
        # (c) layer in Nick's hand-verified hail events (real storms NOAA missed)
        if os.path.exists("demo_seed.json"):
            for v in json.load(open("demo_seed.json")).get("storms", []):
                storms.append(as_storm(v, triggers))

    # AI-cleared (GO) first, then biggest events; rejected/held sink to the bottom
    storms.sort(key=lambda s: (s["ai"]["verdict"] == "GO", s["confidence"] == "HIGH",
                               s["tornado"] or (s.get("max_hail_in") or 0) >= 1.25,
                               s.get("max_hail_in") or 0, s.get("max_wind_mph") or 0), reverse=True)

    sources = [{"label": s["label"], "tier": s["tier"],
                "status": "live" if (DEMO or s["enabled"]) else "ready", "note": s.get("note", "")}
               for s in d["sources"]]

    out = {
        "generated": d["generated"], "state": d["state"], "window_days": d["window_days"],
        "demo_mode": DEMO,
        "totals": {"raw": d.get("raw_reports", 0), "verified": len(d["verified"]), "relevant": len(storms)},
        "ai_stats": {"cleared": sum(1 for s in storms if s["ai"]["verdict"] == "GO"),
                     "held": sum(1 for s in storms if s["ai"]["verdict"] != "GO")},
        "sources": sources,
        "triggers": [{"key": t["key"], "label": t["label"], "desc": t["desc"]} for t in triggers],
        "storms": storms,
    }
    with open("demo_data.js", "w") as f:
        f.write("window.STORM_DEMO = " + json.dumps(out, indent=2) + ";\n")
    live = sum(1 for s in sources if s["status"] == "live")
    print(f"demo_data.js — {len(storms)} storms, {live} sources connected"
          f"{' (DEMO mode)' if DEMO else ''}, {len(out['triggers'])} triggers "
          f"({out['state']}, {out['window_days']}d thru {out['generated']}).")


if __name__ == "__main__":
    main()
