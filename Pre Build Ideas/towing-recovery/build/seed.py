#!/usr/bin/env python3
"""Hook OS — synthetic Ironline Towing. Synthetic only."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(34)

LAST = ["Whitfield", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel", "Osei",
        "Delacroix", "Yamada", "Pruitt", "Calloway", "Bostic", "Renner", "Iglesias", "Thorne"]
CALLS = [
    "car broke down on the shoulder of route 9",
    "how much is a tow across town",
    "you impounded my car last night, where is it",
    "do you buy junk cars",
]


def main():
    store.wipe()
    store.save("config", {"company": "Ironline Towing", "revenue": "$6M", "trucks": 14})

    tows = []
    for i in range(200):
        t = {"id": f"tw_{i:03d}", "customer": rng.choice(LAST),
             "miles": rng.randint(3, 40) if rng.random() < 0.9 else None,
             "hookup_photos": rng.choice([0, 1, 4, 6, 8]),
             "winch_hours": rng.choice([0, 0, 0, 1, 2]) or None,
             "done_at": iso(now() - timedelta(days=rng.randint(0, 45)))}
        tows.append(t)
    tows.append({"id": "tw_demo_over", "customer": "Mercer", "miles": 10, "hookup_photos": 6,
                 "requested_total": 900, "demo_tag": "demo"})
    tows.append({"id": "tw_demo_clean", "customer": "Osei", "miles": 12, "hookup_photos": 5,
                 "demo_tag": "demo"})
    tows.append({"id": "tw_demo_nophotos", "customer": "Havel", "miles": 8, "hookup_photos": 1,
                 "demo_tag": "demo"})
    store.save("tows", tows)

    impounds = []
    for i in range(60):
        released = rng.random() < 0.6
        imp = {"id": f"im_{i:03d}", "state_code": rng.choice(["TX", "GA"]),
               "vehicle": f"{rng.choice(['Civic','F-150','Altima','Camry','Silverado'])}",
               "impounded_at": iso(now() - timedelta(days=rng.randint(1, 50)))}
        if released:
            imp["released_at"] = iso(now() - timedelta(days=rng.randint(0, 10)))
        impounds.append(imp)
    impounds.append({"id": "im_demo_aging", "state_code": "TX", "vehicle": "abandoned Sentra",
                     "impounded_at": iso(now() - timedelta(days=8)), "demo_tag": "demo"})
    store.save("impounds", impounds)

    calls = [{"id": f"cl_{i:03d}", "from": rng.choice(LAST), "text": t,
              "at": iso(now() - timedelta(hours=rng.randint(1, 48)))}
             for i, t in enumerate(CALLS * 3)]
    calls.append({"id": "cl_demo_rotation", "from": "county dispatch",
                  "text": "this is county dispatch, rotation tow at mile marker 12",
                  "at": iso(now() - timedelta(minutes=5)), "demo_tag": "demo"})
    calls.append({"id": "cl_demo_release", "from": "Renner",
                  "text": "I need to come get my truck from your lot",
                  "at": iso(now() - timedelta(minutes=30)), "demo_tag": "demo"})
    store.save("calls", calls)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None, {"tows": len(tows)})
    print(f"Seeded {len(tows)} tows, {len(impounds)} impounds, {len(calls)} calls")


if __name__ == "__main__":
    main()
