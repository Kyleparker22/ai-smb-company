#!/usr/bin/env python3
"""Reserve OS — domain core (HOA management).

Rules live here: the funding-band engine (reserve adequacy as bear/base/bull
projections against the RECORDED reserve study, with the special-assessment
horizon as a band, never one date), the no-study UNKNOWABLE refusal, the
staleness flag, the violation ledger (no recorded rule → no violation,
structurally), the fine clamp (the recorded schedule's arithmetic or nothing),
the human-only hearing, the one-read-path rule for the two doors, safety-first
triage, and the matrix.

THE LOAD-BEARING IDEA: HOA management is a trust desert — boards suspect
managers, homeowners suspect both, and reserve studies rot in drawers until
the six-figure special assessment lands as a surprise. This engine shows its
math: adequacy is bands against the recorded study or it is UNKNOWABLE, every
violation carries its recorded rule verbatim, and the homeowner portal renders
THE SAME numbers the board sees. One set of books, two doors, zero spin.

Stdlib only. Honesty rules come from `_kit`.
"""
import json, re, sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, iso, median, now,   # noqa: E402
                        parse, unmeasured)

TABLES = ("config", "associations", "homeowners", "violations", "messages",
          "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="RESERVEOS_DATA_ROOT")

# ---------------------------------------------------------------- recorded offsets

DEFAULT_INFLATION = {
    "_source": ("DEFAULT construction-cost inflation — the base is the trailing figure the "
                "operator adopts and records; the offsets are the bands. Replace with the "
                "operator's own recorded figures before go-live."),
    "base": 0.03,
    "offsets": {"bear": 0.02, "bull": -0.02},   # bear = costs run hotter, bull = cooler
}
DEFAULT_STALENESS_DAYS = 1095   # 3 years — overridable in config


def inflation():
    return store.load("config").get("inflation") or DEFAULT_INFLATION


def staleness_threshold():
    return store.load("config").get("staleness_threshold_days") or DEFAULT_STALENESS_DAYS


# ---------------------------------------------------------------- funding bands
#
# Adequacy is never one number. It is three projections of the recorded balance
# against the recorded study's component replacements at recorded cost-inflation
# offsets — and the SPECIAL-ASSESSMENT HORIZON is per band: the first year the
# projected balance goes negative, or "beyond the study window", honestly.

def funding_bands(assoc, ref=None):
    """Bear/base/bull funding trajectory for one association. No study →
    UNKNOWABLE refusal: no study, no adequacy claim. A study past the recorded
    staleness threshold FLAGS every number it feeds."""
    ref = ref or now()
    study = (assoc or {}).get("reserve_study")
    if not study or not study.get("components"):
        return {"refused": ("no study, no adequacy claim — record a reserve study and this "
                            "becomes arithmetic; until then any adequacy number would be an "
                            "invention, and a reassuring invention is the worst kind"),
                "unknowable": True, "association": (assoc or {}).get("id")}
    infl = inflation()
    threshold = staleness_threshold()
    as_of = parse(study.get("as_of")) or ref
    age_days = (ref - as_of).days
    stale = age_days > threshold
    elapsed = age_days / 365.25
    comps = study["components"]
    window = min(30, max(int(round(c["remaining_life_years"] - elapsed)) for c in comps) + 5)
    window = max(window, 5)
    contrib_yr = float(assoc.get("monthly_contribution") or 0) * 12
    start = float(assoc.get("reserve_balance") or 0)

    bands = {}
    for name in ("bear", "base", "bull"):
        g = infl["base"] + (infl["offsets"].get(name, 0.0) if name != "base" else 0.0)
        bal, yearly, horizon_year = start, [], None
        for t in range(1, window + 1):
            bal += contrib_yr
            due = [c for c in comps
                   if max(1, int(round(c["remaining_life_years"] - elapsed))) == t]
            spend = sum(c["replacement_cost"] * (1 + g) ** (elapsed + t) for c in due)
            bal -= spend
            yearly.append({"year_out": t, "calendar": ref.year + t,
                           "contribution": round(contrib_yr, 2),
                           "replacements": round(spend, 2),
                           "components_due": [c["name"] for c in due],
                           "balance": round(bal, 2)})
            if horizon_year is None and bal < 0:
                horizon_year = ref.year + t
        band = {"inflation": round(g, 4), "end_balance": round(bal, 2), "yearly": yearly,
                "horizon": ({"year": horizon_year,
                             "note": f"first year the projected balance goes negative at "
                                     f"{g:.1%} cost inflation"}
                            if horizon_year else
                            {"year": None,
                             "note": f"beyond the {window}-year study window — no shortfall "
                                     f"projected inside it; that is the window's honesty, "
                                     f"not a guarantee"})}
        if stale:
            band["stale_flag"] = True
        bands[name] = band

    out = {"association": assoc["id"], "study_as_of": study.get("as_of"),
           "study_age_days": age_days, "stale": stale, "window_years": window,
           "bands": bands, "inflation_source": infl["_source"],
           "label": ("THIS IS A MODEL — the recorded study, the recorded balance, the "
                     "recorded contribution, three recorded inflation bands. A single "
                     "adequacy number would be fiction; the horizon is a band, never a date")}
    if stale:
        out["stale_note"] = (f"the reserve study is {age_days} days old — past the recorded "
                             f"{threshold}-day staleness threshold; EVERY number here is "
                             f"flagged until a new study is recorded")
    return out


def adequacy(assoc_id):
    """The asked-for adequacy read. The no-study refusal is logged here as the
    R0 it is — claim_adequacy_without_study never runs, and the log shows it."""
    assoc = store.by_id("associations", assoc_id)
    if not assoc:
        return {"error": "no such association"}
    fb = funding_bands(assoc)
    if fb.get("unknowable"):
        ev = store.log_event("refused", assoc_id, "agent:reserves", "R0",
                             {"action": "claim_adequacy_without_study", "why": fb["refused"]})
        return {**fb, "event": ev["id"]}
    return fb


# ---------------------------------------------------------------- one ledger, two doors
#
# board_view() is THE read path. The homeowner door calls THE SAME function and
# removes only other homeowners' personal details — every funding number and
# every violation count is structurally identical, and the suite asserts it.

def board_view(assoc_id):
    """Everything the board sees for one association, from the recorded stores.
    This is the ONLY function that assembles these numbers."""
    assoc = store.by_id("associations", assoc_id)
    if not assoc:
        return {"error": "no such association"}
    fb = funding_bands(assoc)
    vios = [v for v in store.load("violations")
            if v.get("association_id") == assoc_id and not v.get("demo_tag")]
    by_stage = {}
    for v in vios:
        by_stage[v.get("stage", "?")] = by_stage.get(v.get("stage", "?"), 0) + 1
    items = assoc.get("dues_line_items") or []
    return {"door": "board", "association": {"id": assoc["id"], "name": assoc.get("name"),
                                             "doors": assoc.get("doors")},
            "funding": fb,
            "reserve_balance": assoc.get("reserve_balance"),
            "monthly_contribution": assoc.get("monthly_contribution"),
            "dues": {"monthly_total": round(sum(i["monthly"] for i in items), 2),
                     "line_items": items,
                     "note": "the recorded line items, verbatim — the same rows answer a "
                             "homeowner's dispute"},
            "violations": {"total": len(vios), "by_stage": by_stage,
                           "open": sum(1 for v in vios if v.get("stage") != "closed"),
                           "rows": [{"id": v["id"], "unit": v.get("unit"),
                                     "rule_section": v.get("rule_section"),
                                     "rule_title": v.get("rule_title"),
                                     "stage": v.get("stage"),
                                     "opened_at": v.get("opened_at"),
                                     "fine_amount": v.get("fine_amount")}
                                    for v in vios]},
            "rules": assoc.get("rules") or [],
            "note": "one ledger — the homeowner door renders from this same function"}


def homeowner_view(assoc_id, homeowner_id):
    """The homeowner door. Calls board_view() — the same read path, structurally
    — and filters ONLY the personal details of OTHER homeowners. The funding
    numbers and the violation counts are the board's, untouched."""
    ho = store.by_id("homeowners", homeowner_id)
    if not ho:
        return {"error": "no such homeowner"}
    bv = board_view(assoc_id)
    if "error" in bv:
        return bv
    out = json.loads(json.dumps(bv))          # deep copy; the numbers are never recomputed
    all_rows = out["violations"]["rows"]
    mine = [r for r in all_rows if r.get("unit") == ho.get("unit")]
    out["violations"]["rows"] = mine
    out["violations"]["others_redacted"] = len(all_rows) - len(mine)
    out["door"] = "homeowner"
    out["homeowner"] = {"id": ho["id"], "name": ho.get("name"), "unit": ho.get("unit")}
    out["note"] = ("the same numbers the board sees — one ledger, two doors; only other "
                   "homeowners' personal details are removed, never a figure")
    return out


# ---------------------------------------------------------------- the dues answer

def dues_answer(assoc, homeowner_name=None):
    """'Why did my dues rise' answered by citation: the recorded line items
    verbatim plus the band math — never a soothing paragraph."""
    items = assoc.get("dues_line_items") or []
    fb = funding_bands(assoc)
    total = sum(i["monthly"] for i in items)
    lines = "\n".join(f"  · {i['label']}: ${i['monthly']:,.2f}/mo" for i in items)
    if fb.get("unknowable"):
        reserve_part = ("On reserves: no reserve study is on record for this association, so "
                        "no adequacy claim rides on this answer — that gap is stated, not "
                        "papered over, and the board has it in front of them.")
    else:
        def hz(b):
            y = fb["bands"][b]["horizon"]["year"]
            return str(y) if y else f"beyond the {fb['window_years']}-year window"
        reserve_part = (f"On reserves: at the recorded contribution, the projected "
                        f"special-assessment horizon is {hz('bear')} (bear) / {hz('base')} "
                        f"(base) / {hz('bull')} (bull) — bands, never one date. The dues "
                        f"line that changed is funding that curve, not a mystery.")
        if fb.get("stale"):
            reserve_part += (" Flag: the study behind these numbers is past the recorded "
                             "staleness threshold — the board sees the same flag.")
    who = (homeowner_name or "there").split()[0]
    return (f"Hi {who} — here is the whole answer, from the same books the board sees.\n"
            f"Your dues, line by recorded line (${total:,.2f}/mo total):\n{lines}\n"
            f"{reserve_part}\n"
            f"Every figure above is the recorded number verbatim — nothing summarized, "
            f"nothing spun.")


# ---------------------------------------------------------------- the violation ledger
#
# Structural rule: create_violation is the ONLY writer to the violations table,
# and it cannot produce a row without resolving the cited section against the
# association's RECORDED rules list. No rule, no violation — there is no code
# path, and the suite proves the refusal.

LADDER = ("courtesy", "notice", "hearing", "fine")


def rule_for(assoc, section):
    for r in (assoc or {}).get("rules") or []:
        if r.get("section") == section:
            return r
    return None


def create_violation(assoc_id, unit, section, description, photo_ref=None,
                     offense_n=1, demo_tag=None):
    assoc = store.by_id("associations", assoc_id)
    rule = rule_for(assoc, section)
    if not rule:
        ev = store.log_event("refused", assoc_id, "agent:compliance", "R0",
                             {"action": "violation_without_recorded_rule",
                              "why": f"no recorded rule {section!r} in this association's "
                                     f"CC&Rs — a violation that cites nothing IS nothing; "
                                     f"record the rule first or drop the complaint"})
        return {"refused": f"no recorded rule {section!r} — no rule, no violation. The "
                           f"ledger only carries what the CC&Rs actually say.",
                "event": ev["id"]}
    v = {"id": store.nid("vi"), "association_id": assoc_id, "unit": unit,
         "rule_section": rule["section"], "rule_title": rule["title"],
         "description": description, "photo_ref": photo_ref,
         "offense_n": int(offense_n or 1), "stage": "courtesy",
         "opened_at": iso(), "history": [{"at": iso(), "stage": "courtesy"}]}
    if demo_tag:
        v["demo_tag"] = demo_tag
    store.upsert("violations", v)
    store.log_event("record_violation", v["id"], "agent:compliance", "R2",
                    {"rule": rule["section"], "unit": unit, "association": assoc_id})
    return {"violation": v, "cited": f"{rule['section']} — {rule['title']}"}


def scheduled_fine(assoc, offense_n):
    """The recorded fine schedule's arithmetic — the only math a fine may use."""
    sched = (assoc or {}).get("fine_schedule") or {}
    amounts = sched.get("amounts") or {}
    if not amounts:
        return unmeasured("no recorded fine schedule — no fine can be computed", field="amount")
    key = str(min(int(offense_n or 1), max(int(k) for k in amounts)))
    return {"amount": amounts[key], "offense_n": int(offense_n or 1),
            "basis": f"the recorded schedule's arithmetic: offense {offense_n} → "
                     f"${amounts[key]:,}",
            "source": sched.get("_source")}


def can_advance(violation):
    """courtesy → notice → hearing, per the recorded policy. The step to fine
    does not exist here — the hearing decision is a human act."""
    stage = violation.get("stage")
    if stage not in ("courtesy", "notice"):
        return None, (f"cannot advance from {stage!r} — the ladder stops at the hearing; "
                      f"the decision there is a human's, on the record")
    return LADDER[LADDER.index(stage) + 1], "next recorded rung of the ladder"


def hearing_decide(violation_id, human=None, outcome="upheld", note=None):
    """The hearing decision. A human, or nothing — software never decides."""
    v = store.by_id("violations", violation_id)
    if not v:
        return {"error": "no such violation"}
    if v.get("stage") != "hearing":
        return {"refused": f"this violation is at {v.get('stage')!r} — the hearing decision "
                           f"only exists at the hearing rung"}
    if not human:
        ev = store.log_event("refused", violation_id, "agent:compliance", "R0",
                             {"action": "decide_hearing",
                              "why": "the hearing decision is a human act on the record — "
                                     "software assembles the file and stops"})
        return {"refused": "the hearing decision is a human act — software assembles the "
                           "file, cites the rule, and stops there", "event": ev["id"]}
    assoc = store.by_id("associations", v["association_id"])
    if outcome == "upheld":
        fine = scheduled_fine(assoc, v.get("offense_n", 1))
        if fine.get("_missing"):
            return {"refused": fine["_missing"]}
        v["stage"] = "fine"
        v["fine_amount"] = fine["amount"]
        v["fine_basis"] = fine["basis"]
    else:
        v["stage"] = "closed"
        v["closed_reason"] = "dismissed at hearing"
    v.setdefault("history", []).append({"at": iso(), "stage": v["stage"],
                                        "by": f"human:{human}", "note": note})
    store.upsert("violations", v)
    store.log_event("hearing_decided", violation_id, f"human:{human}", "R1",
                    {"outcome": outcome, "fine": v.get("fine_amount"), "note": note})
    return {"decided": True, "outcome": outcome, "stage": v["stage"],
            "fine_amount": v.get("fine_amount"), "fine_basis": v.get("fine_basis")}


def check_fine(violation_id, amount):
    """The fine clamp. Any amount that is not the recorded schedule's arithmetic
    is refused — R0, logged, never approvable."""
    v = store.by_id("violations", violation_id)
    if not v:
        return {"error": "no such violation"}
    assoc = store.by_id("associations", v["association_id"])
    sched = scheduled_fine(assoc, v.get("offense_n", 1))
    if sched.get("_missing"):
        return {"refused": sched["_missing"]}
    if v.get("stage") not in ("hearing", "fine"):
        return {"refused": f"this violation is at {v.get('stage')!r} — no fine exists "
                           f"before the hearing rung, per the recorded ladder"}
    if round(float(amount), 2) != round(float(sched["amount"]), 2):
        ev = store.log_event("refused", violation_id, "agent:compliance", "R0",
                             {"action": "fine_off_schedule",
                              "why": f"${float(amount):,.2f} is not the recorded schedule's "
                                     f"arithmetic ({sched['basis']}) — the schedule or a "
                                     f"human hearing, never an ad-hoc number"})
        return {"refused": f"${float(amount):,.2f} is off-schedule — {sched['basis']}. "
                           f"Fines are the recorded schedule's arithmetic, full stop.",
                "event": ev["id"], "scheduled": sched}
    if v.get("stage") == "hearing":
        return {"refused": "the amount matches the schedule, but the hearing decision is a "
                           "human act — no fine lands before a person decides on the record",
                "scheduled": sched}
    return {"ok": True, "scheduled": sched,
            "note": "matches the recorded schedule; upheld at hearing by a human"}


# ---------------------------------------------------------------- triage
#
# The costly label reads FIRST: a common-area safety report routes NOW,
# verbatim, and is never queued behind anything.

SAFETY = (
    r"\b(railings?|handrails?|stairs?|stairwell|balcony|walkway|sidewalk|gate|latch|wiring|"
    r"wires?|light(ing)?s?|pool fence|tree limb|branch|playground|garage door|steps?)\b.*"
    r"\b(loose|broken|falling|fell|came down|down|exposed|hazard|dangerous|unsafe|crack\w*|"
    r"collaps\w*|sparking|hanging|missing|won'?t (close|latch))\b",
    r"\b(loose|broken|exposed|collaps\w*|crack\w*|hanging|fallen)\b.*\b(railings?|handrails?|"
    r"stairs?|stairwell|balcony|walkway|wiring|gate|lights?|limb|steps?)\b",
    r"\bsomeone('s| is)? (going to|gonna|could|about to) (get hurt|fall|trip)\b",
    r"\btrip hazard\b",
)
APPEAL = (
    r"\b(appeal\w*|contest\w*|disput\w*|fight\w*)\b.*\b(violation|notice|fine|citation)\b",
    r"\b(violation|notice|fine)\b.*\b(appeal|contest|dispute|unfair|wrong)\b",
    r"\b(want|request|get)\b.*\bhearing\b",
)
DUES = (
    r"\b(dues|assessments?|hoa fees?|fees?)\b.*\b(went up|going up|go(ne)? up|increased?|"
    r"rise|rose|raised?|higher|jump\w*|doubled|too high)\b",
    r"\bwhy\b.*\b(dues|assessments?|fees?)\b",
    r"\b(charged|billed)\b.*\b(twice|late fee|wrong|error)\b",
)
AMENITY = (
    r"\b(reserve|book|rent)\b.*\b(clubhouse|pool|room|pavilion|cabana)\b",
    r"\b(fob|key ?card|gate code|remote|parking (pass|permit))\b",
    r"\bpool (key|pass|hours)\b",
)


def read_message(text):
    """safety | appeal | dues_dispute | amenity | human. Safety reads FIRST —
    the loose railing is the lawsuit, and it routes NOW, never queued."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in SAFETY:
        if re.search(rx, t):
            return {"label": "safety",
                    "why": "a common-area safety report — routed NOW, verbatim, never "
                           "queued; dismissing it is the one thing this system cannot do"}
    for rx in APPEAL:
        if re.search(rx, t):
            return {"label": "appeal",
                    "why": "a violation appeal — a recorded right; acknowledged with the "
                           "hearing process cited, and the hearing decision stays human"}
    for rx in DUES:
        if re.search(rx, t):
            return {"label": "dues_dispute",
                    "why": "a dues/fee dispute — answered by citation: the recorded line "
                           "items verbatim plus the band math, never a soothing paragraph"}
    for rx in AMENITY:
        if re.search(rx, t):
            return {"label": "amenity", "why": "an amenity/access ask — answered from the record"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="safety",
                   costly_note=("A DISMISSED LOOSE-RAILING REPORT IS THE INJURY LAWSUIT AND "
                                "THE LOST CONTRACT IN ONE. Over-routing an amenity ask "
                                "costs a read."))

EVAL_CASES = [
    {"input": "the stairwell railing is loose", "label": "safety"},
    {"input": "the pool gate latch is broken and kids are getting in", "label": "safety"},
    {"input": "there's exposed wiring by the mailboxes in building C", "label": "safety"},
    {"input": "a big tree limb came down across the walkway last night", "label": "safety"},
    {"input": "the balcony railing on building B is coming loose", "label": "safety"},
    {"input": "why did my dues go up this year", "label": "dues_dispute"},
    {"input": "our assessment jumped forty dollars and nobody explained it", "label": "dues_dispute"},
    {"input": "i was charged a late fee i don't owe", "label": "dues_dispute"},
    {"input": "i want to appeal the violation notice about my flag", "label": "appeal"},
    {"input": "i'm contesting the fine for the trash cans", "label": "appeal"},
    {"input": "can i get a hearing about this notice", "label": "appeal"},
    {"input": "how do i reserve the clubhouse for a birthday party", "label": "amenity"},
    {"input": "my pool fob stopped working", "label": "amenity"},
    {"input": "", "label": "human"},
    {"input": "when is the next board meeting", "label": "human"},
    {"input": "where do i find the approved paint colors", "label": "human"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":            {"rung": "R3", "reason": "routing only; the safety report reads first"},
    "escalate_safety_report":  {"rung": "R2", "reason": "common-area safety routes NOW, verbatim — acts, tells a human, never queued"},
    "dismiss_safety_report":   {"rung": "R0", "reason": "a dismissed safety report is the injury lawsuit — escalation is the only path", "never_promote": True},
    "claim_adequacy_without_study": {"rung": "R0", "reason": "no study, no adequacy claim — UNKNOWABLE is the honest answer, never a reassurance", "never_promote": True},
    "violation_without_recorded_rule": {"rung": "R0", "reason": "structural — no code path creates a violation without a recorded CC&R rule; this row exists so the prohibition is visible", "never_promote": True},
    "fine_off_schedule":       {"rung": "R0", "reason": "fines are the recorded schedule's arithmetic or a human hearing — never an ad-hoc number", "never_promote": True},
    "decide_hearing":          {"rung": "R0", "reason": "the hearing decision is a human act on the record — software assembles the file and stops", "never_promote": True},
    "record_violation":        {"rung": "R2", "reason": "internal ledger write with the rule cited — the citation is structural"},
    "advance_violation":       {"rung": "R2", "reason": "internal stage move on the recorded ladder — the outward notice still queues R1"},
    "assess_fine":             {"rung": "R1", "reason": "money — the recorded schedule's arithmetic, and a human clicks"},
    "draft_violation_notice":  {"rung": "R1", "reason": "outward notice — the rule cited verbatim, a human sends"},
    "draft_safety_ack":        {"rung": "R1", "reason": "outward reply — the escalation already happened at R2; the ack waits for a human"},
    "draft_dues_reply":        {"rung": "R1", "reason": "outward reply — citation-answered, a human sends"},
    "draft_appeal_ack":        {"rung": "R1", "reason": "outward reply — the recorded hearing process cited, a human sends"},
    "draft_amenity_reply":     {"rung": "R1", "reason": "outward reply — a human sends"},
    "draft_board_packet":      {"rung": "R1", "reason": "the monthly packet drafts for the manager — never auto-sent to a board"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Reserve OS — what it computes to")
        .line("Violation-dispute hours returned", "time_saved",
              "disputes/mo × min per citation-answered dispute × 12 × rate",
              ["disputes_month", "min_per_dispute", "rate"],
              lambda g: float(g["disputes_month"]) * float(g["min_per_dispute"]) / 60 * 12
              * float(g["rate"]),
              note="disputes answered is counted from this system's own log")
        .line("Collection lift from citation-answered disputes", "revenue",
              "delinquent balance × your recovery lift",
              ["delinquent_balance", "recovery_lift"],
              lambda g: float(g["delinquent_balance"]) * float(g["recovery_lift"]),
              assumption="your ledger, your lift — counted going forward, never assumed")
        .line("Contracts won or kept on provable fairness", "scenario",
              "you decide what a board that can check the math is worth",
              ["contract_value"], lambda g: float(g["contract_value"]),
              assumption="never a saving we claim — the renewal that didn't churn is "
                         "not our number")
        .line("The special assessment that landed as a plan, not a shock", "scenario",
              "you decide what the early-warned horizon is worth",
              ["shock_value"], lambda g: float(g["shock_value"]),
              assumption="the horizon is a band, never a date — and its value is yours "
                         "to state, not ours"))


def roi(given):
    rec = {}
    ref = now()
    rec["disputes_month"] = sum(
        1 for m in store.load("messages")
        if m.get("label") == "dues_dispute" and m.get("handled_at")
        and (ref - (parse(m["handled_at"]) or ref)).days <= 30)
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


# ---------------------------------------------------------------- counted week

def counted_this_week(ref=None):
    """Counted from the event log — never asserted. Human sends count; agent
    drafts don't."""
    ref = ref or now()

    def recent(rows):
        return [e for e in rows if (ref - (parse(e.get("at")) or ref)).days <= 7]

    escalated = recent(store.events(kind="escalate_safety_report"))
    notices = [e for e in recent(store.events(kind="draft_violation_notice"))
               if str(e.get("actor", "")).startswith("human:")]
    answers = [e for e in recent(store.events(kind="draft_dues_reply"))
               if str(e.get("actor", "")).startswith("human:")]
    hearings = recent(store.events(kind="hearing_decided"))
    return {"safety_reports_escalated": len(escalated),
            "notices_sent": len(notices),
            "disputes_answered": len(answers),
            "hearings_decided": len(hearings),
            "note": "counted from the event log — human sends count; agent drafts don't"}


MOVING = ("read_message", "escalate_safety_report", "record_violation", "advance_violation",
          "assess_fine", "draft_violation_notice", "draft_safety_ack", "draft_dues_reply",
          "draft_appeal_ack", "draft_amenity_reply", "draft_board_packet")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("homeowner:",))
