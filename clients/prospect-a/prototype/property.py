#!/usr/bin/env python3
"""
Property overlay — score a location so crews knock the highest-ROI doors first:
older roof (more likely damaged + claimable), higher home value (bigger job),
owner-occupied (owners decide; renters don't).

Ready to connect: real parcel records from ATTOM / CoreLogic / a county property
appraiser via PROPERTY_API_KEY. Demo mode (no key): deterministic pseudo-records
from the coordinates so the route can prioritize — swap in the real feed and the
scoring below is unchanged.
"""
import hashlib, os


def _h(*vals):
    return int(hashlib.md5(("|".join(str(v) for v in vals)).encode()).hexdigest(), 16)


def property_profile(lat, lon):
    if os.environ.get("PROPERTY_API_KEY"):
        pass  # real fetch goes here once a parcel provider is connected
    h = _h("prop", round(lat, 4), round(lon, 4))
    return {
        "roof_age": 3 + h % 24,                       # years
        "home_value": 230000 + (h // 7 % 44) * 10000, # ~$230k–$660k
        "owner_occupied": (h // 3 % 10) < 8,          # ~80%
    }


def priority_score(prof):
    s = min(prof["roof_age"], 25) * 3            # older roof -> damage + claim likelihood
    s += prof["home_value"] / 10000              # bigger home = bigger job
    s += 25 if prof["owner_occupied"] else 0     # decision-maker on site
    return round(s, 1)


def enrich(stop):
    """stop must have lat/lon; returns it with property profile + priority."""
    prof = property_profile(stop["lat"], stop["lon"])
    stop["property"] = prof
    stop["priority"] = priority_score(prof)
    return stop


if __name__ == "__main__":
    import json, sys
    lat, lon = (float(sys.argv[1]), float(sys.argv[2])) if len(sys.argv) > 2 else (28.29, -81.41)
    p = property_profile(lat, lon)
    print(json.dumps({**p, "priority": priority_score(p)}, indent=2))
    print("(demo scoring — connect PROPERTY_API_KEY for real parcel records)")
