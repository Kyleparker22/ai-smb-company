#!/usr/bin/env python3
"""Traveler OS — synthetic job shop. `python3 seed.py`.

"Kestrel Precision Machining" — machines with capacity, ~140 jobs incl.
cert-required with and without paper, materials fresh and stale, RFQs incl.
cert language. Synthetic only.
"""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(29)

MATERIALS = [("al6061", "6061 aluminum bar", 4.2, 3), ("ss303", "303 stainless bar", 6.8, 5),
             ("ti64", "Ti-6Al-4V bar", 38.0, 40),  # stale on purpose
             ("brass360", "360 brass bar", 5.9, 2), ("delrin", "Delrin rod", 3.1, 60)]  # stale
RFQS = [
    ("qty 200 brackets, 6061, AS9100 required, certs with shipment", "al6061", 14),
    ("qty 50 pins, 303 stainless, no finish, need by friday", "ss303", 6),
    ("titanium spacers for a medical implant assembly, ISO 13485", "ti64", 22),
    ("simple aluminum plate, 12x12, 10 pieces", "al6061", 3),
    ("mill certs and heat lot numbers required with delivery", "brass360", 9),
    ("delrin bushings qty 500", "delrin", 11),
]


def main():
    store.wipe()
    store.save("config", {"company": "Kestrel Precision Machining", "people": 24,
                          "revenue": "$6.5M", "machine_rate_hr": 95, "margin_floor": 0.35,
                          "erp": "modelled, not connected"})

    store.save("machines", [{"id": f"mc_{i}", "name": n, "capacity_hrs_wk": h}
                            for i, (n, h) in enumerate([("Haas VF-2 #1", 80), ("Haas VF-2 #2", 80),
                                                        ("DMG 5-axis", 70), ("Citizen Swiss", 90),
                                                        ("Okuma lathe", 75)])])

    store.save("materials", [{"id": k, "label": l, "price": p,
                              "priced_at": iso(now() - timedelta(days=d))}
                             for k, l, p, d in MATERIALS])

    jobs = []
    for i in range(140):
        cert = rng.random() < 0.3
        shipped = rng.random() < 0.6
        promised = now() - timedelta(days=rng.randint(5, 150))
        j = {"id": f"jb_{i:03d}", "name": f"job {i}", "cert_required": cert,
             "est_hours": rng.randint(4, 60),
             "hours_remaining": 0 if shipped else rng.randint(2, 40),
             "promised_at": iso(promised)}
        if cert:
            j["material_cert_id"] = f"mc_{rng.randint(1000,9999)}" if rng.random() < 0.8 else None
            j["inspection_id"] = f"in_{rng.randint(1000,9999)}" if rng.random() < 0.85 else None
        if shipped:
            j["shipped_at"] = iso(promised + timedelta(days=rng.randint(-3, 6)))
        jobs.append(j)

    # demo jobs
    jobs.append({"id": "jb_demo_nocert", "name": "aerospace bracket (missing paper)",
                 "cert_required": True, "material_cert_id": None, "inspection_id": "in_5555",
                 "est_hours": 12, "hours_remaining": 0, "demo_tag": "demo"})
    jobs.append({"id": "jb_demo_certok", "name": "aerospace bracket (paper complete)",
                 "cert_required": True, "material_cert_id": "mc_7777", "inspection_id": "in_8888",
                 "est_hours": 12, "hours_remaining": 0, "demo_tag": "demo"})
    jobs.append({"id": "jb_demo_promise", "name": "new job needing a date",
                 "cert_required": False, "est_hours": 30, "hours_remaining": 30,
                 "demo_tag": "demo"})
    store.save("jobs", jobs)

    rfqs = []
    for i, (text, mat, hrs) in enumerate(RFQS * 2):
        rfqs.append({"id": f"rq_{i:03d}", "text": text, "material": mat, "est_hours": hrs,
                     "material_qty": rng.randint(5, 80),
                     "at": iso(now() - timedelta(hours=rng.randint(2, 72)))})
    rfqs.append({"id": "rq_demo_stale", "text": "titanium spacers, medical, ISO 13485",
                 "material": "ti64", "est_hours": 22, "material_qty": 30,
                 "at": iso(now() - timedelta(minutes=30)), "demo_tag": "demo"})
    rfqs.append({"id": "rq_demo_fresh", "text": "qty 200 brackets, 6061, AS9100 required",
                 "material": "al6061", "est_hours": 14, "material_qty": 60,
                 "at": iso(now() - timedelta(minutes=40)), "demo_tag": "demo"})
    store.save("rfqs", rfqs)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None, {"jobs": len(jobs), "rfqs": len(rfqs)})
    print(f"Seeded {len(jobs)} jobs, {len(rfqs)} RFQs, {len(MATERIALS)} materials (2 stale)")


if __name__ == "__main__":
    main()
