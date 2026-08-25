#!/usr/bin/env python3
"""Remit OS — domain core (independent pharmacy, PBM reimbursement autopsy).

Rules live here: the contract register (recorded terms or UNAUDITABLE — never a
guessed benchmark), the line-by-line autopsy arithmetic with the clause cited
and the delta to the cent, the ambiguous-clause rule (both readings to a human,
never auto-resolved in either direction), the recoverable ledger aged against
each contract's own appeal window (DATE ALERTS), recovered = counted remittance
corrections only, the margin truth board (the dispensed-at-a-loss list, counted;
no recorded acquisition cost → unmeasured), wrong-pills triage (pharmacist NOW,
never a queue), PHI discipline in outward drafts, and the matrix.

Stdlib only. Honesty rules come from `_kit`.
"""
import re, sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, iso, median, now,   # noqa: E402
                        parse, unmeasured)

TABLES = ("config", "remits", "findings", "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="REMITOS_DATA_ROOT")

# ---------------------------------------------------------------- the contract register

DEFAULT_CONTRACTS = {
    "_source": ("RECORDED contract terms, transcribed from each executed PBM agreement — replace "
                "with the pharmacy's actual contracts before go-live. A PBM whose terms are not "
                "recorded here is UNAUDITABLE, and reads that way; a guessed industry benchmark "
                "is not an audit."),
    "CareMax Rx": {
        "rate_basis": {"kind": "awp_minus", "pct": 0.15,
                       "clause": "§3.1 — brand and generic reimbursed at AWP − 15%"},
        "dispensing_fee": 1.25, "fee_clause": "§3.2 — $1.25 professional dispensing fee per fill",
        "dir_pct": 0.03, "dir_clause": "§5.4 — DIR withheld at 3% of the paid amount",
        "appeal_window_days": 90, "appeal_clause": "§7.2 — 90-day reimbursement appeal window",
    },
    "OptiScript": {
        "rate_basis": {"kind": "awp_minus", "pct": 0.18,
                       "clause": "§4.1 — reimbursement at AWP − 18%"},
        "dispensing_fee": 0.85, "fee_clause": "§4.3 — $0.85 dispensing fee per fill",
        "dir_pct": 0.05, "dir_clause": "§6.1 — DIR withheld at 5% of the paid amount",
        "appeal_window_days": 60, "appeal_clause": "§9.4 — 60-day appeal window",
        "mac_list": {"Metformin 500mg": 0.02, "Lisinopril 10mg": 0.015,
                     "Corvalyn XR 100mg": 2.10},
        "mac_clause": "Exhibit B — MAC list pricing for multi-source generics",
    },
    # "Pinnacle Health Rx" is deliberately NOT here: its remittances exist, its
    # executed contract was never recorded, and the autopsy refuses to guess.
}


def contracts():
    return store.load("config").get("contracts") or DEFAULT_CONTRACTS


def unauditable_pbms():
    cs = contracts()
    return sorted({r["pbm"] for r in store.load("remits") if r.get("pbm") not in cs})


UNAUDITABLE = ("UNAUDITABLE — no recorded contract terms for {pbm}. We can't audit a remittance "
               "against a contract we haven't recorded, and a guessed industry benchmark is not "
               "an audit. Record the executed terms — rate basis, dispensing fee, DIR schedule, "
               "appeal window — and every line here reconciles to the cent.")


# ---------------------------------------------------------------- the autopsy arithmetic

def expected_readings(line, contract):
    """Every plausible reading of what the recorded contract says this line
    pays. One reading when the contract is unambiguous; BOTH when it is not —
    and an ambiguous line is never resolved by software."""
    qty, awp = float(line.get("qty") or 0), float(line.get("awp") or 0)
    fee, rb = contract["dispensing_fee"], contract["rate_basis"]
    awp_reading = {"clause": rb["clause"],
                   "basis": f"AWP ${awp:.2f}/unit × {int(qty)} × (1 − {round(rb['pct']*100)}%) + ${fee:.2f} fee",
                   "expected": round(awp * qty * (1 - rb["pct"]) + fee, 2)}
    mac = (contract.get("mac_list") or {}).get(line.get("drug"))
    if mac is None:
        return {"ambiguous": False, "readings": [awp_reading]}
    mac_reading = {"clause": contract["mac_clause"],
                   "basis": f"MAC ${mac}/unit × {int(qty)} + ${fee:.2f} fee",
                   "expected": round(mac * qty + fee, 2)}
    if line.get("brand"):
        return {"ambiguous": True, "readings": [awp_reading, mac_reading],
                "why": (f"{rb['clause']} prices this brand at AWP − {round(rb['pct']*100)}%, but the "
                        f"drug also appears on the {contract['mac_clause']} — a clause scoped to "
                        f"multi-source generics. The contract does not say which controls for a "
                        f"brand on the list. Both readings go to a human; software never picks "
                        f"the convenient one.")}
    return {"ambiguous": False, "readings": [mac_reading]}


def autopsy_line(line, contract):
    """One remittance line reconciled against the recorded arithmetic.
    Classes: underpaid · dir_drift · correct · ambiguous (· overpaid, to a
    human — kept quietly it becomes a clawback)."""
    out = {k: line.get(k) for k in ("script_ref", "drug", "qty", "awp", "paid", "dir_taken")}
    r = expected_readings(line, contract)
    if r["ambiguous"]:
        out.update({"class": "ambiguous", "readings": r["readings"], "why": r["why"],
                    "route": "human",
                    "note": "never auto-resolved — a human picks the reading, with both shown"})
        return out
    reading = r["readings"][0]
    paid = float(line.get("paid") or 0)
    delta = round(reading["expected"] - paid, 2)
    exp_dir = round(contract["dir_pct"] * paid, 2)
    dir_delta = round(float(line.get("dir_taken") or 0) - exp_dir, 2)
    out.update(expected=reading["expected"], clause=reading["clause"], basis=reading["basis"],
               dir_expected=exp_dir, dir_delta=dir_delta, dir_clause=contract["dir_clause"])
    if delta >= 0.01:
        out.update({"class": "underpaid", "delta": delta,
                    "why": (f"paid ${paid:.2f} against ${reading['expected']:.2f} due under "
                            f"{reading['clause']} — short ${delta:.2f}, to the cent")})
    elif delta <= -0.01:
        out.update({"class": "overpaid", "delta": delta, "route": "human",
                    "why": "paid above the recorded terms — a human reviews; an overpayment "
                           "kept quietly is a clawback later"})
    elif abs(dir_delta) >= 0.01:
        out.update({"class": "dir_drift", "delta": dir_delta,
                    "why": (f"DIR withheld ${float(line.get('dir_taken') or 0):.2f} against "
                            f"${exp_dir:.2f} due under {contract['dir_clause']} — "
                            f"drift ${dir_delta:.2f}")})
    else:
        out.update({"class": "correct", "delta": 0.0,
                    "why": "paid matches the recorded contract arithmetic"})
    return out


def autopsy(remit):
    """The full remittance autopsy — or the UNAUDITABLE refusal, R0, gap named."""
    if isinstance(remit, str):
        remit = store.by_id("remits", remit)
    if not remit:
        return {"error": "no such remittance"}
    c = contracts().get(remit["pbm"])
    if not c:
        ev = store.log_event("refused", remit["id"], "agent:audit", "R0",
                             {"action": "audit_without_recorded_contract",
                              "why": f"no recorded contract terms for {remit['pbm']}"})
        return {"refused": UNAUDITABLE.format(pbm=remit["pbm"]), "unauditable": True,
                "pbm": remit["pbm"], "remit": remit["id"], "event": ev["id"]}
    lines = [autopsy_line(l, c) for l in remit.get("lines") or []]
    by = {}
    for l in lines:
        by[l["class"]] = by.get(l["class"], 0) + 1
    return {"remit": remit["id"], "pbm": remit["pbm"], "remit_date": remit.get("remit_date"),
            "demo_tag": remit.get("demo_tag"), "lines": lines,
            "summary": {"lines": len(lines), "underpaid": by.get("underpaid", 0),
                        "dir_drift": by.get("dir_drift", 0), "ambiguous": by.get("ambiguous", 0),
                        "overpaid": by.get("overpaid", 0), "correct": by.get("correct", 0),
                        "underpaid_value": round(sum(l["delta"] for l in lines
                                                     if l["class"] == "underpaid"), 2),
                        "dir_drift_value": round(sum(l["delta"] for l in lines
                                                     if l["class"] == "dir_drift"), 2)},
            "contract_source": contracts()["_source"]}


# ---------------------------------------------------------------- the recoverable ledger

# The structural PHI whitelist: a finding is built ONLY from these fields, so a
# patient identifier on a remittance line can never reach a finding — and an
# appeal drafts only from a finding, so it can never reach a PBM either.
FINDING_FIELDS = ("script_ref", "drug", "qty", "awp", "paid", "dir_taken", "class",
                  "expected", "delta", "clause", "basis", "dir_expected", "dir_delta",
                  "dir_clause", "readings", "why", "route", "note")


def finding_from_line(remit, al):
    f = {"id": f"fd_{remit['id']}_{al['script_ref']}", "remit": remit["id"],
         "pbm": remit["pbm"], "remit_date": remit.get("remit_date")}
    for k in FINDING_FIELDS:
        if k in al:
            f[k] = al[k]
    f["state"] = "needs_human" if al["class"] in ("ambiguous", "overpaid") else "open"
    if remit.get("demo_tag"):
        f["demo_tag"] = remit["demo_tag"]
    return f


def appeal_days_left(finding, ref=None):
    ref = ref or now()
    c = contracts().get(finding.get("pbm")) or {}
    window = c.get("appeal_window_days")
    rd = parse(finding.get("remit_date"))
    if window is None or not rd:
        return None
    return window - (ref - rd).days


def ledger(ref=None):
    """Every confirmed variance aged against the recorded appeal window.
    Open recoverable is COUNTED (confirmed underpaid + DIR drift, non-demo,
    not yet corrected); ambiguous rows carry no number until a human resolves."""
    ref = ref or now()
    rows = []
    for f in store.load("findings"):
        if f.get("state") == "resolved_correct":
            continue
        dl = appeal_days_left(f, ref)
        row = {k: f.get(k) for k in ("id", "remit", "pbm", "script_ref", "drug", "class",
                                     "expected", "paid", "delta", "clause", "state",
                                     "demo_tag", "readings")}
        row["days_left"] = dl
        row["expired"] = dl is not None and dl < 0
        row["label"] = "DATE ALERT — the contract's own recorded appeal window, not legal advice"
        rows.append(row)
    rows.sort(key=lambda r: (r["days_left"] is None, r["days_left"] or 0))
    open_rows = [r for r in rows if r["class"] in ("underpaid", "dir_drift")
                 and r["state"] in ("open", "appeal_drafted", "appeal_sent")
                 and not r.get("demo_tag")]
    return {"rows": rows,
            "open_recoverable": round(sum(r.get("delta") or 0 for r in open_rows), 2),
            "open_count": len(open_rows),
            "window_source": contracts()["_source"],
            "note": ("counted line-by-line from the recorded contract arithmetic; recovered "
                     "dollars are counted separately, from remittance corrections only")}


def recovered():
    """Recovered = counted remittance corrections ONLY — a recorded correction
    event, posted by a human from the PBM's corrected remittance. Never an
    estimate, never a projection of what appeals 'should' win."""
    evs = store.events(kind="correction_recorded")
    return {"recovered": round(sum((e.get("detail") or {}).get("amount", 0) for e in evs), 2),
            "corrections": len(evs),
            "note": "counted remittance corrections only — never estimated"}


def estimate_recovered():
    """The estimate probe. It refuses, at R0, and never becomes approvable."""
    r = gate.act("estimate_recovered_dollars", "ledger", "recovered_probe",
                 {"why": "an estimate of recovered dollars was requested"})
    return {"refused": ("recovered dollars are COUNTED from recorded remittance corrections "
                        "only — a projection of what appeals 'should' recover is a sales "
                        f"number, not a ledger. Counted so far: ${recovered()['recovered']:,.2f}."),
            "gate": r}


# ---------------------------------------------------------------- the margin truth board

def margin_board():
    """Per-script margin from the RECORDED acquisition cost vs paid. The
    dispensed-at-a-loss list is counted — the number every owner suspects and
    never sees. No recorded acquisition cost → that script reads unmeasured,
    never assumed."""
    cfg = store.load("config")
    acq = (cfg.get("acquisition") or {}).get("costs") or {}
    acq_source = (cfg.get("acquisition") or {}).get("_source", "no acquisition record")
    loss, unmeasured_drugs, measured = [], {}, 0
    for rm in store.load("remits"):
        if rm.get("demo_tag"):
            continue
        for l in rm.get("lines") or []:
            a = acq.get(l.get("drug"))
            if a is None:
                unmeasured_drugs[l["drug"]] = unmeasured_drugs.get(l["drug"], 0) + 1
                continue
            measured += 1
            m = round((float(l.get("paid") or 0) - float(l.get("dir_taken") or 0))
                      - a * float(l.get("qty") or 0), 2)
            if m < 0:
                loss.append({"script_ref": l.get("script_ref"), "drug": l["drug"],
                             "pbm": rm["pbm"], "qty": l.get("qty"), "paid": l.get("paid"),
                             "dir_taken": l.get("dir_taken"),
                             "acq_cost": round(a * float(l.get("qty") or 0), 2), "margin": m})
    loss.sort(key=lambda r: r["margin"])
    return {"loss_rows": loss[:30], "loss_count": len(loss),
            "loss_dollars": round(sum(r["margin"] for r in loss), 2),
            "measured_lines": measured, "acq_source": acq_source,
            "unmeasured": dict(unmeasured(
                "no recorded acquisition cost for these drugs — their margin is unmeasured, "
                "never assumed", field="margin"),
                lines=sum(unmeasured_drugs.values()), drugs=sorted(unmeasured_drugs)),
            "note": "margin = (paid − DIR withheld) − recorded acquisition cost × qty; counted per line"}


# ---------------------------------------------------------------- PHI discipline

def phi_scrub_ok(text, line=None):
    """Outward drafts carry script and remittance references, never patient
    identifiers. Regex net + (when the source line is given) a planted-field
    check. The whitelist in FINDING_FIELDS is the structural half."""
    t = text or ""
    if re.search(r"\b\d{3}-\d{2}-\d{4}\b", t):
        return False, "an SSN pattern never appears in an outward draft"
    if re.search(r"\b(dob|date of birth)\b", t, re.I) and re.search(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", t):
        return False, "a DOB never appears in an outward draft — the script reference is enough"
    if re.search(r"\(\d{3}\)\s?\d{3}-\d{4}|\b\d{3}-\d{3}-\d{4}\b", t):
        return False, "a phone number never appears in an outward draft"
    for f in ("patient", "patient_phone", "patient_dob"):
        v = str((line or {}).get(f) or "")
        if v and v in t:
            return False, f"patient identifier ({f}) found in an outward draft — structurally refused"
    return True, "ok"


# ---------------------------------------------------------------- intake triage

PHARMACIST_NOW = (
    "Please do NOT take anything from that bottle. Keep the bottle and the bag it came in "
    "exactly as they are. A pharmacist is being interrupted right now — not later today, now — "
    "and will call you within minutes at the number on your profile. If any dose has already "
    "been taken and you feel at all unwell, call 911 or Poison Control immediately; do not "
    "wait for our call.")

WRONG_MED = (
    r"\b(wrong|not my|not mine|someone else'?s?)\b.{0,40}\b(pills?|meds?|medications?|medicine|"
    r"prescription|tablets?|capsules?|dose)\b",
    r"\b(pills?|meds?|medications?|medicine|tablets?|capsules?)\b.{0,60}\b(wrong|not mine|not my|"
    r"someone else|don'?t look|look different|looks? wrong|never (?:taken|seen|heard))\b",
    r"\b(label|bottle|bag)\b.{0,60}\b(someone else|different name|never (?:taken|heard)|"
    r"not my name|wrong)\b",
)
PBM_Q = (r"\b(insurance|pbm|prior auth\w*|coverage|covered|deductible|claim|plan)\b",)
PRICE = (r"\b(copay|price|pricing|expensive|overcharg\w*|charged?|cost)\b",)
REFILL = (r"\brefills?\b",
          r"\b(ready|pick ?up)\b.{0,40}\b(prescription|rx|meds?)\b",
          r"\b(prescription|rx|meds?)\b.{0,40}\b(ready|pick ?up)\b")


def read_message(text):
    """wrong_med | pbm_question | price_complaint | refill | human. The
    wrong-pills message reads FIRST — it is the patient-safety event, and its
    reply is the pharmacist-now script, whole and immediate, never a queue."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in WRONG_MED:
        if re.search(rx, t):
            return {"label": "wrong_med",
                    "why": "a possible wrong-medication event — the pharmacist-now script is "
                           "the whole reply, immediately; this never waits in a queue"}
    for rx in PBM_Q:
        if re.search(rx, t):
            return {"label": "pbm_question",
                    "why": "a PBM/insurance question — answered from the recorded claim, "
                           "in the plan's own words"}
    for rx in PRICE:
        if re.search(rx, t):
            return {"label": "price_complaint",
                    "why": "a price question — answered from the fill record, line by line"}
    for rx in REFILL:
        if re.search(rx, t):
            return {"label": "refill", "why": "a refill ask — answered from the fill record"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- counted week

def week_counts(ref=None):
    """The counted week — every number here is counted from the event log or
    the ledgers inside 7 days; nothing asserted."""
    ref = ref or now()

    def within(e):
        return (ref - (parse(e.get("at")) or ref)).days <= 7

    corr = [e for e in store.events(kind="correction_recorded") if within(e)]
    appeals = sum(1 for e in store.events(kind="draft_appeal")
                  if str(e.get("actor", "")).startswith("human:") and within(e))
    alerts = sum(1 for e in store.events(kind="appeal_window_alert") if within(e))
    autopsies = sum(1 for e in store.events(kind="run_autopsy") if within(e))
    return {"corrections_recorded": len(corr),
            "corrected_dollars": round(sum((e.get("detail") or {}).get("amount", 0)
                                           for e in corr), 2),
            "appeals_sent": appeals, "window_alerts": alerts, "autopsies_run": autopsies,
            "note": "counted from the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("intake triage",
                   costly_label="wrong_med",
                   costly_note=("A WRONG-MEDICATION MESSAGE SITTING IN A QUEUE IS A PATIENT "
                                "ABOUT TO TAKE THE WRONG DRUG. Over-routing a refill ask "
                                "costs a read."))

EVAL_CASES = [
    {"input": "i think i got the wrong pills", "label": "wrong_med"},
    {"input": "these pills don't look like my usual ones", "label": "wrong_med"},
    {"input": "the bottle has someone else's name on it", "label": "wrong_med"},
    {"input": "the label says a medication i have never taken", "label": "wrong_med"},
    {"input": "i think these are someone else's pills", "label": "wrong_med"},
    {"input": "grandma got a capsule that looks wrong", "label": "wrong_med"},
    {"input": "my insurance rejected the refill and says prior authorization is needed",
     "label": "pbm_question"},
    {"input": "the pbm says this drug is not covered anymore", "label": "pbm_question"},
    {"input": "insurance says you billed the wrong plan", "label": "pbm_question"},
    {"input": "why did my copay double this month", "label": "price_complaint"},
    {"input": "you charged me more than last time", "label": "price_complaint"},
    {"input": "this prescription got way more expensive", "label": "price_complaint"},
    {"input": "can i get a refill on my lisinopril", "label": "refill"},
    {"input": "is my refill ready for pickup", "label": "refill"},
    {"input": "", "label": "human"},
    {"input": "what time do you close on sunday", "label": "human"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":       {"rung": "R3", "reason": "routing only; the wrong-pills message reads first"},
    "pharmacist_now_reply": {"rung": "R2", "reason": "patient safety cannot wait for a click — the fixed script goes out and the pharmacist is interrupted now"},
    "wrong_med_message_queued": {"rung": "R0", "reason": "a wrong-medication message never waits in a queue — the pharmacist-now script is the whole reply, immediately", "never_promote": True},
    "audit_without_recorded_contract": {"rung": "R0", "reason": "no recorded contract, no audit — a guessed benchmark is not an audit", "never_promote": True},
    "auto_resolve_ambiguous_clause": {"rung": "R0", "reason": "two plausible readings go to a human with both shown — software never picks the convenient one", "never_promote": True},
    "estimate_recovered_dollars": {"rung": "R0", "reason": "recovered = counted remittance corrections only — an estimate is a sales number, not a ledger", "never_promote": True},
    "phi_in_outbound":    {"rung": "R0", "reason": "outward drafts carry script and remit references, never patient identifiers", "never_promote": True},
    "run_autopsy":        {"rung": "R2", "reason": "arithmetic against the recorded terms; every line shows its work"},
    "flag_underpayment":  {"rung": "R2", "reason": "an internal ledger entry with the clause and the delta attached"},
    "appeal_window_alert": {"rung": "R2", "reason": "an internal date alert; the window is the point"},
    "draft_appeal":       {"rung": "R1", "reason": "outward to a PBM — a human sends, with the clause and the delta cited"},
    "draft_pbm_reply":    {"rung": "R1", "reason": "outward reply — a human sends; the plan's own words do the talking"},
    "draft_price_reply":  {"rung": "R1", "reason": "outward reply about money — a human sends, with the fill record attached"},
    "draft_refill_reply": {"rung": "R1", "reason": "outward reply — a human sends; the fill record does the talking"},
    "record_correction":  {"rung": "R1", "reason": "money — a correction is posted by a human from the PBM's corrected remittance, never assumed"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Remit OS — what it computes to")
        .line("Recovered underpayments", "revenue", "counted remittance corrections",
              ["recovered_counted"], lambda g: float(g["recovered_counted"]),
              note="counted from recorded correction events only — never estimated")
        .line("Open recoverable inside the window", "cash_timing",
              "open recoverable × your appeal win rate",
              ["open_recoverable", "appeal_win_rate"],
              lambda g: float(g["open_recoverable"]) * float(g["appeal_win_rate"]),
              note="the open recoverable is counted line-by-line; the win rate is your call")
        .line("Owner audit hours", "time_saved", "hrs/wk × 52 × rate",
              ["audit_hours_wk", "owner_rate"],
              lambda g: float(g["audit_hours_wk"]) * 52 * float(g["owner_rate"]))
        .line("The dispensed-at-a-loss list", "scenario",
              "you decide what the counted at-a-loss list is worth in renegotiation",
              ["loss_list_value"], lambda g: float(g["loss_list_value"]),
              assumption="never a saving — a counted list you renegotiate with, not our number"))


def roi(given):
    rec = {}
    rec["recovered_counted"] = recovered()["recovered"]
    rec["open_recoverable"] = ledger()["open_recoverable"]
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    out["counted_loss_context"] = {"loss_dollars": margin_board()["loss_dollars"],
                                   "note": "shown for the scenario line — counted, and still "
                                           "not summed anywhere as a saving"}
    return out


MOVING = ("read_message", "run_autopsy", "flag_underpayment", "draft_appeal",
          "appeal_window_alert", "draft_pbm_reply", "draft_price_reply",
          "draft_refill_reply", "pharmacist_now_reply", "record_correction")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("patient:", "pbm:"))
