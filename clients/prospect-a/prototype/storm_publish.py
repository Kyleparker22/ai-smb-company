#!/usr/bin/env python3
"""
Publish the verified storm feed to the hosted Sample Product app.

The hosted Cloudflare Worker blocks outbound internet, so it can't fetch NOAA
itself. This script — run wherever there IS internet (the yourco VPS runtime, or
locally) — runs the engine, shapes the result into the app's StormFeed JSON, and
POSTs it to the Worker's /api/ingest. The Worker stores it in D1 and serves it as
the live feed (see app/src/routes/api.ingest.ts + storm.functions.ts:getFeed).

    INGEST_URL=https://sweet-opal-720.higgsfield.app/api/ingest \
    INGEST_SECRET=xxxxx  DAYS=8  python3 storm_publish.py

On the VPS: wrap in a systemd timer (see runtime/). Refresh cadence ~every 15-30m.
"""
import json, os, subprocess, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))

EV_FIELDS = ("time", "hazard", "value", "reporter", "qualifier", "remark")


def outlook_block():
    """SPC day-1/2/3 convective outlook → FL regions (w/ county) at risk (pre-storm staging)."""
    try:
        from staging import risk_for_day, NAME
        from fl_places import FL_PLACES
    except Exception:
        return None
    county_of = {p["name"]: p.get("county") for p in FL_PLACES}
    days = []
    for day in (1, 2, 3):
        try:
            r = risk_for_day(day)
        except Exception:
            r = {}
        regions = sorted(({"name": k, "county": county_of.get(k), "level": lv, "risk": NAME[lv]}
                          for k, lv in r.items()), key=lambda x: -x["level"])
        days.append({"day": day, "regions": regions})
    return {"days": days} if any(d["regions"] for d in days) else None


def hazard_str(v):
    bits = []
    mh, ah = v.get("max_hail_in"), v.get("avg_hail_in")
    if mh is not None:
        bits.append(f'HAIL to {mh:.2f}" (avg {ah:.2f}")' if ah is not None and abs(ah - mh) >= 0.05
                    else f'HAIL to {mh:.2f}"')
    mw, aw = v.get("max_wind_mph"), v.get("avg_wind_mph")
    if mw is not None:
        bits.append(f'WIND {mw:.0f}mph (avg {aw:.0f})' if aw is not None and abs(aw - mw) >= 3
                    else f'WIND {mw:.0f}mph')
    elif v.get("wind_damage"):
        bits.append("WIND damage")
    if v.get("tornado"):
        bits.append("TORNADO")
    return " + ".join(bits) or "storm reports"


def ai_verdict(v):
    """Rule-based verdict (matches the TS engine). verify_ai.py (Claude) can layer
    in richer REJECTs later; this is honest and needs no model call."""
    conf = v["confidence"]
    measured = (v.get("max_hail_in") or 0) > 0 or (v.get("max_wind_mph") or 0) > 0
    n = v.get("reports", 0)
    if conf == "HIGH" and measured:
        return {"verdict": "GO", "confidence": "HIGH", "claim_grade": True,
                "reason": f"Cross-verified across {n} reports — measured, claim-grade.", "flags": []}
    if conf == "HIGH":
        return {"verdict": "GO", "confidence": "HIGH", "claim_grade": True,
                "reason": "Corroborated across sources.", "flags": []}
    return {"verdict": "HOLD", "confidence": "MEDIUM", "claim_grade": False,
            "reason": "Single report — holding for corroboration before dispatching a crew.",
            "flags": ["awaiting a second source"]}


def build_feed():
    subprocess.run([sys.executable, "storm_poc.py"], cwd=HERE, check=True,
                   stdout=subprocess.DEVNULL, env={**os.environ})
    d = json.load(open(os.path.join(HERE, "last_run.json")))
    rel = [v for v in d["verified"] if v.get("roofing_relevant")]

    def trig(v):
        return v.get("trigger") or ("knock_all" if v.get("tornado") or v.get("grade") == "A"
                                    else "knock" if v["confidence"] == "HIGH" else "monitor")

    storms = []
    for v in rel:
        storms.append({
            "county": v["county"], "date": v["date"], "confidence": v["confidence"],
            "grade": v["grade"], "hazard": hazard_str(v),
            "sources": " + ".join(v.get("sources_hit", [])),
            "max_hail_in": v.get("max_hail_in"), "max_wind_mph": v.get("max_wind_mph"),
            "avg_hail_in": v.get("avg_hail_in"), "avg_wind_mph": v.get("avg_wind_mph"),
            "tornado": bool(v.get("tornado")), "trigger": trig(v),
            "lat": v.get("lat"), "lon": v.get("lon"), "ai": ai_verdict(v),
            "evidence": [{k: e.get(k) for k in EV_FIELDS} for e in v.get("evidence", [])][:14],
        })
    storms.sort(key=lambda s: (s["confidence"] == "HIGH",
                               s["tornado"] or (s.get("max_hail_in") or 0) >= 1.25,
                               s.get("max_hail_in") or 0, s.get("max_wind_mph") or 0), reverse=True)
    cleared = sum(1 for s in storms if s["ai"]["verdict"] == "GO")
    live_srcs = [{"label": s["label"], "tier": s["tier"], "status": "live", "note": s.get("note", "")}
                 for s in d["sources"] if s.get("enabled")]
    return {
        "generated": d["generated"], "state": d["state"], "window_days": d["window_days"],
        "totals": {"raw": d.get("raw_reports", 0), "verified": len(d["verified"]), "relevant": len(storms)},
        "ai_stats": {"cleared": cleared, "held": len(storms) - cleared},
        "sources": live_srcs,
        "triggers": [{"key": t["key"], "label": t["label"], "desc": t["desc"]} for t in d["triggers"]],
        "storms": storms,
        "outlook": outlook_block(),
    }


def main():
    url = os.environ.get("INGEST_URL")
    secret = os.environ.get("INGEST_SECRET")
    if not url or not secret:
        sys.exit("set INGEST_URL and INGEST_SECRET")
    feed = build_feed()
    body = json.dumps(feed).encode()
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers={"Content-Type": "application/json", "x-ingest-secret": secret,
                                          "User-Agent": "Mozilla/5.0 (compatible; StormVerified-Publisher/1.0)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        print(f"published {len(feed['storms'])} storms -> {r.status} {r.read().decode()}")


if __name__ == "__main__":
    main()
