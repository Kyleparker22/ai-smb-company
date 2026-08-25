#!/usr/bin/env python3
"""Haul OS — synthetic roll-off operator. `python3 seed.py`.

"Granite City Roll-Off" — ~220 containers, ~700 orders, charges with and
without tickets, item questions incl. every hazardous class. Synthetic only.
"""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(19)

SITES = ["Alder Ct jobsite", "Bramble Way remodel", "Cedarbrook roofing", "Dove Hollow demo",
         "Elmcrest cleanout", "Foxglove build", "Gladehill storm job", "Harvest Bend addition"]
QUESTIONS = [
    "can I toss a few cans of old paint in there",
    "drywall from the garage remodel",
    "got some car batteries and two tires",
    "old couch and a dresser",
    "we're tearing out a popcorn ceiling from the 70s",
    "roofing shingles, one layer off a ranch house",
    "old fridge and a window AC unit",
    "some stuff from my uncle's shed",
]


def main():
    store.wipe()
    store.save("config", {"company": "Granite City Roll-Off", "revenue": "$6M",
                          "trucks": 7, "dispatch": "modelled, not connected"})

    containers, orders, charges = [], [], []
    for i in range(220):
        status = rng.choices(["on_site", "in_yard", "on_truck"], weights=[0.6, 0.35, 0.05])[0]
        c = {"id": f"cn_{i:03d}", "size": rng.choice([10, 15, 20, 30, 40]), "status": status}
        if status == "on_site":
            c["site"] = rng.choice(SITES)
            c["delivered_at"] = iso(now() - timedelta(days=rng.randint(1, 30)))
        containers.append(c)

    on_site = [c for c in containers if c["status"] == "on_site"]
    for i in range(700):
        kind = rng.choices(["delivery", "pickup", "swap"], weights=[0.4, 0.4, 0.2])[0]
        promised = now() + timedelta(days=rng.randint(-6, 6))
        o = {"id": f"or_{i:04d}", "kind": kind,
             "container_id": rng.choice(containers)["id"],
             "promised_at": iso(promised)}
        if promised < now() and rng.random() < 0.85:
            o["completed_at"] = iso(promised + timedelta(hours=rng.randint(1, 30)))
        orders.append(o)

    for i in range(40):
        kind = rng.choice(["overweight", "contamination"])
        ch = {"id": f"ch_{i:03d}", "kind": kind, "amount": rng.randint(75, 600),
              "container_id": rng.choice(containers)["id"]}
        if rng.random() < 0.7:
            if kind == "overweight":
                ch["scale_ticket_id"] = f"tkt_{rng.randint(10000,99999)}"
            else:
                ch["photo_record_id"] = f"ph_{rng.randint(10000,99999)}"
        charges.append(ch)
    # demo charges: one with, one without evidence
    charges.append({"id": "ch_demo_ticket", "kind": "overweight", "amount": 340,
                    "scale_ticket_id": "tkt_55521", "demo_tag": "demo"})
    charges.append({"id": "ch_demo_noticket", "kind": "overweight", "amount": 340,
                    "demo_tag": "demo"})

    messages = [{"id": f"ms_{i:03d}", "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(1, 48)))}
                for i, t in enumerate(QUESTIONS * 2)]
    messages.append({"id": "ms_demo_paint", "text": "can I toss a few cans of old paint in there",
                     "at": iso(now() - timedelta(minutes=20)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_drywall", "text": "drywall from the garage remodel",
                     "at": iso(now() - timedelta(minutes=25)), "demo_tag": "demo"})

    store.save("containers", containers)
    store.save("orders", orders)
    store.save("charges", charges)
    store.save("messages", messages)
    store.save("customers", [])
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"containers": len(containers), "orders": len(orders)})
    print(f"Seeded {len(containers)} containers, {len(orders)} orders, {len(charges)} charges, "
          f"{len(messages)} messages")


if __name__ == "__main__":
    main()
