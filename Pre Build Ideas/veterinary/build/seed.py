#!/usr/bin/env python3
"""Visit OS — synthetic practice. `python3 seed.py [--patients 2400]`.

"Brookhollow Veterinary Clinic" — 3 DVMs, dogs/cats plus a few exotics,
statuses incl. deceased/transferred, due dates across the calendar, a waitlist,
messages incl. every crisis type. Synthetic only; 555 phones.
"""
import argparse, random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(13)

PET_NAMES = ["Biscuit", "Mochi", "Zeus", "Willow", "Pepper", "Finn", "Luna", "Ozzy", "Maple",
             "Ginger", "Bandit", "Clover", "Tank", "Poppy", "Miso", "Rocket", "Hazel", "Bruno"]
OWNERS = ["Whitfield", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel", "Osei",
          "Delacroix", "Yamada", "Pruitt", "Calloway", "Bostic", "Renner", "Iglesias", "Thorne"]
DOCTORS = ["Dr. Ashby", "Dr. Nakamura", "Dr. Vidal"]

MESSAGES = [
    "my dog just ate a bar of baker's chocolate",
    "he keeps retching but nothing comes up and his belly looks swollen",
    "my cat has been straining in the litter box and nothing, he's crying",
    "what dose of benadryl can I give a 40lb dog",
    "she's been vomiting since yesterday, should I be worried",
    "I think it might be time to put her to sleep, I don't know",
    "can I book a nail trim for saturday",
    "need to schedule his annual and vaccines that are due",
    "hi, quick question when you get a chance",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--patients", type=int, default=2400)
    args = ap.parse_args()

    store.wipe()
    store.save("config", {"company": "Brookhollow Veterinary Clinic", "dvms": 3,
                          "revenue": "$2.8M", "pims": "modelled, not connected"})

    clients, patients = [], []
    for i in range(args.patients):
        cid = f"cl_{i:04d}"
        clients.append({"id": cid, "name": f"{rng.choice(OWNERS)} family",
                        "phone": f"555-{rng.randint(200,999)}-{rng.randint(1000,9999)}"})
        status = rng.choices(["active", "deceased", "transferred"], weights=[0.86, 0.09, 0.05])[0]
        species = rng.choices(["dog", "cat", "rabbit"], weights=[0.6, 0.36, 0.04])[0]
        # due dates: a healthy slice current, a big slice lapsed at varying depth
        def due(p_overdue):
            if rng.random() < p_overdue:
                return iso(now() - timedelta(days=rng.randint(10, 400)))
            return iso(now() + timedelta(days=rng.randint(10, 300)))
        patients.append({"id": f"pt_{i:04d}", "client_id": cid,
                         "name": rng.choice(PET_NAMES), "species": species, "status": status,
                         "annual_due": due(0.30), "vaccines_due": due(0.25),
                         "preventive_due": due(0.35) if species != "rabbit" else None,
                         "reminders": []})

    # ensure one demo deceased patient that IS lapsed on paper
    patients.append({"id": "pt_demo_deceased", "client_id": clients[0]["id"],
                     "name": "Scout", "species": "dog", "status": "deceased",
                     "annual_due": iso(now() - timedelta(days=200)),
                     "vaccines_due": iso(now() - timedelta(days=180)), "reminders": [],
                     "demo_tag": "demo"})

    appointments = []
    for i in range(400):
        when = now() + timedelta(days=rng.randint(-90, 21), hours=rng.randint(8, 17) - 12)
        a = {"id": f"ap_{i:04d}", "patient_id": rng.choice(patients)["id"],
             "doctor": rng.choice(DOCTORS), "minutes": rng.choice([20, 30, 40]),
             "when": iso(when), "value": round(rng.uniform(90, 480), 2)}
        if when < now() and rng.random() < 0.12:
            a["cancelled_at"] = iso(when - timedelta(days=1))
            if rng.random() < 0.4:
                a["backfilled_at"] = iso(when)
        appointments.append(a)
    # a demo bookable slot tomorrow
    appointments.append({"id": "ap_demo", "patient_id": patients[0]["id"],
                         "doctor": DOCTORS[0], "minutes": 30,
                         "when": iso(now() + timedelta(days=1, hours=2)),
                         "value": 240.0, "demo_tag": "demo"})

    waitlist = []
    for i in range(14):
        p = rng.choice([x for x in patients if x["status"] == "active"])
        waitlist.append({"id": f"wl_{i:03d}", "patient_id": p["id"], "name": p["name"],
                         "species": p["species"], "minutes_needed": rng.choice([20, 30, 40]),
                         "doctor_pref": rng.choice([None, *DOCTORS]),
                         "reason_urgencyish": rng.random() < 0.3,
                         "since": iso(now() - timedelta(days=rng.randint(1, 30)))})
    # one waitlist row pointing at a deceased patient — must be blocked, never offered
    waitlist.append({"id": "wl_deceased", "patient_id": "pt_demo_deceased", "name": "Scout",
                     "species": "dog", "minutes_needed": 30, "doctor_pref": None,
                     "since": iso(now() - timedelta(days=10))})

    messages = [{"id": f"ms_{i:03d}", "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(1, 48)))}
                for i, t in enumerate(MESSAGES)]

    store.save("clients", clients)
    store.save("patients", patients)
    store.save("appointments", appointments)
    store.save("waitlist", waitlist)
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"patients": len(patients), "appointments": len(appointments)})
    print(f"Seeded {len(patients)} patients, {len(appointments)} appointments, "
          f"{len(waitlist)} waitlist, {len(messages)} messages")


if __name__ == "__main__":
    main()
