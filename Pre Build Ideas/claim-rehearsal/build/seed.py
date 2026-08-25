#!/usr/bin/env python3
"""Rehearsal OS — synthetic Hargrove Insurance Group. Synthetic only:
invented carriers, invented insureds, 555 claim lines. Nothing here is real."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(65)

FIRST = ["Rosalind", "Dario", "Maeve", "Toshi", "Ansel", "Priya", "Colm", "Zora", "Hugh",
         "Ines", "Barrett", "Lucia", "Emeric", "Sana", "Wendell", "Petra"]
LAST = ["Merrow", "Vetch", "Okonkwo", "Lindgren", "Trask", "Abellard", "Havel", "Osei",
        "Delacroix", "Yamashiro", "Pruitt", "Calloway", "Bostic", "Renner", "Iglesias",
        "Thorne", "Quarles", "Madrigal", "Fenn", "Solberg"]
CARRIERS = [("Kestrel Mutual", "1-800-555-0134"), ("Bluewater P&C", "1-800-555-0177"),
            ("Sable National", "1-800-555-0119"), ("Piedmont Underwriters", "1-800-555-0152")]

# per-type exclusion pool — each names its form and the scenario(s) it strikes
EXCLUSION_POOL = {
    "homeowner": [
        {"name": "Cooking-equipment grease fire exclusion", "form_ref": "HX 21 44",
         "scenarios": ["kitchen_fire"], "peril": "contents", "p": 0.12},
        {"name": "Loss-of-use limitation endorsement", "form_ref": "HX 30 06",
         "scenarios": ["kitchen_fire"], "peril": "loss_of_use", "p": 0.08},
        {"name": "Water backup exclusion", "form_ref": "WB 01 08",
         "scenarios": ["water_backup"], "peril": "water_backup", "p": 0.18},
    ],
    "contractor": [
        {"name": "Tools-left-in-vehicle exclusion", "form_ref": "IM 08 22",
         "scenarios": ["tool_theft"], "peril": "tools_equipment", "p": 0.25},
        {"name": "Your-work exclusion", "form_ref": "CG 22 94",
         "scenarios": ["faulty_work_damage"], "peril": "completed_operations", "p": 0.20},
    ],
    "restaurant": [
        {"name": "Grease-duct cleaning warranty exclusion", "form_ref": "RP 14 02",
         "scenarios": ["grease_fire"], "peril": "property", "p": 0.22},
        {"name": "Assault & battery exclusion", "form_ref": "CG 24 06",
         "scenarios": ["patron_slip"], "peril": "general_liability", "p": 0.15},
    ],
}

MESSAGES = [
    "is water backup on our policy",
    "can you quote our home and auto, we're shopping around",
    "what's our deductible on the homeowners",
    "thanks for the holiday card, see you at the game",
]


def _coverages(t):
    if t == "homeowner":
        dwelling = rng.choice([200000, 260000, 320000, 380000, 450000])
        ded = rng.choice([1000, 2500, 5000])
        covs = [{"peril": "dwelling_fire", "limit": dwelling, "deductible": ded},
                {"peril": "contents", "limit": int(dwelling * 0.3), "deductible": ded},
                {"peril": "loss_of_use", "limit": int(dwelling * 0.2), "deductible": ded},
                {"peril": "personal_liability",
                 "limit": rng.choice([100000, 300000, 500000]), "deductible": 0}]
        if rng.random() < 0.55:
            covs.append({"peril": "water_backup", "limit": rng.choice([5000, 10000, 25000]),
                         "deductible": 1000})
        return covs
    if t == "contractor":
        covs = [{"peril": "general_liability", "limit": 1000000, "deductible": 0}]
        if rng.random() < 0.70:
            covs.append({"peril": "tools_equipment",
                         "limit": rng.choice([15000, 30000, 60000]), "deductible": 1000})
        if rng.random() < 0.60:
            covs.append({"peril": "completed_operations", "limit": 500000, "deductible": 0})
        return covs
    covs = [{"peril": "property", "limit": rng.choice([300000, 500000, 900000]),
             "deductible": rng.choice([2500, 5000])},
            {"peril": "general_liability", "limit": 1000000, "deductible": 0}]
    if rng.random() < 0.65:
        covs.append({"peril": "business_income", "limit": rng.choice([100000, 200000, 300000]),
                     "deductible": 0})
    if rng.random() < 0.50:
        covs.append({"peril": "spoilage", "limit": rng.choice([10000, 25000]),
                     "deductible": 500})
    return covs


def main():
    store.wipe()
    store.save("config", {"agency": "Hargrove Insurance Group", "producers": 3, "csrs": 4,
                          "scenarios": core.DEFAULT_SCENARIOS,
                          "rate_card": core.DEFAULT_RATE_CARD,
                          "demo_probes": {
                              "fear": ("Without this endorsement a kitchen fire would be "
                                       "devastating — you could lose everything, God forbid "
                                       "it happens at night. A real nightmare."),
                              "promise": ("Good news — you're fully covered for a water "
                                          "backup, don't worry about a thing."),
                          }})

    accounts, unread = [], 0
    for i in range(900):
        t = rng.choices(["homeowner", "contractor", "restaurant"],
                        weights=[0.60, 0.25, 0.15])[0]
        carrier, line = rng.choice(CARRIERS)
        recorded = rng.random() >= 0.08
        a = {"id": f"ac_{i:04d}",
             "insured": f"{rng.choice(FIRST)} {rng.choice(LAST)}",
             "type": t, "carrier": carrier, "carrier_claim_line": line,
             "premium": rng.randint(12, 180) * 100,
             "renewal": iso(now() + timedelta(days=rng.randint(5, 365))),
             "policy_recorded": recorded, "endorsements": []}
        if recorded:
            a["coverages"] = _coverages(t)
            a["exclusions"] = [dict((k, v) for k, v in e.items() if k != "p")
                               for e in EXCLUSION_POOL[t] if rng.random() < e["p"]]
        else:
            unread += 1
            a["coverages"], a["exclusions"] = [], []
        accounts.append(a)

    # demo fixture: the full rehearsal account — kitchen fire, two named
    # exclusions, typical gap exactly $41,000 (hand-checkable arithmetic:
    # 77,000 × .5 = 38,500 paid on dwelling, minus the 2,500 deductible;
    # contents 23,100 and loss-of-use 15,400 both excluded → gap 41,000).
    accounts.append({
        "id": "ac_demo_full", "insured": "Rosalind Merrow", "type": "homeowner",
        "carrier": "Kestrel Mutual", "carrier_claim_line": "1-800-555-0134",
        "premium": 2400, "renewal": iso(now() + timedelta(days=38)),
        "policy_recorded": True, "demo_tag": "demo", "endorsements": [],
        "coverages": [
            {"peril": "dwelling_fire", "limit": 300000, "deductible": 2500},
            {"peril": "contents", "limit": 90000, "deductible": 2500},
            {"peril": "loss_of_use", "limit": 60000, "deductible": 2500},
            {"peril": "personal_liability", "limit": 100000, "deductible": 0},
        ],  # deliberately NO water_backup coverage — the third gap
        "exclusions": [
            {"name": "Cooking-equipment grease fire exclusion", "form_ref": "HX 21 44",
             "scenarios": ["kitchen_fire"], "peril": "contents"},
            {"name": "Loss-of-use limitation endorsement", "form_ref": "HX 30 06",
             "scenarios": ["kitchen_fire"], "peril": "loss_of_use"},
        ]})
    # demo fixture: the UNREADABLE account — policy detail never recorded
    accounts.append({
        "id": "ac_demo_unread", "insured": "Dario Vetch", "type": "contractor",
        "carrier": "Sable National", "carrier_claim_line": "1-800-555-0119",
        "premium": 8400, "renewal": iso(now() + timedelta(days=25)),
        "policy_recorded": False, "demo_tag": "demo", "endorsements": [],
        "coverages": [], "exclusions": []})
    store.save("accounts", accounts)

    messages = [{"id": f"ms_{i:03d}",
                 "from": f"{rng.choice(FIRST)} {rng.choice(LAST)}", "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(1, 72)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages.append({"id": "ms_demo_active", "from": "Rosalind Merrow",
                     "text": "my basement is flooding right now what do i do",
                     "at": iso(now() - timedelta(minutes=12)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_rehearse", "from": "Rosalind Merrow",
                     "text": "what would a kitchen fire actually cost us out of pocket",
                     "at": iso(now() - timedelta(minutes=45)), "demo_tag": "demo"})
    store.save("messages", messages)
    store.save("rehearsals", [])
    store.save("claims", [])
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"accounts": len(accounts), "unread_policies": unread})
    print(f"Seeded {len(accounts)} accounts ({unread} with unread policies — "
          f"{unread / 900:.1%}), {len(messages)} messages")


if __name__ == "__main__":
    main()
