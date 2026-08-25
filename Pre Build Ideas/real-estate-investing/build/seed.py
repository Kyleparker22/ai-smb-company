#!/usr/bin/env python3
"""Deal OS — synthetic three-market dataset. Synthetic only: invented markets,
invented addresses, 555 phones. Labeled synthetic in config."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

rng = random.Random(61)

MARKETS = [
    # id, name, flavor: (median price, tax rate, base appreciation, str-friendly)
    ("mk_maple", "Maplewood ST", 285000, 0.0095, 0.041, False),
    ("mk_harbor", "Harbor Point FL", 410000, 0.0110, 0.052, True),
    ("mk_cedar", "Cedar Falls OH", 145000, 0.0160, 0.028, True),
]
STREETS = ["Birchwood Ln", "Fernwood Ave", "Cypress Ct", "Dunmore St", "Ellery Rd",
           "Foxglove Dr", "Galloway St", "Harlan Ave", "Ironwood Ter", "Juniper Way"]
NAMES = ["Reyes", "Okafor", "Lindgren", "Castellano", "Whitmore", "Nakagawa", "Boudreaux",
         "Ferris", "Aldana", "Pruett"]

MESSAGES = [
    "run the numbers on 412 Birchwood as a short term rental",
    "what happens if rates drop a point next year",
    "anything new hit the screen this week",
    "thanks for the breakdown yesterday",
]


def main():
    store.wipe()
    t0 = now()
    store.save("config", {
        "company": "Keystone Property Group",
        "doors": 23,
        "data_note": "SYNTHETIC MARKET — invented listings, comps and history. Real "
                     "deployment pulls sanctioned APIs only (FRED, licensed MLS, AirDNA).",
    })

    markets = []
    for mid, name, med, tax, appn, strf in MARKETS:
        hist = []
        idx = 100.0
        for y in range(11):
            hist.append({"year": 2016 + y, "index": round(idx, 2)})
            idx *= 1 + appn + rng.uniform(-0.012, 0.012)
        markets.append({"id": mid, "name": name, "median_price": med, "tax_rate": tax,
                        "str_friendly": strf,
                        "appreciation_history": hist,
                        "rates": {"rate_30yr": round(rng.uniform(0.0625, 0.0675), 4),
                                  "as_of": iso(t0 - timedelta(days=3 if mid != "mk_cedar" else 44))}})
    # Cedar Falls' rate is deliberately 44 days old — the stale path is live.
    store.save("markets", markets)

    listings = []
    for i in range(90):
        mid, name, med, tax, appn, strf = MARKETS[i % 3]
        beds = rng.choice([2, 3, 3, 4])
        price = int(med * rng.uniform(0.7, 1.4) * (0.85 + beds * 0.07))
        listings.append({
            "id": f"ls_{i:03d}", "market_id": mid,
            "address": f"{rng.randint(100, 999)} {rng.choice(STREETS)}, {name}",
            "price": price, "bedrooms": beds, "bathrooms": rng.choice([1, 2, 2, 3]),
            "sqft": rng.randint(950, 2600),
            "taxes": int(price * tax), "insurance": int(price * rng.uniform(0.004, 0.007)),
            "hoa": rng.choice([0, 0, 0, 45, 120]),
            "status": "active", "listed_at": iso(t0 - timedelta(days=rng.randint(0, 60))),
        })
    # demo fixtures
    listings += [
        {"id": "ls_demo_birch", "market_id": "mk_harbor",
         "address": "412 Birchwood Ln, Harbor Point FL", "price": 385000, "bedrooms": 3,
         "bathrooms": 2, "sqft": 1650, "taxes": 4235, "insurance": 2300, "hoa": 0,
         "status": "active", "listed_at": iso(t0 - timedelta(days=4)), "demo_tag": "demo"},
        {"id": "ls_demo_fern", "market_id": "mk_maple",
         "address": "88 Fernwood Ave (duplex), Maplewood ST", "price": 310000, "bedrooms": 4,
         "bathrooms": 2, "sqft": 2100, "taxes": 2945, "insurance": 1650, "hoa": 0,
         "status": "active", "listed_at": iso(t0 - timedelta(days=9)), "demo_tag": "demo"},
        # Maplewood has NO STR comps seeded — the comp-floor refusal is live here.
    ]
    store.save("listings", listings)

    comps = []
    for mid, name, med, tax, appn, strf in MARKETS:
        for beds in (2, 3, 4):
            base_rent = med * 0.0072 * (0.75 + beds * 0.11)
            for j in range(rng.randint(6, 10)):
                comps.append({"id": store.nid("cp"), "market_id": mid, "strategy": "ltr",
                              "bedrooms": beds, "rent": round(base_rent * rng.uniform(0.9, 1.1)),
                              "as_of": iso(t0 - timedelta(days=rng.randint(5, 150)))})
            for j in range(rng.randint(5, 8)):
                comps.append({"id": store.nid("cp"), "market_id": mid, "strategy": "mtr",
                              "bedrooms": beds,
                              "rent": round(base_rent * 1.35 * rng.uniform(0.9, 1.1)),
                              "as_of": iso(t0 - timedelta(days=rng.randint(5, 150)))})
            if strf:  # Maplewood stays STR-comp-free on purpose
                for j in range(rng.randint(5, 9)):
                    comps.append({"id": store.nid("cp"), "market_id": mid, "strategy": "str",
                                  "bedrooms": beds,
                                  "adr": round(med * 0.00062 * (0.7 + beds * 0.13)
                                               * rng.uniform(0.85, 1.15), 2),
                                  "occupancy": round(rng.uniform(0.52, 0.68), 3),
                                  "as_of": iso(t0 - timedelta(days=rng.randint(5, 150)))})
    store.save("comps", comps)

    store.save("criteria", [{
        "id": "cr_1", "investor_id": "inv_1", "investor": "Keystone Property Group",
        "min_dscr": 1.2, "min_coc": 0.06, "max_price": 400000,
        "strategies": ["ltr", "mtr", "str"],
        "recorded_at": iso(t0 - timedelta(days=12)),
        "note": "the investor's own recorded bar — the screen ranks by this and nothing else",
    }])

    messages = [{"id": f"ms_{i:03d}", "from": rng.choice(NAMES), "text": t,
                 "at": iso(t0 - timedelta(hours=rng.randint(1, 72)))}
                for i, t in enumerate(MESSAGES * 2)]
    messages += [
        {"id": "ms_demo_advice", "from": "Reyes",
         "text": "should I buy the duplex on Fernwood", "listing_id": "ls_demo_fern",
         "at": iso(t0 - timedelta(minutes=20)), "demo_tag": "demo"},
        {"id": "ms_demo_numbers", "from": "Whitmore",
         "text": "run the numbers on 412 Birchwood as a short term rental",
         "listing_id": "ls_demo_birch", "at": iso(t0 - timedelta(minutes=35)),
         "demo_tag": "demo"},
        {"id": "ms_demo_whatif", "from": "Ferris",
         "text": "what happens if rates jump another point", "listing_id": "ls_demo_fern",
         "at": iso(t0 - timedelta(minutes=50)), "demo_tag": "demo"},
    ]
    store.save("messages", messages)
    store.save("analyses", [])
    store.save("approvals", [])
    store.save("events", [])
    store.log_event("seeded", "all", "human:seed", None,
                    {"listings": len(listings), "comps": len(comps)})
    print(f"Seeded {len(markets)} markets, {len(listings)} listings, {len(comps)} comps")


if __name__ == "__main__":
    main()
