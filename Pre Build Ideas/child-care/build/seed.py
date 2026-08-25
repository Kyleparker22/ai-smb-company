#!/usr/bin/env python3
"""Ratio OS — synthetic child care operator. `python3 seed.py`.

"Little Elm Learning Centers" — 3 centers, ~340 children with authorized
pickup lists, rooms with age groups, attendance + clock-ins (one room with no
records), messages, waitlist. Synthetic only.
"""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(24)

FIRST = ["Emma", "Liam", "Olivia", "Noah", "Ava", "Mateo", "Sofia", "Kai", "Zara", "Theo",
         "Isla", "Ezra", "Nova", "Rowan", "Luna", "Silas"]
LAST = ["Whitfield", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel", "Osei",
        "Delacroix", "Yamada", "Pruitt", "Calloway", "Bostic", "Renner", "Iglesias", "Thorne"]
ADULTS = ["Alex", "Sam", "Jordan", "Casey", "Morgan", "Riley", "Devon", "Harper"]
MESSAGES = [
    "my brother will pick her up today instead of me",
    "he fell off the slide and hit his head this morning?",
    "she had a fever last night, when can she come back",
    "do you have any infant room openings for the fall",
    "she left her jacket in the cubby I think",
]


def main():
    store.wipe()
    store.save("config", {"company": "Little Elm Learning Centers", "revenue": "$4.1M",
                          "ratio_rules": core.DEFAULT_RATIO_RULES,
                          "cms": "modelled, not connected"})

    centers = [{"id": f"cn_{i}", "name": n} for i, n in enumerate(
        ["Little Elm — Lakeview", "Little Elm — Prairie Trail", "Little Elm — Old Town"])]
    store.save("centers", centers)

    rooms, children, attendance, clockins = [], [], [], []
    kid_n = 0
    for cn in centers:
        for age, cap in (("infant", 12), ("toddler", 18), ("preschool", 40), ("school_age", 30)):
            room = {"id": f"rm_{cn['id']}_{age}", "name": f"{cn['name'].split('—')[1].strip()} {age}",
                    "center": cn["name"], "age_group": age, "state_code": "TX",
                    "capacity": cap, "attendance_recorded": True}
            rooms.append(room)
            enrolled = int(cap * rng.uniform(0.7, 0.98))
            present = int(enrolled * rng.uniform(0.7, 0.95))
            for k in range(enrolled):
                kid_n += 1
                fam = rng.choice(LAST)
                child = {"id": f"ch_{kid_n:04d}", "name": f"{rng.choice(FIRST)} {fam}",
                         "room_id": room["id"], "status": "active",
                         "authorized_pickups": [f"{rng.choice(ADULTS)} {fam}",
                                                f"{rng.choice(ADULTS)} {fam}"]}
                children.append(child)
                if k < present:
                    attendance.append({"id": store.nid("at"), "room_id": room["id"],
                                       "child_id": child["id"], "checked_in": iso(now()),
                                       "checked_out": None})
            rule = core.DEFAULT_RATIO_RULES["TX"][age]
            staff_needed = max(1, -(-present // rule))
            staff_n = staff_needed if rng.random() < 0.8 else staff_needed - 1  # some rooms over
            for s in range(max(0, staff_n)):
                clockins.append({"id": store.nid("ck"), "room_id": room["id"],
                                 "staff": f"staff_{room['id']}_{s}", "clocked_out": None})
    # one room with NO attendance records at all
    rooms.append({"id": "rm_norec", "name": "Old Town pre-k annex", "center": centers[2]["name"],
                  "age_group": "preschool", "state_code": "TX", "capacity": 20,
                  "attendance_recorded": False})

    # demo child with a known list
    children.append({"id": "ch_demo", "name": "Emma Osei", "room_id": rooms[0]["id"],
                     "status": "active", "demo_tag": "demo",
                     "authorized_pickups": ["Alex Osei", "Harper Osei"]})

    waitlist = []
    for i in range(40):
        w = {"id": f"wl_{i:03d}", "family": f"{rng.choice(LAST)} family",
             "age_group": rng.choice(["infant", "toddler", "preschool"]),
             "at": iso(now() - timedelta(days=rng.randint(1, 85)))}
        if rng.random() < 0.5:
            w["toured_at"] = iso(now() - timedelta(days=rng.randint(1, 40)))
            if rng.random() < 0.5:
                w["offered_at"] = iso(now() - timedelta(days=rng.randint(1, 20)))
                if rng.random() < 0.6:
                    w["enrolled_at"] = iso(now() - timedelta(days=rng.randint(1, 10)))
        waitlist.append(w)

    messages = [{"id": f"ms_{i:03d}", "child_id": rng.choice(children)["id"], "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(2, 48)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages.append({"id": "ms_demo_pickup", "child_id": "ch_demo",
                     "text": "my brother will pick her up today instead of me",
                     "at": iso(now() - timedelta(minutes=30)), "demo_tag": "demo"})

    store.save("rooms", rooms)
    store.save("children", children)
    store.save("attendance", attendance)
    store.save("clockins", clockins)
    store.save("waitlist", waitlist)
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"children": len(children), "rooms": len(rooms)})
    print(f"Seeded {len(centers)} centers, {len(rooms)} rooms, {len(children)} children, "
          f"{len(waitlist)} waitlist, {len(messages)} messages")


if __name__ == "__main__":
    main()
