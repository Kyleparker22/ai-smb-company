#!/usr/bin/env python3
"""Blackbox OS — synthetic Comfort First Mechanical. Synthetic only:
invented names, 555 phones, no real addresses."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(62)

LAST = ["Whitfield", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel", "Osei",
        "Delacroix", "Yamada", "Pruitt", "Calloway", "Bostic", "Renner", "Iglesias", "Thorne",
        "Ashby", "Kowalczyk", "Nakamura", "Fontaine", "Brubaker", "Silva", "Odum", "Vance"]
STREETS = ["Maple Ct", "Birchwood Dr", "Fenn Rd", "Cardinal Ln", "Old Mill Rd", "Juniper Way",
           "Harvest Bend", "Cooper St", "Larkspur Ave", "Quarry Rd"]
KINDS = ("furnace", "ac", "water_heater", "plumbing")
MESSAGES = [
    "how much does the maintenance membership cost",
    "can we schedule the spring tune-up",
    "what brands do you install",
    "do you sell air filters",
]


def _components(year_now):
    comps = []
    for kind in KINDS:
        if kind != "plumbing" and rng.random() < 0.08:
            continue  # not every home has every unit on record
        iy = rng.randint(1990, year_now - 1)
        if rng.random() < 0.12:
            iy = None  # the unrecorded age — reads UNKNOWN, prices provisional
        service = []
        for _ in range(rng.randint(0, 4)):
            service.append({"at": iso(now() - timedelta(days=rng.randint(30, 1800))),
                            "kind": "maintenance"})
        for _ in range(rng.choices([0, 1, 2, 3], weights=[70, 18, 8, 4])[0]):
            service.append({"at": iso(now() - timedelta(days=rng.randint(30, 1500))),
                            "kind": "callback"})
        comps.append({"kind": kind, "install_year": iy, "service": service})
    return comps


def main():
    store.wipe()
    store.save("config", {"company": "Comfort First Mechanical",
                          "trade": "HVAC + plumbing", "households": 1400,
                          "phone": "555-0140"})
    year = now().year

    homes = []
    for i in range(1400):
        homes.append({"id": f"hm_{i:04d}",
                      "owner": f"{rng.choice(LAST)}",
                      "address": f"{rng.randint(2, 980)} {rng.choice(STREETS)}",
                      "phone": f"555-{rng.randint(100, 999):03d}{rng.randint(0, 9)}",
                      "components": _components(year)})

    # -- demo fixtures (demo_tag: sweeps skip them; the demo buttons drive them)
    def comp(kind, iy, callbacks=0, cb_days=None):
        service = [{"at": iso(now() - timedelta(days=400)), "kind": "maintenance"}]
        for k in range(callbacks):
            service.append({"at": iso(now() - timedelta(days=(cb_days or [300, 500, 700])[k])),
                            "kind": "callback"})
        return {"kind": kind, "install_year": iy, "service": service}

    homes.append({"id": "hm_demo_full", "owner": "Renner", "address": "41 Maple Ct",
                  "phone": "555-0141", "demo_tag": "demo",
                  "components": [comp("furnace", year - 19), comp("ac", year - 7),
                                 comp("water_heater", year - 5), comp("plumbing", year - 28)]})
    homes.append({"id": "hm_demo_thin", "owner": "Osei", "address": "9 Quarry Rd",
                  "phone": "555-0142", "demo_tag": "demo",
                  "components": [comp("furnace", year - 6), comp("ac", year - 6),
                                 comp("water_heater", None), comp("plumbing", year - 12)]})
    homes.append({"id": "hm_demo_renew_up", "owner": "Havel", "address": "230 Old Mill Rd",
                  "phone": "555-0143", "demo_tag": "demo",
                  "components": [comp("furnace", year - 16), comp("ac", year - 12),
                                 comp("water_heater", year - 8), comp("plumbing", year - 30)]})
    homes.append({"id": "hm_demo_renew_down", "owner": "Mercer", "address": "77 Juniper Way",
                  "phone": "555-0144", "demo_tag": "demo",
                  "components": [comp("furnace", year - 11), comp("ac", year - 10),
                                 comp("water_heater", year - 4), comp("plumbing", year - 26)]})
    store.save("homes", homes)

    # -- members: locked at the quote their record produced at join
    members, n_renew_hist = [], 0
    candidates = [h for h in homes if not h.get("demo_tag")
                  and all(c.get("install_year") for c in h["components"])]
    rng.shuffle(candidates)
    for j, h in enumerate(candidates[:346]):
        q = core.membership_quote(h)
        joined = now() - timedelta(days=rng.randint(20, 700))
        m = {"id": f"mb_{j:04d}", "home_id": h["id"], "owner": h["owner"],
             "locked_price": q["monthly"], "factors_at_lock": q["factors"],
             "joined_at": iso(joined),
             "term_start": iso(joined),
             "term_end": iso(joined + timedelta(days=365 * (1 + (now() - joined).days // 365)))}
        # historical renewals for the honesty board — counted, some DOWN
        if rng.random() < 0.26 and (now() - joined).days > 380:
            drift = rng.choices([-6, -4, -2, 0, 2, 3, 6], weights=[8, 12, 10, 20, 20, 15, 15])[0]
            m["renewal_price"] = round(q["monthly"] + drift, 2)
            m["renewal_at"] = iso(now() - timedelta(days=rng.randint(10, 300)))
            m["renewal_direction"] = "down" if drift < 0 else "up" if drift > 0 else "flat"
            n_renew_hist += 1
        members.append(m)

    def lockf(pairs):
        return [{"label": lb, "dollars": float(d)} for lb, d in pairs]

    members.append({"id": "mb_demo_locked", "home_id": "hm_demo_full", "owner": "Renner",
                    "locked_price": 26.0, "demo_tag": "demo",
                    "factors_at_lock": lockf([("base plan", 18), ("furnace age", 9),
                                              ("ac age", 0), ("water_heater age", 0),
                                              ("plumbing age", 3), ("clean history", -4)]),
                    "joined_at": iso(now() - timedelta(days=120)),
                    "term_start": iso(now() - timedelta(days=120)),
                    "term_end": iso(now() + timedelta(days=245))})
    # locked two years ago at 24; the furnace has since crossed the 15-year band
    members.append({"id": "mb_demo_renew_up", "home_id": "hm_demo_renew_up", "owner": "Havel",
                    "locked_price": 24.0, "demo_tag": "demo",
                    "factors_at_lock": lockf([("base plan", 18), ("furnace age", 3),
                                              ("ac age", 2), ("water_heater age", 2),
                                              ("plumbing age", 3), ("clean history", -4)]),
                    "joined_at": iso(now() - timedelta(days=730)),
                    "term_start": iso(now() - timedelta(days=360)),
                    "term_end": iso(now() + timedelta(days=12))})
    # locked with a callback surcharge; the callbacks have since aged out of the window
    members.append({"id": "mb_demo_renew_down", "home_id": "hm_demo_renew_down",
                    "owner": "Mercer", "locked_price": 32.0, "demo_tag": "demo",
                    "factors_at_lock": lockf([("base plan", 18), ("furnace age", 3),
                                              ("ac age", 2), ("water_heater age", 0),
                                              ("plumbing age", 3), ("callback history", 6)]),
                    "joined_at": iso(now() - timedelta(days=740)),
                    "term_start": iso(now() - timedelta(days=362)),
                    "term_end": iso(now() + timedelta(days=10))})
    store.save("members", members)

    # -- messages
    messages = [{"id": f"ms_{i:03d}", "from": rng.choice(LAST), "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(1, 96)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages.append({"id": "ms_demo_gas", "from": "Trujillo",
                     "text": "i smell gas near the water heater",
                     "at": iso(now() - timedelta(minutes=8)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_noheat", "from": "Calloway",
                     "text": "we have no heat and it's 20 degrees outside",
                     "at": iso(now() - timedelta(minutes=25)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_fair", "from": "Renner", "home_id": "hm_demo_full",
                     "text": "why is my plan more than my neighbor's",
                     "at": iso(now() - timedelta(minutes=50)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_quote", "from": "Renner", "home_id": "hm_demo_full",
                     "text": "how much does the maintenance membership cost",
                     "at": iso(now() - timedelta(hours=2)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_thin_quote", "from": "Osei", "home_id": "hm_demo_thin",
                     "text": "can you quote me the plan for my house",
                     "at": iso(now() - timedelta(hours=3)), "demo_tag": "demo"})
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"homes": len(homes), "members": len(members)})
    print(f"Seeded {len(homes)} homes, {len(members)} members "
          f"({n_renew_hist} with a recorded renewal), {len(messages)} messages")


if __name__ == "__main__":
    main()
