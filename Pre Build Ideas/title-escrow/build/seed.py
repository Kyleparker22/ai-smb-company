#!/usr/bin/env python3
"""Closing OS — synthetic title agency. `python3 seed.py [--files 85]`.

"Cornerstone Title & Escrow" — open files at every stage with typed curative
items, messages incl. every wire-signal shape. Synthetic only.
"""
import argparse, random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(20)

STREETS = ["Alder Ct", "Bramble Way", "Cedarbrook Ln", "Dove Hollow Rd", "Elmcrest Dr",
           "Foxglove Ave", "Gladehill St", "Harvest Bend", "Ivystone Cir", "Juniper Pass"]
MESSAGES = [
    ("updated wiring instructions attached, please use these for closing", None),
    ("our account changed for the payoff, new details below", None),
    ("any update on the file? buyer is asking", "file"),
    ("attached is the payoff letter from the credit union", "file"),
    ("can we close early on friday instead", "file"),
    ("thanks for everything yesterday!", None),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", type=int, default=85)
    args = ap.parse_args()

    store.wipe()
    store.save("config", {"company": "Cornerstone Title & Escrow", "officers": 5,
                          "revenue": "$3.5M", "production": "modelled, not connected"})

    files = []
    for i in range(args.files):
        opened = now() - timedelta(days=rng.randint(3, 60))
        curatives = []
        for kind in rng.sample(core.CURATIVE_TYPES, rng.randint(3, 5)):
            item = {"kind": kind, "requested_at": iso(opened + timedelta(days=rng.randint(0, 5))),
                    "touches": []}
            if rng.random() < 0.55:
                item["received_at"] = iso(opened + timedelta(days=rng.randint(3, 20)))
            curatives.append(item)
        files.append({"id": f"fl_{i:03d}",
                      "address": f"{rng.randint(100,9999)} {rng.choice(STREETS)}",
                      "opened_at": iso(opened),
                      "target_close": iso(now() + timedelta(days=rng.randint(-3, 30))),
                      "curatives": curatives})

    # demo files: one clean, one with an open payoff
    files.append({"id": "fl_demo_clean", "address": "417 Juniper Pass", "demo_tag": "demo",
                  "opened_at": iso(now() - timedelta(days=30)),
                  "target_close": iso(now() + timedelta(days=4)),
                  "curatives": [{"kind": k, "requested_at": iso(now() - timedelta(days=20)),
                                 "received_at": iso(now() - timedelta(days=5)), "touches": []}
                                for k in ("payoff", "hoa_estoppel", "survey")]})
    files.append({"id": "fl_demo_open", "address": "982 Dove Hollow Rd", "demo_tag": "demo",
                  "opened_at": iso(now() - timedelta(days=25)),
                  "target_close": iso(now() + timedelta(days=6)),
                  "curatives": [
                      {"kind": "payoff", "requested_at": iso(now() - timedelta(days=15)), "touches": []},
                      {"kind": "lien_release", "requested_at": iso(now() - timedelta(days=15)),
                       "received_at": iso(now() - timedelta(days=3)), "touches": []}]})

    messages = []
    for i, (t, needs_file) in enumerate(MESSAGES * 2):
        messages.append({"id": f"ms_{i:03d}", "text": t,
                         "file_id": rng.choice(files)["id"] if needs_file else None,
                         "at": iso(now() - timedelta(hours=rng.randint(2, 48)))})
    messages.append({"id": "ms_demo_wire",
                     "text": "updated wiring instructions attached, please use these for closing",
                     "at": iso(now() - timedelta(minutes=15)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_status", "text": "any update on the file? buyer is asking",
                     "file_id": "fl_demo_open",
                     "at": iso(now() - timedelta(hours=1)), "demo_tag": "demo"})

    store.save("files", files)
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"files": len(files), "messages": len(messages)})
    print(f"Seeded {len(files)} files, {len(messages)} messages")


if __name__ == "__main__":
    main()
