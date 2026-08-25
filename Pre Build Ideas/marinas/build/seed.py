#!/usr/bin/env python3
"""Slip OS — synthetic Harborview Marina & Boatworks. Synthetic only."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(48)

LAST = ["Whitfield", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel", "Osei",
        "Delacroix", "Yamada", "Pruitt", "Calloway", "Bostic", "Renner", "Iglesias", "Thorne"]
MESSAGES = [
    "need the boat hauled and bottom paint before june",
    "any slip open for a 32 footer this season",
    "question about my storage fee this quarter",
    "the launch ramp gate code isn't working",
]


def main():
    store.wipe()
    store.save("config", {"company": "Harborview Marina & Boatworks", "slips": 240,
                          "dry_stack": 60})

    slips = []
    for i in range(240):
        occupied = rng.random() < 0.92
        slips.append({"id": f"sl_{i:03d}", "dock": rng.choice(["A", "B", "C", "D"]),
                      "number": i + 1, "max_length_ft": rng.choice([26, 32, 40, 50]),
                      "max_beam_ft": rng.choice([10, 12, 14, 16]),
                      "max_draft_ft": rng.choice([4, 5, 6, 8]),
                      "occupied_by": f"vs_{i:03d}" if occupied else None})
    slips.append({"id": "sl_demo_open", "dock": "B", "number": 41, "max_length_ft": 34,
                  "max_beam_ft": 12, "max_draft_ft": 5, "occupied_by": None,
                  "demo_tag": "demo"})
    store.save("slips", slips)

    vessels = []
    for i in range(60):
        departed = rng.random() < 0.4
        v = {"id": f"vs_y{i:03d}", "owner": rng.choice(LAST),
             "arrived_at": iso(now() - timedelta(days=rng.randint(5, 120))),
             "storage_rate_day": rng.choice([18, 24, 32])}
        if departed:
            v["departed_at"] = iso(now() - timedelta(days=rng.randint(0, 30)))
        vessels.append(v)
    vessels.append({"id": "vs_demo_splashed", "owner": "Mercer",
                    "arrived_at": iso(now() - timedelta(days=40)),
                    "departed_at": iso(now() - timedelta(days=10)),
                    "storage_rate_day": 24, "demo_tag": "demo"})
    store.save("vessels", vessels)

    waitlist = []
    for i in range(25):
        waitlist.append({"id": f"wl_{i:03d}", "name": rng.choice(LAST),
                         "length_ft": rng.choice([24, 28, 32, 38, 44]),
                         "beam_ft": rng.choice([8, 10, 11, 13]),
                         "draft_ft": rng.choice([3, 4, 5, 6]),
                         "since": iso(now() - timedelta(days=rng.randint(10, 400)))})
    waitlist.append({"id": "wl_demo_fits", "name": "Priya Osei", "length_ft": 30,
                     "beam_ft": 11, "draft_ft": 4,
                     "since": iso(now() - timedelta(days=500)), "demo_tag": "demo"})
    waitlist.append({"id": "wl_demo_toobig", "name": "Ray Havel", "length_ft": 44,
                     "beam_ft": 14, "draft_ft": 6,
                     "since": iso(now() - timedelta(days=600)), "demo_tag": "demo"})
    store.save("waitlist", waitlist)

    workorders = [
        {"id": "wo_demo_verbal", "owner": "Renner", "scope_requested": "haul and bottom paint",
         "verbal_note": "owner said go ahead at the fuel dock saturday",
         "opened_at": iso(now() - timedelta(days=2)), "demo_tag": "demo"},
    ]
    store.save("workorders", workorders)

    messages = [{"id": f"ms_{i:03d}", "from": rng.choice(LAST), "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(1, 72)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages.append({"id": "ms_demo_spill", "from": "dockhand Marcus",
                     "text": "there's diesel in the water by the fuel dock",
                     "at": iso(now() - timedelta(minutes=5)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_work", "from": "Pruitt",
                     "text": "need the boat hauled and bottom paint before june",
                     "at": iso(now() - timedelta(minutes=40)), "demo_tag": "demo"})
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None, {"slips": len(slips)})
    print(f"Seeded {len(slips)} slips, {len(vessels)} vessels, {len(waitlist)} waitlist, "
          f"{len(messages)} messages")


if __name__ == "__main__":
    main()
