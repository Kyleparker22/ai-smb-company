#!/usr/bin/env python3
"""Quote Desk OS — synthetic distributor generator.

An $18M industrial distributor with light fabrication. Invented customer and
manufacturer names, obviously fake part numbers. Built so an inside-sales
manager recognizes their own inbox: RFQs as email bodies, spreadsheets and
photo transcriptions, customer part numbers, a discontinued part, POs with
realistic discrepancies, and a year of quote outcomes with structured reasons.

  python3 seed.py --rfqs 90 --weeks 52
"""
import argparse, random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import store
from _kit.store import iso, now

R = random.Random(20260816)

FAMILIES = {
    "valves": [("brass ball valve threaded", ["1/4 in", "1/2 in", "3/4 in", "1 in", "2 in"]),
               ("bronze gate valve", ["1/2 in", "1 in", "2 in"]),
               ("PVC true union ball valve", ["1/2 in", "1 in", "2 in"])],
    "fittings": [("black iron elbow 90", ["1/2 in", "3/4 in", "1 in"]),
                 ("copper coupling", ["1/2 in", "3/4 in", "1 in"]),
                 ("stainless compression tee", ["1/4 in", "3/8 in", "1/2 in"])],
    "fasteners": [("hex cap screw grade 5 zinc", ["1/4-20 x 1", "3/8-16 x 2", "1/2-13 x 3"]),
                  ("flat washer stainless", ["1/4 in", "3/8 in", "1/2 in"])],
    "hose": [("push-lock hydraulic hose", ["3/8 in", "1/2 in", "3/4 in"]),
             ("EPDM water hose", ["3/4 in", "1 in"])],
    "electrical": [("EMT connector steel", ["1/2 in", "3/4 in", "1 in"]),
                   ("liquidtight strain relief", ["1/2 in", "3/4 in"])],
    "abrasives": [("flap disc type 29", ["4-1/2 in 40 grit", "4-1/2 in 60 grit"]),
                  ("cut-off wheel", ["4-1/2 in", "6 in"])],
    "fabricated": [("laser-cut bracket per print", ["rev A", "rev B"]),
                   ("welded frame assembly", ["short", "long"])],
}
CUSTOMERS = ["Ridgeline Mechanical", "Cobalt Fabricators", "Northgate Plumbing", "Delta Ironworks",
             "Everline Utilities", "Foxwood Millwork", "Granite Builders", "Harborview Marine",
             "Ivy Creek Contracting", "Juniper Process", "Kestrel Machine", "Lakeshore Energy"]
MANUFACTURERS = ["Ardmore", "Belfry", "Corvid", "Dunlin", "Emberly"]

MESSY_LINES = [
    "need a price on the usual bracket, rev B",
    "misc hardware as discussed",
    "part per drawing",
    "widget",
    "valve",
    "same as last order",
]


def build(rfqs_per_week, weeks, reset=True):
    if reset:
        store.wipe()
    t0 = now()

    store.save("config", {
        "company": "Halstead Industrial Supply",
        "revenue": "$18M", "inside_sales": 5, "erp": "modelled, not connected",
        "margin_floor": core.MARGIN_FLOOR,
        "seeded_at": iso(),
        "roi_inputs": {"hours_saved_per_quote": 0.6, "loaded_rate": 38,
                       "minutes_per_po": 9, "order_errors_month": 7, "cost_per_error": 340},
    })

    # -- catalog ------------------------------------------------------------
    catalog, n = [], 0
    for family, items in FAMILIES.items():
        for base, sizes in items:
            for size in sizes:
                n += 1
                cost = round(R.uniform(1.2, 240), 2)
                catalog.append({
                    "sku": f"SKU-{1000 + n}", "family": family,
                    "description": f"{size} {base}",
                    "manufacturer": R.choice(MANUFACTURERS),
                    "list": round(cost * R.uniform(1.45, 2.4), 2), "cost": cost,
                    "uom": R.choice(["ea", "ea", "ea", "bx", "ft"]),
                    "status": "active", "spec": size, "material": base.split()[0],
                    "rating": R.choice(["150#", "300#", None]),
                    "lead_days": R.choice([0, 0, 2, 5, 14, 28])})
    # one deliberate discontinued part with a successor that differs on spec
    disc = catalog[3]
    disc["status"] = "discontinued"
    disc["superseded_by"] = catalog[4]["sku"]
    catalog[4]["material"] = "bronze"
    store.save("catalog", catalog)

    # -- customers + cross-references ---------------------------------------
    customers, xref = [], []
    for i, name in enumerate(CUSTOMERS):
        bought = [c["sku"] for c in R.sample(catalog, R.randint(6, 25))]
        agreement = {}
        for sku in R.sample(bought, min(4, len(bought))):
            row = next(c for c in catalog if c["sku"] == sku)
            agreement[sku] = round(row["cost"] * R.uniform(1.15, 1.5), 2)
        customers.append({
            "id": f"cu_{i+1}", "name": name,
            "tier": R.choices(list(core.TIERS), [20, 30, 40, 10])[0],
            "bought": bought, "agreement": agreement,
            "ship_to": f"{R.randint(100,9000)} Industrial Way, Dock {R.randint(1,9)}",
            "terms": R.choice(["Net 30", "Net 30", "Net 45", "2/10 Net 30"])})
        for sku in R.sample(bought, min(6, len(bought))):
            xref.append({"customer_id": f"cu_{i+1}",
                         "customer_part": f"{name.split()[0][:3].upper()}-{R.randint(100,999)}",
                         "sku": sku})
    store.save("customers", customers)
    store.save("xref", xref)

    # -- a year of RFQs, quotes and outcomes --------------------------------
    rfqs, quotes, pos = [], [], []
    for w in range(weeks):
        for _ in range(rfqs_per_week):
            cust = R.choice(customers)
            when = t0 - timedelta(days=w * 7 + R.randint(0, 6), hours=R.randint(0, 9))
            n_lines = R.randint(1, 6)
            lines = []
            for _ in range(n_lines):
                if R.random() < 0.18:
                    lines.append({"qty": R.randint(1, 40), "uom": None,
                                  "description": R.choice(MESSY_LINES), "customer_part": None})
                    continue
                row = R.choice(catalog)
                use_xref = R.random() < 0.3
                cp = next((x["customer_part"] for x in xref
                           if x["customer_id"] == cust["id"] and x["sku"] == row["sku"]), None)
                lines.append({"qty": R.randint(1, 120),
                              "uom": R.choice(["ea", "EA", "each", "bx", None]),
                              "description": (cp if (use_xref and cp) else row["description"]),
                              "customer_part": cp if use_xref else None})
            rid = f"rq_{len(rfqs)+1}"
            rfqs.append({"id": rid, "customer_id": cust["id"], "at": iso(when),
                         "source": R.choice(["email body", "PDF", "spreadsheet", "photo"]),
                         "lines": lines, "quoted_at": iso(when + timedelta(hours=R.choice(
                             [2, 6, 20, 48, 72])))})

            # historical quote with an outcome, so the margin ledger has data
            total = round(R.uniform(180, 24000), 2)
            depth = R.choice([0.02, 0.06, 0.09, 0.14, 0.22, 0.31])
            ta = R.choice([2, 3, 8, 20, 30, 52, 96])
            won = R.random() < (0.22 + depth * 0.6 + (0.18 if ta < 8 else 0))
            fam = R.choice(list(FAMILIES))
            quotes.append({
                "id": f"q_{len(quotes)+1}", "rfq_id": rid, "customer_id": cust["id"],
                "customer": cust["name"], "created_at": iso(when),
                "sent_at": iso(when + timedelta(hours=ta)),
                "total": total, "discount_depth": depth, "turnaround_hours": ta,
                "state": "won" if won else "lost",
                "loss_reason": None if won else R.choice(core.LOSS_REASONS),
                "decided_at": iso(when + timedelta(days=R.randint(1, 20))),
                "lines": [{"sku": R.choice(catalog)["sku"], "family": fam, "qty": 1,
                           "unit": total, "uom": "ea"}],
                "touches": []})

    # -- the live demo set --------------------------------------------------
    demo_cust = customers[0]
    demo_xref = next(x for x in xref if x["customer_id"] == demo_cust["id"])
    demo_rfq = {
        "id": "rq_demo", "customer_id": demo_cust["id"], "at": iso(t0 - timedelta(hours=1)),
        "source": "PDF with their own part numbers", "demo_tag": "the messy one",
        "lines": [
            {"qty": 24, "uom": "EA", "description": demo_xref["customer_part"],
             "customer_part": demo_xref["customer_part"]},
            {"qty": 6, "uom": "each", "description": disc["description"], "customer_part": None},
            {"qty": 100, "uom": None, "description": "misc hardware as discussed",
             "customer_part": None},
            {"qty": 12, "uom": "bx", "description": catalog[10]["description"],
             "customer_part": None},
            {"qty": 2, "uom": None, "description": "part per drawing", "customer_part": None},
        ]}
    rfqs.append(demo_rfq)

    # a quote to reconcile a PO against, plus a discrepant PO
    q_demo = {"id": "q_demo", "rfq_id": "rq_demo", "customer_id": demo_cust["id"],
              "customer": demo_cust["name"], "created_at": iso(t0 - timedelta(days=3)),
              "sent_at": iso(t0 - timedelta(days=3)), "state": "sent",
              "ship_to": demo_cust["ship_to"], "terms": demo_cust["terms"],
              "lines": [{"sku": catalog[0]["sku"], "qty": 20, "unit": 24.50, "uom": "ea",
                         "family": catalog[0]["family"]},
                        {"sku": catalog[1]["sku"], "qty": 8, "unit": 61.00, "uom": "ea",
                         "family": catalog[1]["family"]},
                        {"sku": catalog[2]["sku"], "qty": 4, "unit": 118.25, "uom": "ea",
                         "family": catalog[2]["family"]},
                        {"sku": catalog[5]["sku"], "qty": 50, "unit": 3.10, "uom": "ea",
                         "family": catalog[5]["family"]}],
              "total": round(20 * 24.5 + 8 * 61 + 4 * 118.25 + 50 * 3.10, 2), "touches": []}
    quotes.append(q_demo)
    pos.append({"id": "po_demo", "quote_id": "q_demo", "number": "PO-44817",
                "at": iso(t0 - timedelta(hours=2)), "demo_tag": "line 4 quantity differs",
                "ship_to": demo_cust["ship_to"], "terms": demo_cust["terms"],
                "lines": [{"sku": catalog[0]["sku"], "qty": 20, "unit": 24.50, "uom": "ea"},
                          {"sku": catalog[1]["sku"], "qty": 8, "unit": 61.00, "uom": "ea"},
                          {"sku": catalog[2]["sku"], "qty": 4, "unit": 118.25, "uom": "ea"},
                          {"sku": catalog[5]["sku"], "qty": 500, "unit": 3.10, "uom": "ea"}]})
    pos.append({"id": "po_demo_clean", "quote_id": "q_demo", "number": "PO-44818",
                "at": iso(t0 - timedelta(hours=2)), "demo_tag": "reconciles cleanly",
                "ship_to": demo_cust["ship_to"], "terms": demo_cust["terms"],
                "lines": [dict(l) for l in q_demo["lines"]]})

    # background POs
    for i, q in enumerate(R.sample([q for q in quotes if q["state"] == "won"], 60)):
        bad = R.random() < 0.3
        lines = [dict(l) for l in q["lines"]]
        if bad and lines:
            lines[0]["qty"] = lines[0]["qty"] + R.choice([5, -2, 100])
        pos.append({"id": f"po_{i+1}", "quote_id": q["id"], "number": f"PO-{40000+i}",
                    "at": iso(t0 - timedelta(days=R.randint(0, 20))),
                    "ship_to": q.get("ship_to"), "terms": q.get("terms"), "lines": lines})

    store.save("rfqs", rfqs)
    store.save("quotes", quotes)
    store.save("pos", pos)
    store.save("orders", [])
    store.save("approvals", [])
    store.save("events", [])
    return {"catalog": len(catalog), "customers": len(customers), "xref": len(xref),
            "rfqs": len(rfqs), "quotes": len(quotes), "pos": len(pos)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rfqs", type=int, default=90)
    ap.add_argument("--weeks", type=int, default=52)
    a = ap.parse_args()
    print(build(a.rfqs, a.weeks))
