#!/usr/bin/env python3
"""Move OS — synthetic mover. `python3 seed.py [--moves 300]`.

"Beacon Hill Moving & Storage" — binding and non-binding moves, surveys,
change orders signed and unsigned, condition records, claims, messages.
Synthetic only.
"""
import argparse, random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(22)

ITEMS = ["dresser", "dining table", "sofa", "TV", "piano", "mirror", "bookshelf", "bed frame"]
DAMAGE = ["cracked leg", "deep scratch", "dented corner", "shattered glass", "torn upholstery"]
MESSAGES = [
    ("the dresser arrived with a cracked leg", "claim"),
    ("how much to move a 3 bedroom house across town", "quote"),
    ("can we push the date, closing slipped a week", "date"),
    ("what time does the crew arrive tomorrow", "other"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--moves", type=int, default=300)
    args = ap.parse_args()

    store.wipe()
    store.save("config", {"company": "Beacon Hill Moving & Storage", "trucks": 11,
                          "revenue": "$4.8M", "claim_rules": core.DEFAULT_CLAIM_RULES,
                          "crm": "modelled, not connected"})

    moves, conditions, claims = [], [], []
    for i in range(args.moves):
        binding = rng.random() < 0.55
        when = now() - timedelta(days=rng.randint(1, 360))
        m = {"id": f"mv_{i:04d}", "desc": f"{rng.randint(1,5)}BR move",
             "estimate_type": "binding" if binding else "non_binding",
             "when": iso(when)}
        if binding:
            m["survey_id"] = f"sv_{i:04d}" if rng.random() < 0.9 else None
            m["inventory_items"] = rng.randint(40, 220) if m["survey_id"] else None
            m["binding_amount"] = rng.randint(1800, 12000)
            cos = []
            for _ in range(rng.randint(0, 2)):
                cos.append({"desc": rng.choice(["extra flight of stairs", "packing added",
                                                "shuttle required", "storage week"]),
                            "amount": rng.randint(150, 900),
                            "signed_at": iso(when) if rng.random() < 0.8 else None})
            m["change_orders"] = cos
        else:
            m["hourly_rate"] = rng.choice([139, 159, 189])
            if when < now():
                m["actual_hours"] = round(rng.uniform(3, 11), 1)
        moves.append(m)
        # condition records for a slice
        if rng.random() < 0.4:
            item = rng.choice(ITEMS)
            dmg = rng.random() < 0.2
            conditions.append({"id": store.nid("cd"), "move_id": m["id"], "item": item,
                               "kind": "load", "damage": []})
            conditions.append({"id": store.nid("cd"), "move_id": m["id"], "item": item,
                               "kind": "delivery",
                               "damage": [rng.choice(DAMAGE)] if dmg else []})
            if dmg and rng.random() < 0.6:
                claims.append({"id": store.nid("cm"), "move_id": m["id"], "item": item,
                               "filed_at": iso(when + timedelta(days=rng.randint(1, 10))),
                               "acknowledged_at": iso(when + timedelta(days=rng.randint(11, 20)))
                                                  if rng.random() < 0.5 else None})

    # demo rows
    moves.append({"id": "mv_demo_nosurvey", "desc": "4BR interstate", "estimate_type": "binding",
                  "survey_id": None, "inventory_items": None, "demo_tag": "demo"})
    moves.append({"id": "mv_demo_surveyed", "desc": "3BR local", "estimate_type": "binding",
                  "survey_id": "sv_demo", "inventory_items": 128, "binding_amount": 4200,
                  "change_orders": [
                      {"desc": "packing added", "amount": 400, "signed_at": iso(now())},
                      {"desc": "driver says extra fee", "amount": 850, "signed_at": None}],
                  "demo_tag": "demo"})
    conditions.append({"id": "cd_demo_load", "move_id": "mv_demo_claim", "item": "dresser",
                       "kind": "load", "damage": []})
    conditions.append({"id": "cd_demo_dlv", "move_id": "mv_demo_claim", "item": "dresser",
                       "kind": "delivery", "damage": ["cracked leg"]})
    claims.append({"id": "cm_demo_ok", "move_id": "mv_demo_claim", "item": "dresser",
                   "filed_at": iso(now() - timedelta(days=2)), "demo_tag": "demo"})
    claims.append({"id": "cm_demo_norec", "move_id": "mv_demo_norec", "item": "mirror",
                   "filed_at": iso(now() - timedelta(days=1)), "demo_tag": "demo"})

    messages = [{"id": f"ms_{i:03d}", "text": t[0],
                 "at": iso(now() - timedelta(hours=rng.randint(2, 48)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages.append({"id": "ms_demo_claim", "text": "the dresser arrived with a cracked leg",
                     "move_id": "mv_demo_claim", "item": "dresser",
                     "at": iso(now() - timedelta(minutes=30)), "demo_tag": "demo"})

    store.save("moves", moves)
    store.save("conditions", conditions)
    store.save("claims", claims)
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"moves": len(moves), "claims": len(claims)})
    print(f"Seeded {len(moves)} moves, {len(conditions)} condition records, "
          f"{len(claims)} claims, {len(messages)} messages")


if __name__ == "__main__":
    main()
