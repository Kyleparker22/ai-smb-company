#!/usr/bin/env python3
"""Fix OS — synthetic Reliable Appliance Service. Synthetic only."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(58)

FIRST = ["Renata", "Marcus", "Odell", "Priya", "Tomas", "Ingrid", "Sal", "Nadia", "Curt",
         "Bea", "Harlan", "Yuki", "Dee", "Franklin", "Marisol", "Ade"]
LAST = ["Voss", "Teel", "Okafor", "Lindqvist", "Barrera", "Mercado", "Havel", "Osei",
        "Pruitt", "Thorne", "Calloway", "Renner", "Iglesias", "Bostic", "Whitfield", "Yamada"]

# Invented manufacturers only. Kelmore / Arctica / HausWerk are the three we
# hold warranty authorization for; Bravanti / Coldspar are COD-only. The two
# recalled models (KD-450, HW-DR60) are deliberately NOT in the random pool —
# exactly the two explicit units below match the recall list.
MAKES = {
    "Kelmore":  [("KD-455", "dishwasher"), ("KR-310", "range"), ("KW-720", "washer")],
    "Arctica":  [("AR-2200", "refrigerator"), ("AF-90", "refrigerator")],
    "HausWerk": [("HW-DR61", "dryer"), ("HW-OV45", "range")],
    "Bravanti": [("BV-500", "washer"), ("BV-610", "dishwasher")],
    "Coldspar": [("CS-12", "refrigerator")],
}
FAILURE_CODES = ["F-12", "F-21", "F-31", "F-44", "F-52", "F-63"]
MESSAGES = [
    "any update on my refrigerator repair",
    "is the compressor part in yet",
    "my dryer won't heat, what would a repair cost",
    "the washer stopped spinning mid cycle",
    "our dishwasher won't drain",
    "what are your weekend hours",
]


def _name():
    return f"{rng.choice(FIRST)} {rng.choice(LAST)}"


def _symptom_for(appliance):
    opts = [k.split("|")[1] for k in core.DEFAULT_PARTS_MAP if k.startswith(appliance + "|")]
    return rng.choice(opts) if opts else "wont_start"


def _unit(i, make=None, model=None, appliance=None):
    make = make or rng.choice(list(MAKES))
    if model is None:
        model, appliance = rng.choice(MAKES[make])
    purchased = now() - timedelta(days=rng.randint(30, 1800))
    u = {"id": f"un_{i:03d}", "customer": _name(), "make": make, "model": model,
         "appliance": appliance,
         "serial": f"{make[:2].upper()}-{rng.randint(100000, 999999)}",
         "purchased_at": iso(purchased),
         "warranty_until": iso(purchased + timedelta(days=365)),
         "history": []}
    for _ in range(rng.choice([0, 0, 1, 1, 2])):
        sym = _symptom_for(appliance)
        parts = core.DEFAULT_PARTS_MAP.get(f"{appliance}|{sym}") or ["control board"]
        u["history"].append({"at": iso(now() - timedelta(days=rng.randint(60, 900))),
                             "symptom": sym, "parts_used": [rng.choice(parts)],
                             "note": "closed on first visit" if rng.random() < 0.7
                                     else "second visit for parts"})
    return u


def main():
    store.wipe()
    store.save("config", {"company": "Reliable Appliance Service", "techs": 5,
                          "warranty_makes": ["Kelmore", "Arctica", "HausWerk"]})

    units = [_unit(i) for i in range(400)]
    # Two units matching the recorded recall list — flagged, notice verbatim.
    units.append(_unit(900, make="Kelmore", model="KD-450", appliance="dishwasher"))
    units[-1]["id"] = "un_recall_1"
    units.append(_unit(901, make="HausWerk", model="HW-DR60", appliance="dryer"))
    units[-1]["id"] = "un_recall_2"
    # Demo: the fridge with a memory — its own history names the part to bring.
    units.append({"id": "un_demo_fridge", "customer": "Renata Voss", "make": "Arctica",
                  "model": "AR-2200", "appliance": "refrigerator", "serial": "AR-884210",
                  "purchased_at": iso(now() - timedelta(days=120)),
                  "warranty_until": iso(now() + timedelta(days=245)),
                  "history": [{"at": iso(now() - timedelta(days=60)),
                               "symptom": "not_cooling", "parts_used": ["start relay"],
                               "note": "replaced start relay; compressor tested OK"}],
                  "demo_tag": "demo"})
    store.save("units", units)
    store.save("customers", [{"id": f"cu_{i:03d}", "name": u["customer"]}
                             for i, u in enumerate(units[:300])])

    jobs = []
    for i in range(250):
        u = rng.choice(units[:400])
        kind = "warranty" if (u["make"] in ("Kelmore", "Arctica", "HausWerk")
                              and rng.random() < 0.5) else "cod"
        opened = now() - timedelta(days=rng.randint(0, 180))
        sym = _symptom_for(u["appliance"])
        work = [{"desc": "diagnostic", "amount": 90, "at": iso(opened)}]
        if rng.random() < 0.8:
            work.append({"desc": "parts + labor", "amount": rng.choice([120, 160, 190, 240]),
                         "at": iso(opened + timedelta(days=1))})
        total = round(sum(w["amount"] for w in work), 2)
        j = {"id": f"jb_{i:03d}", "unit_id": u["id"], "customer": u["customer"],
             "appliance": u["appliance"], "symptom": sym, "kind": kind,
             "opened_at": iso(opened), "work": work,
             "visits": 1 if rng.random() < 0.7 else 2}
        if kind == "cod":
            j["authorized_amount"] = total + rng.choice([0, 20, 50, 80])
        if rng.random() < 0.85:
            j["closed_at"] = iso(opened + timedelta(days=rng.randint(1, 5)))
        jobs.append(j)
    # Demo: a COD job sitting exactly at its recorded authorized amount.
    jobs.append({"id": "jb_demo_cod", "unit_id": None, "customer": "Marcus Teel",
                 "appliance": "washer", "symptom": "not_draining", "kind": "cod",
                 "authorized_amount": 280.0, "opened_at": iso(now() - timedelta(days=1)),
                 "visits": 1, "demo_tag": "demo",
                 "work": [{"desc": "diagnostic", "amount": 90,
                           "at": iso(now() - timedelta(days=1))},
                          {"desc": "drain pump + labor", "amount": 190,
                           "at": iso(now() - timedelta(hours=3))}]})
    # Demo: a COD job with headroom, so 'inside the authorization' is showable.
    jobs.append({"id": "jb_demo_cod_room", "unit_id": None, "customer": "Priya Osei",
                 "appliance": "dryer", "symptom": "no_heat", "kind": "cod",
                 "authorized_amount": 350.0, "opened_at": iso(now() - timedelta(days=2)),
                 "visits": 1, "demo_tag": "demo",
                 "work": [{"desc": "diagnostic", "amount": 90,
                           "at": iso(now() - timedelta(days=2))},
                          {"desc": "heating element", "amount": 120,
                           "at": iso(now() - timedelta(days=1))}]})
    store.save("jobs", jobs)

    claims = []
    for i in range(30):
        make = rng.choice(["Kelmore", "Arctica", "HausWerk"])
        model, appliance = rng.choice(MAKES[make])
        sym = _symptom_for(appliance)
        parts = [rng.choice(core.DEFAULT_PARTS_MAP.get(f"{appliance}|{sym}")
                            or ["control board"])]
        c = {"id": f"cl_{i:03d}", "make": make, "appliance": appliance, "symptom": sym,
             "diagnosis": f"{parts[0]} failed under load test",
             "failure_code": rng.choice(FAILURE_CODES), "parts": parts,
             "serial": f"{make[:2].upper()}-{rng.randint(100000, 999999)}",
             "purchase_proof_ref": f"POP-2026-{rng.randint(1000, 9999)}",
             "amount": rng.choice([140, 185, 240, 310, 395, 480]),
             "filed_at": iso(now() - timedelta(days=rng.randint(1, 60)))}
        c["narrative"] = (f"Unit presented with {sym.replace('_', ' ')}. Diagnosis: "
                          f"{c['diagnosis']}. Failure code {c['failure_code']}. Corrected by "
                          f"replacing: {', '.join(parts)}.")
        roll = rng.random()
        if roll < 0.20:
            c["serial"] = None                       # dies on a missing serial
        elif roll < 0.35:
            c["purchase_proof_ref"] = None           # dies on a missing proof ref
        elif roll < 0.60:
            c["submitted_at"] = iso(now() - timedelta(days=rng.randint(1, 30)))
            if rng.random() < 0.6:
                c["paid_at"] = iso(now() - timedelta(days=rng.randint(0, 20)))
        claims.append(c)
    claims.append({"id": "cl_demo_incomplete", "make": "Kelmore", "appliance": "range",
                   "symptom": "no_heat", "diagnosis": "igniter resistance out of spec",
                   "failure_code": "F-31", "parts": ["igniter"],
                   "serial": None, "purchase_proof_ref": None, "amount": 240,
                   "narrative": ("Unit presented with no heat. Diagnosis: igniter resistance "
                                 "out of spec. Failure code F-31. Corrected by replacing: "
                                 "igniter."),
                   "filed_at": iso(now() - timedelta(days=1)), "demo_tag": "demo"})
    claims.append({"id": "cl_demo_complete", "make": "Arctica", "appliance": "refrigerator",
                   "symptom": "not_cooling",
                   "diagnosis": "start relay open circuit; compressor OK under direct test",
                   "failure_code": "F-12", "parts": ["start relay"], "serial": "AR-884210",
                   "purchase_proof_ref": "POP-2026-0412", "amount": 315,
                   "narrative": ("Unit presented with not cooling. Diagnosis: start relay open "
                                 "circuit; compressor OK under direct test. Failure code F-12. "
                                 "Corrected by replacing: start relay."),
                   "filed_at": iso(now() - timedelta(days=2)), "demo_tag": "demo"})
    store.save("claims", claims)

    messages = [{"id": f"ms_{i:03d}", "from": _name(), "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(1, 72)))}
                for i, t in enumerate(MESSAGES * 2)]
    messages.append({"id": "ms_demo_gas", "from": "Ingrid Havel",
                     "text": "I smell gas when the oven is on",
                     "at": iso(now() - timedelta(minutes=15)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_fridge", "from": "Renata Voss",
                     "unit_id": "un_demo_fridge",
                     "text": "our fridge is not cooling and it's still under warranty",
                     "at": iso(now() - timedelta(minutes=35)), "demo_tag": "demo"})
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"units": len(units), "jobs": len(jobs), "claims": len(claims)})
    print(f"Seeded {len(units)} units, {len(jobs)} jobs, {len(claims)} claims, "
          f"{len(messages)} messages")


if __name__ == "__main__":
    main()
