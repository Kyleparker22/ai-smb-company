#!/usr/bin/env python3
"""Lab OS — synthetic Blue Finch Hospitality (5 fast-casual units). Synthetic only.

Seeds: 5 units, ~60 days of daily metric observations, one live experiment
mid-flight (below the floor), one concluded CLEAR, one concluded NOISE, ~30
86/stockout events (some paceless), the graveyard, and demo message fixtures
including the illness claim.
"""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(89)

UNITS = [("u_elm", "Elm Street"), ("u_depot", "Depot District"), ("u_river", "Riverside"),
         ("u_campus", "Campus"), ("u_north", "North Loop")]
ITEMS = [{"name": "brisket plate", "price": 14.0}, {"name": "finch bowl", "price": 12.0},
         {"name": "horchata", "price": 4.0}, {"name": "salsa flight", "price": 6.0},
         {"name": "guacamole", "price": 2.5}, {"name": "street corn esquites", "price": 5.0}]
PACE_ITEMS = {"brisket plate": 7, "finch bowl": 11, "horchata": 9, "salsa flight": 4}
DAYPARTS = ("lunch", "dinner")
CYCLE5 = (-0.6, -0.3, 0.0, 0.3, 0.6)
CYCLE_U = (-2, -1, 0, 1, 2)

ROUTINE = [
    ("gm", "who's winning the guac test"),
    ("gm", "any results on the menu board test yet"),
    ("gm", "how's the bundle experiment doing, can we call it"),
    ("gm", "we 86'd the brisket at 6pm again"),
    ("gm", "ran out of tortillas mid-dinner at riverside"),
    ("gm", "campus sold out of the salsa flight by 7"),
    ("gm", "north loop stocked out of horchata during the rush"),
    ("gm", "let's test $1 off bowls at elm street"),
    ("gm", "can we try a bigger portion on the campus tacos"),
    ("gm", "we should run a price test on horchata"),
    ("guest", "do you cater weddings?"),
    ("guest", "what time does depot district close"),
    ("guest", "loved the new patio at riverside"),
    ("guest", "can I book the back room saturday"),
    ("gm", "riverside ran out of guac mid lunch"),
    ("gm", "who's winning the bundle test so far"),
]


def _date(days_ago):
    return iso(now() - timedelta(days=days_ago))[:10]


def main():
    store.wipe()
    store.save("config", {"company": "Blue Finch Hospitality", "units": 5,
                          "concept": "fast casual",
                          "sample_floors": core.DEFAULT_FLOORS})
    store.save("units", [{"id": uid, "name": name} for uid, name in UNITS])
    store.save("items", ITEMS)

    # -- recorded sales pace: 5 readings per unit × item × daypart.
    #    (u_river, brisket plate, dinner) is pinned for the demo hand-check:
    #    median 8 units/hr × 2.5h × $14 = $280.
    pace = []
    for uid, _ in UNITS:
        for item, base in PACE_ITEMS.items():
            for dp in DAYPARTS:
                if (uid, item, dp) == ("u_river", "brisket plate", "dinner"):
                    readings = [6, 8, 7, 9, 8]
                else:
                    readings = [max(1, base + (dp == "dinner") * 2 + d)
                                for d in (-1, 0, 1, 0, -1)]
                for i, r in enumerate(readings):
                    pace.append({"unit_id": uid, "item": item, "daypart": dp,
                                 "units_per_hour": r, "date": _date(7 * i + 3)})
    store.save("pace_history", pace)

    # -- daily metric observations, ~60 days.
    obs = []
    all_units = [u for u, _ in UNITS]
    clear_treat = {"u_depot", "u_campus"}          # the concluded CLEAR bundle test
    # avg_ticket: every unit, 60 days. Treatment units read +$1.10 inside the window.
    for uid in all_units:
        for d in range(60):
            in_window = uid in clear_treat and 3 <= d <= 45
            base = 16.9 if in_window else 15.8
            obs.append({"id": store.nid("ob"), "unit_id": uid, "date": _date(d),
                        "metric": "avg_ticket", "item": None,
                        "value": round(base + CYCLE5[d % 5], 2)})
    # item_units (horchata): every unit, 60 days, same deterministic cycle both
    # arms — the concluded NOISE menu-board test.
    for uid in all_units:
        for d in range(60):
            obs.append({"id": store.nid("ob"), "unit_id": uid, "date": _date(d),
                        "metric": "item_units", "item": "horchata",
                        "value": 21 + CYCLE_U[d % 5]})
    # attach_rate (guacamole): 5 days so far — the live test, mid-flight.
    for uid in all_units:
        for d in range(5):
            tickets = rng.randint(36, 44)
            rate = 0.31 if uid in ("u_elm", "u_depot") else 0.22
            obs.append({"id": store.nid("ob"), "unit_id": uid, "date": _date(d),
                        "metric": "attach_rate", "item": "guacamole",
                        "value": round(tickets * rate), "n": tickets})
    store.save("observations", obs)

    # -- the three experiments. Floors recorded on each at creation.
    fl = core.DEFAULT_FLOORS
    exps = [
        {"id": "exp_demo_live",
         "hypothesis": "a register guac prompt lifts attach rate",
         "metric": "attach_rate", "item": "guacamole",
         "treatment_units": ["u_elm", "u_depot"],
         "control_units": ["u_river", "u_campus"], "status": "live",
         "started_at": iso(now() - timedelta(days=5)),
         "min_sample": {"n": fl["attach_rate"]["n"], "unit": fl["attach_rate"]["unit"],
                        "_source": fl["_source"]}},
        {"id": "exp_demo_clear",
         "hypothesis": "a taco + drink bundle at $1 off lifts average ticket",
         "metric": "avg_ticket", "item": None,
         "treatment_units": ["u_depot", "u_campus"],
         "control_units": ["u_elm", "u_river", "u_north"], "status": "concluded",
         "started_at": iso(now() - timedelta(days=45)),
         "concluded_at": iso(now() - timedelta(days=3)),
         "min_sample": {"n": fl["avg_ticket"]["n"], "unit": fl["avg_ticket"]["unit"],
                        "_source": fl["_source"]}},
        {"id": "exp_demo_noise",
         "hypothesis": "the new menu board layout lifts horchata units",
         "metric": "item_units", "item": "horchata",
         "treatment_units": ["u_north"],
         "control_units": ["u_elm", "u_river"], "status": "concluded",
         "started_at": iso(now() - timedelta(days=40)),
         "concluded_at": iso(now() - timedelta(days=5)),
         "min_sample": {"n": fl["item_units"]["n"], "unit": fl["item_units"]["unit"],
                        "_source": fl["_source"]}},
    ]
    store.save("experiments", exps)
    # freeze the concluded verdicts over their closed windows
    for eid in ("exp_demo_clear", "exp_demo_noise"):
        e = store.by_id("experiments", eid)
        e["verdict"] = core.verdict(e)
        store.upsert("experiments", e)

    # -- ~30 stockout / 86 events over 21 days; esquites has no pace history
    #    anywhere, so those rows read unmeasured (counted, never dollared).
    stockouts = []
    pool = list(PACE_ITEMS) + ["street corn esquites"]
    for i in range(30):
        item = pool[i % len(pool)]
        stockouts.append({"id": f"so_{i:03d}", "unit_id": rng.choice(all_units),
                          "item": item, "daypart": rng.choice(DAYPARTS),
                          "duration_hours": rng.choice([0.5, 1.0, 1.5, 2.0, 3.0]),
                          "at": iso(now() - timedelta(days=rng.randint(0, 20),
                                                      hours=rng.randint(0, 10)))})
    stockouts.append({"id": "so_demo_friday", "unit_id": "u_river", "item": "brisket plate",
                      "daypart": "dinner", "duration_hours": 2.5,
                      "at": iso(now() - timedelta(days=3)), "demo_tag": "demo"})
    store.save("stockouts", stockouts)

    # -- the menu graveyard: killed items with their recorded numbers.
    store.save("graveyard", [
        {"item": "birria ramen (LTO)", "killed_at": _date(94),
         "why": "labor-heavy; weekday units could not hold the spec",
         "recorded": {"avg_units_per_week": 41, "margin_pct": 18, "weeks_on_menu": 9}},
        {"item": "breakfast daypart", "killed_at": _date(150),
         "why": "sales never covered the 6am labor",
         "recorded": {"avg_units_per_week": 130, "margin_pct": 9, "weeks_on_menu": 14}},
        {"item": "$5 kids combo", "killed_at": _date(210),
         "why": "attached to nothing; discounted tickets that were coming anyway",
         "recorded": {"avg_units_per_week": 55, "margin_pct": 12, "weeks_on_menu": 22}},
    ])

    # -- messages: routine + demo fixtures (demo_tag rows are skipped by sweeps).
    messages = [{"id": f"ms_{i:03d}", "from_role": role,
                 "from": f"{role}-{rng.choice(['sam', 'dre', 'kat', 'leo'])}", "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(1, 96)))}
                for i, (role, t) in enumerate(ROUTINE)]
    messages += [
        {"id": "ms_demo_illness", "from_role": "guest", "from": "guest-jordan",
         "text": "your tacos made me sick last night and I want to talk to someone",
         "at": iso(now() - timedelta(minutes=25)), "demo_tag": "demo"},
        {"id": "ms_demo_gm", "from_role": "gm", "from": "gm-dre",
         "text": "who's winning the guac test",
         "at": iso(now() - timedelta(minutes=50)), "demo_tag": "demo"},
        {"id": "ms_demo_proposal", "from_role": "gm", "from": "gm-kat",
         "text": "let's test $1 off bowls at elm street",
         "at": iso(now() - timedelta(hours=2)), "demo_tag": "demo"},
        {"id": "ms_demo_86", "from_role": "gm", "from": "gm-leo",
         "text": "we 86'd the brisket at 6pm again at riverside",
         "at": iso(now() - timedelta(hours=3)), "demo_tag": "demo"},
    ]
    store.save("messages", messages)
    store.save("incidents", [])
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"units": len(UNITS), "observations": len(obs),
                     "stockouts": len(stockouts)})
    print(f"Seeded {len(UNITS)} units, {len(obs)} observations, {len(exps)} experiments, "
          f"{len(stockouts)} stockouts, {len(messages)} messages")


if __name__ == "__main__":
    main()
