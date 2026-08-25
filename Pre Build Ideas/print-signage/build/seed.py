#!/usr/bin/env python3
"""Proof OS — synthetic Meridian Print & Sign. Synthetic only."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(39)

LAST = ["Whitfield", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel", "Osei",
        "Delacroix", "Yamada", "Pruitt", "Calloway", "Bostic", "Renner", "Iglesias", "Thorne"]
WORK = [("500 tri-fold brochures", 640), ("two 4x8 site signs", 890),
        ("vehicle wrap, box truck", 3400), ("trade-show banner set", 1250),
        ("window lettering, storefront", 520)]
MESSAGES = [
    "looks good, go ahead and print it",
    "here's the artwork attached as a pdf",
    "need these by friday for the trade show, rush if you have to",
    "what are your hours saturday",
]


def main():
    store.wipe()
    store.save("config", {"company": "Meridian Print & Sign", "revenue": "$4M",
                          "press_hours_per_day": 16, "hours_booked_ahead": 44})

    customers = [{"id": f"cu_{i:03d}", "name": rng.choice(LAST)} for i in range(150)]
    store.save("customers", customers)

    jobs = []
    for i in range(160):
        desc, val = rng.choice(WORK)
        produced = rng.random() < 0.5
        j = {"id": f"jb_{i:03d}", "customer_name": rng.choice(LAST), "desc": desc,
             "value": val, "est_hours": rng.choice([2, 3, 5, 8]),
             "current_revision": rng.randint(1, 3),
             "proof_sent_at": iso(now() - timedelta(days=rng.randint(0, 12)))
             if rng.random() < 0.85 else None,
             "promised_date": iso(now() + timedelta(days=rng.randint(1, 14)))}
        if produced and j["proof_sent_at"]:
            j["proof_approval"] = {"approved_by": j["customer_name"],
                                   "at": iso(now() - timedelta(days=rng.randint(0, 10))),
                                   "revision": j["current_revision"]}
            j["produced_at"] = iso(now() - timedelta(days=rng.randint(0, 8)))
        jobs.append(j)
    jobs.append({"id": "jb_demo_verbal", "customer_name": "Mercer", "desc": "banner set",
                 "value": 1250, "est_hours": 3, "current_revision": 2,
                 "proof_sent_at": iso(now() - timedelta(days=3)),
                 "verbal_note": "customer said go ahead on the phone thursday",
                 "demo_tag": "demo"})
    jobs.append({"id": "jb_demo_approved", "customer_name": "Osei", "desc": "site signs",
                 "value": 890, "est_hours": 4, "current_revision": 1,
                 "proof_sent_at": iso(now() - timedelta(days=2)),
                 "proof_approval": {"approved_by": "Osei", "at": iso(now() - timedelta(days=1)),
                                    "revision": 1}, "demo_tag": "demo"})
    jobs.append({"id": "jb_demo_ip", "customer_name": "Havel", "desc": "team shirts",
                 "value": 780, "est_hours": 2, "current_revision": 1,
                 "art_desc": "youth team logo with the Nike swoosh and jersey numbers",
                 "proof_sent_at": iso(now() - timedelta(days=1)), "demo_tag": "demo"})
    store.save("jobs", jobs)

    messages = [{"id": f"ms_{i:03d}", "from": rng.choice(LAST), "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(2, 72)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages.append({"id": "ms_demo_approve", "from": "Mercer", "job_id": "jb_demo_verbal",
                     "text": "looks good, go ahead and print it",
                     "at": iso(now() - timedelta(minutes=15)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_rush", "from": "Renner",
                     "text": "need these by friday for the trade show, rush if you have to",
                     "at": iso(now() - timedelta(minutes=40)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_ip", "from": "Havel", "job_id": "jb_demo_ip",
                     "text": "here's the artwork attached as a pdf",
                     "at": iso(now() - timedelta(minutes=55)), "demo_tag": "demo"})
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None, {"jobs": len(jobs)})
    print(f"Seeded {len(customers)} customers, {len(jobs)} jobs, {len(messages)} messages")


if __name__ == "__main__":
    main()
