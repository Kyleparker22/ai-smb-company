#!/usr/bin/env python3
"""Rehearsal OS — domain core (independent P&C agencies: the claim rehearsal).

The product thesis: agencies sell renewals on price; nobody sells them by
rehearsing the claim. Before each renewal, Rehearsal OS simulates the client's
three most-probable claims against their ACTUAL recorded policy — limits,
deductibles, exclusions, each with its form citation — and shows the
out-of-pocket gap in dollars, at three severities. The fix sheet is the
cross-sell.

Four prohibitions are rules here, not prompt text:
  1. No coverage promises. A rehearsal is arithmetic on the recorded policy;
     only the carrier adjusts a real claim, and every sheet says so.
  2. No rehearsal on an unread policy. No recorded policy detail → UNREADABLE.
     We read policies before we rehearse them.
  3. No fear language in anything client-facing (structural tone check).
  4. No single-number severity. Loss is a recorded range — bands, not points.

Stdlib only. Honesty rules come from `_kit`.
"""
import re, sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, days_until, iso,    # noqa: E402
                        now, parse, unmeasured)

TABLES = ("config", "accounts", "rehearsals", "claims", "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="REHEARSALOS_DATA_ROOT")

REHEARSAL_LABEL = ("THIS IS A REHEARSAL — arithmetic on the recorded policy, nothing more. "
                   "It is not a coverage opinion and not a claim decision; only the carrier "
                   "adjusts a real claim.")
UNREADABLE_WHY = ("UNREADABLE — no recorded policy detail on this account. We read policies "
                  "before we rehearse them; a rehearsal on a guessed policy is a fabricated "
                  "claim. The fix is a policy review, and that is the whole recommendation.")


# ---------------------------------------------------------------- the scenario table
#
# Recorded in config at seed time so the demo runs on a RECORDED table; the
# default below is the fallback and names its own provenance.

DEFAULT_SCENARIOS = {
    "_source": ("DEFAULT scenario table, simplified from loss-frequency practice — replace "
                "with the table the agency actually adopts before go-live. Severity is a "
                "RANGE (low / typical / severe) by design; a point estimate is refused."),
    "homeowner": [
        {"key": "kitchen_fire", "label": "Kitchen fire",
         "components": [{"peril": "dwelling_fire", "share": 0.5},
                        {"peril": "contents", "share": 0.3},
                        {"peril": "loss_of_use", "share": 0.2}],
         "severity": {"low": 24000, "typical": 77000, "severe": 160000}},
        {"key": "water_backup", "label": "Sewer / sump water backup",
         "components": [{"peril": "water_backup", "share": 1.0}],
         "severity": {"low": 9000, "typical": 28000, "severe": 60000}},
        {"key": "liability_slip", "label": "Guest slip-and-fall liability",
         "components": [{"peril": "personal_liability", "share": 1.0}],
         "severity": {"low": 15000, "typical": 90000, "severe": 350000}},
    ],
    "contractor": [
        {"key": "jobsite_injury", "label": "Jobsite third-party injury",
         "components": [{"peril": "general_liability", "share": 1.0}],
         "severity": {"low": 20000, "typical": 110000, "severe": 500000}},
        {"key": "tool_theft", "label": "Tool & equipment theft",
         "components": [{"peril": "tools_equipment", "share": 1.0}],
         "severity": {"low": 6000, "typical": 18000, "severe": 45000}},
        {"key": "faulty_work_damage", "label": "Completed-work property damage",
         "components": [{"peril": "completed_operations", "share": 1.0}],
         "severity": {"low": 12000, "typical": 60000, "severe": 220000}},
    ],
    "restaurant": [
        {"key": "grease_fire", "label": "Kitchen grease fire + shutdown",
         "components": [{"peril": "property", "share": 0.6},
                        {"peril": "business_income", "share": 0.4}],
         "severity": {"low": 30000, "typical": 120000, "severe": 400000}},
        {"key": "patron_slip", "label": "Patron slip-and-fall",
         "components": [{"peril": "general_liability", "share": 1.0}],
         "severity": {"low": 10000, "typical": 70000, "severe": 280000}},
        {"key": "spoilage", "label": "Power loss spoilage",
         "components": [{"peril": "spoilage", "share": 1.0}],
         "severity": {"low": 4000, "typical": 15000, "severe": 38000}},
    ],
}

DEFAULT_RATE_CARD = {
    "_source": ("DEFAULT endorsement rate card, simplified — replace with the agency's "
                "carrier-filed rates before go-live. A fix with no recorded rate is priced "
                "by the producer; a price is never invented here."),
    "by_form": {
        "HX 21 44": {"fix": "Buy back the cooking-equipment grease fire exclusion", "annual_premium": 118},
        # "HX 30 06" is deliberately NOT priced — the sheet must show the honest blank.
        "WB 01 08": {"fix": "Buy back the water backup exclusion", "annual_premium": 96},
        "IM 08 22": {"fix": "Remove the tools-left-in-vehicle exclusion", "annual_premium": 150},
        "RP 14 02": {"fix": "Remove the grease-duct warranty exclusion (with cleaning contract on file)", "annual_premium": 210},
        "CG 24 06": {"fix": "Buy back the assault & battery exclusion", "annual_premium": 380},
    },
    "by_peril": {
        "water_backup": {"fix": "Add water backup coverage, $25,000", "annual_premium": 96},
        "personal_liability": {"fix": "Personal umbrella, $1M over the recorded limit", "annual_premium": 62},
        "tools_equipment": {"fix": "Add an inland-marine tools & equipment floater", "annual_premium": 240},
        "completed_operations": {"fix": "Add completed-operations coverage", "annual_premium": 410},
        "business_income": {"fix": "Add business income coverage, 12 months actual loss", "annual_premium": 175},
        "spoilage": {"fix": "Add spoilage coverage, $25,000", "annual_premium": 130},
        "general_liability": {"fix": "Raise the liability limit / add an umbrella", "annual_premium": 350},
    },
    "commission_rate": 0.12,
}


def scenario_table():
    return store.load("config").get("scenarios") or DEFAULT_SCENARIOS


def rate_card():
    return store.load("config").get("rate_card") or DEFAULT_RATE_CARD


def scenarios_for(acct_type):
    return scenario_table().get(acct_type) or []


# ---------------------------------------------------------------- the rehearsal engine
#
# Pure arithmetic on the recorded policy. Every zeroed dollar carries the
# recorded citation that zeroed it; the deductible is cited, not hidden; the
# output is always all three severities.

def _walk(account, scen, loss):
    covs = {c["peril"]: c for c in account.get("coverages", [])}
    excls = account.get("exclusions", [])
    parts, payout, citations, deductible = [], 0.0, [], None
    for comp in scen["components"]:
        part = round(loss * comp["share"], 2)
        cov = covs.get(comp["peril"])
        if not cov:
            parts.append({"peril": comp["peril"], "loss": part, "payout": 0.0,
                          "kind": "uncovered", "cites": [],
                          "why": f"no {comp['peril']} coverage recorded on this policy"})
            citations.append(f"no recorded {comp['peril']} coverage")
            continue
        hits = [e for e in excls
                if scen["key"] in (e.get("scenarios") or []) and e.get("peril") == comp["peril"]]
        if hits:
            why = "excluded — " + "; ".join(f"{e['name']} ({e['form_ref']})" for e in hits)
            parts.append({"peril": comp["peril"], "loss": part, "payout": 0.0,
                          "kind": "excluded", "cites": hits, "why": why})
            citations.extend(f"{e['name']} ({e['form_ref']})" for e in hits)
            continue
        pay = min(part, cov["limit"])
        capped = part > cov["limit"]
        if capped:
            citations.append(f"{comp['peril']} limit ${cov['limit']:,.0f} (recorded)")
        if deductible is None:
            deductible = cov.get("deductible") or 0
        parts.append({"peril": comp["peril"], "loss": part, "payout": pay,
                      "kind": "capped" if capped else "covered", "cites": [],
                      "limit": cov["limit"],
                      "why": (f"capped at the recorded ${cov['limit']:,.0f} limit" if capped
                              else f"within the recorded ${cov['limit']:,.0f} limit")})
        payout += pay
    ded = deductible or 0
    if ded:
        citations.append(f"deductible ${ded:,.0f} (recorded)")
    payout = max(0.0, round(payout - ded, 2))
    return {"loss": loss, "payout": payout, "deductible": ded,
            "gap": round(loss - payout, 2), "parts": parts, "citations": citations}


def _gap_lines(scen, walk, severe_walk):
    """The fixable shortfalls at TYPICAL severity, plus limit gaps that only
    appear at severe (the umbrella conversation). The deductible is retained by
    design and is never a gap line."""
    out = []
    for p in walk["parts"]:
        short = round(p["loss"] - p["payout"], 2)
        if short <= 0:
            continue
        if p["kind"] == "excluded":
            out.append({"kind": "exclusion", "key": p["cites"][0]["form_ref"],
                        "cite": p["why"], "peril": p["peril"], "gap": short,
                        "scenario_key": scen["key"]})
        elif p["kind"] == "uncovered":
            out.append({"kind": "uncovered", "key": p["peril"], "cite": p["why"],
                        "peril": p["peril"], "gap": short, "scenario_key": scen["key"]})
        elif p["kind"] == "capped":
            out.append({"kind": "limit", "key": p["peril"], "cite": p["why"],
                        "peril": p["peril"], "gap": short, "scenario_key": scen["key"]})
    typical_capped = {p["peril"] for p in walk["parts"] if p["kind"] == "capped"}
    for p in severe_walk["parts"]:
        if p["kind"] == "capped" and p["peril"] not in typical_capped:
            out.append({"kind": "limit", "key": p["peril"], "cite": p["why"],
                        "peril": p["peril"], "gap": round(p["loss"] - p["payout"], 2),
                        "scenario_key": scen["key"], "severe_only": True})
    return out


def rehearse(account):
    """All three severities, every citation, or UNREADABLE. Never one number."""
    if not account.get("policy_recorded"):
        return {"unreadable": True, "account": account.get("id"), "why": UNREADABLE_WHY}
    scens = scenarios_for(account.get("type"))
    if not scens:
        return {"unreadable": True, "account": account.get("id"),
                "why": f"no recorded scenario table for account type '{account.get('type')}' "
                       f"— the table is recorded before the rehearsal runs"}
    out = []
    for scen in scens:
        sev = scen["severity"]
        walks = {lvl: _walk(account, scen, sev[lvl]) for lvl in ("low", "typical", "severe")}
        out.append({"key": scen["key"], "label": scen["label"],
                    "severities": walks,
                    "gap_lines": _gap_lines(scen, walks["typical"], walks["severe"]),
                    "range_note": "severity is a recorded range — low / typical / severe; "
                                  "a single number is refused"})
    return {"account": account["id"], "insured": account.get("insured"),
            "type": account.get("type"), "carrier": account.get("carrier"),
            "renewal": account.get("renewal"),
            "gap_typical_total": round(sum(s["severities"]["typical"]["gap"] for s in out), 2),
            "scenarios": out, "label": REHEARSAL_LABEL,
            "scenario_source": scenario_table()["_source"]}


SINGLE_NUMBER_WHY = ("refused — severity is a recorded range (low / typical / severe), never "
                     "one number. A point estimate is how a rehearsal becomes a promise.")


# ---------------------------------------------------------------- the fix sheet

def _fix_for(kind, key, card):
    src = card["by_form"] if kind == "exclusion" else card["by_peril"]
    rc = src.get(key)
    if not rc:
        return {"fix": None, "annual_premium": None,
                "_missing": f"no recorded rate for {key} — the producer prices this one; "
                            f"a price is never invented here"}
    return {"fix": rc["fix"], "annual_premium": rc["annual_premium"]}


def fix_sheet(account):
    """Each gap → the endorsement/limit change that closes it, priced from the
    RECORDED rate card. A fix without a recorded rate renders blank with the
    reason — never an invented price."""
    r = rehearse(account)
    if r.get("unreadable"):
        return r
    card = rate_card()
    lines, seen = [], set()
    for s in r["scenarios"]:
        for g in s["gap_lines"]:
            k = (g["kind"], g["key"])
            if k in seen:
                continue
            seen.add(k)
            lines.append({**g, "scenario": s["label"], **_fix_for(g["kind"], g["key"], card)})
    closed = {(e.get("kind"), e.get("key")) for e in
              ((account.get("endorsements") or []))}
    for ln in lines:
        ln["closed"] = (ln["kind"], ln["key"]) in closed or \
                       ("exclusion", ln["key"]) in closed or ("uncovered", ln["key"]) in closed
    priced = [ln["annual_premium"] for ln in lines if ln.get("annual_premium")]
    return {"account": account["id"], "insured": account.get("insured"), "lines": lines,
            "priced_total": round(sum(priced), 2) if priced else None,
            "unpriced": len([ln for ln in lines if ln.get("annual_premium") is None]),
            "rate_source": card["_source"], "label": REHEARSAL_LABEL,
            "note": "the deductible is retained by design and is not a gap line"}


# ---------------------------------------------------------------- tone + opinion rules

FORBIDDEN_FEAR = ("devastating", "lose everything", "god forbid", "nightmare")
COVERAGE_OPINIONS = ("you're covered", "you are covered", "fully covered", "should be covered",
                     "will cover", "won't cover", "will be covered", "not covered",
                     "don't worry, it's covered", "denied")


def fear_ok(text):
    t = (text or "").lower()
    hits = [w for w in FORBIDDEN_FEAR if w in t]
    if hits:
        return False, (f"no fear language in anything client-facing — forbidden: "
                       f"{', '.join(hits)}. The rehearsal's arithmetic carries the weight.")
    return True, "ok"


def opinion_free(text):
    t = (text or "").lower()
    hits = [w for w in COVERAGE_OPINIONS if w in t]
    if hits:
        return False, (f"no coverage opinions — forbidden: {', '.join(hits)}. Only the "
                       f"carrier adjusts a real claim; the rehearsal is arithmetic on the "
                       f"recorded policy.")
    return True, "ok"


# ---------------------------------------------------------------- triage
#
# The ACTIVE claim reads first — the client standing in rising water is the
# costly label, and it gets the claims-reporting script, never a coverage
# opinion mid-crisis.

ACTIVE_CLAIM = (
    r"\bflood(ing|ed)?\b.*\b(right now|as we speak|tonight|just)\b",
    r"\b(right now|just happened)\b.*\b(flood|fire|water|pipe|roof)\b",
    r"\bon fire\b",
    r"\bpipe\b.*\bburst\b|\bburst pipe\b",
    r"\breport a claim\b",
    r"\b(broke in(to)?|break[- ]?in|robbed)\b",
    r"\btree (just )?(came|fell|went) through\b",
)
REHEARSAL_ASK = (
    r"\brehears\w*\b",
    r"\bout of pocket\b",
    r"\bwhat (does|would) (our|the|my) policy (actually )?pay\b",
    r"\bwhat would (a|an|the) \w+( \w+)? (fire|backup|claim|slip|lawsuit|theft) (actually )?cost\b",
)
QUOTE_ASK = (
    r"\b(quote|requote|shopping|shop (it|the policy)|price (it|out))\b",
    r"\bcost to add\b",
)
POLICY_QUESTION = (
    r"\b(is|are) \w+( \w+)? on (our|my|the) policy\b",
    r"\bwhat('s| is) (our|my|the) deductible\b",
    r"\bwhich forms\b",
    r"\bwhat (limits|exclusions) (do|does) (we|our policy|my policy) have\b",
)


def read_message(text):
    """active_claim | rehearsal_ask | quote_ask | policy_question | human.
    The active claim reads first — mid-crisis, the script, never an opinion."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in ACTIVE_CLAIM:
        if re.search(rx, t):
            return {"label": "active_claim",
                    "why": "a claim in progress — the claims-reporting script with the "
                           "recorded carrier and claim line, never a coverage opinion "
                           "mid-crisis; only the carrier adjusts the claim"}
    for rx in REHEARSAL_ASK:
        if re.search(rx, t):
            return {"label": "rehearsal_ask",
                    "why": "a rehearsal ask — runs against the recorded policy only, all "
                           "three severities, every citation"}
    for rx in QUOTE_ASK:
        if re.search(rx, t):
            return {"label": "quote_ask",
                    "why": "quoting is a licensed act — routed to a producer; the "
                           "rehearsal can ride along with the quote"}
    for rx in POLICY_QUESTION:
        if re.search(rx, t):
            return {"label": "policy_question",
                    "why": "answered from the recorded policy verbatim, forms cited — "
                           "never an opinion about what the carrier would do"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- renewal integration

RADAR_DAYS = 60


def renewal_radar(ref=None, window=RADAR_DAYS):
    """T-60 DATE ALERTS: every account whose renewal lands inside the window,
    with its rehearsal state. A date from the record, never advice."""
    ref = ref or now()
    latest = {}
    for r in store.load("rehearsals"):
        cur = latest.get(r["account_id"])
        if not cur or (r.get("at") or "") > (cur.get("at") or ""):
            latest[r["account_id"]] = r
    rows = []
    for a in store.load("accounts"):
        d = days_until(a.get("renewal"), ref)
        if d is None or d < 0 or d > window:
            continue
        rh = latest.get(a["id"])
        status = ("UNREADABLE" if not a.get("policy_recorded")
                  else "rehearsed" if rh else "not rehearsed")
        rows.append({"account": a["id"], "insured": a.get("insured"), "type": a.get("type"),
                     "carrier": a.get("carrier"), "renewal": a.get("renewal"),
                     "days": d, "status": status, "demo_tag": a.get("demo_tag"),
                     "gap_typical_total": rh.get("gap_typical_total") if rh else None,
                     "label": f"DATE ALERT — renewal in {d} day(s), from the record; the "
                              f"rehearsal runs at T-{window} and a producer owns the "
                              f"conversation"})
    rows.sort(key=lambda r: r["days"])
    return {"rows": rows, "window_days": window,
            "unreadable": sum(1 for r in rows if r["status"] == "UNREADABLE"),
            "not_rehearsed": sum(1 for r in rows if r["status"] == "not rehearsed")}


# ---------------------------------------------------------------- counted, never asserted

def gap_ledger():
    """gaps_found / gaps_closed, COUNTED from the event log. A gap is closed
    when the endorsement is RECORDED — not when the sheet is sent."""
    found = {}
    for e in store.events(kind="gap_found"):
        found[(e["subject"], (e.get("detail") or {}).get("key"))] = e
    closed = {(e["subject"], (e.get("detail") or {}).get("key"))
              for e in store.events(kind="gap_closed")}
    return {"found": len(found), "closed": len([k for k in closed if k in found]),
            "open": len([k for k in found if k not in closed]),
            "note": "counted from the event log — a gap is closed when the endorsement is "
                    "recorded, not when the sheet is sent"}


def counted_week(ref=None):
    """This week vs last week, both counted; the delta refuses without a
    baseline rather than pretending week one proves anything."""
    ref = ref or now()

    def count(start, end):
        out = {"rehearsals_run": 0, "packets_sent": 0, "gaps_found": 0, "gaps_closed": 0}
        for e in store.load("events"):
            at = parse(e.get("at"))
            if not at or not (start <= at < end):
                continue
            k, actor = e.get("kind"), str(e.get("actor", ""))
            if k == "run_rehearsal" and actor.startswith("agent:"):
                out["rehearsals_run"] += 1
            elif k == "draft_renewal_packet" and actor.startswith("human:"):
                out["packets_sent"] += 1
            elif k == "gap_found":
                out["gaps_found"] += 1
            elif k == "gap_closed":
                out["gaps_closed"] += 1
        return out

    this = count(ref - timedelta(days=7), ref + timedelta(seconds=1))
    prior = count(ref - timedelta(days=14), ref - timedelta(days=7))
    out = {"this_week": this, "prior_week": prior,
           "note": "counted from the event log — never asserted"}
    if not any(prior.values()):
        out["delta"] = unmeasured("no prior-week activity recorded — a delta needs a "
                                  "baseline", field="delta")
    else:
        out["delta"] = {k: this[k] - prior[k] for k in this}
    return out


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="active_claim",
                   costly_note=("AN ACTIVE CLAIM ROUTED LIKE A SALES PING IS THE CLIENT "
                                "STANDING IN RISING WATER WAITING ON US. Recall on "
                                "active_claim reports alone; a false alarm costs a CSR one "
                                "read."))

EVAL_CASES = [
    {"input": "my basement is flooding right now what do i do", "label": "active_claim"},
    {"input": "the kitchen is on fire we just got out", "label": "active_claim"},
    {"input": "a tree just came through the roof and water is coming in", "label": "active_claim"},
    {"input": "someone broke into the shop and took all the tools", "label": "active_claim"},
    {"input": "we need to report a claim, a pipe burst an hour ago", "label": "active_claim"},
    {"input": "what would a kitchen fire actually cost us out of pocket", "label": "rehearsal_ask"},
    {"input": "can you run that claim rehearsal on our policy before renewal", "label": "rehearsal_ask"},
    {"input": "if a customer slips at the restaurant what does our policy pay", "label": "rehearsal_ask"},
    {"input": "can you quote our home and auto, we're shopping around", "label": "quote_ask"},
    {"input": "what would it cost to add my teenage driver", "label": "quote_ask"},
    {"input": "is water backup on our policy", "label": "policy_question"},
    {"input": "what's our deductible on the homeowners", "label": "policy_question"},
    {"input": "which forms are attached to the GL policy", "label": "policy_question"},
    {"input": "", "label": "human"},
    {"input": "thanks for the holiday card, see you at the game", "label": "human"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":           {"rung": "R3", "reason": "routing only; the active claim reads first"},
    "log_claim_intake":       {"rung": "R2", "reason": "the verbatim record and the carrier hand-off cannot wait; internal only"},
    "run_rehearsal":          {"rung": "R2", "reason": "arithmetic on the recorded policy; internal until a human sends anything"},
    "promise_coverage":       {"rung": "R0", "reason": "THE SYSTEM NEVER DOES THIS. A rehearsal is arithmetic on the recorded policy — only the carrier adjusts a real claim, and every sheet says so", "never_promote": True},
    "rehearse_unread_policy": {"rung": "R0", "reason": "THE SYSTEM NEVER DOES THIS. No recorded policy detail → UNREADABLE — we read policies before we rehearse them", "never_promote": True},
    "fear_language":          {"rung": "R0", "reason": "THE SYSTEM NEVER DOES THIS. No 'devastating', no 'lose everything', no 'God forbid', no 'nightmare' — the arithmetic carries the weight; the tone check is structural", "never_promote": True},
    "single_number_severity": {"rung": "R0", "reason": "THE SYSTEM NEVER DOES THIS. Severity is a recorded range — low / typical / severe. A point estimate is how a rehearsal becomes a promise", "never_promote": True},
    "draft_claim_script":     {"rung": "R1", "reason": "outward in a crisis — the recorded carrier and claim line, never a coverage opinion; a human sends"},
    "draft_fix_sheet":        {"rung": "R1", "reason": "outward + money — priced from the recorded rate card; a licensed producer sends"},
    "draft_renewal_packet":   {"rung": "R1", "reason": "outward — the renewal conversation belongs to a producer; the rehearsal rides in the packet"},
    "draft_policy_reply":     {"rung": "R1", "reason": "outward — quotes the recorded policy verbatim, forms cited, no opinion; a human sends"},
    "record_endorsement":     {"rung": "R1", "reason": "money — closing a gap changes the client's bill; a human records it"},
})
gate = Gate(store, matrix)

MOVING = ("read_message", "log_claim_intake", "run_rehearsal", "draft_claim_script",
          "draft_fix_sheet", "draft_renewal_packet", "draft_policy_reply",
          "record_endorsement")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("client:",))


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Rehearsal OS — what it computes to")
        .line("Retention lift at rehearsed renewals", "revenue",
              "rehearsed renewals × points gained × avg commission",
              ["rehearsed_renewals", "retention_points_gained", "avg_commission"],
              lambda g: float(g["rehearsed_renewals"]) * float(g["retention_points_gained"])
              * float(g["avg_commission"]),
              note="rehearsed renewals are counted from this system's own log; the lift is "
                   "your number, measured against your unrehearsed book")
        .line("Endorsement revenue from closed gaps", "revenue",
              "gaps closed × avg endorsement premium × commission",
              ["gaps_closed", "avg_endorsement_premium", "commission_rate"],
              lambda g: float(g["gaps_closed"]) * float(g["avg_endorsement_premium"])
              * float(g["commission_rate"]),
              note="gaps closed are counted — closed when the endorsement is recorded, not "
                   "when the sheet is sent")
        .line("The uncovered-claim E&O file", "scenario",
              "you decide what the uncovered claim that never landed is worth",
              ["eo_claim_value"], lambda g: float(g["eo_claim_value"]),
              assumption="never a saving — the claim that did not land uncovered cannot be "
                         "counted, so this line stays blank until you put your own number "
                         "on it")
        .line("CSR hours on renewal prep", "time_saved", "hrs/wk × 50 × loaded rate",
              ["csr_hours_wk", "csr_rate"],
              lambda g: float(g["csr_hours_wk"]) * 50 * float(g["csr_rate"])))


def roi(given):
    rec = {}
    rows = store.load("rehearsals")
    if rows:
        rec["rehearsed_renewals"] = len({r["account_id"] for r in rows})
    led = gap_ledger()
    rec["gaps_closed"] = led["closed"]
    card = rate_card()
    rec["commission_rate"] = card.get("commission_rate")
    priced = ([v["annual_premium"] for v in card.get("by_form", {}).values()]
              + [v["annual_premium"] for v in card.get("by_peril", {}).values()])
    if priced:
        rec["avg_endorsement_premium"] = round(sum(priced) / len(priced), 2)
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out
