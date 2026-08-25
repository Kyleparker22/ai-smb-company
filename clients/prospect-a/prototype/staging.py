#!/usr/bin/env python3
"""
Pre-storm staging — get crews positioned the DAY BEFORE. Pulls NOAA SPC
convective outlooks (day-1 + day-2), tests Florida metros against the risk
polygons, and flags where to stage so crews canvass the moment the storm clears —
before competitors even know it hit. Free NOAA data, no key.

Usage:  python3 staging.py            # SLGT+ staging recommendations
        MIN_RISK=MRGL python3 staging.py
"""
import json, os, urllib.request
from datetime import date
from fl_places import FL_PLACES

UA = {"User-Agent": "yourco-staging (founder@yourco.example.com)"}
RANK = {"TSTM": 1, "MRGL": 2, "SLGT": 3, "ENH": 4, "MDT": 5, "HIGH": 6}
NAME = {1: "General storms", 2: "Marginal", 3: "Slight", 4: "Enhanced", 5: "Moderate", 6: "High"}
MIN_RISK = RANK.get(os.environ.get("MIN_RISK", "SLGT").upper(), 3)


def _get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25) as r:
        return json.loads(r.read().decode())


def _pip(lon, lat, ring):
    inside, n, j = False, len(ring), len(ring) - 1
    for i in range(n):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def _in_geom(lon, lat, geom):
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    return any(_pip(lon, lat, poly[0]) for poly in polys)


def risk_for_day(day):
    url = f"https://www.spc.noaa.gov/products/outlook/day{day}otlk_cat.nolyr.geojson"
    try:
        feats = _get(url).get("features", [])
    except Exception:
        return {}
    out = {}
    for p in FL_PLACES:
        best = 0
        for f in feats:
            lvl = RANK.get(f["properties"].get("LABEL"), 0)
            if lvl > best and _in_geom(p["lon"], p["lat"], f["geometry"]):
                best = lvl
        if best:
            out[p["name"]] = best
    return out


def main():
    d1, d2 = risk_for_day(1), risk_for_day(2)
    print("=" * 60)
    print("  yourco · PRE-STORM STAGING — Florida (NOAA SPC outlook)")
    print("=" * 60)
    for label, day in (("TODAY (day 1)", d1), ("TOMORROW (day 2)", d2)):
        stage = {n: lvl for n, lvl in day.items() if lvl >= MIN_RISK}
        print(f"\n  {label}:")
        if not stage:
            print(f"    quiet — nothing at {NAME[MIN_RISK]}+ risk. No staging needed.")
            continue
        for n, lvl in sorted(stage.items(), key=lambda x: -x[1]):
            co = next(p["county"] for p in FL_PLACES if p["name"] == n)
            print(f"    ▸ STAGE {n} ({co} Co) — {NAME[lvl]} risk. Position a crew tonight; canvass as it clears.")
    print("\n  (Day-2 = tomorrow: pre-position now to beat everyone to the neighborhood.)")

    def rows(day):
        return sorted([{"name": n, "county": next(p["county"] for p in FL_PLACES if p["name"] == n),
                        "level": lvl, "label": NAME[lvl]} for n, lvl in day.items()], key=lambda r: -r["level"])
    data = {"generated": date.today().isoformat(), "min_risk": MIN_RISK,
            "day1": rows(d1), "day2": rows(d2)}
    open("staging_data.js", "w").write("window.STAGING = " + json.dumps(data, indent=2) + ";\n")


if __name__ == "__main__":
    main()
