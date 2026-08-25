#!/usr/bin/env python3
"""Close OS — synthetic firm generator.

A 14-person CPA firm running both rhythms: the monthly close book and the
ten-week season spike. Invented client names, fake obviously-fake EINs, 555
numbers. Built so a managing partner recognizes their own March — open items at
every age, clients with wildly different responsiveness, documents arriving
misnamed and mis-yeared, and out-of-scope requests buried in ordinary email.

  python3 seed.py --clients 230 --months 18
"""
import argparse, random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

R = random.Random(20260816)

BIZ = ["Alder & Finch", "Brightwater Dental", "Cinder Ridge Farms", "Delta Ironworks",
       "Everly Design Co", "Foxglove Catering", "Granite Peak Rentals", "Harborview Marine",
       "Ivory Lane Salon", "Juniper Software", "Kestrel Logistics", "Lakeshore Roofing",
       "Marrow Coffee", "Northgate Auto", "Oakfield Vet", "Perch Media", "Quarry Stoneworks",
       "Ridgeback Fitness", "Silverbell Florists", "Timberline Homes"]
PEOPLE = ["Aaron Selby", "Bettina Cross", "Cyrus Whitlow", "Delia Marsh", "Eamon Trask",
          "Fiona Delacroix", "Gideon Park", "Halle Norquist", "Ivan Petrov", "Jenna Ruiz",
          "Kwame Osei", "Liora Bench", "Marcus Vale", "Nadia Ferro", "Owen Blackwood"]
PARTNERS = ["Ruth Callender, CPA", "Desmond Iyer, CPA", "Priya Raghavan, CPA"]
STAFF = ["Tom Bexley", "Junie Alvarado", "Rafe Okonkwo", "Simone Dutta", "Casey Lindgren", "Ada Vo"]

MESSY_FILENAMES = [
    "IMG_4471.jpg", "scan.pdf", "Scan 2026-03-02 10.14.pdf", "doc1.pdf",
    "bank stmt.pdf", "statement (3).pdf", "photo of statement.HEIC",
]

CLIENT_MESSAGES = [
    "Quick one — can I deduct the truck I bought in November?",
    "We just formed a new LLC for the rental, can you add it in?",
    "We started selling into Ohio this quarter, do we need to register there?",
    "Can you go back and amend 2023? I think we missed something.",
    "The books are a mess since our bookkeeper left, can you catch us up?",
    "We got a letter from the IRS, not sure what it is.",
    "Should I elect S-corp for next year?",
    "Sold the building in June — there was a 1031 involved.",
    "Sending the statements now, sorry for the delay.",
    "Payroll is in a new state starting next month.",
    "All good on my end, thanks!",
]

LETTER_CLAUSES = [
    dict(text="Preparation of the annual federal and state income tax returns for the entities "
              "listed in Appendix A.", applies_to=[], covers=True),
    dict(text="Monthly bookkeeping and close for the operating entity only. Additional entities "
              "are billed separately at our standard rates.", applies_to=["new entity"], covers=False),
    dict(text="State registrations, nexus studies and multi-state filings are not included in "
              "this engagement.", applies_to=["new state registration", "multi-state payroll"], covers=False),
    dict(text="Prior-year amendments are outside this engagement and are quoted separately.",
         applies_to=["prior-year amendment"], covers=False),
    # deliberately two-sided — the system must refuse to resolve it
    dict(text="Routine questions arising from the work described above are included. Planning and "
              "advisory engagements are separate.", applies_to=["advisory question"], covers="ambiguous"),
    dict(text="Catch-up bookkeeping for periods prior to the engagement start date is billed "
              "hourly.", applies_to=["bookkeeping cleanup"], covers=False),
    dict(text="Representation before taxing authorities, including notice responses, is a separate "
              "engagement.", applies_to=["notice response"], covers=False),
    dict(text="Transaction advisory, including like-kind exchanges, is not included.",
         applies_to=["transaction work"], covers=False),
]


def build(n_clients, months, reset=True):
    if reset:
        store.wipe()
    t0 = now()

    store.save("config", {
        "firm": "Callender Iyer Raghavan",
        "people": 14, "partners": PARTNERS, "staff": STAFF,
        "seeded_at": iso(),
        "roi_inputs": {"touches_each": 3, "minutes_per_touch": 6, "loaded_rate": 42,
                       "minutes_per_doc": 4, "blocker_days_removed": 5,
                       "daily_wip_value": 38, "capture_rate": 0.6, "avg_scope_value": 1250},
    })
    store.save("staff", [{"id": f"p_{i+1}", "name": n, "role": "partner"} for i, n in enumerate(PARTNERS)]
               + [{"id": f"s_{i+1}", "name": n, "role": "staff"} for i, n in enumerate(STAFF)])

    clients, engagements, open_items, documents = [], [], [], []
    for i in range(n_clients):
        biz = R.random() < 0.55
        name = (f"{R.choice(BIZ)}" if biz else R.choice(PEOPLE))
        clients.append({
            "id": f"cl_{i+1}", "name": name, "business": biz,
            "contact": R.choice(PEOPLE), "email": f"contact{i+1}@example.invalid",
            "ein": f"00-{R.randint(1000000,9999999)}" if biz else None,
            "responsiveness": R.choice([0.1, 0.25, 0.4, 0.6, 0.85, 0.95]),
            "channel": R.choice(["email", "email", "sms", "portal"]),
            "engagement_letter": {"signed": iso(t0 - timedelta(days=R.randint(60, 400))),
                                  "clauses": LETTER_CLAUSES},
        })

    for c in clients:
        types = (["monthly_close"] if R.random() < 0.32 else []) + \
                ([R.choice(["1040", "1120s", "1065"])]) + \
                (["payroll"] if c["business"] and R.random() < 0.25 else []) + \
                (["audit_prep"] if R.random() < 0.05 else [])
        for t in types:
            spec = core.ENGAGEMENT_TYPES[t]
            due = t0 + timedelta(days=R.choice([-14, -3, 2, 5, 9, 16, 30, 55]))
            eng = {"id": f"en_{len(engagements)+1}", "client_id": c["id"], "type": t,
                   "entity": c["name"], "period_year": 2025,
                   "due": iso(due), "owner": R.choice(PARTNERS),
                   "fee": spec["fee"], "state": "not_started", "blocker": None,
                   "blocker_since": None}
            # give it a live state with a NAMED blocker (advance() would refuse otherwise)
            state = R.choices(["waiting_on_client", "waiting_on_third_party", "waiting_on_us",
                               "in_review", "complete"], [46, 12, 20, 12, 10])[0]
            if state == "complete":
                eng["state"] = "complete"
            else:
                core.advance(eng, state, core.BLOCKING_STATES[state])
                eng["blocker_since"] = iso(t0 - timedelta(days=R.choice([1, 3, 6, 11, 19, 27, 44])))
            engagements.append(eng)

            if eng["state"] == "complete":
                continue
            n_items = R.randint(2, 11)
            pool = ["bank_statement", "cc_statement", "payroll_report", "k1", "1099", "w2",
                    "receipts", "mileage_log", "question_answer", "loan_statement"]
            for k in range(n_items):
                it = R.choice(pool)
                received = R.random() < c["responsiveness"] * 0.7
                open_items.append({
                    "id": f"it_{len(open_items)+1}", "engagement_id": eng["id"], "type": it,
                    "period_month": R.randint(1, 12) if it in ("bank_statement", "cc_statement",
                                                               "payroll_report") else None,
                    "requested_at": iso(t0 - timedelta(days=R.choice([0, 2, 5, 9, 14, 19, 26, 38]))),
                    "state": "received" if received else "open",
                    "touches": []})
            # dependent items — the chaser must refuse to chase these early
            open_items.append({"id": f"it_{len(open_items)+1}", "engagement_id": eng["id"],
                               "type": "draft_return", "requested_at": iso(t0 - timedelta(days=10)),
                               "state": "open", "touches": []})
            open_items.append({"id": f"it_{len(open_items)+1}", "engagement_id": eng["id"],
                               "type": "signed_8879", "requested_at": iso(t0 - timedelta(days=8)),
                               "state": "open", "touches": []})

    # documents arriving — a third of them messy on purpose
    for i in range(int(n_clients * 6)):
        eng = R.choice(engagements)
        if R.random() < 0.34:
            fn = R.choice(MESSY_FILENAMES)
        else:
            kind = R.choice(["bank stmt", "credit card", "payroll", "K-1", "1099", "W-2"])
            yr = R.choices([2025, 2024], [88, 12])[0]          # a slice are the WRONG year
            mo = R.choice(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
                           "Oct", "Nov", "Dec"])
            fn = f"{eng['entity'].split()[0]} {yr} {mo} {kind}.pdf"
        documents.append({"id": f"dc_{i+1}", "engagement_id": eng["id"], "filename": fn,
                          "arrived_at": iso(t0 - timedelta(days=R.randint(0, 40))),
                          "entity_hint": (R.choice([None, None, eng["entity"], "Beta Holdings"])
                                          if R.random() < 0.3 else None)})

    # -- the demo set -----------------------------------------------------
    demo_client = clients[0]
    demo_eng = {"id": "en_demo", "client_id": demo_client["id"], "type": "1120s",
                "entity": demo_client["name"], "period_year": 2025,
                "due": iso(t0 + timedelta(days=6)), "owner": PARTNERS[0], "fee": 2600,
                "state": "waiting_on_client", "blocker": "client",
                "blocker_since": iso(t0 - timedelta(days=19))}
    engagements.append(demo_eng)
    for k, it in enumerate(["bank_statement", "cc_statement", "k1", "1099", "receipts",
                            "mileage_log", "payroll_report", "loan_statement", "question_answer",
                            "draft_return", "signed_8879"]):
        open_items.append({"id": f"it_demo_{k+1}", "engagement_id": "en_demo", "type": it,
                           "period_month": 3 if it in ("bank_statement", "cc_statement") else None,
                           "requested_at": iso(t0 - timedelta(days=19)),
                           "state": "open", "touches": []})
    for fn, hint in [("Alder 2025 Mar bank stmt.pdf", None),
                     ("Alder 2024 Mar bank stmt.pdf", None),          # wrong year
                     ("IMG_4471.jpg", None),                          # unreadable
                     ("2025 Mar credit card.pdf", "Beta Holdings"),   # wrong entity
                     ("1099 2025.pdf", None)]:
        documents.append({"id": f"dc_demo_{len(documents)}", "engagement_id": "en_demo",
                          "filename": fn, "entity_hint": hint,
                          "arrived_at": iso(t0 - timedelta(hours=2)), "demo_tag": True})

    store.save("clients", clients)
    store.save("engagements", engagements)
    store.save("open_items", open_items)
    store.save("documents", documents)
    store.save("scope_events", [])
    store.save("approvals", [])
    store.save("events", [])
    return {"clients": len(clients), "engagements": len(engagements),
            "open_items": len(open_items), "documents": len(documents)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--clients", type=int, default=230)
    ap.add_argument("--months", type=int, default=18)
    a = ap.parse_args()
    print(build(a.clients, a.months))
