#!/usr/bin/env python3
"""
Rollup — turn the crew-app's field logs (crew_state.json) into the storm-level
outcomes that feed the learning loop + ROI dashboard. This is the wire that makes
learning.py / roi.py run on REAL results instead of seed data: every "signed" tap
in the field becomes a job + revenue attributed to the storm it came off.

    python3 rollup.py            # crew_state.json -> outcomes_live.json
    # then: python3 learning.py / roi.py can read outcomes_live.json

Matches storms back to last_run.json (for hazard/magnitude/area). Falls back to
the storm key when a match isn't found.
"""
import json, os
from fl_places import BY_COUNTY


def storm_meta(county, date):
    if os.path.exists("last_run.json"):
        for v in json.load(open("last_run.json")).get("verified", []):
            if v["county"] == county and v["date"] == date:
                hz = "hail" if v.get("max_hail_in") else ("tornado" if v.get("tornado") else "wind")
                mag = v.get("max_hail_in") or v.get("max_wind_mph") or 0
                return hz, round(mag, 2)
    return "wind", 0


def main():
    if not os.path.exists("crew_state.json"):
        print("No crew_state.json yet — run the crew-app (crew_server.py) and log some doors first.")
        return
    doors = json.load(open("crew_state.json")).get("doors", [])
    by = {}
    for d in doors:
        key = d.get("storm", "?|?")
        county, _, date = key.partition("|")
        r = by.setdefault(key, {"county": county, "date": date, "doors": 0, "jobs": 0, "revenue": 0})
        r["doors"] += 1
        if d.get("status") == "signed":
            r["jobs"] += 1
            r["revenue"] += int(d.get("amount") or 0)

    storms = []
    for key, r in by.items():
        hz, mag = storm_meta(r["county"], r["date"])
        area = BY_COUNTY.get(r["county"], {}).get("name", r["county"])
        storms.append({"county": r["county"], "date": r["date"], "hazard": hz, "magnitude": mag,
                       "area": area, "doors": r["doors"], "jobs": r["jobs"], "revenue": r["revenue"]})

    out = {"_note": "LIVE field outcomes rolled up from the crew-app (crew_state.json).",
           "avg_trip_cost": 400, "monthly_cost": 30, "storms": storms}
    json.dump(out, open("outcomes_live.json", "w"), indent=2)
    tot_j = sum(s["jobs"] for s in storms); tot_r = sum(s["revenue"] for s in storms)
    print(f"outcomes_live.json — {len(storms)} storms, {sum(s['doors'] for s in storms)} doors, "
          f"{tot_j} jobs, ${tot_r:,} revenue (real field data).")
    print("  Point learning.py / roi.py at it:  cp outcomes_live.json outcomes.json  (or set the source).")


if __name__ == "__main__":
    main()
