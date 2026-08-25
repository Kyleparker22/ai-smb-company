#!/usr/bin/env python3
"""Rebid OS — synthetic Ridgeway Precision Machining. Synthetic only."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(68)

CLASSES = {"3-axis mill": 4, "5-axis mill": 2, "lathe": 4, "wire EDM": 2}
RATES = {"3-axis mill": 68, "5-axis mill": 105, "lathe": 62, "wire EDM": 88}
MACHINE_NAMES = {
    "3-axis mill": ["Haas VF-4 #1", "Haas VF-4 #2", "Haas VF-2", "Brother Speedio"],
    "5-axis mill": ["DMU 50", "Matsuura MX-330"],
    "lathe": ["Okuma LB3000 #1", "Okuma LB3000 #2", "Haas ST-20", "Citizen L20"],
    "wire EDM": ["Sodick VL400Q #1", "Sodick VL400Q #2"],
}
PARTS = ["clamp plate", "manifold block", "pump housing", "spindle shaft", "gear blank",
         "valve body", "sensor bracket", "impeller", "bearing cap", "tooling plate",
         "nozzle", "adapter flange", "stop block", "cam follower", "guide rail",
         "piston", "yoke", "spacer", "bushing", "end cap"]
MATERIALS = ["6061", "7075", "303 SS", "17-4", "1018", "brass", "Ti-6Al-4V", "4140"]
BUYERS = ["Halvorsen Controls", "Brixton Hydraulics", "Coyle Aerospace Sub-Tier",
          "Marden Pump Co", "Delfino Automation", "Krieger Tool & Die",
          "Sable Valve Works", "Pinehurst Instruments", "Ostrander Conveyor",
          "Ruckman Marine", "Tellico Robotics", "Vantage Ag Equipment"]
CONTACTS = ["Dana", "Marcus", "Priya", "Wendell", "Sofia", "Grant", "Lena", "Theo",
            "Ingrid", "Cal", "Renata", "Boyd"]

# counted idle by construction: available − booked (wire EDM deliberately unmaintained)
BOOK_TARGETS = {  # (class, week_index): booked hours
    ("3-axis mill", 0): 171, ("3-axis mill", 1): 149,   # idle 9 / 31
    ("5-axis mill", 0): 82,  ("5-axis mill", 1): 61,    # idle 8 / 29
    ("lathe", 0): 176,       ("lathe", 1): 168,          # idle 4 / 12
    ("wire EDM", 0): 77,     ("wire EDM", 1): 64,        # unmeasured either way
}

MESSAGES = [
    "any word on the quote for the housings?",
    "did you get my rfq from last tuesday",
    "we changed the material to 17-4 on the pump housing",
    "rev c drawing attached, tolerances tightened on the bore",
    "what are your shop hours over the holiday",
    "thanks for the tour last week",
    "invoice 4471 shows the wrong PO number",
    "saw the new price on the brackets — send the PO terms",
]


def main():
    store.wipe()
    store.save("config", {"company": "Ridgeway Precision Machining",
                          "machines": sum(CLASSES.values()), "classes": len(CLASSES),
                          "variable_cost_hr": RATES,
                          "min_margin": 0.10, "target_margin": 0.28,
                          "rebid_cooldown_days": core.REBID_COOLDOWN_DAYS})

    machines = [{"id": f"mx_{i:02d}", "name": name, "machine_class": mc}
                for i, (mc, name) in enumerate((mc, n) for mc, names in MACHINE_NAMES.items()
                                               for n in names)]
    store.save("machines", machines)

    weeks, bookings = [], []
    wks = [core.this_week(), core.next_week()]
    for mc, count in CLASSES.items():
        for wi, wk in enumerate(wks):
            weeks.append({"id": f"wk_{mc.split()[0]}_{wi}", "machine_class": mc,
                          "week_of": wk, "available_shift_hours": count * 45,
                          "maintained": mc != "wire EDM",
                          "note": ("schedule board not updated since the setter left"
                                   if mc == "wire EDM" else "maintained")})
            remaining = BOOK_TARGETS[(mc, wi)]
            while remaining > 0:
                h = min(remaining, rng.randint(5, 14))
                bookings.append({"id": store.nid("bk"), "machine_class": mc, "week_of": wk,
                                 "hours": h,
                                 "part": f"{rng.choice(MATERIALS)} {rng.choice(PARTS)}"})
                remaining -= h
    store.save("weeks", weeks)
    store.save("bookings", bookings)

    # -- the graveyard: ~300 lost quotes across loss reasons, 18 months back
    graveyard = []
    reasons = ["price"] * 45 + ["lead_time"] * 25 + ["silence"] * 20 + ["capability"] * 10
    for i in range(300):
        mc = rng.choice(list(CLASSES))
        hours = None if rng.random() < 0.07 else rng.randint(3, 60)
        material = rng.randint(80, 2500)
        lr = rng.choice(reasons)
        died = None
        if hours is not None:
            base = hours * RATES[mc] + material
            died = round(base * rng.uniform(1.05, 1.6), 2)
        graveyard.append({
            "id": f"gq_{i:03d}",
            "part": f"{rng.choice(MATERIALS)} {rng.choice(PARTS)} ×{rng.choice([10, 25, 50, 100, 200])}",
            "machine_class": mc, "hours": hours, "material_cost": material,
            "died_at_price": died, "loss_reason": lr,
            "buyer": rng.choice(BUYERS), "contact": rng.choice(CONTACTS),
            "lost_at": iso(now() - timedelta(days=rng.randint(30, 540)))})

    # -- demo fixtures (demo_tag → sweeps skip them; the buttons own them)
    graveyard += [
        {"id": "gq_demo_rebid", "part": "6061 clamp plate ×50", "machine_class": "3-axis mill",
         "hours": 22, "material_cost": 640, "died_at_price": 2950, "loss_reason": "price",
         "buyer": "Halvorsen Controls", "contact": "Dana",
         "lost_at": iso(now() - timedelta(days=150)), "demo_tag": "demo"},
        {"id": "gq_demo_capability", "part": "Ti-6Al-4V impeller ×10", "machine_class": "5-axis mill",
         "hours": 34, "material_cost": 1900, "died_at_price": 9800, "loss_reason": "capability",
         "buyer": "Coyle Aerospace Sub-Tier", "contact": "Priya",
         "lost_at": iso(now() - timedelta(days=210)), "demo_tag": "demo"},
        {"id": "gq_demo_unrecorded", "part": "4140 yoke ×25", "machine_class": "lathe",
         "hours": None, "material_cost": 410, "died_at_price": 3100, "loss_reason": "silence",
         "buyer": "Ruckman Marine", "contact": "Cal",
         "lost_at": iso(now() - timedelta(days=95)), "demo_tag": "demo"},
        {"id": "gq_demo_cooldown", "part": "brass nozzle ×100", "machine_class": "3-axis mill",
         "hours": 6, "material_cost": 120, "died_at_price": 1400, "loss_reason": "price",
         "buyer": "Delfino Automation", "contact": "Sofia",
         "lost_at": iso(now() - timedelta(days=300)),
         "last_rebid_at": iso(now() - timedelta(days=20)),
         "rebid_history": [{"at": iso(now() - timedelta(days=20)), "price": 676.0,
                            "week_of": core.this_week(), "response": None}],
         "demo_tag": "demo"},
        {"id": "gq_demo_silence", "part": "303 SS bushing ×200", "machine_class": "lathe",
         "hours": 8, "material_cost": 260, "died_at_price": 1600, "loss_reason": "price",
         "buyer": "Sable Valve Works", "contact": "Grant",
         "lost_at": iso(now() - timedelta(days=400)),
         "last_rebid_at": iso(now() - timedelta(days=200)),
         "rebid_history": [{"at": iso(now() - timedelta(days=200)), "price": 940.0,
                            "week_of": core.this_week(), "response": "silence"}],
         "demo_tag": "demo"},
        {"id": "gq_demo_edm", "part": "17-4 cam follower ×50", "machine_class": "wire EDM",
         "hours": 12, "material_cost": 300, "died_at_price": 2400, "loss_reason": "price",
         "buyer": "Pinehurst Instruments", "contact": "Ingrid",
         "lost_at": iso(now() - timedelta(days=120)), "demo_tag": "demo"},
    ]
    store.save("graveyard", graveyard)

    messages = [{"id": f"ms_{i:03d}", "from": rng.choice(CONTACTS), "text": t,
                 "at": iso(now() - timedelta(hours=rng.randint(1, 72)))}
                for i, t in enumerate(MESSAGES)]
    messages += [
        {"id": "ms_demo_friday", "from": "Marcus",
         "text": "need 200 of the 6061 clamp plates by friday, can you?",
         "machine_class": "3-axis mill", "qty": 200, "hours_per_pc": 0.13,
         "at": iso(now() - timedelta(minutes=20)), "demo_tag": "demo"},
        {"id": "ms_demo_edm_friday", "from": "Ingrid",
         "text": "need 40 wire edm slots by friday, can you?",
         "machine_class": "wire EDM", "qty": 40, "hours_per_pc": 0.3,
         "at": iso(now() - timedelta(minutes=35)), "demo_tag": "demo"},
        {"id": "ms_demo_no_hours", "from": "Wendell",
         "text": "can you turn 50 shafts by thursday",
         "at": iso(now() - timedelta(minutes=50)), "demo_tag": "demo"},
        {"id": "ms_demo_rebid_reply", "from": "Dana",
         "text": "got your requote on the manifold blocks, let's talk",
         "quote_id": "gq_demo_rebid",
         "at": iso(now() - timedelta(minutes=65)), "demo_tag": "demo"},
    ]
    store.save("messages", messages)
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"machines": len(machines), "graveyard": len(graveyard)})
    print(f"Seeded {len(machines)} machines in {len(CLASSES)} classes, {len(weeks)} schedule "
          f"weeks, {len(bookings)} bookings, {len(graveyard)} graveyard quotes, "
          f"{len(messages)} messages")


if __name__ == "__main__":
    main()
