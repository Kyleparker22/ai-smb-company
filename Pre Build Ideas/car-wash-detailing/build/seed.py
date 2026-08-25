#!/usr/bin/env python3
"""Shine OS — synthetic Brightline Wash Co. Synthetic only."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(38)

LAST = ["Whitfield", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel", "Osei",
        "Delacroix", "Yamada", "Pruitt", "Calloway", "Bostic", "Renner", "Iglesias", "Thorne"]
MESSAGES = [
    "cancel my membership please, we moved across town",
    "I was charged twice this month",
    "can I book a full detail for saturday",
    "you guys did a great job on the truck",
]


def main():
    store.wipe()
    store.save("config", {"company": "Brightline Wash Co.", "locations": 3, "members": 8000})

    members = []
    for i in range(400):
        members.append({"id": f"mb_{i:03d}", "name": f"{rng.choice(LAST)}",
                        "plan": rng.choice(["basic", "unlimited", "unlimited+"]),
                        "dues": rng.choice([19, 29, 39])})
    members.append({"id": "mb_demo_cancelled", "name": "Dana Mercer", "plan": "unlimited",
                    "dues": 29, "cancel_requested_at": iso(now() - timedelta(days=2)),
                    "demo_tag": "demo"})
    store.save("members", members)

    payments = []
    for i in range(150):
        mb = rng.choice(members[:400])
        failed = rng.random() < 0.25
        p = {"id": f"py_{i:03d}", "member_id": mb["id"], "amount": mb["dues"], "failed": failed}
        if failed and rng.random() < 0.4:
            p["recovered_at"] = iso(now() - timedelta(days=rng.randint(0, 20)))
        payments.append(p)
    store.save("payments", payments)

    details = []
    for i in range(40):
        done = rng.random() < 0.6
        d = {"id": f"dt_{i:03d}", "customer": rng.choice(LAST),
             "kind": rng.choice(["full detail", "ceramic coating", "interior"]),
             "amount": rng.choice([180, 260, 520]),
             "booked_for": iso(now() + timedelta(days=rng.randint(-5, 10)))}
        if done:
            d["completed_at"] = iso(now() - timedelta(days=rng.randint(0, 20)))
        elif rng.random() < 0.3:
            d["rained_out"] = True
        details.append(d)
    store.save("details", details)

    messages = [{"id": f"ms_{i:03d}", "from": rng.choice(LAST), "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(2, 72)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages.append({"id": "ms_demo_damage", "from": "Renner",
                     "text": "your wash snapped my antenna clean off",
                     "at": iso(now() - timedelta(minutes=20)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_cancel", "from": "Pruitt", "member_id": "mb_000",
                     "text": "cancel my membership please, we moved across town",
                     "at": iso(now() - timedelta(minutes=45)), "demo_tag": "demo"})
    store.save("messages", messages)
    store.save("claims", [])
    store.save("cancellations", [])
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None, {"members": len(members)})
    print(f"Seeded {len(members)} members, {len(payments)} payments, {len(details)} details, "
          f"{len(messages)} messages")


if __name__ == "__main__":
    main()
