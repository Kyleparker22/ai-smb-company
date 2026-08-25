#!/usr/bin/env python3
"""Queue OS — domain core (managed service provider).

Rules live here: ticket triage with its security bias, SLA clocks computed
from the agreement tier, the scope engine that cites clauses and refuses to
bill off silence, and the autonomy matrix.

The thesis: an MSP's worst day is a security signal that waited behind printer
tickets, and its quietest leak is agreement-scope work done free. Triage with
a bias, count the clocks, cite the clause or say "ambiguous".

Stdlib only. Honesty rules come from `_kit`.
"""
import re, sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, hours_between, iso, # noqa: E402
                        median, now, parse, unmeasured)

TABLES = ("config", "clients", "tickets", "scope_findings", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="QUEUEOS_DATA_ROOT")


# ---------------------------------------------------------------- triage

# Security signals. The bias: a false escalation costs an engineer five
# minutes; a missed one costs an incident report with the MSP's name on it.
SECURITY = (
    ("phishing", r"\bphish|suspicious (email|link)|clicked (a|the) link|weird email asking\b|"
                 r"\bgift ?cards?\b|\b(email|message|text)\b.*\b(seems|looks) (suspicious|off|phishy)\b"),
    ("ransomware", r"\bransom|files? (are )?encrypted|\.locked\b|can'?t open any(thing| files)|"
                   r"all (my|our) files (changed|renamed)\b"),
    ("account_compromise", r"\bimpossible travel|sign-?in from (russia|china|nigeria|unknown)|"
                           r"logged in from|didn'?t (log|sign) ?in|password (was )?changed (itself|without)\b"),
    ("mfa_bombing", r"\bmfa (requests?|prompts?)\b.*\b(keep|flood|repeated|won'?t stop)|"
                    r"approve requests? I didn'?t\b"),
    ("data_exfil", r"\blarge (download|transfer)|mass (delete|download)|files? (leaving|uploaded to)\b"),
)
OUTAGE = (
    r"\b(server|network|internet|email|site|system)\b.*\b(down|offline|unreachable)\b",
    r"\bnobody can (log ?in|work|connect)\b|\bwhole office\b.*\b(out|down)\b",
)
ROUTINE = (
    r"\bpassword reset\b|\bforgot (my )?password\b",
    r"\bprinter|toner|scan(ner|ning)\b",
    r"\bnew (user|hire|employee|laptop)\b|\bonboard\b",
    r"\bmonitor|docking station|mouse|keyboard\b",
    r"\binstall (office|zoom|teams|software)\b",
)


def triage(text):
    """security | outage | routine | human. Empty is human. Security signals
    carry their kind and can never be closed by software afterwards."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty ticket — a person reads it"}
    for kind, rx in SECURITY:
        if re.search(rx, t):
            return {"label": "security", "kind": kind,
                    "why": f"typed security signal: {kind} — a human security escalation, now"}
    for rx in OUTAGE:
        if re.search(rx, t):
            return {"label": "outage", "why": "multiple users or core service affected"}
    for rx in ROUTINE:
        if re.search(rx, t):
            return {"label": "routine", "why": "known routine pattern — draft response queued"}
    return {"label": "human", "why": "no clean signal — a dispatcher reads it"}


def can_close(ticket, actor_is_human):
    """THE refusal: a security ticket is closed by a human security engineer
    or not at all."""
    if ticket.get("label") == "security" and not actor_is_human:
        return False, ("a security signal is never closed or downgraded by software — a human "
                       "security engineer closes it after investigation")
    return True, "ok"


# ---------------------------------------------------------------- sla

TIERS = {"gold": {"respond_h": 1, "resolve_h": 8},
         "silver": {"respond_h": 4, "resolve_h": 24},
         "bronze": {"respond_h": 8, "resolve_h": 72}}


def sla_state(ticket, ref=None):
    """Clock state for one ticket, computed from the agreement tier. No tier on
    the agreement → the clock is unknowable, and that is said, not defaulted."""
    ref = ref or now()
    client = store.by_id("clients", ticket.get("client_id")) or {}
    tier = client.get("tier")
    if tier not in TIERS:
        return unmeasured(f"agreement for {client.get('name','unknown client')!r} has no SLA tier "
                          f"on file — the clock is unknowable, not defaulted", field="state")
    rules = TIERS[tier]
    opened = parse(ticket.get("opened_at"))
    if not opened:
        return unmeasured("no opened_at on the ticket", field="state")
    out = {"tier": tier}
    if ticket.get("first_response_at"):
        rh = hours_between(ticket["opened_at"], ticket["first_response_at"])
        out["response"] = {"hours": rh, "breached": rh is not None and rh > rules["respond_h"]}
    else:
        left = rules["respond_h"] - (ref - opened).total_seconds() / 3600
        out["response"] = {"hours_left": round(left, 2), "breached": left < 0}
    if ticket.get("resolved_at"):
        vh = hours_between(ticket["opened_at"], ticket["resolved_at"])
        out["resolution"] = {"hours": vh, "breached": vh is not None and vh > rules["resolve_h"]}
    else:
        left = rules["resolve_h"] - (ref - opened).total_seconds() / 3600
        out["resolution"] = {"hours_left": round(left, 2), "breached": left < 0}
    out["state"] = ("breached" if out["response"]["breached"] or out["resolution"]["breached"]
                    else "at_risk" if (out["resolution"].get("hours_left") or 99) < rules["resolve_h"] * 0.25
                    else "inside")
    return out


def sla_board(ref=None):
    rows, unknowable = [], []
    for t in store.load("tickets"):
        if t.get("resolved_at") or t.get("demo_tag"):
            continue
        s = sla_state(t, ref)
        if "_missing" in s:
            unknowable.append({"ticket": t["id"], "why": s["_missing"]})
            continue
        rows.append({"ticket": t["id"], "summary": (t.get("text") or "")[:70],
                     "label": t.get("label"), "tier": s["tier"], "state": s["state"],
                     "resolve_left_h": s["resolution"].get("hours_left")})
    order = {"breached": 0, "at_risk": 1, "inside": 2}
    rows.sort(key=lambda r: (order.get(r["state"], 3), r.get("resolve_left_h") or 0))
    return {"rows": rows, "unknowable": unknowable,
            "breached": sum(1 for r in rows if r["state"] == "breached")}


# ---------------------------------------------------------------- scope

CATEGORY_PATTERNS = (
    ("backup", r"\bbackup|restore|recovery\b"),
    ("patching", r"\bpatch|update (windows|server)|security updates?\b"),
    ("helpdesk", r"\bpassword|printer|monitor|software install|new (user|laptop)|email\b"),
    ("network", r"\bswitch|firewall|wifi|vpn|network\b"),
    ("project", r"\b(new office|cabling|migration|deploy(ment)? of|roll ?out|move (to|office))\b"),
    ("security_service", r"\bphish|ransom|mfa|breach|compromise\b"),
)


def categorize(text):
    t = (text or "").lower()
    for cat, rx in CATEGORY_PATTERNS:
        if re.search(rx, t):
            return cat
    return None


def scope_check(ticket):
    """in_scope (clause cited) | out_of_scope (exclusion cited, billable draft)
    | ambiguous (a human decides). Silence in the agreement is NEVER billable —
    asserting money off a clause that does not exist is how MSPs lose clients."""
    client = store.by_id("clients", ticket.get("client_id")) or {}
    agreement = client.get("agreement") or {}
    cat = categorize(ticket.get("text", ""))
    if not cat:
        return {"verdict": "ambiguous", "why": "no category matched — a human reads the ticket",
                "category": None}
    for cl in agreement.get("includes", []):
        if cat in cl.get("covers", []):
            return {"verdict": "in_scope", "category": cat,
                    "clause": cl["id"], "clause_text": cl["text"],
                    "why": f"covered by clause {cl['id']}"}
    for cl in agreement.get("excludes", []):
        if cat in cl.get("covers", []):
            return {"verdict": "out_of_scope", "category": cat,
                    "clause": cl["id"], "clause_text": cl["text"],
                    "why": f"excluded by clause {cl['id']} — billable draft, a human bills"}
    return {"verdict": "ambiguous", "category": cat,
            "why": f"the agreement neither includes nor excludes {cat!r} — a human decides; "
                   f"the system never asserts billable off silence"}


def recovered_this_week(ref=None):
    """Counted from the log: routine replies a human sent, billable drafts a
    human approved, and security escalations raised inside 7 days."""
    ref = ref or now()
    replies = billables = escalations = 0
    for e in store.events():
        at = parse(e.get("at"))
        if not at or (ref - at).days > 7:
            continue
        human = str(e.get("actor", "")).startswith("human:")
        if e["kind"] == "draft_routine_reply" and human:
            replies += 1
        elif e["kind"] == "draft_billable" and human:
            billables += 1
        elif e["kind"] == "escalate_security":
            escalations += 1
    return {"replies_sent": replies, "billables_approved": billables,
            "security_escalations": escalations,
            "note": "counted from the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("ticket triage",
                   costly_label="security",
                   costly_note=("A SECURITY SIGNAL TRIAGED AS ROUTINE IS A BREACH WITH YOUR NAME "
                                "ON THE INCIDENT REPORT. A false escalation costs five minutes."))

EVAL_CASES = [
    {"input": "got a weird email asking me to approve a payment, I clicked the link", "label": "security"},
    {"input": "all our files changed to .locked and there's a note", "label": "security"},
    {"input": "MFA prompts keep flooding my phone, approve requests I didn't make", "label": "security"},
    {"input": "sign-in from Russia on the CFO account last night", "label": "security"},
    {"input": "email is down for the whole office", "label": "outage"},
    {"input": "server unreachable since 8am, nobody can work", "label": "outage"},
    {"input": "forgot my password again, sorry", "label": "routine"},
    {"input": "printer on 3rd floor jamming", "label": "routine"},
    {"input": "new hire starts monday, needs laptop and accounts", "label": "routine"},
    {"input": "install zoom on the conference room pc", "label": "routine"},
    {"input": "", "label": "human"},
    {"input": "hey can someone call me about the thing from yesterday", "label": "human"},
    {"input": "accounting says a large transfer of files left the shared drive overnight", "label": "security"},
    {"input": "my password was changed without me doing anything", "label": "security"},
    {"input": "whole office is down, nobody can connect since the storm", "label": "outage"},
    {"input": "need a docking station for the new desk", "label": "routine"},
    {"input": "toner low on the copier again", "label": "routine"},
    {"input": "got an email from the ceo asking for gift cards, seems suspicious", "label": "security"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: triage(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "triage_ticket":     {"rung": "R3", "reason": "routing with a security bias; the queue is visible"},
    "escalate_security": {"rung": "R2", "reason": "act now, tell the human — waiting defeats the escalation"},
    "draft_routine_reply": {"rung": "R1", "reason": "outward reply — a human sends"},
    "close_security_ticket": {"rung": "R0", "reason": "a human security engineer closes a security ticket after investigation", "never_promote": True},
    "downgrade_security": {"rung": "R0", "reason": "software never decides a security signal was nothing", "never_promote": True},
    "auto_remediate_production": {"rung": "R0", "reason": "the system drafts runbook steps; hands touch production", "never_promote": True},
    "send_credentials":  {"rung": "R0", "reason": "credentials never travel in a ticket reply", "never_promote": True},
    "draft_billable":    {"rung": "R1", "reason": "money — and structurally requires a cited exclusion clause"},
    "bill_client":       {"rung": "R1", "reason": "an invoice is a relationship event — a human sends it", "never_promote": True},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Queue OS — what it computes to")
        .line("Out-of-scope work captured", "revenue", "cited out-of-scope findings × avg billable",
              ["oos_findings", "avg_billable"],
              lambda g: float(g["oos_findings"]) * float(g["avg_billable"]),
              note="findings are counted with their clause; the rate is your rate card")
        .line("Triage and dispatch time", "time_saved", "tickets/wk × min saved × 52 × rate/60",
              ["tickets_wk", "min_saved", "dispatcher_rate"],
              lambda g: float(g["tickets_wk"]) * float(g["min_saved"]) * 52 * float(g["dispatcher_rate"]) / 60)
        .line("SLA credits avoided", "scenario", "breaches × your credit exposure",
              ["breaches_90d", "credit_per_breach"],
              lambda g: float(g["breaches_90d"]) * float(g["credit_per_breach"]),
              assumption="an exposure you weigh — avoided breaches cannot be counted")
        .line("Security response exposure", "scenario", "you decide what an hour of head start is worth",
              ["security_value"], lambda g: float(g["security_value"]),
              assumption="never monetized by us — this line is yours or blank"))


def roi(given):
    rec = {}
    oos = [f for f in store.load("scope_findings") if f.get("verdict") == "out_of_scope"]
    rec["oos_findings"] = len(oos)
    board = sla_board()
    rec["breaches_90d"] = board["breached"]
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("triage_ticket", "escalate_security", "draft_routine_reply", "draft_billable")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("enduser:",))
