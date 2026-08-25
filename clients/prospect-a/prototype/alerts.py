#!/usr/bin/env python3
"""
Emit the real-time alert feed snapshot (alerts_data.js) for alerts.html — the
verified storms as they'd hit Nick's phone, newest first, with the detection
time pulled from the earliest report. This is the "be first" speed moment.

    python3 storm_poc.py && python3 alerts.py
"""
import json


def haz(v):
    b = []
    if v.get("max_hail_in"):  b.append(f'{v["max_hail_in"]:.2f}" hail')
    if v.get("max_wind_mph"): b.append(f'{v["max_wind_mph"]:.0f}mph wind')
    if v.get("tornado"):      b.append("TORNADO")
    return " + ".join(b) or "storm"


def detected(v):
    ts = [e.get("time") for e in v.get("evidence", []) if e.get("time")]
    return min(ts) if ts else v["date"] + "T00:00:00Z"


def main():
    d = json.load(open("last_run.json"))
    rel = [v for v in d["verified"] if v["roofing_relevant"] and v["confidence"] == "HIGH"]
    alerts = sorted(
        [{"county": v["county"], "date": v["date"], "hazard": haz(v),
          "sources": v.get("sources_hit", []), "detected": detected(v), "trigger": v.get("trigger")}
         for v in rel],
        key=lambda a: a["detected"], reverse=True)
    out = {"generated": d["generated"], "state": d["state"], "alerts": alerts}
    open("alerts_data.js", "w").write("window.ALERTS = " + json.dumps(out, indent=2) + ";\n")
    print(f"alerts_data.js — {len(alerts)} verified-storm alerts.")


if __name__ == "__main__":
    main()
