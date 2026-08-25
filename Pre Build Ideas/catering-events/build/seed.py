#!/usr/bin/env python3
"""Plate OS — synthetic caterer. `python3 seed.py`.

"Juniper & Rye Catering" — ~420 events across the year, 4 spaces, BEOs with
final counts and additions, messages incl. allergen notes and late changes.
Synthetic only.
"""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(28)

SPACES = [("sp_barn", "The Barn", 180), ("sp_hall", "Juniper Hall", 250),
          ("sp_garden", "The Garden", 120), ("sp_loft", "The Rye Loft", 80)]
NAMES = ["Whitfield wedding", "Barrera rehearsal dinner", "Okafor 50th", "Crestline corporate",
         "Lindqvist reception", "Mercer gala", "holiday party", "Osei anniversary"]
MESSAGES = [
    "one guest has a severe nut allergy, what can she eat",
    "can we swap the salmon entree for chicken",
    "do you cater corporate holiday parties in december",
    "the team loved everything saturday, thank you",
]


def main():
    store.wipe()
    store.save("config", {"company": "Juniper & Rye Catering", "revenue": "$5.2M",
                          "events_yr": 420, "software": "modelled, not connected"})
    store.save("spaces", [{"id": i, "name": n, "capacity": c} for i, n, c in SPACES])

    bookings = []
    used = set()
    for i in range(420):
        sp = rng.choice(SPACES)
        d = now() + timedelta(days=rng.randint(-180, 180))
        key = (sp[0], iso(d)[:10])
        if key in used:
            continue
        used.add(key)
        additions = []
        for _ in range(rng.randint(0, 2)):
            additions.append({"desc": rng.choice(["late-night snack station", "extra bar hour",
                                                  "cake cutting", "valet"]),
                              "amount": rng.randint(200, 1200),
                              "recorded_at": iso(now()) if rng.random() < 0.8 else None})
        bookings.append({"id": f"ev_{i:04d}", "name": rng.choice(NAMES), "space_id": sp[0],
                        "date": iso(d), "guests": rng.randint(40, sp[2]),
                        "per_head": rng.choice([68, 85, 105, 145]),
                        "final_count": rng.randint(40, sp[2]) if d < now() + timedelta(days=7) else None,
                        "additions": additions})

    # demo bookings: one inside the lock window, one outside, one for double-book demo
    bookings.append({"id": "ev_demo_locked", "name": "Saturday wedding (locked)",
                    "space_id": "sp_barn", "date": iso(now() + timedelta(hours=40)),
                    "guests": 150, "per_head": 105, "final_count": 150,
                    "additions": [{"desc": "extra bar hour", "amount": 800, "recorded_at": iso(now())},
                                  {"desc": "verbal add nobody wrote down", "amount": 600,
                                   "recorded_at": None}],
                    "demo_tag": "demo"})
    bookings.append({"id": "ev_demo_open", "name": "Corporate dinner (3 weeks out)",
                    "space_id": "sp_hall", "date": iso(now() + timedelta(days=21)),
                    "guests": 90, "per_head": 85, "additions": [], "demo_tag": "demo"})

    messages = [{"id": f"ms_{i:03d}", "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(2, 48)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages.append({"id": "ms_demo_allergen",
                     "text": "one guest has a severe nut allergy, what can she eat",
                     "at": iso(now() - timedelta(minutes=20)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_locked_change", "booking_id": "ev_demo_locked",
                     "text": "can we swap the salmon entree for chicken",
                     "at": iso(now() - timedelta(minutes=30)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_open_change", "booking_id": "ev_demo_open",
                     "text": "can we add a vegetarian entree option",
                     "at": iso(now() - timedelta(minutes=35)), "demo_tag": "demo"})

    store.save("bookings", bookings)
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None, {"bookings": len(bookings)})
    print(f"Seeded {len(bookings)} bookings, {len(SPACES)} spaces, {len(messages)} messages")


if __name__ == "__main__":
    main()
