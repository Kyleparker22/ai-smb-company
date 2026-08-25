#!/usr/bin/env python3
"""Consult OS — synthetic practice generator.

A two-location med spa. Invented names, 555 numbers, no real people, no network
calls. Built so the week is recognizable: DMs at 9:40pm, no-shows, plans that
went quiet after "let me talk to my husband", and a long tail of patients whose
neurotoxin has quietly slipped past four months.

  python3 seed.py --inquiries 180 --months 12
"""
import argparse, random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

R = random.Random(20260816)

FIRST = ["Adrienne", "Bianca", "Camille", "Delaney", "Eve", "Farrah", "Giselle", "Harper",
         "Ivy", "Jolene", "Kendra", "Lourdes", "Maeve", "Noelle", "Odette", "Paloma",
         "Quinn", "Rosalind", "Simone", "Tamsin", "Ursula", "Vivienne", "Wren", "Xiomara",
         "Marcus", "Devin", "Julian", "Theo"]
LAST = ["Ashford", "Beaumont", "Calloway", "Delacroix", "Ellery", "Fairbanks", "Grimaldi",
        "Hawthorne", "Isley", "Jarreau", "Kingsley", "Lachlan", "Merriweather", "Nightingale",
        "Ovalle", "Prescott", "Rennick", "Sable", "Thorpe", "Vandermeer"]

PROVIDERS = [("Dr. Renata Vance", "injector"), ("Sloane Merritt, NP", "injector"),
             ("Adaeze Okoro, PA-C", "injector"), ("Kit Delarosa", "laser")]

COMMERCIAL_TEXTS = [
    "hi! how much is lip filler roughly?",
    "do you have anything thursday evening",
    "what time do you close on saturday",
    "can I book a consult for next week",
    "do you take care credit",
    "where exactly are you located",
    "is the consult fee credited toward treatment",
    "looking to do something about my forehead lines, what do you recommend booking",
    "interested in laser hair removal packages",
    "do you do hydrafacial memberships",
]
CLINICAL_TEXTS = [
    "how many units would I need for my forehead?",
    "is botox safe if I'm breastfeeding?",
    "I'm on eliquis, can I still get filler",
    "am I a good candidate for cheek filler?",
    "what are the side effects of dysport",
    "I have an autoimmune thing, is that a problem",
    "should I stop taking my medication before",
    "not sure if I can, I have a condition",
]
URGENT_TEXTS = [
    "my lip is going white and it really hurts",
    "my eyelid is drooping since Tuesday",
    "my vision is blurry on that side",
    "there's a hard lump and the swelling is spreading",
]

OBJECTIONS = ["price", "nervous", "spouse_partner", "timing", "wants_research"]
PLAN_SUMMARIES = {
    "neurotoxin": "glabella, frontalis and a light lateral canthal treatment, reassess at two weeks",
    "filler_lip": "structured lip with a soft product, one syringe now and reassess at four weeks",
    "filler_cheek": "midface support first, then reassess the nasolabial folds",
    "laser_resurf": "three-session resurfacing series with a pigment-safe protocol",
    "laser_hair": "six-session series, four weeks apart, underarms and lower legs",
    "microneedle": "three microneedling sessions a month apart with growth-factor serum",
    "body_contour": "two-cycle contouring package with a twelve-week reassessment",
}


def build(n_inq, months, reset=True):
    if reset:
        store.wipe()
    t0 = now()

    store.save("config", {
        "practice": "Verrine Aesthetics",
        "locations": ["Ellery Street", "Northgate"],
        "owner": {"name": "Dr. Renata Vance", "role": "Owner / Medical Director"},
        "providers": [p[0] for p in PROVIDERS],
        "consult_fee": core.CONSULT_FEE, "deposit": core.DEPOSIT,
        "seeded_at": iso(),
        # Ad spend is deliberately NOT connected for two of the paid channels, so
        # cost-per-booked-consult opens with an honest blank the owner can check
        # against their own ad account.
        "ad_spend": {"referral": 0, "web_form": 1850},
        "roi_inputs": {"incremental_book_rate": 0.18, "no_show_points_recovered": 0.06,
                       "incremental_close_rate": 0.14, "desk_hours_wk": 9, "loaded_rate": 27},
    })

    providers = [{"id": f"prov_{i+1}", "name": n, "kind": k} for i, (n, k) in enumerate(PROVIDERS)]
    store.save("providers", providers)

    patients, treatments = [], []
    for i in range(int(n_inq * 4)):
        name = f"{R.choice(FIRST)} {R.choice(LAST)}"
        p = {"id": f"pt_{i+1}", "name": name, "phone": f"555-02{R.randint(10,99)}",
             "since": iso(t0 - timedelta(days=R.randint(20, 1400))),
             "flexible": R.random() < 0.3, "distance_min": R.choice([8, 12, 18, 25, 35]),
             "channel": R.choice(core.CHANNELS)}
        patients.append(p)
        # treatment history — a third of patients deliberately have NONE, so the
        # cadence engine has to refuse to flag them
        if R.random() < 0.66:
            svc = R.choices(list(core.SERVICES), [30, 14, 8, 6, 9, 7, 4, 15, 7])[0]
            spec = core.SERVICES[svc]
            n_tx = R.randint(1, 5)
            last = t0 - timedelta(days=R.randint(20, 400))
            for k in range(n_tx):
                when = last - timedelta(days=(spec.get("interval_days") or 120) * (n_tx - k - 1))
                treatments.append({"id": f"tx_{len(treatments)+1}", "patient_id": p["id"],
                                   "service": svc, "at": iso(when),
                                   "amount": round(R.uniform(*spec["band"]), 2),
                                   "provider": R.choice(providers)["name"],
                                   "note": R.choice(["under-treated on purpose, reassess",
                                                     "great result, very happy",
                                                     "asked about doing the midface next time",
                                                     "wants to stay subtle"])})
    store.save("patients", patients)
    store.save("treatments", treatments)

    # -- inquiries, consults, plans ---------------------------------------
    inquiries, consults, plans = [], [], []
    total = int(n_inq * months)
    for i in range(total):
        age = R.randint(0, months * 30)
        hour = R.choices(range(7, 24), [2, 4, 6, 7, 7, 6, 6, 7, 8, 9, 10, 11, 12, 11, 9, 6, 3])[0]
        when = (t0 - timedelta(days=age)).replace(hour=hour, minute=R.randint(0, 59))
        after = hour < 9 or hour >= 18
        roll = R.random()
        text = (R.choice(URGENT_TEXTS) if roll < 0.02 else
                R.choice(CLINICAL_TEXTS) if roll < 0.32 else
                R.choice(COMMERCIAL_TEXTS))
        pt = R.choice(patients)
        inq = {"id": f"inq_{i+1}", "at": iso(when), "channel": R.choice(core.CHANNELS),
               "text": text, "patient_id": pt["id"], "patient_name": pt["name"],
               "after_hours": after, "first_response_at": None}
        # history: most older inquiries were answered, slowly, by a human
        if age > 2:
            lag = R.choice([9, 14, 22, 40, 90, 240, 800]) if after else R.choice([4, 8, 15, 35, 90])
            inq["first_response_at"] = iso(when + timedelta(minutes=lag))
            inq["read_tier"] = "commercial" if text in COMMERCIAL_TEXTS else "clinical"
            if text in COMMERCIAL_TEXTS and R.random() < 0.42:
                svc = R.choices(list(PLAN_SUMMARIES), [30, 16, 10, 8, 10, 9, 4])[0]
                spec = core.SERVICES[svc]
                start = when + timedelta(days=R.randint(2, 12))
                state = R.choices(["showed", "no_show", "cancelled"], [0.72, 0.19, 0.09])[0]
                c = {"id": f"con_{len(consults)+1}", "patient_id": pt["id"], "patient_name": pt["name"],
                     "service": svc, "starts_at": iso(start), "state": state,
                     "created_at": iso(when), "source_inquiry": inq["id"], "touches": [],
                     "consult_fee": core.CONSULT_FEE}
                inq["consult_id"] = c["id"]
                if state == "showed":
                    amount = round(R.uniform(*spec["band"]) * R.choice([1, 1, 2, 3]), 2)
                    pstate = R.choices(["treated", "declined", "presented"], [0.46, 0.24, 0.30])[0]
                    plan = {"id": f"plan_{len(plans)+1}", "patient_id": pt["id"],
                            "patient_name": pt["name"], "service": svc, "amount": amount,
                            "summary": PLAN_SUMMARIES[svc], "presented_at": iso(start),
                            "provider": R.choice([p["name"] for p in providers if p["kind"] == "injector"]),
                            "objection": R.choice(OBJECTIONS), "state": pstate, "touches": []}
                    if pstate in ("treated", "declined"):
                        plan["decided_at"] = iso(start + timedelta(days=R.randint(1, 20)))
                        if pstate == "declined":
                            plan["decline_reason"] = R.choice(core.DECLINE_REASONS)
                        else:
                            c["treated"] = True
                            c["rebooked"] = R.random() < 0.55
                    plans.append(plan)
                consults.append(c)
        inquiries.append(inq)

    # -- the live demo set, deterministic ---------------------------------
    demo = [
        ("9:40pm DM", 21, 40, "instagram_dm", "hi! how much is lip filler roughly?"),
        ("clinical", 22, 5, "instagram_dm", "how many units would I need for my forehead?"),
        ("urgent", 7, 15, "text", "my lip is going white and it really hurts"),
        ("no treatment named", 12, 30, "web_form", "hi, looking to book something, not sure what"),
        ("hedged", 19, 50, "tiktok_dm", "not sure if I can, I have a condition"),
    ]
    for k, (tag, hh, mm, ch, text) in enumerate(demo):
        pt = patients[k]
        inquiries.append({"id": f"inq_demo_{k+1}", "at": iso(t0.replace(hour=hh, minute=mm) - timedelta(days=1)),
                          "channel": ch, "text": text, "patient_id": pt["id"],
                          "patient_name": pt["name"], "after_hours": hh < 9 or hh >= 18,
                          "first_response_at": None, "demo_tag": tag})

    # an upcoming consult so the show-up ladder has something to work on
    pt = patients[7]
    consults.append({"id": "con_demo_1", "patient_id": pt["id"], "patient_name": pt["name"],
                     "service": "filler_cheek", "starts_at": iso(t0 + timedelta(days=1, hours=6)),
                     "state": "booked", "created_at": iso(t0 - timedelta(days=9)),
                     "touches": [], "consult_fee": core.CONSULT_FEE})
    # a flagship undecided plan
    plans.append({"id": "plan_demo_1", "patient_id": patients[9]["id"],
                  "patient_name": patients[9]["name"], "service": "laser_resurf", "amount": 4800.0,
                  "summary": PLAN_SUMMARIES["laser_resurf"],
                  "presented_at": iso(t0 - timedelta(days=11)), "provider": "Dr. Renata Vance",
                  "objection": "spouse_partner", "state": "presented", "touches": []})

    store.save("inquiries", inquiries)
    store.save("consults", consults)
    store.save("plans", plans)
    store.save("approvals", [])
    store.save("messages", [])
    store.save("events", [])
    return {"patients": len(patients), "treatments": len(treatments), "inquiries": len(inquiries),
            "consults": len(consults), "plans": len(plans)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--inquiries", type=int, default=180)
    ap.add_argument("--months", type=int, default=12)
    a = ap.parse_args()
    print(build(a.inquiries, a.months))
