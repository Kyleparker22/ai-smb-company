#!/usr/bin/env python3
"""
Claim-assist — auto-fill the storm-verification section of an insurance claim
from the evidence trail the engine already captured (last_run.json). NOAA is the
source of record carriers use for wind/hail; this hands the roofer/adjuster a
documented packet (date, county, peak MEASURED value, named stations) instead of
"trust me." Faster approvals, fewer denials, roofer paid sooner.

Usage:  python3 claim.py <County> [YYYY-MM-DD] [--address "123 Main St"]
        python3 claim.py Duval
"""
import json, sys, os


def load_storm(county, date=None):
    d = json.load(open("last_run.json"))
    cands = [v for v in d["verified"] if v["county"].lower() == county.lower()
             and (date is None or v["date"] == date)]
    if not cands:
        sys.exit(f"No storm for {county}" + (f" on {date}" if date else "") + " in last_run.json.")
    return sorted(cands, key=lambda v: v["reports"], reverse=True)[0], d["generated"]


def peak(v):
    bits = []
    if v.get("max_hail_in"):  bits.append(f'{v["max_hail_in"]:.2f}" hail')
    if v.get("max_wind_mph"): bits.append(f'{v["max_wind_mph"]:.0f} mph wind')
    if v.get("tornado"):      bits.append("tornado")
    return ", ".join(bits) or "storm damage"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    address = None
    if "--address" in sys.argv:
        address = sys.argv[sys.argv.index("--address") + 1]
    if not args:
        sys.exit("Usage: python3 claim.py <County> [YYYY-MM-DD] [--address \"...\"]")
    county = args[0]
    date = args[1] if len(args) > 1 else None
    v, gen = load_storm(county, date)

    measured = [e for e in v.get("evidence", []) if (e.get("qualifier") or "").upper() == "M"]
    other = [e for e in v.get("evidence", []) if (e.get("qualifier") or "").upper() != "M"]

    L = []
    L.append(f"# STORM VERIFICATION — insurance claim support")
    L.append("")
    L.append(f"**Property:** {address or '[address]'}")
    L.append(f"**Location:** {v['county']} County, Florida")
    L.append(f"**Date of loss:** {v['date']}")
    L.append(f"**Verified peak:** {peak(v)}")
    L.append(f"**Confidence:** {v['confidence']} — cross-verified across {', '.join(v.get('sources_hit', []))}")
    L.append("")
    L.append("## Official measured data (source of record)")
    if measured:
        for e in measured:
            L.append(f"- {(e.get('time') or '')[:16].replace('T',' ')}Z — **{e['hazard']} {e.get('value')}** "
                     f"({e.get('reporter')}, measured) — {e.get('remark') or ''}")
    else:
        L.append("- (No instrument-measured value in NOAA reports for this event; see corroborating reports below.)")
    L.append("")
    if other:
        L.append("## Corroborating reports")
        for e in other:
            q = {"E": "estimated"}.get((e.get("qualifier") or "").upper(), "report")
            L.append(f"- {(e.get('time') or '')[:16].replace('T',' ')}Z — {e['hazard']} "
                     f"{e.get('value') if e.get('value') is not None else ''} ({e.get('reporter')}, {q}) — {e.get('remark') or ''}")
        L.append("")
    L.append("## Source")
    L.append("NOAA National Weather Service Local Storm Reports — the storm-verification "
             "standard used by property insurers. Corroborated by NOAA SPC and active NWS "
             "alerts where noted. Evidence trail retained and auditable.")
    L.append("")
    L.append(f"*Prepared by yourco storm-command · verification date {gen}. "
             "Documentation only — not an adjustment or a coverage determination.*")

    doc = "\n".join(L)
    slug = "".join(c for c in f"{v['county']}_{v['date']}" if c.isalnum() or c in "_-")
    fn = f"claim_{slug}.md"
    open(fn, "w").write(doc + "\n")

    def ev(e):
        return {"time": (e.get("time") or "")[:16].replace("T", " "), "hazard": e["hazard"],
                "value": e.get("value"), "reporter": e.get("reporter"),
                "qualifier": (e.get("qualifier") or "").upper(), "remark": e.get("remark")}
    data = {"address": address or "", "county": v["county"], "date": v["date"], "peak": peak(v),
            "confidence": v["confidence"], "sources": v.get("sources_hit", []),
            "measured": [ev(e) for e in measured], "other": [ev(e) for e in other], "generated": gen}
    open("claim_data.js", "w").write("window.CLAIM = " + json.dumps(data, indent=2) + ";\n")

    print(doc)
    print(f"\n(saved -> {fn} + claim_data.js)")


if __name__ == "__main__":
    main()
