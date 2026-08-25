#!/usr/bin/env python3
"""Renewal OS — domain core (independent P&C agencies).

Everything that is a *rule* lives here: the policy and coverage model, the
renewal diff and its cause classification, materiality thresholds, the
comparison-sheet rule, certificate standard-vs-non-standard classification, the
cross-sell score and its permitted-factor list, the ROI model and the autonomy
matrix.

The product thesis: an agency's economics are retention economics. A policy lost
at renewal takes its commission every year forever, and the renewal usually
arrives untouched.

Three prohibitions are rules here, not prompt text:
  1. No coverage advice, no quoting, no binding, no coverage opinions. Material
     client communication is drafted for a LICENSED PRODUCER.
  2. A price comparison cannot render without its coverage diff attached.
  3. A non-standard certificate is never auto-issued.

Stdlib only.
"""
import re, sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, days_until, iso,    # noqa: E402
                        median, now, parse, unmeasured)

TABLES = ("config", "households", "policies", "renewals", "certificates", "claims",
          "producers", "carriers", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="RENEWALOS_DATA_ROOT")


# ---------------------------------------------------------------- the book

LINES = {
    "auto":         dict(label="Personal auto", personal=True, premium=(900, 2900), commission=0.12),
    "home":         dict(label="Homeowners", personal=True, premium=(1100, 4200), commission=0.14),
    "umbrella":     dict(label="Personal umbrella", personal=True, premium=(240, 780), commission=0.14),
    "bop":          dict(label="Business owners policy", personal=False, premium=(1400, 8500), commission=0.13),
    "gl":           dict(label="General liability", personal=False, premium=(1800, 12000), commission=0.13),
    "wc":           dict(label="Workers compensation", personal=False, premium=(3200, 48000), commission=0.09),
    "comm_auto":    dict(label="Commercial auto", personal=False, premium=(2400, 22000), commission=0.11),
    "cyber":        dict(label="Cyber", personal=False, premium=(900, 6500), commission=0.15),
}

# Bundle logic — which lines belong together. This is the only thing the
# cross-sell finder is allowed to reason about, plus the permitted factors below.
BUNDLES = {"auto": ["home", "umbrella"], "home": ["auto", "umbrella"],
           "bop": ["comm_auto", "cyber", "wc"], "gl": ["comm_auto", "cyber", "wc"]}


# ---------------------------------------------------------------- the renewal diff
#
# The classification exists so a producer opens the right conversation. A 22%
# increase caused by a carrier-wide filing is a different call from one caused by
# a claim, and both are different from one caused by a lost discount.

CAUSES = {
    "rate_action":    "carrier rate filing — nothing the client did",
    "exposure":       "the exposure changed (vehicle, driver, payroll, revenue, property value)",
    "credit_loss":    "a discount or credit fell off",
    "claim_driven":   "a claim in the experience period",
    "coverage_change": "the coverage itself changed at renewal",
    "unknown":        "the carrier did not state a reason — the producer has to ask",
}
MATERIAL_PCT = 0.10          # the point at which a human must own the conversation
LARGE_PCT = 0.20


def renewal_diff(expiring, renewal):
    """Premium and coverage, diffed. A coverage change is reported even when the
    premium is flat, because that is the one clients discover at claim time."""
    dp = None
    if expiring.get("premium"):
        dp = round((renewal["premium"] - expiring["premium"]) / expiring["premium"], 4)
    cov = []
    for k in set(list(expiring.get("coverage", {})) + list(renewal.get("coverage", {}))):
        a, b = expiring.get("coverage", {}).get(k), renewal.get("coverage", {}).get(k)
        if a != b:
            cov.append({"field": k, "was": a, "now": b})
    return {"premium_delta_pct": dp,
            "premium_delta": round(renewal["premium"] - expiring.get("premium", 0), 2)
            if expiring.get("premium") else None,
            "coverage_changes": cov,
            "_missing": None if expiring.get("premium") else
            "no expiring premium on file — the change cannot be computed, only the new number shown"}


def classify_renewal(expiring, renewal):
    d = renewal_diff(expiring, renewal)
    dp = d["premium_delta_pct"]
    cause = renewal.get("carrier_reason") or ("coverage_change" if d["coverage_changes"] else "unknown")
    if cause not in CAUSES:
        cause = "unknown"
    if dp is None:
        material = True          # unknowable change is material by default
        why = "the change could not be computed, so it goes to a producer"
    else:
        material = abs(dp) >= MATERIAL_PCT or bool(d["coverage_changes"])
        why = (f"{dp:+.1%} premium change" if abs(dp) >= MATERIAL_PCT else
               "coverage changed at renewal" if d["coverage_changes"] else
               f"{dp:+.1%} — quiet renewal")
    return {**d, "cause": cause, "cause_note": CAUSES[cause], "material": material,
            "large": bool(dp is not None and abs(dp) >= LARGE_PCT), "why": why}


# ---------------------------------------------------------------- the comparison rule
#
# The rule that keeps the agency out of an E&O claim: you may not put a cheaper
# number in front of a client without the coverage differences beside it.

def comparison_sheet(current, quote):
    diffs = []
    for k in set(list(current.get("coverage", {})) + list(quote.get("coverage", {}))):
        a, b = current.get("coverage", {}).get(k), quote.get("coverage", {}).get(k)
        if a != b:
            diffs.append({"field": k, "current": a, "quoted": b})
    if not quote.get("coverage"):
        return {"renderable": False,
                "_missing": "the quote came back without a coverage schedule — a price comparison "
                            "cannot be shown without one, and this is a rule rather than a setting"}
    return {"renderable": True, "current_premium": current.get("premium"),
            "quoted_premium": quote.get("premium"),
            "savings": (round(current["premium"] - quote["premium"], 2)
                        if current.get("premium") else None),
            "coverage_differences": diffs,
            "note": ("apples-to-apples: no coverage differences found" if not diffs else
                     f"{len(diffs)} coverage difference(s) — read these before the price")}


# ---------------------------------------------------------------- certificates
#
# Routine certificates are the CSR's day. Non-standard language is an E&O event
# waiting to happen, and it is a hard stop rather than a lower confidence score.

NON_STANDARD = [
    (r"additional insured|\bAI\b endors", "additional insured"),
    (r"waiver of subrogation|waives? subrogation", "waiver of subrogation"),
    (r"primary (and|&) non[- ]?contributory|primary/non", "primary and non-contributory"),
    (r"30 ?days? (written )?notice|notice of cancell", "notice of cancellation endorsement"),
    (r"per project aggregate|per[- ]project", "per-project aggregate"),
    (r"completed operations", "completed operations"),
    (r"blanket", "blanket endorsement"),
]
_NS = [(re.compile(p, re.I), lbl) for p, lbl in NON_STANDARD]


def classify_certificate(request):
    """standard | non_standard. Anything it cannot read is non_standard —
    unreadable is not the same as routine."""
    text = (request.get("requested_language") or "").strip()
    hits = [lbl for rx, lbl in _NS if rx.search(text)]
    if hits:
        return {"kind": "non_standard", "reasons": hits,
                "why": f"requested language includes {', '.join(hits)} — a human reads the "
                       f"underlying policy before this issues"}
    if request.get("holder_language_attached") and not text:
        return {"kind": "non_standard", "reasons": ["unreadable attachment"],
                "why": "the holder attached language we could not read — unreadable is not routine"}
    prior = request.get("prior_certificate")
    if not prior:
        return {"kind": "non_standard", "reasons": ["no prior certificate"],
                "why": "no prior certificate to match against — the first one for a holder is a human's"}
    return {"kind": "standard", "reasons": [],
            "why": f"matches the prior certificate for this holder ({prior})"}


# ---------------------------------------------------------------- cross-sell
#
# PERMITTED FACTORS ONLY. The scorer physically reads nothing else — no purchased
# data, no inference about protected characteristics, and no proxies for them.
# The test suite proves it by mutating everything else and asserting the score
# does not move.

PERMITTED_FACTORS = ("lines_held", "policy_age_days", "prior_quote_declined",
                     "life_event_recorded", "claim_free_years", "premium_total")


def cross_sell_score(household, policies):
    mine = [p for p in policies if p["household_id"] == household["id"] and p.get("active")]
    lines = {p["line"] for p in mine}
    if len(lines) >= 2:
        return {"score": 0.0, "gap": None, "why": ["already multi-line"]}
    if not mine:
        return {"score": 0.0, "gap": None, "why": ["no active policy"]}
    held = list(lines)[0]
    gaps = [g for g in BUNDLES.get(held, []) if g not in lines]
    if not gaps:
        return {"score": 0.0, "gap": None, "why": [f"no natural companion line to {held}"]}

    why, score = [], 1.0
    why.append(f"holds {held} only; natural companion is {gaps[0]}")
    age = household.get("policy_age_days")
    if age is None:
        why.append("policy age not recorded")
    else:
        score *= 1.2 if age > 365 else 0.9
        why.append(f"{age // 30} months on the books")
    if household.get("prior_quote_declined"):
        score *= 0.6
        why.append("declined a quote on this line before")
    if household.get("life_event_recorded"):
        score *= 1.4
        why.append(f"recorded life event: {household['life_event_recorded']}")
    cf = household.get("claim_free_years")
    if cf is None:
        why.append("claim history not recorded")
    else:
        score *= 1.0 + min(cf, 5) * 0.04
        why.append(f"{cf} claim-free years")
    prem = sum(p["premium"] for p in mine)
    return {"score": round(score * (1 + prem / 10000), 3), "gap": gaps[0], "why": why,
            "premium_total": round(prem, 2)}


# ---------------------------------------------------------------- book reads

def retention(days=365, floor=30):
    """Counted from renewals that reached a terminal state."""
    rows = [r for r in store.load("renewals") if r.get("outcome") in ("retained", "lost")
            and (parse(r.get("effective")) or now()) >= now() - timedelta(days=days)]
    if len(rows) < floor:
        return unmeasured(f"only {len(rows)} completed renewals in {days} days; need {floor}",
                          field="rate", n=len(rows))
    kept = sum(1 for r in rows if r["outcome"] == "retained")
    by_producer, by_carrier = {}, {}
    for r in rows:
        for bucket, key in ((by_producer, r.get("producer")), (by_carrier, r.get("carrier"))):
            b = bucket.setdefault(key or "unassigned", {"kept": 0, "n": 0})
            b["n"] += 1
            b["kept"] += (r["outcome"] == "retained")
    fmt = lambda b: {k: {**v, "rate": round(v["kept"] / v["n"], 3) if v["n"] >= 10 else None,
                         "_missing": None if v["n"] >= 10 else f"only {v['n']} renewals — too few to rate"}
                     for k, v in b.items()}
    return {"rate": round(kept / len(rows), 3), "n": len(rows), "window_days": days,
            "by_producer": fmt(by_producer), "by_carrier": fmt(by_carrier)}


def premium_at_risk(days=90, ref=None):
    ref = ref or now()
    live = [p for p in store.load("policies") if p.get("active")]
    soon = [p for p in live if (days_until(p["expires"], ref) or 999) <= days]
    return {"policies": len(soon), "premium": round(sum(p["premium"] for p in soon), 2),
            "commission": round(sum(p["premium"] * LINES[p["line"]]["commission"] for p in soon), 2),
            "window_days": days}


def mono_line_share():
    hh, pol = store.load("households"), store.load("policies")
    if not hh:
        return unmeasured("no households on file", field="share")
    counts = {}
    for p in pol:
        if p.get("active"):
            counts.setdefault(p["household_id"], set()).add(p["line"])
    mono = sum(1 for h in hh if len(counts.get(h["id"], set())) == 1)
    with_any = sum(1 for h in hh if counts.get(h["id"]))
    return {"share": round(mono / with_any, 3) if with_any else None, "mono": mono,
            "households_with_a_policy": with_any}


def coi_turnaround(days=90, floor=10):
    rows = [c for c in store.load("certificates") if c.get("issued_at")
            and (parse(c["requested_at"]) or now()) >= now() - timedelta(days=days)]
    vals = []
    for c in rows:
        a, b = parse(c["requested_at"]), parse(c["issued_at"])
        if a and b:
            vals.append(round((b - a).total_seconds() / 3600, 2))
    if len(vals) < floor:
        return unmeasured(f"only {len(vals)} issued certificates in {days} days; need {floor}",
                          field="median_hours", n=len(vals))
    return {"median_hours": round(median(vals), 2), "n": len(vals)}


# ---------------------------------------------------------------- autonomy

MATRIX = Matrix({
    "classify_renewal":   dict(rung="R3", reason="diffing two documents and naming the cause is arithmetic; the producer corrects it in one click"),
    "quiet_renewal_touch": dict(rung="R2", reason="a templated 'your renewal is on the way, nothing changed' against a computed sub-threshold delta"),
    "draft_renewal_call": dict(rung="R1", reason="a material increase is a conversation a licensed producer owns — the draft waits for them"),
    "coverage_advice":    dict(rung="R0", reason="THE SYSTEM NEVER DOES THIS. No coverage opinion, no 'are you covered for', no recommendation to change limits — routed to a licensed producer", never_promote=True),
    "quote_or_bind":      dict(rung="R0", reason="THE SYSTEM NEVER DOES THIS. Quoting and binding are licensed acts", never_promote=True),
    "assemble_remarket":  dict(rung="R2", reason="pulling our own data into a submission commits nobody"),
    "present_comparison": dict(rung="R1", reason="a comparison in front of a client is a producer's document — and it is blocked outright without its coverage diff", never_promote=True),
    "issue_standard_coi": dict(rung="R2", reason="matches a prior certificate for the same holder against the same policy; the CSR is notified on every one"),
    "issue_nonstandard_coi": dict(rung="R0", reason="THE SYSTEM NEVER DOES THIS. Additional insured, waiver of subrogation, primary/non-contributory, notice endorsements — a human reads the policy", never_promote=True),
    "cross_sell_list":    dict(rung="R2", reason="a ranked internal list for a producer, not an outbound message"),
    "claims_touch":       dict(rung="R1", reason="the highest-emotion moment in the relationship — a human sends it"),
    "state_notice":       dict(rung="R0", reason="cancellation and non-renewal notices are statutory. An agent drafts nothing and sends nothing", never_promote=True),
})
gate = Gate(store, MATRIX)

MOVING_KINDS = {"classify_renewal", "quiet_renewal_touch", "draft_renewal_call",
                "renewal_call_sent", "assemble_remarket", "present_comparison",
                "issue_standard_coi", "cross_sell_list", "claims_touch"}


def automation(days=90):
    return automation_rate(store.load("events"), MOVING_KINDS, days, exclude_actors=("client:",))


# ---------------------------------------------------------------- eval

COI_EVAL = Eval(
    "certificate classification", "non_standard",
    "a non-standard certificate auto-issued as routine is an E&O event — recall on non_standard is "
    "reported alone, and a false alarm merely costs a CSR two minutes")


def eval_coi():
    cases = [
        ({"requested_language": "Additional insured per written contract", "prior_certificate": "c1"}, "non_standard"),
        ({"requested_language": "waiver of subrogation in favor of the owner", "prior_certificate": "c1"}, "non_standard"),
        ({"requested_language": "primary and non-contributory", "prior_certificate": "c1"}, "non_standard"),
        ({"requested_language": "30 days written notice of cancellation", "prior_certificate": "c1"}, "non_standard"),
        ({"requested_language": "per project aggregate required", "prior_certificate": "c1"}, "non_standard"),
        ({"requested_language": "including completed operations", "prior_certificate": "c1"}, "non_standard"),
        ({"requested_language": "", "holder_language_attached": True, "prior_certificate": "c1"}, "non_standard"),
        ({"requested_language": "", "prior_certificate": None}, "non_standard"),
        ({"requested_language": "", "prior_certificate": "c1"}, "standard"),
        ({"requested_language": "evidence of coverage for the landlord", "prior_certificate": "c2"}, "standard"),
        ({"requested_language": "copy of current GL cert please", "prior_certificate": "c3"}, "standard"),
        ({"requested_language": "same as last year", "prior_certificate": "c4"}, "standard"),
    ]
    return COI_EVAL.run([{"input": i, "label": l} for i, l in cases],
                        lambda i: classify_certificate(i)["kind"])


# ---------------------------------------------------------------- the board

def book_board(ref=None):
    return {
        "generated": iso(ref or now()),
        "retention": retention(),
        "at_risk_90": premium_at_risk(90, ref),
        "mono_line": mono_line_share(),
        "coi_turnaround": coi_turnaround(),
        "automation": automation(),
    }


# ---------------------------------------------------------------- ROI

ROI = (Roi("What retention is worth here")
       .line("Retention lift", "revenue",
             "policies at renewal × points gained × avg commission × persistency years",
             ["renewals_per_year", "retention_points_gained", "avg_commission", "persistency_years"],
             lambda g: g["renewals_per_year"] * g["retention_points_gained"] * g["avg_commission"]
             * g["persistency_years"],
             note="renewals and average commission are counted from your own book",
             assumption="PERSISTENCY YEARS COMPOUNDS. A policy saved this year earns again every "
                        "year it stays. This is the number that makes this line large and it is "
                        "the easiest place to lie — set it to 1 if you want the one-year answer")
       .line("Remarket saves", "revenue",
             "flagged increases × save% × avg commission",
             ["flagged_increases_per_year", "save_rate", "avg_commission"],
             lambda g: g["flagged_increases_per_year"] * g["save_rate"] * g["avg_commission"],
             note="flagged increases are counted from your own renewal classifications")
       .line("Cross-sell", "revenue",
             "mono-line households × contact% × bind% × added commission",
             ["mono_line_households", "contact_rate", "bind_rate", "added_commission"],
             lambda g: g["mono_line_households"] * g["contact_rate"] * g["bind_rate"]
             * g["added_commission"],
             note="mono-line count is counted from your own book")
       .line("Certificate time", "time_saved",
             "certs/wk × minutes each × 48 × loaded rate",
             ["certs_wk", "minutes_each", "loaded_rate"],
             lambda g: g["certs_wk"] * (g["minutes_each"] / 60) * 48 * g["loaded_rate"],
             note="CSR time, reported apart from commission and never added into it"))


def roi(given=None):
    cfg = store.load("config")
    recorded = {}
    pol = [p for p in store.load("policies") if p.get("active")]
    if pol:
        recorded["renewals_per_year"] = len(pol)
        recorded["avg_commission"] = round(
            sum(p["premium"] * LINES[p["line"]]["commission"] for p in pol) / len(pol), 2)
    ml = mono_line_share()
    if not ml.get("_missing"):
        recorded["mono_line_households"] = ml["mono"]
    flagged = [r for r in store.load("renewals") if r.get("material")]
    if flagged:
        recorded["flagged_increases_per_year"] = len(flagged)
    merged = dict(recorded)
    merged.update({k: v for k, v in (cfg.get("roi_inputs") or {}).items() if v not in (None, "")})
    merged.update({k: v for k, v in (given or {}).items() if v not in (None, "")})
    out = ROI.render(merged)
    out["recorded"] = recorded
    out["operator_supplied"] = {k: v for k, v in merged.items() if k not in recorded}
    return out
