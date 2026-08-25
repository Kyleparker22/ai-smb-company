#!/usr/bin/env python3
"""Code OS — synthetic Sentinel Fire Protection. Synthetic only."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(35)

NAMES = ["Meridian Plaza", "Harborview Offices", "Cedar Mill Lofts", "Northgate Warehouse",
         "Lakeside Medical", "Fifth Street Garage", "Summit Schoolhouse", "Ironworks Kitchen"]
FINDINGS = [("three heads painted over in the stockroom", "NFPA 25", 480),
            ("exit light dead on the mezzanine", "NFPA 101", 190),
            ("extinguisher past hydro date at dock 2", "NFPA 10", 95),
            ("panel battery past service life", "NFPA 72", 260)]
MESSAGES = [
    "when is our annual due for the extinguishers",
    "how much to replace the three bad heads you found",
    "fire marshal left a notice after his walk-through",
    "invoice received, thanks",
]


def main():
    store.wipe()
    store.save("config", {"company": "Sentinel Fire Protection", "revenue": "$8M", "techs": 22})

    sites = [{"id": f"si_{i:03d}", "name": f"{rng.choice(NAMES)} {i}"} for i in range(120)]
    store.save("sites", sites)

    devices = []
    for i in range(900):
        site = rng.choice(sites)
        kind = rng.choice(list(core.INTERVALS))
        has_record = rng.random() < 0.85
        devices.append({"id": f"dv_{i:04d}", "site_id": site["id"], "kind": kind,
                        "last_inspected": iso(now() - timedelta(days=rng.randint(30, 500)))
                        if has_record else None})
    devices.append({"id": "dv_demo_unknown", "site_id": sites[0]["id"], "kind": "sprinkler",
                    "last_inspected": None, "demo_tag": "demo"})
    store.save("devices", devices)

    deficiencies = []
    for i in range(50):
        finding, code, quote = rng.choice(FINDINGS)
        site = rng.choice(sites)
        deficiencies.append({"id": f"df_{i:03d}", "site_id": site["id"],
                             "site_name": site["name"], "finding": finding, "code_ref": code,
                             "quote": quote,
                             "found_at": iso(now() - timedelta(days=rng.randint(5, 90)))})
    store.save("deficiencies", deficiencies)

    messages = [{"id": f"ms_{i:03d}", "from": rng.choice(NAMES), "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(2, 72)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages.append({"id": "ms_demo_impair", "from": "Northgate Warehouse",
                     "text": "the riser valve is shut off on floor 3 after the leak",
                     "at": iso(now() - timedelta(minutes=10)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_marshal", "from": "Lakeside Medical",
                     "text": "fire marshal left a notice after his walk-through",
                     "at": iso(now() - timedelta(minutes=50)), "demo_tag": "demo"})
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None, {"devices": len(devices)})
    print(f"Seeded {len(sites)} sites, {len(devices)} devices, {len(deficiencies)} deficiencies, "
          f"{len(messages)} messages")


if __name__ == "__main__":
    main()
