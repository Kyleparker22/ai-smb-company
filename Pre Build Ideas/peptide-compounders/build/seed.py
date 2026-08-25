#!/usr/bin/env python3
"""Provenance OS — synthetic seed. Deterministic."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import REQUIRED_RECORDS, store
from _kit.store import iso, now

R = random.Random(8896)

SKUS = [
    ("Semaglutide 2.5mg/mL", "Semaglutide", ["GLP-1"], "injection", ["weight management"]),
    ("Tirzepatide 5mg/mL", "Tirzepatide", ["GIP/GLP-1"], "injection", ["weight management"]),
    ("BPC-157 5mg", "BPC-157", ["pentadecapeptide"], "injection", []),
    ("Sermorelin 15mg", "Sermorelin", [], "injection", []),
    ("Glutathione 200mg/mL", "Glutathione", [], "injection", []),
    ("NAD+ 100mg/mL", "NAD+", ["nicotinamide adenine dinucleotide"], "infusion", []),
    ("Methylcobalamin 1mg/mL", "Methylcobalamin", ["B12"], "injection", []),
    ("Ipamorelin 5mg", "Ipamorelin", [], "injection", []),
]
SOURCES = ["federal register", "agency guidance", "state board bulletin", "compendial update",
           "warning letter digest"]
CHANGES = [
    ("Guidance on compounded semaglutide preparations", "addresses compounded semaglutide products", "high"),
    ("Bulk drug substance nominations — tirzepatide", "tirzepatide nomination status", "high"),
    ("Marketing claims for GLP-1 preparations", "weight management claims under review", "high"),
    ("Sterile injection facility standards", "products for injection, sterility assurance", "medium"),
    ("Labelling of compounded preparations", "compounded preparation labelling", "medium"),
    ("Infusion clinic supervision requirements", "infusion services supervision", "medium"),
    ("Methylcobalamin sourcing note", "methylcobalamin bulk sourcing", "low"),
    ("Sermorelin compounding eligibility question", "sermorelin eligibility", "high"),
    ("Veterinary feed directive revision", "livestock feed directives", "low"),
    ("Sunscreen monograph revision", "OTC sunscreen active ingredients", "low"),
    ("Medical device UDI compliance dates", "unique device identifiers", "low"),
    ("Pharmacy technician ratio rule", "technician supervision ratios", "medium"),
]


def build(n_batches=48):
    store.wipe()
    store.save("config", {
        "company": "Halden Compounding",
        "kind": "Compounding pharmacy / peptide supplier",
        "staff": "14 (3 pharmacists, 1 QA lead, 6 technicians, 4 admin)",
        "revenue": "~$6.2M/yr",
        "note": "SYNTHETIC DEMONSTRATION DATA — no real pharmacy, product, lot or report.",
    })

    skus = [{"id": f"sku{i+1:02d}", "name": n, "analyte": a, "aliases": al, "route": r,
             "claims": c, "category": "compounded", "active": True}
            for i, (n, a, al, r, c) in enumerate(SKUS)]
    store.save("skus", skus)

    suppliers = [{"id": f"sup{i+1}", "name": n, "country": c}
                 for i, (n, c) in enumerate([("Meridian API", "US"), ("Larkspur Chemical", "US"),
                                             ("Tancred Fine Chemicals", "DE"),
                                             ("Wexford Bulk", "US")])]
    store.save("suppliers", suppliers)

    coas, batches = [], []
    for i in range(n_batches):
        s = R.choice(skus)
        sup = R.choice(suppliers)
        made = now() - timedelta(days=R.randint(1, 300))
        cid = f"scoa{i+1:03d}"
        # Most upstream certificates are fine; a minority carry the classic faults.
        roll = R.random()
        coa = {"id": cid, "supplier": sup["name"], "issuer": "Rivermark Analytical",
               "analyte": s["analyte"], "claimed_analyte": s["analyte"],
               "lot": f"A{R.randint(1000,9999)}", "purity_pct": round(R.uniform(98.0, 99.9), 2),
               "expires_at": iso(made + timedelta(days=R.randint(200, 700))),
               "state": "unverified", "checked_at": None}
        coa["received_lot"] = coa["lot"]
        if roll < 0.08:
            coa["issuer"] = ""
        elif roll < 0.14:
            coa["received_lot"] = f"A{R.randint(1000,9999)}"
        elif roll < 0.19:
            coa["claimed_analyte"] = R.choice([x["analyte"] for x in skus if x["analyte"] != s["analyte"]])
        elif roll < 0.24:
            coa["purity_pct"] = None
        elif roll < 0.29:
            coa["expires_at"] = iso(now() - timedelta(days=R.randint(5, 200)))
        coas.append(coa)

        kinds = list(REQUIRED_RECORDS)
        if R.random() < 0.35:
            for _ in range(R.randint(1, 2)):
                if len(kinds) > 3:
                    kinds.remove(R.choice(kinds))
        batches.append({"id": f"B{4100+i}", "lot": f"L{R.randint(10000,99999)}",
                        "sku": s["name"], "sku_id": s["id"],
                        "made_at": iso(made), "quantity": R.choice([50, 100, 200, 250, 500]),
                        "supplier_coa_id": cid,
                        "records": [{"kind": k, "at": iso(made + timedelta(hours=j))}
                                    for j, k in enumerate(kinds)],
                        "released_at": None, "released_by": None})
    store.save("supplier_coas", coas)
    store.save("batches", batches)

    changes = []
    for i, (t, sm, sev) in enumerate(CHANGES):
        pub = now() - timedelta(days=R.randint(1, 90))
        reviewed = None
        if R.random() < 0.55:
            reviewed = iso(pub + timedelta(days=R.randint(1, 21)))
        changes.append({"id": f"ch{i+1:02d}", "source": R.choice(SOURCES), "title": t,
                        "summary": sm, "severity": sev, "published_at": iso(pub),
                        "reviewed_at": reviewed})
    store.save("changes", changes)
    store.save("complaints", [])
    store.save("approvals", [])
    store.save("events", [])

    for c in changes:
        if c["reviewed_at"]:
            store.log_event("watch_sources", c["id"], "agent:watcher", "R3", {})
            store.log_event("flag_impact", c["id"], "agent:watcher", "R2", {})
    for b in batches[:20]:
        store.log_event("assemble_dossier", b["id"], "agent:qa", "R3", {})

    print(f"seeded {len(skus)} SKUs · {len(batches)} batches · {len(coas)} upstream certificates "
          f"· {len(changes)} source changes")
    return {"batches": len(batches)}


if __name__ == "__main__":
    build()
