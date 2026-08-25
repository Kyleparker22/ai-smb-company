#!/usr/bin/env python3
"""Claim OS — synthetic Meridian Practice Solutions. Synthetic only, no real PHI."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(37)

PRACTICES = ["Lakeside Family Medicine", "Northgate Orthopedics", "Cedar Dermatology",
             "Fifth Street Pediatrics"]
PAYERS = ["BlueCap", "Medicare", "UnitedH"]
CARCS = ["CO-29", "CO-16", "CO-11", "CO-50", "CO-97", "PR-1"]


def main():
    store.wipe()
    store.save("config", {"company": "Meridian Practice Solutions", "revenue": "$3M",
                          "practices": len(PRACTICES)})
    store.save("practices", [{"id": f"pr_{i}", "name": n} for i, n in enumerate(PRACTICES)])

    claims = []
    for i in range(600):
        paid = rng.random() < 0.6
        c = {"id": f"cm_{i:04d}", "practice": rng.choice(PRACTICES),
             "payer": rng.choice(PAYERS), "cpt": rng.choice(core.RVU_ORDER),
             "icd10": rng.choice(["M54.5", "J06.9", "E11.9", "I10"]),
             "date_of_service": iso(now() - timedelta(days=rng.randint(5, 150))),
             "rendering_npi": f"12345{rng.randint(10000, 99999)}",
             "amount": rng.choice([85, 120, 145, 210, 260])}
        if paid:
            c["paid_at"] = iso(now() - timedelta(days=rng.randint(0, 60)))
        claims.append(c)
    claims.append({"id": "cm_demo_upcode", "practice": PRACTICES[0], "payer": "BlueCap",
                   "cpt": "99212", "icd10": "M54.5",
                   "date_of_service": iso(now() - timedelta(days=20)),
                   "rendering_npi": "1234512345", "amount": 120, "demo_tag": "demo"})
    claims.append({"id": "cm_demo_docd", "practice": PRACTICES[0], "payer": "BlueCap",
                   "cpt": "99212", "icd10": "M54.5",
                   "date_of_service": iso(now() - timedelta(days=20)),
                   "rendering_npi": "1234512345", "amount": 120,
                   "provider_doc_ref": "DOC-2214", "demo_tag": "demo"})
    claims.append({"id": "cm_demo_dirty", "practice": PRACTICES[1], "payer": None,
                   "cpt": "99213", "icd10": None,
                   "date_of_service": iso(now() - timedelta(days=3)),
                   "rendering_npi": None, "amount": 145, "demo_tag": "demo"})
    claims.append({"id": "cm_demo_atrisk", "practice": PRACTICES[2], "payer": "BlueCap",
                   "cpt": "99214", "icd10": "I10",
                   "date_of_service": iso(now() - timedelta(days=80)),
                   "rendering_npi": "1234598765", "amount": 210})
    store.save("claims", claims)

    denials = []
    for i in range(80):
        claim = rng.choice([c for c in claims if not c.get("paid_at") and not c.get("demo_tag")])
        denials.append({"id": f"dn_{i:03d}", "claim_id": claim["id"],
                        "carc": rng.choice(CARCS),
                        "denied_at": iso(now() - timedelta(days=rng.randint(3, 40)))})
    denials.append({"id": "dn_demo", "claim_id": "cm_demo_docd", "carc": "CO-50",
                    "denied_at": iso(now() - timedelta(days=16)), "demo_tag": "demo"})
    store.save("denials", denials)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None, {"claims": len(claims)})
    print(f"Seeded {len(claims)} claims, {len(denials)} denials")


if __name__ == "__main__":
    main()
