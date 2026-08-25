#!/usr/bin/env python3
"""Seed a realistic portfolio so every read in the product has real arithmetic
behind it. Deterministic (seeded RNG) — the same portfolio every time, so a
demo is reproducible and the test suite can pin numbers.

  python3 seed.py                 # 6 properties / 220 units / 18 months
  python3 seed.py --units 300     # top of the ICP
  python3 seed.py --units 24      # bottom of the ICP
  python3 seed.py --months 24

Nothing here is a claim about a real portfolio. It is synthetic data whose
DISTRIBUTIONS are drawn from what a 20–300 unit operator actually sees:
~3.2 maintenance requests per occupied unit per year, plumbing and HVAC
together over half of volume, a long tail of cosmetic, ~16% of jobs stalled
on a part / an approval / access, and a vendor bench where two are excellent,
most are fine, and one is quietly costing the portfolio money.

One consequence worth stating up front, because it surprises people: by
Little's Law a well-run portfolio carries a SMALL open queue. 220 units at
3.2 requests/unit/year with a ~4-day mean cycle is ~25–30 open at any moment,
not hundreds. If a competing dashboard shows a 200-row open board for this
portfolio size, that is a backlog, not a feature.
"""
import argparse, random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import iso, now, nid, parse, CATEGORIES, PRIORITIES, COMPONENT_LIFE

R = random.Random(20260814)
RA = random.Random(20260817)   # availability-only stream — never touches R's sequence

# Requests per occupied unit per year. 1.5–2 is class-A new construction;
# 3–4 is the mixed-vintage class B/C stock a 20–300 unit operator actually
# holds. Using the class-A number is how software demos end up with an empty
# board and a resolution-time average built on nothing.
REQ_PER_UNIT_YEAR = 3.2

FIRST = ["Maria", "James", "Aisha", "Daniel", "Sofia", "Marcus", "Priya", "Kevin", "Elena",
         "Tyrone", "Hannah", "Luis", "Grace", "Omar", "Nicole", "Andre", "Fatima", "Ryan",
         "Camila", "Isaac", "Wen", "Bianca", "Jonah", "Leila", "Trevor", "Dana", "Nikhil",
         "Rosa", "Curtis", "Yara", "Peter", "Simone", "Adam", "Naomi", "Victor", "Kelly"]
LAST = ["Alvarez", "Brooks", "Chen", "Delgado", "Ellis", "Ferrara", "Gaines", "Huang",
        "Ibrahim", "Jensen", "Koval", "Lombardi", "Mensah", "Nakamura", "Okafor", "Patel",
        "Quintero", "Reyes", "Santos", "Thompson", "Ustinov", "Vargas", "Whitaker", "Yousef"]

PROPERTIES = [
    ("Cedar Ridge Apartments", "4120 Cedar Ridge Rd", "Yourtown", "NC", 1998, 0.34),
    ("The Millworks Lofts", "88 Foundry St", "Yourtown", "NC", 1926, 0.16),
    ("Harborview Townhomes", "215 Harborview Ln", "Yourtown", "NC", 2015, 0.14),
    ("Pinecrest Garden", "9 Pinecrest Ct", "Concord", "NC", 1985, 0.18),
    ("Elm & Third", "301 Elm St", "Concord", "NC", 2004, 0.11),
    ("Waverly Duplexes", "12–40 Waverly Ave", "Gastonia", "NC", 1972, 0.07),
]

# (name, email, property indexes, standing per-job limit, emergency authority)
# The two limits are different instruments: the standing limit is how much
# routine spend the owner delegates per job; the emergency authority is how far
# the manager may go WITHOUT asking when a P1 habitability clock is running.
OWNERS = [
    ("Nakamura Family Trust", "k.nakamura@example.com", [0, 2], 400, 2000),
    ("Beacon Hill Holdings LLC", "ops@beaconhillhold.example.com", [1, 4], 750, 3500),
    ("R. Whitaker", "rwhitaker@example.com", [3, 5], 250, 1200),
]

VENDORS = [
    # name, trades, hourly, quality tier (drives the simulated outcomes)
    ("Sutter Plumbing Co.",       ["plumbing"],               115, "great"),
    ("Bluewater Drain & Sewer",   ["plumbing"],                98, "good"),
    ("Rapid Rooter 24/7",         ["plumbing"],               140, "poor"),
    ("Carolina Comfort HVAC",     ["hvac"],                   125, "great"),
    ("AirLogic Heating & Air",    ["hvac"],                   110, "good"),
    ("Volt & Sons Electric",      ["electrical"],             130, "great"),
    ("Piedmont Electrical",       ["electrical"],             105, "good"),
    ("Queen City Appliance",      ["appliance"],               95, "good"),
    ("FixIt Appliance Repair",    ["appliance"],               85, "poor"),
    ("Guardian Lock & Key",       ["locksmith"],               95, "good"),
    ("Sentry Pest Solutions",     ["pest"],                    80, "great"),
    ("Handy Hands LLC",           ["handyman", "general"],     70, "good"),
    ("Tri-County General Contr.", ["general", "handyman"],     95, "good"),
    ("Westside Handyman",         ["handyman"],                65, "poor"),
]

TIER = {  # first-time-fix, sla-hit, rating mean, response hours, cost multiplier
    "great": (0.93, 0.94, 4.7, 2.5, 1.00),
    "good":  (0.84, 0.82, 4.2, 5.0, 1.05),
    "poor":  (0.62, 0.55, 3.1, 14.0, 1.42),
}

CAT_WEIGHTS = [
    ("leak_slow", 11), ("drain_slow", 9), ("toilet_clog", 8), ("disposal", 6),
    ("no_hot_water", 6), ("leak_active", 2),
    ("no_cooling", 10), ("no_heat", 6),
    ("no_power_partial", 6), ("no_power_full", 1),
    ("appliance", 12), ("smoke_alarm", 5), ("pest", 5), ("lock_door", 2),
    ("mold_moisture", 2), ("cosmetic", 8), ("other", 3),
]

FREETEXT = {
    "leak_slow": ["there's water under the kitchen sink again, the cabinet floor is damp",
                  "small leak from the bathroom faucet, drips all night"],
    "drain_slow": ["shower drain is backing up, water to my ankles by the end",
                   "kitchen sink draining really slow the last few days"],
    "toilet_clog": ["toilet won't flush and the water came near the rim", "guest bathroom toilet is clogged"],
    "disposal": ["garbage disposal just hums, doesn't spin", "disposal stopped working, nothing happens"],
    "no_hot_water": ["no hot water at all since last night, cold showers",
                     "water heater not heating, only lukewarm"],
    "leak_active": ["water pouring from the ceiling in the hallway!!", "pipe burst under the sink, flooding"],
    "no_cooling": ["a/c is running but blowing warm air, apartment is 84 degrees",
                   "air conditioning not cooling at all"],
    "no_heat": ["no heat, furnace won't come on and it's 38 outside", "heater blowing cold, apartment freezing"],
    "no_power_partial": ["outlets in the kitchen are dead, breaker looks fine",
                         "bathroom outlets have no power"],
    "no_power_full": ["whole unit has no electricity", "power out in the entire apartment"],
    "appliance": ["dishwasher won't drain, standing water in the bottom",
                  "oven doesn't heat up past 200", "refrigerator not cooling, food spoiling",
                  "dryer runs but clothes stay wet"],
    "smoke_alarm": ["smoke detector chirping every minute all night", "hallway alarm beeping"],
    "pest": ["seeing roaches in the kitchen at night", "mice in the pantry, found droppings"],
    "lock_door": ["front door lock is broken, won't latch", "locked out, key snapped in the lock"],
    "mold_moisture": ["black spots growing on the bathroom ceiling", "musty smell and damp wall in the bedroom"],
    "cosmetic": ["closet door came off the track", "big paint scuff and hole from the previous tenant",
                 "window screen torn"],
    "other": ["window won't stay open", "mailbox lock is stuck"],
}


def weighted(pairs):
    tot = sum(w for _, w in pairs)
    x = R.uniform(0, tot)
    for k, w in pairs:
        x -= w
        if x <= 0:
            return k
    return pairs[-1][0]


def build(n_units=220, months=18):
    t0 = now()
    props, units, tenants, owners, vendors = [], [], [], [], []
    components, requests, events, surveys, messages = [], [], [], [], []

    # ---- owners & properties
    for i, (name, addr, city, st, built, share) in enumerate(PROPERTIES):
        props.append({"id": f"prop_{i+1}", "name": name, "address": addr, "city": city,
                      "state": st, "year_built": built, "owner_id": None})
    for i, (name, email, pidx, limit, em_limit) in enumerate(OWNERS):
        oid = f"own_{i+1}"
        owners.append({"id": oid, "name": name, "email": email,
                       "properties": [props[j]["id"] for j in pidx],
                       "spend_approval_limit": limit,
                       "emergency_spend_limit": em_limit,
                       "reserve_policy": "Approve anything under the limit; notify same-day. "
                                         "P1 habitability: proceed up to the emergency "
                                         "authority, notice immediately."})
        for j in pidx:
            props[j]["owner_id"] = oid
    limit_by_prop = {pr["id"]: next((o["spend_approval_limit"] for o in owners
                                     if pr["id"] in o["properties"]), 400)
                     for pr in props}

    # ---- units
    for i, p in enumerate(props):
        count = max(2, round(n_units * PROPERTIES[i][5]))
        for k in range(count):
            floor = k // 8 + 1
            label = f"{floor}{k % 8 + 1:02d}" if count > 8 else f"Unit {chr(65 + k)}"
            beds = weighted([(1, 3), (2, 5), (3, 2)])
            rent = int((820 + beds * 340 + max(0, p["year_built"] - 1970) * 3.2) / 5) * 5
            u = {"id": nid("unit"), "property_id": p["id"], "label": label, "beds": beds,
                 "baths": 1 if beds == 1 else 2, "sqft": 520 + beds * 280,
                 "rent": rent, "tenant_id": None, "lease": {}}
            units.append(u)

    # ---- tenants & leases (staggered, with a realistic 60-day cluster)
    for u in units:
        if R.random() < 0.045:          # ~4.5% vacancy
            u["lease"] = {"start": None, "end": None, "status": "vacant"}
            continue
        tid = nid("ten")
        months_in = R.randint(2, 42)
        start = t0 - timedelta(days=30 * months_in)
        term = R.choice([12, 12, 12, 18, 24])
        end = start + timedelta(days=365 * (term // 12) + (183 if term == 18 else 0))
        while end < t0:                 # roll renewals forward to today
            start, end = end, end + timedelta(days=365)
        name = f"{R.choice(FIRST)} {R.choice(LAST)}"
        tenants.append({
            "id": tid, "name": name, "unit_id": u["id"],
            "email": name.lower().replace(" ", ".") + "@example.com",
            "phone": f"704-555-{R.randint(1000, 9999)}",
            "move_in": iso(t0 - timedelta(days=30 * months_in)),
            "language": "es" if R.random() < 0.12 else "en",
            "comms_pref": R.choice(["sms", "sms", "sms", "email", "app"]),
            "vulnerable_occupant": R.random() < 0.09,
            "rent_on_time_streak": R.randint(0, 24),
        })
        u["tenant_id"] = tid
        u["lease"] = {"start": iso(start), "end": iso(end), "term_months": term,
                      "status": "active", "renewal_status": "not_started"}

    # ---- components (the asset ledger)
    for u in units:
        p = next(x for x in props if x["id"] == u["property_id"])
        for kind in ("water_heater", "furnace", "ac", "disposal", "appliance"):
            if kind == "disposal" and R.random() < 0.25:
                continue
            spec = COMPONENT_LIFE[kind]
            # Install date spread across the service life, capped by the building's
            # age. Drawing ages clustered AT the service life (the obvious way to
            # write this) makes ~70% of the portfolio read as end-of-life, which is
            # not what a real building looks like and would make the capital
            # recommendations meaningless noise.
            age = R.uniform(0.08, 1.25) * spec["life"]
            age = max(1.0, min(age, max(1, 2026 - p["year_built"])))
            components.append({
                "id": nid("cmp"), "unit_id": u["id"], "property_id": p["id"], "kind": kind,
                "label": spec["label"],
                "installed": iso(t0 - timedelta(days=int(365.25 * age))),
                "capital_flagged": None,
                "make": R.choice(["Rheem", "Bradford White", "Goodman", "Carrier", "Trane",
                                  "InSinkErator", "Whirlpool", "GE", "Frigidaire"]),
                "model": f"{R.choice('ABCDXR')}{R.randint(100, 999)}-{R.randint(10, 99)}",
                "serial": f"SN{R.randint(10**7, 10**8)}",
                "notes": "",
            })

    vmap = {}
    for i, (name, trades, rate, tier) in enumerate(VENDORS):
        vid = f"vnd_{i+1}"
        vmap[vid] = tier
        vendors.append({"id": vid, "name": name, "trades": trades, "hourly": rate,
                        "tier_seed": tier,
                        "phone": f"704-555-{R.randint(1000, 9999)}",
                        "email": name.lower().replace(" ", "").replace(".", "").replace("&", "and")[:16] + "@example.com",
                        "insurance_expires": iso(t0 + timedelta(days=R.randint(-20, 400))),
                        "w9_on_file": R.random() < 0.85,
                        "after_hours": tier != "poor",
                        "service_areas": ["Yourtown", "Concord", "Gastonia"],
                        "active": True})

    occupied = [u for u in units if u.get("tenant_id")]
    total_requests = int(len(occupied) * REQ_PER_UNIT_YEAR * (months / 12))
    # The last 12 days get their own burst so the live board reflects a real
    # working week rather than the tail of a uniform distribution.
    recent_n = max(18, int(len(occupied) * 0.22))

    for idx in range(total_requests + recent_n):
        u = R.choice(occupied)
        ten = next(t for t in tenants if t["id"] == u["tenant_id"])
        cat = weighted(CAT_WEIGHTS)
        spec = CATEGORIES[cat]
        if idx >= total_requests:
            sub = t0 - timedelta(days=R.randint(0, 12), hours=R.randint(0, 23))
        else:
            sub = t0 - timedelta(days=R.randint(1, int(30.4 * months)), hours=R.randint(0, 23))
        # Seasonality: heat calls in winter, cooling calls in summer. Shifting the
        # month can land the date in the future, which shows up downstream as a
        # negative request age — so pull the year back whenever it does.
        def reseason(d, months):
            d = d.replace(month=R.choice(months), day=min(d.day, 28))
            while d > t0:
                d = d.replace(year=d.year - 1)
            return d
        if cat == "no_heat" and sub.month in (4, 5, 6, 7, 8, 9):
            sub = reseason(sub, [12, 1, 2])
        if cat == "no_cooling" and sub.month in (11, 12, 1, 2, 3):
            sub = reseason(sub, [6, 7, 8])
        text = R.choice(FREETEXT.get(cat, FREETEXT["other"]))
        tri = core.classify(text, photo_present=R.random() < 0.72)
        pri = tri["priority"]
        comp = next((c for c in components
                     if c["unit_id"] == u["id"] and c["kind"] == spec["component"]), None)

        rid = nid("req")
        r = {"id": rid, "unit_id": u["id"], "property_id": u["property_id"],
             "tenant_id": ten["id"], "title": text[:62], "description": text,
             "category": cat, "priority": pri, "status": "submitted",
             "submitted_at": iso(sub), "channel": R.choice(["app", "app", "app", "sms", "phone"]),
             "photos": ["(seed) tenant photo"] if tri["confidence"] > 0.5 else [],
             "triage": tri, "component_id": comp["id"] if comp else None,
             "entry_permission": R.choice(["anytime", "anytime", "appointment", "appointment"]),
             "pets": R.random() < 0.35}
        # appointment residents mostly state availability at intake; a slice is
        # deliberately old so the stale path ("never consent to enter") is live.
        # Drawn from a SEPARATE stream (RA) — consuming R here shifted every
        # downstream draw and broke the anomaly fixtures, found by the suite.
        if r["entry_permission"] == "appointment" and RA.random() < 0.7:
            r["availability"] = {
                "windows": RA.sample(list(core.AVAILABILITY_CHIPS), RA.randint(1, 3)),
                "stated_at": iso(sub if RA.random() < 0.85
                                 else sub - timedelta(days=RA.randint(20, 40)))}
        r.update(core.sla_due(r))
        events.append({"id": nid("ev"), "at": iso(sub), "kind": "submitted", "subject": rid,
                       "actor": f"tenant:{ten['id']}", "rung": None, "detail": {"channel": r["channel"]}})

        # Requests that arrived in the last ~36 hours are left exactly as the
        # resident filed them: status 'submitted', no triage, no vendor. This is
        # the live intake queue the triage agent picks up on its next run.
        # Simulating them all the way through would hide the one part of the
        # pipeline a reviewer most wants to watch actually run.
        if (t0 - sub).total_seconds() < 36 * 3600:
            requests.append(r)
            continue

        # --- triage (agent, R3)
        t_tri = sub + timedelta(minutes=R.randint(1, 4))
        events.append({"id": nid("ev"), "at": iso(t_tri), "kind": "triaged", "subject": rid,
                       "actor": "agent:triage", "rung": "R3",
                       "detail": {"category": cat, "priority": pri, "confidence": tri["confidence"]}})

        # --- deflection: only where a real self-fix exists
        if spec["self_fix"] and R.random() < 0.42:
            res = t_tri + timedelta(minutes=R.randint(4, 90))
            r.update(triage_final=True, spend_decided=True, checkback_sent=True,
                     status="resolved", resolution_kind="deflected",
                     resolved_at=iso(res), actual_cost=0,
                     tenant_rating=R.choice([4, 5, 5, 5]),
                     resolution_note=f"Tenant resolved with the guided fix: {spec['self_fix']}")
            events.append({"id": nid("ev"), "at": iso(t_tri), "kind": "deflected", "subject": rid,
                           "actor": "agent:concierge", "rung": "R3",
                           "detail": {"self_fix": spec["self_fix"], "avoided": spec["median_cost"]}})
            requests.append(r)
            continue

        # --- assignment
        cands = [v for v in vendors if spec["trade"] in v["trades"]] or \
                [v for v in vendors if "handyman" in v["trades"]]
        # the OS routes to the better vendor most of the time; the residual is
        # the availability reality (nights, weekends, the poor vendor picking up)
        cands.sort(key=lambda v: {"great": 0, "good": 1, "poor": 2}[v["tier_seed"]])
        v = cands[0] if R.random() < 0.6 else R.choice(cands)
        ftf, slahit, rmean, resp_h, mult = TIER[v["tier_seed"]]
        assign_delay = R.uniform(0.05, 0.6) if pri == "P1" else R.uniform(0.2, 6)
        t_as = t_tri + timedelta(hours=assign_delay)
        r.update(status="assigned", vendor_id=v["id"], assigned_at=iso(t_as))
        events.append({"id": nid("ev"), "at": iso(t_as), "kind": "assigned", "subject": rid,
                       "actor": "agent:dispatch", "rung": "R2",
                       "detail": {"vendor": v["name"], "why": "highest score for this trade + availability"}})

        # --- SLA escalation for the poor vendor
        if v["tier_seed"] == "poor" and R.random() < 0.3:
            events.append({"id": nid("ev"), "at": iso(t_as + timedelta(hours=resp_h * 0.8)),
                           "kind": "escalated", "subject": rid, "actor": "agent:dispatch", "rung": "R2",
                           "detail": {"reason": "no vendor confirmation before 75% of the response clock"}})

        # Cycle time is scheduling, not wrench time. The vendor is on site for
        # an hour; the tenant was available on Thursday. Modelling only the
        # wrench time is why software demos show 6-hour resolution and real
        # portfolios run in days.
        sched_h = {"P1": R.uniform(0.5, 4), "P2": R.uniform(8, 36),
                   "P3": R.uniform(48, 144), "P4": R.uniform(168, 500)}[pri]
        sched_h *= {"great": 0.75, "good": 1.0, "poor": 1.6}[v["tier_seed"]]
        t_start = t_as + timedelta(hours=max(0.4, sched_h))
        t_done = t_start + timedelta(hours=max(0.3, R.gauss(spec["minutes"] / 60, 0.5)))

        # The stall. In a real portfolio the queue is not clogged by slow work —
        # it is clogged by work that is WAITING on something: a backordered
        # part, an owner who hasn't approved a $900 quote, a tenant who won't
        # confirm entry, a cosmetic job scheduled three weeks out. Modelling
        # this is the difference between a demo board and a real one, and each
        # stall reason is a different agent's job to clear.
        #
        # The first few requests of the recent burst are FORCED to stall on the
        # owner's approval. Left to the 16% dice, a small seed (a 24-unit
        # portfolio, or the journey suite's 60-unit store) can roll zero of
        # them, and then the spend-approval path — the owner limit, the R1
        # escalation, the anomaly flag — exists in no seed of that size. The
        # journey suite asserts that path is alive; a guarantee, not a dice
        # roll, is what keeps that assertion meaningful.
        force_spend = total_requests <= idx < total_requests + 6
        if force_spend or R.random() < 0.16:
            stall = "awaiting_owner_approval" if force_spend else \
                weighted([("parts_backorder", 3), ("awaiting_owner_approval", 3),
                          ("no_access", 2), ("scheduled_out", 3), ("vendor_unresponsive", 2)])
            add_days = {"parts_backorder": R.randint(4, 21), "awaiting_owner_approval": R.randint(2, 16),
                        "no_access": R.randint(3, 18), "scheduled_out": R.randint(5, 24),
                        "vendor_unresponsive": R.randint(2, 11)}[stall]
            t_done = t_start + timedelta(days=add_days)
            r["stall_reason"] = stall
            r["stall_since"] = iso(t_start)
            if stall == "awaiting_owner_approval":
                # Most quotes waiting on an owner are waiting because the JOB is
                # big relative to that owner's standing limit, not because the
                # vendor is gouging. Drawing them all at 2–4x the median made
                # every single one trip the price-anomaly flag, which is the same
                # as having no flag at all.
                # A job that stalls on the owner's approval is BY DEFINITION one
                # their standing limit does not cover — drawing the quote from the
                # category median alone produced under-limit quotes that the agent
                # correctly auto-approved at R2, and the stall reason made no
                # sense. The quote is over the limit; whether it ALSO trips the
                # price-anomaly flag depends on the category (a $460 disposal
                # quote is genuinely both over-limit and anomalous; a $280
                # appliance quote against a $250 limit is neither gouging nor
                # unusual — just above what this owner delegates).
                cap = limit_by_prop.get(u["property_id"], 400)
                r["quote"] = round(max(
                    spec["median_cost"] * (R.uniform(2.0, 4.2) if R.random() < 0.18
                                           else R.uniform(0.9, 1.5)),
                    cap * R.uniform(1.03, 1.3)))
                # Hold RECENT ones open so the spend-approval path exists in
                # every seed (it had never once fired — a control nobody has
                # exercised is not a control). The first version of this held
                # open EVERY owner-approval stall across the whole history,
                # which put 26 zombie requests on the demo board, open 60–528
                # days and all "breached" — a quote from 17 months ago does not
                # sit unanswered in a portfolio anyone is actually running. An
                # owner who has not answered in ~3 weeks got chased and decided
                # historically; only the recent ones are legitimately live.
                if (t0 - t_start).days <= 21:
                    t_done = t0 + timedelta(days=R.randint(1, 9))

        # a slice is still open today
        if t_done > t0:
            r.update(status="in_progress" if t_start < t0 else "assigned")
            if t_start < t0:
                r["started_at"] = iso(t_start)
                events.append({"id": nid("ev"), "at": iso(t_start), "kind": "started", "subject": rid,
                               "actor": f"human:{v['id']}", "rung": None, "detail": {}})
            r["sla_breached"] = core.parse(r["resolve_by"]) < now()
            r["triage_final"] = True
            requests.append(r)
            continue

        cost = round(spec["median_cost"] * mult * R.uniform(0.75, 1.35))
        reopened = R.random() > ftf
        rating = max(1, min(5, round(R.gauss(rmean, 0.8))))
        r.update(triage_final=True, spend_decided=True, spend_approved=True,
                 checkback_sent=True, status_note_sent=True,
                 status="resolved", resolution_kind="fixed", started_at=iso(t_start),
                 resolved_at=iso(t_done), actual_cost=cost, quote=round(cost * R.uniform(0.9, 1.15)),
                 tenant_rating=rating, reopened=reopened,
                 sla_breached=core.parse(r["resolve_by"]) < t_done,
                 resolution_note=f"{v['name']} completed the repair.")
        events.append({"id": nid("ev"), "at": iso(t_start), "kind": "started", "subject": rid,
                       "actor": f"human:{v['id']}", "rung": None, "detail": {}})
        if cost <= 400:
            events.append({"id": nid("ev"), "at": iso(t_start), "kind": "spend_approved", "subject": rid,
                           "actor": "agent:dispatch", "rung": "R2",
                           "detail": {"amount": cost, "under_owner_limit": True}})
        else:
            events.append({"id": nid("ev"), "at": iso(t_start), "kind": "spend_approved", "subject": rid,
                           "actor": "human:mgr_1", "rung": None, "detail": {"amount": cost}})
        events.append({"id": nid("ev"), "at": iso(t_done), "kind": "resolved", "subject": rid,
                       "actor": f"human:{v['id']}", "rung": None, "detail": {"cost": cost}})
        events.append({"id": nid("ev"), "at": iso(t_done + timedelta(hours=48)), "kind": "message_sent",
                       "subject": rid, "actor": "agent:concierge", "rung": "R2",
                       "detail": {"template": "48h check-back", "to": "tenant"}})
        if reopened:
            events.append({"id": nid("ev"), "at": iso(t_done + timedelta(hours=50)), "kind": "reopened",
                           "subject": rid, "actor": "agent:concierge", "rung": "R3",
                           "detail": {"reason": "tenant answered 'not fixed' on the 48h check-back"}})
        requests.append(r)

    # ---- renewal surveys on a slice of units
    for u in occupied:
        if R.random() < 0.3:
            surveys.append({"id": nid("srv"), "unit_id": u["id"], "tenant_id": u["tenant_id"],
                            "at": iso(t0 - timedelta(days=R.randint(5, 120))),
                            "nps": R.randint(2, 10),
                            "renew_intent": weighted([("yes", 6), ("unsure", 3), ("no", 1)])})

    # ---- the money loop: 6 months of charges/payments, deposits, fees, and a
    # delinquency ladder with real cases at every stage. Ledger rows are built
    # in memory and saved once — per-row post() would rewrite the file 2,500
    # times. Every transaction still balances; the suite checks the invariant
    # on seeded data too.
    import hashlib as _hh
    charges, payments, ledger, turnovers = [], [], [], []

    def txn(entries, memo, kind, actor="human:mgr_1", at=None, subject=None):
        d = round(sum(e[1] for e in entries), 2); c = round(sum(e[2] for e in entries), 2)
        assert abs(d - c) < 0.005, memo
        ledger.append({"id": nid("txn"), "at": at or iso(), "memo": memo,
                       "actor": actor, "kind": kind, "subject": subject,
                       "entries": [{"account": a, "debit": dr, "credit": cr}
                                   for a, dr, cr in entries]})

    owner_of = {}
    for pr in props:
        owner_of[pr["id"]] = pr.get("owner_id", "unknown")

    # payer personas: reliable 84%, slow 10%, troubled 4%, delinquent 2%
    # A tenant surnamed like an owner must never be seeded delinquent: "Adam
    # Nakamura, 46 days behind" on the ladder next to owner "Nakamura Family
    # Trust" reads like the OWNER is behind on rent, and a demo audience will
    # trip on it every time. The name pool overlap itself is fine — a reliable
    # tenant Nakamura is just a name — so the fix caps the PERSONA, not the pool.
    owner_surnames = {w.rstrip(".") for o, *_ in OWNERS for w in o.split()
                      if w.rstrip(".") in LAST}
    def surname_clash(t):
        return t["name"].split()[-1] in owner_surnames

    persona = {}
    for t in tenants:
        r_ = R.random()
        kind = ("delinquent" if r_ < 0.02 else "troubled" if r_ < 0.06
                else "slow" if r_ < 0.16 else "reliable")
        if kind in ("delinquent", "troubled") and surname_clash(t):
            kind = "slow"
        persona[t["id"]] = kind
    # Deterministic anchors so EVERY seed size exercises the whole ladder:
    # the demo resident stays reliable (their rent card reads paid-up), one
    # tenant is missing this month (notice stage), one is two months gone
    # (referral stage). Anchors are drawn from tenants who DON'T share an
    # owner surname; the dice add more, these guarantee the floor.
    if len(tenants) >= 3:
        persona[tenants[0]["id"]] = "reliable"
        eligible = [t for t in tenants[1:] if not surname_clash(t)]
        if len(eligible) >= 2:
            persona[eligible[0]["id"]] = "troubled"
            persona[eligible[1]["id"]] = "delinquent"

    for u in units:
        tid = u.get("tenant_id")
        if not tid:
            continue
        oacct = f"owner:{owner_of[u['property_id']]}"
        # deposit held at move-in (one month's rent)
        t_row = next(x for x in tenants if x["id"] == tid)
        txn([("trust_cash", u["rent"], 0), (f"deposits:{tid}", 0, u["rent"])],
            f"security deposit held — {t_row['name']}", "deposit_held",
            at=t_row["move_in"], subject=tid)
        for mb in range(5, -1, -1):
            due = (t0 - timedelta(days=30 * mb)).replace(day=1)
            if parse(t_row["move_in"]) > due:
                continue
            mk = due.strftime("%Y-%m")
            charges.append({"id": nid("chg"), "unit_id": u["id"], "tenant_id": tid,
                            "month": mk, "amount": u["rent"], "due": iso(due),
                            "kind": "rent"})
            kind = persona[tid]
            skip = (kind == "delinquent" and mb <= 1) or                    (kind == "troubled" and mb == 0)
            if skip:
                continue
            delay = (R.randint(0, 4) if kind == "reliable"
                     else R.randint(6, 12) if kind == "slow" else R.randint(3, 9))
            paid_at = due + timedelta(days=delay)
            if paid_at > t0:
                continue
            payments.append({"id": nid("pay"), "tenant_id": tid, "unit_id": u["id"],
                             "amount": u["rent"], "method": R.choice(["ach", "ach", "check"]),
                             "at": iso(paid_at), "recorded_by": "human:mgr_1"})
            txn([("trust_cash", u["rent"], 0), (oacct, 0, u["rent"])],
                f"rent received — {t_row['name']} {mk}", "rent_received",
                at=iso(paid_at), subject=payments[-1]["id"])

    # maintenance bills paid out of trust for resolved work in the ledger
    # window — without these the statement said "maintenance $0" while the
    # owner report said $7,017, two surfaces disagreeing about the same month.
    ledger_start = t0 - timedelta(days=185)
    for r in requests:
        cost = r.get("actual_cost")
        done = r.get("resolved_at")
        if not cost or not done or parse(done) < ledger_start:
            continue
        txn([(f"owner:{owner_of[r['property_id']]}", cost, 0), ("trust_cash", 0, cost)],
            f"vendor invoice paid — {r.get('title', '')[:40]}", "expense_paid",
            at=done, subject=r["id"])

    # management fees per owner-month on collected rent (8%)
    for o in owners:
        o["mgmt_fee_pct"] = 0.08
        o["reserve_floor"] = 300 * len(o["properties"])
    coll = {}
    for t_ in ledger:
        if t_["kind"] != "rent_received":
            continue
        mk = t_["at"][:7]
        for e in t_["entries"]:
            if e["account"].startswith("owner:"):
                coll[(e["account"], mk)] = coll.get((e["account"], mk), 0) + e["credit"]
    for (acct, mk), amt in sorted(coll.items()):
        fee = round(amt * 0.08, 2)
        oid = acct.split(":", 1)[1]
        txn([(acct, fee, 0), ("trust_cash", 0, fee),
             ("operating_cash", fee, 0), ("fees_earned", 0, fee)],
            f"management fee 8% on ${amt:,.0f} — {mk}", "mgmt_fee",
            at=iso(parse(mk + "-28T12:00:00+00:00")), subject=f"{oid}:{mk}")

    # Historical owner draws, MONTHLY — the way owners actually take money.
    # The first version drew six months of accumulated balance in one August
    # transaction, which put "$807,178 in draws" on a single month's statement:
    # arithmetically consistent, narratively absurd. Each past month now closes
    # with a draw down to the reserve floor; the current month has no draw yet,
    # because that is exactly what the drafted disbursement batch is for.
    for o in owners:
        acct = f"owner:{o['id']}"
        for mb in range(5, 0, -1):   # past months only, oldest first
            mk = (t0 - timedelta(days=30 * mb)).strftime("%Y-%m")
            bal = 0.0
            for t_ in ledger:
                if t_["at"][:7] > mk:
                    continue
                for e in t_["entries"]:
                    if e["account"] == acct:
                        bal += e["credit"] - e["debit"]
            draw = round(bal - o["reserve_floor"], 2)
            if draw > 100:
                txn([(acct, draw, 0), ("trust_cash", 0, draw)],
                    f"owner disbursement — {o['name']} (ref SEED-{mk})",
                    "disbursement",
                    at=iso(parse(mk + "-28T15:00:00+00:00")), subject=o["id"])

    # ---- turnovers: 3 completed (the measured-vacancy floor), 1 mid-pipeline
    vac_units = [u for u in units if not u.get("tenant_id")]
    for i, days_vac in enumerate([24, 31, 41]):
        uu = R.choice(units)
        out_at = t0 - timedelta(days=R.randint(60, 240))
        turnovers.append({"id": nid("trn"), "unit_id": uu["id"],
                          "property_id": uu["property_id"], "tenant_id": None,
                          "state": "leased", "opened_at": iso(out_at - timedelta(days=14)),
                          "moveout_date": iso(out_at), "moved_out": iso(out_at),
                          "new_lease_start": iso(out_at + timedelta(days=days_vac)),
                          "vacancy_days": days_vac, "tasks": [],
                          "history": [{"state": "leased", "at": iso(out_at + timedelta(days=days_vac))}]})
    if vac_units:
        uu = vac_units[0]
        # Seeded one state BEFORE inspection on purpose: the inspection step is
        # what queues the deposit-disposition draft, and that must happen
        # through the real advance path (the journey suite drives it), never
        # by seeding its side-effects.
        turnovers.append({"id": nid("trn"), "unit_id": uu["id"],
                          "property_id": uu["property_id"], "tenant_id": None,
                          "state": "moveout_scheduled", "opened_at": iso(t0 - timedelta(days=9)),
                          "moveout_date": iso(t0 - timedelta(days=4)),
                          "tasks": [], "history": [{"state": "moveout_scheduled", "at": iso(t0 - timedelta(days=8))}]})

    # ---- vendor job tokens for every open assigned request
    for r in requests:
        if r.get("vendor_id") and r.get("status") in ("assigned", "in_progress"):
            r["vendor_token"] = nid("vtk")

    # ---- growth: owner referrals + leasing inquiries on vacant units.
    # Referrals are names handed over, nothing more — working them is a human's
    # job (and the Growth module's, later). Inquiries land FIFO with real
    # arrival times so the queue-position column has arithmetic behind it.
    referrals = [
        {"id": nid("ref"), "at": iso(t0 - timedelta(days=11)),
         "name": "Marcus Hale", "contact": "m.hale@example.com",
         "note": "Owns an 8-unit on Central Ave, self-managing and tired of it.",
         "source": f"owner:{owners[0]['id']}", "status": "contacted",
         "status_at": iso(t0 - timedelta(days=8))},
        {"id": nid("ref"), "at": iso(t0 - timedelta(days=2)),
         "name": "Dana Whitfield", "contact": "704-555-2214",
         "note": "Met at the CLT landlord meetup — 12 doors across Concord.",
         "source": "human:mgr_1", "status": "new"},
    ]
    inquiries = []
    if vac_units:
        prospect_rows = [
            ("Jordan Blake", "jordan.blake@example.com", "Looking for a 2bd, move in next month.", 6, "toured"),
            ("Sam Okoye", "704-555-8830", "Is the unit still available? Flexible on dates.", 4, "new"),
            ("Riley Chen", "riley.c@example.com", "Relocating for work, need something by the 1st.", 2, "new"),
            ("Casey Morgan", "704-555-1147", "Saw the listing — what utilities are included?", 1, "new"),
        ]
        for i, (name, contact, msg, days_ago, status) in enumerate(prospect_rows):
            uu = vac_units[i % len(vac_units)]
            inquiries.append({
                "id": nid("inq"), "at": iso(t0 - timedelta(days=days_ago,
                                                           hours=R.randint(0, 9))),
                "name": name, "contact": contact, "unit_id": uu["id"],
                "unit": uu["label"],
                "property": next(p["name"] for p in props if p["id"] == uu["property_id"]),
                "move_in": "", "message": msg, "status": status, "messages": [],
            })
        inquiries.sort(key=lambda x: x["at"])

    # ---- the Growth module: one manual prospect mid-pipeline (overdue on the
    # meeting cadence, so the nag and the proposal shell both demo live). The
    # two referrals above become prospects when the scout's first sweep imports
    # them — through the real path, never pre-seeded around it.
    prospects = [{
        "id": nid("pros"), "at": iso(t0 - timedelta(days=16)),
        "name": "Priya Raman", "contact": "priya.raman@example.com",
        "note": "15 doors in Ballantyne, self-managing with a spreadsheet; met "
                "at the CLT investor breakfast. Frustrated by vendor no-shows.",
        "source": {"kind": "manual", "by": "human:mgr_1"},
        "stage": "meeting", "stage_at": iso(t0 - timedelta(days=9)),
        "history": [
            {"stage": "recorded", "at": iso(t0 - timedelta(days=16))},
            {"stage": "researched", "at": iso(t0 - timedelta(days=15)), "by": "agent:scout"},
            {"stage": "first_touch_drafted", "at": iso(t0 - timedelta(days=15)), "by": "agent:scribe"},
            {"stage": "contacted", "at": iso(t0 - timedelta(days=13)), "by": "human:mgr_1"},
            {"stage": "meeting", "at": iso(t0 - timedelta(days=9)), "by": "human:mgr_1"}],
        "brief": None, "drafts": [], "nagged_on": None,
    }]
    # Sourced (cold) prospects — the prospecting side. Provenance is required
    # and recorded; the scout briefs them and the scribe drafts the COLD
    # first touch (opt-out line + address bracket) on the first sweep.
    _prov = "Mecklenburg County absentee-owner records pull, 2026-08 (demo data)"
    for name, contact, note in [
            ("Jo Delgado", "j.delgado@example.com",
             "Owns a 6-unit on Central Ave; tax mail goes to a Yourtown address."),
            ("Sam Whitcomb", "704-555-6120",
             "Two quadplexes in NoDa per the parcel roll; no PM of record.")]:
        prospects.append({
            "id": nid("pros"), "at": iso(t0 - timedelta(days=1)),
            "name": name, "contact": contact, "note": note,
            "source": {"kind": "sourced", "provenance": _prov, "by": "human:mgr_1"},
            "stage": "recorded", "stage_at": iso(t0 - timedelta(days=1)),
            "history": [{"stage": "recorded", "at": iso(t0 - timedelta(days=1))}],
            "brief": None, "drafts": [], "nagged_on": None})

    # ---- access codes (auth is optional; codes exist so it can be turned on).
    # Codes are stored hashed; the plaintext lives ONLY in demo_codes because
    # every person in this store is synthetic. A real deployment delivers codes
    # out-of-band and demo_codes does not exist.
    demo_codes, code_map = {}, {}
    def code_for(role, ident, name):
        c = f"{role[:2]}-{nid('x')[2:8]}"
        code_map[_hh.sha256(c.encode()).hexdigest()] = {"role": role, "id": ident, "name": name}
        return c
    demo_codes["staff"] = code_for("staff", "mgr_1", "Property Manager")
    for o in owners:
        demo_codes[o["name"]] = code_for("owner", o["id"], o["name"])
    demo_codes[tenants[0]["name"]] = code_for("tenant", tenants[0]["id"], tenants[0]["name"])

    cfg = {
        "org": "Keystone Residential",
        "manager": {"id": "mgr_1", "name": "Property Manager", "email": "pm@keystone.example.com"},
        "unit_count": len(units),
        "seeded_at": iso(),
        "spend_default_limit": 400,
        "quiet_hours": {"start": "21:00", "end": "07:30"},
        "after_hours_emergency_line": "704-555-0199",
        "credit_reporting": True,
        "seed_params": {"units": n_units, "months": months},
        "auth": {"secret": nid("sec") + nid("sec"), "codes": code_map,
                 "demo_codes": demo_codes,
                 "note": "demo_codes exists because everyone here is synthetic"},
        # The white-label one-pager link. The token IS the credential; rotating
        # it (staff console → Leads) revokes every copy in the wild.
        "share": {"performance_token": "shr_" + nid("x")[2:] + nid("x")[2:],
                  "created": iso()},
    }

    core.save("properties", props); core.save("units", units)
    core.save("tenants", tenants); core.save("owners", owners)
    core.save("vendors", vendors); core.save("components", components)
    core.save("requests", requests); core.save("events", events)
    core.save("surveys", surveys); core.save("messages", messages)
    core.save("approvals", []); core.save("config", cfg)
    core.save("charges", charges); core.save("payments", payments)
    core.save("ledger", ledger); core.save("batches", [])
    core.save("turnovers", turnovers)
    core.save("referrals", referrals); core.save("inquiries", inquiries)
    core.save("prospects", prospects)
    # An importer's findings must not outlive the data they describe.
    core.save("findings", [])

    return dict(properties=len(props), units=len(units), tenants=len(tenants),
                vendors=len(vendors), components=len(components),
                requests=len(requests), events=len(events), surveys=len(surveys),
                charges=len(charges), payments=len(payments),
                ledger_txns=len(ledger), turnovers=len(turnovers),
                referrals=len(referrals), inquiries=len(inquiries))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", type=int, default=220)
    ap.add_argument("--months", type=int, default=18)
    a = ap.parse_args()
    out = build(a.units, a.months)
    print("Seeded Property OS:")
    for k, v in out.items():
        print(f"  {k:<12} {v}")
    op = core.open_requests()
    print(f"\n  open requests {len(op)}")
    print(f"  avg resolution {core.avg_resolution_hours()}")
    print(f"  deflection    {core.deflection_savings()}")
    print(f"  automation    {core.automation_rate(core.load('events'))}")
