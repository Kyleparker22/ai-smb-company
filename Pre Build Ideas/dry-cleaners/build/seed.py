#!/usr/bin/env python3
"""Garment OS — synthetic Lexington Cleaners. Synthetic only."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(49)

LAST = ["Whitfield", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel", "Osei",
        "Delacroix", "Yamada", "Pruitt", "Calloway", "Bostic", "Renner", "Iglesias", "Thorne"]
MESSAGES = [
    "is my order ready for pickup",
    "can you get red wine out of a linen shirt",
    "the hotel needs the napkin count corrected on the invoice",
    "what time do you close saturday",
]


def main():
    store.wipe()
    store.save("config", {"company": "Lexington Cleaners", "storefronts": 3,
                          "wholesale_routes": 2})

    customers = [{"id": f"cu_{i:03d}", "name": rng.choice(LAST)} for i in range(300)]
    store.save("customers", customers)

    orders = []
    for i in range(400):
        ready = rng.random() < 0.8
        o = {"id": f"or_{i:03d}", "customer_name": rng.choice(LAST),
             "amount": rng.choice([14, 22, 38, 65])}
        if ready:
            o["ready_at"] = iso(now() - timedelta(days=rng.randint(0, 120)))
            if rng.random() < 0.75:
                o["picked_up_at"] = iso(now() - timedelta(days=rng.randint(0, 30)))
        orders.append(o)
    orders.append({"id": "or_demo_aging", "customer_name": "Mercer", "amount": 38,
                   "ready_at": iso(now() - timedelta(days=40)), "demo_tag": "demo"})
    orders.append({"id": "or_demo_expired", "customer_name": "Havel", "amount": 22,
                   "ready_at": iso(now() - timedelta(days=100)), "demo_tag": "demo"})
    store.save("orders", orders)

    claims = [
        {"id": "cl_demo_full", "customer": "Renner",
         "text": "my wedding dress came back with a mark on the train",
         "garment_class": "gown", "age_years": 1, "replacement_value": 2400,
         "intake_tag_notes": "beading loose at hem noted at intake",
         "filed_at": iso(now() - timedelta(days=1)), "demo_tag": "demo"},
        {"id": "cl_demo_partial", "customer": "Osei",
         "text": "you shrunk my husband's suit",
         "garment_class": "suit", "age_years": None, "replacement_value": None,
         "filed_at": iso(now() - timedelta(days=2)), "demo_tag": "demo"},
    ]
    store.save("claims", claims)

    messages = [{"id": f"ms_{i:03d}", "from": rng.choice(LAST), "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(1, 72)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages.append({"id": "ms_demo_claim", "from": "Renner",
                     "text": "my wedding dress came back with a mark on the train",
                     "at": iso(now() - timedelta(minutes=20)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_stain", "from": "Pruitt",
                     "text": "can you get red wine out of a linen shirt",
                     "at": iso(now() - timedelta(minutes=40)), "demo_tag": "demo"})
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None, {"orders": len(orders)})
    print(f"Seeded {len(customers)} customers, {len(orders)} orders, {len(claims)} claims, "
          f"{len(messages)} messages")


if __name__ == "__main__":
    main()
