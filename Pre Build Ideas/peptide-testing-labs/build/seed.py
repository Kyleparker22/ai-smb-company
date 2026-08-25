#!/usr/bin/env python3
"""Assay OS — synthetic seed. Deterministic: same seed, same lab, every run."""
import random, sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import coa_hash, coa_payload, grade, store
from _kit.store import iso, now

R = random.Random(8895)

BRANDS = ["Northlake Research", "Corvid Biosciences", "Halcyon Supply Co", "Meridian Peptide",
          "Ashgrove Labs", "Vector Chemical", "Bright Harbor Research", "Kestrel Compounds",
          "Ninebark Scientific", "Ardent Research Supply", "Cobalt Line", "Fenwick Biologics"]
ANALYTES = ["BPC-157", "TB-500", "GHK-Cu", "Semax", "Selank", "Ipamorelin", "CJC-1295",
            "Thymosin alpha-1", "Epithalon", "KPV"]
INSTRUMENTS = ["HPLC-UV #1", "HPLC-UV #2", "LC-MS #1", "LC-MS #2"]
CUSTODY = ("received", "logged", "aliquoted", "analysed")


def build(n_samples=240):
    store.wipe()
    store.save("config", {
        "company": "Rivermark Analytical",
        "kind": "Third-party analytical testing lab",
        "staff": "6 (2 analysts, 1 QA, 1 lab manager, 2 sample handling)",
        "revenue": "~$1.4M/yr",
        "note": "SYNTHETIC DEMONSTRATION DATA — no real lab, client, sample or result.",
    })

    clients = []
    for i, b in enumerate(BRANDS):
        clients.append({"id": f"cl{i+1:02d}", "name": b,
                        "since": iso(now() - timedelta(days=R.randint(60, 900))),
                        "terms": R.choice(["net-15", "net-30", "prepaid"])})
    store.save("clients", clients)

    samples, results, coas = [], [], []
    for i in range(n_samples):
        age_days = R.randint(0, 120)
        received = now() - timedelta(days=age_days, hours=R.randint(0, 23))
        c = R.choice(clients)
        sid = f"S{2600 + i}"
        # Most samples are clean; this market's whole problem is the ones that aren't.
        roll = R.random()
        if roll < 0.72:
            res = {"purity_pct": round(R.uniform(98.2, 99.9), 2), "identity_match": True,
                   "water_pct": round(R.uniform(1.5, 7.4), 2), "acetate_pct": round(R.uniform(3.0, 13.5), 2)}
        elif roll < 0.86:
            res = {"purity_pct": round(R.uniform(88.0, 97.9), 2), "identity_match": True,
                   "water_pct": round(R.uniform(2.0, 9.5), 2), "acetate_pct": round(R.uniform(4.0, 17.0), 2)}
        elif roll < 0.93:
            res = {"purity_pct": round(R.uniform(40.0, 96.0), 2), "identity_match": False,
                   "water_pct": round(R.uniform(3.0, 12.0), 2), "acetate_pct": round(R.uniform(5.0, 20.0), 2)}
        else:
            # partial panels — the INDETERMINATE population, deliberately present
            res = {"purity_pct": round(R.uniform(97.0, 99.8), 2), "identity_match": True,
                   "water_pct": None, "acetate_pct": round(R.uniform(4.0, 12.0), 2)}

        steps_done = CUSTODY if age_days > 2 or R.random() < 0.8 else CUSTODY[:R.randint(1, 3)]
        custody = [{"step": s, "at": iso(received + timedelta(hours=j * R.randint(1, 6))),
                    "by": R.choice(["k.mora", "d.ellis", "s.vance"])}
                   for j, s in enumerate(steps_done)]

        samples.append({"id": sid, "client": c["name"], "client_id": c["id"],
                        "client_lot": f"{R.choice(['LOT','B','R'])}{R.randint(1000,9999)}",
                        "analyte": R.choice(ANALYTES),
                        "received_at": iso(received), "custody": custody,
                        "price": R.choice([120, 145, 165, 185, 210]),
                        "rush": R.random() < 0.15})

        # Older samples have results and released certificates; recent ones are in flight.
        if age_days > 1:
            run_at = iso(received + timedelta(hours=R.randint(6, 70)))
            results.append({"sample_id": sid, "run_at": run_at,
                            "instrument": R.choice(INSTRUMENTS),
                            "analyst": R.choice(["k.mora", "d.ellis"]), **res})
            if age_days > 3 and len(custody) == 4:
                s_row = samples[-1]
                r_row = results[-1]
                payload = coa_payload(s_row, r_row)
                released = received + timedelta(hours=R.randint(20, 96))
                coas.append({"id": store.nid("coa"), "sample_id": sid,
                             "token": f"COA-{R.randint(10**7, 10**8-1)}",
                             "state": "released", "grade": grade(r_row)["grade"],
                             "reasons": grade(r_row)["reasons"], "hash": coa_hash(payload),
                             "created_at": run_at, "released_at": iso(released),
                             "released_by": R.choice(["s.vance", "lab.manager"]),
                             "superseded_by": None})

    store.save("samples", samples)
    store.save("results", results)
    store.save("coas", coas)
    store.save("approvals", [])
    store.save("events", [])

    # A truthful starting log: the released certificates actually happened.
    for c in coas:
        store.log_event("log_sample", c["sample_id"], "agent:intake", "R3", {})
        store.log_event("grade_result", c["sample_id"], "agent:analyst", "R2",
                        {"grade": c["grade"]})
        store.log_event("draft_coa", c["sample_id"], "agent:coa", "R1", {"coa": c["id"]})
        store.log_event("release_coa", c["sample_id"], f"human:{c['released_by']}", "R1",
                        {"coa": c["id"], "token": c["token"], "grade": c["grade"]})

    print(f"seeded {len(samples)} samples · {len(results)} results · {len(coas)} released certificates")
    print(f"  in flight: {len(samples) - len(coas)}")
    return {"samples": len(samples), "coas": len(coas)}


if __name__ == "__main__":
    build()
