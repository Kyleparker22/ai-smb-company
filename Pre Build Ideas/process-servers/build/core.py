#!/usr/bin/env python3
"""Serve OS — domain core (process serving agencies).

Rules live here: deadline-first triage (the court deadline is the master
clock), the append-only attempt log recorded AT the attempt (a late-recorded
attempt is labeled late_recorded forever; corrections are NEW entries —
`edit_attempt` does not exist), the affidavit rule (drafts assemble ONLY from
the attempt log, verbatim; software never signs, never attests), the
per-jurisdiction due-diligence table (substituted service refuses until the
recorded rule is satisfied by the log itself), and the matrix.

Stdlib only. Honesty rules come from `_kit`.
"""
import re, sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, days_until,         # noqa: E402
                        hours_between, iso, now, parse, unmeasured)

TABLES = ("config", "servers", "serves", "attempts", "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="SERVEOS_DATA_ROOT")

# ---------------------------------------------------------------- the attempt log

LATE_RECORD_THRESHOLD_H = 4.0

BANDS = {"morning": (6, 12), "afternoon": (12, 18), "evening": (18, 22)}
BAND_ORDER = ("morning", "afternoon", "evening")


def band_of(at):
    d = parse(at)
    if not d:
        return "unknown"
    for name, (a, b) in BANDS.items():
        if a <= d.hour < b:
            return name
    return "off-hours"


def attempt_row(serve_id, server_id, outcome, address, attempted_at=None,
                recorded_at=None, gps_ref=None, who_answered=None, supersedes=None):
    """Build one attempt entry. The late-record arithmetic happens HERE, once,
    at write time — the label is part of the record and is never recomputed
    away. There is deliberately no function in this module that edits or
    deletes an attempt."""
    attempted_at = attempted_at or iso()
    recorded_at = recorded_at or iso()
    gap = hours_between(attempted_at, recorded_at)
    late = gap is not None and gap > LATE_RECORD_THRESHOLD_H
    row = {"id": store.nid("at"), "serve_id": serve_id, "server_id": server_id,
           "attempted_at": attempted_at, "recorded_at": recorded_at,
           "address": address, "gps_ref": gps_ref, "outcome": outcome,
           "who_answered": who_answered, "band": band_of(attempted_at),
           "late_recorded": late, "supersedes": supersedes}
    if late:
        row["late_note"] = (f"recorded {gap:.0f}h after the attempt (threshold "
                            f"{LATE_RECORD_THRESHOLD_H:.0f}h) — labeled late_recorded "
                            f"permanently; a log written from memory is disclosed, never laundered")
    return row


def record_attempt(serve_id, server_id, outcome, address, **kw):
    """The ONLY way an attempt enters the log: append. Recorded AT the attempt
    by the server in the field; `recorded_at` defaults to now."""
    row = attempt_row(serve_id, server_id, outcome, address, **kw)
    store.upsert("attempts", row)
    store.log_event("attempt_recorded", serve_id, f"human:{server_id}", None,
                    {"attempt": row["id"], "outcome": outcome,
                     "late_recorded": row["late_recorded"]})
    s = store.by_id("serves", serve_id)
    if s and s.get("status") == "papers_in":
        s["status"] = "attempting"
        store.upsert("serves", s)
    return row


def correct_attempt(attempt_id, server_id, **fields):
    """A correction is a NEW entry from the SAME server pointing at the old
    one. Both stay in the log; the original — flags included — is untouched."""
    old = store.by_id("attempts", attempt_id)
    if not old:
        return {"error": "no such attempt"}
    if server_id != old.get("server_id"):
        return {"refused": ("only the server who recorded an attempt corrects it — anyone "
                            "else's version is a separate statement, not a correction")}
    merged = {k: fields.get(k, old.get(k)) for k in
              ("outcome", "address", "gps_ref", "who_answered", "attempted_at")}
    row = attempt_row(old["serve_id"], server_id, merged["outcome"], merged["address"],
                      attempted_at=merged["attempted_at"], recorded_at=iso(),
                      gps_ref=merged["gps_ref"], who_answered=merged["who_answered"],
                      supersedes=attempt_id)
    store.upsert("attempts", row)
    store.log_event("attempt_corrected", old["serve_id"], f"human:{server_id}", None,
                    {"attempt": row["id"], "supersedes": attempt_id,
                     "note": "both entries remain; the original keeps its labels"})
    return row


def current_attempts(rows):
    """The current chain: entries not superseded by a later correction,
    ordered by when they were attempted. Superseded entries stay on disk."""
    sup = {a["supersedes"] for a in rows if a.get("supersedes")}
    return sorted((a for a in rows if a["id"] not in sup),
                  key=lambda a: a.get("attempted_at") or "")


def attempts_for(serve_id, all_rows=None):
    rows = all_rows if all_rows is not None else store.load("attempts")
    return current_attempts([a for a in rows if a.get("serve_id") == serve_id])


# ---------------------------------------------------------------- due diligence

DEFAULT_DILIGENCE_RULES = {
    "_source": ("DEFAULT due-diligence rules, simplified per-county placeholders — replace with "
                "each court's actual rule before go-live. A rule nobody recorded cannot "
                "authorize substituted service."),
    "counties": {
        "Hardin":  {"attempts": 3, "distinct_bands": 2},
        "Bellamy": {"attempts": 4, "distinct_bands": 3},
        "Ashford": {"attempts": 3, "distinct_bands": 3},
    },
}


def diligence_rules():
    return store.load("config").get("diligence_rules") or DEFAULT_DILIGENCE_RULES


def due_diligence(serve, atts=None):
    """The recorded jurisdiction rule (n attempts across k distinct recorded
    hour-bands) evaluated against the log ITSELF — never against a story.
    Unmet → not met, with the gap named."""
    rules = diligence_rules()
    county = serve.get("county")
    rule = (rules.get("counties") or {}).get(county)
    if not rule:
        return {"met": False, "rule": None,
                "why": (f"no recorded due-diligence rule for "
                        f"{county or 'this county'} — a rule nobody recorded cannot authorize "
                        f"substituted service; record the court's rule first")}
    atts = atts if atts is not None else attempts_for(serve["id"])
    bands = sorted({a["band"] for a in atts if a.get("band") in BANDS})
    n, b = len(atts), len(bands)
    rule_str = f"{county} rule: {rule['attempts']} attempts across {rule['distinct_bands']} hour-bands"
    gaps = []
    if n < rule["attempts"]:
        gaps.append(f"{rule['attempts'] - n} more attempt(s)")
    if b < rule["distinct_bands"]:
        gaps.append(f"coverage of {rule['distinct_bands'] - b} more hour-band(s)")
    counted = {"attempts": n, "bands": bands, "source": rules["_source"]}
    if gaps:
        return {"met": False, "rule": rule_str, "counted": counted,
                "why": (f"substituted service refused — {rule_str} (the recorded rule); the log "
                        f"shows {n} attempt(s) across {b} band(s) "
                        f"({', '.join(bands) or 'none'}); gap: {' and '.join(gaps)}. "
                        f"A substituted service the log can't defend is the quashed-service file.")}
    return {"met": True, "rule": rule_str, "counted": counted,
            "why": (f"{rule_str} — satisfied by the log itself: {n} attempt(s) across "
                    f"{b} band(s) ({', '.join(bands)})")}


def next_window(serve, atts=None):
    """The next attempt hour-band, from the bands the log hasn't covered."""
    atts = atts if atts is not None else attempts_for(serve["id"])
    covered = {a["band"] for a in atts}
    for name in BAND_ORDER:
        if name not in covered:
            a, b = BANDS[name]
            return f"{name} ({a:02d}:00–{b:02d}:00)"
    return "any band — the log already covers morning, afternoon and evening"


# ---------------------------------------------------------------- the affidavit rule

def affidavit_draft(serve_id, extra_fact=None):
    """Assembles ONLY from the attempt log, verbatim. An extra 'fact' offered
    from outside the log is refused and the request preserved verbatim —
    structurally, there is no parameter path by which it reaches the draft."""
    s = store.by_id("serves", serve_id)
    if not s:
        return {"error": "no such serve"}
    if extra_fact:
        ev = store.log_event("refused", serve_id, "agent:desk", "R0",
                             {"action": "add_unrecorded_fact_to_affidavit",
                              "verbatim": extra_fact,
                              "why": "the affidavit assembles ONLY from the attempt log — a fact "
                                     "never recorded at an attempt has no way into the draft"})
        return {"refused": ("the affidavit assembles ONLY from the attempt log, verbatim. A fact "
                            "that was never recorded at an attempt has no way into this draft — "
                            "if it happened, the server records it as a NEW log entry and the "
                            "draft rebuilds. This request is now part of the record."),
                "event": ev["id"]}
    atts = attempts_for(serve_id)
    if not atts:
        return {"refused": ("cannot draft — no recorded attempts on this serve. An affidavit "
                            "without a log behind it is a story, not an oath.")}
    servers = store.index("servers")
    kind = ("AFFIDAVIT OF SERVICE" if s.get("status") in ("served", "substituted")
            else "AFFIDAVIT OF DUE DILIGENCE (non-service)")
    lines = [f"{kind} — DRAFT (assembled verbatim from the attempt log)", "",
             f"Court: {s.get('court', '—')}",
             f"Case: {s.get('case_number', '—')}",
             f"Defendant: {s.get('defendant', '—')}",
             f"Papers: {s.get('papers', '—')}", ""]
    for i, a in enumerate(atts, 1):
        who = (servers.get(a.get("server_id")) or {}).get("name", a.get("server_id"))
        line = (f"Attempt {i}: On {str(a['attempted_at'])[:16].replace('T', ' ')} "
                f"({a.get('band')}), at {a['address']}, server {who} attempted service. "
                f"Outcome: {a['outcome']}.")
        if a.get("who_answered"):
            line += f" Answered by: {a['who_answered']}."
        if a.get("gps_ref"):
            line += f" GPS ref {a['gps_ref']}."
        if a.get("late_recorded"):
            line += f" [LATE-RECORDED — {a.get('late_note')}]"
        lines.append(line)
    lines += ["", f"Recorded status: {s.get('status')}"
              + (f" — completed {str(s.get('completed_at'))[:10]}." if s.get("completed_at") else "."),
              "",
              "Every operative fact above is copied verbatim from the attempt log, recorded at "
              "the attempt. A fact that is not in the log cannot appear here.",
              "",
              "Signature: ____________________________",
              "The serving officer reviews, corrects the log with NEW entries if needed, and "
              "signs under oath. Software never signs and never attests."]
    return {"draft": "\n".join(lines), "assembled_from": [a["id"] for a in atts],
            "note": "a DRAFT for the server's review and oath — nothing here is signed"}


# ---------------------------------------------------------------- triage

DEADLINE_RISK = (
    r"\b(still (isn'?t|not)|hasn'?t been|has not been|not yet)\b.*\bserved\b",
    r"\b(dodg|evad|avoid|duck)\w*\b",
    r"\brunning out of time\b",
    r"\b(deadline|due date|court date|hearing|answer is due|response is due)\b.*"
    r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow|today|this week|"
    r"next week|\d+ days?)\b",
)
AFFIDAVIT_REQ = (
    r"\b(affidavit|proof of service|return of service)\b",
)
RUSH = (
    r"\b(rush|expedite|asap|same.?day|urgent)\b",
)
NEW_SERVE = (
    r"\bnew\b.*\b(summons|complaint|subpoena|papers|serve|garnishment|citation)\b",
    r"\b(summons|complaint|subpoena|papers|citation|garnishment)\b.*"
    r"\b(attached|enclosed|to follow|incoming|coming over)\b",
    r"\beffect service\b",
)
STATUS_ASK = (
    r"\b(any update|status|progress|where (are we|do we stand))\b",
    r"\bbeen served\b",
    r"\bserved yet\b",
)


def read_message(text):
    """deadline_risk | affidavit_request | rush_request | new_serve |
    status_ask | human. Deadline risk reads FIRST — a blown deadline collapses
    the case, and the law firm's evasion message is the alarm."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in DEADLINE_RISK:
        if re.search(rx, t):
            return {"label": "deadline_risk",
                    "why": "deadline risk / evasion — flagged to a human NOW; the reply cites "
                           "the attempt log and the recorded due-diligence rule, nothing "
                           "speculative"}
    for rx in AFFIDAVIT_REQ:
        if re.search(rx, t):
            return {"label": "affidavit_request",
                    "why": "an affidavit ask — drafts assemble verbatim from the attempt log, "
                           "and only a human signs"}
    for rx in RUSH:
        if re.search(rx, t):
            return {"label": "rush_request",
                    "why": "a rush ask — the board re-ranks by the court clock"}
    for rx in NEW_SERVE:
        if re.search(rx, t):
            return {"label": "new_serve",
                    "why": "papers in — the file opens and the deadline clock starts"}
    for rx in STATUS_ASK:
        if re.search(rx, t):
            return {"label": "status_ask",
                    "why": "a status ask — answered from the record: attempts and the next window"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- boards

def deadline_board(ref=None):
    """Open serves ranked by days-to-deadline — the court deadline is the
    master clock. A serve with no recorded deadline is named, never guessed
    into the ranking."""
    ref = ref or now()
    by_serve = {}
    for a in store.load("attempts"):
        by_serve.setdefault(a.get("serve_id"), []).append(a)
    rows = []
    for s in store.load("serves"):
        if s.get("status") not in ("papers_in", "attempting") or s.get("demo_tag"):
            continue
        atts = current_attempts(by_serve.get(s["id"], []))
        dd = due_diligence(s, atts)
        d = days_until(s.get("deadline"), ref)
        row = {"serve": s["id"], "defendant": s.get("defendant"), "county": s.get("county"),
               "firm": s.get("firm"), "fee": s.get("fee", 0), "days_to_deadline": d,
               "attempts": len(atts), "rush": bool(s.get("rush")),
               "assigned_to": s.get("assigned_to"),
               "diligence": (dd.get("rule") and
                             f"{dd['counted']['attempts']} att / "
                             f"{len(dd['counted']['bands'])} band(s) — "
                             f"{'met' if dd['met'] else 'not met'}") or "no rule recorded"}
        if d is None:
            row["_missing"] = "no recorded court deadline — an unset clock is named, not guessed"
        rows.append(row)
    rows.sort(key=lambda r: (r["days_to_deadline"] is None,
                             r["days_to_deadline"] if r["days_to_deadline"] is not None else 0,
                             not r["rush"]))
    return {"rows": rows, "rules_source": diligence_rules()["_source"]}


def day_list(server_id, ref=None):
    """A server's day: their open serves ordered by the court clock, not drive
    whim."""
    board = deadline_board(ref)
    return {"server": server_id,
            "rows": [r for r in board["rows"] if r.get("assigned_to") == server_id],
            "note": "ordered by days-to-deadline — the court clock drives the route"}


def recovered_this_week(ref=None):
    """Counted: serves completed, fees earned, deadline flags raised early,
    late-recorded attempts labeled (caught, not hidden)."""
    ref = ref or now()
    done = [s for s in store.load("serves")
            if s.get("completed_at") and s.get("status") in ("served", "substituted")
            and (ref - (parse(s["completed_at"]) or ref)).days <= 7]
    flags = sum(1 for e in store.events(kind="flag_deadline_risk")
                if (ref - (parse(e.get("at")) or ref)).days <= 7)
    late = sum(1 for a in store.load("attempts")
               if a.get("late_recorded")
               and (ref - (parse(a.get("recorded_at")) or ref)).days <= 7)
    return {"serves_completed": len(done),
            "fees_earned": round(sum(s.get("fee", 0) for s in done), 2),
            "deadline_flags_raised": flags, "late_records_labeled": late,
            "note": "counted from the serve ledger and the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="deadline_risk",
                   costly_note=("A BLOWN DEADLINE COLLAPSES THE CASE — and ends the law-firm "
                                "relationship that feeds the agency. Over-routing a status ask "
                                "costs a read."))

EVAL_CASES = [
    {"input": "the answer is due monday and he still isn't served", "label": "deadline_risk"},
    {"input": "defendant is dodging, hearing friday", "label": "deadline_risk"},
    {"input": "hearing is thursday and we are running out of time on the marsh serve",
     "label": "deadline_risk"},
    {"input": "he's evading service and the answer deadline is this week", "label": "deadline_risk"},
    {"input": "any update on the kessler serve", "label": "status_ask"},
    {"input": "what's the status of service on the delgado defendant", "label": "status_ask"},
    {"input": "has the records custodian been served yet", "label": "status_ask"},
    {"input": "new summons and complaint attached, please effect service", "label": "new_serve"},
    {"input": "subpoena for a witness, papers to follow this afternoon", "label": "new_serve"},
    {"input": "we need the affidavit of service for the friday filing", "label": "affidavit_request"},
    {"input": "please send the proof of service on the whitaker matter", "label": "affidavit_request"},
    {"input": "can you expedite this one, the client wants it served asap", "label": "rush_request"},
    {"input": "rush service on the garnishment, same-day if possible", "label": "rush_request"},
    {"input": "", "label": "human"},
    {"input": "question about last month's invoice", "label": "human"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":       {"rung": "R3", "reason": "routing only; the deadline-risk read comes first"},
    "sign_or_attest":     {"rung": "R0", "reason": "the affidavit is a human's oath — software assembles the draft, a server swears to it", "never_promote": True},
    "add_unrecorded_fact_to_affidavit": {"rung": "R0", "reason": "STRUCTURAL — drafts assemble only from the attempt log, verbatim; a fact outside the log has no way in", "never_promote": True},
    "declare_due_diligence_met": {"rung": "R0", "reason": "only the recorded jurisdiction rule evaluated against the log itself — a gap is named, never argued past", "never_promote": True},
    "flag_deadline_risk": {"rung": "R2", "reason": "the court deadline is the master clock — the human hears early; this cannot wait"},
    "log_serve":          {"rung": "R2", "reason": "papers in — the file opens and the deadline clock starts now"},
    "log_rush":           {"rung": "R2", "reason": "an internal re-rank by the court clock; nothing outward"},
    "propose_assignment": {"rung": "R1", "reason": "a server's day is a commitment — a human confirms the day list"},
    "draft_affidavit":    {"rung": "R1", "reason": "court paper — assembles verbatim from the log; a human reviews and signs"},
    "draft_status_reply": {"rung": "R1", "reason": "outward reply — the record does the talking; a human sends"},
    "draft_deadline_reply": {"rung": "R1", "reason": "outward reply on a deadline-risk matter — a human sends it, today"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Serve OS — what it computes to")
        .line("Throughput on the day list", "revenue",
              "completed serves/90d (counted) × your lift × your fee",
              ["serves_completed_90d", "throughput_lift", "serve_fee"],
              lambda g: float(g["serves_completed_90d"]) * float(g["throughput_lift"])
                        * float(g["serve_fee"]),
              note="completions are counted; the lift from deadline-ranked day lists is your call")
        .line("Rush serves captured", "revenue",
              "rush requests/90d (counted) × your capture × your premium",
              ["rush_requests_90d", "rush_capture", "rush_premium"],
              lambda g: float(g["rush_requests_90d"]) * float(g["rush_capture"])
                        * float(g["rush_premium"]),
              note="rush demand is counted from the ledger; capture and premium are yours")
        .line("Status-call hours returned", "time_saved", "hrs/wk × 52 × rate",
              ["status_hours_wk", "office_rate"],
              lambda g: float(g["status_hours_wk"]) * 52 * float(g["office_rate"]))
        .line("The quashed-service file", "scenario",
              "you decide what a service that survives a motion to quash is worth",
              ["quashed_value"], lambda g: float(g["quashed_value"]),
              assumption="never a saving — the collapsed case that didn't happen is not our number"))


def roi(given):
    ref = now()
    rec = {}
    rec["serves_completed_90d"] = sum(
        1 for s in store.load("serves")
        if s.get("completed_at") and s.get("status") in ("served", "substituted")
        and (ref - (parse(s["completed_at"]) or ref)).days <= 90)
    rec["rush_requests_90d"] = sum(
        1 for s in store.load("serves")
        if s.get("rush") and s.get("received_at")
        and (ref - (parse(s["received_at"]) or ref)).days <= 90)
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "log_serve", "propose_assignment", "draft_affidavit",
          "draft_status_reply", "draft_deadline_reply", "flag_deadline_risk")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("firm:",))
