#!/usr/bin/env python3
"""Rig OS — synthetic Blue Iron Crane & Rigging. Synthetic only."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(47)

FIRST = ["Marcus", "Dana", "Elena", "Ray", "Priya", "Jordan", "Tomas", "Nia"]
LAST = ["Whitfield", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel", "Osei"]
RFQS = [
    "set two hvac units on a strip mall roof, sunday morning closed",
    "hang steel for a two-story frame, open site",
    "set trusses over the occupied school gym wing",
    "lift a hot tub over a one-story ranch house, nobody home",
]


def main():
    store.wipe()
    store.save("config", {"company": "Blue Iron Crane & Rigging", "revenue": "$12M"})

    cranes = [
        {"id": "cr_00", "desc": "90-ton RT", "cert_class": "TLL"},
        {"id": "cr_01", "desc": "40-ton boom truck", "cert_class": "TSS"},
        {"id": "cr_02", "desc": "275-ton AT", "cert_class": "TLL"},
    ]
    store.save("cranes", cranes)

    operators = []
    for i in range(12):
        certs = {}
        if rng.random() < 0.8:
            certs["TSS"] = iso(now() + timedelta(days=rng.randint(-20, 600)))
        if rng.random() < 0.5:
            certs["TLL"] = iso(now() + timedelta(days=rng.randint(-10, 600)))
        operators.append({"id": f"op_{i:02d}", "name": f"{rng.choice(FIRST)} {rng.choice(LAST)}",
                          "certs": certs})
    operators.append({"id": "op_demo_tss", "name": "Ray Barrera",
                      "certs": {"TSS": iso(now() + timedelta(days=300))}, "demo_tag": "demo"})
    operators.append({"id": "op_demo_tll", "name": "Dana Okafor",
                      "certs": {"TSS": iso(now() + timedelta(days=300)),
                                "TLL": iso(now() + timedelta(days=250))}, "demo_tag": "demo"})
    store.save("operators", operators)

    rfqs = [{"id": f"rf_{i:03d}", "from": rng.choice(LAST), "text": t,
             "radius_ft": rng.choice([None, 40, 60, 85]),
             "weight_lbs": rng.choice([None, 8000, 22000, 46000]),
             "obstructions_noted": rng.choice([None, "power lines east", "clear approach"])}
            for i, t in enumerate(RFQS * 3)]
    rfqs.append({"id": "rf_demo_critical", "from": "Mercer GC",
                 "text": "set trusses over the occupied school gym wing",
                 "radius_ft": 70, "weight_lbs": 12000,
                 "obstructions_noted": "occupied wing under", "demo_tag": "demo"})
    rfqs.append({"id": "rf_demo_nodata", "from": "Havel Builders",
                 "text": "hang steel for a two-story frame, open site",
                 "radius_ft": None, "weight_lbs": None, "obstructions_noted": None,
                 "demo_tag": "demo"})
    rfqs.append({"id": "rf_demo_clean", "from": "Osei Mechanical",
                 "text": "set two hvac units on a strip mall roof, sunday morning closed",
                 "radius_ft": 55, "weight_lbs": 9000, "obstructions_noted": "clear approach",
                 "demo_tag": "demo"})
    store.save("rfqs", rfqs)

    lifts = []
    for i in range(30):
        done = rng.random() < 0.5
        l = {"id": f"lf_{i:03d}", "crane_id": rng.choice(cranes)["id"],
             "critical": rng.random() < 0.2, "wind_limit_mph": rng.choice([20, 25, 28]),
             "scheduled_at": iso(now() + timedelta(days=rng.randint(-10, 14)))}
        if l["critical"] and rng.random() < 0.7:
            l["lift_plan"] = {"ref": f"LP-{rng.randint(100, 999)}",
                              "signed_by": "R. Calloway, lift director"}
        if done:
            l["completed_at"] = iso(now() - timedelta(days=rng.randint(0, 20)))
        lifts.append(l)
    lifts.append({"id": "lf_demo_noplan", "crane_id": "cr_02", "critical": True,
                  "wind_limit_mph": 22, "demo_tag": "demo"})
    lifts.append({"id": "lf_demo_planned", "crane_id": "cr_02", "critical": True,
                  "wind_limit_mph": 22,
                  "lift_plan": {"ref": "LP-441", "signed_by": "R. Calloway, lift director"},
                  "demo_tag": "demo"})
    lifts.append({"id": "lf_demo_windy", "crane_id": "cr_00", "critical": False,
                  "wind_limit_mph": 20, "demo_tag": "demo"})
    store.save("lifts", lifts)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None, {"lifts": len(lifts)})
    print(f"Seeded {len(cranes)} cranes, {len(operators)} operators, {len(rfqs)} RFQs, "
          f"{len(lifts)} lifts")


if __name__ == "__main__":
    main()
