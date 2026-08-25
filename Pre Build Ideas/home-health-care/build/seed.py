#!/usr/bin/env python3
"""Shift OS — synthetic agency generator.

A private-duty home care agency. Invented client, caregiver and referral-source
names, 555 numbers, no real addresses. Built so a scheduler recognizes their own
Monday: callouts at bad hours, caregivers at every stage of retention risk, EVV
exceptions of every type, authorizations near their limits, and family messages
including clinical and crisis phrasing.

  python3 seed.py --caregivers 210 --clients 140 --weeks 26
"""
import argparse, random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

R = random.Random(20260816)

CG_FIRST = ["Adaeze", "Bernadette", "Clarisse", "Dorothy", "Esperanza", "Felicity", "Grace",
            "Hyacinth", "Imelda", "Josephine", "Kesia", "Loretta", "Marguerite", "Ndidi",
            "Ophelia", "Perpetua", "Rosalind", "Sunita", "Theodora", "Ursuline", "Valentina",
            "Winifred", "Yolanda", "Zipporah", "Marcus", "Devon", "Emmanuel"]
CG_LAST = ["Achebe", "Boateng", "Castellanos", "Duarte", "Eze", "Fofana", "Gutierrez", "Haddad",
           "Ibrahim", "Jimenez", "Kamau", "Lindqvist", "Mensah", "Nkemelu", "Okafor", "Perreira",
           "Quintero", "Ramnarine", "Sowande", "Tetteh"]
CL_FIRST = ["Arthur", "Beatrice", "Clifford", "Dorothea", "Edmund", "Frances", "Gerald",
            "Harriet", "Irving", "Josephine", "Kenneth", "Lillian", "Mortimer", "Norma",
            "Oswald", "Priscilla", "Raymond", "Sylvia", "Theodore", "Vivian"]
CL_LAST = ["Ainsworth", "Bellamy", "Carmichael", "Dunmore", "Everhart", "Fitzgerald", "Grantham",
           "Hollingsworth", "Ives", "Jennings", "Kingsbury", "Lockridge", "Merriman", "Nightingale"]
ZONES = ["north", "central", "south", "west"]
REFERRERS = ["Mercy General discharge planning", "Cedar Ridge SNF", "Northshore case management",
             "Dr. Vasquez's office", "family (self-referred)"]

ROUTINE_MSGS = ["can we move Thursday to Friday", "what time is the visit tomorrow",
                "please send the invoice again", "the aide was 20 minutes late",
                "can we add a Saturday shift", "is the same person coming next week"]
CLINICAL_MSGS = ["should she take her pill twice today?", "what is this new pill for",
                 "her blood pressure was 180 over 100", "is that wound getting infected",
                 "do you think she's getting worse", "can we change her care plan to add oxygen"]
CRISIS_MSGS = ["she fell in the bathroom and I can't get her up",
               "mom is complaining of chest pain",
               "he can't breathe properly, gasping",
               "there are bruises we can't explain and she's afraid of her son"]


def build(n_caregivers, n_clients, weeks, reset=True):
    if reset:
        store.wipe()
    t0 = now()

    store.save("config", {
        "agency": "Willowmere Home Care",
        "revenue": "$6.5M", "software": "modelled, not connected",
        # EVV rules are the agency's, editable — no state's requirements are hardcoded
        "evv_rules": {**core.DEFAULT_EVV_RULES,
                      "_source": "agency default for this demo — replace with the state's own "
                                 "rule set before go-live"},
        "seeded_at": iso(),
        "roi_inputs": {"fill_points_gained": 0.12, "revenue_per_shift": 132, "margin": 0.34,
                       "avoidable_share": 0.4, "denial_rate": 0.22, "avg_visit_value": 132,
                       "departures_per_year": 84, "replacement_cost": 3200,
                       "prevention_share": 0.15},
    })

    caregivers = []
    for i in range(n_caregivers):
        skills = R.sample(core.SKILLS, R.randint(1, 4))
        caregivers.append({
            "id": f"cg_{i+1}", "name": f"{R.choice(CG_FIRST)} {R.choice(CG_LAST)}",
            "phone": f"555-07{R.randint(10,99)}", "skills": skills,
            "pay_rate": round(R.uniform(15.5, 22.0), 2),
            "travel_minutes": {z: R.choice([8, 12, 18, 26, 34, 50, 70]) for z in ZONES},
            "available": R.random() < 0.55,
            "preferred_hours_week": R.choice([None, 20, 30, 32, 40]),
            "short_notice_accepted": R.choice([None, 0, 1, 2, 3, 4, 5]),
            "declined_in_a_row": R.choices([0, 1, 2, 3, 4], [60, 20, 10, 7, 3])[0],
            "last_office_contact": (None if R.random() < 0.1 else
                                    iso(t0 - timedelta(days=R.choice([2, 6, 14, 25, 40, 70])))),
        })
    store.save("caregivers", caregivers)

    clients, pairings, auths = [], [], []
    for i in range(n_clients):
        plan = R.sample(list(core.TASKS), R.randint(2, 5))
        c = {"id": f"cl_{i+1}", "name": f"{R.choice(CL_FIRST)} {R.choice(CL_LAST)}",
             "zone": R.choice(ZONES), "care_plan": plan,
             "payer": R.choices(["private", "medicaid_waiver"], [62, 38])[0],
             "preferred_caregivers": []}
        clients.append(c)
        pool = [cg for cg in caregivers
                if not ({core.TASKS[t]["skill"] for t in plan if core.TASKS[t]["skill"]} - set(cg["skills"]))]
        for cg in R.sample(pool, min(len(pool), R.randint(2, 5))):
            pairings.append({"id": f"pr_{len(pairings)+1}", "caregiver_id": cg["id"],
                             "client_id": c["id"],
                             "state": R.choices(["approved", "declined"], [88, 12])[0]})
        c["preferred_caregivers"] = [p["caregiver_id"] for p in pairings
                                     if p["client_id"] == c["id"] and p["state"] == "approved"][:2]
        auths.append({"id": f"au_{i+1}", "client_id": c["id"],
                      "authorized_hours": R.choice([20, 30, 40, 60, 80]),
                      "used_hours": R.choice([5, 15, 25, 38, 58, 79]),
                      "period": "month"})
    store.save("clients", clients)
    store.save("pairings", pairings)
    store.save("authorizations", auths)

    # -- shifts -------------------------------------------------------------
    shifts = []
    for w in range(weeks):
        for c in clients:
            approved = [p["caregiver_id"] for p in pairings
                        if p["client_id"] == c["id"] and p["state"] == "approved"]
            if not approved:
                continue
            for _ in range(R.randint(2, 5)):
                start = t0 - timedelta(days=w * 7 + R.randint(0, 6),
                                       hours=R.randint(0, 12))
                hours = R.choice([3, 4, 4, 6, 8])
                state = R.choices(["completed", "caregiver_cancelled"], [93, 7])[0]
                s = {"id": f"sh_{len(shifts)+1}", "client_id": c["id"],
                     "caregiver_id": R.choice(approved), "starts_at": iso(start),
                     "hours": hours, "state": state}
                if state == "completed":
                    late = R.choice([0, 0, 0, 5, 25])
                    s["clock_in"] = (None if R.random() < 0.07 else
                                     iso(start + timedelta(minutes=late)))
                    s["clock_out"] = (None if R.random() < 0.05 else
                                      iso(start + timedelta(hours=hours)))
                    s["notes"] = None if R.random() < 0.11 else "tasks completed per care plan"
                    s["gps"] = R.random() < 0.8
                shifts.append(s)

    # upcoming scheduled shifts
    for c in clients:
        approved = [p["caregiver_id"] for p in pairings
                    if p["client_id"] == c["id"] and p["state"] == "approved"]
        if not approved:
            continue
        for d in range(1, 4):
            if R.random() < 0.5:
                continue
            start = (t0 + timedelta(days=d)).replace(hour=R.choice([7, 9, 13, 17]), minute=0)
            shifts.append({"id": f"sh_up_{len(shifts)+1}", "client_id": c["id"],
                           "caregiver_id": R.choice(approved), "starts_at": iso(start),
                           "hours": R.choice([3, 4, 6]), "state": "scheduled"})

    # open (unfilled) shifts inside 72 hours
    for i in range(14):
        c = R.choice(clients)
        start = t0 + timedelta(hours=R.randint(2, 70))
        shifts.append({"id": f"sh_open_{i+1}", "client_id": c["id"], "caregiver_id": None,
                       "starts_at": iso(start), "hours": R.choice([3, 4, 6]),
                       "state": "open", "opened_at": iso(t0 - timedelta(hours=1))})

    # -- the demo set -------------------------------------------------------
    demo_client = next(c for c in clients if "transfer" in c["care_plan"]) if any(
        "transfer" in c["care_plan"] for c in clients) else clients[0]
    if "transfer" not in demo_client["care_plan"]:
        demo_client["care_plan"].append("transfer")
    demo_shift = {"id": "sh_demo", "client_id": demo_client["id"],
                  "caregiver_id": [p["caregiver_id"] for p in pairings
                                   if p["client_id"] == demo_client["id"]
                                   and p["state"] == "approved"][0],
                  "starts_at": iso(t0.replace(minute=0) + timedelta(hours=1)),
                  "hours": 6, "state": "scheduled", "demo_tag": "the 6:12am callout"}
    shifts.append(demo_shift)
    store.save("shifts", shifts)

    # -- messages -----------------------------------------------------------
    messages = []
    for i in range(240):
        roll = R.random()
        text = (R.choice(CRISIS_MSGS) if roll < 0.04 else
                R.choice(CLINICAL_MSGS) if roll < 0.34 else R.choice(ROUTINE_MSGS))
        messages.append({"id": f"m_{i+1}", "at": iso(t0 - timedelta(days=R.randint(0, 60),
                                                                   hours=R.randint(0, 20))),
                         "client_id": R.choice(clients)["id"], "from": "family",
                         "text": text, "handled_at": None})
    for k, (tag, text) in enumerate([
            ("crisis — fall", "she fell in the bathroom and I can't get her up"),
            ("clinical — dosing", "should she take her pill twice today?"),
            ("suspected abuse", "there are bruises we can't explain and she's afraid of her son"),
            ("routine", "can we move Thursday to Friday")]):
        messages.append({"id": f"m_demo_{k+1}", "at": iso(t0 - timedelta(minutes=10 * (k + 1))),
                         "client_id": clients[k]["id"], "from": "family", "text": text,
                         "handled_at": None, "demo_tag": tag})
    store.save("messages", messages)
    store.save("evv", [])
    store.save("approvals", [])
    store.save("events", [])
    return {"caregivers": len(caregivers), "clients": len(clients), "pairings": len(pairings),
            "shifts": len(shifts), "messages": len(messages)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--caregivers", type=int, default=210)
    ap.add_argument("--clients", type=int, default=140)
    ap.add_argument("--weeks", type=int, default=26)
    a = ap.parse_args()
    print(build(a.caregivers, a.clients, a.weeks))
