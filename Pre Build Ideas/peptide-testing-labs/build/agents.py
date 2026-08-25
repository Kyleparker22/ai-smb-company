#!/usr/bin/env python3
"""Assay OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso


def intake(sample_id):
    """Log a received sample and open its chain of custody."""
    s = store.by_id("samples", sample_id)
    if not s:
        return {"error": "no such sample"}
    gate.act("log_sample", "intake", sample_id, {"lot": s.get("client_lot")})
    return {"sample": sample_id, "custody": core.custody_complete(s)}


def grade_sample(sample_id):
    """Grade against the published spec. Deterministic, and it always shows why."""
    r = next((x for x in store.load("results") if x.get("sample_id") == sample_id), None)
    g = core.grade(r)
    gate.act("grade_result", "analyst", sample_id,
             {"grade": g["grade"], "reasons": g["reasons"]})
    return {"sample": sample_id, "result": r, **g}


def draft_coa(sample_id):
    """Prepare a certificate. It is a DRAFT — it has no token a stranger can look
    up until a named human releases it, so a leaked draft cannot masquerade as
    an issued certificate."""
    s = store.by_id("samples", sample_id)
    if not s:
        return {"error": "no such sample"}
    cust = core.custody_complete(s)
    if not cust["complete"]:
        ev = store.log_event("refused", sample_id, "agent:coa", "R0",
                             {"action": "draft_coa", "missing_custody": cust["missing"]})
        return {"refused": "chain of custody is incomplete", "missing": cust["missing"],
                "why": "a certificate over a broken custody chain is not evidence of anything",
                "event": ev["id"]}
    r = next((x for x in store.load("results") if x.get("sample_id") == sample_id), None)
    if not r:
        return {"refused": "no analytical result recorded", "why": "nothing to certify"}
    g = core.grade(r)
    existing = [c for c in store.load("coas")
                if c.get("sample_id") == sample_id and c.get("state") == "draft"]
    if existing:
        return {"coa": existing[0]["id"], "state": "draft", "grade": g["grade"],
                "note": "a draft already exists for this sample"}
    row = {"id": store.nid("coa"), "sample_id": sample_id, "token": None, "state": "draft",
           "grade": g["grade"], "reasons": g["reasons"], "hash": None,
           "created_at": iso(), "released_at": None, "released_by": None,
           "superseded_by": None}
    store.upsert("coas", row)
    res = gate.act("draft_coa", "coa", sample_id, {"coa": row["id"], "grade": g["grade"]})
    return {"coa": row["id"], "state": "draft", "grade": g["grade"],
            "reasons": g["reasons"], "approval": res.get("approval"),
            "why": res.get("reason")}


def release_coa(coa_id, human):
    """Release. This is the only place a token and a hash come into existence,
    and it is permanently R1 — a person's name goes on every certificate."""
    c = store.by_id("coas", coa_id)
    if not c or c.get("state") != "draft":
        return {"error": "no draft certificate with that id"}
    s = store.by_id("samples", c["sample_id"]) or {}
    r = next((x for x in store.load("results") if x.get("sample_id") == c["sample_id"]), {})
    payload = core.coa_payload(s, r)
    c.update(state="released", token=f"COA-{store.nid('t').split('_')[1][:8].upper()}",
             hash=core.coa_hash(payload), released_at=iso(), released_by=human,
             grade=payload["grade"])
    store.upsert("coas", c)
    store.log_event("release_coa", c["sample_id"], f"human:{human}", "R1",
                    {"coa": coa_id, "token": c["token"], "grade": c["grade"]})
    return {"coa": coa_id, "token": c["token"], "grade": c["grade"], "hash": c["hash"],
            "state": "released", "scope": core.SCOPE_NOTE}


def supersede(coa_id, human, reason):
    """A correction is a NEW certificate. The old one stays looked-up-able and
    says it was replaced — because deleting it is how a lab loses the argument
    about what it said and when."""
    old = store.by_id("coas", coa_id)
    if not old or old.get("state") != "released":
        return {"error": "only a released certificate can be superseded"}
    new = draft_coa(old["sample_id"])
    if "coa" not in new:
        return new
    rel = release_coa(new["coa"], human)
    old.update(state="superseded", superseded_by=new["coa"])
    store.upsert("coas", old)
    store.log_event("coa_superseded", old["sample_id"], f"human:{human}", "R1",
                    {"old": coa_id, "new": new["coa"], "reason": reason})
    return {"superseded": coa_id, "replacement": new["coa"], "token": rel.get("token"),
            "reason": reason,
            "note": "the original certificate is retained and reports itself as superseded"}


def answer_client(text):
    """Clients ask the lab what a number means for their product. That is the
    question a testing lab must not answer, and it is refused by class, not by
    keyword luck."""
    gate.act("interpret_for_health", "support", "inbound", {"asked": text[:120]})
    return {"refused": True,
            "reply": ("We report what we measured in the sample you sent. We cannot tell you "
                      "whether a product is safe to use, suitable for any purpose, or how it "
                      "compares to any other lot."),
            "scope": core.SCOPE_NOTE,
            "why": "interpretation for health is outside a testing lab's scope, permanently"}


def run_all():
    """The sweep: intake anything unlogged, grade anything with a result, draft
    certificates for anything gradeable. Release is never in the sweep."""
    out = {"intake": 0, "graded": 0, "drafted": 0, "blocked": []}
    results = {r["sample_id"] for r in store.load("results")}
    have_coa = {c["sample_id"] for c in store.load("coas")}
    for s in store.load("samples"):
        if s["id"] not in results:
            intake(s["id"])
            out["intake"] += 1
            continue
        if s["id"] in have_coa:
            continue
        grade_sample(s["id"])
        out["graded"] += 1
        d = draft_coa(s["id"])
        if d.get("refused"):
            out["blocked"].append({"sample": s["id"], "why": d["refused"]})
        else:
            out["drafted"] += 1
    out["note"] = "release is never swept — a certificate leaves only on a human click"
    return out
