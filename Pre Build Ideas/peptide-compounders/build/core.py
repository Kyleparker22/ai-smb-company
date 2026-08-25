#!/usr/bin/env python3
"""Provenance OS — domain core (peptide compounder / supplier).

Three things break this kind of business, and none of them is lead flow:

  1. **The rulebook moves.** Eligibility, permitted claims and route restrictions
     change under the business, and nobody is watching the sources against the
     actual SKU list. A change that lands on one product is invisible until it is
     expensive.
  2. **The paperwork is the asset.** Batch records, stability data and upstream
     supplier certificates are what survive an inspection — and they live in
     folders nobody can assemble under time pressure.
  3. **Complaints arrive as clinical questions.** An adverse-event report must be
     captured completely and never assessed by software.

What this core will not do: state that anything is compliant, interpret a
complaint, or edit a batch record. Those refusals are the product.

Stdlib only. Honesty rules come from `_kit`.
"""
import re, sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, days_until, iso,    # noqa: E402
                        median, now, parse, unmeasured)

TABLES = ("config", "skus", "batches", "suppliers", "supplier_coas",
          "changes", "complaints", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="PROVOS_DATA_ROOT")

# Said whenever the watcher reports. The system flags *relevance*, never status.
WATCH_SCOPE = ("This flags source changes that mention something on your product list. It is a "
               "reading aid, not a legal determination — it cannot tell you whether you are "
               "compliant, and it is not a substitute for your counsel or your QA function.")

COMPLAINT_SCRIPT = ("Thank you — we have logged this report. We are not able to give medical advice "
                    "or assess a health outcome. If you are experiencing a medical problem, contact "
                    "a healthcare professional now; if it is urgent, seek emergency care.")


# ---------------------------------------------------------------- the rulebook watcher

# A change matters to a SKU when it touches that SKU's analyte, its route of
# administration, or a claim the SKU makes. Deliberately over-inclusive: a false
# flag costs a QA read, a missed one costs the product line.
def impact(change, skus):
    """Which SKUs a source change plausibly touches, and why."""
    text = f"{change.get('title','')} {change.get('summary','')}".lower()
    hits = []
    for s in skus:
        why = []
        analyte = (s.get("analyte") or "").lower()
        if analyte and analyte in text:
            why.append(f"names {s['analyte']}")
        for term in (s.get("aliases") or []):
            if term.lower() in text and f"names {s['analyte']}" not in why:
                why.append(f"names {term}, an alias of {s['analyte']}")
        route = (s.get("route") or "").lower()
        if route and re.search(rf"\b{re.escape(route)}\b", text):
            why.append(f"restricts the {s['route']} route")
        for claim in (s.get("claims") or []):
            if claim.lower() in text:
                why.append(f"touches the claim “{claim}”")
        if (s.get("category") or "").lower() and (s.get("category") or "").lower() in text:
            why.append(f"names the {s['category']} category")
        if why:
            hits.append({"sku": s["id"], "name": s.get("name"), "why": why})
    return {"change": change.get("id"), "severity": change.get("severity"),
            "affected": hits, "n": len(hits),
            "verdict": "affects your list" if hits else "no product on your list is named",
            "scope": WATCH_SCOPE}


def open_changes():
    skus = store.load("skus")
    out = []
    for c in store.load("changes"):
        if c.get("reviewed_at"):
            continue
        i = impact(c, skus)
        out.append({**c, "impact": i, "affected_n": i["n"]})
    out.sort(key=lambda c: (-c["affected_n"], c.get("published_at") or ""))
    return out


# ---------------------------------------------------------------- batch records

REQUIRED_RECORDS = ("formula", "weighing", "compounding_log", "yield",
                    "stability", "supplier_coa", "release_test")


def dossier(batch_id):
    """Assemble everything that exists for a batch and name what does not.

    The refusal that matters: a missing document is reported as MISSING. This
    never returns 'complete' by omission, because an inspection-ready packet
    that quietly drops a section is worse than no packet.
    """
    b = store.by_id("batches", batch_id)
    if not b:
        return {"error": "no such batch"}
    have = {r["kind"]: r for r in (b.get("records") or [])}
    missing = [k for k in REQUIRED_RECORDS if k not in have]
    sup = next((c for c in store.load("supplier_coas")
                if c.get("id") == b.get("supplier_coa_id")), None)
    sup_state = "missing" if not sup else sup.get("state", "unverified")
    return {
        "batch": batch_id, "lot": b.get("lot"), "sku": b.get("sku"),
        "made_at": b.get("made_at"), "quantity": b.get("quantity"),
        "records_present": sorted(have), "records_missing": missing,
        "complete": not missing and sup_state == "verified",
        "supplier_coa": sup_state,
        "blockers": ([f"missing {m}" for m in missing] +
                     ([] if sup_state == "verified" else [f"upstream certificate is {sup_state}"])),
        "note": ("a packet is complete only when every required record exists AND the upstream "
                 "certificate has been verified — never by omission"),
    }


def verify_supplier_coa(coa_id):
    """Check an incoming certificate rather than filing it.

    A supplier certificate whose analyte or lot does not match what was received
    is the classic upstream failure, and it is caught here by comparison, not by
    trust."""
    c = store.by_id("supplier_coas", coa_id)
    if not c:
        return {"error": "no such certificate"}
    problems = []
    if not c.get("issuer"):
        problems.append("no issuing laboratory named")
    if c.get("analyte") and c.get("claimed_analyte") and c["analyte"] != c["claimed_analyte"]:
        problems.append(f"certificate is for {c['analyte']}, the material was received as "
                        f"{c['claimed_analyte']}")
    if c.get("lot") and c.get("received_lot") and c["lot"] != c["received_lot"]:
        problems.append(f"certificate lot {c['lot']} does not match received lot {c['received_lot']}")
    if c.get("purity_pct") is None:
        problems.append("no purity value reported")
    exp = days_until(c.get("expires_at")) if c.get("expires_at") else None
    if exp is not None and exp < 0:
        problems.append(f"certificate expired {abs(exp)} days ago")
    return {"coa": coa_id, "issuer": c.get("issuer"), "ok": not problems,
            "problems": problems,
            "state": "verified" if not problems else "rejected",
            "note": "an unverifiable upstream certificate blocks the batch packet"}


# ---------------------------------------------------------------- complaints

# A trailing \b after a PREFIX (e.g. `\b(vomit)\b`) can never match "vomiting" —
# there is no boundary between "vomit" and "ing". Prefixes carry \w* explicitly.
# Caught by the Protocol OS suite on the same pattern and fixed here too.
ADVERSE = (r"\b(reaction|rash|hives|swollen|chest pain|hospital|emergency|fever|"
           r"abscess|passed out|fainted|dizzy|palpitations)\b|"
           r"\bshort(ness)? of breath\b|\bheart (rate|racing)\b|"
           r"\bswell\w*|\bbreath\w*|\binfect\w*|\bvomit\w*|\bnause\w*|\bnumb\w*")
PRODUCT = (r"\b(cloudy|broken|cracked|seal|short fill|underfill)\b|"
           r"\bcrystals?\b|\bdiscolou?r\w*|\bleak\w*|\bmislabel\w*|"
           r"\bwrong (label|product|vial)\b")


def classify_complaint(text):
    t = (text or "").lower()
    if re.search(ADVERSE, t):
        return {"label": "adverse_event",
                "why": "the report describes a health outcome — captured, never assessed here",
                "route": "QA + the responsible person, immediately"}
    if re.search(PRODUCT, t):
        return {"label": "product_quality",
                "why": "the report describes the product itself, not a person",
                "route": "QA investigation against the batch record"}
    return {"label": "other", "why": "no adverse or product-quality signal matched",
            "route": "customer service"}


# ---------------------------------------------------------------- eval

watcher_eval = Eval(
    "regulatory change relevance",
    costly_label="affects",
    costly_note=("A CHANGE THAT TOUCHES A LIVE PRODUCT AND IS FILED AS IRRELEVANT is the error "
                 "this module exists to prevent — the business finds out from a letter instead. "
                 "Over-flagging costs a QA read and is the deliberate bias."))

EVAL_SKUS = [
    {"id": "k1", "name": "Alpha", "analyte": "Semaglutide", "aliases": ["GLP-1"],
     "route": "injection", "claims": ["weight management"], "category": "compounded"},
    {"id": "k2", "name": "Beta", "analyte": "Tirzepatide", "aliases": [],
     "route": "injection", "claims": [], "category": "compounded"},
]
EVAL_CASES = [
    {"input": {"title": "Guidance on compounded semaglutide products",
               "summary": "addresses compounded semaglutide"}, "label": "affects"},
    {"input": {"title": "GLP-1 marketing claims", "summary": "weight management claims reviewed"},
     "label": "affects"},
    {"input": {"title": "Tirzepatide bulk substance status", "summary": "tirzepatide"}, "label": "affects"},
    {"input": {"title": "Injection route restrictions", "summary": "products for injection"}, "label": "affects"},
    {"input": {"title": "Compounded product labelling", "summary": "compounded preparations"}, "label": "affects"},
    {"input": {"title": "Veterinary feed directive update", "summary": "livestock feed"}, "label": "clear"},
    {"input": {"title": "Sunscreen monograph revision", "summary": "OTC sunscreen actives"}, "label": "clear"},
    {"input": {"title": "Medical device UDI deadline", "summary": "device identifiers"}, "label": "clear"},
]


def run_eval():
    def predict(ch):
        return "affects" if impact(ch, EVAL_SKUS)["n"] else "clear"
    return watcher_eval.run(EVAL_CASES, predict)


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "watch_sources":        {"rung": "R3", "reason": "reading published sources changes nothing"},
    "flag_impact":          {"rung": "R2", "reason": "flags for a human read and shows its reasoning; over-flagging is the deliberate bias"},
    "assemble_dossier":     {"rung": "R3", "reason": "collects documents that already exist and names what is missing"},
    "verify_supplier_coa":  {"rung": "R2", "reason": "a comparison against what was received, fully shown"},
    "log_complaint":        {"rung": "R3", "reason": "capturing a report completely is the compliance obligation"},
    "release_batch":        {"rung": "R1", "reason": "releasing a lot for sale is a quality decision a named person owns",
                             "never_promote": True},
    "alter_batch_record":   {"rung": "R0", "reason": "a batch record is the inspection artifact; software never edits it",
                             "never_promote": True},
    "assert_compliance":    {"rung": "R0", "reason": "no system here may state that the business is compliant with anything",
                             "never_promote": True},
    "assess_adverse_event": {"rung": "R0", "reason": "assessing a health outcome is a clinical act; this system captures and routes only",
                             "never_promote": True},
    "notify_customer":      {"rung": "R1", "reason": "outward message — a human sends"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- counted reads

def packet_readiness(floor=8):
    batches = store.load("batches")
    if len(batches) < floor:
        return unmeasured(f"only {len(batches)} batches on file — need {floor}",
                          field="ready_rate", n=len(batches))
    ready = sum(1 for b in batches if dossier(b["id"])["complete"])
    return {"ready_rate": round(ready / len(batches), 3), "ready": ready,
            "batches": len(batches),
            "note": "counted by assembling every packet, not by asking anyone"}


def review_lag(floor=6):
    done = [c for c in store.load("changes") if c.get("reviewed_at") and c.get("published_at")]
    if len(done) < floor:
        return unmeasured(f"only {len(done)} reviewed changes — need {floor}",
                          field="median_days", n=len(done))
    gaps = []
    for c in done:
        a, b = parse(c["published_at"]), parse(c["reviewed_at"])
        if a and b:
            gaps.append((b - a).days)
    if not gaps:
        return unmeasured("reviewed changes carry no usable dates", field="median_days")
    return {"median_days": round(median(gaps), 1), "n": len(gaps),
            "note": "published to reviewed, counted"}


def roi_model():
    return (Roi("Provenance OS — what it computes to")
        .line("Packet assembly time", "time_saved", "hrs/packet × packets/yr × rate",
              ["packet_hours", "packets_year", "staff_rate"],
              lambda g: float(g["packet_hours"]) * float(g["packets_year"]) * float(g["staff_rate"]),
              note="reported separately; never summed into revenue")
        .line("Source-monitoring time", "time_saved", "hrs/wk × 52 × rate",
              ["watch_hours_wk", "staff_rate"],
              lambda g: float(g["watch_hours_wk"]) * 52 * float(g["staff_rate"]))
        .line("Upstream certificate checking", "time_saved", "min/lot × lots/yr ÷ 60 × rate",
              ["coa_minutes", "lots_year", "staff_rate"],
              lambda g: float(g["coa_minutes"]) * float(g["lots_year"]) / 60.0 * float(g["staff_rate"]))
        .line("A rule change caught before it lands", "scenario",
              "you decide what this is worth",
              ["change_value"], lambda g: float(g["change_value"]),
              assumption=("we will not put a number on a prevented regulatory event — prevented "
                          "incidents cannot be counted, and borrowing an industry figure here "
                          "would be inventing your exposure for you")))


def roi(given):
    rec = {}
    lots = store.load("batches")
    if len(lots) >= 8:
        rec["lots_year"] = len(lots)
        rec["packets_year"] = len(lots)
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("watch_sources", "flag_impact", "assemble_dossier", "verify_supplier_coa",
          "log_complaint", "release_batch", "notify_customer")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("customer:",))
