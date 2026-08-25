#!/usr/bin/env python3
"""Redeploy OS — synthetic agency generator.

A 19-person light-industrial and skilled-trades staffing agency. Invented
candidate, client and certification-body names, 555 numbers, no real résumés.
Built so a staffing owner recognizes their own desk: a database mostly full of
stale records, assignments ending across the next 60 days, credentials at every
expiry distance, and a submission history rich enough to measure time-to-submit.

Candidate records carry a `display_name` for the UI. The RANKER never sees it —
`core._permitted()` strips everything that is not a permitted factor.

  python3 seed.py --candidates 11000 --months 24
"""
import argparse, random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

R = random.Random(20260816)

FIRST = ["Marcus", "Latoya", "Dmitri", "Aracely", "Beau", "Chandra", "Eli", "Fatima", "Gus",
         "Hana", "Isaiah", "Jolene", "Kwame", "Lucia", "Miguel", "Nadia", "Omar", "Pilar",
         "Quinton", "Rosa", "Sami", "Tanya", "Ulises", "Vera", "Wendell", "Xiomara", "Yosef"]
LAST = ["Abbott", "Braswell", "Cardenas", "Delgado", "Emory", "Fontenot", "Guzman", "Hollis",
        "Ivey", "Jacobs", "Kearns", "Lozano", "Mireles", "Navarro", "Oyelaran", "Pham",
        "Quintanilla", "Ruiz", "Sandoval", "Tran"]
CLIENTS = [("Ridgeline Manufacturing", "cl_1"), ("Cobalt Cold Storage", "cl_2"),
           ("Delta Ironworks", "cl_3"), ("Everline Packaging", "cl_4"),
           ("Foxwood Distribution", "cl_5"), ("Granite Precision", "cl_6")]
GEOS = ["north", "central", "south", "west"]


def build(n_candidates, months, reset=True):
    if reset:
        store.wipe()
    t0 = now()

    store.save("config", {
        "agency": "Ironline Staffing",
        "people": 19, "revenue": "$14M",
        "permitted_factors": list(core.PERMITTED_FACTORS),
        "excluded_factors": list(core.EXCLUDED_FACTORS),
        "brand": {"name": "Ironline Staffing", "color": "#1a3c5e",
                  "footer": "Candidate contact is available through Ironline Staffing."},
        "seeded_at": iso(),
        "roi_inputs": {"redeploy_points_gained": 0.15, "avg_duration_weeks": 14,
                       "database_fill_rate": 0.4, "sourcing_cost_per_req": 420,
                       "lapses_per_year": 18, "cost_per_lapse": 1600},
    })
    store.save("clients", [{"id": cid, "name": n} for n, cid in CLIENTS])

    candidates, credentials, assignments, reqs, submissions = [], [], [], [], []

    for i in range(n_candidates):
        reachable = R.random() < 0.19          # most of a staffing database is stale
        skills = R.sample(core.SKILLS, R.randint(1, 4))
        geo_times = {g: R.choice([8, 14, 22, 30, 38, 55, 80]) for g in GEOS}
        c = {
            "id": f"cd_{i+1}",
            # display_name is for humans only — the ranker never sees it
            "display_name": f"{R.choice(FIRST)} {R.choice(LAST)}",
            "skills": skills,
            "verified_experience_months": R.choice([None, 4, 11, 20, 36, 72, 120]),
            "geo": R.choice(GEOS), "commute_minutes": geo_times,
            "pay_rate_history": [round(R.uniform(16, 34), 2) for _ in range(R.randint(1, 4))],
            "availability": R.choices(["available", "on_assignment", "unreachable", "ending_soon"],
                                      [22, 30, 40, 8])[0] if reachable else "unreachable",
            "prior_client_ids": R.sample([c for _, c in CLIENTS], R.randint(0, 3)),
            "performance_notes": [{"rating": R.randint(2, 5)} for _ in range(R.randint(0, 3))],
            "short_notice_history": R.choice([None, 0, 1, 2, 3, 4, 5]),
            "assignment_history_count": R.randint(0, 9),
            "last_worked_at": iso(t0 - timedelta(days=R.randint(5, 1200))),
        }
        candidates.append(c)

        for ct in R.sample(list(core.CREDENTIALS), R.randint(0, 3)):
            spec = core.CREDENTIALS[ct]
            # a slice have no issue date on purpose — expiry is then unknowable
            issued = (None if R.random() < 0.08 else
                      iso(t0 - timedelta(days=R.randint(10, spec["valid_days"] + 200))))
            credentials.append({"id": f"cr_{len(credentials)+1}", "candidate_id": c["id"],
                                "type": ct, "issued_at": issued})

    # -- assignments --------------------------------------------------------
    active_pool = [c for c in candidates if c["availability"] in ("on_assignment", "ending_soon")]
    for i, c in enumerate(active_pool[:340]):
        client, cid = R.choice(CLIENTS)
        start = t0 - timedelta(days=R.randint(10, 200))
        ends = start + timedelta(days=R.choice([30, 60, 90, 120, 180]))
        assignments.append({"id": f"as_{i+1}", "candidate_id": c["id"], "client": client,
                            "client_id": cid, "starts_at": iso(start), "ends_at": iso(ends),
                            "state": "active" if ends > t0 else "ended",
                            "gm_per_week": round(R.uniform(180, 460), 2)})
    # historical, ended assignments so the redeploy rate is countable
    for i in range(400):
        c = R.choice(candidates)
        client, cid = R.choice(CLIENTS)
        start = t0 - timedelta(days=R.randint(200, 600))
        ends = start + timedelta(days=R.choice([30, 60, 90]))
        assignments.append({"id": f"as_h_{i+1}", "candidate_id": c["id"], "client": client,
                            "client_id": cid, "starts_at": iso(start), "ends_at": iso(ends),
                            "state": "ended", "gm_per_week": round(R.uniform(180, 460), 2)})
        if R.random() < 0.33:                  # a real redeployment
            s2 = ends + timedelta(days=R.randint(1, 25))
            assignments.append({"id": f"as_r_{i+1}", "candidate_id": c["id"], "client": client,
                                "client_id": cid, "starts_at": iso(s2),
                                "ends_at": iso(s2 + timedelta(days=90)),
                                "state": "ended", "gm_per_week": round(R.uniform(180, 460), 2)})

    # -- reqs + submissions -------------------------------------------------
    for i in range(140):
        client, cid = R.choice(CLIENTS)
        opened = t0 - timedelta(days=R.randint(0, months * 30), hours=R.randint(0, 20))
        r = {"id": f"rq_{i+1}", "client": client, "client_id": cid,
             "skills": R.sample(core.SKILLS, R.randint(1, 2)), "geo": R.choice(GEOS),
             "pay_rate": round(R.uniform(17, 32), 2), "opened_at": iso(opened),
             "client_requirements": R.sample(["background", "drug_screen"], R.randint(0, 2)),
             "state": "open" if R.random() < 0.32 else "filled"}
        reqs.append(r)
        for _ in range(R.randint(0, 3)):
            c = R.choice(candidates)
            submissions.append({"id": f"sb_{len(submissions)+1}", "req_id": r["id"],
                                "candidate_id": c["id"], "state": "submitted",
                                "screened_at": iso(opened + timedelta(hours=R.randint(1, 40))),
                                "submitted_at": iso(opened + timedelta(
                                    hours=R.choice([3, 8, 16, 30, 55, 96])))})

    # -- the demo set -------------------------------------------------------
    demo_req = {"id": "rq_demo", "client": "Ridgeline Manufacturing", "client_id": "cl_1",
                "skills": ["forklift"], "geo": "north", "pay_rate": 21.5,
                "opened_at": iso(t0 - timedelta(hours=1)),
                "client_requirements": ["background"], "state": "open",
                "demo_tag": "4:50pm req"}
    reqs.append(demo_req)
    # a req the database genuinely cannot fill — the gap statement
    gap_req = {"id": "rq_gap", "client": "Granite Precision", "client_id": "cl_6",
               "skills": ["cnc_setup", "welding_tig", "quality_inspect", "maintenance"],
               "must_have": ["cnc_setup", "welding_tig", "quality_inspect", "maintenance"],
               "geo": "west", "pay_rate": 31.0,
               "opened_at": iso(t0 - timedelta(hours=2)),
               "client_requirements": ["welding_cert", "background"], "state": "open",
               "demo_tag": "the honest gap"}
    reqs.append(gap_req)

    # a candidate with a full source résumé on file — the Present demo. The
    # source deliberately carries contact routes in the fields AND pasted into
    # the summary, so the demo shows the scrub actually working.
    present_cand = {
        "id": "cd_demo_present", "display_name": "Aracely Mireles",
        "skills": ["forklift", "pick_pack"], "verified_experience_months": 68,
        "geo": "north", "commute_minutes": {g: 18 for g in GEOS},
        "pay_rate_history": [22.5], "availability": "available",
        "prior_client_ids": ["cl_4"], "performance_notes": [{"rating": 5}],
        "short_notice_history": 4, "assignment_history_count": 6,
        "last_worked_at": iso(t0 - timedelta(days=12)),
        "demo_tag": "the present demo",
        "resume_source": {
            "summary": "Forklift operator, responsible for inbound at a 400k sq ft DC. "
                       "Call me at (555) 014-2299 or aracely.m@example.com.",
            "email": "aracely.m@example.com", "phone": "555-014-2299",
            "address": "48 Kildeer Rd", "linkedin": "linkedin.com/in/aracelym",
            "employment": [
                {"employer": "Foxwood Distribution", "title": "Forklift Operator",
                 "start": "2024-02", "end": None},
                {"employer": "Everline Packaging", "title": "responsible for pick/pack line",
                 "start": "2021-03", "end": "2024-01"},
            ],
            "skills": ["forklift", "pick_pack"],
            "certifications": ["Forklift certification"],
            "education": ["Crestview High School"],
        },
    }
    candidates.append(present_cand)
    credentials.append({"id": f"cr_{len(credentials)+1}", "candidate_id": "cd_demo_present",
                        "type": "forklift_cert", "issued_at": iso(t0 - timedelta(days=90))})
    submissions.append({"id": "sb_demo_present", "req_id": "rq_demo",
                        "candidate_id": "cd_demo_present", "state": "screened",
                        "screened_at": iso(t0 - timedelta(minutes=30)),
                        "demo_tag": "the present demo"})

    store.save("candidates", candidates)
    store.save("credentials", credentials)
    store.save("assignments", assignments)
    store.save("reqs", reqs)
    store.save("submissions", submissions)
    store.save("approvals", [])
    store.save("events", [])
    return {"candidates": len(candidates), "credentials": len(credentials),
            "assignments": len(assignments), "reqs": len(reqs), "submissions": len(submissions)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", type=int, default=11000)
    ap.add_argument("--months", type=int, default=24)
    a = ap.parse_args()
    print(build(a.candidates, a.months))
