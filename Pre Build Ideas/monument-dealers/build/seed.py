#!/usr/bin/env python3
"""Stone OS — synthetic Hartwell Memorials. Synthetic only: invented names,
555 numbers, no real people, no real cemeteries."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(51)

LAST = ["Merrow", "Okonkwo", "Vasquez", "Lindgren", "Abernathy", "Toussaint", "Kowalski",
        "Delgado", "Fairweather", "Nakamura", "Bristow", "Calloway", "Ostrander", "Reyes",
        "Whitlock", "Sorensen", "Padgett", "Iverson"]
FIRST = ["Eleanor", "Walter", "Ruth", "Harold", "Margaret", "Clarence", "Dorothy", "Ernest",
         "Beatrice", "Raymond", "Lucille", "Vernon", "Mabel", "Chester", "Opal", "Rosalind"]

CEMETERIES = [
    ("cem_001", "Cedar Rest Memorial Gardens"), ("cem_002", "St. Brigid Cemetery"),
    ("cem_003", "Oakhaven Cemetery"), ("cem_004", "Willow Creek Memorial Park"),
    ("cem_005", "Mount Solace Cemetery"), ("cem_006", "Evergreen Hill Cemetery"),
    ("cem_007", "Riverbend Memorial Gardens"), ("cem_008", "Holy Cross Cemetery"),
    ("cem_009", "Prairie View Cemetery"), ("cem_010", "Lakeside Memorial Park"),
    ("cem_011", "Fairfield Cemetery"), ("cem_012", "Chapel Ridge Cemetery"),
    ("cem_norules1", "Old Pioneer Burial Ground"),
    ("cem_norules2", "Maple Bend Township Cemetery"),
]

FINISHES = ["polished", "steeled", "rock pitch"]

MESSAGES = [
    "when will my father's headstone be set",
    "what do we still owe on the headstone",
    "how much does a granite companion monument cost",
    "what are your hours on saturday",
]

STAGE_WEIGHTS = [("contract", 8), ("cemetery_approval", 14), ("proof", 18), ("engraving", 16),
                 ("foundation", 10), ("cure", 12), ("setting", 12)]


def _pick_stage():
    total = sum(w for _, w in STAGE_WEIGHTS)
    r = rng.randint(1, total)
    for s, w in STAGE_WEIGHTS:
        r -= w
        if r <= 0:
            return s
    return "proof"


def main():
    store.wipe()
    store.save("config", {"company": "Hartwell Memorials", "showrooms": 1,
                          "phone": "(555) 010-8871", "cemeteries_served": len(CEMETERIES)})

    cemeteries = []
    for i, (cid, name) in enumerate(CEMETERIES):
        row = {"id": cid, "name": name, "contact": f"(555) 01{i:02d}-{rng.randint(1000, 9999)}"}
        if not cid.startswith("cem_norules"):
            row["rules"] = {
                "max_height_in": rng.choice([36, 42, 48, 54, 60]),
                "base_required": rng.random() < 0.8,
                "finishes": rng.sample(FINISHES, rng.randint(2, 3)),
                "approval_form": f"Form MC-{rng.randint(2, 9)}",
                "cure_days": rng.choice([21, 28, 28, 30, 35]),
                "_source": (f"recorded from the {name} rules sheet, "
                            f"dated 2026-0{rng.randint(3, 7)}-{rng.randint(10, 28)}"),
            }
        cemeteries.append(row)
    store.save("cemeteries", cemeteries)

    families = [{"id": f"fa_{i:03d}", "name": rng.choice(LAST),
                 "phone": f"(555) 0{rng.randint(10, 99)}-{rng.randint(1000, 9999)}"}
                for i in range(220)]
    store.save("families", families)

    orders, proofs = [], []
    ruled = [c for c in cemeteries if c.get("rules")]
    for i in range(300):
        fam, first = rng.choice(LAST), rng.choice(FIRST)
        cem = rng.choice(ruled) if rng.random() < 0.9 else rng.choice(cemeteries)
        price = rng.choice([2400, 3200, 4100, 5600, 7800])
        birth = rng.randint(1928, 1962)
        active = i < 90                      # ~90 active, the rest set & complete
        stage = _pick_stage() if active else "set"
        clock = core.STAGE_CLOCK_DAYS.get(stage, 30)
        entered = now() - timedelta(days=rng.randint(1, int(clock * 1.5)) if active
                                    else rng.randint(8, 400))
        o = {"id": f"or_{i:03d}", "family_name": fam,
             "deceased_name": f"{first} {fam}",
             "inscription": {"name": f"{first} {fam}", "birth_year": birth,
                             "death_year": rng.randint(2024, 2026),
                             "epitaph": rng.choice(["Forever in our hearts", "At rest",
                                                    "Beloved and remembered", ""])},
             "cemetery_id": cem["id"], "stage": stage, "stage_entered_at": iso(entered),
             "monument": {"type": rng.choice(["upright", "slant", "flat marker", "companion"]),
                          "height_in": rng.choice([24, 30, 36, 42]),
                          "base": rng.random() < 0.9, "finish": rng.choice(FINISHES)},
             "price": price, "deposit_paid": round(price * 0.5, 2), "balance_due": 0}
        idx = core.STAGES.index(stage)
        if idx >= core.STAGES.index("engraving"):
            # past the proof gate → the family approval is on the record
            p = {"id": f"pr_{i:03d}", "order_id": o["id"],
                 "inscription_text": f"{first} {fam} · {birth}–{o['inscription']['death_year']}",
                 "rendered_at": iso(entered - timedelta(days=rng.randint(5, 30))),
                 "approval": {"by": f"{rng.choice(FIRST)} {fam}",
                              "signature_ref": f"SIG-{rng.randint(1000, 9999)}",
                              "at": iso(entered - timedelta(days=rng.randint(1, 5))),
                              "recorded_by": "showroom"}}
            proofs.append(p)
            o["proof_id"] = p["id"]
        elif stage == "proof":
            p = {"id": f"pr_{i:03d}", "order_id": o["id"],
                 "inscription_text": f"{first} {fam} · {birth}–{o['inscription']['death_year']}",
                 "rendered_at": iso(entered), "approval": None}
            proofs.append(p)
            o["proof_id"] = p["id"]
        if idx >= core.STAGES.index("foundation"):
            o["cemetery_approval_at"] = iso(entered - timedelta(days=rng.randint(20, 60)))
        if idx >= core.STAGES.index("cure"):
            o["foundation_poured_at"] = iso(entered - timedelta(days=rng.randint(0, 20)))
        if stage == "set":
            o["set_at"] = iso(entered)
            if rng.random() < 0.25:          # the quiet leak: final balances uncollected
                o["balance_due"] = round(price * 0.5, 2)
                if rng.random() < 0.3:
                    o["balance_touches"] = [{"at": iso(now() - timedelta(days=rng.randint(20, 40))),
                                             "kind": "drafted"}]
            else:
                o["balance_paid_at"] = iso(entered + timedelta(days=rng.randint(1, 21)))
                o["balance_paid_amount"] = round(price * 0.5, 2)
        elif active:
            o["balance_due"] = round(price * 0.5, 2)
            if rng.random() < 0.35 and stage in ("cemetery_approval", "proof", "engraving"):
                o["blocker"] = rng.choice(core.BLOCKERS) if rng.random() < 0.75 else None
        orders.append(o)

    # -- demo fixtures (demo_tag rows; sweeps skip them)
    orders.append({"id": "or_demo_typo", "family_name": "Merrow",
                   "deceased_name": "Katharine A. Merrow",
                   "inscription": {"name": "Katharine A. Merrow", "birth_year": 1941,
                                   "death_year": 2026, "epitaph": "Beloved mother"},
                   "cemetery_id": "cem_001", "stage": "proof",
                   "stage_entered_at": iso(now() - timedelta(days=6)),
                   "monument": {"type": "upright", "height_in": 36, "base": True,
                                "finish": "polished"},
                   "price": 5600, "deposit_paid": 2800, "balance_due": 2800,
                   "proof_id": "pr_demo_typo", "demo_tag": "demo"})
    proofs.append({"id": "pr_demo_typo", "order_id": "or_demo_typo",
                   "inscription_text": "Katherine A. Merrow · 1942–2026",   # both wrong
                   "rendered_at": iso(now() - timedelta(days=6)), "approval": None,
                   "demo_tag": "demo"})
    orders.append({"id": "or_demo_precure", "family_name": "Okonkwo",
                   "deceased_name": "Walter Okonkwo",
                   "cemetery_id": "cem_002", "stage": "cure",
                   "stage_entered_at": iso(now() - timedelta(days=10)),
                   "cemetery_approval_at": iso(now() - timedelta(days=25)),
                   "foundation_poured_at": iso(now() - timedelta(days=10)),
                   "monument": {"type": "upright", "height_in": 42, "base": True,
                                "finish": "steeled"},
                   "price": 4100, "deposit_paid": 2050, "balance_due": 2050,
                   "demo_tag": "demo"})
    orders.append({"id": "or_demo_noca", "family_name": "Vasquez",
                   "deceased_name": "Ruth Vasquez",
                   "cemetery_id": "cem_003", "stage": "foundation",
                   "stage_entered_at": iso(now() - timedelta(days=45)),
                   "foundation_poured_at": iso(now() - timedelta(days=45)),
                   "monument": {"type": "slant", "height_in": 30, "base": True,
                                "finish": "polished"},
                   "price": 3200, "deposit_paid": 1600, "balance_due": 1600,
                   "demo_tag": "demo"})
    orders.append({"id": "or_demo_norules", "family_name": "Lindgren",
                   "deceased_name": "Harold Lindgren",
                   "cemetery_id": "cem_norules1", "stage": "cemetery_approval",
                   "stage_entered_at": iso(now() - timedelta(days=30)),
                   "monument": {"type": "upright", "height_in": 48, "base": True,
                                "finish": "rock pitch"},
                   "price": 5600, "deposit_paid": 2800, "balance_due": 2800,
                   "demo_tag": "demo"})
    orders.append({"id": "or_demo_ready", "family_name": "Abernathy",
                   "deceased_name": "Margaret Abernathy",
                   "cemetery_id": "cem_004", "stage": "setting",
                   "stage_entered_at": iso(now() - timedelta(days=5)),
                   "cemetery_approval_at": iso(now() - timedelta(days=70)),
                   "foundation_poured_at": iso(now() - timedelta(days=50)),
                   "monument": {"type": "companion", "height_in": 36, "base": True,
                                "finish": "polished"},
                   "price": 7800, "deposit_paid": 3900, "balance_due": 3900,
                   "demo_tag": "demo"})
    orders.append({"id": "or_demo_balance", "family_name": "Toussaint",
                   "deceased_name": "Clarence Toussaint",
                   "cemetery_id": "cem_005", "stage": "set",
                   "stage_entered_at": iso(now() - timedelta(days=40)),
                   "set_at": iso(now() - timedelta(days=40)),
                   "monument": {"type": "upright", "height_in": 36, "base": True,
                                "finish": "steeled"},
                   "price": 3600, "deposit_paid": 1800, "balance_due": 1800,
                   "demo_tag": "demo"})
    store.save("orders", orders)
    store.save("proofs", proofs)

    messages = [{"id": f"ms_{i:03d}", "from": rng.choice(LAST), "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(1, 72)))}
                for i, t in enumerate(MESSAGES * 3)]
    messages.append({"id": "ms_demo_proof", "from": "Dana Merrow",
                     "order_id": "or_demo_typo",
                     "text": "the date on the proof is wrong, my mother was born in 1941 "
                             "not 1942",
                     "at": iso(now() - timedelta(minutes=20)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_timeline", "from": "Sam Okonkwo",
                     "order_id": "or_demo_precure",
                     "text": "when will my father's headstone be set",
                     "at": iso(now() - timedelta(minutes=50)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_balance", "from": "Renee Toussaint",
                     "order_id": "or_demo_balance",
                     "text": "what do we still owe on the headstone",
                     "at": iso(now() - timedelta(hours=2)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_inquiry", "from": "Joan Fairweather",
                     "text": "my husband passed away last month and we need a headstone",
                     "at": iso(now() - timedelta(hours=4)), "demo_tag": "demo"})
    store.save("messages", messages)
    store.save("corrections", [])
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"orders": len(orders), "cemeteries": len(cemeteries)})
    print(f"Seeded {len(families)} families, {len(orders)} orders, {len(cemeteries)} "
          f"cemeteries ({sum(1 for c in cemeteries if not c.get('rules'))} with no recorded "
          f"rules), {len(proofs)} proofs, {len(messages)} messages")


if __name__ == "__main__":
    main()
