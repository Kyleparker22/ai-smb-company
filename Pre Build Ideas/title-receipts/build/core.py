#!/usr/bin/env python3
"""Receipt OS — domain core (title & escrow: the underwritable audit trail).

Rules live here: the control ledger (append-only; a correction is a new entry —
there is deliberately no edit function), the coverage-year file with its
exceptions list, the UNTESTED honesty rule, the renewal packet that evidences
and never promises, the realtor proof that carries zero client data, the
inherited wire-fraud stop, and the matrix.

The thesis: the agency's security controls already generate receipts —
callback-verified wire changes, dual-control releases, blocked attempts,
drills. Receipt OS packages that evidence into a file an insurer can price
against and a proof a realtor can trust. The moat itself becomes a revenue
line: evidence-backed premium reduction — and the premium claim is exactly
what the file never makes.

Stdlib only. Honesty rules come from `_kit`.
"""
import re, sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, iso, now,           # noqa: E402
                        parse, unmeasured)

TABLES = ("config", "wires", "ledger", "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="RECEIPTOS_DATA_ROOT")

# The law of this vertical, inherited verbatim from Closing OS (build 20).
WIRE_PROTOCOL = ("TREAT AS FRAUD UNTIL VERIFIED. Call the party at the number already on file — "
                 "NEVER the number in this message. Do not reply. Do not restate, confirm, or "
                 "send wiring instructions in any channel. A human handles this now.")

# The only value number_called_ref can ever hold — there is no parameter
# anywhere that lets a number from an email into a verification receipt.
CALLBACK_REF = "the recorded number on file, never the one in the email"

CONTROLS = ("callback_verification", "dual_control_release", "positive_pay")

# ---------------------------------------------------------------- the control ledger

LEDGER_KINDS = ("wire_change_request", "callback_verification", "dual_control_release",
                "blocked_attempt", "drill_result", "correction")


def ledger_append(kind, wire_id=None, detail=None, at=None, demo_tag=None):
    """The ONLY write path into the control ledger. Append-only by construction:
    this module has no edit, update, or delete function for ledger entries
    (tested with hasattr) — a wrong entry is corrected by `ledger_correct`,
    which appends, and both states stay in the ledger forever."""
    if kind not in LEDGER_KINDS:
        raise ValueError(f"unknown ledger kind: {kind}")
    row = {"id": store.nid("lg"), "at": at or iso(), "kind": kind,
           "wire_id": wire_id, "detail": detail or {}}
    if demo_tag:
        row["demo_tag"] = demo_tag
    rows = store.load("ledger")
    rows.append(row)
    store.save("ledger", rows)
    return row


def ledger_correct(entry_id, why, detail=None, at=None):
    """A correction is a NEW entry pointing at the old one. The old entry is
    not touched; a reader sees both, which is the point."""
    prior = next((e for e in store.load("ledger") if e["id"] == entry_id), None)
    if not prior:
        return {"error": "no such ledger entry"}
    d = {"corrects": entry_id, "why": why}
    d.update(detail or {})
    return ledger_append("correction", wire_id=prior.get("wire_id"), detail=d, at=at,
                         demo_tag=prior.get("demo_tag"))


def ledger_entries(kind=None, wire_id=None, include_demo=True):
    rows = store.load("ledger")
    if kind:
        kinds = {kind} if isinstance(kind, str) else set(kind)
        rows = [e for e in rows if e["kind"] in kinds]
    if wire_id:
        rows = [e for e in rows if e.get("wire_id") == wire_id]
    if not include_demo:
        rows = [e for e in rows if not e.get("demo_tag")]
    return rows


# ---------------------------------------------------------------- the coverage year

def policy_period():
    return store.load("config").get("policy_period") or {}


def _in_period(at, period):
    d = parse(at)
    if not d:
        return False
    start, end = parse(period.get("start")), parse(period.get("end"))
    return (not start or d >= start) and (not end or d <= end)


def _gaps(wire, entries):
    """The chain rule for one wire: every release needs dual control; a wire
    that carried a change request also needs a callback verification."""
    kinds = {e["kind"] for e in entries}
    gaps = []
    if "wire_change_request" in kinds and "callback_verification" not in kinds:
        gaps.append("missing callback — a wire change moved without callback verification")
    if "dual_control_release" not in kinds:
        gaps.append("single-control release — only one human on the release")
    return gaps


def wire_chains(period=None):
    """THE one read path. The successes and the exceptions are computed
    together, in one pass, from the same store — there is no exceptions-free
    variant of this query, so `omit_exception` has no code path. The packet
    renderer requires both halves (see `render_renewal_packet`)."""
    period = period or policy_period()
    by_wire = {}
    for e in ledger_entries(include_demo=False):
        if e.get("wire_id"):
            by_wire.setdefault(e["wire_id"], []).append(e)
    complete, exceptions = [], []
    moved = 0
    for w in store.load("wires"):
        if w.get("demo_tag") or not w.get("released_at"):
            continue
        if not _in_period(w["released_at"], period):
            continue
        moved += 1
        gaps = _gaps(w, by_wire.get(w["id"], []))
        row = {"wire": w["id"], "released_at": w["released_at"]}
        if gaps:
            exceptions.append({**row, "gaps": gaps})
        else:
            complete.append(row)
    return {"wires_moved": moved, "complete": complete, "exceptions": exceptions,
            "note": "successes and exceptions read from the same store in one pass — "
                    "a packet cannot have one without the other"}


def wire_chain(wire_id):
    """One wire's chain end-to-end, for the demo/ledger view. Demo wires
    included here (this is a viewer, not a counter)."""
    w = store.by_id("wires", wire_id)
    if not w:
        return {"error": "no such wire"}
    entries = sorted(ledger_entries(wire_id=wire_id), key=lambda e: e["at"] or "")
    return {"wire": w, "entries": entries, "gaps": _gaps(w, entries)}


def drill_status(control, period=None):
    """A control with no drill result in the period reads UNTESTED — never
    'in place'. A control with no drill behind it is a claim, not a control."""
    period = period or policy_period()
    drills = [e for e in ledger_entries(kind="drill_result", include_demo=False)
              if e["detail"].get("control") == control and _in_period(e["at"], period)]
    if not drills:
        return {"control": control, "status": "UNTESTED",
                "note": "no drill on record this period — a control with no drill behind it "
                        "is a claim, not a control; this file never says 'in place'"}
    last = max(drills, key=lambda e: e["at"] or "")
    return {"control": control, "status": f"tested — {last['detail'].get('result')}",
            "result": last["detail"].get("result"), "last_drill": last["at"],
            "drills_this_period": len(drills)}


def coverage_year():
    """The coverage-year file: everything counted from the control ledger for
    the policy period, exceptions included by construction."""
    period = policy_period()
    chains = wire_chains(period)

    def count(kind):
        return len([e for e in ledger_entries(kind=kind, include_demo=False)
                    if _in_period(e["at"], period)])

    return {"period": period,
            "wires_moved": chains["wires_moved"],
            "chains_complete": len(chains["complete"]),
            "exceptions": chains["exceptions"],
            "wire_change_requests": count("wire_change_request"),
            "verifications": count("callback_verification"),
            "blocked_attempts": count("blocked_attempt"),
            "dual_control_releases": count("dual_control_release"),
            "drills": {c: drill_status(c, period) for c in CONTROLS},
            "note": "counted from the append-only control ledger — never asserted; "
                    "demo fixtures excluded"}


# ---------------------------------------------------------------- the premium rule

FORBIDDEN_PREMIUM = ("guaranteed discount", "will lower your premium", "will reduce your premium",
                     "premium will drop", "premium will go down", "guarantees a discount",
                     "guaranteed reduction")


def premium_ok(text):
    t = (text or "").lower()
    hits = [w for w in FORBIDDEN_PREMIUM if w in t]
    if hits:
        return False, f"no premium promises — forbidden language: {', '.join(hits)}"
    return True, "ok"


# ---------------------------------------------------------------- the renewal packet

def render_renewal_packet(cov):
    """Renders the insurer-facing packet text. STRUCTURAL: it requires both
    halves of the chain read — a coverage file without its exceptions data
    cannot render, which is what makes the counted successes credible."""
    for k in ("exceptions", "chains_complete"):
        if k not in cov:
            raise ValueError("structural: the renewal packet cannot render without the "
                             "exceptions read — omit_exception has no code path")
    cfg = store.load("config")
    period = cov.get("period") or {}
    exc = cov["exceptions"]
    exc_lines = ("\n".join(f"  - wire {x['wire']} ({str(x['released_at'])[:10]}): {'; '.join(x['gaps'])}"
                           for x in exc) if exc else "  - none this period")
    drill_lines = "\n".join(
        f"  - {c}: {d['status']}"
        + (f" (last drill {str(d.get('last_drill'))[:10]}, {d.get('drills_this_period')} this period)"
           if d.get("last_drill") else f" — {d.get('note')}")
        for c, d in cov["drills"].items())
    return (
        f"{cfg.get('company', 'the agency')} — coverage-year control file\n"
        f"Policy period: {str(period.get('start'))[:10]} → {str(period.get('end'))[:10]}\n\n"
        f"Counted from the append-only control ledger (corrections are new entries; "
        f"nothing is ever edited):\n"
        f"  - wires released this period: {cov['wires_moved']}\n"
        f"  - complete control chains: {cov['chains_complete']} of {cov['wires_moved']}\n"
        f"  - wire-change requests received: {cov['wire_change_requests']} — verification is by "
        f"callback to {CALLBACK_REF}; any request that moved unverified is in the exceptions "
        f"below; this system never confirms or acts on a change from the message itself (R0, "
        f"never promotable)\n"
        f"  - callback verifications recorded: {cov['verifications']}\n"
        f"  - blocked or refused attempts: {cov['blocked_attempts']}\n"
        f"  - dual-control releases (two named humans each): {cov['dual_control_releases']}\n\n"
        f"Exceptions — every wire that moved with any gap in its chain:\n{exc_lines}\n\n"
        f"Drill record (a control with no drill this period reads UNTESTED — we do not claim "
        f"it):\n{drill_lines}\n\n"
        f"Underwriters price; we evidence. This file makes no premium claim: the counted year "
        f"and its exceptions are the submission, and the number is yours to set."
    )


# ---------------------------------------------------------------- the client-data scrub

def client_data_leaks(text):
    """Scan outward copy against every recorded party name, file number, and
    amount. Returns the hits; an empty list is the only pass. The realtor
    one-pager is built from counts only, and this check proves it stayed
    that way."""
    t = (text or "").lower()
    flat = t.replace(",", "")
    hits = []
    for w in store.load("wires"):
        party = str(w.get("party") or "")
        if party and party.lower() in t:
            hits.append({"wire": w["id"], "leak": "party name", "value": party})
        ref = str(w.get("file_ref") or "")
        if ref and ref.lower() in t:
            hits.append({"wire": w["id"], "leak": "file number", "value": ref})
        amt = w.get("amount")
        if amt and (f"{int(amt):,}".lower() in t or str(int(amt)) in flat):
            hits.append({"wire": w["id"], "leak": "amount", "value": amt})
    return hits


# ---------------------------------------------------------------- triage

# Inherited exactly from Closing OS — the wire stop reads first, always.
WIRE_SIGNALS = (
    r"\bwir(e|ing)\b.*\b(instructions?|info|details?)\b.*\b(new|updated?|changed?|revised|attached|resend)\b",
    r"\b(new|updated?|changed?|revised)\b.*\bwir(e|ing)\b",
    r"\b(account|routing)\b.*\b(changed?|different|new|updated?)\b",
    r"\bpayoff\b.*\b(bank|account|instructions?)\b.*\b(changed?|new|updated?)\b",
    r"\bresend\b.*\bwir(e|ing)\b|\bwir(e|ing)\b.*\bresend\b",
    r"\bsend\b.*\bwire (instructions|info|details)\b",
    r"\bwhere (do|should) (i|we) (send|wire)\b",
)
INSURER = (
    r"\b(underwriter|insurer|carrier)\b.*\b(needs?|ask\w*|request\w*|wants?)\b",
    r"\b(renewal|e&o|cyber|policy)\b.*\b(audit|application|questionnaire|documentation|controls)\b",
    r"\b(controls?|documentation)\b.*\b(renewal|underwriter|insurer|audit)\b",
)
REALTOR = (
    r"\b(realtor|broker(age)?|referr\w*)\b.*\b(proof|protect\w*|controls?|security|share|safe)\b",
    r"\bproof\b.*\b(buyer|funds|wire)\b",
)
STATUS = (r"\b(where are we|status|any update|when (is|do we) clos|what('?s| is) left|eta)\b",)


def read_message(text):
    """wire_change | insurer_info | realtor_proof | closing_status | human.
    Anything that touches wiring is a fraud signal FIRST — before any other
    read. That ordering is inherited law, not a preference."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in WIRE_SIGNALS:
        if re.search(rx, t):
            return {"label": "wire_change", "protocol": WIRE_PROTOCOL,
                    "why": "the message touches wire instructions — the defining fraud vector of "
                           "this industry; recorded verbatim, verified by callback to the "
                           "recorded number, never acted from the message"}
    for rx in INSURER:
        if re.search(rx, t):
            return {"label": "insurer_info",
                    "why": "an insurer/audit evidence ask — answered from the coverage-year "
                           "file, exceptions included, no premium claim"}
    for rx in REALTOR:
        if re.search(rx, t):
            return {"label": "realtor_proof",
                    "why": "a referral-proof ask — the counted one-pager drafts, zero client data"}
    for rx in STATUS:
        if re.search(rx, t):
            return {"label": "closing_status",
                    "why": "closing status lives in the closing file system — a person answers"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="wire_change",
                   costly_note=("A MISSED WIRE-CHANGE SIGNAL IS THE AGENCY-ENDING EVENT — and the "
                                "one receipt the renewal file cannot survive without. Over-routing "
                                "an insurer ask to a human costs thirty seconds."))

EVAL_CASES = [
    {"input": "updated wiring instructions attached, please use these for closing", "label": "wire_change"},
    {"input": "our account changed for the payoff, new details below", "label": "wire_change"},
    {"input": "can you resend the wire info? urgent, closing is today", "label": "wire_change"},
    {"input": "seller's bank routing number is different now", "label": "wire_change"},
    {"input": "where do we send the earnest money wire", "label": "wire_change"},
    {"input": "we revised the wire details, disregard the earlier sheet", "label": "wire_change"},
    {"input": "our cyber renewal is coming up, the underwriter needs your wire controls documentation", "label": "insurer_info"},
    {"input": "can you send the application info for the E&O renewal audit", "label": "insurer_info"},
    {"input": "the E&O carrier's questionnaire asks for our callback verification drill dates", "label": "insurer_info"},
    {"input": "a realtor asked how we protect buyer funds, do we have something to share", "label": "realtor_proof"},
    {"input": "the brokerage wants proof of your wire fraud controls before referring", "label": "realtor_proof"},
    {"input": "any update on the Bramble Way closing?", "label": "closing_status"},
    {"input": "what's the status on clear to close for maple street", "label": "closing_status"},
    {"input": "where are we on the Hollis closing, seller is asking", "label": "closing_status"},
    {"input": "", "label": "human"},
    {"input": "thanks for the smooth closing last week!", "label": "human"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":         {"rung": "R3", "reason": "routing only; the wire stop reads first, always"},
    "route_wire_change":    {"rung": "R2", "reason": "act now, tell the human — a wire signal must not queue"},
    "record_control_event": {"rung": "R2", "reason": "the receipt writes itself the moment the control runs — that is the product"},
    "act_on_emailed_wire_change": {"rung": "R0", "reason": "the law of the vertical: a wire change is verified by callback to the recorded number on file — never acted from the message, in any channel", "never_promote": True},
    "claim_untested_control": {"rung": "R0", "reason": "a control with no drill behind it is a claim, not a control — it reads UNTESTED, never 'in place'", "never_promote": True},
    "omit_exception":       {"rung": "R0", "reason": "structural: the exceptions query is the same read path as the counted successes — the packet cannot render without both", "never_promote": True},
    "promise_premium_outcome": {"rung": "R0", "reason": "underwriters price; we evidence — the file never claims a discount, it earns one", "never_promote": True},
    "draft_renewal_packet": {"rung": "R1", "reason": "outward to the insurer — a human sends; exceptions included by construction"},
    "draft_realtor_proof":  {"rung": "R1", "reason": "outward to a referral source — a human sends; zero client data, scrub-checked"},
    "draft_insurer_reply":  {"rung": "R1", "reason": "outward reply — a human sends; counts cited, nothing promised"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- counted week

def receipts_this_week(ref=None):
    """Counted, never asserted: control receipts recorded inside 7 days, plus
    wire signals caught at intake."""
    ref = ref or now()

    def count(kind):
        return len([e for e in ledger_entries(kind=kind, include_demo=False)
                    if (ref - (parse(e["at"]) or ref)).days <= 7])

    wire_signals = len([e for e in store.events(kind="route_wire_change")
                        if (ref - (parse(e.get("at")) or ref)).days <= 7])
    return {"verifications": count("callback_verification"),
            "dual_controls": count("dual_control_release"),
            "blocked_attempts": count("blocked_attempt"),
            "drills_run": count("drill_result"),
            "wire_signals_caught": wire_signals,
            "note": "counted from the control ledger and the event log — never asserted"}


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Receipt OS — what it computes to")
        .line("Premium reduction earned at renewal", "revenue",
              "last premium − this premium, from your own invoices",
              ["premium_before", "premium_after"],
              lambda g: float(g["premium_before"]) - float(g["premium_after"]),
              assumption="counted AFTER a renewal from your own invoices — never promised in "
                         "advance; this line is blank until a renewal has happened")
        .line("Realtor referral lift", "revenue", "referred closings/mo × avg fee × 12",
              ["referral_closings_mo", "avg_fee"],
              lambda g: float(g["referral_closings_mo"]) * float(g["avg_fee"]) * 12,
              note="the one-pager opens doors; how many is your count, not ours")
        .line("Audit and renewal prep hours", "time_saved", "hrs/yr × rate",
              ["audit_prep_hours_yr", "staff_rate"],
              lambda g: float(g["audit_prep_hours_yr"]) * float(g["staff_rate"]),
              note="the coverage-year file assembles itself from receipts already recorded")
        .line("The breach that didn't happen", "scenario",
              "you decide what the control chain is worth",
              ["breach_exposure"], lambda g: float(g["breach_exposure"]),
              assumption="never a saving — prevented incidents cannot be counted, and the "
                         "average BEC loss is not our number to quote; this line is yours or blank"))


def roi(given):
    # No ROI input here is counted by this build — the premium delta and the
    # lift are the operator's own numbers, recorded after the fact.
    out = roi_model().render({k: v for k, v in given.items() if v not in (None, "")})
    cov = coverage_year()
    out["counted_context"] = {"verifications": cov["verifications"],
                              "blocked_attempts": cov["blocked_attempts"],
                              "exceptions": len(cov["exceptions"])}
    return out


MOVING = ("read_message", "route_wire_change", "record_control_event",
          "draft_renewal_packet", "draft_realtor_proof", "draft_insurer_reply")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("party:",))
