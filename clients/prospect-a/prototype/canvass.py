#!/usr/bin/env python3
"""
Canvass planner — turn a verified storm into a crew standing at the right door
with proof in hand:
  · swath stops around the impact (production: HailTrace/MESH swath polygons)
  · property overlay so the highest-ROI doors surface (property.py)
  · nearest-neighbor route so the crew drives the least
  · a door-knock script with the NOAA proof baked in

Usage:  python3 canvass.py [County]        # default = top storm in last_run.json
        python3 canvass.py Duval
"""
import hashlib, json, math, sys
from property import enrich

STREETS = ["Oak", "Palmetto", "Magnolia", "Cypress", "Heron", "Sabal",
           "Live Oak", "Mangrove", "Bayshore", "Ibis", "Egret", "Sawgrass"]


def _h(*a):
    return int(hashlib.md5("|".join(map(str, a)).encode()).hexdigest(), 16)


def haz(v):
    b = []
    if v.get("max_hail_in"):  b.append(f'{v["max_hail_in"]:.2f}" hail')
    if v.get("max_wind_mph"): b.append(f'{v["max_wind_mph"]:.0f}mph wind')
    if v.get("tornado"):      b.append("a tornado")
    return " and ".join(b) or "storm damage"


def pick(county=None):
    d = json.load(open("last_run.json"))
    rel = [v for v in d["verified"] if v["roofing_relevant"]]
    if not rel:
        sys.exit("No roofing-relevant storms in last_run.json.")
    if county:
        c = [v for v in rel if v["county"].lower() == county.lower()]
        if not c:
            sys.exit(f"No roofing-relevant storm in {county}.")
        return sorted(c, key=lambda v: v["reports"], reverse=True)[0]
    return rel[0]


def gen_stops(v, n=10):
    lat, lon = v.get("lat") or 28.5, v.get("lon") or -81.4
    stops = []
    for i in range(n):
        h = _h(v["county"], v["date"], i)
        dlat = ((h % 1000) / 1000 - 0.5) * 0.06          # ~±3km swath spread
        dlon = (((h // 1000) % 1000) / 1000 - 0.5) * 0.06
        stops.append(enrich({
            "id": i + 1, "address": f"{100 + (h // 7 % 900)} {STREETS[h % len(STREETS)]} St",
            "lat": round(lat + dlat, 4), "lon": round(lon + dlon, 4)}))
    return stops


def route(stops, start):
    rem, cur, order = stops[:], {"lat": start[0], "lon": start[1]}, []
    while rem:
        nxt = min(rem, key=lambda s: math.hypot(cur["lat"] - s["lat"], cur["lon"] - s["lon"]))
        order.append(nxt); rem.remove(nxt); cur = nxt
    return order


def main():
    county = sys.argv[1] if len(sys.argv) > 1 else None
    v = pick(county)
    stops = gen_stops(v)
    start = (v.get("lat") or 28.5, v.get("lon") or -81.4)
    ordered = route(stops, start)
    top = sorted(stops, key=lambda s: -s["priority"])[:3]
    scr = (f"Hi, I'm with Prospect A Roofing. On {v['date']} NOAA verified {haz(v)} "
           f"right here in {v['county']} County. We're doing free 15-minute storm-damage "
           f"inspections — hail/wind this size cracks shingles even when the roof looks fine "
           f"from the ground. I can show you the official NOAA report. No obligation — want me "
           f"to take a quick look?")

    print("=" * 62)
    print(f"  CANVASS PLAN — {v['county']} County · {v['date']} · {haz(v)}")
    print("=" * 62)
    print(f"  Optimized route ({len(ordered)} stops, least driving):")
    for i, s in enumerate(ordered, 1):
        p = s["property"]
        print(f"   {i:>2}. {s['address']:16} · roof {p['roof_age']}yr · ${p['home_value']//1000}k"
              f"{' · owner' if p['owner_occupied'] else ' · rental'} · priority {s['priority']}")
    print(f"\n  ★ Top targets (knock these first — highest-ROI doors):")
    for s in top:
        print(f"     {s['address']} — priority {s['priority']} (roof {s['property']['roof_age']}yr, ${s['property']['home_value']//1000}k)")
    print(f"\n  Door-knock script (NOAA proof baked in):")
    print(f"   “{scr}”")

    out = {"county": v["county"], "date": v["date"], "hazard": haz(v),
           "center": [start[0], start[1]], "route": ordered,
           "top_targets": [s["id"] for s in top], "script": scr}
    fn = f"canvass_{v['county'].replace(' ', '')}_{v['date']}.json"
    json.dump(out, open(fn, "w"), indent=2)
    # visual snapshot for canvass.html (committed like demo_data.js so the page opens standalone)
    open("canvass_data.js", "w").write("window.CANVASS = " + json.dumps(out, indent=2) + ";\n")
    print(f"\n  (saved -> {fn} + canvass_data.js · addresses are demo swath points; connect HailTrace swaths + a parcel feed for real streets)")


if __name__ == "__main__":
    main()
