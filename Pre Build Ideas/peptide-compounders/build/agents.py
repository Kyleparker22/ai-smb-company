#!/usr/bin/env python3
"""Provenance OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso


def sweep_changes():
    """Read the source list, map each change onto the SKU list, flag what lands."""
    skus = store.load("skus")
    flagged, clear = [], 0
    for c in store.load("changes"):
        if c.get("reviewed_at"):
            continue
        gate.act("watch_sources", "watcher", c["id"], {"source": c.get("source")})
        i = core.impact(c, skus)
        if i["n"]:
            gate.act("flag_impact", "watcher", c["id"],
                     {"affected": [h["sku"] for h in i["affected"]], "severity": c.get("severity")})
            flagged.append({"change": c["id"], "title": c.get("title"),
                            "severity": c.get("severity"), "affected": i["affected"]})
        else:
            clear += 1
    return {"flagged": flagged, "cleared": clear, "scope": core.WATCH_SCOPE,
            "note": "flags relevance for a human read — it never decides status"}


def assemble(batch_id):
    d = core.dossier(batch_id)
    if "error" in d:
        return d
    gate.act("assemble_dossier", "qa", batch_id,
             {"missing": d["records_missing"], "complete": d["complete"]})
    return d


def check_supplier(coa_id):
    v = core.verify_supplier_coa(coa_id)
    if "error" in v:
        return v
    c = store.by_id("supplier_coas", coa_id)
    c["state"] = v["state"]
    c["checked_at"] = iso()
    store.upsert("supplier_coas", c)
    gate.act("verify_supplier_coa", "qa", coa_id,
             {"state": v["state"], "problems": v["problems"]})
    return v


def release_batch(batch_id, human):
    """Release a lot for sale. Permanently R1: a named person owns this, and the
    packet must actually be complete first — the gate cannot be talked past."""
    d = core.dossier(batch_id)
    if "error" in d:
        return d
    if not d["complete"]:
        ev = store.log_event("refused", batch_id, "agent:qa", "R0",
                             {"action": "release_batch", "blockers": d["blockers"]})
        return {"refused": "the batch packet is incomplete", "blockers": d["blockers"],
                "why": "a lot is not released over a packet with holes in it",
                "event": ev["id"]}
    b = store.by_id("batches", batch_id)
    b.update(released_at=iso(), released_by=human)
    store.upsert("batches", b)
    store.log_event("release_batch", batch_id, f"human:{human}", "R1",
                    {"lot": b.get("lot"), "sku": b.get("sku")})
    return {"batch": batch_id, "lot": b.get("lot"), "released_by": human,
            "note": "released against a complete packet"}


def intake_complaint(text, who="customer"):
    """Capture a report completely. An adverse event is logged and routed and is
    never assessed — the reply says so rather than pretending to help."""
    c = core.classify_complaint(text)
    row = {"id": store.nid("cx"), "at": iso(), "text": text, "from": who,
           "label": c["label"], "route": c["route"], "assessed": False}
    store.upsert("complaints", row)
    gate.act("log_complaint", "intake", row["id"], {"label": c["label"]})
    out = {"complaint": row["id"], **c}
    if c["label"] == "adverse_event":
        ev = store.log_event("refused", row["id"], "agent:intake", "R0",
                             {"action": "assess_adverse_event", "why": c["why"]})
        out.update(refused="no assessment of any kind was made",
                   reply=core.COMPLAINT_SCRIPT, event=ev["id"],
                   escalated="QA and the responsible person, immediately")
    return out


def answer_compliance_question(text):
    """'Are we compliant?' is the question the system must never answer."""
    gate.act("assert_compliance", "watcher", "inbound", {"asked": text[:120]})
    return {"refused": True,
            "reply": ("This system flags source changes that name something on your product list. "
                      "It cannot tell you whether you are compliant — that is a determination for "
                      "your QA function and your counsel."),
            "scope": core.WATCH_SCOPE,
            "why": "stating compliance is outside what any monitoring tool can honestly do"}


def run_all():
    out = {"changes": sweep_changes(), "packets": 0, "supplier_checks": 0, "blocked": []}
    for b in store.load("batches"):
        d = assemble(b["id"])
        out["packets"] += 1
        if not d["complete"]:
            out["blocked"].append({"batch": b["id"], "blockers": d["blockers"]})
    for c in store.load("supplier_coas"):
        if not c.get("checked_at"):
            check_supplier(c["id"])
            out["supplier_checks"] += 1
    out["note"] = "release is never swept — a lot leaves on a named human's decision"
    return out
