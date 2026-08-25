#!/usr/bin/env python3
"""
Build a 12-month storm-history cache for the claim-date lookup (address.py).
Pulls NOAA Local Storm Reports (via IEM) for the state, chunked by month so no
single request is huge, keeps hail/wind/tornado, and writes storm_history.json.

Production swaps in Xweather's historical storm reports by lat/lon + radius; this
free NOAA pull proves the tool.

    python3 history.py            # last 12 months, FL
    MONTHS=6 STATE=FL python3 history.py
"""
import json, os, urllib.request, urllib.parse
from datetime import date, timedelta

STATE = os.environ.get("STATE", "FL").upper()
MONTHS = int(os.environ.get("MONTHS", "12"))
UA = {"User-Agent": "yourco-history (founder@yourco.example.com)"}


def _hazard(t):
    t = (t or "").upper()
    if "TORNADO" in t: return "tornado"
    if "HAIL" in t: return "hail"
    if "MARINE" in t: return None
    if "WND" in t or "WIND" in t: return "wind"
    return None


def fetch(sts, ets):
    url = ("https://mesonet.agron.iastate.edu/geojson/lsr.geojson?"
           + urllib.parse.urlencode({"sts": sts, "ets": ets, "states": STATE}))
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=45) as r:
            return json.loads(r.read().decode()).get("features", [])
    except Exception as e:
        print(f"  (chunk {sts[:10]} failed: {e})"); return []


def main():
    today = date.today()
    start = today - timedelta(days=MONTHS * 31)
    out, cur = [], start
    while cur < today:
        nxt = min(cur + timedelta(days=31), today)
        feats = fetch(cur.strftime("%Y-%m-%dT00:00Z"), nxt.strftime("%Y-%m-%dT23:59Z"))
        for f in feats:
            p = f.get("properties", {})
            hz = _hazard(p.get("typetext"))
            if hz is None:
                continue
            geom = (f.get("geometry") or {}).get("coordinates") or [None, None]
            if geom[0] is None:
                continue
            mag, unit = p.get("magnitude"), (p.get("unit") or "").upper()
            val = None
            try:
                m = float(mag)
                val = m if hz == "hail" else (m * 1.15 if unit.startswith("K") else m)
            except (TypeError, ValueError):
                val = None
            out.append({"date": (p.get("valid") or "")[:10], "hazard": hz, "value": val,
                        "county": (p.get("county") or "").strip(), "city": p.get("city"),
                        "lat": geom[1], "lon": geom[0], "reporter": p.get("source"),
                        "qualifier": (p.get("qualifier") or "").upper(), "remark": p.get("remark")})
        print(f"  {cur:%Y-%m} … {len(out)} reports so far")
        cur = nxt
    json.dump({"state": STATE, "generated": today.isoformat(), "months": MONTHS, "reports": out},
              open("storm_history.json", "w"))
    print(f"storm_history.json — {len(out)} {STATE} hail/wind/tornado reports over {MONTHS} months.")


if __name__ == "__main__":
    main()
