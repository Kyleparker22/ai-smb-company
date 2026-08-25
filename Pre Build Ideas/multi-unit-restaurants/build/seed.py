#!/usr/bin/env python3
"""Unit OS — synthetic restaurant group. `python3 seed.py`.

"Verano Taqueria Group" — 6 units, 12 months of inventory periods with one
unit skipping counts, messages incl. illness/allergen/health-dept cases.
Synthetic only.
"""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(16)

UNITS = ["Verano — Midtown", "Verano — Lakeside", "Verano — University", "Verano — Oak Park",
         "Verano — Station District", "Verano — Westgate"]

MESSAGES = [
    ("I got food poisoning from your carnitas last night", None),
    ("is the mole gluten free? my son has celiac", None),
    ("my daughter had an allergic reaction, we used her epipen", None),
    ("health inspector left a notice at the counter today", None),
    ("my burrito was cold and the wait was 40 minutes", None),
    ("order was wrong again, missing the guac we paid for", None),
    ("do you cater weddings?", None),
    ("service was slow but the food was great honestly", None),
]


def main():
    store.wipe()
    store.save("config", {"company": "Verano Taqueria Group", "units": len(UNITS),
                          "revenue": "$11M", "pos": "modelled, not connected"})

    units = [{"id": f"un_{i}", "name": n} for i, n in enumerate(UNITS)]
    store.save("units", units)

    periods = []
    for u in units:
        skip_counts = u["name"].endswith("Westgate")  # the unit that skips counts
        for m in range(12):
            period = iso(now() - timedelta(days=30 * (12 - m)))[:7]
            sales = rng.uniform(120_000, 190_000)
            theo = sales * rng.uniform(0.27, 0.30)
            drift = rng.uniform(0.0, 0.035) if u["name"].endswith("University") else rng.uniform(-0.005, 0.02)
            actual = theo + sales * drift
            p = {"id": f"pd_{u['id']}_{m}", "unit_id": u["id"], "period": period,
                 "sales": round(sales, 2),
                 "counts_taken": not skip_counts,
                 "theoretical_cost": round(theo, 2) if not skip_counts else None,
                 "actual_cost": round(actual, 2) if not skip_counts else None}
            periods.append(p)
    store.save("periods", periods)

    messages = []
    for i in range(60):
        text, _ = rng.choice(MESSAGES)
        messages.append({"id": f"ms_{i:03d}", "unit_id": rng.choice(units)["id"], "text": text,
                         "at": iso(now() - timedelta(days=rng.randint(0, 40)))})
    # demo rows guaranteed fresh and unhandled
    for j, text in enumerate(["I got food poisoning from your carnitas last night",
                              "is the mole gluten free? my son has celiac",
                              "my burrito was cold and the wait was 40 minutes"]):
        messages.append({"id": f"ms_demo_{j}", "unit_id": units[0]["id"], "text": text,
                         "at": iso(now() - timedelta(hours=j + 1)), "demo_tag": "demo"})

    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"units": len(units), "periods": len(periods), "messages": len(messages)})
    print(f"Seeded {len(units)} units, {len(periods)} periods, {len(messages)} messages")


if __name__ == "__main__":
    main()
