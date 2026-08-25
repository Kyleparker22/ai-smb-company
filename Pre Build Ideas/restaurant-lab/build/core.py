#!/usr/bin/env python3
"""Lab OS — domain core (a multi-unit restaurant group run as a laboratory).

Rules live here: the experiment desk whose verdict function structurally cannot
name a winner below the recorded sample floor ("TOO EARLY TO KNOW" is a real
verdict), the one-lever-per-dial overlap refusal, the rollout gate with no path
from anything but a concluded CLEAR result, the counterfactual 86 ledger priced
only from the unit's own recorded pace, the menu graveyard, and the illness
hard stop inherited from the Unit OS rule: logged verbatim, never answered in
writing by software.

The thesis: five locations is a laboratory nobody uses. Chains run continuous
honest experiments with data teams; a 5-unit group runs on gut feel and calls
one good weekend a result. Count the experiments honestly, price every 86 from
recorded pace, and refuse every number the records can't defend.

Stdlib only. Honesty rules come from `_kit`.
"""
import math, re, sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, iso, median, now,   # noqa: E402
                        parse, unmeasured)

TABLES = ("config", "units", "items", "observations", "experiments", "stockouts",
          "pace_history", "graveyard", "incidents", "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="LABOS_DATA_ROOT")

METRICS = ("attach_rate", "item_units", "avg_ticket")

# ---------------------------------------------------------------- sample floors

DEFAULT_FLOORS = {
    "_source": ("DEFAULT sample floors, simplified from a two-proportion / two-means power "
                "sketch at a ~10% detectable lift — replace with the group's own recorded "
                "floors before go-live. attach_rate counts tickets per arm; item_units and "
                "avg_ticket count unit-days per arm."),
    "attach_rate": {"n": 500, "unit": "tickets per arm"},
    "item_units":  {"n": 28,  "unit": "unit-days per arm"},
    "avg_ticket":  {"n": 28,  "unit": "unit-days per arm"},
}


def sample_floors():
    return store.load("config").get("sample_floors") or DEFAULT_FLOORS


# ---------------------------------------------------------------- the experiment desk

def _overlap(metric, unit_ids):
    """A live experiment already pulling this metric on any of these units."""
    for e in store.load("experiments"):
        if e.get("status") != "live" or e.get("metric") != metric:
            continue
        shared = (set(e.get("treatment_units") or []) | set(e.get("control_units") or [])) \
            & set(unit_ids)
        if shared:
            return e, sorted(shared)
    return None, []


def create_experiment(hypothesis, metric, treatment_units, control_units, item=None,
                      started_at=None):
    """Creation refuses an overlap — one lever per dial. The floor is recorded
    ON the experiment at creation, from the _source-named config table, so a
    later floor edit can never quietly re-grade a running test."""
    if metric not in METRICS:
        return {"refused": f"unknown metric '{metric}' — one of {', '.join(METRICS)}"}
    t, c = list(treatment_units or []), list(control_units or [])
    if not t or not c:
        return {"refused": "an experiment needs both a treatment arm and a control arm — "
                           "a test with no control is a launch wearing a lab coat"}
    if set(t) & set(c):
        return {"refused": "a unit cannot sit in both arms"}
    clash, shared = _overlap(metric, set(t) | set(c))
    if clash:
        why = (f"one lever per dial — “{clash['hypothesis']}” is already live on "
               f"{metric} for shared unit(s) {', '.join(shared)}; two live levers on one "
               f"dial make both experiments unreadable. Sequence them instead.")
        ev = store.log_event("refused", clash["id"], "agent:desk", "R0",
                             {"action": "overlapping_experiments_same_metric", "why": why})
        return {"refused": why, "event": ev["id"], "clashes_with": clash["id"]}
    floors = sample_floors()
    fl = floors[metric]
    exp = {"id": store.nid("exp"), "hypothesis": hypothesis, "metric": metric,
           "item": item, "treatment_units": t, "control_units": c, "status": "live",
           "started_at": started_at or iso(),
           "min_sample": {"n": fl["n"], "unit": fl["unit"], "_source": floors["_source"]}}
    store.upsert("experiments", exp)
    gate.act("create_experiment", "desk", exp["id"],
             {"hypothesis": hypothesis, "metric": metric,
              "floor": f"{fl['n']} {fl['unit']}"})
    return {"experiment": exp}


def _window(exp, ref=None):
    start = (exp.get("started_at") or "")[:10]
    end = iso(ref or now())[:10] if not exp.get("concluded_at") else exp["concluded_at"][:10]
    return start, end


def _arm(exp, unit_ids, ref=None):
    """Per-arm totals from recorded daily unit-metric observations, inside the
    experiment window. attach_rate arms count tickets; the others count unit-days."""
    start, end = _window(exp, ref)
    rows = [o for o in store.load("observations")
            if o.get("unit_id") in unit_ids and o.get("metric") == exp["metric"]
            and (o.get("item") or None) == (exp.get("item") or None)
            and start <= (o.get("date") or "") <= end]
    if exp["metric"] == "attach_rate":
        n = sum(int(o.get("n") or 0) for o in rows)
        x = sum(float(o.get("value") or 0) for o in rows)
        return {"kind": "proportion", "n": n, "x": x,
                "p": (x / n) if n else None, "days": len(rows)}
    vals = [float(o["value"]) for o in rows if o.get("value") is not None]
    n = len(vals)
    mean = (sum(vals) / n) if n else None
    var = sum((v - mean) ** 2 for v in vals) / (n - 1) if n > 1 else 0.0
    return {"kind": "mean", "n": n, "mean": mean, "sd": math.sqrt(var)}


CLEAR_Z, PROBABLE_Z = 2.6, 1.7

CONFIDENCE_READ = {
    "CLEAR": ("clear — a gap this size on this many observations is very unlikely to be "
              "luck (|z| ≥ 2.6)"),
    "PROBABLE": ("probable — likely real, but at this sample a gap this size still shows "
                 "up by luck now and then (1.7 ≤ |z| < 2.6)"),
    "NOISE": ("noise — a gap this small at this sample proves nothing; the honest call "
              "is no call"),
}


def verdict(exp, ref=None):
    """The verdict. Below the recorded floor the return LITERALLY has no winner,
    no lift, no direction and no z — not hidden ones, none: the early return
    fires before any lift arithmetic exists to leak. A fake 900% lift on 40
    tickets comes back exactly as TOO EARLY TO KNOW."""
    if isinstance(exp, str):
        exp = store.by_id("experiments", exp)
    if not exp:
        return {"error": "no such experiment"}
    t = _arm(exp, set(exp.get("treatment_units") or []), ref)
    c = _arm(exp, set(exp.get("control_units") or []), ref)
    floor = exp.get("min_sample") or dict(sample_floors()[exp["metric"]],
                                          _source=sample_floors()["_source"])
    need = int(floor["n"])
    base = {"experiment": exp["id"], "hypothesis": exp.get("hypothesis"),
            "metric": exp["metric"], "item": exp.get("item"), "status": exp.get("status"),
            "n_treatment": t["n"], "n_control": c["n"],
            "need": need, "floor_unit": floor.get("unit"),
            "floor_source": floor.get("_source")}
    if t["n"] < need or c["n"] < need:
        base["verdict"] = f"TOO EARLY TO KNOW (n={min(t['n'], c['n'])}, need {need})"
        base["why"] = ("below the recorded sample floor there is no winner, no lift and no "
                       "direction — by construction, not by policy; keep counting")
        return base
    # -- at or above the floor: the ONLY place lift arithmetic exists.
    if t["kind"] == "proportion":
        diff, baseline = t["p"] - c["p"], c["p"]
        pooled = (t["x"] + c["x"]) / (t["n"] + c["n"])
        se = math.sqrt(pooled * (1 - pooled) * (1 / t["n"] + 1 / c["n"])) \
            if 0 < pooled < 1 else 0.0
        method = "two-proportion z approximation (pooled) — deterministic, stated, stdlib"
    else:
        diff, baseline = t["mean"] - c["mean"], c["mean"]
        se = math.sqrt((t["sd"] ** 2) / t["n"] + (c["sd"] ** 2) / c["n"])
        method = "two-sample means z approximation (Welch-style) — deterministic, stated, stdlib"
    z = (diff / se) if se else (math.inf if diff else 0.0)
    az = abs(z)
    label = "CLEAR" if az >= CLEAR_Z else "PROBABLE" if az >= PROBABLE_Z else "NOISE"
    base.update({
        "verdict": label,
        "direction": ("treatment ahead" if diff > 0
                      else "treatment behind" if diff < 0 else "level"),
        "diff": round(diff, 4),
        "lift_pct": round(diff / baseline * 100, 1) if baseline else None,
        "z": round(z, 2) if math.isfinite(z) else None,
        "confidence_read": CONFIDENCE_READ[label],
        "method": method})
    return base


def conclude(exp_id, human="owner"):
    """Concluding freezes the verdict over the closed window. Below the floor
    there is nothing to conclude — refused, structurally: the verdict this
    function would freeze contains no winner to freeze."""
    exp = store.by_id("experiments", exp_id)
    if not exp:
        return {"error": "no such experiment"}
    if exp.get("status") == "concluded":
        return {"refused": "already concluded — the frozen verdict stands",
                "verdict": exp.get("verdict")}
    v = verdict(exp)
    if str(v.get("verdict", "")).startswith("TOO EARLY"):
        ev = store.log_event("refused", exp_id, "agent:desk", "R0",
                             {"action": "conclude_below_sample_floor",
                              "why": (f"{v['verdict']} — an early conclusion is the confident "
                                      f"fiction this desk exists to prevent")})
        return {"refused": f"cannot conclude: {v['verdict']}", "event": ev["id"]}
    exp["status"], exp["concluded_at"] = "concluded", iso()
    exp["verdict"] = verdict(exp)
    store.upsert("experiments", exp)
    store.log_event("conclude_experiment", exp_id, f"human:{human}", "R1",
                    {"verdict": exp["verdict"]["verdict"]})
    return {"concluded": True, "verdict": exp["verdict"]}


def rollout(exp_id):
    """A rollout recommendation drafts at R1 ONLY from a concluded CLEAR verdict
    with treatment ahead. From anything else there is no path — not a warning,
    not an override, a refusal."""
    exp = store.by_id("experiments", exp_id)
    if not exp:
        return {"error": "no such experiment"}
    if exp.get("status") != "concluded":
        live = verdict(exp)
        why = (f"no path — the experiment is still live (current read: {live['verdict']}); "
               f"a rollout drafts only from a concluded CLEAR verdict")
        ev = store.log_event("refused", exp_id, "agent:desk", "R0",
                             {"action": "rollout_unconcluded_experiment", "why": why})
        return {"refused": why, "event": ev["id"]}
    v = exp.get("verdict") or {}
    if v.get("verdict") != "CLEAR" or (v.get("diff") or 0) <= 0:
        why = (f"no path — concluded verdict is {v.get('verdict')} "
               f"({v.get('direction', 'no direction')}); rolling that out system-wide "
               f"institutionalizes luck")
        ev = store.log_event("refused", exp_id, "agent:desk", "R0",
                             {"action": "rollout_unconcluded_experiment", "why": why})
        return {"refused": why, "event": ev["id"]}
    r = gate.act("draft_rollout_recommendation", "desk", exp_id,
                 {"summary": (f"{exp['hypothesis'][:60]} — CLEAR, lift {v.get('lift_pct')}% "
                              f"(z={v.get('z')}, n={v.get('n_treatment')}/{v.get('n_control')})"),
                  "stats": v})
    return {"drafted": True, "stats_attached": v, "gate": r}


# ---------------------------------------------------------------- the counterfactual ledger

def _unit_name(unit_id):
    u = store.by_id("units", unit_id)
    return u["name"] if u else (unit_id or "?")


def price_stockout(ev):
    """cost = median recorded pace (this unit, this item, this daypart) ×
    duration × recorded price. No pace history → unmeasured: counted, never
    dollared. An 86 with no history priced anyway is just a made-up refund."""
    paces = [p.get("units_per_hour") for p in store.load("pace_history")
             if p.get("unit_id") == ev.get("unit_id") and p.get("item") == ev.get("item")
             and p.get("daypart") == ev.get("daypart")]
    if not paces:
        return unmeasured(
            f"no recorded sales pace for {ev.get('item')} at {_unit_name(ev.get('unit_id'))} "
            f"({ev.get('daypart')}) — counted, not dollared", field="cost")
    item = next((i for i in store.load("items") if i.get("name") == ev.get("item")), None)
    if not item or item.get("price") is None:
        return unmeasured(f"no recorded price for {ev.get('item')}", field="cost")
    pace = median(paces)
    dur = float(ev.get("duration_hours") or 0)
    cost = round(pace * dur * item["price"], 2)
    return {"cost": cost, "pace_units_per_hour": pace, "pace_n": len(paces),
            "basis": (f"median {pace} units/hr × {dur}h × ${item['price']} — this unit's own "
                      f"recorded pace ({len(paces)} readings), never an industry average")}


def eightysix_counted(days=7, ref=None):
    """What the 86 board cost you — counted from priced events only. Demo
    fixtures and paceless events never enter the dollar figure; paceless events
    are counted separately, not estimated."""
    ref = ref or now()
    dollared, priced, unpriced = 0.0, 0, 0
    for s in store.load("stockouts"):
        if s.get("demo_tag"):
            continue
        at = parse(s.get("at"))
        if not at or (ref - at).days > days:
            continue
        p = price_stockout(s)
        if p.get("cost") is None:
            unpriced += 1
        else:
            priced += 1
            dollared += p["cost"]
    return {"days": days, "dollared": round(dollared, 2), "priced": priced,
            "unmeasured": unpriced,
            "note": ("counted from the ledger — priced rows only; an event with no recorded "
                     "pace is counted, never dollared")}


def ledger_board(days=21, ref=None):
    ref = ref or now()
    rows = []
    for s in store.load("stockouts"):
        at = parse(s.get("at"))
        if not at or (ref - at).days > days:
            continue
        rows.append({**s, "unit": _unit_name(s.get("unit_id")), **price_stockout(s)})
    rows.sort(key=lambda r: r.get("at") or "", reverse=True)
    return {"rows": rows, "days": days, "week": eightysix_counted(7, ref)}


# ---------------------------------------------------------------- triage

# The illness rule is inherited from the Unit OS exactly: logged verbatim,
# NEVER answered in writing by software — an answer is an admission in a
# future lawsuit. Human + counsel path only.
ILLNESS = (
    r"\b(food poisoning|got (so |really )?sick|sick after (eating|dinner|lunch)|"
    r"vomit(ing|ed)?|throwing up|stomach (bug|cramps)|e\.? ?coli|salmonella|norovirus)\b",
    r"\bmade (me|us|him|her|them|my \w+) (so |really )?sick\b",
)
STOCKOUT = (
    r"\b(86'?d|86 ?ed|eighty.?six(ed)?)\b",
    r"\b(ran out of|out of stock|sold out|stocked out)\b",
)
GM_RESULT = (
    r"\b(who'?s|who is) winning\b",
    r"\bhow('?s| is) the [\w$ -]{0,24}(test|experiment)\b",
    r"\bresults?\b[^.?!]*\b(test|experiment)\b|\b(test|experiment)\b[^.?!]*\bresults?\b",
    r"\bcan we (call (it|the test)|conclude|roll (it |the winner )?out)\b",
)
PROPOSAL = (
    r"\b(let'?s|can we|could we|want to|we should) (try|test|run|pilot)\b",
    r"\ba/?b test\b",
    r"\btest(ing)?\b[^.?!]*\b(price|portion|menu|item|combo|bundle|discount)\b",
)


def read_message(text):
    """illness | stockout_report | gm_result_ask | experiment_proposal | human.
    The illness claim reads first — it gets NO written reply, that is the rule."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in ILLNESS:
        if re.search(rx, t):
            return {"label": "illness",
                    "why": "possible foodborne-illness claim — logged verbatim; software "
                           "answers nothing in writing; a human calls, with counsel on the "
                           "language"}
    for rx in STOCKOUT:
        if re.search(rx, t):
            return {"label": "stockout_report",
                    "why": "an 86/stockout report — onto the ledger, priced from the unit's "
                           "own recorded pace or counted unmeasured"}
    for rx in GM_RESULT:
        if re.search(rx, t):
            return {"label": "gm_result_ask",
                    "why": "a GM asking for results — the verdict is quoted verbatim; TOO "
                           "EARLY TO KNOW is a real answer"}
    for rx in PROPOSAL:
        if re.search(rx, t):
            return {"label": "experiment_proposal",
                    "why": "a proposed experiment — routed to the desk; one lever per dial "
                           "runs at creation"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- counted week

def week_counted(ref=None):
    """Counted from the records and the event log, never asserted."""
    ref = ref or now()

    def within(at, days=7):
        d = parse(at)
        return d is not None and (ref - d).days <= days

    gm_sent = sum(1 for e in store.events(kind="draft_gm_result_reply")
                  if str(e.get("actor", "")).startswith("human:") and within(e.get("at")))
    illness = sum(1 for e in store.events(kind="escalate_illness") if within(e.get("at")))
    rollouts = sum(1 for e in store.events(kind="queued_for_approval")
                   if (e.get("detail") or {}).get("action") == "draft_rollout_recommendation"
                   and within(e.get("at")))
    concluded = sum(1 for x in store.load("experiments") if within(x.get("concluded_at")))
    stockouts = sum(1 for s in store.load("stockouts")
                    if not s.get("demo_tag") and within(s.get("at")))
    return {"eightysix": eightysix_counted(7, ref), "stockouts_logged": stockouts,
            "experiments_concluded": concluded, "rollout_drafts": rollouts,
            "gm_replies_sent": gm_sent, "illness_escalated": illness,
            "note": "counted from the records and the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="illness",
                   costly_note=("AN ILLNESS CLAIM ANSWERED IN WRITING BY SOFTWARE IS AN "
                                "ADMISSION IN A FUTURE LAWSUIT. Over-routing a stockout "
                                "report costs a manager a read."))

EVAL_CASES = [
    {"input": "your tacos made me sick last night", "label": "illness"},
    {"input": "I got food poisoning from the brisket bowl", "label": "illness"},
    {"input": "whole office was throwing up after the catering order", "label": "illness"},
    {"input": "pretty sure the horchata gave me a stomach bug", "label": "illness"},
    {"input": "we 86'd the brisket at 6pm again", "label": "stockout_report"},
    {"input": "ran out of tortillas mid-dinner at riverside", "label": "stockout_report"},
    {"input": "campus sold out of the salsa flight by 7", "label": "stockout_report"},
    {"input": "who's winning the guac test", "label": "gm_result_ask"},
    {"input": "how's the bundle experiment doing, can we call it", "label": "gm_result_ask"},
    {"input": "any results on the menu board test yet", "label": "gm_result_ask"},
    {"input": "let's test $1 off bowls at elm street", "label": "experiment_proposal"},
    {"input": "can we try a bigger portion on the campus tacos", "label": "experiment_proposal"},
    {"input": "we should run a price test on horchata", "label": "experiment_proposal"},
    {"input": "", "label": "human"},
    {"input": "do you cater weddings?", "label": "human"},
    {"input": "what time does depot district close", "label": "human"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":        {"rung": "R3", "reason": "routing only; the illness hard stop is the point"},
    "escalate_illness":    {"rung": "R2", "reason": "act now, tell the human — an illness claim must not sit in a queue"},
    "log_stockout":        {"rung": "R2", "reason": "an internal ledger record — reversible, counted"},
    "create_experiment":   {"rung": "R2", "reason": "records an experiment the operators are running — the overlap refusal is the gate; nothing outward"},
    "conclude_experiment": {"rung": "R1", "reason": "freezing a verdict is a human call — and only at or above the recorded floor"},
    "draft_rollout_recommendation": {"rung": "R1", "reason": "money across every unit — a human approves, with the stats attached"},
    "draft_gm_result_reply": {"rung": "R1", "reason": "outward reply — a human sends"},
    "draft_desk_ack":      {"rung": "R1", "reason": "outward reply — a human sends"},
    "conclude_below_sample_floor": {"rung": "R0", "reason": "below the recorded floor the verdict enum has no winner — an early conclusion is confident fiction", "never_promote": True},
    "rollout_unconcluded_experiment": {"rung": "R0", "reason": "no path from anything but a concluded CLEAR verdict — rolling out noise institutionalizes luck", "never_promote": True},
    "overlapping_experiments_same_metric": {"rung": "R0", "reason": "one lever per dial — two live levers on one metric on one unit make both unreadable", "never_promote": True},
    "answer_illness_claim": {"rung": "R0", "reason": "an illness claim is logged verbatim and never answered in writing by software — no accidental admissions", "never_promote": True},
    "estimate_counterfactual_without_pace": {"rung": "R0", "reason": "no recorded pace, no dollar — an 86 with no history is counted, never priced", "never_promote": True},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def clear_lift_per_ticket():
    """Counted from concluded CLEAR avg_ticket experiments only — the frozen
    verdict's mean difference in dollars. No CLEAR conclusion → no number."""
    for e in store.load("experiments"):
        v = e.get("verdict") or {}
        if (e.get("status") == "concluded" and v.get("verdict") == "CLEAR"
                and e.get("metric") == "avg_ticket" and (v.get("diff") or 0) > 0):
            return round(v["diff"], 2)
    return None


def roi_model():
    return (Roi("Lab OS — what it computes to")
        .line("Winning-experiment lift", "revenue",
              "counted lift $/ticket (concluded CLEAR only) × your weekly tickets × 52",
              ["clear_lift_per_ticket", "weekly_tickets"],
              lambda g: float(g["clear_lift_per_ticket"]) * float(g["weekly_tickets"]) * 52,
              note="the $/ticket is counted from a concluded CLEAR experiment; the volume is your number")
        .line("86 board recovered", "revenue",
              "counted 86 cost (28d) × 13 × your recovery share",
              ["eightysix_cost_28d", "recovery_share"],
              lambda g: float(g["eightysix_cost_28d"]) * 13 * float(g["recovery_share"]),
              note="the cost is counted from priced events only — unmeasured rows are excluded, never estimated")
        .line("Owner analysis hours", "time_saved", "hrs/wk × 52 × rate",
              ["analysis_hours_wk", "owner_rate"],
              lambda g: float(g["analysis_hours_wk"]) * 52 * float(g["owner_rate"]))
        .line("The bad rollout avoided", "scenario",
              "you decide what a system-wide rollout of noise would have cost",
              ["bad_rollout_value"], lambda g: float(g["bad_rollout_value"]),
              assumption="never a saving — the rollout that didn't happen cannot be counted"))


def roi(given):
    rec = {}
    lift = clear_lift_per_ticket()
    if lift is not None:
        rec["clear_lift_per_ticket"] = lift
    rec["eightysix_cost_28d"] = eightysix_counted(days=28)["dollared"]
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "escalate_illness", "log_stockout", "create_experiment",
          "conclude_experiment", "draft_gm_result_reply", "draft_desk_ack",
          "draft_rollout_recommendation")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("guest:", "gm:"))
