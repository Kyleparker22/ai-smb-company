#!/usr/bin/env python3
"""Inspect OS — domain core (property / home inspection).

Rules live here: the append-only findings register (a revision is a NEW entry,
both versions kept), the soften-request refusal, the client-first release rule,
the repair-cost and buy-advice refusals, the report clock, and the matrix.

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

TABLES = ("config", "inspections", "findings", "messages", "referrals",
          "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="INSPECTOS_DATA_ROOT")

REPORT_HOURS = 24

# ---------------------------------------------------------------- triage

SOFTEN = (
    r"\b(leave (out|off)|remove|delete|drop|take out|soften|tone down|downplay|reword)\b.*"
    r"\b(finding|note|item|roof|section|comment|the part about)\b",
    r"\bdon'?t (mention|include|put)\b.*\b(report|finding)\b",
    r"\b(finding|note|item|section|comment)\b.*\b(reword|soften|tone down|leave out|remove|drop)\b",
    r"\b(kill|tank)\b.*\bdeal\b.*\b(report|reword|comment)\b|"
    r"\b(report|comment|finding)\b.*\b(kill|tank)\b.*\bdeal\b",
)
EARLY_COPY = (
    r"\b(send|get|see|forward|shoot)\b.*\b(me|us)\b.*\b(report|copy|findings)\b.*"
    r"\b(before|early|first|preview|ahead)\b",
    r"\b(agent|realtor|listing side)\b.*\b(copy|report)\b",
    r"\bcan (i|we) (see|get) (the|a) (report|copy)\b.*\b(before|ahead)\b",
)
COST_ASK = (
    r"\b(how much|what (would|will) it cost|cost to|estimate)\b.*\b(fix|repair|replace)\b",
    r"\b(fix|repair|replace)\w*\b.*\b(how much|cost|estimate|run me)\b",
)
BOOKING = (
    r"\b(book|schedule|need|set up)\b.*\binspect\w*",
    r"\binspect\w*\b.*\b(friday|monday|this week|next week|tomorrow|closing)\b",
)
STATUS = (
    r"\b(report|results?)\b.*\b(ready|status|when|done|eta)\b",
    r"\bwhen (will|do) (i|we) (get|see)\b.*\breport\b",
)


def read_message(text):
    """soften_request | early_copy_request | cost_ask | booking | status | human.
    The soften request reads FIRST — it is the integrity event."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in SOFTEN:
        if re.search(rx, t):
            return {"label": "soften_request",
                    "why": "a request to soften or omit a finding — refused and logged verbatim; "
                           "the refusal event IS the E&O defense file"}
    for rx in EARLY_COPY:
        if re.search(rx, t):
            return {"label": "early_copy_request",
                    "why": "a non-client asking for the report — the report releases to the "
                           "paying client; anyone else needs the client's recorded authorization"}
    for rx in COST_ASK:
        if re.search(rx, t):
            return {"label": "cost_ask",
                    "why": "a repair-cost question — not our license; the report refers to trades"}
    for rx in STATUS:
        if re.search(rx, t):
            return {"label": "status", "why": "report status — answered from the clock"}
    for rx in BOOKING:
        if re.search(rx, t):
            return {"label": "booking", "why": "booking — draft at R1"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- append-only findings

def add_finding(inspection_id, text, severity, actor="inspector"):
    """Findings are append-only. This is the ONLY way one enters."""
    f = {"id": store.nid("fn"), "inspection_id": inspection_id, "text": text,
         "severity": severity, "at": iso(), "supersedes": None}
    store.upsert("findings", f)
    store.log_event("finding_recorded", f["id"], f"human:{actor}", "R1",
                    {"severity": severity})
    return f


def revise_finding(finding_id, new_text, new_severity, actor="inspector"):
    """A revision is a NEW entry pointing at the old one. Both stay. There is
    no edit and no delete anywhere in this module — that absence is the rule."""
    old = store.by_id("findings", finding_id)
    if not old:
        return {"error": "no such finding"}
    f = {"id": store.nid("fn"), "inspection_id": old["inspection_id"], "text": new_text,
         "severity": new_severity, "at": iso(), "supersedes": finding_id}
    store.upsert("findings", f)
    store.log_event("finding_revised", f["id"], f"human:{actor}", "R1",
                    {"supersedes": finding_id,
                     "note": "both versions remain in the register"})
    return f


def findings_for(inspection_id):
    """Current view + full history. Superseded entries are marked, never gone."""
    rows = [f for f in store.load("findings") if f.get("inspection_id") == inspection_id]
    superseded = {f["supersedes"] for f in rows if f.get("supersedes")}
    return {"current": [f for f in rows if f["id"] not in superseded],
            "history": rows,
            "note": "append-only — a revision points at what it replaced; nothing is ever edited "
                    "or deleted"}


# ---------------------------------------------------------------- release rule

def can_release(inspection, requester):
    """The report releases to the paying client. Anyone else needs the client's
    recorded authorization."""
    if requester == inspection.get("client_name"):
        return True, "the paying client — released on request"
    authorized = inspection.get("release_authorized") or []
    if requester in authorized:
        return True, f"released under the client's recorded authorization for {requester}"
    return False, (f"the report belongs to the paying client ({inspection.get('client_name')}). "
                   f"{requester} gets it when the client's authorization is recorded — not before, "
                   f"and not because the deal is stressful.")


# ---------------------------------------------------------------- report clock

def report_clock(inspection, ref=None):
    ref = ref or now()
    done = parse(inspection.get("inspected_at"))
    if not done:
        return unmeasured("no inspection timestamp", field="hours_left")
    if inspection.get("report_sent_at"):
        hours = (parse(inspection["report_sent_at"]) - done).total_seconds() / 3600
        return {"delivered_in_hours": round(hours, 1), "on_time": hours <= REPORT_HOURS}
    left = REPORT_HOURS - (ref - done).total_seconds() / 3600
    return {"hours_left": round(left, 1), "overdue": left < 0}


def referral_ledger():
    rows = {}
    for r in store.load("referrals"):
        src = r.get("source", "direct")
        rows.setdefault(src, 0)
        rows[src] += 1
    return {"by_source": rows, "note": "counted from the referral records"}


def recovered_this_week(ref=None):
    """Counted: reports delivered on time, soften requests refused, bookings
    a human confirmed, inside 7 days."""
    ref = ref or now()
    delivered = [i for i in store.load("inspections")
                 if i.get("report_sent_at")
                 and (ref - (parse(i["report_sent_at"]) or ref)).days <= 7]
    on_time = [i for i in delivered
               if report_clock(i).get("on_time")]
    refusals = sum(1 for e in store.events(kind="refused")
                   if (e.get("detail") or {}).get("action") == "soften_or_remove_finding"
                   and (ref - (parse(e.get("at")) or ref)).days <= 7)
    bookings = sum(1 for e in store.events(kind="draft_booking")
                   if str(e.get("actor", "")).startswith("human:")
                   and (ref - (parse(e.get("at")) or ref)).days <= 7)
    return {"reports_delivered": len(delivered), "on_time": len(on_time),
            "soften_requests_refused": refusals, "bookings_confirmed": bookings,
            "note": "counted from the records and the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="soften_request",
                   costly_note=("A SOFTEN REQUEST GRANTED ONCE IS AN E&O CASE AND A REPUTATION "
                                "GONE — and one MISSED means it was granted by accident. "
                                "Over-routing costs a read."))

EVAL_CASES = [
    {"input": "any chance you could leave out the note about the roof", "label": "soften_request"},
    {"input": "can you tone down the electrical section, it reads scary", "label": "soften_request"},
    {"input": "please don't mention the moisture reading in the report", "label": "soften_request"},
    {"input": "that foundation comment is going to kill the deal, can you reword it", "label": "soften_request"},
    {"input": "I'm the listing agent, can you send me the report before the buyer", "label": "early_copy_request"},
    {"input": "shoot me a copy ahead of the sellers seeing it", "label": "early_copy_request"},
    {"input": "how much would it cost to fix the deck issue you found", "label": "cost_ask"},
    {"input": "what would the furnace repair run me", "label": "cost_ask"},
    {"input": "need to book an inspection before closing on the 28th", "label": "booking"},
    {"input": "can you schedule an inspection for friday morning", "label": "booking"},
    {"input": "is the report ready yet", "label": "status"},
    {"input": "when will we get the report", "label": "status"},
    {"input": "", "label": "human"},
    {"input": "thanks for being so thorough yesterday", "label": "human"},
    {"input": "drop the part about the water heater, seller already knows", "label": "soften_request"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":       {"rung": "R3", "reason": "routing only; the soften-first read is the point"},
    "soften_or_remove_finding": {"rung": "R0", "reason": "findings are append-only — the refusal event IS the defense file", "never_promote": True},
    "release_to_non_client": {"rung": "R0", "reason": "the report belongs to the paying client", "never_promote": True},
    "estimate_repair_cost": {"rung": "R0", "reason": "not our license — the report refers to trades", "never_promote": True},
    "advise_buy_or_walk": {"rung": "R0", "reason": "the inspector reports conditions; the decision is the client's", "never_promote": True},
    "draft_booking":      {"rung": "R1", "reason": "outward booking — a human sends"},
    "draft_status_reply": {"rung": "R1", "reason": "outward reply — a human sends, from the clock"},
    "draft_referral_thanks": {"rung": "R1", "reason": "outward thanks — a human sends"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Inspect OS — what it computes to")
        .line("Report turnaround kept", "revenue", "inspections/mo × avg fee × referral lift",
              ["inspections_mo", "avg_fee", "referral_lift"],
              lambda g: float(g["inspections_mo"]) * 12 * float(g["avg_fee"]) * float(g["referral_lift"]),
              assumption="the referral lift is your estimate of what 24h turnaround earns")
        .line("Admin hours", "time_saved", "hrs/wk × 52 × rate",
              ["office_hours_wk", "office_rate"],
              lambda g: float(g["office_hours_wk"]) * 52 * float(g["office_rate"]))
        .line("The unaltered-findings file", "scenario", "you decide what an E&O defense is worth",
              ["defense_value"], lambda g: float(g["defense_value"]),
              assumption="never a saving — the append-only register is the product"))


def roi(given):
    rec = {}
    rec["inspections_mo"] = len([i for i in store.load("inspections")
                                 if i.get("inspected_at")
                                 and (now() - (parse(i["inspected_at"]) or now())).days <= 30])
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "draft_booking", "draft_status_reply", "draft_referral_thanks")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("agent_ext:", "client:"))
