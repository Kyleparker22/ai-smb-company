#!/usr/bin/env python3
"""Serve OS — synthetic Docket Process Service. Synthetic only: invented
names, 555 phones, invented courts and counties."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(57)

COUNTIES = ("Hardin", "Bellamy", "Ashford")
COURTS = {"Hardin": "Hardin County Circuit Court",
          "Bellamy": "Bellamy County District Court",
          "Ashford": "Ashford County Superior Court"}
SERVERS = [
    {"id": "srv_dre",   "name": "Dre Okonkwo",    "territory": ["Hardin"]},
    {"id": "srv_marta", "name": "Marta Villanueva", "territory": ["Hardin", "Bellamy"]},
    {"id": "srv_gil",   "name": "Gil Fenwick",    "territory": ["Bellamy"]},
    {"id": "srv_tasha", "name": "Tasha Broome",   "territory": ["Bellamy", "Ashford"]},
    {"id": "srv_ray",   "name": "Ray Delacourt",  "territory": ["Ashford"]},
    {"id": "srv_june",  "name": "June Okabe",     "territory": ["Ashford", "Hardin"]},
]
FIRMS = ["Calder & Voss LLP", "Petrakis Law", "Brumfield & Associates",
         "Ostrander Legal Group", "Yun & Whitaker PLLC"]
DEFENDANTS = ["R. Gutierrez", "M. Kessler", "T. Delgado", "S. Whitaker", "A. Marsh",
              "D. Okafor", "L. Trask", "P. Villanova", "K. Bostwick", "E. Renshaw",
              "J. Calloway", "N. Iglesias", "B. Thorne", "C. Havlik", "F. Mercado",
              "G. Pruitt"]
STREETS = ["Larkspur Ave", "Quarry Ridge Rd", "Millbrook Ln", "Cotter St", "Vance Blvd",
           "Old Post Rd", "Juniper Ct", "Harrow Dr"]
PAPERS = ["summons and complaint", "subpoena", "garnishment", "eviction notice",
          "citation", "small-claims summons"]
OUTCOMES = ["no answer", "no answer — car in the driveway", "bad address per current occupant",
            "refused to open the door", "spoke to a neighbor — defendant works days"]
BAND_HOURS = {"morning": 9, "afternoon": 14, "evening": 19}
MESSAGES = [
    "any update on the kessler serve",
    "what's the status of service on the delgado defendant",
    "has the records custodian been served yet",
    "new summons and complaint attached, please effect service",
    "subpoena for a witness, papers to follow this afternoon",
    "we need the affidavit of service for the friday filing",
    "can you expedite this one, the client wants it served asap",
    "question about last month's invoice",
]


def addr(county):
    return f"{rng.randint(12, 4899)} {rng.choice(STREETS)}, {county} County"


def att(sid, server, county, days_ago, band, outcome, late_h=0, who=None):
    at = (now() - timedelta(days=days_ago)).replace(hour=BAND_HOURS[band], minute=rng.randint(0, 59))
    return core.attempt_row(sid, server, outcome, addr(county),
                            attempted_at=iso(at),
                            recorded_at=iso(at + timedelta(hours=late_h, minutes=8)),
                            gps_ref=f"gps_{rng.randint(100000, 999999)}",
                            who_answered=who)


def main():
    store.wipe()
    store.save("config", {"company": "Docket Process Service", "counties": list(COUNTIES),
                          "phone": "(555) 013-4477",
                          "diligence_rules": core.DEFAULT_DILIGENCE_RULES})
    store.save("servers", [dict(s, status="active") for s in SERVERS])

    serves, attempts = [], []

    # ~300 open serves
    for i in range(300):
        county = rng.choice(COUNTIES)
        received = now() - timedelta(days=rng.randint(0, 28))
        s = {"id": f"sv_{i:03d}", "case_number": f"{rng.randint(24, 26)}-CV-{rng.randint(1000, 9899)}",
             "court": COURTS[county], "county": county,
             "defendant": rng.choice(DEFENDANTS), "address": addr(county),
             "firm": rng.choice(FIRMS), "papers": rng.choice(PAPERS),
             "fee": rng.choice([65, 85, 95, 120, 150]),
             "received_at": iso(received),
             "deadline": iso(received + timedelta(days=rng.randint(7, 40))),
             "status": "papers_in", "rush": rng.random() < 0.12}
        if rng.random() < 0.75:
            s["status"] = "attempting"
            s["assigned_to"] = rng.choice([x["id"] for x in SERVERS
                                           if county in x["territory"]])
            for k in range(rng.randint(1, 2)):
                attempts.append(att(s["id"], s["assigned_to"], county,
                                    rng.randint(0, 6), rng.choice(list(BAND_HOURS)),
                                    rng.choice(OUTCOMES)))
        serves.append(s)

    # history: 120 completed serves in the last 90 days
    for i in range(120):
        county = rng.choice(COUNTIES)
        received = now() - timedelta(days=rng.randint(10, 90))
        done = received + timedelta(days=rng.randint(2, 9))
        server = rng.choice([x["id"] for x in SERVERS if county in x["territory"]])
        status = rng.choices(["served", "substituted", "non_est"], [0.72, 0.18, 0.10])[0]
        s = {"id": f"sv_h{i:03d}", "case_number": f"{rng.randint(23, 26)}-CV-{rng.randint(1000, 9899)}",
             "court": COURTS[county], "county": county,
             "defendant": rng.choice(DEFENDANTS), "address": addr(county),
             "firm": rng.choice(FIRMS), "papers": rng.choice(PAPERS),
             "fee": rng.choice([65, 85, 95, 120, 150]),
             "received_at": iso(received), "deadline": iso(received + timedelta(days=30)),
             "status": status, "assigned_to": server,
             "completed_at": iso(done) if status != "non_est" else None,
             "rush": rng.random() < 0.15}
        days_ago = max(1, (now() - done).days)
        for k, band in enumerate(rng.sample(list(BAND_HOURS), rng.randint(1, 3))):
            attempts.append(att(s["id"], server, county, days_ago + k, band,
                                rng.choice(OUTCOMES)))
        if status == "served":
            attempts.append(att(s["id"], server, county, days_ago, "evening",
                                "served personally — identified and confirmed by name",
                                who="the defendant"))
        serves.append(s)

    # ---- demo fixtures (demo_tag) ------------------------------------
    # 2-of-3 attempts in Hardin (rule: 3 attempts / 2 bands) — substituted refused
    serves.append({"id": "sv_demo_two", "case_number": "26-CV-4410",
                   "court": COURTS["Hardin"], "county": "Hardin",
                   "defendant": "R. Gutierrez", "address": "1412 Larkspur Ave, Hardin County",
                   "firm": "Calder & Voss LLP", "papers": "summons and complaint", "fee": 95,
                   "received_at": iso(now() - timedelta(days=9)),
                   "deadline": iso(now() + timedelta(days=6)),
                   "status": "attempting", "assigned_to": "srv_dre", "demo_tag": "demo"})
    attempts.append(att("sv_demo_two", "srv_dre", "Hardin", 5, "morning", "no answer"))
    attempts.append(att("sv_demo_two", "srv_dre", "Hardin", 3, "evening",
                        "no answer — car in the driveway"))

    # the rule satisfied in Hardin — substituted allowed
    serves.append({"id": "sv_demo_diligent", "case_number": "26-CV-4477",
                   "court": COURTS["Hardin"], "county": "Hardin",
                   "defendant": "L. Trask", "address": "77 Old Post Rd, Hardin County",
                   "firm": "Petrakis Law", "papers": "eviction notice", "fee": 85,
                   "received_at": iso(now() - timedelta(days=12)),
                   "deadline": iso(now() + timedelta(days=9)),
                   "status": "attempting", "assigned_to": "srv_marta", "demo_tag": "demo"})
    for d, band in ((6, "morning"), (4, "afternoon"), (2, "evening")):
        attempts.append(att("sv_demo_diligent", "srv_marta", "Hardin", d, band, "no answer"))

    # a late-recorded attempt (recorded 3 days after the attempt) — labeled forever
    serves.append({"id": "sv_demo_late", "case_number": "26-CV-5102",
                   "court": COURTS["Bellamy"], "county": "Bellamy",
                   "defendant": "K. Bostwick", "address": "310 Cotter St, Bellamy County",
                   "firm": "Brumfield & Associates", "papers": "subpoena", "fee": 120,
                   "received_at": iso(now() - timedelta(days=8)),
                   "deadline": iso(now() + timedelta(days=12)),
                   "status": "attempting", "assigned_to": "srv_gil", "demo_tag": "demo"})
    attempts.append(att("sv_demo_late", "srv_gil", "Bellamy", 4, "morning",
                        "no answer", late_h=72))

    # affidavit-ready: served on the second attempt
    serves.append({"id": "sv_demo_affidavit", "case_number": "26-CV-3388",
                   "court": COURTS["Ashford"], "county": "Ashford",
                   "defendant": "S. Whitaker", "address": "88 Quarry Ridge Rd, Ashford County",
                   "firm": "Yun & Whitaker PLLC", "papers": "summons and complaint", "fee": 95,
                   "received_at": iso(now() - timedelta(days=7)),
                   "deadline": iso(now() + timedelta(days=14)),
                   "status": "served", "assigned_to": "srv_ray",
                   "completed_at": iso(now() - timedelta(days=1)), "demo_tag": "demo"})
    attempts.append(att("sv_demo_affidavit", "srv_ray", "Ashford", 3, "morning", "no answer"))
    attempts.append(att("sv_demo_affidavit", "srv_ray", "Ashford", 1, "evening",
                        "served personally — identified and confirmed by name",
                        who="the defendant"))

    store.save("serves", serves)
    store.save("attempts", attempts)

    open_ids = [s["id"] for s in serves if s["status"] in ("papers_in", "attempting")
                and not s.get("demo_tag")]
    messages = []
    for i, t in enumerate(MESSAGES * 2):
        m = {"id": f"ms_{i:03d}", "from": rng.choice(["Dana", "Priya", "Cole", "Renata"]),
             "firm": rng.choice(FIRMS), "text": t,
             "at": iso(now() - timedelta(hours=rng.randint(1, 72)))}
        if "update" in t or "status" in t or "served yet" in t or "affidavit" in t \
           or "expedite" in t:
            m["serve_id"] = rng.choice(open_ids)
        messages.append(m)
    # the deadline-risk message, matched to the 2-of-3 demo serve
    messages.append({"id": "ms_demo_deadline", "from": "Dana Calder",
                     "firm": "Calder & Voss LLP",
                     "text": "the answer is due monday and he still isn't served — "
                             "where do we stand on gutierrez",
                     "serve_id": "sv_demo_two",
                     "at": iso(now() - timedelta(minutes=20)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_status", "from": "Priya Yun",
                     "firm": "Yun & Whitaker PLLC",
                     "text": "any update on the whitaker serve",
                     "serve_id": "sv_demo_diligent",
                     "at": iso(now() - timedelta(minutes=45)), "demo_tag": "demo"})
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"serves": len(serves), "attempts": len(attempts)})
    print(f"Seeded {len(SERVERS)} servers, {len(serves)} serves "
          f"({sum(1 for s in serves if s['status'] in ('papers_in', 'attempting'))} open), "
          f"{len(attempts)} attempts, {len(messages)} messages")


if __name__ == "__main__":
    main()
