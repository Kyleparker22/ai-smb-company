#!/usr/bin/env python3
"""Hours OS — synthetic Redline Carriers. Synthetic only."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(45)

FIRST = ["Marcus", "Dana", "Elena", "Ray", "Priya", "Jordan", "Tomas", "Nia", "Sam", "Lena"]
LAST = ["Whitfield", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel", "Osei"]
LANES = ["Memphis turn", "Atlanta reefer", "Dallas dry van", "Nashville flatbed",
         "Louisville dedicated"]
MESSAGES = [
    "can marcus take the memphis load tonight",
    "been at the dock four hours, shipper says another two",
    "how many hours does dana have left today",
    "fuel card isn't working at the pilot",
]


def main():
    store.wipe()
    store.save("config", {"company": "Redline Carriers", "trucks": 22, "revenue": "$7M"})

    drivers = []
    for i in range(24):
        has_clock = rng.random() < 0.85
        drivers.append({"id": f"dr_{i:02d}", "name": f"{rng.choice(FIRST)} {rng.choice(LAST)}",
                        "hos_remaining_h": round(rng.uniform(1, 11), 1) if has_clock else None})
    drivers.append({"id": "dr_demo_short", "name": "Marcus Okafor", "hos_remaining_h": 3.0,
                    "demo_tag": "demo"})
    drivers.append({"id": "dr_demo_full", "name": "Dana Lindqvist", "hos_remaining_h": 10.5,
                    "demo_tag": "demo"})
    drivers.append({"id": "dr_demo_unknown", "name": "Ray Havel", "hos_remaining_h": None,
                    "demo_tag": "demo"})
    store.save("drivers", drivers)

    trucks = []
    for i in range(22):
        trucks.append({"id": f"tr_{i:02d}", "unit": f"unit {100 + i}",
                       "odometer": rng.randint(80000, 480000),
                       "service_due_odometer": rng.randint(85000, 490000)})
    trucks.append({"id": "tr_demo_oos", "unit": "unit 131", "odometer": 300000,
                   "service_due_odometer": 310000,
                   "oos_at": iso(now() - timedelta(days=2)), "demo_tag": "demo"})
    store.save("trucks", trucks)

    loads = []
    for i in range(60):
        done = rng.random() < 0.6
        l = {"id": f"ld_{i:03d}", "lane": rng.choice(LANES),
             "run_hours": round(rng.uniform(3, 10), 1),
             "free_time_h": 2, "detention_rate": 60}
        if done:
            arr = now() - timedelta(days=rng.randint(1, 20), hours=rng.randint(1, 10))
            l["arrived_at"] = iso(arr)
            if rng.random() < 0.9:
                l["departed_at"] = iso(arr + timedelta(hours=rng.uniform(0.5, 7)))
            if rng.random() < 0.5:
                l["detention_billed_at"] = iso(now() - timedelta(days=rng.randint(0, 10)))
        loads.append(l)
    loads.append({"id": "ld_demo_long", "lane": "Memphis turn", "run_hours": 8.0,
                  "free_time_h": 2, "detention_rate": 60, "demo_tag": "demo"})
    loads.append({"id": "ld_demo_short", "lane": "Louisville dedicated", "run_hours": 2.0,
                  "free_time_h": 2, "detention_rate": 60, "demo_tag": "demo"})
    loads.append({"id": "ld_demo_detention", "lane": "Atlanta reefer", "run_hours": 6.0,
                  "arrived_at": iso(now() - timedelta(hours=9)),
                  "departed_at": iso(now() - timedelta(hours=3)),
                  "free_time_h": 2, "detention_rate": 60, "demo_tag": "demo"})
    loads.append({"id": "ld_demo_nostamps", "lane": "Dallas dry van", "run_hours": 5.0,
                  "arrived_at": iso(now() - timedelta(hours=8)), "departed_at": None,
                  "free_time_h": 2, "detention_rate": 60, "demo_tag": "demo"})
    store.save("loads", loads)

    messages = [{"id": f"ms_{i:03d}", "from": rng.choice(FIRST),
                 "driver_id": f"dr_{rng.randint(0, 23):02d}", "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(1, 48)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages.append({"id": "ms_demo_log", "from": "a customer service rep", "driver_id": "dr_00",
                     "text": "can you fix his log from tuesday, he forgot to flag the break",
                     "at": iso(now() - timedelta(minutes=20)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_accident", "from": "Marcus",
                     "text": "we had an accident on i-40, everyone is ok",
                     "at": iso(now() - timedelta(minutes=8)), "demo_tag": "demo"})
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None, {"loads": len(loads)})
    print(f"Seeded {len(drivers)} drivers, {len(trucks)} trucks, {len(loads)} loads, "
          f"{len(messages)} messages")


if __name__ == "__main__":
    main()
