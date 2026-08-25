#!/usr/bin/env python3
"""Bay OS — synthetic shop. `python3 seed.py [--ros 4300]`.

"Cedar Ridge Auto Care" — 8 bays, $3.2M, 18 months of ROs, declined items at
every age and class, seeded comebacks, calls including an undriveable one.
Synthetic only; 555 phones.
"""
import argparse, random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(12)

FIRST = ["Avery", "Jordan", "Sam", "Riley", "Casey", "Morgan", "Drew", "Quinn", "Reese", "Sawyer",
         "Marisol", "Deshawn", "Priya", "Kenji", "Elena", "Marcus", "Tanya", "Cole", "Nina", "Omar"]
LAST = ["Whitfield", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel", "Osei",
        "Delacroix", "Yamada", "Pruitt", "Calloway", "Bostic", "Renner", "Iglesias", "Thorne"]
VEHICLES = [("Toyota", "Camry"), ("Honda", "CR-V"), ("Ford", "F-150"), ("Chevy", "Silverado"),
            ("Subaru", "Outback"), ("Honda", "Civic"), ("Toyota", "RAV4"), ("Jeep", "Wrangler"),
            ("Hyundai", "Sonata"), ("Nissan", "Altima")]
SYSTEMS = ["brakes", "engine", "electrical", "suspension", "hvac", "maintenance", "tires", "transmission"]
KINDS = {"oil_service": (70, 130), "brake_job": (380, 900), "diagnostic": (140, 190),
         "timing_service": (900, 1900), "suspension": (450, 1400), "hvac": (250, 1200),
         "tires": (500, 1100), "tune_up": (300, 700)}

DECLINED_TEXTS = [
    ("front brake pads 2mm, rotors scored, caliper sticking", 780, "safety"),
    ("both rear tires worn to 2/32, cord showing on inner edge", 620, "safety"),
    ("inner tie rod has play, alignment off", 540, "safety"),
    ("left front wheel bearing growl, play at 12 and 6", 480, "safety"),
    ("fuel line weeping at the rail", 390, "safety"),
    ("engine air filter at 70%", 45, "defer"),
    ("coolant service due by mileage", 190, "defer"),
    ("valve cover gasket seeping, monitor", 320, "defer"),
    ("serpentine belt aging", 140, "defer"),
    ("battery marginal on load test", 210, "defer"),
    ("spark plugs due by mileage", 340, "defer"),
    ("cabin air filter dirty", 60, "cosmetic"),
    ("wiper blades streaking", 40, "cosmetic"),
    ("customer states noise sometimes", 0, "review"),
]

CALLS = [
    "my brakes are to the floor, I can barely stop the car",
    "can I book an oil change for thursday",
    "how much is a brake job on a 2019 CR-V",
    "what's wrong with my car? it makes a clicking noise, is it the alternator",
    "need to schedule the 60k service",
    "do you do alignments, what does it cost",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ros", type=int, default=1400)
    args = ap.parse_args()

    store.wipe()
    store.save("config", {"company": "Cedar Ridge Auto Care", "bays": 8, "revenue": "$3.2M",
                          "sms": "modelled, not connected", "dms": "modelled, not connected"})

    customers, vehicles = [], []
    for i in range(min(700, args.ros)):
        cid = f"cu_{i:04d}"
        customers.append({"id": cid, "name": f"{rng.choice(FIRST)} {rng.choice(LAST)}",
                          "phone": f"555-{rng.randint(200,999)}-{rng.randint(1000,9999)}"})
        mk, md = rng.choice(VEHICLES)
        vehicles.append({"id": f"vh_{i:04d}", "customer_id": cid,
                         "desc": f"{rng.randint(2012,2024)} {mk} {md}"})

    ros, declined = [], []
    for i in range(args.ros):
        v = rng.choice(vehicles)
        kind = rng.choice(list(KINDS))
        lo, hi = KINDS[kind]
        closed = now() - timedelta(days=rng.randint(1, 540))
        state = rng.choices(["closed", "presented"], weights=[0.9, 0.1])[0]
        ro = {"id": f"ro_{i:05d}", "vehicle_id": v["id"], "customer_id": v["customer_id"],
              "kind": kind, "system": rng.choice(SYSTEMS),
              "total": round(rng.uniform(lo, hi), 2), "state": state,
              "presented_at": iso(closed - timedelta(days=rng.randint(0, 2)))}
        if state == "closed":
            ro["closed_at"] = iso(closed)
        ros.append(ro)
        # declined items on ~35% of ROs
        if rng.random() < 0.35:
            t, val, _ = rng.choice(DECLINED_TEXTS)
            declined.append({"id": store.nid("dc"), "ro_id": ro["id"], "vehicle_id": v["id"],
                            "customer_id": v["customer_id"], "text": t, "value": val,
                            "declined_at": iso(closed),
                            "recovered_at": iso(closed + timedelta(days=rng.randint(10, 90)))
                                            if rng.random() < 0.12 else None})

    # seeded comebacks: same vehicle+system pairs close together
    for i in range(30):
        v = rng.choice(vehicles)
        base = now() - timedelta(days=rng.randint(20, 150))
        for j, gap in enumerate((0, rng.randint(5, 25))):
            ros.append({"id": f"ro_cb{i:03d}_{j}", "vehicle_id": v["id"],
                        "customer_id": v["customer_id"], "kind": "brake_job",
                        "system": "brakes", "total": round(rng.uniform(380, 900), 2),
                        "state": "closed", "closed_at": iso(base + timedelta(days=gap)),
                        "presented_at": iso(base + timedelta(days=gap - 1))})

    # demo rows
    declined.append({"id": "dc_demo_safety", "ro_id": "ro_demo", "vehicle_id": vehicles[0]["id"],
                     "customer_id": vehicles[0]["customer_id"], "demo_tag": "demo",
                     "text": "front brake pads 2mm, rotors scored, caliper sticking",
                     "value": 780, "declined_at": iso(now() - timedelta(days=50)),
                     "label": "safety_critical", "why": "braking system"})
    declined.append({"id": "dc_demo_defer", "ro_id": "ro_demo2", "vehicle_id": vehicles[1]["id"],
                     "customer_id": vehicles[1]["customer_id"], "demo_tag": "demo",
                     "text": "coolant service due by mileage", "value": 190,
                     "declined_at": iso(now() - timedelta(days=50)),
                     "label": "deferrable", "why": "fluid service"})

    calls = [{"id": f"cl_{i:03d}", "transcript": t, "at": iso(now() - timedelta(hours=rng.randint(1, 72)))}
             for i, t in enumerate(CALLS)]

    store.save("customers", customers)
    store.save("vehicles", vehicles)
    store.save("ros", ros)
    store.save("declined", declined)
    store.save("calls", calls)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"ros": len(ros), "declined": len(declined)})
    print(f"Seeded {len(ros)} ROs, {len(declined)} declined items, {len(calls)} calls")


if __name__ == "__main__":
    main()
