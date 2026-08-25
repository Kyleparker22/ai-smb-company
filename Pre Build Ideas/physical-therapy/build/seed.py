#!/usr/bin/env python3
"""Rehab OS — synthetic PT group. `python3 seed.py [--patients 950]`.

"Riverbend Physical Therapy" — 3 clinics, plans of care at every stage incl.
dropouts and over-auth patients, messages incl. every red-flag type.
Synthetic only.
"""
import argparse, random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(26)

FIRST = ["Avery", "Jordan", "Sam", "Riley", "Casey", "Morgan", "Drew", "Quinn", "Reese", "Sawyer"]
LAST = ["Whitfield", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel", "Osei"]
MESSAGES = [
    "my calf is swollen and hot since yesterday's session",
    "should I push through the pain on the band exercises",
    "can't make my appointment tomorrow, need to reschedule",
    "what time is my session thursday",
    "is it normal to be this sore two days after",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--patients", type=int, default=950)
    args = ap.parse_args()

    store.wipe()
    store.save("config", {"company": "Riverbend Physical Therapy", "clinics": 3,
                          "revenue": "$3.4M", "emr": "modelled, not connected"})

    patients, visits = [], []
    for i in range(args.patients):
        prescribed = rng.choice([8, 10, 12, 16])
        started = now() - timedelta(days=rng.randint(7, 90))
        auth = prescribed if rng.random() < 0.8 else (None if rng.random() < 0.3
                                                      else rng.randint(6, prescribed))
        p = {"id": f"pt_{i:04d}", "name": f"{rng.choice(FIRST)} {rng.choice(LAST)}",
             "status": "active" if rng.random() < 0.85 else "discharged",
             "visits_prescribed": prescribed, "visits_per_week": 2,
             "poc_started": iso(started), "authorized_visits": auth,
             "recert_due": iso(now() + timedelta(days=rng.randint(-5, 45)))
                           if rng.random() < 0.4 else None}
        patients.append(p)
        # visit history: some on track, some dropping out
        dropout = rng.random() < 0.25
        n = rng.randint(2, 5) if dropout else min(prescribed,
                                                  int((now() - started).days / 3.5))
        for k in range(max(0, n)):
            v = {"id": store.nid("vs"), "patient_id": p["id"],
                 "attended_at": iso(started + timedelta(days=3 * k + 1))}
            visits.append(v)
        for _ in range(rng.randint(0, 3) if dropout else 0):
            visits.append({"id": store.nid("vs"), "patient_id": p["id"],
                           "no_show": True} if rng.random() < 0.5 else
                          {"id": store.nid("vs"), "patient_id": p["id"],
                           "cancelled_at": iso(now() - timedelta(days=rng.randint(1, 20)))})

    # demo patients
    patients.append({"id": "pt_demo_over", "name": "Demo Over-Auth", "status": "active",
                     "visits_prescribed": 12, "visits_per_week": 2,
                     "poc_started": iso(now() - timedelta(days=45)),
                     "authorized_visits": 8, "demo_tag": "demo"})
    for k in range(8):
        visits.append({"id": store.nid("vs"), "patient_id": "pt_demo_over",
                       "attended_at": iso(now() - timedelta(days=44 - 5 * k))})
    patients.append({"id": "pt_demo_noauth", "name": "Demo No-Auth", "status": "active",
                     "visits_prescribed": 10, "visits_per_week": 2,
                     "poc_started": iso(now() - timedelta(days=10)),
                     "authorized_visits": None, "demo_tag": "demo"})
    patients.append({"id": "pt_demo_ok", "name": "Demo Within-Auth", "status": "active",
                     "visits_prescribed": 12, "visits_per_week": 2,
                     "poc_started": iso(now() - timedelta(days=14)),
                     "authorized_visits": 12, "demo_tag": "demo"})
    for k in range(4):
        visits.append({"id": store.nid("vs"), "patient_id": "pt_demo_ok",
                       "attended_at": iso(now() - timedelta(days=13 - 3 * k))})

    messages = [{"id": f"ms_{i:03d}", "patient_id": rng.choice(patients)["id"], "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(2, 48)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages.append({"id": "ms_demo_redflag", "patient_id": patients[0]["id"],
                     "text": "I can't control my bladder since this morning and my back is worse",
                     "at": iso(now() - timedelta(minutes=20)), "demo_tag": "demo"})

    store.save("patients", patients)
    store.save("visits", visits)
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"patients": len(patients), "visits": len(visits)})
    print(f"Seeded {len(patients)} patients, {len(visits)} visits, {len(messages)} messages")


if __name__ == "__main__":
    main()
