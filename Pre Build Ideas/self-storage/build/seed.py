#!/usr/bin/env python3
"""Gate OS — synthetic storage operator. `python3 seed.py`.

"Summit Ridge Storage" — 3 facilities, ~1,900 units, tenants at every
delinquency stage incl. military-flagged and unverified. Synthetic only.
"""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(23)

FIRST = ["Avery", "Jordan", "Sam", "Riley", "Casey", "Morgan", "Drew", "Quinn", "Reese", "Sawyer",
         "Marisol", "Deshawn", "Priya", "Kenji", "Elena", "Marcus", "Tanya", "Cole", "Nina", "Omar"]
LAST = ["Whitfield", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel", "Osei",
        "Delacroix", "Yamada", "Pruitt", "Calloway", "Bostic", "Renner", "Iglesias", "Thorne"]
MESSAGES = [
    "I'm deployed overseas until March, can't deal with this right now",
    "I'll pay friday I promise, just got paid late",
    "moving out end of the month, unit will be empty",
    "the gate code isn't working again",
    "do you have any 10x20s available",
]


def main():
    store.wipe()
    store.save("config", {"company": "Summit Ridge Storage", "revenue": "$3.2M",
                          "lien_rules": core.DEFAULT_LIEN_RULES,
                          "fms": "modelled, not connected"})

    facilities = [
        {"id": "fa_tx1", "name": "Summit Ridge — Lakeway", "state": "TX", "unit_count": 720},
        {"id": "fa_tx2", "name": "Summit Ridge — Buda", "state": "TX", "unit_count": 640},
        {"id": "fa_co1", "name": "Summit Ridge — Loveland", "state": "CO", "unit_count": None},  # no count
    ]
    store.save("facilities", facilities)

    tenants = []
    for i in range(1900):
        fac = rng.choice(facilities)
        t = {"id": f"tn_{i:04d}", "name": f"{rng.choice(FIRST)} {rng.choice(LAST)}",
             "facility_id": fac["id"], "state_code": fac["state"],
             "unit": f"{rng.choice('ABCDE')}{rng.randint(100,499)}",
             "status": "active", "rate": rng.choice([79, 109, 149, 209]),
             "dunning_touches": []}
        r = rng.random()
        if r < 0.07:  # delinquent
            t["delinquent_since"] = iso(now() - timedelta(days=rng.randint(5, 70)))
            t["balance"] = t["rate"] * rng.randint(1, 3)
            t["scra_verified_at"] = iso(now() - timedelta(days=rng.randint(1, 20))) \
                if rng.random() < 0.5 else None
            if rng.random() < 0.06:
                t["military_flag"] = True
        tenants.append(t)

    # demo tenants
    tenants.append({"id": "tn_demo_mil", "name": "Jordan Osei", "facility_id": "fa_tx1",
                    "state_code": "TX", "unit": "B221", "status": "active", "rate": 149,
                    "delinquent_since": iso(now() - timedelta(days=40)), "balance": 298,
                    "military_flag": True, "demo_tag": "demo", "dunning_touches": []})
    tenants.append({"id": "tn_demo_unv", "name": "Casey Renner", "facility_id": "fa_tx1",
                    "state_code": "TX", "unit": "C310", "status": "active", "rate": 109,
                    "delinquent_since": iso(now() - timedelta(days=35)), "balance": 218,
                    "scra_verified_at": None, "demo_tag": "demo", "dunning_touches": []})
    tenants.append({"id": "tn_demo_ok", "name": "Nina Havel", "facility_id": "fa_tx1",
                    "state_code": "TX", "unit": "A105", "status": "active", "rate": 79,
                    "delinquent_since": iso(now() - timedelta(days=38)), "balance": 158,
                    "scra_verified_at": iso(now() - timedelta(days=2)),
                    "demo_tag": "demo", "dunning_touches": []})

    messages = [{"id": f"ms_{i:03d}", "tenant_id": rng.choice(tenants)["id"], "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(2, 48)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages.append({"id": "ms_demo_mil", "tenant_id": "tn_demo_unv",
                     "text": "I'm deployed overseas until March, can't deal with this right now",
                     "at": iso(now() - timedelta(minutes=30)), "demo_tag": "demo"})

    store.save("tenants", tenants)
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None, {"tenants": len(tenants)})
    delinquent = [t for t in tenants if t.get("delinquent_since")]
    print(f"Seeded {len(tenants)} tenants ({len(delinquent)} delinquent), {len(messages)} messages")


if __name__ == "__main__":
    main()
