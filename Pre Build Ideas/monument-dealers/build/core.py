#!/usr/bin/env python3
"""Stone OS — domain core (monument & headstone dealers).

Rules live here: proof-first triage (the family's correction is the message
that can never be mis-routed — granite is not reworked), the proof gate
(approval is a recorded human act by the family; software never approves and
engraving cannot start without the record), the cemetery rulebook (recorded
rules are cited or the answer is UNKNOWN), the setting date-checks (cemetery
approval + foundation cure, both recorded), the bounded balance ladder, and
the matrix.

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

TABLES = ("config", "families", "orders", "cemeteries", "proofs", "corrections",
          "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="STONEOS_DATA_ROOT")

# ---------------------------------------------------------------- the pipeline

STAGES = ("contract", "cemetery_approval", "proof", "engraving", "foundation",
          "cure", "setting", "set")

STAGE_CLOCK_DAYS = {"contract": 10, "cemetery_approval": 21, "proof": 14,
                    "engraving": 28, "foundation": 14, "cure": 35, "setting": 14}

STAGE_NOTE = {
    "contract": "signed contract, order opened",
    "cemetery_approval": "waiting on the cemetery's own approval form",
    "proof": "the proof is with the family — nothing is carved until they approve it",
    "engraving": "in the shop, cutting to the approved proof",
    "foundation": "foundation work at the cemetery",
    "cure": "the foundation is curing — a date clock, not a judgment call",
    "setting": "setting is being scheduled with the cemetery",
    "set": "set and complete",
}

BLOCKERS = ("family", "cemetery", "shop", "weather")


def pipeline_board(ref=None):
    """Active orders with per-stage clocks. A stalled order names its blocker;
    a stalled order with no recorded blocker says so — 'unrecorded' is an
    answer, a guessed blocker is not."""
    ref = ref or now()
    rows, by_stage = [], {s: 0 for s in STAGES}
    for o in store.load("orders"):
        if o.get("demo_tag") or o.get("stage") == "set":
            if o.get("stage") == "set" and not o.get("demo_tag"):
                by_stage["set"] += 1
            continue
        by_stage[o.get("stage", "contract")] = by_stage.get(o.get("stage", "contract"), 0) + 1
        entered = parse(o.get("stage_entered_at"))
        days = (ref - entered).days if entered else None
        clock = STAGE_CLOCK_DAYS.get(o.get("stage"))
        stalled = days is not None and clock is not None and days > clock
        row = {"order": o["id"], "family": o.get("family_name"),
               "deceased": o.get("deceased_name"), "cemetery_id": o.get("cemetery_id"),
               "stage": o.get("stage"), "days_in_stage": days, "stage_clock_days": clock,
               "stalled": stalled}
        if stalled:
            row["blocker"] = o.get("blocker") or ("unrecorded — nobody has written down "
                                                  "what this order waits on")
        rows.append(row)
    rows.sort(key=lambda r: (not r["stalled"], -(r["days_in_stage"] or 0)))
    return {"rows": rows, "active": len(rows), "by_stage": by_stage,
            "stalled": sum(1 for r in rows if r["stalled"]),
            "note": "a stalled order names its blocker (family / cemetery / shop / weather) "
                    "or says 'unrecorded' — it never guesses"}


# ---------------------------------------------------------------- the proof gate

def proof_for(order):
    if not order:
        return None
    if order.get("proof_id"):
        return store.by_id("proofs", order["proof_id"])
    for p in store.load("proofs"):
        if p.get("order_id") == order.get("id"):
            return p
    return None


def proof_approval(order):
    """The recorded family approval, or None. There is no other source of a
    'yes' — not a phone note, not a hunch, not software."""
    p = proof_for(order)
    return (p or {}).get("approval") or None


def can_engrave(order):
    """Structural: engraving needs the family's recorded approval — a named
    person and a signature reference on the proof record. No record, no path."""
    p = proof_for(order)
    if not p:
        return False, ("no proof on record for this order — nothing exists for the family "
                       "to have approved. A proof renders first, always.")
    ap = p.get("approval")
    if not ap:
        return False, (f"proof {p['id']} has no recorded family approval — engraving cannot "
                       f"start. Approval is a recorded human act by the family (a name and a "
                       f"signature reference), never a phone note and never software. "
                       f"Granite is not reworked.")
    return True, (f"family approval on record: {ap.get('by')} (signature ref "
                  f"{ap.get('signature_ref')}, {ap.get('at')}) — the record is the permission")


# ---------------------------------------------------------------- the cemetery rulebook

DEFAULT_CURE_DAYS = 28


def cemetery_rules(cemetery_id):
    cem = store.by_id("cemeteries", cemetery_id)
    if not cem:
        return None, None
    return cem, cem.get("rules")


def compliance(order):
    """Every line CITES the recorded per-cemetery rulebook. A cemetery with no
    recorded rules reads UNKNOWN — never assumed, never borrowed from the
    cemetery next door."""
    cem, rules = cemetery_rules(order.get("cemetery_id"))
    if not cem:
        return unmeasured("no such cemetery on record", field="state")
    if not rules:
        return unmeasured(
            f"no recorded rulebook for {cem['name']} — compliance is UNKNOWN, never assumed. "
            f"Get their rules sheet on the record; until then no monument spec can be called "
            f"compliant here", field="state", cemetery=cem["name"])
    mon = order.get("monument") or {}
    checks = []

    def check(rule, recorded, got, okv):
        checks.append({"rule": rule, "recorded": recorded, "order": got, "ok": okv,
                       "cite": rules["_source"]})

    h = mon.get("height_in")
    check(f"max height {rules['max_height_in']}\"", rules["max_height_in"], h,
          None if h is None else h <= rules["max_height_in"])
    check("base required" if rules["base_required"] else "base optional",
          rules["base_required"], bool(mon.get("base")),
          (bool(mon.get("base")) or not rules["base_required"]))
    f = mon.get("finish")
    check(f"finish in {', '.join(rules['finishes'])}", rules["finishes"], f,
          None if f is None else f in rules["finishes"])
    unable = [c for c in checks if c["ok"] is None]
    okall = None if unable else all(c["ok"] for c in checks)
    return {"state": "cited", "cemetery": cem["name"], "checks": checks, "ok": okall,
            "approval_form": rules.get("approval_form"), "source": rules["_source"],
            "note": ("every line cites the recorded rulebook — software never declares "
                     "compliance beyond what the record supports"
                     + ("; a spec field not recorded on the order reads unchecked, not passed"
                        if unable else ""))}


# ---------------------------------------------------------------- setting: two date checks

def can_set(order, ref=None):
    """Setting needs BOTH records: the cemetery's approval (a date on file) and
    the foundation cure clock complete. Date checks, with the dates named."""
    ref = ref or now()
    ca = parse(order.get("cemetery_approval_at"))
    if not ca:
        return False, ("no recorded cemetery approval — setting waits for the cemetery's own "
                       "approval, on the record. A monument set without it comes back up.")
    fp = parse(order.get("foundation_poured_at"))
    if not fp:
        return False, ("cemetery approval is on record, but there is no recorded foundation "
                       "pour date — the cure clock never started.")
    _, rules = cemetery_rules(order.get("cemetery_id"))
    cure = (rules or {}).get("cure_days", DEFAULT_CURE_DAYS)
    settable = fp + timedelta(days=cure)
    if ref < settable:
        return False, (f"foundation poured {fp.date().isoformat()}; the cure runs {cure} days "
                       f"→ settable {settable.date().isoformat()}; today is "
                       f"{ref.date().isoformat()}. Granite over green concrete is a leaning "
                       f"monument.")
    return True, (f"cemetery approval recorded {ca.date().isoformat()}; foundation poured "
                  f"{fp.date().isoformat()} and cured ({cure} days complete "
                  f"{settable.date().isoformat()}) — settable")


# ---------------------------------------------------------------- grief-safe tone

FORBIDDEN_TONE = ("act now", "final notice", "last chance", "urgent", "immediately",
                  "limited time", "don't delay", "must pay", "asap", "past due",
                  "expires", "overdue")


def tone_ok(text):
    t = (text or "").lower()
    hits = [w for w in FORBIDDEN_TONE if w in t]
    if hits:
        return False, (f"grief comms carry no urgency or pressure — forbidden language: "
                       f"{', '.join(hits)}")
    return True, "ok"


# ---------------------------------------------------------------- the balance ladder

BALANCE_MAX_TOUCHES = 3
BALANCE_COOLDOWN_DAYS = 14


def balance_plan(order, ref=None):
    ref = ref or now()
    if not order.get("balance_due"):
        return {"action": "none", "why": "nothing owed"}
    touches = order.get("balance_touches") or []
    if len(touches) >= BALANCE_MAX_TOUCHES:
        return {"action": "none",
                "why": (f"ladder exhausted at {BALANCE_MAX_TOUCHES} — silence is an answer; "
                        f"what happens next is a person's call, made gently. Nobody duns a "
                        f"widow by robot.")}
    last = parse(touches[-1]["at"]) if touches else parse(order.get("set_at"))
    if last and (ref - last).days < BALANCE_COOLDOWN_DAYS:
        return {"action": "none", "why": f"inside the {BALANCE_COOLDOWN_DAYS}-day cooldown"}
    return {"action": "draft_reminder", "why": f"touch {len(touches)+1} of {BALANCE_MAX_TOUCHES}"}


def recovered_this_week(ref=None):
    """Counted: balances collected (from the ledger), proofs family-approved
    (recorded human acts), family notes sent (human sends count; agent drafts
    don't), monuments set."""
    ref = ref or now()
    collected = [o for o in store.load("orders")
                 if o.get("balance_paid_at")
                 and (ref - (parse(o["balance_paid_at"]) or ref)).days <= 7]
    just_set = [o for o in store.load("orders")
                if o.get("set_at") and (ref - (parse(o["set_at"]) or ref)).days <= 7]
    approvals = sum(1 for e in store.events(kind="proof_approved")
                    if str(e.get("actor", "")).startswith("human:")
                    and (ref - (parse(e.get("at")) or ref)).days <= 7)
    sends = sum(1 for e in store.events(kind=("draft_family_update", "draft_balance_reminder",
                                              "draft_balance_reply", "draft_proof_reply",
                                              "draft_inquiry_reply"))
                if str(e.get("actor", "")).startswith("human:")
                and (ref - (parse(e.get("at")) or ref)).days <= 7)
    return {"balances_collected": len(collected),
            "balance_cash": round(sum(o.get("balance_paid_amount") or 0 for o in collected), 2),
            "proofs_family_approved": approvals,
            "family_notes_sent": sends,
            "monuments_set": len(just_set),
            "note": "counted from the ledger and the event log — human sends count; agent "
                    "drafts don't"}


# ---------------------------------------------------------------- triage

PROOF_CHANGE = (
    r"\b(proofs?|inscription|stone|engraving|lettering|epitaph|spelling)\b.*"
    r"\b(wrong|incorrect|error|mistakes?|misspell\w*|fix\w*|chang\w*|should (be|read|say))\b",
    r"\b(wrong|incorrect|error|mistakes?|misspell\w*|fix|chang\w*|correct\w*)\b.*"
    r"\b(proofs?|inscription|date|name|spelling|epitaph|stone|year)\b",
    r"\bspell\w*\b.*\bnot\b",
    r"\b(19|20)\d\d\b.*\bnot\b.*\b(19|20)\d\d\b",
    r"\bproofs?\b.*\b(19|20)\d\d\b",
)
TIMELINE = (
    r"\b(when|how long|what'?s (left|next)|any update|update on|status)\b.*"
    r"\b(stone|headstone|monument|marker|memorial|order|set|setting|ready)\b",
    r"\b(stone|headstone|monument|marker|memorial)\b.*\b(ready|finished|done|set yet|status|"
    r"update)\b",
)
BALANCE = (
    r"\b(balance|owe|owed|pay ?off|invoice|bill|final payment|remaining)\b",
    r"\bpay\b.*\b(balance|remaining|rest|off|monument|stone|headstone)\b",
)
NEW_INQUIRY = (
    r"\b(passed away|passed last|died|lost (my|our))\b",
    r"\b(how much|price|cost|quote|estimate)\b.*\b(stone|headstone|monument|marker|memorial|"
    r"granite|bronze)\b",
    r"\b(need|looking for|interested in)\b.*\b(headstone|monument|marker|memorial)\b",
)


def read_message(text):
    """proof_change | timeline | balance | new_inquiry | human. The proof
    change reads FIRST — a family correcting a date is the one message that
    can never be mis-routed, because granite is not reworked."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in PROOF_CHANGE:
        if re.search(rx, t):
            return {"label": "proof_change",
                    "why": "a proof/inscription correction from the family — engraving holds "
                           "the moment this arrives; the corrected proof goes back to the "
                           "family, and only the family approves it"}
    for rx in TIMELINE:
        if re.search(rx, t):
            return {"label": "timeline",
                    "why": "a where-is-it ask — answered from the recorded stage, blocker "
                           "named, never a guessed date"}
    for rx in BALANCE:
        if re.search(rx, t):
            return {"label": "balance",
                    "why": "a balance ask — answered from the ledger, gently; no urgency "
                           "language exists in this lane"}
    for rx in NEW_INQUIRY:
        if re.search(rx, t):
            return {"label": "new_inquiry",
                    "why": "a new family — grief-appropriate welcome, no hurry, every number "
                           "in writing before any decision"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="proof_change",
                   costly_note=("A FAMILY'S CORRECTION MIS-ROUTED IS A MISSPELLED HEADSTONE — "
                                "GRANITE IS NOT REWORKED, AND THE REMAKE IS FIVE FIGURES AND A "
                                "SEASON. Over-routing a balance ask costs a read."))

EVAL_CASES = [
    {"input": "the date on the proof is wrong, my mother was born in 1941 not 1942",
     "label": "proof_change"},
    {"input": "katharine is spelled with an a not an e, please fix the proof before you carve",
     "label": "proof_change"},
    {"input": "we'd like to change the epitaph on the proof to beloved father and grandfather",
     "label": "proof_change"},
    {"input": "the middle name on the stone should be anne not ann", "label": "proof_change"},
    {"input": "the proof shows 1938 but dad was born in 1939", "label": "proof_change"},
    {"input": "when will my father's headstone be set", "label": "timeline"},
    {"input": "any update on my mother's monument", "label": "timeline"},
    {"input": "is the marker finished yet", "label": "timeline"},
    {"input": "what do we still owe on the headstone", "label": "balance"},
    {"input": "can i pay the remaining balance over the phone", "label": "balance"},
    {"input": "wanted to pay off dad's monument this week", "label": "balance"},
    {"input": "my husband passed away last month and we need a headstone",
     "label": "new_inquiry"},
    {"input": "how much does a granite companion monument cost", "label": "new_inquiry"},
    {"input": "", "label": "human"},
    {"input": "thank you, the graveside service yesterday was beautiful", "label": "human"},
    {"input": "what are your hours on saturday", "label": "human"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":         {"rung": "R3", "reason": "routing only; the proof change reads first"},
    "approve_proof":        {"rung": "R0", "reason": "only the family approves a proof, on the record — a proof approved by software is a misspelled headstone waiting to happen", "never_promote": True},
    "start_engraving_without_proof_approval":
                            {"rung": "R0", "reason": "structural — engraving starts from the family's recorded approval or it does not start; granite is not reworked", "never_promote": True},
    "declare_cemetery_compliant":
                            {"rung": "R0", "reason": "the recorded per-cemetery rulebook is cited or the answer is UNKNOWN — a guessed rule is a rejected monument at the gate", "never_promote": True},
    "set_before_cure":      {"rung": "R0", "reason": "setting needs the cemetery's recorded approval AND the foundation cure clock — both date checks; a monument set early comes back up", "never_promote": True},
    "record_proof_change":  {"rung": "R2", "reason": "the correction record and the engraving hold cannot wait — holding stone is safe; cutting it is not"},
    "start_engraving":      {"rung": "R2", "reason": "queueing shop work with the family's recorded approval attached — the approval record is the gate; this is the calendar"},
    "schedule_setting":     {"rung": "R1", "reason": "a date to the cemetery and the family — a human sends, with both date checks attached"},
    "draft_proof_reply":    {"rung": "R1", "reason": "outward grief comms on the costliest subject — a human sends"},
    "draft_family_update":  {"rung": "R1", "reason": "outward grief comms — a human sends; the recorded stage does the talking"},
    "draft_balance_reply":  {"rung": "R1", "reason": "money in grief comms — a human sends, the ledger cited"},
    "draft_balance_reminder": {"rung": "R1", "reason": "the ladder is bounded and gentle, and a human sends every rung of it"},
    "draft_inquiry_reply":  {"rung": "R1", "reason": "a new family's first impression — a human sends"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Stone OS — what it computes to")
        .line("Balances collected sooner", "cash_timing", "open balances × your collection lift",
              ["open_balances", "collection_lift"],
              lambda g: float(g["open_balances"]) * float(g["collection_lift"]),
              note="open balances are counted from the ledger; the lift from a bounded, "
                   "gentle ladder is your call")
        .line("Office hours returned", "time_saved", "hrs/wk × 52 × rate",
              ["office_hours_wk", "office_rate"],
              lambda g: float(g["office_hours_wk"]) * 52 * float(g["office_rate"]),
              note="cemetery rule lookups, status calls, and proof chasing are the hours")
        .line("Orders per season lift", "revenue", "extra orders per season × your avg margin",
              ["extra_orders_season", "avg_margin"],
              lambda g: float(g["extra_orders_season"]) * float(g["avg_margin"]),
              note="throughput on the counted pipeline — the extra orders are your estimate")
        .line("The remake that didn't happen", "scenario",
              "you decide what a caught typo is worth",
              ["remake_value"], lambda g: float(g["remake_value"]),
              assumption="never a promised save — granite is not reworked, and the misspelled "
                         "stone that was never cut is not our number"))


def roi(given):
    rec = {}
    rec["open_balances"] = round(sum(o.get("balance_due") or 0
                                     for o in store.load("orders")
                                     if not o.get("demo_tag")), 2)
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "record_proof_change", "start_engraving", "schedule_setting",
          "draft_proof_reply", "draft_family_update", "draft_balance_reply",
          "draft_balance_reminder", "draft_inquiry_reply")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("family:",))
