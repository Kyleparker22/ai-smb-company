#!/usr/bin/env python3
"""Canopy OS — synthetic Hartwood Tree Company. `python3 seed.py`. Synthetic only."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(32)

LAST = ["Whitfield", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel", "Osei",
        "Delacroix", "Yamada", "Pruitt", "Calloway", "Bostic", "Renner", "Iglesias", "Thorne"]
WORK = [("remove two dead ash near the drive", 2800), ("crown reduction on the front maple", 1400),
        ("stump grinding, three stumps", 650), ("takedown of storm-split oak", 3900),
        ("trim the pin oaks off the roofline", 1100)]
MESSAGES = [
    "is my oak safe? it's leaning more than last year",
    "how much to remove two trees in the backyard",
    "what day is the crew coming this week",
    "thanks, yard looks great",
]


def main():
    store.wipe()
    store.save("config", {"company": "Hartwood Tree Company", "revenue": "$4M",
                          "crews": 4, "crane": 1})

    customers = [{"id": f"cu_{i:03d}", "name": f"{rng.choice(LAST)} residence"} for i in range(260)]
    store.save("customers", customers)

    jobs = []
    for i in range(120):
        near = rng.random() < 0.2
        jobs.append({"id": f"jb_{i:03d}", "customer_id": rng.choice(customers)["id"],
                     "desc": rng.choice(WORK)[0], "near_powerlines": near,
                     "utility_clearance_ref": (f"UC-{rng.randint(1000,9999)}"
                                               if near and rng.random() < 0.6 else None)})
    jobs.append({"id": "jb_demo_lines", "customer_id": "cu_000",
                 "desc": "takedown between the service drop and the garage",
                 "near_powerlines": True, "utility_clearance_ref": None, "demo_tag": "demo"})
    jobs.append({"id": "jb_demo_clear", "customer_id": "cu_001",
                 "desc": "backyard maple removal", "near_powerlines": False, "demo_tag": "demo"})
    store.save("jobs", jobs)

    estimates = []
    for i in range(70):
        desc, amt = rng.choice(WORK)
        estimates.append({"id": f"es_{i:03d}", "customer_name": rng.choice(LAST), "desc": desc,
                          "amount": amt + rng.randint(-200, 400),
                          "sent_at": iso(now() - timedelta(days=rng.randint(2, 45)))})
    store.save("estimates", estimates)

    phc = [{"id": f"ph_{i:03d}", "customer_name": rng.choice(LAST),
            "program": rng.choice(["oak treatment", "deep-root feed", "spray program"]),
            "next_due": iso(now() + timedelta(days=rng.randint(-10, 60)))}
           for i in range(40)]
    store.save("phc", phc)

    messages = [{"id": f"ms_{i:03d}", "from": rng.choice(LAST), "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(2, 72)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages.append({"id": "ms_demo_storm", "from": "Renner residence",
                     "text": "a tree came down on the garage last night",
                     "at": iso(now() - timedelta(minutes=25)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_hazard", "from": "Pruitt",
                     "text": "is my oak safe? it's leaning more than last year",
                     "at": iso(now() - timedelta(minutes=45)), "demo_tag": "demo"})
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None, {"jobs": len(jobs)})
    print(f"Seeded {len(customers)} customers, {len(jobs)} jobs, {len(estimates)} estimates, "
          f"{len(phc)} PHC programs, {len(messages)} messages")


if __name__ == "__main__":
    main()
