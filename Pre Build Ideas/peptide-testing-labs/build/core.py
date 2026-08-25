#!/usr/bin/env python3
"""Assay OS — domain core (third-party analytical testing lab).

The lab's product is not the instrument run. It is the **certificate**, and in
this market certificates are routinely forged, recycled between lots, or edited
after the fact. So the two things this core exists to do are:

  1. Move a sample from received → result → released without the queue being
     the bottleneck, and
  2. Make the released certificate **checkable by a stranger** — a hash over the
     exact reported values, a token anyone can look up, and a superseded chain
     that never deletes what was said before.

What it deliberately will not do: interpret a result, answer whether a product
is safe to take, or release a certificate without a named human signing it.
Those are not features that were skipped; they are the reason a lab is trusted.

Stdlib only. Honesty rules come from `_kit`.
"""
import hashlib, json, sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                        # noqa: E402
from _kit.store import (Store, automation_rate, hours_between, iso,  # noqa: E402
                        median, now, parse, unmeasured)

TABLES = ("config", "clients", "samples", "results", "coas", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="ASSAYOS_DATA_ROOT")

# Said verbatim on every lookup and every certificate. A purity number is not a
# safety opinion, and the lab that blurs the two inherits liability it never priced.
SCOPE_NOTE = ("This certificate reports what was measured in the submitted sample only. "
              "It is not a safety assessment, not a fitness-for-use opinion, and not "
              "medical advice. It says nothing about any other unit or lot.")

# ---------------------------------------------------------------- specification

# Identity + purity thresholds, per analyte. A result is PASS only if it clears
# every applicable line; anything missing is INDETERMINATE, never a pass.
SPEC = {
    "purity_pct":     {"min": 98.0, "label": "chromatographic purity"},
    "identity_match": {"exact": True, "label": "mass identity confirmation"},
    "water_pct":      {"max": 8.0, "label": "water content"},
    "acetate_pct":    {"max": 15.0, "label": "residual acetate"},
}


def grade(result):
    """PASS / FAIL / INDETERMINATE, with the failing line named.

    INDETERMINATE exists on purpose. A missing assay is not a quiet pass — the
    single most consequential dishonesty available to a testing lab is letting an
    absent measurement read as a clean one.
    """
    if not result:
        return {"grade": "INDETERMINATE", "reasons": ["no result recorded"]}
    reasons, missing = [], []
    for field, rule in SPEC.items():
        v = result.get(field)
        if v is None:
            missing.append(rule["label"])
            continue
        if "min" in rule and float(v) < rule["min"]:
            reasons.append(f"{rule['label']} {v} below {rule['min']}")
        if "max" in rule and float(v) > rule["max"]:
            reasons.append(f"{rule['label']} {v} above {rule['max']}")
        if rule.get("exact") and not v:
            reasons.append(f"{rule['label']} did not confirm")
    if missing:
        return {"grade": "INDETERMINATE",
                "reasons": [f"not measured: {', '.join(missing)}"],
                "note": "an unmeasured line is never reported as a pass"}
    if reasons:
        return {"grade": "FAIL", "reasons": reasons}
    return {"grade": "PASS", "reasons": ["every specification line cleared"]}


# ---------------------------------------------------------------- the certificate

def coa_payload(sample, result):
    """The exact bytes the hash covers. Ordered and explicit so the same inputs
    always hash the same, on any machine, forever."""
    g = grade(result)
    return {
        "lab": store.load("config").get("company"),
        "sample_id": sample.get("id"),
        "client_lot": sample.get("client_lot"),
        "analyte": sample.get("analyte"),
        "received_at": sample.get("received_at"),
        "tested_at": result.get("run_at"),
        "instrument": result.get("instrument"),
        "purity_pct": result.get("purity_pct"),
        "identity_match": result.get("identity_match"),
        "water_pct": result.get("water_pct"),
        "acetate_pct": result.get("acetate_pct"),
        "grade": g["grade"],
        "scope": SCOPE_NOTE,
    }


def coa_hash(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"))
                          .encode()).hexdigest()


def verify(token):
    """The public lookup. Answers exactly one question — *did this lab issue this
    certificate, and is it still the current one* — and refuses the question it is
    always really being asked, which is whether the product is safe.
    """
    rows = [c for c in store.load("coas") if c.get("token") == token]
    if not rows:
        return {"status": "unknown", "token": token,
                "meaning": "no certificate with this identifier was ever issued by this lab",
                "scope": SCOPE_NOTE}
    c = rows[0]
    if c.get("state") == "draft":
        return {"status": "unknown", "token": token,
                "meaning": "no released certificate carries this identifier",
                "scope": SCOPE_NOTE}
    sample = store.by_id("samples", c["sample_id"]) or {}
    result = next((r for r in store.load("results") if r.get("sample_id") == c["sample_id"]), {})
    recomputed = coa_hash(coa_payload(sample, result))
    intact = (recomputed == c.get("hash"))
    out = {"status": "superseded" if c.get("state") == "superseded" else "genuine",
           "token": token, "issued_at": c.get("released_at"), "released_by": c.get("released_by"),
           "grade": c.get("grade"), "analyte": sample.get("analyte"),
           "client_lot": sample.get("client_lot"), "hash": c.get("hash"),
           "hash_intact": intact, "scope": SCOPE_NOTE}
    if c.get("state") == "superseded":
        out["superseded_by"] = c.get("superseded_by")
        out["meaning"] = ("this certificate was issued and then replaced — the record is kept, "
                          "not deleted; ask the holder for the current one")
    else:
        out["meaning"] = "issued by this lab and unchanged since release"
    if not intact:
        out["meaning"] = ("ISSUED BY THIS LAB BUT THE STORED VALUES NO LONGER HASH TO THE "
                          "RELEASED CERTIFICATE — treat as compromised and contact the lab")
    store.log_event("verification_lookup", token, "public:anon", "R3",
                    {"status": out["status"], "intact": intact})
    return out


# ---------------------------------------------------------------- the queue

def turnaround(window_days=90, floor=10):
    """Median hours received → released. Refuses below the floor rather than
    quoting a median off three samples."""
    cutoff = now() - timedelta(days=window_days)
    done = [c for c in store.load("coas")
            if c.get("released_at") and (parse(c["released_at"]) or now()) >= cutoff]
    if len(done) < floor:
        return unmeasured(f"only {len(done)} certificates released in {window_days} days — need {floor}",
                          field="median_hours", n=len(done))
    idx = store.index("samples")
    hrs = [hours_between(idx.get(c["sample_id"], {}).get("received_at"), c["released_at"])
           for c in done]
    hrs = [h for h in hrs if h is not None]
    if not hrs:
        return unmeasured("released certificates carry no received timestamp", field="median_hours")
    return {"median_hours": round(median(hrs), 1), "n": len(hrs),
            "slowest_hours": round(max(hrs), 1),
            "note": "counted from the sample log — received to release"}


def in_flight():
    """Everything not yet released, oldest first, with the stage it is stuck in."""
    released = {c["sample_id"] for c in store.load("coas") if c.get("state") == "released"}
    res = {r["sample_id"] for r in store.load("results")}
    rows = []
    for s in store.load("samples"):
        if s["id"] in released:
            continue
        stage = "awaiting result" if s["id"] not in res else "awaiting release"
        age = hours_between(s.get("received_at"), iso())
        rows.append({"sample": s["id"], "client": s.get("client"), "lot": s.get("client_lot"),
                     "analyte": s.get("analyte"), "stage": stage, "age_hours": age,
                     "custody_steps": len(s.get("custody") or [])})
    rows.sort(key=lambda r: -(r["age_hours"] or 0))
    return rows


def custody_complete(sample):
    """Chain of custody must be unbroken before anything can be released.
    A gap is a blocker, not a warning."""
    steps = sample.get("custody") or []
    need = ("received", "logged", "aliquoted", "analysed")
    have = [s.get("step") for s in steps]
    missing = [n for n in need if n not in have]
    return {"complete": not missing, "missing": missing, "steps": steps}


# ---------------------------------------------------------------- eval

false_pass_eval = Eval(
    "specification grading",
    costly_label="FAIL",
    costly_note=("A FAILING SAMPLE GRADED AS PASSING is the error that ends a testing lab. "
                 "It is reported on its own because an aggregate accuracy hides exactly the "
                 "one number a buyer is paying this lab to get right."))

EVAL_CASES = [
    {"input": {"purity_pct": 99.4, "identity_match": True, "water_pct": 4.1, "acetate_pct": 9.0}, "label": "PASS"},
    {"input": {"purity_pct": 98.0, "identity_match": True, "water_pct": 7.9, "acetate_pct": 14.9}, "label": "PASS"},
    {"input": {"purity_pct": 97.9, "identity_match": True, "water_pct": 3.0, "acetate_pct": 8.0}, "label": "FAIL"},
    {"input": {"purity_pct": 99.8, "identity_match": False, "water_pct": 3.0, "acetate_pct": 8.0}, "label": "FAIL"},
    {"input": {"purity_pct": 99.1, "identity_match": True, "water_pct": 9.2, "acetate_pct": 8.0}, "label": "FAIL"},
    {"input": {"purity_pct": 99.1, "identity_match": True, "water_pct": 4.0, "acetate_pct": 18.0}, "label": "FAIL"},
    {"input": {"purity_pct": 62.0, "identity_match": False, "water_pct": 12.0, "acetate_pct": 22.0}, "label": "FAIL"},
    {"input": {"purity_pct": 99.1, "identity_match": True, "water_pct": None, "acetate_pct": 8.0}, "label": "INDETERMINATE"},
    {"input": {"purity_pct": None, "identity_match": True, "water_pct": 4.0, "acetate_pct": 8.0}, "label": "INDETERMINATE"},
    {"input": {}, "label": "INDETERMINATE"},
]


def run_eval():
    return false_pass_eval.run(EVAL_CASES, lambda r: grade(r)["grade"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "log_sample":          {"rung": "R3", "reason": "clerical intake of a physical sample; fully reversible"},
    "advance_custody":     {"rung": "R3", "reason": "records a step that already happened, append-only"},
    "grade_result":        {"rung": "R2", "reason": "deterministic against a published spec, and the grade is shown with its reasons"},
    "draft_coa":           {"rung": "R1", "reason": "a draft certificate is one click from being a public claim"},
    "release_coa":         {"rung": "R1", "reason": "releasing a certificate is a public analytical claim carrying the lab's name",
                            "never_promote": True},
    "alter_result":        {"rung": "R0", "reason": "analytical values are never edited by software — a correction is a new certificate that supersedes",
                            "never_promote": True},
    "backdate_coa":        {"rung": "R0", "reason": "a certificate's dates are evidence; changing them is falsification",
                            "never_promote": True},
    "interpret_for_health": {"rung": "R0", "reason": "whether a substance is safe to use is not a testing lab's statement to make",
                             "never_promote": True},
    "notify_client":       {"rung": "R1", "reason": "outward message to a customer — a human sends"},
    "verification_lookup": {"rung": "R3", "reason": "read-only public check; it can only confirm what was already released"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Assay OS — what it computes to")
        .line("Throughput at the same bench", "revenue",
              "samples/mo × turnaround improvement × price",
              ["samples_month", "turnaround_gain", "price_per_sample"],
              lambda g: float(g["samples_month"]) * float(g["turnaround_gain"]) * float(g["price_per_sample"]),
              note="turnaround gain is yours to set — we count the current median, not the future one")
        .line("Certificate production time", "time_saved", "hrs/wk × 52 × rate",
              ["coa_hours_wk", "staff_rate"],
              lambda g: float(g["coa_hours_wk"]) * 52 * float(g["staff_rate"]),
              note="reported separately; never summed into revenue")
        .line("Status-chasing time", "time_saved", "hrs/wk × 52 × rate",
              ["status_hours_wk", "staff_rate"],
              lambda g: float(g["status_hours_wk"]) * 52 * float(g["staff_rate"]))
        .line("Certificates verifiable by your customers", "scenario",
              "you decide what this is worth",
              ["verification_value"], lambda g: float(g["verification_value"]),
              assumption=("we will not price your brand protection for you — forged certificates "
                          "in this market are common, and what that costs you is your number, "
                          "not an industry benchmark we borrowed")))


def roi(given):
    rec = {}
    ta = turnaround()
    if "_missing" not in ta:
        rec["current_median_hours"] = ta["median_hours"]
    prices = [s.get("price") for s in store.load("samples") if s.get("price")]
    if len(prices) >= 30:
        rec["price_per_sample"] = round(median(prices), 2)
    recent = [s for s in store.load("samples")
              if (parse(s.get("received_at")) or now()) >= now() - timedelta(days=30)]
    if len(recent) >= 20:
        rec["samples_month"] = len(recent)
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("log_sample", "advance_custody", "grade_result", "draft_coa", "release_coa", "notify_client")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("public:", "client:"))
