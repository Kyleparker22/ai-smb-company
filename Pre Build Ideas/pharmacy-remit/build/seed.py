#!/usr/bin/env python3
"""Remit OS — synthetic Lakeside Pharmacy. Synthetic only: invented PBMs and
brand drugs, invented patients, 555 phones. No real PHI ever."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(66)

# (drug, awp_per_unit, brand, acq_per_unit or None — None = deliberately unrecorded)
DRUGS = [
    ("Atorvastatin 20mg", 0.42, False, 0.06),
    ("Lisinopril 10mg", 0.18, False, 0.02),
    ("Metformin 500mg", 0.22, False, 0.03),
    ("Amlodipine 5mg", 0.30, False, 0.04),
    ("Sertraline 50mg", 0.55, False, 0.07),
    ("Omeprazole 20mg", 0.35, False, 0.05),
    ("Zephrelex 50mg", 14.80, True, 11.90),      # invented brand
    ("Corvalyn XR 100mg", 6.40, True, 4.05),     # invented brand — the ambiguity fixture
    ("Velotrix 25mg", 3.75, False, None),        # acquisition cost deliberately unrecorded
    ("Duloxetine 30mg", 0.62, False, None),      # acquisition cost deliberately unrecorded
]
PATIENTS = ["Marisol Vance", "Dot Ellery", "Ambrose Kittle", "Renata Osei", "Hal Pruitt",
            "Ines Barrera", "Clyde Mercer", "Yuki Yamada", "Ora Bostic", "Felix Havel",
            "Nadia Trujillo", "Wes Calloway"]

MESSAGES = [
    "is my refill ready for pickup",
    "why did my copay double this month",
    "the pbm says this drug is not covered anymore",
    "what time do you close on sunday",
]


def _patient(i):
    return rng.choice(PATIENTS), f"(555) 014-{1000 + (i % 8999):04d}"


def _line(i, pbm, drug_t, variance):
    """Build one remittance line; `paid` derives from the RECORDED contract
    arithmetic (via core), so seed and autopsy can never disagree on 'correct'."""
    drug, awp, brand, _ = drug_t
    qty = rng.choice([90, 180] if drug == "Metformin 500mg" else [30, 60, 90])
    name, phone = _patient(i)
    line = {"script_ref": f"RX-{60000 + i}", "drug": drug, "qty": qty, "awp": awp,
            "brand": brand, "patient": name, "patient_phone": phone}
    c = core.contracts().get(pbm)
    if not c:  # the unrecorded PBM — paid is whatever the PBM says it is
        line["paid"] = round(awp * qty * 0.8, 2)
        line["dir_taken"] = round(line["paid"] * 0.04, 2)
        return line
    r = core.expected_readings(line, c)
    expected = r["readings"][-1]["expected"]  # controlling reading for unambiguous lines
    if variance == "underpaid":
        line["paid"] = round(max(expected - rng.uniform(2.0, 45.0), 0.50), 2)
        line["dir_taken"] = round(c["dir_pct"] * line["paid"], 2)
    elif variance == "dir":
        line["paid"] = expected
        line["dir_taken"] = round(c["dir_pct"] * line["paid"] + rng.uniform(1.0, 9.0), 2)
    else:
        line["paid"] = expected
        line["dir_taken"] = round(c["dir_pct"] * line["paid"], 2)
    return line


def _remit_lines(pbm, n, n_under, n_dir, start, pool):
    plan = ["underpaid"] * n_under + ["dir"] * n_dir + ["correct"] * (n - n_under - n_dir)
    rng.shuffle(plan)
    return [_line(start + i, pbm, rng.choice(pool), v) for i, v in enumerate(plan)]


def main():
    store.wipe()
    store.save("config", {
        "company": "Lakeside Pharmacy", "scripts_per_day": 310, "pbm_contracts": 3,
        "acquisition": {
            "_source": ("recorded wholesaler acquisition costs, per unit, from the last "
                        "invoice cycle — a drug with no recorded cost reads unmeasured"),
            "costs": {d: a for d, _, _, a in DRUGS if a is not None}},
    })

    # CareMax Rx — recorded; carries the big hand-checkable underpaid line.
    # Random pool excludes Corvalyn (ambiguity stays a deliberate 2-line fixture).
    cm_pool = [d for d in DRUGS if d[0] != "Corvalyn XR 100mg"]
    cm_lines = _remit_lines("CareMax Rx", 168, 12, 7, 0, cm_pool)
    cm_lines.append({  # the demo underpayment: expected 378.65, paid 166.18, delta 212.47
        "script_ref": "RX-88214", "drug": "Zephrelex 50mg", "qty": 30, "awp": 14.80,
        "brand": True, "patient": "Marisol Vance", "patient_phone": "(555) 014-7212",
        "paid": 166.18, "dir_taken": 4.99})
    dir_expected = core.expected_readings(
        {"drug": "Sertraline 50mg", "qty": 30, "awp": 0.55},
        core.contracts()["CareMax Rx"])["readings"][0]["expected"]
    cm_lines.append({  # the demo DIR drift: paid correct, DIR over-withheld by exactly $5.25
        "script_ref": "RX-77103", "drug": "Sertraline 50mg", "qty": 30, "awp": 0.55,
        "brand": False, "patient": "Hal Pruitt", "patient_phone": "(555) 014-3390",
        "paid": dir_expected, "dir_taken": round(0.03 * dir_expected, 2) + 5.25})

    # OptiScript — recorded; MAC list live (metformin below acquisition cost —
    # the dispensed-at-a-loss story) and the two ambiguous brand-on-MAC lines.
    os_pool = [d for d in DRUGS if d[0] != "Corvalyn XR 100mg"]
    os_lines = _remit_lines("OptiScript", 166, 13, 8, 200, os_pool)
    os_lines += [_line(380 + i, "OptiScript",
                       next(d for d in DRUGS if d[0] == "Metformin 500mg"), "correct")
                 for i in range(12)]
    for i, ref in enumerate(("RX-90455", "RX-90456")):  # ambiguous: brand on the MAC list
        name, phone = _patient(500 + i)
        os_lines.append({"script_ref": ref, "drug": "Corvalyn XR 100mg", "qty": 60,
                         "awp": 6.40, "brand": True, "patient": name, "patient_phone": phone,
                         "paid": 126.85, "dir_taken": 6.34})

    # Pinnacle Health Rx — remittance in hand, contract never recorded → UNAUDITABLE.
    px_lines = [_line(600 + i, "Pinnacle Health Rx", rng.choice(cm_pool), "correct")
                for i in range(50)]

    remits = [
        {"id": "rm_cm_01", "pbm": "CareMax Rx", "remit_date": iso(now() - timedelta(days=12)),
         "lines": cm_lines},
        {"id": "rm_os_01", "pbm": "OptiScript", "remit_date": iso(now() - timedelta(days=20)),
         "lines": os_lines},
        {"id": "rm_px_01", "pbm": "Pinnacle Health Rx",
         "remit_date": iso(now() - timedelta(days=9)), "lines": px_lines},
    ]

    # Demo remit: an underpayment whose 60-day OptiScript window has already
    # lapsed — the expired DATE ALERT, kept out of every counted board.
    exp = core.expected_readings({"drug": "Sertraline 50mg", "qty": 60, "awp": 0.55},
                                 core.contracts()["OptiScript"])["readings"][0]["expected"]
    remits.append({"id": "rm_demo_expired", "pbm": "OptiScript", "demo_tag": "demo",
                   "remit_date": iso(now() - timedelta(days=75)),
                   "lines": [{"script_ref": "RX-99001", "drug": "Sertraline 50mg", "qty": 60,
                              "awp": 0.55, "brand": False, "patient": "Dot Ellery",
                              "patient_phone": "(555) 014-2288", "paid": 20.00,
                              "dir_taken": 1.00, "_note_expected": exp}]})
    store.save("remits", remits)

    messages = [{"id": f"ms_{i:03d}", "from": rng.choice(PATIENTS), "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(1, 72)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages.append({"id": "ms_demo_wrongmed", "from": "Marisol Vance",
                     "text": "i think i got the wrong pills",
                     "at": iso(now() - timedelta(minutes=12)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_pbm", "from": "Clyde Mercer",
                     "text": "my insurance rejected the refill and says prior authorization is needed",
                     "at": iso(now() - timedelta(minutes=45)), "demo_tag": "demo"})
    store.save("messages", messages)

    store.save("findings", [])
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"remits": len(remits),
                     "lines": sum(len(r["lines"]) for r in remits)})
    print(f"Seeded {len(remits)} remittances "
          f"({sum(len(r['lines']) for r in remits)} lines), "
          f"{len(messages)} messages — 1 PBM deliberately unrecorded")


if __name__ == "__main__":
    main()
