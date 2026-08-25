#!/usr/bin/env python3
"""Fuel OS — synthetic Northline Propane. Synthetic only."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(43)

LAST = ["Whitfield", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel", "Osei",
        "Delacroix", "Yamada", "Pruitt", "Calloway", "Bostic", "Renner", "Iglesias", "Thorne"]
CALLS = [
    "need a fill before the cold snap this weekend",
    "what's your price per gallon right now",
    "we're out of gas and the furnace quit last night",
    "the driver was great, thanks",
]


def main():
    store.wipe()
    store.save("config", {"company": "Northline Propane", "revenue": "$14M", "bobtails": 6,
                          "market_price": 2.89})

    customers = []
    for i in range(300):
        contract = rng.random() < 0.4
        c = {"id": f"cu_{i:03d}", "name": f"{rng.choice(LAST)} residence"}
        if contract:
            c["contract_price"] = round(rng.uniform(2.15, 2.55), 2)
            c["contract_through"] = iso(now() + timedelta(days=rng.randint(60, 300)))
        customers.append(c)
    customers.append({"id": "cu_demo_contract", "name": "Mercer residence",
                      "contract_price": 2.29,
                      "contract_through": iso(now() + timedelta(days=200)), "demo_tag": "demo"})
    store.save("customers", customers)

    tanks = []
    for i in range(300):
        has_history = rng.random() < 0.8
        t = {"id": f"tk_{i:03d}", "customer_name": customers[i]["name"],
             "size_gal": rng.choice([120, 250, 500, 1000]),
             "requal_due": iso(now() + timedelta(days=rng.randint(-30, 2000)))
             if rng.random() < 0.9 else None}
        if has_history:
            t["gallons_per_day"] = round(rng.uniform(0.8, 6.0), 1)
            t["last_reading_pct"] = rng.randint(8, 80)
        tanks.append(t)
    tanks.append({"id": "tk_demo_expired", "customer_name": "Osei residence", "size_gal": 250,
                  "requal_due": iso(now() - timedelta(days=10)), "gallons_per_day": 2.0,
                  "last_reading_pct": 40, "demo_tag": "demo"})
    tanks.append({"id": "tk_demo_ok", "customer_name": "Havel residence", "size_gal": 500,
                  "requal_due": iso(now() + timedelta(days=500)), "gallons_per_day": 3.0,
                  "last_reading_pct": 60, "demo_tag": "demo"})
    store.save("tanks", tanks)

    calls = [{"id": f"cl_{i:03d}", "from": rng.choice(LAST),
              "customer_id": f"cu_{rng.randint(0, 299):03d}", "text": t,
              "at": iso(now() - timedelta(hours=rng.randint(1, 72)))}
             for i, t in enumerate(CALLS * 3)]
    calls.append({"id": "cl_demo_smell", "from": "Renner residence",
                  "text": "we smell gas in the basement by the water heater",
                  "at": iso(now() - timedelta(minutes=5)), "demo_tag": "demo"})
    calls.append({"id": "cl_demo_outage", "from": "Pruitt residence",
                  "text": "we're out of gas and the furnace quit last night",
                  "at": iso(now() - timedelta(minutes=30)), "demo_tag": "demo"})
    calls.append({"id": "cl_demo_price", "from": "Mercer residence",
                  "customer_id": "cu_demo_contract",
                  "text": "what's my contract rate this season",
                  "at": iso(now() - timedelta(minutes=50)), "demo_tag": "demo"})
    store.save("calls", calls)
    store.save("tickets", [])
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None, {"tanks": len(tanks)})
    print(f"Seeded {len(customers)} customers, {len(tanks)} tanks, {len(calls)} calls")


if __name__ == "__main__":
    main()
