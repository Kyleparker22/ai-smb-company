#!/usr/bin/env python3
"""Crew OS — synthetic janitorial company. `python3 seed.py`.

"Northstar Building Services" — ~85 contracts, night crews with per-building
access, reports incl. every security type, inspections on some contracts only.
Synthetic only.
"""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(21)

BUILDINGS = ["Alder Medical Plaza", "Bramble Corporate Center", "Cedarbrook Bank", "Dove Hollow Law",
             "Elmcrest Tech Campus", "Foxglove Dental", "Gladehill Logistics", "Harvest Credit Union",
             "Ivystone Offices", "Juniper Schools Admin"]
CREW_NAMES = ["Marisol V.", "Deshawn P.", "Priya K.", "Kenji T.", "Elena R.", "Marcus B.",
              "Tanya O.", "Cole H.", "Nina D.", "Omar S.", "Reese L.", "Sawyer M."]
REPORTS = [
    "found the back door unlocked when we arrived",
    "what's the alarm code for the medical building?",
    "restrooms on 3 weren't done last night per the client",
    "we're out of liners and low on towels at the bank",
    "crew got done early, all good tonight",
    "trash was missed in the corner offices again",
]


def main():
    store.wipe()
    store.save("config", {"company": "Northstar Building Services", "revenue": "$5.5M",
                          "contracts": 85, "comms": "modelled, not connected"})

    contracts = []
    for i in range(85):
        contracts.append({"id": f"ct_{i:03d}", "name": f"{rng.choice(BUILDINGS)} #{i:02d}",
                          "value_month": rng.choice([1800, 2600, 3400, 5200, 8800])})

    crew = []
    for i, name in enumerate(CREW_NAMES * 3):
        member = {"id": f"cw_{i:03d}", "name": f"{name}{i//12 or ''}",
                  "access": [c["id"] for c in rng.sample(contracts, rng.randint(2, 8))],
                  "out_tonight": rng.random() < 0.12}
        member["assigned"] = [cid for cid in member["access"] if rng.random() < 0.5]
        crew.append(member)

    # make a few contracts genuinely uncovered tonight: nobody assigned
    assigned_all = {cid for m in crew for cid in m["assigned"]}
    uncovered = [c for c in contracts if c["id"] not in assigned_all]

    inspections = []
    for c in rng.sample(contracts, 50):  # only ~60% have a recent inspection
        inspections.append({"id": store.nid("in"), "contract_id": c["id"],
                            "at": iso(now() - timedelta(days=rng.randint(1, 13))),
                            "score": round(rng.uniform(3.4, 5.0), 1)})
    for c in rng.sample(contracts, 20):  # stale ones outside the window
        inspections.append({"id": store.nid("in"), "contract_id": c["id"],
                            "at": iso(now() - timedelta(days=rng.randint(30, 90))),
                            "score": round(rng.uniform(3.0, 5.0), 1)})

    reports = [{"id": f"rp_{i:03d}", "contract_id": rng.choice(contracts)["id"], "text": t,
                "at": iso(now() - timedelta(hours=rng.randint(2, 30)))}
               for i, t in enumerate(REPORTS * 3)]
    # demo rows: a security report, an access ask, a complaint on an uninspected contract
    no_insp = next(c for c in contracts
                   if not any(i["contract_id"] == c["id"] for i in inspections))
    reports.append({"id": "rp_demo_sec", "contract_id": contracts[0]["id"],
                    "text": "found the back door unlocked when we arrived",
                    "at": iso(now() - timedelta(minutes=30)), "demo_tag": "demo"})
    reports.append({"id": "rp_demo_access", "contract_id": contracts[1]["id"],
                    "text": "can you text me the lockbox combo for suite 200",
                    "at": iso(now() - timedelta(minutes=40)), "demo_tag": "demo"})
    reports.append({"id": "rp_demo_complaint", "contract_id": no_insp["id"],
                    "text": "restrooms on 3 weren't done last night per the client",
                    "at": iso(now() - timedelta(hours=1)), "demo_tag": "demo"})

    store.save("contracts", contracts)
    store.save("crew", crew)
    store.save("inspections", inspections)
    store.save("reports", reports)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"contracts": len(contracts), "crew": len(crew),
                     "uncovered_tonight": len(uncovered)})
    print(f"Seeded {len(contracts)} contracts, {len(crew)} crew, {len(inspections)} inspections, "
          f"{len(reports)} reports ({len(uncovered)} contracts uncovered tonight)")


if __name__ == "__main__":
    main()
