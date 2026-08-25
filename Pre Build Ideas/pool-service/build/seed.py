#!/usr/bin/env python3
"""Pool OS — synthetic Bluewater Pool Care. `python3 seed.py`. Synthetic only."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(31)

LAST = ["Whitfield", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel", "Osei",
        "Delacroix", "Yamada", "Pruitt", "Calloway", "Bostic", "Renner", "Iglesias", "Thorne"]
ITEMS = [("filter cartridge set", 380), ("salt cell replacement", 940), ("variable-speed pump", 1650),
         ("heater igniter", 420), ("pool light", 510)]
MESSAGES = [
    "pool turned green over the weekend",
    "how much shock should I add after the party",
    "skip this week's service, we're out of town",
    "invoice received, thanks for the great work",
]


def main():
    store.wipe()
    store.save("config", {"company": "Bluewater Pool Care", "revenue": "$3M", "routes": 8})

    customers = [{"id": f"cu_{i:03d}", "name": f"{rng.choice(LAST)} household"} for i in range(450)]
    store.save("customers", customers)

    pools = [{"id": f"pl_{i:03d}", "customer_id": customers[i]["id"],
              "target_ranges": {"fc": [1.0, 4.0], "ph": [7.2, 7.8], "ta": [80, 120]}
              if rng.random() < 0.9 else {}}
             for i in range(450)]
    store.save("pools", pools)

    stops = []
    for i in range(900):
        pool = rng.choice(pools)
        at = now() - timedelta(days=rng.randint(0, 30))
        complete = rng.random() < 0.85
        s = {"id": f"st_{i:04d}", "pool_id": pool["id"], "rate": rng.choice([45, 55, 65]),
             "arrived_at": iso(at) if complete or rng.random() < 0.5 else None}
        if complete:
            s["readings"] = {"fc": round(rng.uniform(0.5, 5.0), 1),
                             "ph": round(rng.uniform(7.0, 8.0), 1),
                             "ta": rng.randint(60, 140)}
        elif rng.random() < 0.5:
            s["readings"] = {"fc": round(rng.uniform(1, 4), 1), "ph": None, "ta": None}
        if s.get("readings") and s.get("arrived_at") and rng.random() < 0.7:
            s["billed_at"] = iso(at + timedelta(days=2))
        stops.append(s)
    stops.append({"id": "st_demo_proven", "pool_id": "pl_000", "rate": 55,
                  "arrived_at": iso(now() - timedelta(days=2)),
                  "readings": {"fc": 2.4, "ph": 7.5, "ta": 95}, "demo_tag": "demo"})
    stops.append({"id": "st_demo_noproof", "pool_id": "pl_001", "rate": 55,
                  "arrived_at": None, "readings": {"fc": 2.0, "ph": None, "ta": None},
                  "demo_tag": "demo"})
    store.save("stops", stops)

    quotes = []
    for i in range(60):
        item, amt = rng.choice(ITEMS)
        quotes.append({"id": f"qt_{i:03d}", "customer_name": f"{rng.choice(LAST)}",
                       "item": item, "amount": amt,
                       "sent_at": iso(now() - timedelta(days=rng.randint(3, 40)))})
    store.save("quotes", quotes)

    messages = [{"id": f"ms_{i:03d}", "from": rng.choice(LAST), "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(2, 72)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages.append({"id": "ms_demo_injury", "from": "Renner household",
                     "text": "my son got a chemical burn on his legs after swimming yesterday",
                     "at": iso(now() - timedelta(minutes=20)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_dose", "from": "Pruitt",
                     "text": "how much shock should I add after the party",
                     "at": iso(now() - timedelta(minutes=40)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_green", "from": "Osei household",
                     "text": "pool turned green over the weekend",
                     "at": iso(now() - timedelta(hours=1)), "demo_tag": "demo"})
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None, {"stops": len(stops)})
    print(f"Seeded {len(customers)} customers, {len(stops)} stops, {len(quotes)} quotes, "
          f"{len(messages)} messages")


if __name__ == "__main__":
    main()
