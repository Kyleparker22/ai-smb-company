#!/usr/bin/env python3
"""Case OS — synthetic firm generator.

A six-attorney personal-injury firm. Invented client, provider and insurer
names, 555 numbers, no real people. Built so a managing attorney recognizes
their own docket: leads at 2am, borderline screens, providers that stall,
incomplete productions, and matters that have gone quiet.

  python3 seed.py --matters 310 --months 24
"""
import argparse, random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

R = random.Random(20260816)

FIRST = ["Dana", "Reggie", "Marisol", "Terrence", "Aisling", "Kwabena", "Lorraine", "Dmitri",
         "Perpetua", "Hollis", "Yvette", "Barrett", "Nadira", "Clemens", "Fern", "Ozzie",
         "Simone", "Gil", "Ravenna", "Toby", "Winnie", "Amos", "Delphine", "Rueben"]
LAST = ["Reyes", "Okafor", "Villanueva", "Bright", "Cassidy", "Drummond", "Estrada", "Fairbairn",
        "Guillory", "Hutchins", "Ibarra", "Janowicz", "Kowalczyk", "Lassiter", "Mbeki",
        "Nakamura", "Ortiz", "Prewitt", "Quintero", "Rasmussen"]
ATTORNEYS = ["Vera Sandoval", "Emmanuel Boateng", "Cassandra Lin", "Hugh Devereaux",
             "Priya Anand", "Roland Marsh"]
PARALEGALS = ["Sam Whitby", "Delia Osorio", "Kenji Alvarez", "Maureen Slade"]

FACILITIES = [
    ("Cedarbrook Regional", dict(format="ror_form", needs_prepay=True, prepay_amount=45, turnaround_days=30)),
    ("Harborlight Orthopedics", dict(format="portal", portal="harborlight-roi", turnaround_days=14)),
    ("Ninth Street Imaging", dict(format="fax", turnaround_days=21)),
    ("Ridgeway Physical Therapy", dict(format="email", turnaround_days=10)),
    ("Meridian Emergency Group", dict(format="ror_form", needs_prepay=True, prepay_amount=75,
                                      turnaround_days=45, escalation_contact="custodian of records")),
    ("Palisade Family Medicine", dict(format="ror_form", turnaround_days=18)),
    ("Sable Chiropractic", dict(format="email", turnaround_days=7)),
    ("Vantage Surgical Center", dict(format="portal", portal="vantage-hio", turnaround_days=28)),
]
INSURERS = ["Ironvale Mutual", "Cascade Standard", "Pemberton Casualty", "Northlight"]

ENTRY_KINDS = [("ED evaluation", 2400), ("MRI lumbar", 1850), ("PT session", 165),
               ("Ortho consult", 420), ("Injection", 1250), ("Follow-up", 210)]


def build(n_matters, months, reset=True):
    if reset:
        store.wipe()
    t0 = now()

    store.save("config", {
        "firm": "Sandoval Boateng Injury Law",
        "attorneys": ATTORNEYS, "paralegals": PARALEGALS,
        "criteria": {"accepted_types": ["auto", "premises", "dog_bite", "trucking"],
                     "states": ["NC", "SC"]},
        "seeded_at": iso(),
        "roi_inputs": {"incremental_sign_rate": 0.08, "days_removed": 22, "daily_carry": 14,
                       "paralegal_hours_wk": 26, "loaded_rate": 34, "rescued_per_year": 6},
    })
    store.save("providers", [{"id": f"pv_{i+1}", "name": n, **cfg}
                             for i, (n, cfg) in enumerate(FACILITIES)])

    clients, matters, records, productions, contacts, leads = [], [], [], [], [], []

    for i in range(n_matters):
        name = f"{R.choice(FIRST)} {R.choice(LAST)}"
        ct = R.choices(["auto", "premises", "dog_bite", "trucking"], [64, 18, 10, 8])[0]
        # a real docket has a few cases approaching the statute — the alert is
        # worthless if the seed never produces one
        incident = t0 - timedelta(days=R.choices(
            [R.randint(20, 400), R.randint(400, 900), R.randint(1010, 1080)],
            [62, 30, 8])[0])
        stage = R.choices(core.STAGES[1:], [10, 26, 22, 16, 12, 8, 6])[0]
        clients.append({"id": f"cl_{i+1}", "name": name, "phone": f"555-05{R.randint(10,99)}"})
        m = {"id": f"mt_{i+1}", "client_id": f"cl_{i+1}", "client_name": name,
             "case_type": ct, "incident_date": iso(incident),
             "stage": stage, "attorney": R.choice(ATTORNEYS),
             "paralegal": R.choice(PARALEGALS),
             "opposing": f"{R.choice(FIRST)} {R.choice(LAST)}",
             "insurer": R.choice(INSURERS),
             "treatment_end": iso(incident + timedelta(days=R.randint(60, 260)))
             if stage not in ("intake", "signed", "treating") else None}
        matters.append(m)

        # contact history — a slice deliberately silent, a slice never contacted.
        # The first six are held out of the status sweep AND given no contact at
        # all, so the walkthrough always has a genuinely silent matter to point
        # at rather than one the sweep already cleaned up.
        if i < 6:
            m["demo_tag"] = "held out of the status sweep"
        elif R.random() < 0.12:
            pass                                    # never contacted at all
        else:
            last = t0 - timedelta(days=R.choices([3, 9, 18, 34, 52, 88], [30, 24, 18, 14, 9, 5])[0])
            contacts.append({"id": f"ct_{len(contacts)+1}", "matter_id": m["id"],
                             "at": iso(last), "kind": "call"})

        if stage in ("records", "demand", "negotiation", "litigation"):
            for p in R.sample(store.load("providers"), R.randint(2, 5)):
                st = R.choices(["sent", "produced", "complete", "drafted"], [30, 26, 34, 10])[0]
                rec = {"id": f"rc_{len(records)+1}", "matter_id": m["id"], "provider_id": p["id"],
                       "patient_name": name, "state": st,
                       "date_from": m["incident_date"],
                       "date_to": m.get("treatment_end") or iso(t0),
                       "sent_at": iso(t0 - timedelta(days=R.randint(5, 120)))
                       if st != "drafted" else None}
                records.append(rec)
                if st in ("produced", "complete"):
                    # a real slice of productions are INCOMPLETE on purpose
                    bad = R.random() < 0.38
                    prod = {"id": f"pr_{len(productions)+1}", "request_id": rec["id"],
                            "matter_id": m["id"], "patient_name": name,
                            "date_from": (iso(parse_shift(m["incident_date"], 45)) if bad and R.random() < 0.5
                                          else m["incident_date"]),
                            "date_to": m.get("treatment_end") or iso(t0),
                            "has_billing": not (bad and R.random() < 0.5),
                            "illegible_pages": R.choice([0, 0, 0, 3]) if bad else 0,
                            "verified": st == "complete" and not bad,
                            "entries": [{"date": iso(t0 - timedelta(days=R.randint(30, 400))),
                                         "what": k, "charge": c,
                                         "exhibit": chr(65 + R.randint(0, 6)),
                                         "page": R.randint(1, 80)}
                                        for k, c in R.sample(ENTRY_KINDS, R.randint(1, 4))]}
                    # a couple of entries deliberately lack a citation
                    if R.random() < 0.3 and prod["entries"]:
                        prod["entries"].append({"date": iso(t0 - timedelta(days=90)),
                                                "what": "Chiropractic (referenced, no record)",
                                                "charge": 480})
                    if st == "complete" and not bad:
                        rec["state"] = "complete"
                    productions.append(prod)

    # -- leads --------------------------------------------------------------
    for i in range(int(n_matters * 3)):
        hour = R.choices(range(0, 24), [4, 3, 3, 2, 2, 2, 3, 4, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6,
                                        5, 5, 5, 4, 4, 4])[0]
        when = (t0 - timedelta(days=R.randint(0, months * 30))).replace(hour=hour)
        ct = R.choices(["auto", "premises", "dog_bite", "trucking", "workers_comp"],
                       [56, 16, 9, 7, 12])[0]
        leads.append({
            "id": f"ld_{i+1}", "at": iso(when), "name": f"{R.choice(FIRST)} {R.choice(LAST)}",
            "opposing": f"{R.choice(FIRST)} {R.choice(LAST)}",
            "after_hours": hour < 8 or hour >= 18,
            "message": R.choice(["I was rear-ended yesterday", "do I have a case?",
                                 "what's my case worth", "a dog bit my son at a park",
                                 "I slipped at a grocery store", "I need a lawyer"]),
            "facts": {"case_type": ct, "state": R.choices(["NC", "SC", "VA"], [70, 22, 8])[0],
                      "incident_date": iso(when - timedelta(days=R.choice([1, 5, 40, 400, 1300]))),
                      "liability_facts": R.random() < 0.8,
                      "treated": R.random() < 0.72,
                      "coverage": R.choices(["policy", "policy", "none"], [60, 25, 15])[0]},
            "handled_at": None})

    # -- the demo set -------------------------------------------------------
    demo = [
        ("11:40pm, qualifies", 23, {"case_type": "auto", "state": "NC",
                                    "incident_date": iso(t0 - timedelta(days=2)),
                                    "liability_facts": True, "treated": True, "coverage": "policy"},
         "I was rear-ended at a light last night"),
        ("legal question", 9, {"case_type": "auto", "state": "NC",
                               "incident_date": iso(t0 - timedelta(days=10)),
                               "liability_facts": True, "treated": True, "coverage": "policy"},
         "do I have a case? and what's my case worth"),
        ("no incident date", 14, {"case_type": "premises", "state": "NC",
                                  "incident_date": None, "liability_facts": True,
                                  "treated": True, "coverage": "policy"},
         "I slipped at a store, I don't remember exactly when"),
        ("out of state", 16, {"case_type": "auto", "state": "VA",
                              "incident_date": iso(t0 - timedelta(days=20)),
                              "liability_facts": True, "treated": True, "coverage": "policy"},
         "car accident in Virginia"),
    ]
    # Names outside the generated pools on purpose: the conflict check is real,
    # and a demo lead whose name collides with a random opposing party gets
    # stopped before the walkthrough starts (it did).
    DEMO_NAMES = ["Bexley Ashgrove", "Corwin Vandermolen", "Lucienne Fairweather",
                  "Thaddeus Okonjo-Brill"]
    for k, (tag, hour, facts, msg) in enumerate(demo):
        leads.append({"id": f"ld_demo_{k+1}", "at": iso(t0.replace(hour=hour) - timedelta(days=1)),
                      "name": DEMO_NAMES[k], "opposing": "Unknown Driver",
                      "after_hours": hour < 8 or hour >= 18, "message": msg,
                      "facts": facts, "handled_at": None, "demo_tag": tag})
    # a conflict lead: opposing party IS one of our clients
    leads.append({"id": "ld_demo_conflict", "at": iso(t0 - timedelta(hours=4)),
                  "name": "Walton Pryce", "opposing": clients[0]["name"],
                  "after_hours": False, "message": "I want to sue over a car accident",
                  "facts": {"case_type": "auto", "state": "NC",
                            "incident_date": iso(t0 - timedelta(days=6)),
                            "liability_facts": True, "treated": True, "coverage": "policy"},
                  "handled_at": None, "demo_tag": "conflict"})

    store.save("clients", clients)
    store.save("matters", matters)
    store.save("records", records)
    store.save("productions", productions)
    store.save("contacts", contacts)
    store.save("leads", leads)
    store.save("approvals", [])
    store.save("events", [])
    return {"matters": len(matters), "records": len(records), "productions": len(productions),
            "leads": len(leads), "contacts": len(contacts)}


def parse_shift(iso_str, days):
    from _kit.store import parse
    d = parse(iso_str)
    return d + timedelta(days=days) if d else now()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--matters", type=int, default=310)
    ap.add_argument("--months", type=int, default=24)
    a = ap.parse_args()
    print(build(a.matters, a.months))
