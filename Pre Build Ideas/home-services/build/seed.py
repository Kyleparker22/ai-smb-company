#!/usr/bin/env python3
"""Dispatch OS — synthetic business generator.

Builds a whole residential HVAC + plumbing + electrical contractor at any
scale. Everything is invented: 555 phone ranges, made-up names, no real
addresses, no network calls. The point is that an operator recognizes their
own week in it — seasonal peaks, calls that ring out at 6pm, estimates rotting
at every age, and technician notes written the way technicians actually write.

  python3 seed.py                    # the default shop
  python3 seed.py --jobs 4000 --months 24 --reset

Stdlib only.
"""
import argparse, random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

R = random.Random(20260816)

FIRST = ["Dana", "Marcus", "Priya", "Ellis", "Tomas", "Nia", "Grant", "Sofia", "Wes", "Imani",
         "Beau", "Carla", "Devon", "Rosa", "Hank", "June", "Ozzie", "Tanya", "Vic", "Yolanda",
         "Cody", "Meg", "Rashad", "Lena", "Otis", "Bree", "Sam", "Kira", "Nolan", "Pearl"]
LAST = ["Alvarez", "Brenner", "Castile", "Dorsey", "Eakin", "Fontaine", "Gaddis", "Holloway",
        "Ives", "Jessup", "Kimball", "Lowery", "Mancuso", "Nunez", "Ostrander", "Pruitt",
        "Quimby", "Reddick", "Sackett", "Thorne", "Uhlman", "Vandiver", "Whitlock", "Yancey"]
STREETS = ["Bellhaven Ct", "Copperline Dr", "Dunhill Rd", "Everly Ln", "Fairmount Ave",
           "Grovepoint Way", "Hollis St", "Ironwood Dr", "Juniper Bend", "Kestrel Ct"]

TECHS = [("Ray Sackett", ["hvac"]), ("Marcus Dorsey", ["hvac", "plumbing"]),
         ("Priya Kimball", ["hvac"]), ("Ellis Thorne", ["plumbing"]),
         ("Nia Whitlock", ["plumbing"]), ("Grant Pruitt", ["electrical"]),
         ("Sofia Mancuso", ["electrical", "hvac"]), ("Wes Holloway", ["hvac"]),
         ("Beau Reddick", ["plumbing", "electrical"])]

# The messy prose half of the deferred-work ledger. Written the way a tech
# writes at 4:50pm on a phone.
TECH_NOTES = [
    "cap reading low, out of spec. told cust, declined for now",
    "contactor pitted pretty bad — quoted, cust wants to wait til next month",
    "coil dirty, restricted airflow. recommended clean, declined",
    "duct leak in crawl, disconnected boot at back bedroom. cust said maybe fall",
    "heat exchanger has rust and a suspect crack - RED TAG discussed, cust wants 2nd opinion",
    "water heater is 14 yr, rusty at base. recommended replace, not today",
    "PRV failed, pressure at 118. quoted, declined",
    "panel is a Federal Pacific, obsolete + unsafe. gave quote, cust thinking",
    "no gfci in the kitchen or exterior, ungrounded. recommended, declined",
    "cleared the clog, all good",                      # parses to nothing on purpose
    "replaced capacitor under warranty, running fine",  # ditto
    "cust asked about a mini split for the garage, said he'd call back",  # ditto — a human should read this
]

SCOPES = {
    "hvac_replacement": ["14 SEER2 3-ton system, coil and lineset flush", "furnace + coil replacement, 80% AFUE",
                         "heat pump changeout with new pad and disconnect"],
    "plumb_water_heater": ["50 gal gas water heater, new expansion tank and pan"],
    "elec_panel": ["200A panel and meter base, permit and inspection included"],
    "hvac_no_cool": ["compressor start kit and capacitor"],
    "plumb_leak": ["repipe of the wet wall under the kitchen"],
}


def money(lo, hi):
    return round(R.uniform(lo, hi), 2)


def build(n_jobs, months, reset):
    if reset:
        store.wipe()
    t0 = now()

    # -- config -----------------------------------------------------------
    store.save("config", {
        "company": "Ridgeline Home Services",
        "owner": {"name": "Dale Ridgeway", "role": "Owner"},
        "trades": list(core.TRADES),
        "service_area": list(core.ZONES),
        "trucks": len(TECHS),
        "employees": 22,
        "diagnostic_fee": core.DIAGNOSTIC_FEE,
        "after_hours_fee": core.AFTER_HOURS_FEE,
        "membership_fee": core.MEMBERSHIP_FEE,
        "seeded_at": iso(),
        # The operator's own numbers. `recovered_book_rate` is deliberately
        # absent so the ROI panel opens with a line honestly blank.
        "roi_inputs": {"incremental_close_rate": 0.12, "reoffer_accept_rate": 0.18,
                       "admin_hours_wk": 11, "loaded_rate": 34},
    })

    # -- people -----------------------------------------------------------
    techs = []
    for i, (name, skills) in enumerate(TECHS):
        techs.append({"id": f"tech_{i+1}", "name": name, "skills": skills,
                      "home_zone": R.choice(core.ZONES)})
    store.save("technicians", techs)

    customers = []
    for i in range(max(240, n_jobs // 3)):
        name = f"{R.choice(FIRST)} {R.choice(LAST)}"
        customers.append({
            "id": f"cust_{i+1}", "name": name,
            "phone": f"555-01{R.randint(10,99)}", "zone": R.choice(core.ZONES),
            "address": f"{R.randint(100,9800)} {R.choice(STREETS)}",
            "member": R.random() < 0.22,
            "since": iso(t0 - timedelta(days=R.randint(30, 1800))),
        })
    store.save("customers", customers)

    # -- jobs, notes, calls, estimates ------------------------------------
    jobs, calls, estimates, recs = [], [], [], []
    classes = list(core.JOB_CLASSES)

    for i in range(n_jobs):
        age = R.randint(0, months * 30)
        when = t0 - timedelta(days=age, hours=R.randint(0, 9))
        # seasonality: cooling calls in summer months, heat in winter
        m = when.month
        pool = [c for c in classes
                if core.JOB_CLASSES[c]["season"] in ("any", "shoulder")
                or (core.JOB_CLASSES[c]["season"] == "summer" and m in (5, 6, 7, 8, 9))
                or (core.JOB_CLASSES[c]["season"] == "winter" and m in (11, 12, 1, 2, 3))]
        cls = R.choice(pool or classes)
        spec = core.JOB_CLASSES[cls]
        cust = R.choice(customers)
        note = R.choice(TECH_NOTES) if R.random() < 0.34 else None
        job = {"id": f"job_{i+1}", "customer_id": cust["id"], "job_class": cls,
               "trade": spec["trade"], "zone": cust["zone"],
               "created_at": iso(when), "completed_at": iso(when + timedelta(hours=2)),
               "status": "complete", "invoiced": money(*spec["ticket"]),
               "tech_id": R.choice([t["id"] for t in techs if spec["trade"] in t["skills"]]),
               "tech_note": note,
               "note_declined": True}
        jobs.append(job)

        # a slice of the big-ticket jobs started life as an estimate
        if spec["ticket"][1] > 2000 and R.random() < 0.75:
            presented = when - timedelta(days=R.randint(0, 40))
            amount = money(spec["ticket"][0], spec["ticket"][1])
            state = R.choices(["won", "lost", "presented"], [0.34, 0.31, 0.35])[0]
            est = {"id": f"est_{len(estimates)+1}", "customer_id": cust["id"],
                   "customer_name": cust["name"], "job_class": cls,
                   "scope": R.choice(SCOPES.get(cls, [spec["label"].lower()])),
                   "amount": amount, "presented_at": iso(presented),
                   "tech_name": R.choice(techs)["name"], "state": state, "touches": []}
            if state in ("won", "lost"):
                est["decided_at"] = iso(presented + timedelta(days=R.randint(1, 25)))
                if state == "lost":
                    est["loss_reason"] = R.choice(core.LOSS_REASONS)
            estimates.append(est)

    # calls: 18 months of them, with a real abandon pattern — peak-hour
    # simultaneity and everything after 5pm.
    for i in range(int(n_jobs * 1.6)):
        age = R.randint(0, months * 30)
        hour = R.choices(range(6, 23), [2, 6, 9, 10, 11, 10, 9, 8, 8, 7, 6, 5, 5, 4, 3, 2, 2])[0]
        when = t0 - timedelta(days=age)
        when = when.replace(hour=hour, minute=R.randint(0, 59))
        after = hour < core.WORK_START or hour >= core.WORK_END
        missed = R.random() < (0.55 if after else 0.14)
        cust = R.choice(customers)
        calls.append({"id": f"call_{i+1}", "at": iso(when), "customer_id": cust["id"],
                      "channel": R.choice(["phone", "phone", "phone", "web_form", "text"]),
                      "transcript": R.choice([
                          "my ac is not cooling, house is 81",
                          "no heat this morning, thermostat is calling",
                          "kitchen drain is slow again",
                          "no hot water since last night",
                          "half the outlets in the living room are dead",
                          "want a quote on a new system",
                          "need a tune up before summer",
                          "toilet keeps running"]),
                      "outcome": "missed" if missed else "answered",
                      "handled_at": None if missed else iso(when + timedelta(minutes=2)),
                      "booked_job": None})

    # -- today's live board: the demo set, deterministic on purpose ---------
    demo = [
        ("9:40pm, after hours", 21, 40, "my ac is not cooling, house is 81 in here"),
        ("emergency", 22, 12, "I smell gas in the basement near the furnace"),
        ("ambiguous", 7, 5, "not sure, something smells weird near the furnace"),
        ("no symptom", 9, 15, "the thing on the wall is beeping and I don't know what it is"),
        ("standard", 10, 30, "no hot water since this morning"),
    ]
    for k, (tag, hh, mm, text) in enumerate(demo):
        cust = customers[k]
        cust["zone"] = "central"
        calls.append({"id": f"call_demo_{k+1}", "at": iso(t0.replace(hour=hh, minute=mm) - timedelta(days=0 if hh < t0.hour else 1)),
                      "customer_id": cust["id"], "channel": "phone", "demo_tag": tag,
                      "transcript": text, "outcome": None, "handled_at": None, "booked_job": None})

    # a flagship aging estimate for the demo
    estimates.append({"id": "est_demo_1", "customer_id": customers[6]["id"],
                      "customer_name": customers[6]["name"], "job_class": "hvac_replacement",
                      "scope": "14 SEER2 3-ton system, coil and lineset flush",
                      "amount": 9400.0, "presented_at": iso(t0 - timedelta(days=16)),
                      "tech_name": "Ray Sackett", "state": "presented", "touches": []})

    store.save("jobs", jobs)
    store.save("calls", calls)
    store.save("estimates", estimates)
    store.save("recommendations", recs)

    # -- the board: today + tomorrow --------------------------------------
    slots = []
    for d in (0, 1):
        day = (t0 + timedelta(days=d)).replace(minute=0, second=0, microsecond=0)
        for t in techs:
            for h in (8, 11, 14, 16):
                if R.random() < 0.35 and d == 0:
                    continue                      # today is already partly full
                slots.append({"id": f"slot_{d}_{t['id']}_{h}", "tech_id": t["id"],
                              "tech_name": t["name"], "skills": t["skills"],
                              "starts_at": iso(day.replace(hour=h)),
                              "from_zone": t["home_zone"], "minutes_free": R.choice([120, 180, 240]),
                              "booked_job": None})
        # a genuine after-hours slot so the R1 path is demonstrable
        slots.append({"id": f"slot_{d}_after", "tech_id": techs[0]["id"], "tech_name": techs[0]["name"],
                      "skills": ["hvac", "plumbing"], "starts_at": iso(day.replace(hour=19)),
                      "from_zone": "central", "minutes_free": 240, "booked_job": None})
    store.save("slots", slots)
    store.save("approvals", [])
    store.save("messages", [])
    store.save("events", [])

    return {"customers": len(customers), "technicians": len(techs), "jobs": len(jobs),
            "calls": len(calls), "estimates": len(estimates), "slots": len(slots)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=2800)
    ap.add_argument("--months", type=int, default=18)
    ap.add_argument("--reset", action="store_true", default=True)
    a = ap.parse_args()
    print(build(a.jobs, a.months, a.reset))
