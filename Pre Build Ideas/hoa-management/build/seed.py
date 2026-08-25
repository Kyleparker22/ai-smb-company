#!/usr/bin/env python3
"""Reserve OS — synthetic Northgate Community Management. Synthetic only.

14 associations, ~2,300 doors. One association has NO reserve study (the
UNKNOWABLE refusal), one has a stale study (every number flagged). All names,
units, and phone-shaped things are invented.
"""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(88)

LAST = ["Oyelaran", "Marchetti", "Solberg", "Ketterman", "Abreu", "Villanueva", "Prather",
        "Okonkwo", "Lindgren", "Castellano", "Whitby", "Nakagawa", "Ferreira", "Boudreaux",
        "Hollis", "Tavares", "Quimby", "Ashworth", "Delgadillo", "Munroe"]

RULES_POOL = [
    {"section": "§4.2", "title": "Trash containers stored out of view except collection day"},
    {"section": "§5.1", "title": "Exterior modifications require ARC approval before work begins"},
    {"section": "§6.3", "title": "No inoperable or unregistered vehicle parked in common view"},
    {"section": "§7.4", "title": "Pets leashed and attended in all common areas"},
    {"section": "§3.8", "title": "Holiday lighting removed within 30 days of the holiday"},
    {"section": "§8.1", "title": "Rentals under 30 days prohibited"},
    {"section": "§5.6", "title": "Lawns and beds maintained to the community standard"},
    {"section": "§9.2", "title": "Quiet hours 10pm–7am in all common areas"},
]

COMPONENT_POOL = [
    ("Roof replacement — all buildings", 18, 900_000),
    ("Asphalt overlay — private streets", 8, 330_000),
    ("Pool resurfacing & equipment", 6, 90_000),
    ("Exterior paint cycle", 7, 140_000),
    ("Elevator modernization", 20, 260_000),
    ("Perimeter fencing", 12, 75_000),
    ("Clubhouse HVAC", 10, 60_000),
    ("Irrigation mains", 15, 110_000),
]

ASSOC_NAMES = ["Briarwood Commons", "Larkspur Village", "Stonebridge Court",
               "Miramont Terrace", "Cedar Hollow", "Foxglove Green", "Harborview Mews",
               "Willow Bend", "Quailwood", "Saddle Creek", "Alder Pointe",
               "Rosemary Square", "Kestrel Ridge", "Bayberry Landing"]

MESSAGES = [
    "how do i reserve the clubhouse for a birthday party",
    "my pool fob stopped working",
    "when is the next board meeting",
    "i want to appeal the violation notice about my flag",
    "where do i find the approved paint colors",
]


def _study(components, years_old):
    return {"as_of": iso(now() - timedelta(days=int(years_old * 365.25))),
            "components": [{"name": n, "remaining_life_years": life, "replacement_cost": cost}
                           for n, life, cost in components]}


def _dues(reserve_monthly):
    return [
        {"label": "Reserve contribution", "monthly": reserve_monthly},
        {"label": "Landscaping contract", "monthly": rng.choice([28.0, 34.0, 41.0])},
        {"label": "Master insurance", "monthly": rng.choice([52.0, 61.0, 74.0])},
        {"label": "Water & common utilities", "monthly": rng.choice([22.0, 30.0, 37.0])},
        {"label": "Management fee", "monthly": rng.choice([18.0, 21.0, 24.0])},
    ]


def main():
    store.wipe()
    store.save("config", {
        "company": "Northgate Community Management",
        "associations": 14, "doors": 2300,
        "staleness_threshold_days": 1095,
        "inflation": dict(core.DEFAULT_INFLATION),
        "enforcement_policy": {
            "_source": "the recorded enforcement policy each board adopted — the ladder the "
                       "software may not skip",
            "ladder": ["courtesy", "notice", "hearing", "fine"],
            "min_days_between": 10},
    })

    associations = []
    # -- as_001 Briarwood Commons: the demo association, numbers crafted so the
    #    bands separate visibly (bear/base go negative years before bull).
    associations.append({
        "id": "as_001", "name": "Briarwood Commons", "doors": 220,
        "reserve_balance": 300_000, "monthly_contribution": 3_500,
        "reserve_study": _study([("Pool resurfacing & equipment", 3, 80_000),
                                 ("Asphalt overlay — private streets", 5, 330_000),
                                 ("Roof replacement — all buildings", 8, 900_000),
                                 ("Exterior paint cycle", 11, 120_000)], years_old=1.0),
        "rules": RULES_POOL[:6],
        "fine_schedule": {"_source": "fine schedule adopted by the Briarwood board, "
                                     "recorded 2025-03 — the only arithmetic a fine may use",
                          "amounts": {"1": 100, "2": 200, "3": 300}},
        "dues_line_items": _dues(52.0),
    })
    # -- as_002 Larkspur Village: well funded — the horizon sits beyond the window.
    associations.append({
        "id": "as_002", "name": "Larkspur Village", "doors": 180,
        "reserve_balance": 1_400_000, "monthly_contribution": 9_000,
        "reserve_study": _study([("Pool resurfacing & equipment", 4, 85_000),
                                 ("Exterior paint cycle", 6, 130_000),
                                 ("Perimeter fencing", 9, 70_000)], years_old=0.5),
        "rules": RULES_POOL[:5],
        "fine_schedule": {"_source": "fine schedule adopted by the Larkspur board, "
                                     "recorded 2024-11", "amounts": {"1": 75, "2": 150, "3": 250}},
        "dues_line_items": _dues(64.0),
    })
    # -- as_005 Cedar Hollow: NO reserve study on record → UNKNOWABLE.
    # -- as_006 Foxglove Green: a stale study (4.5 years old vs the 3-year threshold).
    for i, name in enumerate(ASSOC_NAMES[2:], start=3):
        aid = f"as_{i:03d}"
        comps = rng.sample(COMPONENT_POOL, rng.randint(3, 5))
        a = {"id": aid, "name": name, "doors": rng.choice([90, 120, 150, 175, 210]),
             "reserve_balance": rng.choice([180_000, 260_000, 420_000, 650_000]),
             "monthly_contribution": rng.choice([2_200, 3_100, 4_400, 6_000]),
             "rules": rng.sample(RULES_POOL, rng.randint(4, 7)),
             "fine_schedule": {"_source": f"fine schedule adopted by the {name} board, "
                                          f"recorded 2025",
                               "amounts": {"1": rng.choice([50, 100]), "2": 200, "3": 300}},
             "dues_line_items": _dues(rng.choice([38.0, 47.0, 55.0]))}
        if name == "Cedar Hollow":
            a["reserve_study"] = None          # UNKNOWABLE — no study, no adequacy claim
        elif name == "Foxglove Green":
            a["reserve_study"] = _study(comps, years_old=4.5)   # stale — everything flags
        else:
            a["reserve_study"] = _study(comps, years_old=rng.uniform(0.5, 2.5))
        associations.append(a)
    store.save("associations", associations)

    # -- homeowners (a roster for the demo association, a few elsewhere)
    homeowners = []
    for i in range(14):
        homeowners.append({"id": f"ho_{i:03d}", "name": f"{rng.choice(LAST)}",
                           "unit": f"{rng.randint(1, 24)}{rng.choice('ABCD')}",
                           "association_id": "as_001",
                           "phone": f"555-01{rng.randint(10, 99)}"})
    homeowners.append({"id": "ho_demo", "name": "Renata Oyelaran", "unit": "14B",
                       "association_id": "as_001", "phone": "555-0144"})
    for i in range(14, 40):
        homeowners.append({"id": f"ho_{i:03d}", "name": f"{rng.choice(LAST)}",
                           "unit": f"{rng.randint(1, 30)}{rng.choice('ABCD')}",
                           "association_id": rng.choice(associations)["id"],
                           "phone": f"555-02{rng.randint(10, 99)}"})
    store.save("homeowners", homeowners)

    # -- violations: ~120 across the ladder, every one created THROUGH the
    #    structural path (rule resolved against the association's recorded list)
    store.save("violations", [])
    stages = ["courtesy"] * 5 + ["notice"] * 3 + ["hearing"] * 2 + ["fine"] * 1 + ["closed"] * 1
    made = 0
    while made < 120:
        assoc = rng.choice(associations)
        rule = rng.choice(assoc["rules"])
        r = core.create_violation(
            assoc["id"], f"{rng.randint(1, 30)}{rng.choice('ABCD')}", rule["section"],
            rng.choice(["trash containers at the curb since monday",
                        "unapproved storm door installed",
                        "boat trailer in the guest lot two weeks",
                        "dog off leash at the north lawn",
                        "string lights still up in february",
                        "lawn past the community standard",
                        "loud gathering past quiet hours"]),
            photo_ref=f"ph_{made:04d}.jpg", offense_n=rng.choice([1, 1, 1, 2, 3]))
        v = r["violation"]
        target = rng.choice(stages)
        idx = ["courtesy", "notice", "hearing", "fine", "closed"].index(target)
        if target == "closed":
            idx = 0                     # cured at courtesy — no intermediate rungs
        for s in ["notice", "hearing"][: max(0, min(idx, 2))]:
            v["stage"] = s
            v["history"].append({"at": iso(), "stage": s})
        if target == "fine":
            v["stage"] = "fine"
            fine = core.scheduled_fine(assoc, v["offense_n"])
            v["fine_amount"], v["fine_basis"] = fine["amount"], fine["basis"]
            v["history"].append({"at": iso(), "stage": "fine", "by": "human:board"})
        if target == "closed":
            v["stage"] = "closed"
            v["closed_reason"] = "cured after courtesy"
            v["history"].append({"at": iso(), "stage": "closed"})
        v["opened_at"] = iso(now() - timedelta(days=rng.randint(1, 180)))
        store.upsert("violations", v)
        made += 1
    # a real (non-demo) violation on the demo homeowner's own unit, so the
    # homeowner door has something of hers to show
    r = core.create_violation("as_001", "14B", "§3.8",
                              "string lights still up in february",
                              photo_ref="ph_demo_14b.jpg", offense_n=1)

    # -- demo fixtures (demo_tag: skipped by counts and sweeps)
    core.create_violation("as_001", "7C", "§4.2",
                          "trash containers at the curb since monday",
                          photo_ref="ph_demo_7c.jpg", offense_n=2, demo_tag="demo")
    vios = store.load("violations")
    vd = vios[-1]
    vd["id"] = "vi_demo_courtesy"
    store.save("violations", vios)
    core.create_violation("as_001", "22A", "§6.3",
                          "boat trailer in the guest lot two weeks",
                          photo_ref="ph_demo_22a.jpg", offense_n=1, demo_tag="demo")
    vios = store.load("violations")
    vh = vios[-1]
    vh["id"] = "vi_demo_hearing"
    vh["stage"] = "hearing"
    vh["history"].append({"at": iso(), "stage": "notice"})
    vh["history"].append({"at": iso(), "stage": "hearing"})
    store.save("violations", vios)

    # -- messages
    messages = []
    for i, t in enumerate(MESSAGES * 2):
        messages.append({"id": f"ms_{i:03d}", "from": rng.choice(LAST), "text": t,
                         "association_id": rng.choice(("as_001", "as_002", "as_003")),
                         "at": iso(now() - timedelta(hours=rng.randint(1, 96)))})
    messages.append({"id": "ms_demo_safety", "from": "Renata Oyelaran",
                     "association_id": "as_001",
                     "text": "the stairwell railing is loose",
                     "at": iso(now() - timedelta(minutes=12)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_dues", "from": "Renata Oyelaran",
                     "association_id": "as_001",
                     "text": "why did my dues go up this year",
                     "at": iso(now() - timedelta(minutes=35)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_appeal", "from": "Marchetti",
                     "association_id": "as_001",
                     "text": "i want to appeal the violation notice about my flag",
                     "at": iso(now() - timedelta(hours=2)), "demo_tag": "demo"})
    store.save("messages", messages)
    store.save("approvals", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"associations": len(associations), "violations": len(store.load("violations")),
                     "homeowners": len(homeowners)})
    print(f"Seeded {len(associations)} associations, {len(homeowners)} homeowners, "
          f"{len(store.load('violations'))} violations, {len(messages)} messages")


if __name__ == "__main__":
    main()
