#!/usr/bin/env python3
"""Post OS — synthetic Granite Shield Security. Synthetic only."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(42)

LAST = ["Whitfield", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel", "Osei",
        "Delacroix", "Yamada", "Pruitt", "Calloway", "Bostic", "Renner", "Iglesias", "Thorne"]
SITES = ["County Courthouse", "Riverside Corporate", "Northgate Construction", "Harbor Mall",
         "Lakeside Hospital", "Fifth Street Garage"]
REPORTS = [
    "I can't make my shift tonight, kid is sick",
    "we need an extra guard for the event saturday",
    "when does my armed card expire",
    "paycheck question, who do I talk to",
]


def main():
    store.wipe()
    store.save("config", {"company": "Granite Shield Security", "revenue": "$9M", "guards": 120})

    guards = []
    for i in range(120):
        creds = {"guard_card": iso(now() + timedelta(days=rng.randint(-20, 400)))}
        if rng.random() < 0.4:
            creds["armed"] = iso(now() + timedelta(days=rng.randint(-10, 300)))
        if rng.random() < 0.7:
            creds["cpr"] = iso(now() + timedelta(days=rng.randint(5, 500)))
        guards.append({"id": f"gd_{i:03d}", "name": f"{rng.choice(LAST)}",
                       "status": "active", "credentials": creds})
    guards.append({"id": "gd_demo_expired", "name": "Dana Mercer", "status": "active",
                   "credentials": {"guard_card": iso(now() - timedelta(days=5)),
                                   "armed": iso(now() + timedelta(days=100))},
                   "demo_tag": "demo"})
    guards.append({"id": "gd_demo_clean", "name": "Jordan Osei", "status": "active",
                   "credentials": {"guard_card": iso(now() + timedelta(days=200)),
                                   "armed": iso(now() + timedelta(days=150)),
                                   "cpr": iso(now() + timedelta(days=300))},
                   "demo_tag": "demo"})
    store.save("guards", guards)

    posts = []
    for i in range(40):
        filled = rng.random() < 0.8
        posts.append({"id": f"ps_{i:03d}", "site": rng.choice(SITES),
                      "when": iso(now() + timedelta(hours=rng.randint(4, 96))),
                      "required_creds": ["guard_card"] + (["armed"] if rng.random() < 0.3 else []),
                      "filled_by": f"gd_{rng.randint(0, 119):03d}" if filled else None})
    posts.append({"id": "ps_demo_armed", "site": "County Courthouse",
                  "when": iso(now() + timedelta(hours=10)),
                  "required_creds": ["guard_card", "armed"], "filled_by": None,
                  "demo_tag": "demo"})
    store.save("posts", posts)

    reports = [{"id": f"rp_{i:03d}", "from": rng.choice(LAST),
                "guard_id": f"gd_{rng.randint(0, 119):03d}",
                "post_id": f"ps_{rng.randint(0, 39):03d}", "text": t,
                "at": iso(now() - timedelta(hours=rng.randint(1, 72)))}
               for i, t in enumerate(REPORTS * 3)]
    reports.append({"id": "rp_demo_incident", "from": "Calloway", "guard_id": "gd_001",
                    "post_id": "ps_001",
                    "text": "two guys got into a fight at the loading dock, police came",
                    "at": iso(now() - timedelta(minutes=20)), "demo_tag": "demo"})
    store.save("reports", reports)
    store.save("incidents", [])
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None, {"guards": len(guards)})
    print(f"Seeded {len(guards)} guards, {len(posts)} posts, {len(reports)} reports")


if __name__ == "__main__":
    main()
