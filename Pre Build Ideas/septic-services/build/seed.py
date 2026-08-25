#!/usr/bin/env python3
"""Pump OS — synthetic Clearline Septic & Site Services. Synthetic only."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(33)

LAST = ["Whitfield", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel", "Osei",
        "Delacroix", "Yamada", "Pruitt", "Calloway", "Bostic", "Renner", "Iglesias", "Thorne"]
SITES = ["County WWTP", "Regional Receiving Station", "Northside Treatment"]
MESSAGES = [
    "it's been about three years, probably time to pump again",
    "is it the baffle or the leach field, what do you think",
    "need four porta johns for a wedding in june",
    "invoice looks right, check is out today",
]


def main():
    store.wipe()
    store.save("config", {"company": "Clearline Septic & Site Services", "revenue": "$5M",
                          "pump_trucks": 5, "portable_units": 320})

    customers = [{"id": f"cu_{i:03d}", "name": f"{rng.choice(LAST)} residence"} for i in range(400)]
    store.save("customers", customers)

    systems = []
    for i in range(400):
        has_record = rng.random() < 0.85
        systems.append({"id": f"sy_{i:03d}", "customer_name": customers[i]["name"],
                        "last_pumped": iso(now() - timedelta(days=rng.randint(200, 1800)))
                        if has_record else None,
                        "interval_years": rng.choice([2, 3, 3, 4]) if has_record else None})
    store.save("systems", systems)

    jobs = []
    for i in range(300):
        done = rng.random() < 0.8
        j = {"id": f"jb_{i:03d}", "customer_name": rng.choice(customers)["name"],
             "amount": rng.choice([385, 425, 495]),
             "done_at": iso(now() - timedelta(days=rng.randint(1, 60))) if done else None}
        if done:
            complete = rng.random() < 0.85
            j["disposal"] = {"gallons": rng.choice([1000, 1250, 1500]) if complete else None,
                             "disposal_site": rng.choice(SITES),
                             "manifest_ref": f"MF-{rng.randint(10000, 99999)}" if complete else None}
            if complete and rng.random() < 0.7:
                j["billed_at"] = iso(now() - timedelta(days=rng.randint(0, 20)))
        jobs.append(j)
    jobs.append({"id": "jb_demo_manifest", "customer_name": "Mercer residence", "amount": 425,
                 "done_at": iso(now() - timedelta(days=2)),
                 "disposal": {"gallons": 1250, "disposal_site": "County WWTP",
                              "manifest_ref": "MF-55120"}, "demo_tag": "demo"})
    jobs.append({"id": "jb_demo_nomanifest", "customer_name": "Osei residence", "amount": 425,
                 "done_at": iso(now() - timedelta(days=1)),
                 "disposal": {"gallons": 1000, "disposal_site": "County WWTP",
                              "manifest_ref": None}, "demo_tag": "demo"})
    jobs.append({"id": "jb_demo_landapp", "customer_name": "Havel farm", "amount": 900,
                 "done_at": iso(now() - timedelta(days=1)), "land_application": True,
                 "permit_ref": None,
                 "disposal": {"gallons": 3000, "disposal_site": "field spread",
                              "manifest_ref": "MF-55200"}, "demo_tag": "demo"})
    store.save("jobs", jobs)
    store.save("units", [{"id": f"un_{i:03d}", "status": rng.choice(["out", "yard", "yard"])}
                         for i in range(320)])

    messages = [{"id": f"ms_{i:03d}", "from": rng.choice(LAST), "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(2, 72)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages.append({"id": "ms_demo_backup", "from": "Renner residence",
                     "text": "sewage is backing up into the downstairs shower",
                     "at": iso(now() - timedelta(minutes=15)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_diag", "from": "Pruitt",
                     "text": "is it the baffle or the leach field, what do you think",
                     "at": iso(now() - timedelta(minutes=35)), "demo_tag": "demo"})
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None, {"jobs": len(jobs)})
    print(f"Seeded {len(customers)} customers, {len(systems)} systems, {len(jobs)} jobs, "
          f"{len(messages)} messages")


if __name__ == "__main__":
    main()
