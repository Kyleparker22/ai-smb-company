#!/usr/bin/env python3
"""Yard OS — synthetic rental house. `python3 seed.py [--rentals 900]`.

"Blue Heron Equipment Rental" — ~650 units in 8 classes, 12 months of rentals
incl. off-rent-called-still-out rows, damage cases with and without evidence
pairs, calls incl. the 4:50pm off-rent. Synthetic only.
"""
import argparse, random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(15)

CLASSES = {"mini_excavator": 140, "skid_steer": 220, "scissor_lift": 160, "boom_lift": 210,
           "generator": 85, "compactor": 95, "trencher": 120, "light_tower": 70}
FLEET_COUNTS = {"mini_excavator": 90, "skid_steer": 110, "scissor_lift": 80, "boom_lift": 60,
                "generator": 120, "compactor": 70, "trencher": 50, "light_tower": 65}
CUSTOMERS = ["Harlow Build Group", "Crestline Constructors", "Bandera Landscapes", "city parks dept",
             "Palmetto Paving", "Ironvale Concrete", "Sunbelt Fence", "weekend homeowner",
             "Redbud Roofing", "Vantage Utilities", "Halstead Grading", "Bluebonnet Events"]
DAMAGE_KINDS = ["bent boom section", "cracked window", "torn seat", "hydraulic hose cut",
                "tire sidewall gash", "dented panel"]
CALLS = [
    "we're done with the mini ex, come get it",
    "the skid steer won't start this morning",
    "we need to keep the compactor another week",
    "do you have a 5k generator available next monday",
    "can you email me the invoice from last month",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rentals", type=int, default=900)
    args = ap.parse_args()

    store.wipe()
    store.save("config", {"company": "Blue Heron Equipment Rental", "revenue": "$9M",
                          "rms": "modelled, not connected"})

    fleet = []
    for cls, n in FLEET_COUNTS.items():
        for i in range(n):
            fleet.append({"id": f"un_{cls[:4]}{i:03d}", "cls": cls})
    store.save("fleet", fleet)

    customers = [{"id": f"cu_{i:03d}", "name": n} for i, n in enumerate(CUSTOMERS)]
    store.save("customers", customers)

    rentals, conditions = [], []
    for i in range(args.rentals):
        cls = rng.choice(list(CLASSES))
        unit = rng.choice([u for u in fleet if u["cls"] == cls])
        start = now() - timedelta(days=rng.randint(2, 360))
        dur = rng.randint(2, 45)
        r = {"id": f"rn_{i:04d}", "unit_id": unit["id"], "cls": cls,
             "customer_id": rng.choice(customers)["id"],
             "day_rate": CLASSES[cls] * rng.uniform(0.9, 1.15),
             "on_rent_at": iso(start)}
        r["day_rate"] = round(r["day_rate"], 2)
        ended = start + timedelta(days=dur)
        if ended < now():
            r["off_rent_called_at"] = iso(ended)
            if rng.random() < 0.9:
                r["picked_up_at"] = iso(ended + timedelta(days=rng.randint(0, 4)))
            # condition records: most have both, a slice miss one
            has_out = rng.random() < 0.85
            has_in = rng.random() < 0.9
            dmg = rng.random() < 0.12
            if has_out:
                conditions.append({"id": store.nid("cd"), "rental_id": r["id"], "kind": "checkout",
                                   "photos": rng.randint(2, 8), "damage": []})
            if has_in and r.get("picked_up_at"):
                conditions.append({"id": store.nid("cd"), "rental_id": r["id"], "kind": "checkin",
                                   "photos": rng.randint(2, 8),
                                   "damage": [rng.choice(DAMAGE_KINDS)] if dmg else []})
            if dmg:
                r["damage_suspected"] = True
        rentals.append(r)

    # demo rows
    rentals.append({"id": "rn_demo_offrent", "unit_id": fleet[0]["id"], "cls": fleet[0]["cls"],
                    "customer_id": customers[0]["id"], "day_rate": 145.0,
                    "on_rent_at": iso(now() - timedelta(days=12)), "demo_tag": "demo"})
    # damage with full evidence
    rentals.append({"id": "rn_demo_evidence", "unit_id": fleet[1]["id"], "cls": fleet[1]["cls"],
                    "customer_id": customers[1]["id"], "day_rate": 210.0,
                    "on_rent_at": iso(now() - timedelta(days=30)),
                    "off_rent_called_at": iso(now() - timedelta(days=3)),
                    "picked_up_at": iso(now() - timedelta(days=2)),
                    "damage_suspected": True, "demo_tag": "demo"})
    conditions.append({"id": "cd_demo_out", "rental_id": "rn_demo_evidence", "kind": "checkout",
                       "photos": 6, "damage": []})
    conditions.append({"id": "cd_demo_in", "rental_id": "rn_demo_evidence", "kind": "checkin",
                       "photos": 7, "damage": ["bent boom section"]})
    # damage with NO checkout record
    rentals.append({"id": "rn_demo_noevidence", "unit_id": fleet[2]["id"], "cls": fleet[2]["cls"],
                    "customer_id": customers[2]["id"], "day_rate": 180.0,
                    "on_rent_at": iso(now() - timedelta(days=25)),
                    "off_rent_called_at": iso(now() - timedelta(days=2)),
                    "picked_up_at": iso(now() - timedelta(days=1)),
                    "damage_suspected": True, "demo_tag": "demo"})
    conditions.append({"id": "cd_demo_in2", "rental_id": "rn_demo_noevidence", "kind": "checkin",
                       "photos": 3, "damage": ["cracked window"]})

    calls = [{"id": f"cl_{i:03d}", "transcript": t,
              "at": iso(now() - timedelta(hours=rng.randint(2, 48)))}
             for i, t in enumerate(CALLS)]
    calls.append({"id": "cl_demo", "transcript": "we're done with the mini ex, come get it",
                  "rental_id": "rn_demo_offrent",
                  "at": iso(now().replace(hour=16, minute=50, second=0))})

    store.save("rentals", rentals)
    store.save("conditions", conditions)
    store.save("calls", calls)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"fleet": len(fleet), "rentals": len(rentals)})
    print(f"Seeded {len(fleet)} units, {len(rentals)} rentals, {len(conditions)} condition records, "
          f"{len(calls)} calls")


if __name__ == "__main__":
    main()
