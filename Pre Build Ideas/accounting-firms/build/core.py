#!/usr/bin/env python3
"""Close OS — domain core (CPA · bookkeeping · tax firms).

Everything that is a *rule* lives here: the engagement and open-item model,
deadline calendars, dependency logic, the chase cadence and its escalation, the
document taxonomy and matching rules, engagement-letter scope evaluation, the
ROI model and the autonomy matrix.

The product thesis: a firm's throughput is not limited by how fast it works. It
is limited by THE CHASE — the statement nobody uploaded, the K-1 that's coming
"next week", the eleven open items nineteen days old. The second half is the
money half: out-of-scope work, caught as it arrives instead of discovered at
write-off.

Two prohibitions are rules here, not prompt text:
  1. No tax position, no accounting judgment, no advice. A question touching
     treatment, deductibility, entity choice or a filing position is routed to a
     CPA UNANSWERED.
  2. No document is ever deleted. A misfile is corrected by a NEW event and both
     states stay in the log.

An engagement may not sit in a vague "in progress": it must name its current
blocker. `advance()` refuses to write a state without one.

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

TABLES = ("config", "clients", "staff", "engagements", "open_items", "documents",
          "scope_events", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="CLOSEOS_DATA_ROOT")


# ---------------------------------------------------------------- engagements

ENGAGEMENT_TYPES = {
    "monthly_close": dict(label="Monthly close", cadence="monthly", due_day=20, fee=850),
    "1040":          dict(label="Individual return", cadence="annual", season=True, fee=1400),
    "1120s":         dict(label="S-corp return", cadence="annual", season=True, fee=2600),
    "1065":          dict(label="Partnership return", cadence="annual", season=True, fee=2900),
    "audit_prep":    dict(label="Audit preparation", cadence="annual", fee=7500),
    "payroll":       dict(label="Payroll", cadence="monthly", due_day=5, fee=320),
}

# Open-item types, and — the part that matters — what each one DEPENDS on. A
# chase for something that cannot be produced yet is worse than no chase: it
# teaches the client to ignore us.
ITEM_TYPES = {
    "bank_statement":   dict(label="Bank statement", party="client", depends_on=None),
    "cc_statement":     dict(label="Credit card statement", party="client", depends_on=None),
    "loan_statement":   dict(label="Loan statement", party="client", depends_on=None),
    "payroll_report":   dict(label="Payroll report", party="client", depends_on=None),
    "k1":               dict(label="K-1", party="third_party", depends_on=None),
    "1099":             dict(label="1099", party="third_party", depends_on=None),
    "w2":               dict(label="W-2", party="third_party", depends_on=None),
    "receipts":         dict(label="Receipts / substantiation", party="client", depends_on=None),
    "mileage_log":      dict(label="Mileage log", party="client", depends_on=None),
    "question_answer":  dict(label="Answer to our question", party="client", depends_on=None),
    "signed_8879":      dict(label="Signed e-file authorization", party="client", depends_on="draft_return"),
    "draft_return":     dict(label="Draft return", party="firm", depends_on="all_client_items"),
    "trial_balance":    dict(label="Trial balance", party="firm", depends_on="bank_statement"),
}

STATES = ("not_started", "waiting_on_client", "waiting_on_third_party", "waiting_on_us",
          "in_review", "complete")
# The state that does NOT exist: "in progress". Every live state names who is blocking.
BLOCKING_STATES = {"waiting_on_client": "client", "waiting_on_third_party": "third_party",
                   "waiting_on_us": "firm", "in_review": "firm"}


def advance(engagement, state, blocker=None, actor="agent:close"):
    """An engagement cannot move to a live state without naming its blocker.

    This is a structural refusal, not a validation warning: the partner board's
    entire value is that every row answers "who is holding this up", and a
    single unnamed blocker makes the board a to-do list again.
    """
    if state not in STATES:
        raise ValueError(f"unknown engagement state: {state}")
    if state in BLOCKING_STATES and not blocker:
        raise ValueError(
            f"state '{state}' requires a named blocker — an engagement may not sit in a vague "
            f"'in progress'")
    engagement["state"] = state
    engagement["blocker"] = blocker
    engagement["blocker_since"] = engagement.get("blocker_since") or iso() if blocker else None
    if not blocker:
        engagement["blocker_since"] = None
    return engagement


def blocker_age_days(engagement, ref=None):
    if not engagement.get("blocker_since"):
        return None
    return -(days_until(engagement["blocker_since"], ref) or 0)


# ---------------------------------------------------------------- the chase
#
# Per-client cadence and channel. The two rules that make it not-spam: never
# chase something already received, and never chase a dependent item whose
# dependency is not met.

LADDER = [
    dict(day=0, channel="portal", kind="request", note="the list, itemised, with a link"),
    dict(day=3, channel="email", kind="nudge", note="only what is STILL outstanding"),
    dict(day=7, channel="sms", kind="short", note="one line, one link"),
    dict(day=12, channel="email", kind="deadline", note="names the actual deadline and what slips"),
    dict(day=18, channel="partner_task", kind="escalate", note="a partner calls — the ladder ends here"),
]


def deps_met(item, engagement_items):
    dep = ITEM_TYPES.get(item["type"], {}).get("depends_on")
    if not dep:
        return True, None
    if dep == "all_client_items":
        outstanding = [i for i in engagement_items
                       if ITEM_TYPES.get(i["type"], {}).get("party") == "client"
                       and i.get("state") != "received"]
        return (not outstanding,
                None if not outstanding else f"{len(outstanding)} client items still outstanding")
    got = [i for i in engagement_items if i["type"] == dep and i.get("state") == "received"]
    return (bool(got), None if got else f"waiting on {ITEM_TYPES.get(dep, {}).get('label', dep)}")


def due_chase(item, engagement_items, ref=None):
    """Which ladder steps are due for this item, and why not, when not."""
    if item.get("state") == "received":
        return [], "already received — never chased again"
    ok, why = deps_met(item, engagement_items)
    if not ok:
        return [], f"not chaseable yet: {why}"
    age = -(days_until(item.get("requested_at"), ref) or 0)
    sent = {t.get("day") for t in item.get("touches", [])}
    due = [t for t in LADDER if t["day"] <= age and t["day"] not in sent]
    return due, None


# ---------------------------------------------------------------- document intake
#
# Type / entity / period, then match to the open request. A mismatch is FLAGGED,
# never silently accepted — a document filed to the wrong entity is worse than
# one not filed at all, which is why the false-match rate is measured alone.

DOC_PATTERNS = [
    (r"bank|checking|savings|stmt.*(chk|sav)", "bank_statement"),
    (r"visa|mastercard|amex|credit ?card|cc[_ -]?stmt", "cc_statement"),
    (r"loan|note payable|mortgage", "loan_statement"),
    (r"payroll|gusto|adp|paychex|941|w-?3", "payroll_report"),
    (r"k-?1", "k1"),
    (r"1099", "1099"),
    (r"w-?2", "w2"),
    (r"receipt|invoice|substantiat", "receipts"),
    (r"mileage|odometer", "mileage_log"),
    (r"8879|e-?file auth", "signed_8879"),
]
_DOC = [(re.compile(p, re.I), t) for p, t in DOC_PATTERNS]
_YEAR = re.compile(r"20\d{2}")
_MONTH = re.compile(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b", re.I)
MONTHS = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}


def read_document(doc):
    """Filename + metadata → {type, year, month, entity_hint, confidence}.

    Confidence is emitted per document. Anything ambiguous goes to a human queue
    rather than into a client's folder.
    """
    name = (doc.get("filename") or "")
    hits = [t for rx, t in _DOC if rx.search(name)]
    y = _YEAR.search(name)
    m = _MONTH.search(name)
    conf = 0.0
    if hits:
        conf += 0.6
    if y:
        conf += 0.2
    if m:
        conf += 0.1
    if doc.get("entity_hint"):
        conf += 0.1
    return {"type": hits[0] if hits else None,
            "year": int(y.group(0)) if y else None,
            "month": MONTHS.get(m.group(0)[:3].lower()) if m else None,
            "entity_hint": doc.get("entity_hint"),
            "confidence": round(min(conf, 1.0), 2),
            "why": ("nothing in the filename identified a document type" if not hits else
                    f"filename matched {hits[0]}")}


MATCH_THRESHOLD = 0.7


def match_document(doc, open_items, engagement, ref=None):
    """Match to an open request, or refuse with a named reason."""
    r = read_document(doc)
    if r["confidence"] < MATCH_THRESHOLD or not r["type"]:
        return {"matched": None, "read": r, "action": "human_queue",
                "why": f"confidence {r['confidence']} below {MATCH_THRESHOLD} — {r['why']}"}
    candidates = [i for i in open_items if i["type"] == r["type"] and i.get("state") != "received"]
    if not candidates:
        return {"matched": None, "read": r, "action": "flag",
                "why": f"a {r['type']} arrived but no open request for one — do not file it blindly"}
    want_year = engagement.get("period_year")
    if want_year and r["year"] and r["year"] != want_year:
        return {"matched": None, "read": r, "action": "flag",
                "why": f"this is a {r['year']} document and the engagement is {want_year} — "
                       f"wrong period, flagged rather than filed"}
    if want_year and not r["year"]:
        return {"matched": None, "read": r, "action": "human_queue",
                "why": "no period in the filename and the engagement is period-specific"}
    if engagement.get("entity") and r["entity_hint"] and r["entity_hint"] != engagement["entity"]:
        return {"matched": None, "read": r, "action": "flag",
                "why": f"entity hint '{r['entity_hint']}' does not match the engagement entity "
                       f"'{engagement['entity']}' — filing to the wrong entity is the expensive error"}
    want_month = None
    for i in candidates:
        want_month = i.get("period_month")
        if want_month and r["month"] and want_month == r["month"]:
            return {"matched": i["id"], "read": r, "action": "file", "why": "type and period match"}
    if want_month and not r["month"]:
        return {"matched": None, "read": r, "action": "human_queue",
                "why": "the request is for a specific month and the filename has none"}
    return {"matched": candidates[0]["id"], "read": r, "action": "file",
            "why": "type matches an open request with no period constraint"}


# ---------------------------------------------------------------- scope
#
# The revenue half. Out-of-scope work is detected against the engagement
# LETTER'S OWN LANGUAGE, and a scope event cannot be logged without citing it.

SCOPE_TRIGGERS = [
    (r"new (entity|llc|corp|company|business)|just (formed|set up|started)", "new entity"),
    (r"(new|another) state|nexus|register(ed)? in", "new state registration"),
    (r"amend(ed)?|prior year|restate|go back and fix", "prior-year amendment"),
    (r"(should i|can i|what if).*(elect|convert|s-?corp|deduct|write off)", "advisory question"),
    (r"quickbooks (cleanup|catch ?up)|books are a mess|behind on the books", "bookkeeping cleanup"),
    (r"(audit|notice|letter) from the (irs|state|department)", "notice response"),
    (r"payroll (in|for) (another|a new)", "multi-state payroll"),
    (r"sold (the|a) (building|property|business)|1031", "transaction work"),
]
_SCOPE = [(re.compile(p, re.I), lbl) for p, lbl in SCOPE_TRIGGERS]


def detect_scope(text, letter):
    """Returns [] or a list of events, each carrying the letter clause it falls
    outside. No citation, no event — that is enforced in `log_scope_event`."""
    out = []
    for rx, label in _SCOPE:
        m = rx.search(text or "")
        if not m:
            continue
        clause = _clause_for(label, letter)
        covers = (clause or {}).get("covers")
        out.append({"label": label, "matched": m.group(0).strip(),
                    "letter_clause": clause,
                    "in_scope": covers is True,
                    "ambiguous": covers == "ambiguous",
                    "citation": (clause or {}).get("text")})
    return out


def _clause_for(label, letter):
    for c in (letter or {}).get("clauses", []):
        if label in c.get("applies_to", []):
            return c
    return None


def log_scope_event(engagement, detected, evidence):
    """A scope event cannot exist without a citation to the engagement letter.

    Three ways this refuses, and the third is the one that matters: a clause can
    speak BOTH ways ("routine questions are included; advisory engagements are
    separate"), and a keyword match cannot tell which side a given question lands
    on. Asserting scope creep off an ambiguous clause is the system overstepping,
    so it surfaces the ambiguity for a partner instead of resolving it.
    """
    if not detected.get("citation"):
        return {"logged": False, "verdict": "no_clause",
                "why": "no clause in the engagement letter speaks to this — a partner decides "
                       "whether it is out of scope before it becomes a billing conversation"}
    if detected.get("ambiguous"):
        return {"logged": False, "verdict": "ambiguous",
                "why": f"the letter speaks both ways here — “{detected['citation']}” — so a "
                       f"partner reads it, not us"}
    if detected.get("in_scope"):
        return {"logged": False, "verdict": "in_scope",
                "why": f"the letter covers this: “{detected['citation']}”"}
    row = {"id": store.nid("sc"), "engagement_id": engagement["id"],
           "client_id": engagement["client_id"], "label": detected["label"],
           "matched": detected["matched"], "citation": detected["citation"],
           "evidence": evidence, "at": iso(), "decision": None}
    store.upsert("scope_events", row)
    return {"logged": True, "id": row["id"]}


# ---------------------------------------------------------------- autonomy

MATRIX = Matrix({
    "request_items":     dict(rung="R2", reason="sending the itemised list of what we need is the engagement doing what the client signed up for"),
    "chase_nudge":       dict(rung="R2", reason="a reminder listing only what is STILL outstanding, on a cadence the client agreed to"),
    "chase_escalate":    dict(rung="R1", reason="the last rung is a partner's call, not a fifth email"),
    "file_document":     dict(rung="R2", reason="filing a confidently-matched document to the right engagement is reversible and logged"),
    "flag_mismatch":     dict(rung="R3", reason="raising a hand about a wrong-year or wrong-entity document is always the safe direction"),
    "answer_tax_question": dict(rung="R0", reason="THE SYSTEM NEVER DOES THIS. No tax position, no treatment, no deductibility, no entity choice — routed to a CPA unanswered", never_promote=True),
    "log_scope_event":   dict(rung="R2", reason="recording that something arrived which the letter does not cover; the partner still decides bill-or-forgive"),
    "propose_billing":   dict(rung="R1", reason="asking a client for more money is a partner's conversation", never_promote=True),
    "delete_document":   dict(rung="R0", reason="THE SYSTEM NEVER DOES THIS. Nothing is deleted; a misfile is corrected by a new event and both states stay in the log", never_promote=True),
    "message_custom":    dict(rung="R1", reason="free text to a client can become advice"),
})
gate = Gate(store, MATRIX)

MOVING_KINDS = {"request_items", "chase_nudge", "chase_escalate", "chase_sent",
                "file_document", "flag_mismatch", "log_scope_event", "propose_billing",
                "message_custom"}


def automation(days=90):
    return automation_rate(store.load("events"), MOVING_KINDS, days, exclude_actors=("client:",))


# ---------------------------------------------------------------- eval

DOC_EVAL = Eval(
    "document matching", "flag",
    "a document filed to the wrong entity or the wrong year is worse than one not filed at all — "
    "the false-match rate is what this measures, and it is reported alone")


def eval_documents():
    eng = {"id": "e", "period_year": 2025, "entity": "YourCo LLC"}
    items = [{"id": "i1", "type": "bank_statement", "state": "open", "period_month": 3},
             {"id": "i2", "type": "k1", "state": "open"}]
    cases = [
        ({"filename": "YourCo 2025 Mar bank stmt.pdf"}, "file"),
        ({"filename": "K-1 2025.pdf"}, "file"),
        ({"filename": "bank statement 2024 march.pdf"}, "flag"),          # wrong year
        ({"filename": "2025 Mar bank stmt.pdf", "entity_hint": "Beta Inc"}, "flag"),  # wrong entity
        ({"filename": "1099-NEC 2025.pdf"}, "flag"),                       # nothing open for it
        ({"filename": "IMG_4471.jpg"}, "human_queue"),                     # unreadable
        ({"filename": "scan.pdf"}, "human_queue"),
        ({"filename": "bank stmt.pdf"}, "human_queue"),                    # no period
    ]
    return DOC_EVAL.run([{"input": c[0]["filename"], "label": c[1]} for c in cases],
                        lambda fn: match_document(
                            next(c[0] for c in cases if c[0]["filename"] == fn),
                            items, eng)["action"])


# ---------------------------------------------------------------- the partner board

def partner_board(ref=None):
    ref = ref or now()
    engs = store.load("engagements")
    items = store.load("open_items")
    by_eng = {}
    for i in items:
        by_eng.setdefault(i["engagement_id"], []).append(i)
    clients = store.index("clients")
    rows = []
    for e in engs:
        if e.get("state") == "complete":
            continue
        mine = by_eng.get(e["id"], [])
        outstanding = [i for i in mine if i.get("state") != "received"]
        rows.append({
            "engagement": e["id"], "client": clients.get(e["client_id"], {}).get("name"),
            "type": e["type"], "label": ENGAGEMENT_TYPES[e["type"]]["label"],
            "state": e.get("state"), "blocker": e.get("blocker"),
            "blocker_age": blocker_age_days(e, ref),
            "due": e.get("due"), "days_to_due": days_until(e.get("due"), ref),
            "open_items": len(outstanding),
            "owner": e.get("owner"),
        })
    rows.sort(key=lambda r: ((r["days_to_due"] if r["days_to_due"] is not None else 999),
                             -(r["blocker_age"] or 0)))
    return {"generated": iso(ref), "rows": rows,
            "at_risk": [r for r in rows if (r["days_to_due"] is not None and r["days_to_due"] <= 7)],
            "blocked_on_client": sum(1 for r in rows if r["blocker"] == "client"),
            "blocked_on_us": sum(1 for r in rows if r["blocker"] == "firm"),
            "automation": automation()}


def blocker_ages(ref=None, floor=10):
    ages = [a for a in (blocker_age_days(e, ref) for e in store.load("engagements")
                        if e.get("state") != "complete") if a is not None]
    if len(ages) < floor:
        return unmeasured(f"only {len(ages)} blocked engagements; need {floor} for a median",
                          field="median_days", n=len(ages))
    return {"median_days": round(median(ages), 1), "max_days": max(ages), "n": len(ages)}


def scope_ledger():
    rows = store.load("scope_events")
    undecided = [r for r in rows if not r.get("decision")]
    return {"n": len(rows), "undecided": len(undecided), "rows": rows[-40:],
            "note": "every row cites the clause of the engagement letter it falls outside; "
                    "without a citation it is not logged at all"}


# ---------------------------------------------------------------- ROI

ROI = (Roi("What the chase is worth here")
       .line("Chase time", "time_saved",
             "chase messages/wk × minutes each × 48 × loaded rate",
             ["chase_messages_wk", "minutes_per_touch", "loaded_rate"],
             lambda g: g["chase_messages_wk"] * (g["minutes_per_touch"] / 60) * 48 * g["loaded_rate"],
             note="counted per MESSAGE, not per item — bundling eleven open items into one "
                  "message is most of the saving, so counting per item would double-count it")
       .line("Intake time", "time_saved",
             "documents/wk × minutes each × 48 × loaded rate",
             ["documents_wk", "minutes_per_doc", "loaded_rate"],
             lambda g: g["documents_wk"] * (g["minutes_per_doc"] / 60) * 48 * g["loaded_rate"])
       .line("Cycle time → cash", "cash_timing",
             "engagements × blocker days removed × daily WIP value",
             ["engagements", "blocker_days_removed", "daily_wip_value"],
             lambda g: g["engagements"] * g["blocker_days_removed"] * g["daily_wip_value"],
             note="THIS IS CASH CONVERSION, NOT REVENUE. Faster engagements change WHEN you get "
                  "paid, not whether — it is a real benefit and it is not a new dollar")
       .line("Recovered scope", "revenue",
             "out-of-scope events × capture% × avg billable value",
             ["scope_events_per_year", "capture_rate", "avg_scope_value"],
             lambda g: g["scope_events_per_year"] * g["capture_rate"] * g["avg_scope_value"],
             note="the honest headline: new revenue, measurable, and invisible today",
             assumption="capture% is the share a partner decides to bill rather than forgive"))


def roi(given=None):
    cfg = store.load("config")
    recorded = {}
    # Both of these are counted over the LAST SEVEN DAYS, not derived by dividing
    # a standing backlog. "Outstanding ÷ 4" would have reported 694 items a week
    # at a 230-client firm, which is the kind of number a partner checks once and
    # then stops believing the rest of the panel.
    since = now() - timedelta(days=7)
    items = [i for i in store.load("open_items")
             if (parse(i.get("requested_at")) or now()) >= since]
    if items:
        recorded["open_items_wk"] = len(items)
    msgs = [e for e in store.load("events")
            if e["kind"] in ("request_items", "chase_nudge", "chase_escalate", "chase_sent")
            and (parse(e["at"]) or now()) >= since]
    if msgs:
        recorded["chase_messages_wk"] = len(msgs)
    docs = [d for d in store.load("documents")
            if (parse(d.get("arrived_at")) or now()) >= since]
    if docs:
        recorded["documents_wk"] = len(docs)
    engs = [e for e in store.load("engagements") if e.get("state") != "complete"]
    if engs:
        recorded["engagements"] = len(engs)
    sc = store.load("scope_events")
    if sc:
        recorded["scope_events_per_year"] = len(sc)
    merged = dict(recorded)
    merged.update({k: v for k, v in (cfg.get("roi_inputs") or {}).items() if v not in (None, "")})
    merged.update({k: v for k, v in (given or {}).items() if v not in (None, "")})
    out = ROI.render(merged)
    out["recorded"] = recorded
    out["operator_supplied"] = {k: v for k, v in merged.items() if k not in recorded}
    return out
