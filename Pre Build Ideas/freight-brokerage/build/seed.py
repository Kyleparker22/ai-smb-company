#!/usr/bin/env python3
"""Carrier OS — synthetic brokerage generator.

A 22-person brokerage. Invented carrier names, obviously fake MC/DOT numbers,
555 phones, no live FMCSA calls of any kind. Built so an ops manager recognizes
their own board: a year of booked history so a benchmark can actually be
computed, lanes too thin to benchmark, clean long-standing carriers, brand-new
authorities, one hijacked-identity pattern and one re-broker pattern.

  python3 seed.py --loads 140 --weeks 52
"""
import argparse, random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

R = random.Random(20260816)

CARRIER_WORDS = [("Ironwood", "Transport"), ("Blue Ridge", "Carriers"), ("Halcyon", "Freight"),
                 ("Meridian", "Trucking"), ("Cordova", "Logistics"), ("Windrow", "Lines"),
                 ("Saltmarsh", "Hauling"), ("Kestrel", "Motor Freight"), ("Deerfield", "Express"),
                 ("Tallgrass", "Transit"), ("Verdant", "Cartage"), ("Northpine", "Trucking"),
                 ("Ember", "Freightways"), ("Quarry Hill", "Transport"), ("Sundown", "Carriers"),
                 ("Blackwater", "Logistics"), ("Fairhaven", "Trucking"), ("Redbird", "Lines")]
CUSTOMERS = ["Alder Foods", "Brightline Retail", "Cobalt Chemical", "Dunmore Paper",
             "Everline Beverage", "Foxwood Furniture", "Granite Building Supply",
             "Harbor Electronics"]
LANES = [("ATL-CHI", 715), ("DAL-LAX", 1435), ("CLT-NYC", 630), ("MEM-DEN", 1050),
         ("PHX-SEA", 1420), ("MIA-ATL", 660), ("KC-MSP", 440), ("IND-PIT", 360),
         ("SLC-BOI", 340), ("OKC-STL", 500)]
EQUIP = ["van", "reefer"]


def build(loads_per_week, weeks, reset=True):
    if reset:
        store.wipe()
    t0 = now()

    store.save("config", {
        "brokerage": "Halyard Freight Group",
        "people": 22, "tms": "modelled, not connected",
        "seeded_at": iso(),
        "roi_inputs": {"vetting_minutes_saved": 16, "calls_each": 3, "minutes_per_call": 5,
                       "loaded_rate": 31, "margin_bps": 90, "exposure_per_event": 42000},
    })
    store.save("lanes", [{"lane": k, "miles": m} for k, m in LANES])

    carriers = []
    for i, (a, b) in enumerate(CARRIER_WORDS):
        age_days = R.choice([1800, 2600, 900, 4000, 1200, 300])
        carriers.append({
            "id": f"ca_{i+1}", "name": f"{a} {b}", "mc": f"MC-00{R.randint(10000,99999)}",
            "dot": f"DOT-0{R.randint(100000,999999)}",
            "authority_status": "active", "authority_since": iso(t0 - timedelta(days=age_days)),
            "authority_checked_at": iso(t0 - timedelta(days=R.choice([0, 1, 3, 20, 95]))),
            "insurance_expires": iso(t0 + timedelta(days=R.choice([12, 60, 140, 240, 400]))),
            "insurance_checked_at": iso(t0 - timedelta(days=R.choice([0, 2, 40]))),
            "cargo_limit": R.choice([100000, 100000, 250000, 50000]),
            "safety_checked_at": iso(t0 - timedelta(days=R.choice([1, 5, 70]))),
            "oos_rate": R.choice([0.02, 0.05, 0.09, 0.18, 0.31, None]),
            "contact_checked_at": iso(t0 - timedelta(days=R.choice([0, 1, 10]))),
            "phone": f"555-06{10+i}", "registered_phone": f"555-06{10+i}",
            "email_domain": f"{a.lower().replace(' ', '')}.example",
            "registered_domain": f"{a.lower().replace(' ', '')}.example",
            "domain_age_days": age_days,
            "address": f"{R.randint(100,9000)} Depot Rd", "registered_address": None,
            "equipment": R.choice([["van"], ["reefer"], ["van", "reefer"]]),
            "loads_with_us": R.choice([0, 2, 8, 19, 40, 65]),
            "claims_with_us": R.choices([0, 1, 2], [88, 9, 3])[0],
        })
        carriers[-1]["registered_address"] = carriers[-1]["address"]

    # -- the two fraud patterns, deterministic ------------------------------
    carriers.append({
        "id": "ca_hijack", "name": "Northpine Trucking LLC", "mc": "MC-0088412", "dot": "DOT-0774120",
        "authority_status": "active", "authority_since": iso(t0 - timedelta(days=2900)),
        "authority_checked_at": iso(t0 - timedelta(days=1)),
        "insurance_expires": iso(t0 + timedelta(days=180)),
        "insurance_checked_at": iso(t0 - timedelta(days=1)), "cargo_limit": 100000,
        "safety_checked_at": iso(t0 - timedelta(days=2)), "oos_rate": 0.06,
        "contact_checked_at": iso(t0),
        # the tell: an old, clean authority reached at a brand-new domain and a
        # phone that is not the one on the registered record
        "phone": "555-0777", "registered_phone": "555-0421",
        "email_domain": "northpine-dispatch.example", "registered_domain": "northpine.example",
        "domain_age_days": 11,
        "address": "88 Yard St", "registered_address": "412 Old Depot Rd",
        "equipment": ["van", "reefer"], "loads_with_us": 0, "claims_with_us": 0,
        "demo_tag": "hijacked identity"})
    carriers.append({
        "id": "ca_rebroker", "name": "Swiftline Capacity Partners", "mc": "MC-0099001",
        "dot": "DOT-0991001", "authority_status": "active",
        "authority_since": iso(t0 - timedelta(days=41)),
        "authority_checked_at": iso(t0), "insurance_expires": iso(t0 + timedelta(days=300)),
        "insurance_checked_at": iso(t0), "cargo_limit": 25000,
        "safety_checked_at": iso(t0), "oos_rate": None, "contact_checked_at": iso(t0),
        "phone": "555-0812", "registered_phone": "555-0812",
        "email_domain": "swiftline-cap.example", "registered_domain": "swiftline-cap.example",
        "domain_age_days": 38, "address": "9 Suite B", "registered_address": "9 Suite B",
        "equipment": ["van"], "loads_with_us": 0, "claims_with_us": 0,
        "demo_tag": "re-broker pattern"})
    # the two carriers used as the CLEAN comparators in the demo must genuinely
    # be able to take this load, or the walkthrough compares three refusals
    for cid in ("ca_1", "ca_4"):
        c = next(x for x in carriers if x["id"] == cid)
        c["equipment"] = ["van", "reefer"]
        c["cargo_limit"] = 100000
        c["insurance_expires"] = iso(t0 + timedelta(days=240))
    store.save("carriers", carriers)

    # -- a year of booked history -------------------------------------------
    loads = []
    for w in range(weeks):
        for _ in range(loads_per_week):
            lane, miles = R.choice(LANES[:8])                # last two stay thin on purpose
            eq = R.choice(EQUIP)
            when = t0 - timedelta(days=w * 7 + R.randint(0, 6))
            base = miles * (1.95 if eq == "van" else 2.35)
            season = 1.0 + (0.12 if when.month in (5, 6, 10, 11) else -0.04)
            carrier_rate = round(base * season * R.uniform(0.88, 1.14), 2)
            loads.append({"id": f"ld_{len(loads)+1}", "lane": lane, "miles": miles,
                          "equipment": eq, "booked_at": iso(when),
                          "carrier_rate": carrier_rate,
                          "customer_rate": round(carrier_rate * R.uniform(1.09, 1.24), 2),
                          "customer": R.choice(CUSTOMERS),
                          "carrier_name": R.choice(carriers[:18])["name"],
                          "value": R.choice([18000, 35000, 60000, 90000]),
                          "state": "delivered"})
    # thin lanes: a couple of loads only, so the benchmark must refuse
    for lane, miles in LANES[8:]:
        for _ in range(3):
            loads.append({"id": f"ld_{len(loads)+1}", "lane": lane, "miles": miles,
                          "equipment": "van", "booked_at": iso(t0 - timedelta(days=R.randint(5, 200))),
                          "carrier_rate": round(miles * 2.1, 2),
                          "customer_rate": round(miles * 2.4, 2),
                          "customer": R.choice(CUSTOMERS), "carrier_name": carriers[0]["name"],
                          "value": 22000, "state": "delivered"})

    # -- live board ---------------------------------------------------------
    for i in range(26):
        lane, miles = R.choice(LANES[:8])
        eq = R.choice(EQUIP)
        deliver = t0 + timedelta(days=R.randint(1, 4))
        l = {"id": f"ld_live_{i+1}", "lane": lane, "miles": miles, "equipment": eq,
             "booked_at": iso(t0 - timedelta(days=R.randint(0, 3))),
             "carrier_rate": round(miles * 2.05, 2), "customer_rate": round(miles * 2.35, 2),
             "customer": R.choice(CUSTOMERS), "carrier_name": R.choice(carriers[:18])["name"],
             "value": R.choice([18000, 35000, 60000]), "state": "in_transit",
             "deliver_by": iso(deliver),
             "last_contact_at": iso(t0 - timedelta(hours=R.choice([1, 2, 4, 9, 14]))),
             "dwell_hours": R.choice([0, 0, 1, 4, 6]),
             "off_route_miles": R.choice([0, 0, 0, 70, 120]),
             "eta": iso(deliver + timedelta(hours=R.choice([-6, -2, 3, 9])))}
        loads.append(l)

    # the demo load: high-value electronics, tendered, three offers
    # $60k of freight: high enough that a 90-day authority is a tripwire, low
    # enough that a normal $100k cargo policy is NOT — otherwise every carrier
    # trips the same wire and the demo says nothing.
    demo = {"id": "ld_demo", "lane": "ATL-CHI", "miles": 715, "equipment": "van",
            "booked_at": iso(t0), "customer_rate": 1980.0, "customer": "Harbor Electronics",
            "value": 60000, "state": "tendered",
            "deliver_by": iso(t0 + timedelta(days=2)), "demo_tag": "high-value electronics"}
    loads.append(demo)
    store.save("loads", loads)

    offers = [
        {"id": "of_demo_1", "load_id": "ld_demo", "carrier_id": "ca_hijack", "rate": 940.0},
        {"id": "of_demo_2", "load_id": "ld_demo", "carrier_id": "ca_rebroker", "rate": 1420.0},
        {"id": "of_demo_3", "load_id": "ld_demo", "carrier_id": "ca_1", "rate": 1690.0},
        {"id": "of_demo_4", "load_id": "ld_demo", "carrier_id": "ca_4", "rate": 1740.0},
    ]
    store.save("offers", offers)
    store.save("checkcalls", [])
    store.save("tripwire_log", [])
    store.save("approvals", [])
    store.save("events", [])
    return {"carriers": len(carriers), "loads": len(loads), "offers": len(offers)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--loads", type=int, default=140)
    ap.add_argument("--weeks", type=int, default=52)
    a = ap.parse_args()
    print(build(a.loads, a.weeks))
