#!/usr/bin/env python3
"""Post OS — domain core (security guard services).

Rules live here: incident-first triage with append-only verbatim narratives,
the credential gate (a post fills only with a matching recorded license set),
the coverage board, the credential calendar, and the matrix.

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

TABLES = ("config", "guards", "posts", "incidents", "reports", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="POSTOS_DATA_ROOT")

# ---------------------------------------------------------------- triage

INCIDENT = (
    r"\b(fight|assault|injur|ambulance|police|arrest|weapon|gun|knife|use of force|"
    r"altercation|theft|break-?in|trespass)\w*",
    r"\b(someone|guy|person)\b.*\b(down|hurt|bleeding|unconscious)\b",
)
CALLOUT = (
    r"\b(can'?t (make|come in)|calling (out|off)|sick tonight|no.?show|not going to make)\b",
    r"\b(miss(ing)? my shift|won'?t be (in|there))\b",
)
COVERAGE = (
    r"\b(need|add|extra)\b.*\b(guard|coverage|officer|post)\b",
    r"\b(cover|coverage)\b.*\b(tonight|weekend|event|this week)\b",
)
CREDENTIAL = (
    r"\b(license|cert|card|renewal|training|cpr|armed)\b.*\b(expir\w*|renew\w*|due|update|status|"
    r"current|valid|good)\b",
    r"\bwhen does my\b.*\b(license|cert|card)\b",
)


def read_message(text):
    """incident | callout | coverage_request | credential | human. Incident
    reads first — the narrative starts verbatim or not at all."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in INCIDENT:
        if re.search(rx, t):
            return {"label": "incident",
                    "why": "an incident — the guard's words go in verbatim and append-only; a "
                           "supervisor is briefed with logistics, and software edits nothing"}
    for rx in CALLOUT:
        if re.search(rx, t):
            return {"label": "callout",
                    "why": "a callout — the post goes open NOW and the coverage board proposes "
                           "qualified fills"}
    for rx in COVERAGE:
        if re.search(rx, t):
            return {"label": "coverage_request", "why": "coverage request — fills draft at R1"}
    for rx in CREDENTIAL:
        if re.search(rx, t):
            return {"label": "credential", "why": "credential question — answered from the calendar"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- verbatim narratives

def record_incident(post_id, guard_id, narrative):
    """The ONLY way an incident narrative enters: verbatim, append-only."""
    inc = {"id": store.nid("inc"), "post_id": post_id, "guard_id": guard_id,
           "narrative": narrative, "at": iso(), "supersedes": None}
    store.upsert("incidents", inc)
    store.log_event("incident_recorded", inc["id"], f"human:{guard_id}", "R1",
                    {"post": post_id})
    return inc


def correct_incident(incident_id, new_narrative, guard_id):
    """A correction is a NEW entry from the SAME guard pointing at the old one.
    Both stay. There is no edit and no delete in this module."""
    old = store.by_id("incidents", incident_id)
    if not old:
        return {"error": "no such incident"}
    if guard_id != old.get("guard_id"):
        return {"refused": ("only the reporting guard corrects their own narrative — anyone "
                            "else's version is a separate statement, not a correction")}
    inc = {"id": store.nid("inc"), "post_id": old["post_id"], "guard_id": guard_id,
           "narrative": new_narrative, "at": iso(), "supersedes": incident_id}
    store.upsert("incidents", inc)
    store.log_event("incident_corrected", inc["id"], f"human:{guard_id}", "R1",
                    {"supersedes": incident_id, "note": "both versions remain"})
    return inc


def adjust_request(incident_id, requester, request_text):
    """A client's request to adjust a narrative is refused and logged verbatim."""
    ev = store.log_event("refused", incident_id, "agent:desk", "R0",
                        {"action": "edit_incident_narrative",
                         "requester": requester, "verbatim": request_text,
                         "why": "narratives are append-only; the request itself is now part of "
                                "the record"})
    return {"refused": ("the narrative stands as the guard wrote it — and this request is now "
                        "part of the record"), "event": ev["id"]}


# ---------------------------------------------------------------- the credential gate

def can_fill(post, guard, ref=None):
    """A post fills only with a guard whose recorded, unexpired credential set
    matches the post's requirements."""
    ref = ref or now()
    need = set(post.get("required_creds") or [])
    creds = guard.get("credentials") or {}
    missing, expired = [], []
    for c in need:
        exp = parse(creds.get(c))
        if not creds.get(c):
            missing.append(c)
        elif exp and exp < ref:
            expired.append(c)
    if missing or expired:
        parts = []
        if missing:
            parts.append(f"missing: {', '.join(sorted(missing))}")
        if expired:
            parts.append(f"expired: {', '.join(sorted(expired))}")
        return False, (f"cannot fill this post with {guard.get('name', guard.get('id'))} — "
                       f"{'; '.join(parts)}. An unlicensed guard on post is the liability the "
                       f"client is paying to avoid.")
    return True, f"credential set matches: {', '.join(sorted(need)) or 'no special requirements'}"


def coverage_board(ref=None):
    """Open posts tonight + qualified candidates per post."""
    ref = ref or now()
    guards = [g for g in store.load("guards") if g.get("status") == "active"]
    rows = []
    for p in store.load("posts"):
        if p.get("filled_by") or p.get("demo_tag"):
            continue
        candidates = []
        for g in guards:
            okf, why = can_fill(p, g, ref)
            if okf:
                candidates.append({"guard": g["id"], "name": g.get("name")})
        rows.append({"post": p["id"], "site": p.get("site"), "when": p.get("when"),
                     "required": p.get("required_creds") or [],
                     "candidates": candidates[:5],
                     "note": "only credential-matched guards appear — the gate built the list"})
    return rows


def credential_calendar(ref=None, horizon_days=45):
    ref = ref or now()
    rows = []
    for g in store.load("guards"):
        if g.get("status") != "active":
            continue
        for cred, exp in (g.get("credentials") or {}).items():
            d = parse(exp)
            if d and (d - ref).days <= horizon_days:
                rows.append({"guard": g.get("name"), "guard_id": g["id"], "cred": cred,
                             "expires": exp, "days": (d - ref).days,
                             "label": "DATE ALERT — an expired card drops the guard from fill lists by construction"})
    rows.sort(key=lambda r: r["days"])
    return rows


def recovered_this_week(ref=None):
    """Counted: posts filled, incidents recorded, credential lapses caught."""
    ref = ref or now()
    filled = sum(1 for e in store.events(kind="fill_post")
                 if str(e.get("actor", "")).startswith("human:")
                 and (ref - (parse(e.get("at")) or ref)).days <= 7)
    incidents = [i for i in store.load("incidents")
                 if (ref - (parse(i.get("at")) or ref)).days <= 7]
    alerts = sum(1 for e in store.events(kind="credential_alert")
                 if (ref - (parse(e.get("at")) or ref)).days <= 7)
    return {"posts_filled": filled, "incidents_recorded": len(incidents),
            "credential_alerts": alerts,
            "note": "counted from the event log and the incident register — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="incident",
                   costly_note=("AN INCIDENT HANDLED CASUALLY IS A DEPOSITION EXHIBIT — and a "
                                "narrative touched by software is a career-ending one. "
                                "Over-routing costs a read."))

EVAL_CASES = [
    {"input": "two guys got into a fight at the loading dock, police came", "label": "incident"},
    {"input": "someone is down in the parking structure, calling the ambulance", "label": "incident"},
    {"input": "caught a trespasser in the east stairwell", "label": "incident"},
    {"input": "there was an altercation at the front desk, no injuries", "label": "incident"},
    {"input": "I can't make my shift tonight, kid is sick", "label": "callout"},
    {"input": "calling out for the weekend, doctor's orders", "label": "callout"},
    {"input": "we need an extra guard for the event saturday", "label": "coverage_request"},
    {"input": "can you cover the warehouse this week, our guy quit", "label": "coverage_request"},
    {"input": "when does my armed card expire", "label": "credential"},
    {"input": "is my cpr cert still current", "label": "credential"},
    {"input": "", "label": "human"},
    {"input": "paycheck question, who do I talk to", "label": "human"},
    {"input": "guard reported a weapon spotted in a backpack at gate 3", "label": "incident"},
    {"input": "no-show at the courthouse post this morning", "label": "callout"},
    {"input": "my guard card renewal is due, what do I need", "label": "credential"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":       {"rung": "R3", "reason": "routing only; incident-first is the point"},
    "brief_supervisor":   {"rung": "R2", "reason": "the logistics brief cannot wait — words stay the guard's"},
    "edit_incident_narrative": {"rung": "R0", "reason": "narratives are append-only — the adjust request becomes part of the record", "never_promote": True},
    "fill_post_unqualified": {"rung": "R0", "reason": "an unlicensed guard on post is the liability the client pays to avoid", "never_promote": True},
    "advise_use_of_force": {"rung": "R0", "reason": "policy questions go to a human supervisor", "never_promote": True},
    "fill_post":          {"rung": "R1", "reason": "an assignment is a promise to the client — a human fills, past the gate"},
    "draft_coverage_reply": {"rung": "R1", "reason": "outward reply — a human sends"},
    "credential_alert":   {"rung": "R2", "reason": "an internal date alert; expiry drops the guard from lists by construction"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Post OS — what it computes to")
        .line("Open posts filled before the client notices", "revenue", "open posts/mo × avg shift bill",
              ["open_posts_mo", "avg_shift_bill"],
              lambda g: float(g["open_posts_mo"]) * 12 * float(g["avg_shift_bill"]))
        .line("Scheduling hours", "time_saved", "hrs/wk × 52 × rate",
              ["office_hours_wk", "office_rate"],
              lambda g: float(g["office_hours_wk"]) * 52 * float(g["office_rate"]))
        .line("The unedited-incident file", "scenario", "you decide what a clean deposition is worth",
              ["incident_value"], lambda g: float(g["incident_value"]),
              assumption="never a saving — append-only narratives are the product")
        .line("Credential lapses caught before post", "scenario", "lapses × your exposure per lapse",
              ["lapses_caught", "exposure_per_lapse"],
              lambda g: float(g["lapses_caught"]) * float(g["exposure_per_lapse"]),
              assumption="an exposure you weigh"))


def roi(given):
    rec = {}
    rec["lapses_caught"] = len(credential_calendar())
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "brief_supervisor", "fill_post", "draft_coverage_reply",
          "credential_alert")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("client:",))
