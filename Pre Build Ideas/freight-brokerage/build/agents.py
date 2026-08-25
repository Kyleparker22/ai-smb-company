#!/usr/bin/env python3
"""Carrier OS — the agents: vetting, offer triage, the check-call engine.

The asymmetry is enforced here as well as in the matrix: `vet()` can return a
refusal on its own authority, and there is no code path in this file that
approves a carrier or releases a load without a human decision row.

Stdlib only.
"""
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now, parse


# ---------------------------------------------------------------- 1 · vetting

def vet(carrier_id, load_id, ref=None):
    ref = ref or now()
    carrier = store.by_id("carriers", carrier_id)
    load = store.by_id("loads", load_id)
    if not carrier or not load:
        return {"error": "unknown carrier or load"}

    bench = core.benchmark(load.get("lane"), load.get("equipment"), ref)
    # The offer rate lives on the OFFER, not the load — without threading it in,
    # the rate tripwire can never fire, which is exactly what happened the first
    # time this was run against the seeded board.
    offer = next((o for o in store.load("offers")
                  if o["load_id"] == load_id and o["carrier_id"] == carrier_id), None)
    load_ctx = {**load, "offer_rate": (offer or {}).get("rate")}
    tf = core.trust_file(carrier, load_ctx, ref)
    fired = core.run_tripwires(carrier, load_ctx, {"benchmark": bench})
    gate.act("score_carrier", "vetting", carrier_id,
             {"summary": f"{carrier.get('name')} · score {tf['score']}", "load": load_id})

    for f in fired:
        store.upsert("tripwire_log", {"id": store.nid("tw"), "at": iso(ref),
                                      "carrier_id": carrier_id, "load_id": load_id,
                                      "tripwire": f["tripwire"], "evidence": f["evidence"],
                                      "hard_stop": f["hard_stop"]})
        gate.act("log_tripwire", "vetting", carrier_id,
                 {"summary": f"{f['tripwire']} — {f['evidence']}", "load": load_id})

    hard = [f for f in fired if f["hard_stop"]]
    weak = tf["score"] is not None and tf["score"] < 0.4
    if hard or weak or len(fired) >= 3:
        reasons = [f["evidence"] for f in fired] or [f"trust score {tf['score']}"]
        gate.act("refuse_carrier", "vetting", carrier_id,
                 {"summary": f"REFUSED for load {load_id}", "reasons": reasons, "load": load_id})
        return {"verdict": "refused", "trust": tf, "tripwires": fired, "benchmark": bench,
                "why": reasons,
                "note": "refused autonomously — refusing is the safe direction. This is NOT an "
                        "assertion that the carrier is fraudulent; it is a list of what fired and "
                        "the evidence each one fired on"}

    res = gate.act("approve_carrier", "vetting", carrier_id,
                   {"summary": f"{carrier.get('name')} cleared vetting for load {load_id} — "
                               f"score {tf['score']}", "load": load_id,
                    "tripwires": [f["tripwire"] for f in fired]})
    return {"verdict": "clean_for_human", "trust": tf, "tripwires": fired, "benchmark": bench,
            "gate": res,
            "note": "nothing fired and the score holds — but the system does NOT approve. A human "
                    "clicks, and that is permanent: this action is excluded from rung promotion"}


def sweep_offers(ref=None, limit=60):
    ref = ref or now()
    out = []
    for o in store.load("offers"):
        if o.get("vetted_at"):
            continue
        r = vet(o["carrier_id"], o["load_id"], ref)
        o["vetted_at"] = iso(ref)
        o["verdict"] = r.get("verdict")
        store.upsert("offers", o)
        out.append({"offer": o["id"], "verdict": r.get("verdict")})
        if len(out) >= limit:
            break
    return {"vetted": len(out),
            "refused": sum(1 for x in out if x["verdict"] == "refused")}


# ---------------------------------------------------------------- 2 · offer triage

def triage(load_id, ref=None):
    ref = ref or now()
    load = store.by_id("loads", load_id)
    if not load:
        return {"error": "no such load"}
    bench = core.benchmark(load.get("lane"), load.get("equipment"), ref)
    offers = [o for o in store.load("offers") if o["load_id"] == load_id]
    carriers = store.index("carriers")
    rows = []
    for o in offers:
        c = carriers.get(o["carrier_id"], {})
        load_ctx = {**load, "offer_rate": o["rate"]}
        tf = core.trust_file(c, load_ctx, ref)
        fired = core.run_tripwires(c, load_ctx, {"benchmark": bench})
        margin = (load.get("customer_rate") - o["rate"]) if load.get("customer_rate") else None
        rows.append({"offer": o["id"], "carrier": c.get("name"), "rate": o["rate"],
                     "margin": margin,
                     "margin_pct": round(margin / load["customer_rate"], 3)
                     if margin is not None and load.get("customer_rate") else None,
                     "trust": tf["score"], "tripwires": [f["tripwire"] for f in fired],
                     "hard_stop": any(f["hard_stop"] for f in fired),
                     "vs_benchmark": (None if bench.get("_missing")
                                      else round(o["rate"] / bench["median"] - 1, 3))})
    rows.sort(key=lambda r: (1 if r["hard_stop"] else 0, -(r["trust"] or 0), -(r["margin"] or 0)))
    gate.act("rank_offers", "triage", load_id,
             {"summary": f"{len(rows)} offers ranked on {load.get('lane')}"})
    return {"load": load, "benchmark": bench, "offers": rows,
            "note": ("no benchmark for this lane and equipment — the offers are still ranked by "
                     "trust and margin, but nothing here claims to know the market rate"
                     if bench.get("_missing") else
                     "ranked by hard stops, then trust, then margin")}


# ---------------------------------------------------------------- 3 · check calls

def check_calls(ref=None):
    ref = ref or now()
    collected, exceptions = 0, []
    for l in store.load("loads"):
        if l.get("state") != "in_transit":
            continue
        gate.act("collect_status", "tracking", l["id"],
                 {"summary": f"status request on {l['id']}"})
        collected += 1
        for e in core.load_exceptions(l, ref):
            gate.act("raise_exception", "tracking", l["id"],
                     {"summary": f"{e['label']} — {e['evidence']}", "severity": e["severity"]})
            draft = _customer_note(l, e)
            res = gate.act("notify_customer", "tracking", l["id"],
                           {"summary": f"customer note about {e['type']}", "preview": draft[:110]})
            exceptions.append({"load": l["id"], "customer": l.get("customer"), **e,
                               "customer_note": draft, "note_gate": res})
            store.upsert("checkcalls", {"id": store.nid("cc"), "load_id": l["id"], "at": iso(ref),
                                        "exception": e["type"], "evidence": e["evidence"]})
    exceptions.sort(key=lambda e: 0 if e["severity"] == "high" else 1)
    return {"collected": collected, "exceptions": exceptions[:40],
            "note": "the customer note is DRAFTED. What a customer is told about their freight is "
                    "the broker's word, not ours"}


def _customer_note(load, e):
    return (f"[FOR THE REP] {load.get('customer')} — load {load['id']} ({load.get('lane')}): "
            f"{e['label'].lower()}, {e['evidence']}. Suggested next move: {e['suggested']}.")


def run_all():
    return {"offers": sweep_offers(), "tracking": {"collected": check_calls()["collected"]}}
