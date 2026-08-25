#!/usr/bin/env python3
"""Arrangement OS — synthetic funeral home. `python3 seed.py`.

"Hartwell & Sons Funeral Home" — 2 locations, a full GPL, ~60 active cases,
pre-need contracts, calls incl. first calls at hard hours. Synthetic only.
"""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(25)

GPL = [
    ("basic_services", "Basic services of funeral director and staff", 2495),
    ("transfer", "Transfer of remains to funeral home", 495),
    ("embalming", "Embalming", 895),
    ("dressing", "Dressing, casketing, cosmetology", 395),
    ("visitation", "Use of facilities for visitation (per day)", 595),
    ("service_chapel", "Funeral ceremony in our chapel", 795),
    ("graveside", "Graveside service", 595),
    ("hearse", "Hearse", 425),
    ("direct_cremation", "Direct cremation (container included)", 2395),
    ("cremation_service", "Memorial service with cremation", 3595),
    ("casket_poplar", "Poplar wood casket", 2895),
    ("casket_steel", "20-gauge steel casket", 1995),
    ("urn_standard", "Standard urn", 295),
]
CALLS = [
    "my father just passed at the hospice, they said to call you",
    "I'd like to plan ahead for myself, what does that look like",
    "how much is cremation with a small service",
    "are the death certificates ready? we need copies for the bank",
    "thank you all for everything last week",
]
LAST = ["Whitfield", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel", "Osei"]


def main():
    store.wipe()
    store.save("config", {"company": "Hartwell & Sons Funeral Home", "locations": 2,
                          "cases_yr": 380, "software": "modelled, not connected"})
    store.save("gpl", [{"key": k, "label": l, "price": p} for k, l, p in GPL])

    cases = []
    for i in range(60):
        opened = now() - timedelta(days=rng.randint(1, 40))
        docs = []
        for kind in rng.sample(core.DOC_TYPES, rng.randint(2, 3)):
            d = {"kind": kind, "requested_at": iso(opened + timedelta(days=1)), "touches": []}
            if rng.random() < 0.55:
                d["received_at"] = iso(opened + timedelta(days=rng.randint(2, 12)))
            elif kind.endswith("permit"):
                d["needed_by"] = iso(now() + timedelta(days=rng.randint(1, 10)))
            docs.append(d)
        cases.append({"id": f"cs_{i:03d}", "family": f"{rng.choice(LAST)} family",
                      "opened_at": iso(opened), "documents": docs})

    preneed = []
    for i in range(45):
        preneed.append({"id": f"pn_{i:03d}", "name": f"{rng.choice(LAST)} pre-need",
                        "funding_recorded": rng.random() < 0.7})

    calls = [{"id": f"cl_{i:03d}", "text": t,
              "at": iso(now() - timedelta(hours=rng.randint(1, 48)))}
             for i, t in enumerate(CALLS * 3)]
    calls.append({"id": "cl_demo_first",
                  "text": "mom died this morning at the hospital, we don't know what to do",
                  "at": iso(now() - timedelta(minutes=10)), "demo_tag": "demo"})

    store.save("cases", cases)
    store.save("preneed", preneed)
    store.save("calls", calls)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None, {"cases": len(cases)})
    print(f"Seeded {len(cases)} cases, {len(GPL)} GPL items, {len(preneed)} pre-need, "
          f"{len(calls)} calls")


if __name__ == "__main__":
    main()
