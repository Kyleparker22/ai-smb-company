#!/usr/bin/env python3
"""Renewal OS — synthetic agency generator.

An 11-person independent agency. Invented carrier names, 555 numbers, no real
people. Built so a principal recognizes their own book: effective dates spread
across the year, renewals coming back at every delta including one at +23%, a
pile of mono-line households, routine certificates and the ones that are not.

  python3 seed.py --policies 4200 --months 24
"""
import argparse, random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

R = random.Random(20260816)

FIRST = ["Arthur", "Bernice", "Clay", "Dolores", "Emmett", "Fran", "Gus", "Harriet", "Ike",
         "Josephine", "Karl", "Lucinda", "Mort", "Nadine", "Oscar", "Petra", "Roland", "Sylvia",
         "Travis", "Ursula", "Vernon", "Wanda", "Yusuf", "Zora", "Priya", "Diego"]
LAST = ["Abernathy", "Bellweather", "Crowder", "Dunmore", "Ellsworth", "Fairchild", "Grimes",
        "Hollinger", "Ironside", "Jessup", "Kilgore", "Lindqvist", "Marchetti", "Nordstrom",
        "Ollivander", "Pennington", "Quarles", "Radcliffe", "Sutherland", "Tolliver"]
BIZ = ["Ridgeline Millwork", "Cobalt Freight", "Harbour Dental Group", "Ninth Street Bakery",
       "Vantage Roofing", "Pinegrove Landscaping", "Ardent Electric", "Solstice Fitness",
       "Beacon Property Services", "Trailhead Outfitters", "Kestrel Machining", "Union Tap House"]

PRODUCERS = ["Marguerite Ospina", "Dell Hartigan", "Rosalie Kwan", "Bo Fenwick"]
CARRIERS = ["Ironvale Mutual", "Cascade Standard", "Pemberton Casualty", "Northlight Insurance",
            "Argent Reciprocal", "Sable Ridge", "Halcyon National", "Twin Rivers Group"]

COVERAGE = {
    "auto": lambda: {"bi_limit": R.choice(["100/300", "250/500", "500/500"]),
                     "comp_deductible": R.choice([250, 500, 1000]),
                     "um": R.choice(["100/300", "250/500"])},
    "home": lambda: {"dwelling": R.choice([280000, 340000, 420000, 610000]),
                     "deductible": R.choice([1000, 2500, 5000]),
                     "water_backup": R.choice([True, False]),
                     "roof_settlement": R.choice(["replacement", "acv"])},
    "umbrella": lambda: {"limit": R.choice([1000000, 2000000])},
    "bop": lambda: {"gl_agg": R.choice([2000000, 3000000]), "bpp": R.choice([50000, 150000, 400000])},
    "gl": lambda: {"occurrence": 1000000, "aggregate": R.choice([2000000, 3000000])},
    "wc": lambda: {"el_limit": R.choice(["500/500/500", "1000/1000/1000"]),
                   "payroll": R.choice([240000, 480000, 1250000])},
    "comm_auto": lambda: {"csl": R.choice([500000, 1000000]), "units": R.randint(2, 14)},
    "cyber": lambda: {"limit": R.choice([250000, 500000, 1000000])},
}

CERT_LANGUAGE = ["", "", "", "same as last year", "copy of current GL cert please",
                 "evidence of coverage for the landlord",
                 "Additional insured per written contract",
                 "waiver of subrogation in favor of the owner",
                 "primary and non-contributory required",
                 "30 days written notice of cancellation",
                 "per project aggregate required"]


def build(n_pol, months, reset=True):
    if reset:
        store.wipe()
    t0 = now()

    store.save("config", {
        "agency": "Hollinger & Kwan Insurance",
        "people": 11, "producers": PRODUCERS, "carriers": CARRIERS,
        "seeded_at": iso(),
        "roi_inputs": {"retention_points_gained": 0.03, "save_rate": 0.35,
                       "contact_rate": 0.5, "bind_rate": 0.25, "added_commission": 210,
                       "persistency_years": 4, "certs_wk": 42, "minutes_each": 9,
                       "loaded_rate": 29},
    })
    store.save("producers", [{"id": f"pr_{i+1}", "name": n} for i, n in enumerate(PRODUCERS)])
    store.save("carriers", [{"id": f"ca_{i+1}", "name": n} for i, n in enumerate(CARRIERS)])

    households, policies, renewals, certs, claims = [], [], [], [], []
    n_hh = max(200, n_pol * 2 // 3)
    for i in range(n_hh):
        commercial = R.random() < 0.28
        name = R.choice(BIZ) if commercial else f"{R.choice(FIRST)} {R.choice(LAST)}"
        households.append({
            "id": f"hh_{i+1}", "name": name, "commercial": commercial,
            "phone": f"555-04{R.randint(10,99)}",
            "years_with_agency": R.randint(1, 18),
            "policy_age_days": R.choice([None, 90, 300, 700, 1500, 2900]),
            "prior_quote_declined": R.random() < 0.18,
            "life_event_recorded": R.choice([None, None, None, "new home", "teen driver",
                                             "new vehicle", "business expansion"]),
            "claim_free_years": R.choice([None, 0, 1, 3, 5, 9]),
        })

    for i in range(n_pol):
        hh = R.choice(households)
        pool = [k for k, v in core.LINES.items() if v["personal"] != hh["commercial"]]
        line = R.choice(pool)
        prem = round(R.uniform(*core.LINES[line]["premium"]), 2)
        eff = t0 - timedelta(days=R.randint(0, 365))
        exp = eff + timedelta(days=365)
        p = {"id": f"pol_{i+1}", "household_id": hh["id"], "line": line, "premium": prem,
             "effective": iso(eff), "expires": iso(exp), "active": R.random() < 0.93,
             "carrier": R.choice(CARRIERS), "producer": R.choice(PRODUCERS),
             "coverage": COVERAGE[line]()}
        policies.append(p)

        # Renewal history — outcomes for the retention read. back=0 is the
        # renewal that started THIS term, which is what puts completed renewals
        # inside the trailing-12-month window the retention read looks at.
        for back in (0, 1):
            when = eff - timedelta(days=365 * back)
            renewals.append({"id": f"rn_{len(renewals)+1}", "policy_id": p["id"],
                             "effective": iso(when), "premium": round(prem * R.uniform(0.9, 1.2), 2),
                             "carrier": p["carrier"], "producer": p["producer"],
                             "outcome": R.choices(["retained", "lost"], [0.88, 0.12])[0],
                             "triaged_at": iso(when), "coverage": p["coverage"]})

        # an upcoming renewal for a slice of the book
        if R.random() < 0.3:
            delta = R.choices([R.uniform(-0.05, 0.04), R.uniform(0.05, 0.09),
                               R.uniform(0.10, 0.19), R.uniform(0.20, 0.35)],
                              [40, 25, 22, 13])[0]
            cov = dict(p["coverage"])
            if R.random() < 0.15:                     # a quiet coverage change
                k = R.choice(list(cov))
                cov[k] = R.choice([1000, 2500, 5000]) if isinstance(cov[k], int) else cov[k]
            renewals.append({
                "id": f"rn_{len(renewals)+1}", "policy_id": p["id"],
                "effective": iso(t0 + timedelta(days=R.randint(3, 88))),
                "premium": round(prem * (1 + delta), 2), "carrier": p["carrier"],
                "producer": p["producer"], "coverage": cov,
                "carrier_reason": R.choice([None, "rate_action", "rate_action", "exposure",
                                            "credit_loss", "claim_driven"]),
                "outcome": None, "triaged_at": None})

        if R.random() < 0.09:
            claims.append({"id": f"cl_{len(claims)+1}", "policy_id": p["id"],
                           "household_id": hh["id"], "producer": p["producer"],
                           "date": iso(t0 - timedelta(days=R.randint(5, 400))),
                           "type": R.choice(["water", "collision", "theft", "wind", "liability"]),
                           "paid": round(R.uniform(800, 42000), 2),
                           "state": R.choices(["open", "closed"], [0.3, 0.7])[0]})

    # certificates
    for i in range(240):
        hh = R.choice([h for h in households if h["commercial"]])
        requested = R.choice(CERT_LANGUAGE)
        issued = R.random() < 0.75
        req_at = t0 - timedelta(days=R.randint(0, 80), hours=R.randint(0, 20))
        certs.append({"id": f"coi_{i+1}", "household_id": hh["id"], "holder": R.choice(BIZ),
                      "requested_language": requested,
                      "prior_certificate": R.choice([None, f"coi_prior_{R.randint(1,90)}",
                                                     f"coi_prior_{R.randint(1,90)}"]),
                      "requested_at": iso(req_at),
                      "issued_at": iso(req_at + timedelta(hours=R.choice([2, 5, 22, 48]))) if issued else None})

    # -- the demo set -----------------------------------------------------
    demo_hh = households[0]
    demo_pol = {"id": "pol_demo", "household_id": demo_hh["id"], "line": "home", "premium": 2180.0,
                "effective": iso(t0 - timedelta(days=340)), "expires": iso(t0 + timedelta(days=25)),
                "active": True, "carrier": "Ironvale Mutual", "producer": "Marguerite Ospina",
                "coverage": {"dwelling": 420000, "deductible": 2500, "water_backup": True,
                             "roof_settlement": "replacement"}}
    policies.append(demo_pol)
    renewals.append({"id": "rn_demo", "policy_id": "pol_demo",
                     "effective": iso(t0 + timedelta(days=25)), "premium": 2681.4,
                     "carrier": "Ironvale Mutual", "producer": "Marguerite Ospina",
                     "carrier_reason": "rate_action",
                     "coverage": {"dwelling": 420000, "deductible": 5000, "water_backup": False,
                                  "roof_settlement": "acv"},
                     "outcome": None, "triaged_at": None, "demo_tag": "+23% and coverage moved"})
    certs.append({"id": "coi_demo_std", "household_id": households[1]["id"], "holder": "Vantage Roofing",
                  "requested_language": "same as last year", "prior_certificate": "coi_prior_7",
                  "requested_at": iso(t0 - timedelta(hours=3)), "issued_at": None,
                  "demo_tag": "routine"})
    certs.append({"id": "coi_demo_ai", "household_id": households[2]["id"], "holder": "Cobalt Freight",
                  "requested_language": "Additional insured per written contract, primary and non-contributory",
                  "prior_certificate": "coi_prior_9",
                  "requested_at": iso(t0 - timedelta(hours=2)), "issued_at": None,
                  "demo_tag": "non-standard"})

    store.save("households", households)
    store.save("policies", policies)
    store.save("renewals", renewals)
    store.save("certificates", certs)
    store.save("claims", claims)
    store.save("approvals", [])
    store.save("events", [])
    return {"households": len(households), "policies": len(policies), "renewals": len(renewals),
            "certificates": len(certs), "claims": len(claims)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--policies", type=int, default=4200)
    ap.add_argument("--months", type=int, default=24)
    a = ap.parse_args()
    print(build(a.policies, a.months))
