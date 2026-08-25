#!/usr/bin/env python3
"""Ride OS — synthetic CareRoute Transport. Synthetic only, no real PHI."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(46)

FIRST = ["Marcus", "Dana", "Elena", "Ray", "Priya", "Jordan", "Tomas", "Nia"]
LAST = ["Whitfield", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel", "Osei"]
PURPOSES = ["dialysis", "chemo", "pt appointment", "primary care", "dental", "radiation"]
MESSAGES = [
    "need to reschedule tuesday's pickup to the afternoon",
    "the claim for last week's trips was denied",
    "the van was 40 minutes late and she missed the appointment",
    "what's the office number for the billing department",
]


def main():
    store.wipe()
    store.save("config", {"company": "CareRoute Transport", "vehicles": 18, "revenue": "$4M"})

    drivers = []
    for i in range(20):
        creds = {"license": iso(now() + timedelta(days=rng.randint(30, 700))),
                 "background": iso(now() + timedelta(days=rng.randint(30, 700))),
                 "cpr": iso(now() + timedelta(days=rng.randint(-20, 400)))}
        if rng.random() < 0.9:
            creds["securement"] = iso(now() + timedelta(days=rng.randint(-10, 500)))
        drivers.append({"id": f"dr_{i:02d}", "name": f"{rng.choice(FIRST)} {rng.choice(LAST)}",
                        "credentials": creds})
    drivers.append({"id": "dr_demo_lapsed", "name": "Ray Trujillo",
                    "credentials": {"license": iso(now() + timedelta(days=300)),
                                    "background": iso(now() + timedelta(days=300)),
                                    "cpr": iso(now() - timedelta(days=5))},
                    "demo_tag": "demo"})
    drivers.append({"id": "dr_demo_clean", "name": "Priya Okafor",
                    "credentials": {c: iso(now() + timedelta(days=300))
                                    for c in core.REQUIRED_CREDS}, "demo_tag": "demo"})
    store.save("drivers", drivers)

    trips = []
    for i in range(200):
        done = rng.random() < 0.6
        t = {"id": f"tp_{i:03d}", "patient_ref": f"PT-{rng.randint(1000, 9999)}",
             "purpose": rng.choice(PURPOSES), "amount": rng.choice([38, 52, 75]),
             "scheduled_at": iso(now() + timedelta(hours=rng.randint(-72, 48)))}
        if done:
            complete = rng.random() < 0.8
            t["completed_at"] = iso(now() - timedelta(days=rng.randint(0, 20)))
            t["trip_log"] = {"pickup_odo": 10000 + i, "dropoff_odo": 10012 + i,
                             "pickup_at": t["completed_at"], "dropoff_at": t["completed_at"],
                             "signature_ref": f"SIG-{i}" if complete else None}
            if complete and rng.random() < 0.7:
                t["billed_at"] = iso(now() - timedelta(days=rng.randint(0, 10)))
        trips.append(t)
    trips.append({"id": "tp_demo_dialysis", "patient_ref": "PT-4401", "purpose": "dialysis",
                  "amount": 52, "scheduled_at": iso(now() + timedelta(hours=18)),
                  "demo_tag": "demo"})
    trips.append({"id": "tp_demo_nolog", "patient_ref": "PT-4402", "purpose": "primary care",
                  "amount": 38, "completed_at": iso(now() - timedelta(days=1)),
                  "trip_log": {"pickup_odo": 22001, "dropoff_odo": None, "pickup_at": None,
                               "dropoff_at": None, "signature_ref": None}, "demo_tag": "demo"})
    trips.append({"id": "tp_demo_logged", "patient_ref": "PT-4403", "purpose": "dental",
                  "amount": 38, "completed_at": iso(now() - timedelta(days=1)),
                  "trip_log": {"pickup_odo": 30000, "dropoff_odo": 30014,
                               "pickup_at": iso(now() - timedelta(hours=30)),
                               "dropoff_at": iso(now() - timedelta(hours=29)),
                               "signature_ref": "SIG-D1"}, "demo_tag": "demo"})
    store.save("trips", trips)

    messages = [{"id": f"ms_{i:03d}", "from": rng.choice(FIRST), "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(1, 48)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages.append({"id": "ms_demo_cond", "from": "Elena (daughter)",
                     "text": "grandma seems confused today, more than usual",
                     "at": iso(now() - timedelta(minutes=12)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_bump", "from": "facility scheduler",
                     "trip_id": "tp_demo_dialysis",
                     "text": "can we move tomorrow's pickup to make room for another trip",
                     "at": iso(now() - timedelta(minutes=30)), "demo_tag": "demo"})
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None, {"trips": len(trips)})
    print(f"Seeded {len(drivers)} drivers, {len(trips)} trips, {len(messages)} messages")


if __name__ == "__main__":
    main()
