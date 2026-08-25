#!/usr/bin/env python3
"""Counter OS — synthetic Tri-State Supply Co. Synthetic only.

An electrical/plumbing distributor, two branches (Fairfield · Riverside),
~600 catalog items with recorded margins, on-hand counts and reorder points,
eight vendors, and ~250 counted no-events over 60 days — including one item
the count pushes over the stocking threshold, several that stay anecdotes,
some no's with no comparable (UNPRICED), and out-of-stock no's on carried
items whose recorded pace beat their recorded reorder point.
"""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(8890)

BRANCHES = ("Fairfield", "Riverside")

FAMILIES = {
    # category → (sku prefix, [(base description, [sizes], list lo-hi)])
    "conduit & fittings": ("ELC", [("EMT connector", ["1/2 in", "3/4 in", "1 in", "2 in"], (0.6, 4.0)),
                                   ("EMT coupling", ["1/2 in", "3/4 in", "1 in", "2 in"], (0.5, 3.5)),
                                   ("rigid conduit stick", ["1/2 in", "3/4 in", "1 in", "2 in"], (9, 60)),
                                   ("liquidtight strain relief", ["1/2 in", "3/4 in"], (2, 6)),
                                   ("PVC conduit body", ["1/2 in", "3/4 in", "1 in"], (4, 12))]),
    "wire & cable": ("WIR", [("THHN copper spool", ["12 AWG", "10 AWG", "8 AWG", "6 AWG"], (60, 320)),
                             ("MC cable coil", ["12/2", "12/3", "10/2"], (70, 240)),
                             ("NM-B romex coil", ["14/2", "12/2", "10/3"], (55, 210)),
                             ("bare ground spool", ["8 AWG", "6 AWG"], (45, 130))]),
    "boxes & covers": ("BOX", [("steel handy box", ["1-gang", "2-gang"], (1.5, 5)),
                               ("weatherproof cover", ["1-gang", "2-gang"], (3, 9)),
                               ("ceiling fan box", ["standard", "old work"], (6, 15))]),
    "valves & brass": ("PVF", [("brass ball valve threaded", ["1/2 in", "3/4 in", "1 in", "2 in"], (7, 45)),
                               ("check valve bronze", ["1/2 in", "1 in", "2 in"], (11, 60)),
                               ("boiler drain", ["1/2 in", "3/4 in"], (5, 12))]),
    "copper & fittings": ("CPR", [("copper coupling", ["1/2 in", "3/4 in", "1 in"], (0.4, 3)),
                                  ("copper elbow 90", ["1/2 in", "3/4 in", "1 in"], (0.5, 4)),
                                  ("copper tube stick", ["1/2 in", "3/4 in", "1 in"], (14, 70))]),
    "PVC & DWV": ("DWV", [("DWV coupling", ["1-1/2 in", "2 in", "3 in", "4 in"], (0.8, 6)),
                          ("DWV wye", ["1-1/2 in", "2 in", "3 in"], (2, 11)),
                          ("closet flange", ["3 in", "4 in"], (4, 13))]),
    "PEX & supply": ("PEX", [("PEX crimp ring bag", ["1/2 in", "3/4 in"], (8, 18)),
                             ("PEX tubing coil", ["1/2 in", "3/4 in", "1 in"], (30, 160)),
                             ("supply stop", ["3/8 in", "1/2 in"], (4, 11))]),
    "fasteners & strut": ("FST", [("strut channel stick", ["10 ft solid", "10 ft slotted"], (14, 30)),
                                  ("strut strap", ["1/2 in", "3/4 in", "1 in"], (0.5, 2.5)),
                                  ("concrete anchor box", ["1/4 in", "3/8 in", "1/2 in"], (9, 28))]),
}

VENDORS = [
    {"id": "v_larkspur", "name": "Larkspur Electrical Supply",
     "lines": ["conduit & fittings", "boxes & covers"], "lead_time_days": 5,
     "rep": "D. Moss", "phone": "(555) 014-2288"},
    {"id": "v_cobble", "name": "Cobblewick Wire & Cable",
     "lines": ["wire & cable"], "lead_time_days": 7, "rep": "R. Ferro", "phone": "(555) 014-6031"},
    {"id": "v_dover", "name": "Doverline Tool Group",
     "lines": ["press tools"], "lead_time_days": 4, "rep": "K. Anand", "phone": "(555) 014-8874"},
    {"id": "v_brassmere", "name": "Brassmere Valve & Fitting",
     "lines": ["valves & brass", "copper & fittings"], "lead_time_days": 6,
     "rep": "T. Okafor", "phone": "(555) 014-1440"},
    {"id": "v_plaskett", "name": "Plaskett Plastics",
     "lines": ["PVC & DWV", "PEX & supply"], "lead_time_days": 8,
     "rep": "M. Reyes", "phone": "(555) 014-9917"},
    {"id": "v_ironvale", "name": "Ironvale Fastener Co.",
     "lines": ["fasteners & strut"], "lead_time_days": 9, "rep": "J. Palowski", "phone": "(555) 014-3302"},
    {"id": "v_stateside", "name": "Stateside Master Distribution",
     "lines": ["conduit & fittings", "wire & cable", "valves & brass", "PVC & DWV"],
     "lead_time_days": 12, "rep": "B. Crane", "phone": "(555) 014-5560"},
    {"id": "v_quarry", "name": "Quarry Light & Fixture",
     "lines": ["fixtures"], "lead_time_days": 14, "rep": "S. Ang", "phone": "(555) 014-7708"},
]

ASKERS = ["Calloway Mechanical", "Brightwater Plumbing", "Ostrander Electric", "Ferrell & Sons",
          "Meridian Builders", "Halvorsen HVAC", "Redpoint Contracting", "Silva Underground",
          "walk-in", "Trask Facilities", "Lowry Electric", "Pemberton Pools"]

# Not-carried asks that stay anecdotes — cycled so none accidentally crosses the
# threshold; demand for a case has to be seeded on purpose.
ANECDOTES = [
    "smart panel load controller", "1-1/4 in EMT connector", "arc rated gloves",
    "tankless heater isolation kit", "cast iron no-hub coupling 5 in", "solar rapid shutdown box",
    "direct burial splice kit 4 awg", "stainless strut channel", "3 in brass check valve",
    "pex expansion tool head 3/4", "generator inlet box 50a", "roof jack 2 in",
    "mixing valve high flow", "conduit bender 1-1/4 shoe", "led high bay 200w",
    "gas flex csst 1 in coil", "hydronic air separator 1-1/4", "pvc long sweep 90 6 in",
    "grounding busbar kit", "tamper resistant gfci black", "well pump control box 1hp",
    "backflow preventer 1 in rpz", "insulated throat connector 3 in", "copper press elbow 2 in",
    "channel drain kit", "dielectric union 1-1/4", "sump check valve quiet 2 in",
    "fire caulk sausage pack", "romex staple bulk pail", "meter socket 400a",
]

MESSAGES = [
    "price on 500 ft of 12/2 romex",
    "how much for a case of pvc primer",
    "is my will call order ready",
    "what time do you open saturday",
    "turned away another guy asking for pex crimp rings",
    "we were out of 2 in emt connectors again, he walked",
]


def _catalog():
    rows = []
    for cat, (prefix, fams) in FAMILIES.items():
        i = 0
        for base, sizes, (lo, hi) in fams:
            for size in sizes:
                for variant in range(8):  # depth per size → ~600 rows
                    i += 1
                    lst = round(rng.uniform(lo, hi), 2)
                    cost = round(lst * rng.uniform(0.55, 0.75), 2)
                    desc = f"{size} {base}" if variant == 0 else f"{size} {base} grade {variant}"
                    vend = next((v["id"] for v in VENDORS if cat in v["lines"]), "v_stateside")
                    rows.append({
                        "sku": f"{prefix}-{1000 + i:04d}", "description": desc,
                        "category": cat, "vendor": vend, "list": lst, "cost": cost,
                        "uom": "ea",
                        "on_hand": {b: rng.randint(0, 80) for b in BRANCHES},
                        "reorder_point": rng.randint(5, 40),
                        "pace_per_day": round(rng.uniform(0.1, 3.0), 1),
                        "pace_basis": "counted from 90 days of recorded sales (synthetic)"})
    # The demo OOS item — carried, counted zero everywhere, recorded pace 6/day
    # against a recorded point of 20 with a 5-day vendor lead: the pace beat it.
    demo = next(r for r in rows if r["description"] == "2 in EMT connector")
    demo.update(sku="ELC-0042", list=1.18, cost=0.62, vendor="v_larkspur",
                on_hand={"Fairfield": 0, "Riverside": 0}, reorder_point=20, pace_per_day=6.0)
    return rows


def _days_ago(d, hours=None):
    return iso(now() - timedelta(days=d, hours=hours if hours is not None else rng.randint(0, 9)))


def _no(item, kind, days_ago, branch=None, asked_by=None, ww=None, category=None,
        sku=None, qty=None, demo_tag=None):
    row = {"id": store.nid("no"), "at": _days_ago(days_ago),
           "item_asked": item, "kind": kind,
           "asked_by": asked_by or rng.choice(ASKERS),
           "branch": branch or rng.choice(BRANCHES),
           "walked_or_waited": ww or rng.choice(["walked", "waited", "waited"]),
           "category": category, "sku": sku, "qty": qty}
    if demo_tag:
        row["demo_tag"] = demo_tag
    return row


def main():
    store.wipe()
    store.save("config", {
        "company": "Tri-State Supply Co.",
        "tagline": "electrical & plumbing distribution",
        "branches": list(BRANCHES),
        "counts_as_of": iso(now() - timedelta(hours=3)),
        "stocking_threshold": {
            "count": 5, "window_days": 60,
            "_source": ("adopted by the owner 2026-07: five counted no's for the same item "
                        "inside sixty days is demand; fewer is an anecdote")},
        "safety_days": {
            "days": 2,
            "_source": "owner's rule: two days of pace held back for delivery variance"},
        "category_margins": {
            "_source": ("recorded average margin dollars per counter sale, by category, from "
                        "the operator's own sales export (synthetic here) — never an industry "
                        "stat"),
            "margins": {"press tools": 38.0, "specialty plumbing": 22.0,
                        "wire & cable": 31.0, "conduit & fittings": 9.0}},
    })

    catalog = _catalog()
    store.save("catalog", catalog)
    store.save("vendors", VENDORS)

    nos = []
    # 1) The threshold-crossing item: seven counted no's in the window for a
    #    press jaw we don't carry — priced from the recorded category margin.
    for d in (3, 9, 16, 24, 31, 42, 55):
        nos.append(_no("Ridgeline RL-34 press jaw", "not_carried", d,
                       category="press tools", qty=1))
    # 2) Below the threshold — an anecdote, on purpose.
    for d in (6, 33):
        nos.append(_no("2 in copper repair coupling", "not_carried", d,
                       category="specialty plumbing", qty=1))
    # 3) No comparable at all — counted, never dollared.
    for d in (2, 18, 40):
        nos.append(_no("the blue connector thing for the old zinsco panel", "not_carried", d,
                       category=None, qty=1))
    # 4) OOS no's on the carried demo SKU — the walked ones are the hand-checkable
    #    counted cost: (40 + 25 + 60) units × $0.56 recorded margin = $70.00.
    for d, ww, qty in ((1, "walked", 40), (5, "walked", 25), (12, "walked", 60),
                       (8, "waited", 10), (20, "waited", 15), (34, "waited", 30)):
        nos.append(_no("2 in EMT connector", "out_of_stock", d, sku="ELC-0042",
                       ww=ww, qty=qty))
    # 5) The background hum: ~230 more over 60 days.
    pool = [c for c in catalog if c["sku"] != "ELC-0042"]
    for i in range(230):
        d = rng.randint(0, 59)
        roll = rng.random()
        if roll < 0.55:
            row = rng.choice(pool)
            nos.append(_no(row["description"], "out_of_stock", d, sku=row["sku"],
                           qty=rng.randint(1, 12)))
        elif roll < 0.80:
            item = ANECDOTES[i % len(ANECDOTES)]
            cat = rng.choice(["wire & cable", "conduit & fittings", None, None])
            nos.append(_no(item, "not_carried", d, category=cat, qty=rng.randint(1, 4)))
        else:
            row = rng.choice(pool)
            nos.append(_no(f"{row['description']} (other size)", "wrong_size", d,
                           sku=None, category=row["category"]
                           if row["category"] in ("wire & cable", "conduit & fittings")
                           else None, qty=rng.randint(1, 6)))
    # 6) One demo fixture, excluded from every counted read.
    nos.append(_no("demo row — excluded from counts", "not_carried", 1, qty=999,
                   demo_tag="demo"))
    nos[-1]["id"] = "no_demo_excluded"
    store.save("nos", nos)

    messages = [{"id": f"ms_{i:03d}", "from": rng.choice(ASKERS), "text": t,
                 "branch": rng.choice(BRANCHES),
                 "at": iso(now() - timedelta(hours=rng.randint(1, 72)))}
                for i, t in enumerate(MESSAGES * 2)]
    messages.append({
        "id": "ms_demo_down", "from": "Meridian Builders", "branch": "Fairfield",
        "text": ("my crew is standing around at the meridian job — do you have "
                 "2 in EMT connectors RIGHT NOW"),
        "at": iso(now() - timedelta(minutes=12)), "demo_tag": "demo"})
    messages.append({
        "id": "ms_demo_noreport", "from": "counter — Fairfield", "branch": "Fairfield",
        "text": "customer asked for a ridgeline rl-34 press jaw, we don't carry it",
        "no": {"item_asked": "Ridgeline RL-34 press jaw", "kind": "not_carried",
               "asked_by": "Calloway Mechanical", "walked_or_waited": "walked",
               "branch": "Fairfield", "category": "press tools", "qty": 1},
        "at": iso(now() - timedelta(minutes=35)), "demo_tag": "demo"})
    store.save("messages", messages)

    store.save("cases", [])
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"catalog": len(catalog), "nos": len(nos)})
    print(f"Seeded {len(catalog)} catalog items, {len(VENDORS)} vendors, {len(nos)} no-events, "
          f"{len(messages)} messages")


if __name__ == "__main__":
    main()
