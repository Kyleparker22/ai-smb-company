#!/usr/bin/env python3
"""Central OS — synthetic Beacon Alarm & Monitoring. Synthetic only."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(44)

LAST = ["Whitfield", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel", "Osei",
        "Delacroix", "Yamada", "Pruitt", "Calloway", "Bostic", "Renner", "Iglesias", "Thorne"]
MESSAGES = [
    "motion signal tripped in zone 4 at the office",
    "question about my bill this month",
    "pause monitoring while we renovate the kitchen",
    "what time does the office open",
]


def main():
    store.wipe()
    store.save("config", {"company": "Beacon Alarm & Monitoring", "accounts": 4200,
                          "operators": 9})

    accounts = []
    for i in range(200):
        has_permit = rng.random() < 0.8
        accounts.append({"id": f"ac_{i:03d}", "name": f"{rng.choice(LAST)} {rng.choice(['residence', 'storefront', 'office'])}",
                         "city": rng.choice(["Riverton", "Lakewood"]),
                         "permit_expires": iso(now() + timedelta(days=rng.randint(-60, 500)))
                         if has_permit else None,
                         "false_alarms_ytd": rng.choice([0, 0, 0, 1, 1, 2, 3, 5])})
    store.save("accounts", accounts)

    signals = [
        {"id": "sg_demo_fire", "kind": "fire", "account_id": "ac_000",
         "at": iso(now() - timedelta(minutes=2)), "demo_tag": "demo"},
        {"id": "sg_demo_burg", "kind": "burglary", "account_id": "ac_001",
         "at": iso(now() - timedelta(minutes=6)), "demo_tag": "demo"},
    ]
    store.save("signals", signals)

    messages = [{"id": f"ms_{i:03d}", "from": rng.choice(LAST),
                 "account_id": f"ac_{rng.randint(0, 199):03d}", "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(1, 72)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages.append({"id": "ms_demo_test", "from": "unknown number", "account_id": "ac_002",
                     "text": "put my account in test mode for the afternoon",
                     "at": iso(now() - timedelta(minutes=10)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_pass", "from": "unknown number", "account_id": "ac_003",
                     "text": "my passcode is 4471, go ahead and cancel that",
                     "at": iso(now() - timedelta(minutes=15)), "demo_tag": "demo"})
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None, {"accounts": len(accounts)})
    print(f"Seeded {len(accounts)} accounts, {len(signals)} signals, {len(messages)} messages")


if __name__ == "__main__":
    main()
