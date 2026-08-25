#!/usr/bin/env python3
"""Exam OS — synthetic optometry practice. `python3 seed.py [--patients 8200]`.

"Clearwater Eye Care" — patients with exam dates and Rx expiries, purchases,
messages incl. every emergency type. Synthetic only.
"""
import argparse, random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(27)

FIRST = ["Avery", "Jordan", "Sam", "Riley", "Casey", "Morgan", "Drew", "Quinn", "Reese", "Sawyer"]
LAST = ["Whitfield", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel", "Osei"]
MESSAGES = [
    "flashes and floaters since last night and now a dark curtain on the side",
    "is it normal for my eyes to be this dry with the new drops",
    "need to reorder contacts, running low",
    "can you send a copy of my prescription",
    "book an exam for me and my daughter",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--patients", type=int, default=8200)
    args = ap.parse_args()

    store.wipe()
    store.save("config", {"company": "Clearwater Eye Care", "doctors": 2, "revenue": "$2.6M",
                          "ehr": "modelled, not connected"})

    patients, exams, purchases = [], [], []
    for i in range(args.patients):
        last_exam = now() - timedelta(days=rng.randint(30, 900))
        p = {"id": f"pt_{i:05d}", "name": f"{rng.choice(FIRST)} {rng.choice(LAST)}",
             "status": "active" if rng.random() < 0.9 else "inactive",
             "last_exam": iso(last_exam),
             "cl_rx_expires": iso(last_exam + timedelta(days=365)) if rng.random() < 0.4 else None,
             "recalls": []}
        patients.append(p)
        if (now() - last_exam).days < 90:
            ex = {"id": store.nid("ex"), "patient_id": p["id"], "at": iso(last_exam)}
            exams.append(ex)
            if rng.random() < 0.55:
                purchases.append({"id": store.nid("pu"), "exam_id": ex["id"],
                                  "amount": round(rng.uniform(180, 650), 2)})

    # demo patients: expired Rx and current Rx
    patients.append({"id": "pt_demo_expired", "name": "Demo Expired-Rx", "status": "active",
                     "last_exam": iso(now() - timedelta(days=500)),
                     "cl_rx_expires": iso(now() - timedelta(days=135)),
                     "recalls": [], "demo_tag": "demo"})
    patients.append({"id": "pt_demo_current", "name": "Demo Current-Rx", "status": "active",
                     "last_exam": iso(now() - timedelta(days=100)),
                     "cl_rx_expires": iso(now() + timedelta(days=265)),
                     "recalls": [], "demo_tag": "demo"})

    messages = [{"id": f"ms_{i:03d}", "patient_id": rng.choice(patients)["id"], "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(2, 48)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages.append({"id": "ms_demo_retinal", "patient_id": patients[0]["id"],
                     "text": "flashes and floaters since last night and now a dark curtain on the side",
                     "at": iso(now() - timedelta(minutes=15)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_reorder_expired", "patient_id": "pt_demo_expired",
                     "text": "need to reorder contacts, running low",
                     "at": iso(now() - timedelta(minutes=25)), "demo_tag": "demo"})

    store.save("patients", patients)
    store.save("exams", exams)
    store.save("purchases", purchases)
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"patients": len(patients), "exams": len(exams)})
    print(f"Seeded {len(patients)} patients, {len(exams)} recent exams, "
          f"{len(purchases)} purchases, {len(messages)} messages")


if __name__ == "__main__":
    main()
