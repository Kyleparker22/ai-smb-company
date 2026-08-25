#!/usr/bin/env python3
"""Key OS — synthetic Ironclad Lock & Access. Synthetic only (555 phones)."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(74)

FIRST = ["Dana", "Marcus", "Priya", "Elena", "Tomas", "Ruth", "Omar", "Sylvie", "Grant",
         "Noor", "Felix", "Ida", "Cole", "Marisol", "Viktor", "June"]
LAST = ["Whitcomb", "Okonkwo", "Raghavan", "Bergstrom", "Calloway", "Ferreira", "Nakash",
        "Trudeau", "Iverson", "Delgado", "Ostrowski", "Meline", "Barreto", "Hyland",
        "Quiroga", "Sandoval"]
STREETS = ["Alder Ct", "Birchwood Ln", "Copper Ridge Rd", "Dunmore Ave", "Ellery St",
           "Foxglove Dr", "Granite Way", "Harbor Point Blvd", "Ivywood Ter", "Juniper Loop"]
SITES = ["Harborview Professional Center", "Brookfield Office Park", "Lakeside Medical Annex",
         "Foundry Row Lofts", "Cypress Gate Apartments", "Meridian Logistics Hub",
         "Old Mill Business Center", "Summit Ridge Storage", "Pinehurst Academy",
         "Cannonside Marina Offices"]
KEYWAYS = ["SC1", "SC4", "KW1", "KW5", "WR3", "BE2"]
ROUTINE_MESSAGES = [
    "I'm locked out of my house",
    "how much to rekey a 3 bedroom house with 5 locks",
    "what time do you open saturday",
    "do you sell safes",
]


def _name():
    return f"{rng.choice(FIRST)} {rng.choice(LAST)}"


def _address():
    return f"{rng.randint(10, 999)} {rng.choice(STREETS)}"


def main():
    store.wipe()
    store.save("config", {"company": "Ironclad Lock & Access", "vans": 4,
                          "phone": "555-0148", "rate_card": core.DEFAULT_RATE_CARD})

    # -- ~30 master-key systems, each with named authorizers and an append-only history
    systems, registry = [], []
    for i in range(30):
        site = SITES[i % len(SITES)] + ("" if i < len(SITES) else f" — bldg {i // len(SITES) + 1}")
        authorizers = sorted({_name() for _ in range(rng.randint(1, 3))})
        s = {"id": f"sys_{i:03d}", "site": site, "keyway": rng.choice(KEYWAYS),
             "doors": rng.randint(8, 120), "authorizers": authorizers}
        systems.append(s)
        for n in range(rng.randint(1, 4)):
            registry.append({"id": f"rg_{i:03d}_{n}", "system_id": s["id"],
                             "at": iso(now() - timedelta(days=rng.randint(30, 900))),
                             "change": rng.choice(["system commissioned", "key issued",
                                                   "key revoked", "cylinder added",
                                                   "sub-master cut"]),
                             "authorized_by": rng.choice(authorizers),
                             "key_code": f"{s['keyway']}-{rng.randint(10000, 99999)}",
                             "supersedes": None})
    registry.sort(key=lambda r: r["at"])
    store.save("systems", systems)
    store.save("registry", registry)

    # -- authorization records: many addresses recorded, some DELIBERATELY without
    authorizations, recorded_addresses = [], []
    for i in range(60):
        addr = _address()
        if addr == "14 Alder Ct":  # deliberately unrecorded — the unverifiable demo
            addr = "15 Alder Ct"
        recorded_addresses.append(addr)
        authorizations.append({"id": f"au_{i:03d}", "address": addr, "name": _name(),
                               "role": rng.choice(["owner_of_record", "manager_of_record"]),
                               "verified_acts": rng.choice([["id_seen", "deed_shown"],
                                                            ["id_seen", "lease_shown"],
                                                            ["id_seen"]]),
                               "recorded_at": iso(now() - timedelta(days=rng.randint(10, 700)))})
    # the demo authority: recorded, verified, ready to dispatch against
    authorizations.append({"id": "au_demo", "address": "412 Birchwood Ln",
                           "name": "Dana Whitcomb", "role": "owner_of_record",
                           "verified_acts": ["id_seen", "deed_shown"],
                           "recorded_at": iso(now() - timedelta(days=200))})
    store.save("authorizations", authorizations)
    # 14 Alder Ct deliberately has NO record — the unverifiable demo path.

    # -- ~250 historical jobs, closed with authorization ref + card citation
    jobs = []
    for i in range(250):
        kind = rng.choice(["lockout_auto", "lockout_residential", "lockout_commercial",
                           "rekey", "unlock", "access_control_service"])
        card_item = {"rekey": "rekey_base", "unlock": "lockout_residential"}.get(kind, kind)
        j = {"id": f"jb_{i:03d}", "kind": kind, "address": rng.choice(recorded_addresses),
             "customer": _name(), "card_item": card_item,
             "after_hours": rng.random() < 0.25,
             "opened_at": iso(now() - timedelta(days=rng.randint(0, 180)))}
        if kind in ("rekey", "unlock", "lockout_residential", "lockout_commercial"):
            j["authorization_ref"] = rng.choice(authorizations[:-1])["id"]
        if rng.random() < 0.9:
            j["closed_at"] = iso(now() - timedelta(days=rng.randint(0, 170)))
        jobs.append(j)
    # a job with no references — the close refusal demo
    jobs.append({"id": "jb_demo_norefs", "kind": "rekey", "address": "88 Granite Way",
                 "customer": "Felix Ostrowski", "opened_at": iso(now() - timedelta(days=2)),
                 "demo_tag": "demo"})
    store.save("jobs", jobs)

    # -- access-control service clocks (bounded ladder)
    clocks = []
    for i in range(12):
        clocks.append({"id": f"ck_{i:03d}", "site": systems[i]["site"],
                       "kind": rng.choice(["battery", "firmware", "audit_export"]),
                       "interval_days": rng.choice([90, 180, 365]),
                       "last_done_at": iso(now() - timedelta(days=rng.randint(10, 400))),
                       "touches": []})
    clocks.append({"id": "ck_demo_due", "site": "Meridian Logistics Hub", "kind": "battery",
                   "interval_days": 90,
                   "last_done_at": iso(now() - timedelta(days=140)), "touches": []})
    clocks.append({"id": "ck_demo_exhausted", "site": "Summit Ridge Storage",
                   "kind": "firmware", "interval_days": 90,
                   "last_done_at": iso(now() - timedelta(days=300)),
                   "touches": [{"at": iso(now() - timedelta(days=d)), "kind": "drafted"}
                               for d in (60, 40, 20)]})
    clocks.append({"id": "ck_demo_skip", "site": "Pinehurst Academy", "kind": "battery",
                   "interval_days": 90, "last_done_at": iso(now() - timedelta(days=200)),
                   "touches": [], "demo_tag": "demo"})
    store.save("clocks", clocks)

    # -- messages: routine traffic + the demo fixtures
    messages = [{"id": f"ms_{i:03d}", "from": _name(), "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(1, 72)))}
                for i, t in enumerate(ROUTINE_MESSAGES * 3)]
    messages += [
        {"id": "ms_demo_hotcar", "from": "Marisol Delgado", "phone": "555-0119",
         "text": "my toddler is locked in the car and it's hot, please hurry",
         "at": iso(now() - timedelta(minutes=5)), "demo_tag": "demo"},
        {"id": "ms_demo_rekey_auth", "from": "Dana Whitcomb", "phone": "555-0126",
         "text": "I need the house rekeyed after my roommate moved out",
         "address": "412 Birchwood Ln",
         "at": iso(now() - timedelta(minutes=30)), "demo_tag": "demo"},
        {"id": "ms_demo_rekey_noauth", "from": "Grant Hyland", "phone": "555-0163",
         "text": "just bought the place and want all the locks changed today",
         "address": "14 Alder Ct",
         "at": iso(now() - timedelta(minutes=45)), "demo_tag": "demo"},
        {"id": "ms_demo_master", "from": systems[0]["authorizers"][0], "phone": "555-0177",
         "text": f"we need to add a key to the master system at {systems[0]['site']}",
         "system_id": systems[0]["id"],
         "at": iso(now() - timedelta(hours=1)), "demo_tag": "demo"},
        {"id": "ms_demo_quote", "from": "June Barreto", "phone": "555-0184",
         "text": "how much to rekey a 3 bedroom house with 5 locks", "cylinders": 5,
         "at": iso(now() - timedelta(hours=2)), "demo_tag": "demo"},
    ]
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"systems": len(systems), "jobs": len(jobs)})
    print(f"Seeded {len(systems)} master systems, {len(registry)} registry records, "
          f"{len(authorizations)} authorization records, {len(jobs)} jobs, "
          f"{len(clocks)} service clocks, {len(messages)} messages")


if __name__ == "__main__":
    main()
