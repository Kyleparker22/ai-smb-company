#!/usr/bin/env python3
"""Well OS — synthetic Blue Ridge Well & Water. Synthetic only; 555 phones."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(52)

LAST = ["Kowalczyk", "Tavares", "Aldeen", "McElroy", "Bruns", "Ferebee", "Okonkwo", "Stallard",
        "Vickery", "Halvorsen", "Reyes-Cota", "Pfaff", "Dunbar", "Yoon", "Castellano", "Wren",
        "Ashworth", "Nakagawa", "Trivette", "Boggs"]
COUNTIES = ["Harlan", "Beaufort", "Watauga"]
COMPONENTS = [("sediment_filter", 180, 149), ("carbon_filter", 365, 229),
              ("uv_lamp", 365, 189), ("softener_media", 1095, 499)]
RESULTS = [
    "Total coliform: ABSENT · E. coli: ABSENT — meets the state drinking-water standard",
    "Total coliform: ABSENT · nitrate 4.1 mg/L (limit 10) — meets the state drinking-water standard",
    "Total coliform: PRESENT · E. coli: ABSENT — retest and shock disinfection advised",
    "Iron 1.9 mg/L (secondary limit 0.3) — treatment recommended; not a health-based exceedance",
]
MESSAGES = [
    "is my uv lamp due for a change",
    "any update on our drilling permit",
    "can you price a softener install",
    "what time do you open saturday",
]


def main():
    store.wipe()
    store.save("config", {"company": "Blue Ridge Well & Water", "rigs": 2,
                          "service_contracts": 350, "counties": COUNTIES})

    customers = [{"id": f"cu_{i:03d}", "name": rng.choice(LAST),
                  "phone": f"555-01{i % 100:02d}"} for i in range(350)]
    store.save("customers", customers)

    wells = []
    for i in range(40):
        w = {"id": f"we_{i:03d}", "owner": rng.choice(LAST),
             "county": rng.choice(COUNTIES)}
        if rng.random() < 0.75:  # a recorded log; the rest were never measured
            w.update(depth_ft=rng.randrange(120, 620, 20), casing_ft=rng.randrange(40, 120, 5),
                     yield_gpm=round(rng.uniform(2, 30), 1),
                     static_level_ft=rng.randrange(20, 90, 5),
                     logged_at=iso(now() - timedelta(days=rng.randint(30, 2000))))
        wells.append(w)
    wells.append({"id": "we_demo_logged", "owner": "Ferebee", "county": "Harlan",
                  "depth_ft": 340, "casing_ft": 80, "yield_gpm": 12.0,
                  "static_level_ft": 45,
                  "logged_at": iso(now() - timedelta(days=200)), "demo_tag": "demo"})
    wells.append({"id": "we_demo_nolog", "owner": "Tavares", "county": "Beaufort",
                  "demo_tag": "demo"})
    store.save("wells", wells)

    reports = []
    for i, w in enumerate(w for w in wells[:40] if rng.random() < 0.55):
        sampled = now() - timedelta(days=rng.randint(10, 400))
        pending = rng.random() < 0.15
        reports.append({"id": f"lr_{i:03d}", "well_id": w["id"],
                        "report_no": f"LR-26-{1000 + i}", "lab": "Ridgeline Analytical",
                        "sampled_at": iso(sampled),
                        "received_at": None if pending else iso(sampled + timedelta(days=6)),
                        "result": None if pending else rng.choice(RESULTS)})
    reports.append({"id": "lr_demo_ok", "well_id": "we_demo_logged",
                    "report_no": "LR-26-0417", "lab": "Ridgeline Analytical",
                    "sampled_at": iso(now() - timedelta(days=12)),
                    "received_at": iso(now() - timedelta(days=6)),
                    "result": RESULTS[0], "demo_tag": "demo"})
    store.save("lab_reports", reports)

    systems = []
    for i in range(300):
        comps = []
        for kind, interval, ticket in rng.sample(COMPONENTS, rng.randint(1, 3)):
            comp = {"kind": kind, "interval_days": interval, "ticket": ticket}
            if rng.random() > 0.05:  # a few clocks nobody ever recorded
                comp["last_service_at"] = iso(now() - timedelta(days=rng.randint(5, 500)))
            comps.append(comp)
        systems.append({"id": f"sy_{i:03d}", "customer_name": rng.choice(LAST),
                        "well_id": f"we_{rng.randint(0, 39):03d}", "components": comps})
    systems.append({"id": "sy_demo_overdue", "customer_name": "Kowalczyk",
                    "well_id": "we_demo_logged", "demo_tag": "demo",
                    "components": [{"kind": "uv_lamp", "interval_days": 365, "ticket": 189,
                                    "last_service_at": iso(now() - timedelta(days=460))}]})
    store.save("systems", systems)

    jobs = []
    for i in range(18):
        stage = rng.choice(core.STAGES[:5])
        j = {"id": f"jb_{i:03d}", "customer_name": rng.choice(LAST),
             "county": rng.choice(COUNTIES), "stage": stage,
             "permit_issued_at": iso(now() - timedelta(days=rng.randint(10, 170)))}
        if stage in ("pump_test", "water_test", "state_report"):
            j["drilled_at"] = iso(now() - timedelta(days=rng.randint(5, 40)))
        jobs.append(j)
    store.save("jobs", jobs)

    messages = [{"id": f"ms_{i:03d}", "from": rng.choice(LAST), "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(1, 72)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages.append({"id": "ms_demo_contam", "from": "Kowalczyk",
                     "text": "my water smells like rotten eggs",
                     "at": iso(now() - timedelta(minutes=20)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_dry", "from": "McElroy",
                     "text": "we have no water at the house this morning",
                     "at": iso(now() - timedelta(minutes=35)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_quote", "from": "Tavares",
                     "text": "how much to drill a new well on our property",
                     "at": iso(now() - timedelta(minutes=50)), "demo_tag": "demo"})
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"systems": len(systems), "wells": len(wells)})
    print(f"Seeded {len(customers)} households, {len(wells)} wells, {len(systems)} systems, "
          f"{len(jobs)} jobs, {len(reports)} lab reports, {len(messages)} messages")


if __name__ == "__main__":
    main()
