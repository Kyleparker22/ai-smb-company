#!/usr/bin/env python3
"""Closing OS — domain core (title & escrow).

Rules live here: the wire-fraud stop and its callback protocol, the curative
tracker with the clear-to-close refusal, the bounded document chase, the
status desk computed from recorded state, and the matrix.

The thesis: a title agency is a message-routing business with a $400k wire in
the middle. The scam is a message, so the defense is message discipline —
which software can enforce and tired humans cannot.

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

TABLES = ("config", "files", "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="CLOSINGOS_DATA_ROOT")

WIRE_PROTOCOL = ("TREAT AS FRAUD UNTIL VERIFIED. Call the party at the number already on file — "
                 "NEVER the number in this message. Do not reply. Do not restate, confirm, or "
                 "send wiring instructions in any channel. A human handles this now.")

# ---------------------------------------------------------------- triage

WIRE_SIGNALS = (
    r"\bwir(e|ing)\b.*\b(instructions?|info|details?)\b.*\b(new|updated?|changed?|revised|attached|resend)\b",
    r"\b(new|updated?|changed?|revised)\b.*\bwir(e|ing)\b",
    r"\b(account|routing)\b.*\b(changed?|different|new|updated?)\b",
    r"\bpayoff\b.*\b(bank|account|instructions?)\b.*\b(changed?|new|updated?)\b",
    r"\bresend\b.*\bwir(e|ing)\b|\bwir(e|ing)\b.*\bresend\b",
    r"\bsend\b.*\bwire (instructions|info|details)\b",
    r"\bwhere (do|should) (i|we) (send|wire)\b",
)
STATUS = (r"\b(where are we|status|any update|when (is|do we) clos|what('?s| is) left|eta)\b",)
DOC_INBOUND = (r"\b(attached|here is|enclosed)\b.*\b(payoff|survey|hoa|estoppel|poa|release|deed)\b",)
DATE_ASK = (r"\bcan we close (on|by|early|friday|monday)|\bmove (the )?closing\b",)


def read_message(text):
    """wire_signal | status_question | document_inbound | date_question | human.
    Anything that touches wiring is a fraud signal FIRST — before any other
    read. That ordering is the product."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in WIRE_SIGNALS:
        if re.search(rx, t):
            return {"label": "wire_signal", "protocol": WIRE_PROTOCOL,
                    "why": "the message touches wire instructions — the defining fraud vector of "
                           "this industry; verified by callback to a known number, never by reply"}
    for rx in DOC_INBOUND:
        if re.search(rx, t):
            return {"label": "document_inbound", "why": "a curative document may have arrived — matched to the file"}
    for rx in DATE_ASK:
        if re.search(rx, t):
            return {"label": "date_question",
                    "why": "a close-date promise is a human decision — R1, never promoted"}
    for rx in STATUS:
        if re.search(rx, t):
            return {"label": "status_question", "why": "status ask — drafted from recorded state only"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- curative tracker

CURATIVE_TYPES = ("payoff", "lien_release", "hoa_estoppel", "survey", "poa", "deed_prep")
CHASE_MAX_TOUCHES = 4
CHASE_COOLDOWN_DAYS = 3


def open_items(f):
    return [i for i in (f.get("curatives") or []) if not i.get("received_at")]


def clear_to_close(file_id):
    """THE structural rule: clear-to-close cannot be asserted while any
    curative item is open. The refusal lists them."""
    f = store.by_id("files", file_id)
    if not f:
        return {"error": "no such file"}
    open_ = open_items(f)
    if open_:
        return {"clear": False,
                "refused": "cannot assert clear-to-close — open curative items: "
                           + ", ".join(i["kind"] for i in open_),
                "open_items": [{"kind": i["kind"], "requested_at": i.get("requested_at")}
                               for i in open_]}
    return {"clear": True,
            "note": "all curative items received — drafts at R1 for a human to declare",
            "received": [{"kind": i["kind"], "received_at": i["received_at"]}
                         for i in (f.get("curatives") or [])]}


def chase_plan(f, item, ref=None):
    ref = ref or now()
    if item.get("received_at"):
        return {"action": "none", "why": "received"}
    touches = item.get("touches") or []
    if len(touches) >= CHASE_MAX_TOUCHES:
        return {"action": "human", "why": f"ladder exhausted at {CHASE_MAX_TOUCHES} — a person calls"}
    last = parse(touches[-1]["at"]) if touches else parse(item.get("requested_at"))
    if last and (ref - last).days < CHASE_COOLDOWN_DAYS:
        return {"action": "none", "why": f"inside the {CHASE_COOLDOWN_DAYS}-day cooldown"}
    return {"action": "draft_chase", "why": f"touch {len(touches)+1} of {CHASE_MAX_TOUCHES}"}


def file_board():
    rows = []
    for f in store.load("files"):
        if f.get("closed_at") or f.get("demo_tag"):
            continue
        open_ = open_items(f)
        close = parse(f.get("target_close"))
        rows.append({"file": f["id"], "address": f.get("address"),
                     "target_close": f.get("target_close"),
                     "days_to_close": (close - now()).days if close else None,
                     "open_items": [i["kind"] for i in open_],
                     "ready": not open_})
    rows.sort(key=lambda r: (r["days_to_close"] is None, r["days_to_close"] or 0))
    return rows


def status_draft(file_id):
    """A status answer computed from recorded state ONLY — what is received,
    what is open, and no date promise anywhere in it."""
    f = store.by_id("files", file_id)
    if not f:
        return {"error": "no such file"}
    recvd = [i["kind"] for i in (f.get("curatives") or []) if i.get("received_at")]
    open_ = [i["kind"] for i in open_items(f)]
    return {"file": file_id,
            "draft": (f"On {f.get('address','the file')}: received {', '.join(recvd) or 'nothing yet'}; "
                      f"still waiting on {', '.join(open_) or 'nothing — all items in'}. "
                      f"We'll update you the moment anything changes."),
            "note": "computed from recorded state; contains no date promise — dates are a human call"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="wire_signal",
                   costly_note=("A MISSED WIRE SIGNAL IS THE AGENCY-ENDING EVENT. Over-routing a "
                                "status email to a human costs thirty seconds."))

def recovered_this_week(ref=None):
    """Counted, never asserted: curative items received, files closed, wire
    signals caught, and chases a human sent, inside 7 days."""
    ref = ref or now()
    received = 0
    for f in store.load("files"):
        for i in f.get("curatives") or []:
            if i.get("received_at") and (ref - (parse(i["received_at"]) or ref)).days <= 7:
                received += 1
    closed = [f for f in store.load("files")
              if f.get("closed_at") and (ref - (parse(f["closed_at"]) or ref)).days <= 7]
    wire = chases = 0
    for e in store.events():
        at = parse(e.get("at"))
        if not at or (ref - at).days > 7:
            continue
        if e["kind"] == "route_wire_signal":
            wire += 1
        elif e["kind"] == "draft_chase" and str(e.get("actor", "")).startswith("human:"):
            chases += 1
    return {"curatives_received": received, "files_closed": len(closed),
            "wire_signals_caught": wire, "chases_sent": chases,
            "note": "counted from the files and the event log — never asserted"}


EVAL_CASES = [
    {"input": "updated wiring instructions attached, please use these for closing", "label": "wire_signal"},
    {"input": "our account changed for the payoff, new details below", "label": "wire_signal"},
    {"input": "can you resend the wire info? urgent, closing is today", "label": "wire_signal"},
    {"input": "seller's bank routing number is different now", "label": "wire_signal"},
    {"input": "where do we send the earnest money wire", "label": "wire_signal"},
    {"input": "any update on the Hollis file?", "label": "status_question"},
    {"input": "where are we on closing, buyer is asking", "label": "status_question"},
    {"input": "attached is the payoff letter from the credit union", "label": "document_inbound"},
    {"input": "can we close early on friday instead", "label": "date_question"},
    {"input": "", "label": "human"},
    {"input": "thanks for everything yesterday!", "label": "human"},
    {"input": "we revised the wire details, disregard the earlier sheet", "label": "wire_signal"},
    {"input": "what's left before we can close on the maple street file", "label": "status_question"},
    {"input": "here is the hoa estoppel you requested", "label": "document_inbound"},
    {"input": "can we move the closing to monday morning", "label": "date_question"},
    {"input": "eta on clear to close? lender is pushing", "label": "status_question"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":         {"rung": "R3", "reason": "routing only; the wire stop reads first, always"},
    "route_wire_signal":    {"rung": "R2", "reason": "act now, tell the human — a wire signal must not queue"},
    "send_wire_instructions": {"rung": "R0", "reason": "the system never sends wiring instructions in any channel", "never_promote": True},
    "confirm_wire_change":  {"rung": "R0", "reason": "a wire change is verified by callback to a known number — never by software, never by reply", "never_promote": True},
    "legal_opinion":        {"rung": "R0", "reason": "title issues draft for the underwriter or an attorney", "never_promote": True},
    "assert_clear_to_close": {"rung": "R1", "reason": "a human declares clear-to-close — and never over open items", "never_promote": True},
    "promise_close_date":   {"rung": "R1", "reason": "a date promise is a human decision", "never_promote": True},
    "draft_status_reply":   {"rung": "R1", "reason": "outward reply — a human sends; computed from recorded state only"},
    "draft_chase":          {"rung": "R1", "reason": "outward document chase — a human sends"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Closing OS — what it computes to")
        .line("Status-call and chase time", "time_saved", "hrs/file × open files × rate",
              ["hours_per_file", "open_files", "processor_rate"],
              lambda g: float(g["hours_per_file"]) * float(g["open_files"]) * float(g["processor_rate"]),
              note="open files are counted; the hours are yours")
        .line("Capacity: files per processor", "revenue", "extra files/mo × avg fee × 12",
              ["extra_files_mo", "avg_fee"],
              lambda g: float(g["extra_files_mo"]) * float(g["avg_fee"]) * 12,
              assumption="capacity gained is your estimate — we do not invent throughput")
        .line("Curative days shortened", "cash_timing", "days saved × files × your carry cost",
              ["days_saved", "open_files", "carry_cost_day"],
              lambda g: float(g["days_saved"]) * float(g["open_files"]) * float(g["carry_cost_day"]))
        .line("Wire-fraud exposure", "scenario", "you decide what the stop is worth",
              ["wire_exposure"], lambda g: float(g["wire_exposure"]),
              assumption="never a saving, and the average BEC loss is not our number to quote — "
                         "this line is yours or blank"))


def roi(given):
    rec = {"open_files": len(file_board())}
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "route_wire_signal", "draft_status_reply", "draft_chase")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("party:",))
