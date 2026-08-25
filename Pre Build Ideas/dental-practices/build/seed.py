#!/usr/bin/env python3
"""Chair OS — synthetic practice generator.

A two-doctor general practice with four hygiene chairs. Invented payer names,
555 numbers, no real patients. Built so an office manager recognizes their own
Tuesday: a ledger full of diagnosed-unscheduled treatment at every age, patients
whose benefit year is about to close, a payer that never answers the phone, and
a 7am cancellation waiting to happen.

  python3 seed.py --patients 1900 --months 24
"""
import argparse, random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

R = random.Random(20260816)

FIRST = ["Alma", "Bernard", "Corinne", "Dashiell", "Elsie", "Fitz", "Greta", "Hollis", "Inez",
         "Jonah", "Katarina", "Linus", "Mabel", "Nestor", "Orla", "Percival", "Rhoda", "Silas",
         "Tabitha", "Ulric", "Verity", "Warren", "Xenia", "Yusuf", "Zelda", "Priya", "Malik"]
LAST = ["Ackerley", "Bramwell", "Chastain", "Dunbar", "Ellington", "Fenwick", "Gallagher",
        "Hargrove", "Ipswich", "Jubilee", "Kettering", "Lambourne", "Mortimer", "Northcutt",
        "Oakhurst", "Pemberton", "Quillen", "Ramsgate", "Stanhope", "Trelawney"]

DOCTORS = ["Dr. Aurelia Nash", "Dr. Emmett Poe"]
HYGIENISTS = ["Dana Wexley, RDH", "Corinne Ault, RDH", "Marisol Vega, RDH", "Tess Bramley, RDH"]

TEETH = ["#3", "#14", "#19", "#30", "#2", "#31", "#12", "#20", "#8", "#9"]


def build(n_patients, months, reset=True):
    if reset:
        store.wipe()
    t0 = now()

    store.save("config", {
        "practice": "Northcutt Family Dental",
        "doctors": DOCTORS, "hygienists": HYGIENISTS,
        "chairs": {"dds": 3, "rdh": 4},
        "seeded_at": iso(),
        "roi_inputs": {"contact_rate": 0.55, "acceptance_rate": 0.28,
                       "canceled_hours_wk": 6, "fill_rate": 0.6,
                       "reactivation_rate": 0.22, "annual_patient_value": 640,
                       "verifications_wk": 95, "minutes_each": 11, "loaded_rate": 26},
    })
    store.save("providers", [{"id": f"dds_{i+1}", "name": n, "type": "dds"} for i, n in enumerate(DOCTORS)]
               + [{"id": f"rdh_{i+1}", "name": n, "type": "rdh"} for i, n in enumerate(HYGIENISTS)])
    store.save("payers", [{"key": k, **{kk: vv for kk, vv in v.items() if kk != "freq"}}
                          for k, v in core.PAYERS.items()])

    payer_keys = list(core.PAYERS)
    patients, plan_rows, appts = [], [], []

    for i in range(n_patients):
        # benefit years end at different points so the expiry hook is real for some
        year_end = t0 + timedelta(days=R.choice([18, 40, 62, 95, 140, 200, 280, 330]))
        p = {
            "id": f"pt_{i+1}", "name": f"{R.choice(FIRST)} {R.choice(LAST)}",
            "phone": f"555-03{R.randint(10,99)}",
            "payer": R.choices(payer_keys, [40, 28, 24, 8])[0],
            "coverage_active": R.random() < 0.94,
            "benefits_used": R.choice([0, 0, 112, 240, 380, 720, 1180]),
            "procedures_this_year": {"prophy": R.choice([0, 1, 1, 2]),
                                     "exam_periodic": R.choice([0, 1, 2])},
            # a slice deliberately has no enrollment date — waiting periods become unknowable
            "months_enrolled": R.choice([None, 2, 4, 9, 14, 26, 48]),
            "benefit_year_end": iso(year_end),
            # most of the book is current; a real practice's overdue list is a
            # third of it, not three quarters — a seed that makes every patient
            # overdue produces an ROI number an office manager will laugh at
            "last_hygiene": (iso(t0 - timedelta(days=R.choices(
                [R.randint(10, 120), R.randint(120, 200), R.randint(200, 400), R.randint(400, 900)],
                [46, 24, 20, 10])[0]))
                if R.random() < 0.82 else None),
            "hygiene_type": R.choices(["prophy", "perio_maint"], [78, 22])[0],
            # a slice has no recorded responsiveness — the ranker must say so
            "responsiveness": R.choice([None, 0.2, 0.4, 0.6, 0.8, 0.95]),
            "flexible": R.random() < 0.28,
            "distance_min": R.choice([6, 9, 14, 20, 28, 40]),
            "short_notice_history": R.choice([None, 0, 1, 2, 3, 4]),
        }
        patients.append(p)

        # diagnosed-but-unscheduled treatment — the asset
        for _ in range(R.choices([0, 1, 2, 3], [52, 27, 14, 7])[0]):
            proc = R.choices(list(core.PROCEDURES),
                             [2, 4, 5, 9, 16, 20, 9, 7, 4, 6])[0]
            diag = t0 - timedelta(days=R.randint(10, 700))
            plan_rows.append({
                "id": f"tp_{len(plan_rows)+1}", "patient_id": p["id"], "procedure": proc,
                "tooth": R.choice(TEETH) if core.PROCEDURES[proc]["cat"] in
                         ("restorative", "major", "endo", "oral_surgery") else None,
                "diagnosed_at": iso(diag), "diagnosed_by": R.choice(DOCTORS),
                "state": R.choices(["unscheduled", "scheduled", "declined"], [0.74, 0.16, 0.10])[0]})

    store.save("patients", patients)
    store.save("treatment_plan", plan_rows)

    # -- the schedule: history + tomorrow ---------------------------------
    for i in range(int(n_patients * 1.7)):
        when = t0 - timedelta(days=R.randint(1, months * 30), hours=R.randint(0, 8))
        proc = R.choices(list(core.PROCEDURES), [12, 30, 10, 6, 14, 12, 5, 5, 2, 4])[0]
        spec = core.PROCEDURES[proc]
        appts.append({"id": f"ap_{i+1}", "patient_id": R.choice(patients)["id"],
                      "procedure": proc, "starts_at": iso(when), "state": "complete",
                      "provider_type": spec["provider"], "minutes": spec["minutes"]})

    tomorrow = (t0 + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
    slot = 0
    for hour in range(8, 17):
        for chair in ("dds", "dds", "rdh", "rdh"):
            if R.random() < 0.22:
                continue
            proc = R.choice([k for k, v in core.PROCEDURES.items() if v["provider"] == chair])
            spec = core.PROCEDURES[proc]
            slot += 1
            appts.append({"id": f"ap_tm_{slot}", "patient_id": R.choice(patients)["id"],
                          "procedure": proc, "starts_at": iso(tomorrow.replace(hour=hour)),
                          "state": "scheduled", "provider_type": chair, "minutes": spec["minutes"]})

    # two deliberate holes tomorrow — one hygiene, one doctor
    appts.append({"id": "ap_hole_rdh", "patient_id": None, "procedure": None,
                  "starts_at": iso(tomorrow.replace(hour=10)), "state": "open",
                  "provider_type": "rdh", "minutes": 60, "demo_tag": "hygiene hole"})
    appts.append({"id": "ap_hole_dds", "patient_id": None, "procedure": None,
                  "starts_at": iso(tomorrow.replace(hour=14)), "state": "open",
                  "provider_type": "dds", "minutes": 90, "demo_tag": "doctor hole"})
    # and a live 7:04am cancellation to walk through
    appts.append({"id": "ap_cancel_demo", "patient_id": patients[3]["id"], "procedure": "crown",
                  "starts_at": iso(t0.replace(hour=9, minute=0) + timedelta(days=1)),
                  "state": "scheduled", "provider_type": "dds", "minutes": 90,
                  "demo_tag": "cancels at 7:04am"})

    store.save("appointments", appts)
    store.save("verifications", [])
    store.save("recall", [])
    store.save("approvals", [])
    store.save("events", [])
    return {"patients": len(patients), "treatment_plan": len(plan_rows), "appointments": len(appts)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--patients", type=int, default=1900)
    ap.add_argument("--months", type=int, default=24)
    a = ap.parse_args()
    print(build(a.patients, a.months))
