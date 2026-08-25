#!/usr/bin/env python3
"""Lot OS — synthetic Crossroads Auto Group. Synthetic only."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(41)

LAST = ["Whitfield", "Barrera", "Okafor", "Lindqvist", "Trujillo", "Mercer", "Havel", "Osei",
        "Delacroix", "Yamada", "Pruitt", "Calloway", "Bostic", "Renner", "Iglesias", "Thorne"]
CARS = ["2019 Civic LX", "2018 F-150 XLT", "2020 Camry SE", "2017 Altima SV",
        "2019 Silverado LT", "2021 CR-V EX"]
LEADS = [
    "is the blue civic still available",
    "what would payments be with 2k down",
    "has the altima been in an accident",
    "what time do you close today",
]


def main():
    store.wipe()
    store.save("config", {"company": "Crossroads Auto Group", "lots": 2,
                          "floorplan_daily_cost": 9.5,
                          "trade_book": {"accord": [9800, 10400, 11200, 11800, 12500],
                                         "f150": [18200, 19500, 21000, 22400, 24100]}})

    units = []
    for i in range(140):
        has_report = rng.random() < 0.85
        u = {"id": f"un_{i:03d}", "desc": rng.choice(CARS),
             "acquired_at": iso(now() - timedelta(days=rng.randint(3, 130)))}
        if has_report:
            u["history_report"] = {"source": "AutoRecord", "date": iso(now() - timedelta(days=rng.randint(5, 60))),
                                   "summary": rng.choice(["no reported accidents, 2 owners, service records present",
                                                          "one reported minor rear impact 2022, repaired, clean title",
                                                          "clean title, fleet history, highway miles"])}
        if rng.random() < 0.3:
            u["sold_at"] = iso(now() - timedelta(days=rng.randint(0, 30)))
        units.append(u)
    units.append({"id": "un_demo_report", "desc": "2019 Civic LX",
                  "acquired_at": iso(now() - timedelta(days=95)),
                  "history_report": {"source": "AutoRecord",
                                     "date": iso(now() - timedelta(days=10)),
                                     "summary": "one reported minor rear impact 2022, repaired, clean title"},
                  "demo_tag": "demo"})
    units.append({"id": "un_demo_noreport", "desc": "2017 Altima SV",
                  "acquired_at": iso(now() - timedelta(days=40)), "demo_tag": "demo"})
    store.save("units", units)

    leads = [{"id": f"ld_{i:03d}", "from": rng.choice(LAST), "text": t,
              "at": iso(now() - timedelta(hours=rng.randint(1, 96)))}
             for i, t in enumerate(LEADS * 3)]
    leads.append({"id": "ld_demo_lead", "from": "Renner", "unit_id": "un_demo_report",
                  "text": "is the blue civic still available",
                  "at": iso(now() - timedelta(minutes=8)), "demo_tag": "demo"})
    leads.append({"id": "ld_demo_cond", "from": "Pruitt", "unit_id": "un_demo_noreport",
                  "text": "has the altima been in an accident",
                  "at": iso(now() - timedelta(minutes=25)), "demo_tag": "demo"})
    leads.append({"id": "ld_demo_pay", "from": "Osei",
                  "text": "what would payments be with 2k down",
                  "at": iso(now() - timedelta(minutes=40)), "demo_tag": "demo"})
    leads.append({"id": "ld_demo_trade", "from": "Havel", "model_key": "accord",
                  "text": "what's my 2018 accord worth on trade",
                  "at": iso(now() - timedelta(minutes=55)), "demo_tag": "demo"})
    store.save("leads", leads)

    deals = [
        {"id": "dl_demo_notitle", "unit_id": "un_demo_report", "buyer": "Renner",
         "title_status": None, "demo_tag": "demo"},
        {"id": "dl_demo_titled", "unit_id": "un_001", "buyer": "Mercer",
         "title_status": "in_hand",
         "lender_terms": {"apr": 8.9, "months": 60, "amount": 14500}, "demo_tag": "demo"},
    ]
    store.save("deals", deals)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None, {"units": len(units)})
    print(f"Seeded {len(units)} units, {len(leads)} leads, {len(deals)} deals")


if __name__ == "__main__":
    main()
