#!/usr/bin/env python3
"""Cab OS — synthetic Vertex Elevator Service. Synthetic only."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(40)

BUILDINGS = ["Meridian Tower", "Harborview Medical", "Cedar Mill Lofts", "Northgate Plaza",
             "Lakeside Courts", "Fifth Street Garage"]
CALLS = [
    "the service elevator is down again at the loading dock",
    "there's a grinding noise on the ride up",
    "when is our cat 1 test due this year",
    "invoice received, processing this week",
]


def main():
    store.wipe()
    store.save("config", {"company": "Vertex Elevator Service", "revenue": "$11M",
                          "mechanics": 28})

    buildings = []
    for i, name in enumerate(BUILDINGS * 15):
        buildings.append({
            "id": f"bd_{i:03d}", "name": f"{name} {i}",
            "contract": {
                "includes": [{"id": "M-1", "covers": ["door_operator", "controller"],
                              "text": "adjustment and repair of door operators and controllers"}],
                "excludes": [{"id": "X-2", "covers": ["vandalism", "lamp_cosmetic"],
                              "text": "vandalism, cosmetic items, lamps and buttons are billable"},
                             {"id": "X-3", "covers": ["modernization"],
                              "text": "modernization and equipment replacement are quoted separately"}],
            }})
    store.save("buildings", buildings)

    units = []
    for i in range(380):
        b = rng.choice(buildings)
        has_cat1 = rng.random() < 0.85
        u = {"id": f"un_{i:03d}", "building_id": b["id"], "building": b["name"],
             "kind": rng.choice(["traction", "hydro", "escalator"]),
             "tests": {}}
        if has_cat1:
            u["tests"]["cat1"] = iso(now() - timedelta(days=rng.randint(30, 500)))
        if rng.random() < 0.7:
            u["tests"]["cat5"] = iso(now() - timedelta(days=rng.randint(200, 2000)))
        units.append(u)
    units.append({"id": "un_demo_red", "building_id": buildings[0]["id"],
                  "building": buildings[0]["name"], "kind": "traction",
                  "tests": {"cat1": iso(now() - timedelta(days=100))},
                  "red_tagged_at": iso(now() - timedelta(days=2)), "demo_tag": "demo"})
    units.append({"id": "un_demo_unknown", "building_id": buildings[1]["id"],
                  "building": buildings[1]["name"], "kind": "hydro", "tests": {},
                  "demo_tag": "demo"})
    store.save("units", units)

    calls = [{"id": f"cl_{i:03d}", "from": rng.choice(BUILDINGS),
              "unit_id": rng.choice(units[:380])["id"], "text": t,
              "at": iso(now() - timedelta(hours=rng.randint(1, 72)))}
             for i, t in enumerate(CALLS * 3)]
    calls.append({"id": "cl_demo_entrap", "from": "Harborview Medical",
                  "text": "we're stuck in the elevator at the medical building",
                  "at": iso(now() - timedelta(minutes=3)), "demo_tag": "demo"})
    store.save("calls", calls)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None, {"units": len(units)})
    print(f"Seeded {len(buildings)} buildings, {len(units)} units, {len(calls)} calls")


if __name__ == "__main__":
    main()
