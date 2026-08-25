#!/usr/bin/env python3
"""Flue OS — synthetic Hearthstone Chimney Co. Synthetic only: invented names,
555 phones. ~1,900 households with per-chimney history."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(56)

FIRST = ["Ada", "Bram", "Cleo", "Dov", "Edie", "Fern", "Gus", "Hattie", "Ira", "June",
         "Kip", "Lena", "Milo", "Nora", "Otis", "Pearl", "Quinn", "Rosa", "Sy", "Tess",
         "Uma", "Vern", "Willa", "Yusuf", "Zora"]
LAST = ["Ashcroft", "Bellamy", "Cormier", "Draper", "Eastman", "Fairweather", "Granger",
        "Holloway", "Ibarra", "Jessup", "Kowalski", "Lockhart", "Mabry", "Naylor",
        "Ostrander", "Pemberton", "Quimby", "Rutledge", "Sandoval", "Thackeray",
        "Umberg", "Vandermeer", "Wexler", "Yancey", "Zellner"]
STREETS = ["Alder Ln", "Birch Hollow Rd", "Chestnut Ridge", "Dover Ct", "Elmwood Ave",
           "Foxglove Way", "Granite St", "Hemlock Dr", "Juniper Pass", "Kettle Creek Rd"]
TECHS = [{"id": "tech_dana", "name": "Dana Okafor"},
         {"id": "tech_ray", "name": "Ray Mabry"},
         {"id": "tech_luz", "name": "Luz Sandoval"}]
FLUE_KINDS = ["masonry fireplace", "prefab fireplace", "wood-stove insert", "furnace flue"]
LINERS = ["clay tile, sound", "clay tile, hairline cracks noted", "stainless reline 2021", "unlined"]
CAPS = ["cap sound", "cap missing", "cap rusted through", "cap and crown sound"]
CLEAN_FINDINGS = [
    "light first-stage soot, brushed clean",
    "cap and crown sound, no water intrusion",
    "damper operates freely, seals well",
    "firebox mortar joints intact",
    "second-stage flake creosote removed by rotary brush",
    "smoke chamber parged, draft normal",
]
HAZARD_FINDINGS = [
    "Stage 3 glazed creosote across the smoke chamber and the first three flue tiles; "
    "flue partially blocked at the damper. Do not use this fireplace until it is remediated.",
    "Flue blocked by collapsed tile and nesting debris at the second joint; no draft path. "
    "Do not use this appliance until the blockage is cleared and the liner verified.",
    "Active CO spillage at the appliance connector under draft test; connector corroded "
    "through. Do not operate this furnace flue until the connector is replaced.",
]
STAGE3_TEXT = HAZARD_FINDINGS[0]

MESSAGES = [
    "need to schedule our annual sweep",
    "how much for a new chimney cap",
    "is my invoice paid up",
    "do you sell firewood",
    "price to reline the flue",
]


def _phone():
    return f"(555) {rng.randint(200, 999)}-{rng.randint(1000, 9999)}"


def _household(i, ref):
    name = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
    hh = {"id": f"hh_{i:04d}", "name": name,
          "address": f"{rng.randint(3, 980)} {rng.choice(STREETS)}",
          "phone": _phone(), "flue": rng.choice(FLUE_KINDS),
          "liner": rng.choice(LINERS), "cap": rng.choice(CAPS)}
    r = rng.random()
    if r < 0.45:                       # current — inside the annual
        age = rng.randint(10, 330)
    elif r < 0.80:                     # the due slice
        age = rng.randint(370, 520)
    elif r < 0.95:                     # the overdue/lapsed slice
        age = rng.randint(521, 1100)
    else:                              # no record at all
        age = None
    if age is not None:
        svc = ref - timedelta(days=age)
        hh["last_sweep"] = iso(svc)
        if rng.random() < 0.6:
            findings = [{"text": t, "hazard": False}
                        for t in rng.sample(CLEAN_FINDINGS, rng.randint(1, 3))]
            if rng.random() < 0.03:
                findings.append({"text": rng.choice(HAZARD_FINDINGS), "hazard": True,
                                 "photo": f"IMG_{rng.randint(1000, 9999)}"})
            hh["inspections"] = [{"level": rng.choice([1, 1, 1, 1, 1, 1, 2, 2, 2, 3]),
                                  "date": iso(svc), "tech": rng.choice(TECHS)["name"],
                                  "findings": findings}]
    return hh


def main():
    ref = now()
    store.wipe()
    store.save("config", {
        "company": "Hearthstone Chimney Co.", "techs": 3, "households": 1900,
        "jobs_per_tech_day": 5, "avg_ticket": 289,
        "price_book": {"sweep": 289, "level2_inspection": 189, "cap": 450, "reline": 3200},
        "off_season_discount": {"pct": 15,
                                "_source": "recorded February off-season rate, set by the "
                                           "operator 2026-08"},
        "level3_rule": core.DEFAULT_LEVEL3_RULE,
    })
    store.save("techs", TECHS)

    households = [_household(i, ref) for i in range(1900)]

    # -- demo fixtures (demo_tag: excluded from boards, sweeps, and counts)
    households.append({
        "id": "hh_demo_l2", "name": "Marisol Vega", "address": "12 Kettle Creek Rd",
        "phone": "(555) 555-0141", "flue": "masonry fireplace",
        "liner": "clay tile, sound", "cap": "cap and crown sound",
        "last_sweep": iso(ref - timedelta(days=90)),
        "inspections": [{"level": 2, "date": iso(ref - timedelta(days=90)),
                         "tech": "Dana Okafor",
                         "findings": [{"text": "light first-stage soot, brushed clean",
                                       "hazard": False},
                                      {"text": "cap and crown sound, no water intrusion",
                                       "hazard": False}]}],
        "demo_tag": "demo"})
    households.append({
        "id": "hh_demo_none", "name": "Pete Callahan", "address": "77 Granite St",
        "phone": "(555) 555-0177", "flue": "prefab fireplace",
        "liner": "unlined", "cap": "cap missing", "demo_tag": "demo"})
    households.append({
        "id": "hh_demo_stage3", "name": "Ruth Ellison", "address": "5 Foxglove Way",
        "phone": "(555) 555-0105", "flue": "masonry fireplace",
        "liner": "clay tile, hairline cracks noted", "cap": "cap rusted through",
        "last_sweep": iso(ref - timedelta(days=30)),
        "inspections": [{"level": 2, "date": iso(ref - timedelta(days=30)),
                         "tech": "Luz Sandoval",
                         "findings": [{"text": "damper operates freely, seals well",
                                       "hazard": False},
                                      {"text": STAGE3_TEXT, "hazard": True,
                                       "photo": "IMG_0231"}]}],
        "demo_tag": "demo"})
    store.save("households", households)

    messages = [{"id": f"ms_{i:03d}", "from": rng.choice(households[:1900])["name"],
                 "text": t, "at": iso(ref - timedelta(hours=rng.randint(1, 72)))}
                for i, t in enumerate(MESSAGES * 2)]
    messages.append({"id": "ms_demo_co", "from": "Pete Callahan",
                     "text": "the carbon monoxide alarm keeps going off and we feel dizzy",
                     "at": iso(ref - timedelta(minutes=12)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_burn", "from": "Marisol Vega",
                     "text": "is it safe to use the fireplace this winter",
                     "at": iso(ref - timedelta(minutes=25)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_burn_none", "from": "Pete Callahan",
                     "text": "safe to burn this year? we just moved in",
                     "at": iso(ref - timedelta(minutes=31)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_burn_stage3", "from": "Ruth Ellison",
                     "text": "is it safe to burn in the fireplace this season",
                     "at": iso(ref - timedelta(minutes=44)), "demo_tag": "demo"})
    messages.append({"id": "ms_demo_fire", "from": "Marisol Vega",
                     "text": "we had a chimney fire last night, the fire department came",
                     "at": iso(ref - timedelta(minutes=58)), "demo_tag": "demo"})
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"households": len(households), "messages": len(messages)})
    db = core.due_board()
    print(f"Seeded {len(households)} households ({db['due']} due for annual, "
          f"{db['no_record']} with no record), {len(TECHS)} techs, "
          f"{len(messages)} messages")


if __name__ == "__main__":
    main()
