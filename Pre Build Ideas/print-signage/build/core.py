#!/usr/bin/env python3
"""Proof OS — domain core (print & signage shop).

Rules live here: the proof gate (no production without a recorded approval),
the approval chase ladder, capacity promise dates (Traveler pattern), the IP
red-flag check, and the matrix.

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

TABLES = ("config", "customers", "jobs", "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="PROOFOS_DATA_ROOT")

# ---------------------------------------------------------------- the proof gate

def can_produce(job):
    """A job reaches the press only with a recorded proof approval — who
    clicked, when, which revision. A verbal go-ahead is a note, not a gate pass."""
    ap = job.get("proof_approval") or {}
    if ap.get("approved_by") and ap.get("at") and ap.get("revision"):
        return True, (f"proof rev {ap['revision']} approved by {ap['approved_by']} at "
                      f"{str(ap['at'])[:16]} — to the press")
    if job.get("verbal_note"):
        return False, (f"a verbal go-ahead is on file (\"{job['verbal_note'][:40]}…\") and it is "
                       f"a note, not a gate pass. No recorded proof approval, no production — an "
                       f"eaten reprint always starts with 'they said go ahead'.")
    return False, ("no recorded proof approval — no production. The approval records who "
                   "clicked, when, and which revision; that record is what a reprint dispute "
                   "reads from.")


# ---------------------------------------------------------------- IP red flags

IP_MARKS = ("nike", "disney", "nfl", "mlb", "marvel", "coca-cola", "star wars", "pokemon",
            "supreme", "gucci")


def ip_check(job):
    """Art referencing third-party marks queues for a human authorization
    check; software never approves those to press."""
    desc = (job.get("art_desc") or "").lower()
    hits = [m for m in IP_MARKS if m in desc]
    if hits:
        return {"flagged": True, "marks": hits,
                "why": (f"the art references {', '.join(hits)} — a human confirms the customer's "
                        f"right to print it; software never approves trademarked art to press")}
    return {"flagged": False}


# ---------------------------------------------------------------- capacity dates

def promise_date(hours_needed, ref=None):
    """A date computes from recorded press capacity or is refused."""
    ref = ref or now()
    cfg = store.load("config")
    daily = cfg.get("press_hours_per_day")
    if not daily:
        return unmeasured("no recorded press capacity — a date without arithmetic is a guess "
                          "with a calendar on it", field="date")
    booked = cfg.get("hours_booked_ahead") or 0
    days_out = (booked + hours_needed) / daily
    date = ref + timedelta(days=days_out + 1)
    return {"date": iso(date), "basis": f"({booked}h booked + {hours_needed}h this job) / "
                                        f"{daily}h-day + 1 buffer day",
            "note": "a human commits the date — the arithmetic is shown"}


def rush_displacement(hours_needed):
    """What a rush actually displaces — named, never silent."""
    jobs = [j for j in store.load("jobs")
            if not j.get("produced_at") and j.get("promised_date") and not j.get("demo_tag")]
    jobs.sort(key=lambda j: j["promised_date"])
    displaced, remaining = [], hours_needed
    for j in jobs:
        if remaining <= 0:
            break
        displaced.append({"job": j["id"], "desc": j.get("desc"),
                          "promised": j.get("promised_date")})
        remaining -= j.get("est_hours", 2)
    return {"displaced": displaced,
            "note": "a rush is a trade, not free speed — these promised jobs move, and their "
                    "customers hear it from us before they notice"}


# ---------------------------------------------------------------- triage

APPROVAL_MSG = (
    r"\b(approved?|looks good|good to go|go ahead|print it|run it|ship it)\b",
)
ART_INBOUND = (
    r"\b(attached|here('?s| is)|sending)\b.*\b(art|artwork|file|logo|design|pdf|ai file)\b",
    r"\b(art|artwork|files?)\b.*\b(attached|enclosed|coming|sent)\b",
)
RUSH = (
    r"\b(rush|asap|urgent|tomorrow|by friday|need (it|them) (by|for))\b",
)
COMPLAINT = (
    r"\b(wrong|off|doesn'?t match|different|misspell|typo|crooked|blurry|color is)\b",
)


def read_message(text):
    """approval | art_inbound | rush | complaint | human. Approval reads FIRST —
    a click that never got recorded is the costly miss."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in COMPLAINT:
        if re.search(rx, t):
            return {"label": "complaint",
                    "why": "a quality complaint — answered from the approved proof revision, or "
                           "honestly if no approval exists ('what we approved' in a complaint is "
                           "not an approval)"}
    for rx in APPROVAL_MSG:
        if re.search(rx, t):
            return {"label": "approval",
                    "why": "an approval — recorded against the proof revision NOW; the click that "
                           "never got recorded is the eaten reprint"}
    for rx in ART_INBOUND:
        if re.search(rx, t):
            return {"label": "art_inbound", "why": "art received — preflight + IP check queue"}
    for rx in RUSH:
        if re.search(rx, t):
            return {"label": "rush", "why": "rush request — priced with its displacement named"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- chase ladder

CHASE_MAX_TOUCHES = 3
CHASE_COOLDOWN_DAYS = 2


def chase_plan(job, ref=None):
    ref = ref or now()
    if job.get("proof_approval") or job.get("produced_at") or job.get("demo_tag"):
        return {"action": "none", "why": "approved or produced"}
    if not job.get("proof_sent_at"):
        return {"action": "none", "why": "no proof out yet"}
    touches = job.get("chase_touches") or []
    if len(touches) >= CHASE_MAX_TOUCHES:
        return {"action": "human", "why": f"ladder exhausted at {CHASE_MAX_TOUCHES} — a person calls"}
    last = parse(touches[-1]["at"]) if touches else parse(job.get("proof_sent_at"))
    if last and (ref - last).days < CHASE_COOLDOWN_DAYS:
        return {"action": "none", "why": f"inside the {CHASE_COOLDOWN_DAYS}-day cooldown"}
    return {"action": "draft_chase", "why": f"touch {len(touches)+1} of {CHASE_MAX_TOUCHES}"}


def waiting_on_proof(ref=None):
    ref = ref or now()
    rows = []
    for j in store.load("jobs"):
        if j.get("proof_approval") or j.get("produced_at") or not j.get("proof_sent_at") \
           or j.get("demo_tag"):
            continue
        sent = parse(j["proof_sent_at"])
        rows.append({"job": j["id"], "desc": j.get("desc"), "value": j.get("value", 0),
                     "days_waiting": (ref - sent).days if sent else None})
    rows.sort(key=lambda r: -(r["days_waiting"] or 0))
    return {"rows": rows, "value": round(sum(r["value"] for r in rows), 2),
            "note": "money waiting on a click — counted from the job ledger"}


def recovered_this_week(ref=None):
    """Counted: approvals recorded, jobs produced, chases a human sent."""
    ref = ref or now()
    approved = [j for j in store.load("jobs")
                if (j.get("proof_approval") or {}).get("at")
                and (ref - (parse(j["proof_approval"]["at"]) or ref)).days <= 7]
    produced = [j for j in store.load("jobs")
                if j.get("produced_at") and (ref - (parse(j["produced_at"]) or ref)).days <= 7]
    chases = sum(1 for e in store.events(kind="draft_proof_chase")
                 if str(e.get("actor", "")).startswith("human:")
                 and (ref - (parse(e.get("at")) or ref)).days <= 7)
    return {"approvals_recorded": len(approved),
            "approved_value": round(sum(j.get("value", 0) for j in approved), 2),
            "jobs_produced": len(produced), "chases_sent": chases,
            "note": "counted from the job ledger and the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="approval",
                   costly_note=("AN APPROVAL THAT NEVER GOT RECORDED IS THE EATEN REPRINT — "
                                "'they said go ahead' with nothing behind it. Over-routing "
                                "costs a read."))

EVAL_CASES = [
    {"input": "looks good, go ahead and print it", "label": "approval"},
    {"input": "approved! run it", "label": "approval"},
    {"input": "good to go on the banners", "label": "approval"},
    {"input": "here's the artwork attached as a pdf", "label": "art_inbound"},
    {"input": "sending the logo files over now", "label": "art_inbound"},
    {"input": "need these by friday for the trade show, rush if you have to", "label": "rush"},
    {"input": "can you do 500 flyers asap", "label": "rush"},
    {"input": "the color is way off from what we approved", "label": "complaint"},
    {"input": "there's a typo in the headline on the signs", "label": "complaint"},
    {"input": "", "label": "human"},
    {"input": "what are your hours saturday", "label": "human"},
    {"input": "ship it, we're happy with the last revision", "label": "approval"},
    {"input": "the banner came out crooked on the grommet side", "label": "complaint"},
    {"input": "artwork enclosed, two versions to choose from", "label": "art_inbound"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":       {"rung": "R3", "reason": "routing only; the approval-first read is the point"},
    "record_approval":    {"rung": "R2", "reason": "recording the click against the revision cannot wait"},
    "produce_without_proof_approval": {"rung": "R0", "reason": "no recorded approval, no production — by construction", "never_promote": True},
    "promise_date_without_capacity": {"rung": "R0", "reason": "a date without arithmetic is a guess with a calendar on it", "never_promote": True},
    "approve_trademarked_art": {"rung": "R0", "reason": "a human confirms the right to print third-party marks", "never_promote": True},
    "draft_proof_chase":  {"rung": "R1", "reason": "outward message — a human sends; the clock starts at the click"},
    "draft_rush_quote":   {"rung": "R1", "reason": "a rush is a trade — a human prices it with the displacement named"},
    "draft_complaint_reply": {"rung": "R1", "reason": "outward reply — cites the approved revision, or admits none exists"},
    "release_to_press":   {"rung": "R1", "reason": "production start — a human releases, past the proof gate"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Proof OS — what it computes to")
        .line("Proof-stalled revenue released", "cash_timing", "value waiting on a click (counted)",
              ["waiting_value"], lambda g: float(g["waiting_value"]),
              note="cash timing — the work is sold; the click is the bottleneck")
        .line("Reprints avoided at the gate", "scenario", "reprints/yr × avg reprint cost",
              ["reprints_yr", "avg_reprint"],
              lambda g: float(g["reprints_yr"]) * float(g["avg_reprint"]),
              assumption="prevented errors cannot be counted — this is your history priced by you")
        .line("Scheduling hours", "time_saved", "hrs/wk × 52 × rate",
              ["office_hours_wk", "office_rate"],
              lambda g: float(g["office_hours_wk"]) * 52 * float(g["office_rate"])))


def roi(given):
    rec = {}
    rec["waiting_value"] = waiting_on_proof()["value"]
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "record_approval", "draft_proof_chase", "draft_rush_quote",
          "draft_complaint_reply", "release_to_press")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("customer:",))
