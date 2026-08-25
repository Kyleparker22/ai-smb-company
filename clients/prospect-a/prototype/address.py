#!/usr/bin/env python3
"""
Address → best storm date (last 12 months). Type a property address, get the
strongest verified storm over it within the claim-filing window (you get ~1 year
to file). Geocodes the address (free US Census geocoder), searches the 12-month
storm-history cache (history.py) near that point, ranks by severity, and returns
the best storm date + how many days are left to file.

    python3 address.py "400 Magnolia Ave, Panama City, FL"
    python3 address.py --emit "1 Independent Dr, Jacksonville, FL"   # write address_data.js for the demo page
"""
import json, math, os, sys, urllib.request, urllib.parse
from datetime import date

UA = {"User-Agent": "yourco-address (founder@yourco.example.com)"}
HIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "storm_history.json")


def geocode(addr):
    url = ("https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress?"
           + urllib.parse.urlencode({"address": addr, "benchmark": "Public_AR_Current",
                                     "vintage": "Current_Current", "format": "json"}))
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25) as r:
            d = json.loads(r.read().decode())
    except Exception:
        return None
    m = d.get("result", {}).get("addressMatches", [])
    if not m:
        return None
    a = m[0]; c = a["coordinates"]
    co = ((a.get("geographies", {}).get("Counties") or [{}])[0].get("BASENAME"))
    return {"matched": a["matchedAddress"], "lat": c["y"], "lon": c["x"], "county": co}


def miles(la1, lo1, la2, lo2):
    p = math.pi / 180
    x = math.sin((la2 - la1) * p / 2) ** 2 + math.cos(la1 * p) * math.cos(la2 * p) * math.sin((lo2 - lo1) * p / 2) ** 2
    return 2 * 3959 * math.asin(math.sqrt(x))


def severity(r):
    if r["hazard"] == "tornado": return 80.0
    if r["hazard"] == "hail":    return (r["value"] or 0) * 55
    return (r["value"] or 55) * 0.8 if r["value"] else 45.0   # wind


def hazstr(r):
    if r["hazard"] == "hail": return f'{r["value"]:.2f}" hail' if r["value"] else "hail"
    if r["hazard"] == "wind": return f'{r["value"]:.0f} mph wind' if r["value"] else "wind damage"
    return "tornado"


def lookup(addr, radius=15):
    g = geocode(addr)
    if not g:
        return {"error": "Address not found. Try a full street address."}
    if not os.path.exists(HIST):
        return {"error": "No storm history cache — run history.py first."}
    hist = json.load(open(HIST))["reports"]
    today = date.today()
    near = []
    for r in hist:
        if r["lat"] is None:
            continue
        dist = miles(g["lat"], g["lon"], r["lat"], r["lon"])
        if dist > radius:
            continue
        try:
            days = (today - date.fromisoformat(r["date"])).days
        except ValueError:
            continue
        if days < 0 or days > 365:
            continue
        near.append({**r, "dist": round(dist, 1), "days_ago": days, "claim_days_left": 365 - days,
                     "severity": round(severity(r), 1), "hazard_str": hazstr(r)})
    near.sort(key=lambda x: (-x["severity"], x["days_ago"]))
    return {"address": g, "radius": radius, "best": near[0] if near else None,
            "alternates": near[1:5], "count": len(near)}


def main():
    emit = "--emit" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--emit"]
    if not args:
        sys.exit('Usage: python3 address.py "400 Magnolia Ave, Panama City, FL"')
    res = lookup(" ".join(args))
    if emit:
        open("address_data.js", "w").write("window.ADDRESS = " + json.dumps(res, indent=2) + ";\n")
        print("address_data.js written.")
    if res.get("error"):
        print(res["error"]); return
    b = res["best"]
    print(f"\n  {res['address']['matched']}  ({res['address']['county']} County)")
    print(f"  {res['count']} storm reports within {res['radius']} mi in the last 12 months.\n")
    if not b:
        print("  No qualifying storm at this address in the claim window."); return
    print(f"  ★ BEST CLAIM DATE: {b['date']} — {b['hazard_str']}")
    print(f"    {b['dist']} mi away · {b['days_ago']} days ago · {b['claim_days_left']} days left to file")
    print(f"    {b['reporter']}: {b.get('remark') or ''}")
    if res["alternates"]:
        print("\n  Other dates in window:")
        for a in res["alternates"]:
            print(f"    {a['date']} — {a['hazard_str']} ({a['dist']}mi, {a['claim_days_left']}d left)")


if __name__ == "__main__":
    main()
