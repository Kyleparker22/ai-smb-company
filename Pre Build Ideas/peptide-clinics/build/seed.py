#!/usr/bin/env python3
"""Protocol OS — synthetic seed. Deterministic."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import CONTACTABLE, NEVER_CONTACT, store
from _kit.store import iso, now

R = random.Random(8897)

FIRST = ["Dana", "Marcus", "Priya", "Ellis", "Nora", "Tomas", "Ivy", "Reed", "Jonah", "Selma",
         "Colin", "Ruth", "Amara", "Felix", "Wren", "Oscar", "Lena", "Hugo", "Mira", "Cass"]
LAST = ["Alderman", "Boyle", "Cortez", "Duval", "Espinoza", "Frost", "Gallagher", "Hale",
        "Ibarra", "Jarrell", "Kwan", "Lindqvist", "Marek", "Nowak", "Okafor", "Pruitt"]
PROTOCOLS = [("Weight management program", 28), ("Recovery protocol", 30),
             ("Longevity protocol", 30), ("Sleep & recovery", 28), ("Metabolic program", 28)]
URGENT_MSGS = ["my face and lips are swelling up", "I can't breathe properly since last night",
               "chest pain and my heart is racing", "the injection site is hot and swollen with pus",
               "I fainted this morning"]
CLIN_MSGS = ["should I increase my dose this week?", "is it normal to feel this tired?",
             "can I combine this with my other medication", "I've had a headache for three days"]
ADMIN_MSGS = ["I need a copy of my receipt", "can I reschedule to Friday",
              "when is my next shipment going out", "my card on file expired"]


def build(n=260):
    store.wipe()
    store.save("config", {
        "company": "Ardenwood Longevity",
        "kind": "Cash-pay peptide & longevity clinic",
        "staff": "7 (1 MD, 2 NPs, 1 RN, 3 front of house)",
        "revenue": "~$2.9M/yr",
        "note": "SYNTHETIC DEMONSTRATION DATA — no real clinic, patient, protocol or message.",
    })

    patients, protocols, refills, labs, messages = [], [], [], [], []
    for i in range(n):
        pid = f"pt{i+1:04d}"
        roll = R.random()
        if roll < 0.62:
            status = "active"
        elif roll < 0.80:
            status = "lapsed"
        else:
            status = R.choice(NEVER_CONTACT)
        patients.append({"id": pid, "name": f"{R.choice(FIRST)} {R.choice(LAST)}",
                         "status": status,
                         "since": iso(now() - timedelta(days=R.randint(20, 900)))})

        if status in CONTACTABLE or R.random() < 0.7:
            name, interval = R.choice(PROTOCOLS)
            started = now() - timedelta(days=R.randint(25, 500))
            cycles = R.randint(1, 14)
            last_fill = now() - timedelta(days=R.randint(1, 70))
            last_change = None
            if R.random() < 0.30:
                last_change = iso(now() - timedelta(days=R.randint(5, 60)))
            protocols.append({"patient": pid, "name": name, "interval_days": interval,
                              "started_at": iso(started), "last_fill": iso(last_fill),
                              "cycles_filled": cycles, "last_change": last_change})
            for c in range(min(cycles, 6)):
                refills.append({"patient": pid, "at": iso(last_fill - timedelta(days=interval * c)),
                                "value": R.choice([320, 385, 420, 495, 550])})

        if R.random() < 0.25:
            drawn = now() - timedelta(days=R.randint(2, 60))
            labs.append({"id": store.nid("lab"), "patient": pid, "panel": R.choice(
                ["baseline metabolic", "lipid + A1c", "hormone panel", "CBC + CMP"]),
                "drawn_at": iso(drawn), "resulted_at": iso(drawn + timedelta(days=R.randint(1, 4))),
                "reviewed_at": iso(drawn + timedelta(days=R.randint(4, 12))) if R.random() < 0.6 else None})

    for i in range(34):
        pool = URGENT_MSGS if i < 5 else (CLIN_MSGS if i < 16 else ADMIN_MSGS)
        messages.append({"id": f"m{i+1:03d}", "patient": R.choice(patients)["id"],
                         "at": iso(now() - timedelta(hours=R.randint(1, 200))),
                         "text": R.choice(pool), "handled_at": None, "label": None})

    store.save("patients", patients)
    store.save("protocols", protocols)
    store.save("refills", refills)
    store.save("labs", labs)
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])

    for p in protocols[:60]:
        store.log_event("draft_refill_nudge", p["patient"], "agent:cycle", "R1", {})
        store.log_event("refill_sent", p["patient"], "human:frontdesk", "R1", {})

    excluded = sum(1 for p in patients if p["status"] in NEVER_CONTACT)
    print(f"seeded {len(patients)} patients ({excluded} permanently un-contactable) · "
          f"{len(protocols)} protocols · {len(messages)} messages · {len(labs)} lab panels")
    return {"patients": len(patients)}


if __name__ == "__main__":
    build()
