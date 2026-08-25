#!/usr/bin/env python3
"""Case OS — domain core (plaintiff-side PI · family · small litigation).

Everything that is a *rule* lives here: the matter and stage model, intake
criteria evaluation, the conflict check, the per-provider records playbook and
its state machine, production-verification rules, chronology construction,
contact-cadence thresholds, the ROI model and the autonomy matrix.

The product thesis: a plaintiff's firm loses money in two places that have
nothing to do with lawyering — the first ten minutes (the lead is shopped) and
the records chase (a case cannot be valued until the records are in hand). The
third module is retention insurance: clients who don't know what's happening.

The UPL rule, from `offerings/conduit/SPEC.md`, applied here: no legal advice,
no case-value opinion, no liability assessment, no fee discussion beyond the
published agreement, no guarantees. "Do I have a case?" is routed to a licensed
attorney UNANSWERED. Every AI output touching legal substance is labelled for
attorney review.

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

TABLES = ("config", "matters", "clients", "leads", "providers", "records",
          "productions", "contacts", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="CASEOS_DATA_ROOT")


# ---------------------------------------------------------------- matters

CASE_TYPES = {
    "auto":     dict(label="Motor vehicle", sol_years=3, avg_treatment_months=6),
    "premises": dict(label="Premises liability", sol_years=3, avg_treatment_months=5),
    "dog_bite": dict(label="Dog bite", sol_years=3, avg_treatment_months=3),
    "trucking": dict(label="Commercial trucking", sol_years=3, avg_treatment_months=9),
    "family":   dict(label="Family law", sol_years=None, avg_treatment_months=None),
}

STAGES = ("intake", "signed", "treating", "records", "demand", "negotiation",
          "litigation", "resolved")
CONTACT_THRESHOLD_DAYS = 30     # the #1 source of bar complaints is silence


# ---------------------------------------------------------------- intake
#
# Criteria are the FIRM'S, written down, and the screener reads only these.
# A decline is recorded with its reason so the firm can audit its own screening
# later — the cases you turned away are the half nobody measures.

def conflict_check(name, opposing, matters, clients):
    """Runs BEFORE any substantive conversation. A hit is a hard stop."""
    n = (name or "").strip().lower()
    o = (opposing or "").strip().lower()
    hits = []
    for c in clients:
        if c.get("name", "").lower() == o and o:
            hits.append({"kind": "adverse_to_current_client", "who": c["name"]})
    for m in matters:
        if (m.get("opposing") or "").lower() == n and n:
            hits.append({"kind": "we_are_adverse_to_this_person", "matter": m["id"]})
        if (m.get("client_name") or "").lower() == o and o:
            hits.append({"kind": "opposing_party_is_our_client", "matter": m["id"]})
    return {"clear": not hits, "hits": hits,
            "why": "no conflict found in current clients or open matters" if not hits
                   else "conflict — a lawyer clears this before anyone says another word"}


CRITERIA = {
    "case_type_accepted": lambda f, c: (f.get("case_type") in c["accepted_types"],
                                        f"we take {', '.join(c['accepted_types'])}"),
    "jurisdiction": lambda f, c: (f.get("state") in c["states"],
                                  f"we are licensed in {', '.join(c['states'])}"),
    "statute_not_expired": lambda f, c: _sol_ok(f),
    "liability_stated": lambda f, c: (bool(f.get("liability_facts")),
                                      "the caller described how it happened"),
    "treatment_started": lambda f, c: (bool(f.get("treated")),
                                       "the client has seen a provider"),
    "coverage_present": lambda f, c: (f.get("coverage") not in (None, "none"),
                                      "there is a policy to recover against"),
}


def _sol_ok(f):
    spec = CASE_TYPES.get(f.get("case_type"), {})
    yrs = spec.get("sol_years")
    if not yrs:
        return True, "no statute clock modelled for this case type"
    if not f.get("incident_date"):
        return None, "no incident date given — this cannot be evaluated, so a human does it"
    days = -(days_until(f["incident_date"]) or 0)
    left = yrs * 365 - days
    return (left > 0, f"{left} days left on a {yrs}-year clock (a DATE ALERT, not legal advice)")


def screen(facts, criteria_config):
    """Against the firm's written criteria. Anything unevaluable → a human."""
    results, unknown = [], []
    for key, fn in CRITERIA.items():
        ok, why = fn(facts, criteria_config)
        if ok is None:
            unknown.append({"criterion": key, "why": why})
        results.append({"criterion": key, "pass": ok, "why": why})
    failed = [r for r in results if r["pass"] is False]
    if unknown:
        return {"verdict": "human_review", "results": results, "unknown": unknown,
                "why": "a criterion could not be evaluated — the firm decides, not the software"}
    return {"verdict": "qualified" if not failed else "declined",
            "results": results, "failed": failed, "unknown": [],
            "why": "meets every written criterion" if not failed
                   else "; ".join(f"{r['criterion']}: {r['why']}" for r in failed)}


# ---------------------------------------------------------------- the UPL stop

LEGAL_QUESTION = [
    r"do i have a case", r"what('s| is) (my|the) case worth", r"how much (will|can) i get",
    r"should i (sue|settle|accept|sign)", r"am i (going to|gonna) win", r"whose fault",
    r"is (he|she|they|the driver|the store) liable", r"can i sue", r"will (i|we) win",
    r"how long (do i have|until).*(sue|file)", r"what are my (rights|options|chances)",
    r"is this (worth|enough)", r"should i talk to (the )?(insurance|adjuster)",
]
_LQ = [re.compile(p, re.I) for p in LEGAL_QUESTION]


def legal_question(text):
    for rx in _LQ:
        m = rx.search(text or "")
        if m:
            return {"is_legal": True, "matched": m.group(0).strip()}
    return {"is_legal": False, "matched": None}


# ---------------------------------------------------------------- records
#
# The per-provider playbook. This is where a PI case actually loses its months.

RECORD_STATES = ("drafted", "sent", "acknowledged", "prepaid", "produced", "verified", "complete")

PROVIDER_DEFAULTS = dict(format="ror_form", needs_prepay=False, auth_form="hipaa_auth",
                         turnaround_days=21, portal=None)


def request_packet(provider, matter):
    """What this specific provider needs, in the form they need it."""
    p = {**PROVIDER_DEFAULTS, **(provider or {})}
    packet = {"provider": p.get("name"), "format": p["format"], "auth": p["auth_form"],
              "prepay": p["needs_prepay"], "expected_days": p["turnaround_days"],
              "date_range": {"from": matter.get("incident_date"),
                             "to": matter.get("treatment_end") or iso()},
              "requested": ["records", "billing"]}
    if p.get("portal"):
        packet["channel"] = f"portal: {p['portal']}"
    return packet


def verify_production(request, production):
    """The valuable half. Compare what ARRIVED against what was ASKED FOR.

    A production is not complete because a PDF showed up. Missing date ranges,
    missing billing and illegible pages are how a demand gets built on an
    incomplete file, which is the expensive error this module exists to prevent.
    """
    gaps = []
    want_from, want_to = request.get("date_from"), request.get("date_to")
    got_from, got_to = production.get("date_from"), production.get("date_to")
    if not got_from or not got_to:
        gaps.append({"gap": "no date range stated in the production", "severity": "high"})
    else:
        if want_from and parse(got_from) and parse(want_from) and parse(got_from) > parse(want_from):
            gaps.append({"gap": f"records start {got_from[:10]}, we asked from {want_from[:10]}",
                         "severity": "high"})
        if want_to and parse(got_to) and parse(want_to) and parse(got_to) < parse(want_to):
            gaps.append({"gap": f"records end {got_to[:10]}, we asked to {want_to[:10]}",
                         "severity": "high"})
    if "billing" in request.get("requested", []) and not production.get("has_billing"):
        gaps.append({"gap": "billing not included — a demand without bills is not a demand",
                     "severity": "high"})
    if production.get("illegible_pages"):
        gaps.append({"gap": f"{production['illegible_pages']} illegible page(s)", "severity": "medium"})
    if production.get("patient_name") and request.get("patient_name") and \
            production["patient_name"].lower() != request["patient_name"].lower():
        gaps.append({"gap": f"wrong patient: '{production['patient_name']}'", "severity": "critical"})
    return {"complete": not gaps, "gaps": gaps,
            "verdict": "verified" if not gaps else "incomplete",
            "why": "matches what was requested" if not gaps
                   else f"{len(gaps)} gap(s) — this is NOT a complete production"}


def completeness(matter_id, ref=None):
    """% of the file that is verified-complete — or a refusal to say."""
    reqs = [r for r in store.load("records") if r["matter_id"] == matter_id]
    if not reqs:
        return unmeasured("no records requests on file for this matter — completeness is unknown, "
                          "not zero", field="pct", n=0)
    done = [r for r in reqs if r.get("state") == "complete"]
    return {"pct": round(len(done) / len(reqs), 3), "complete": len(done), "of": len(reqs)}


# ---------------------------------------------------------------- chronology + demand
#
# A fact without an exhibit citation is OMITTED and listed as unsupported.
# Never written anyway.

def build_chronology(matter_id):
    prods = [p for p in store.load("productions") if p.get("matter_id") == matter_id
             and p.get("verified")]
    entries, unsupported = [], []
    for p in prods:
        for e in p.get("entries", []):
            if e.get("exhibit") and e.get("page"):
                entries.append({**e, "citation": f"Ex. {e['exhibit']} p.{e['page']}"})
            else:
                unsupported.append({**e, "why": "no exhibit and page — omitted from the draft"})
    entries.sort(key=lambda e: e.get("date") or "")
    bills = sum(e.get("charge", 0) for e in entries)
    return {"entries": entries, "unsupported": unsupported,
            "billed_total": round(bills, 2) if entries else None,
            "note": "every line carries an exhibit citation. A fact we cannot cite is listed as "
                    "unsupported rather than written into the demand — this draft is FOR ATTORNEY "
                    "REVIEW and states no case value"}


# ---------------------------------------------------------------- autonomy

MATRIX = Matrix({
    "conflict_check":     dict(rung="R3", reason="running names against our own client and matter list before anyone speaks is pure safety"),
    "screen_intake":      dict(rung="R2", reason="evaluating a caller against the firm's OWN written criteria; anything unevaluable goes to a human"),
    "legal_advice":       dict(rung="R0", reason="THE SYSTEM NEVER DOES THIS. No case value, no liability opinion, no 'do I have a case', no chances, no advice on whether to sign or settle — routed to a licensed attorney unanswered", never_promote=True),
    "send_retainer":      dict(rung="R1", reason="putting a fee agreement in front of a person is the firm entering a relationship", never_promote=True),
    "send_records_request": dict(rung="R2", reason="a standard authorization-backed request in the provider's own format"),
    "records_prepay":     dict(rung="R1", reason="money leaves the firm — a human approves every one"),
    "records_followup":   dict(rung="R2", reason="following our own schedule on a request we already sent"),
    "mark_production_complete": dict(rung="R2", reason="only when verification found zero gaps; a gap keeps it open and that is not overridable by an agent"),
    "draft_demand_facts": dict(rung="R1", reason="a demand is an attorney's document — drafted with citations, never sent", never_promote=True),
    "client_status_update": dict(rung="R2", reason="a factual status drawn from case events on a guaranteed cadence"),
    "message_custom":     dict(rung="R1", reason="free text to a client can become advice"),
})
gate = Gate(store, MATRIX)

MOVING_KINDS = {"conflict_check", "screen_intake", "send_retainer", "retainer_signed",
                "send_records_request", "records_prepay", "records_followup",
                "mark_production_complete", "draft_demand_facts", "demand_sent",
                "client_status_update", "message_custom"}


def automation(days=90):
    return automation_rate(store.load("events"), MOVING_KINDS, days, exclude_actors=("client:",))


# ---------------------------------------------------------------- evals

UPL_EVAL = Eval(
    "legal-question routing", "legal",
    "a legal question answered by software is unauthorized practice — recall is reported alone, and "
    "a false alarm merely means an attorney reads one extra message")


def eval_upl():
    cases = [("do I have a case?", "legal"), ("what's my case worth", "legal"),
             ("how much will I get", "legal"), ("should I sign what the adjuster sent", "legal"),
             ("whose fault is it", "legal"), ("can I sue the store", "legal"),
             ("what are my chances", "legal"), ("should I settle", "legal"),
             ("am I going to win", "legal"),
             ("what time is my appointment", "routine"), ("can you send me a W-9", "routine"),
             ("I moved, here's my new address", "routine"),
             ("who is my paralegal", "routine"), ("did you get my records", "routine"),
             ("I finished physical therapy last week", "routine")]
    return UPL_EVAL.run([{"input": t, "label": l} for t, l in cases],
                        lambda t: "legal" if legal_question(t)["is_legal"] else "routine")


PROD_EVAL = Eval(
    "production verification", "incomplete",
    "a production wrongly marked complete produces a demand built on a partial file — the "
    "false-'complete' rate is what this measures and it must be zero")


def eval_productions():
    req = {"date_from": "2026-01-01T00:00:00+00:00", "date_to": "2026-06-01T00:00:00+00:00",
           "requested": ["records", "billing"], "patient_name": "Dana Reyes"}
    cases = [
        (dict(date_from="2026-01-01T00:00:00+00:00", date_to="2026-06-01T00:00:00+00:00",
              has_billing=True, patient_name="Dana Reyes"), "verified"),
        (dict(date_from="2026-03-01T00:00:00+00:00", date_to="2026-06-01T00:00:00+00:00",
              has_billing=True, patient_name="Dana Reyes"), "incomplete"),
        (dict(date_from="2026-01-01T00:00:00+00:00", date_to="2026-04-01T00:00:00+00:00",
              has_billing=True, patient_name="Dana Reyes"), "incomplete"),
        (dict(date_from="2026-01-01T00:00:00+00:00", date_to="2026-06-01T00:00:00+00:00",
              has_billing=False, patient_name="Dana Reyes"), "incomplete"),
        (dict(has_billing=True, patient_name="Dana Reyes"), "incomplete"),
        (dict(date_from="2026-01-01T00:00:00+00:00", date_to="2026-06-01T00:00:00+00:00",
              has_billing=True, patient_name="D. Ramirez"), "incomplete"),
        (dict(date_from="2026-01-01T00:00:00+00:00", date_to="2026-06-01T00:00:00+00:00",
              has_billing=True, illegible_pages=4, patient_name="Dana Reyes"), "incomplete"),
    ]
    keyed = {f"case_{i}": c for i, (c, _) in enumerate(cases)}
    return PROD_EVAL.run([{"input": f"case_{i}", "label": l} for i, (_, l) in enumerate(cases)],
                         lambda k: verify_production(req, keyed[k])["verdict"])


# ---------------------------------------------------------------- the case board

def case_board(ref=None):
    ref = ref or now()
    matters = [m for m in store.load("matters") if m.get("stage") != "resolved"]
    contacts = {}
    for c in store.load("contacts"):
        prev = contacts.get(c["matter_id"])
        if not prev or c["at"] > prev:
            contacts[c["matter_id"]] = c["at"]
    rows = []
    for m in matters:
        last = contacts.get(m["id"])
        since = -(days_until(last, ref) or 0) if last else None
        spec = CASE_TYPES.get(m["case_type"], {})
        sol_left = None
        if spec.get("sol_years") and m.get("incident_date"):
            sol_left = spec["sol_years"] * 365 + (days_until(m["incident_date"], ref) or 0)
        rows.append({
            "matter": m["id"], "client": m.get("client_name"), "type": m["case_type"],
            "stage": m.get("stage"), "attorney": m.get("attorney"),
            "days_since_contact": since,
            "contact_overdue": (since is not None and since > CONTACT_THRESHOLD_DAYS),
            "no_contact_recorded": last is None,
            "completeness": completeness(m["id"], ref),
            "sol_days_left": sol_left,
        })
    rows.sort(key=lambda r: (r["sol_days_left"] if r["sol_days_left"] is not None else 99999))
    return {"generated": iso(ref), "rows": rows,
            "contact_overdue": sum(1 for r in rows if r["contact_overdue"]),
            "no_contact_recorded": sum(1 for r in rows if r["no_contact_recorded"]),
            "sol_under_90": sum(1 for r in rows if r["sol_days_left"] is not None
                                and r["sol_days_left"] < 90),
            "automation": automation(),
            "note": "statute proximity is a DATE ALERT computed from the incident date on file. "
                    "It is not legal advice and it is not a tolling analysis"}


def records_board():
    reqs = store.load("records")
    open_reqs = [r for r in reqs if r.get("state") not in ("complete",)]
    incomplete = [r for r in reqs if r.get("verification")
                  and not r["verification"].get("complete")]
    providers = store.index("providers", "id")
    return {"open": len(open_reqs), "total": len(reqs),
            "incomplete_productions": [
                {"request": r["id"], "provider": providers.get(r.get("provider_id"), {}).get("name"),
                 "matter": r["matter_id"], "gaps": r["verification"]["gaps"]}
                for r in incomplete][:30],
            "by_state": {s: sum(1 for r in reqs if r.get("state") == s) for s in RECORD_STATES},
            "aging": _aging(open_reqs)}


def _aging(reqs, floor=8):
    ages = [a for a in (-(days_until(r.get("sent_at")) or 0) for r in reqs if r.get("sent_at")) if a]
    if len(ages) < floor:
        return unmeasured(f"only {len(ages)} sent requests; need {floor} for a median",
                          field="median_days", n=len(ages))
    return {"median_days": round(median(ages), 1), "max_days": max(ages), "n": len(ages)}


# ---------------------------------------------------------------- ROI

ROI = (Roi("What the two bottlenecks are worth here")
       .line("Speed to signed retainer", "revenue",
             "after-hours leads/yr × incremental sign% × YOUR average case fee",
             ["after_hours_leads_yr", "incremental_sign_rate", "avg_case_fee"],
             lambda g: g["after_hours_leads_yr"] * g["incremental_sign_rate"] * g["avg_case_fee"],
             note="after-hours leads are counted from your own intake log",
             assumption="AVERAGE CASE FEE IS YOURS. We will not use a published settlement "
                        "statistic — contingency outcomes are wide and lumpy and a borrowed "
                        "average would make this line fiction")
       .line("Records cycle time", "cash_timing",
             "matters × days removed from the file × daily carry",
             ["open_matters", "days_removed", "daily_carry"],
             lambda g: g["open_matters"] * g["days_removed"] * g["daily_carry"],
             note="THIS CHANGES WHEN FEES ARRIVE more than whether they do. A faster file resolves "
                  "sooner; it does not by itself make the case worth more")
       .line("Paralegal time", "time_saved",
             "requests + follow-ups + chronology hours/wk × 48 × loaded rate",
             ["paralegal_hours_wk", "loaded_rate"],
             lambda g: g["paralegal_hours_wk"] * 48 * g["loaded_rate"])
       .line("Screening quality", "scenario",
             "declined-but-qualified rescued × avg case fee",
             ["rescued_per_year", "avg_case_fee"],
             lambda g: g["rescued_per_year"] * g["avg_case_fee"],
             note="A SCENARIO, not a saving. You cannot count cases you did not take. This line "
                  "exists so the firm can audit its own screening — the recorded decline reasons "
                  "are the evidence, not this number"))


def roi(given=None):
    cfg = store.load("config")
    recorded = {}
    leads = store.load("leads")
    ah = [l for l in leads if l.get("after_hours")]
    if leads:
        recorded["after_hours_leads_yr"] = len(ah)
    open_m = [m for m in store.load("matters") if m.get("stage") != "resolved"]
    if open_m:
        recorded["open_matters"] = len(open_m)
    merged = dict(recorded)
    merged.update({k: v for k, v in (cfg.get("roi_inputs") or {}).items() if v not in (None, "")})
    merged.update({k: v for k, v in (given or {}).items() if v not in (None, "")})
    out = ROI.render(merged)
    out["recorded"] = recorded
    out["operator_supplied"] = {k: v for k, v in merged.items() if k not in recorded}
    return out
