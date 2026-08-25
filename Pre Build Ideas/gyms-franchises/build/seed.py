#!/usr/bin/env python3
"""Member OS — synthetic gym group. `python3 seed.py [--members 5200]`.

"Foundry Fitness" — 4 locations across CA/TX, members with visit histories,
failed payments at every ladder stage, freezes, cancellations, messages incl.
injury and cancellation. Synthetic only; 555 phones.
"""
import argparse, random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(17)

FIRST = ["Avery", "Jordan", "Sam", "Riley", "Casey", "Morgan", "Drew", "Quinn", "Reese", "Sawyer",
         "Marisol", "Deshawn", "Priya", "Kenji", "Elena", "Marcus", "Tanya", "Cole", "Nina", "Omar"]
LAST = ["Whitfield", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel", "Osei",
        "Delacroix", "Yamada", "Pruitt", "Calloway", "Bostic", "Renner", "Iglesias", "Thorne"]

MESSAGES = [
    "I want to cancel my membership please",
    "I hurt my shoulder during the 6am class yesterday",
    "I was charged twice this month, need a refund",
    "can I freeze my membership for the summer",
    "will lifting fix my back pain",
    "what time does the pool open saturday",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--members", type=int, default=5200)
    args = ap.parse_args()

    store.wipe()
    store.save("config", {"company": "Foundry Fitness", "locations": 4, "revenue": "$6.8M",
                          "billing": "modelled, not connected",
                          "cancel_rules": core.DEFAULT_CANCEL_RULES})

    members, payments, cancellations = [], [], []
    for i in range(args.members):
        state = rng.choice(["CA", "CA", "TX"])
        vp = rng.randint(0, 16)
        v30 = max(0, vp - rng.choice([0, 0, 0, 1, 2, vp]))  # a slice drops hard
        m = {"id": f"mb_{i:05d}", "name": f"{rng.choice(FIRST)} {rng.choice(LAST)}",
             "state_code": state, "status": "active", "dues": rng.choice([39, 59, 89, 129]),
             "visits_30d": v30, "visits_prior_30d": vp,
             "freeze_requested": rng.random() < 0.03,
             "no_future_booking": rng.random() < 0.25,
             "dunning_touches": []}
        members.append(m)
        # ~6% have a failed payment
        if rng.random() < 0.06:
            payments.append({"id": store.nid("py"), "member_id": m["id"], "failed": True,
                             "amount": m["dues"], "at": iso(now() - timedelta(days=rng.randint(1, 40))),
                             "recovered_at": iso(now() - timedelta(days=rng.randint(0, 10)))
                                             if rng.random() < 0.3 else None})

    # cancellations history for the churn split
    for i in range(40):
        cancellations.append({"id": store.nid("cx"), "member_id": rng.choice(members)["id"],
                              "at": iso(now() - timedelta(days=rng.randint(1, 85))),
                              "reason": rng.choices(["voluntary", "payment_failure"],
                                                    weights=[0.6, 0.4])[0]})

    messages = [{"id": f"ms_{i:03d}", "member_id": rng.choice(members)["id"], "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(2, 72)))}
                for i, t in enumerate(MESSAGES * 3)]
    # demo rows: a CA cancellation and an injury
    ca_member = next(m for m in members if m["state_code"] == "CA")
    messages.append({"id": "ms_demo_cancel", "member_id": ca_member["id"],
                     "text": "I want to cancel my membership please",
                     "at": iso(now() - timedelta(hours=1)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_injury", "member_id": members[1]["id"],
                     "text": "I hurt my shoulder during the 6am class yesterday",
                     "at": iso(now() - timedelta(hours=2)), "demo_tag": "demo"})

    store.save("members", members)
    store.save("payments", payments)
    store.save("cancellations", cancellations)
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"members": len(members), "payments": len(payments)})
    print(f"Seeded {len(members)} members, {len(payments)} failed-payment rows, "
          f"{len(messages)} messages")


if __name__ == "__main__":
    main()
