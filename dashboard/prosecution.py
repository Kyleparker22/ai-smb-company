#!/usr/bin/env python3
"""Prosecution — HQ arguing against its own headline numbers.

Every dashboard is a persuasion surface for the figures it displays. None ships a prosecutor.
The Evidence door already proves yourco won't overstate a number it cannot defend; this proves
it will argue against a number it *can*.

The primitive exists: the CRM's `spread` runs two opposed readers over one evidence bundle, and
its prosecution counts only buyer-side action. This points the same idea at HQ's top line.

THE RULES THAT KEEP IT FROM BEING THEATRE
1. **Every charge is computed, never written.** A hard-coded pessimistic sentence is decoration.
   Each charge below derives from the same data the headline derives from, and if the data does
   not support the charge, the charge does not appear.
2. **A number with no case against it says so.** "No case to answer" is a real verdict and the
   most useful one — it means the figure survived an honest attempt to undermine it.
3. **It prosecutes, it does not sentence.** No charge concludes what to do. The point is to make
   the weakest joint visible, not to nag.
4. **It never invents a worse number.** The headline stays whatever it is; the charge is about
   what the headline *omits*.

Read-only. GET /api/prosecution.
"""
import os, sys, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

CRM = os.path.join(ROOT, "crm", "data.json")
STALE_TOUCH_DAYS = 21
BENCH = ("relationship", "parked", "prospect", "pre-convo")


def _load(p):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _age(iso, today):
    try:
        return (today - datetime.date.fromisoformat(str(iso)[:10])).days
    except (ValueError, TypeError):
        return None


def _pipeline_case(crm, today):
    """The headline everyone quotes. What does it omit?"""
    import server
    pipe = server.pipeline_summary(crm) or {}
    deals = [d for d in (crm.get("deals") or []) if server._in_motion(d)]
    value = pipe.get("value")
    if not deals:
        return None
    charges = []

    # never-touched and long-untouched are different facts and are reported as different facts;
    # the first version rendered a missing lastTouch as "Noned"
    never = [d for d in deals if not (d.get("lastTouch") or "").strip()]
    stale = [d for d in deals
             if (d.get("lastTouch") or "").strip()
             and (_age(d.get("lastTouch"), today) or 0) > STALE_TOUCH_DAYS]
    if never:
        charges.append({
            "charge": f"{len(never)} of {len(deals)} deals have never been touched at all",
            "detail": "; ".join(str(d.get("name")) for d in never[:4]),
            "why": "these are in the total and have never had a conversation"})
    if stale:
        charges.append({
            "charge": f"{len(stale)} of {len(deals)} deals have not been touched in "
                      f"{STALE_TOUCH_DAYS}+ days",
            "detail": "; ".join(f"{d.get('name')} ({_age(d.get('lastTouch'), today)}d ago)"
                                for d in stale[:4]),
            "why": "a pipeline number counts deals that exist, not deals that are moving"})

    no_next = [d for d in deals if not (d.get("nextAction") or "").strip()]
    if no_next:
        charges.append({
            "charge": f"{len(no_next)} of {len(deals)} have no next action recorded",
            "detail": "; ".join(str(d.get("name")) for d in no_next[:4]),
            "why": "a deal with no next action is a hope with a dollar value attached"})

    overdue = [d for d in deals
               if d.get("nextDate") and str(d["nextDate"])[:10] < today.isoformat()]
    if overdue:
        charges.append({
            "charge": f"{len(overdue)} have a next action whose date has passed",
            "detail": "; ".join(f"{d.get('name')} (due {str(d.get('nextDate'))[:10]})"
                                for d in overdue[:4]),
            "why": "the plan existed and the date went by"})

    return {
        "headline": "Pipeline value",
        "stated": f"${value:,.0f}" if isinstance(value, (int, float)) else str(value),
        "charges": charges,
        "verdict": ("no case to answer — every deal in motion is touched, actioned and on time"
                    if not charges else
                    f"{len(charges)} charge(s): the figure counts deals that exist, not deals "
                    f"that are moving"),
    }


def _goal_case(crm, today):
    """Goals show progress toward outputs. The case against: are any of them moving?"""
    import server
    cur = server.goals_currents(crm)
    charges = []
    zero = [k for k, v in cur.items() if not k.startswith("_") and v in (0, None)]
    if zero:
        charges.append({
            "charge": f"{len(zero)} of {len([k for k in cur if not k.startswith('_')])} goal "
                      f"metrics are zero or unmeasurable",
            "detail": ", ".join(sorted(zero)),
            "why": "a goal band mostly reading zero is a plan, not a measurement"})
    try:
        import wbr
        ib = wbr.inputs_block(today)
        if ib["allQuiet"]:
            charges.append({
                "charge": "every controllable input is zero across six weeks",
                "detail": "conversations, deliverables, companies touched, deals advanced",
                "why": "outputs cannot move if none of their inputs did"})
        else:
            dead = [r["label"] for r in ib["rows"] if r["thisWeek"] == 0]
            if dead:
                charges.append({
                    "charge": f"{len(dead)} controllable input(s) were zero this week",
                    "detail": ", ".join(dead),
                    "why": "the score is downstream of these, and these are the part that is "
                           "actually chooseable"})
    except Exception:
        pass
    return {"headline": "Goals", "stated": f"{len(cur) - 1} tracked metrics",
            "charges": charges,
            "verdict": "no case to answer" if not charges else
                       f"{len(charges)} charge(s): the band tracks outcomes nobody moved this week"}


def _agents_case(today):
    """'N agents live' is HQ's most-quoted internal number."""
    charges = []
    try:
        import vacancies
        ret = vacancies.build()["retire"]
        prop = [r for r in ret["rows"] if r["verdict"] == "propose retire"]
        watch = [r for r in ret["rows"] if r["verdict"] == "watch"]
        total = len(ret["rows"])
        if prop:
            charges.append({
                "charge": f"{len(prop)} of {total} agents have produced nothing in the "
                          f"evidence window",
                "detail": ", ".join(r["name"] for r in prop[:6]),
                "why": "'live' is a status somebody typed; production is a fact the repo records"})
        if watch:
            charges.append({
                "charge": f"{len(watch)} agent(s) have a loop armed that produces no artifact",
                "detail": ", ".join(r["name"] for r in watch),
                "why": "a scheduled loop with no output is a broken loop counted as coverage"})
    except Exception as e:
        return {"headline": "Agent roster", "stated": "unknown",
                "charges": [], "verdict": f"could not be prosecuted ({type(e).__name__})"}
    return {"headline": "Agent roster", "stated": f"{total} agents",
            "charges": charges,
            "verdict": "no case to answer" if not charges else
                       f"{len(charges)} charge(s): headcount is not output"}


def _loops_case(today):
    charges = []
    try:
        import refresh
        d = refresh.derive(today)
        ls = d.get("loopSummary") or {}
        stale = (ls.get("stale") or 0) + (ls.get("neverRan") or 0)
        tracked = ls.get("tracked") or 0
        if stale:
            charges.append({
                "charge": f"{stale} of {tracked} tracked loops are stale or have never run",
                "detail": ", ".join(l["loop"] for l in (d.get("loops") or [])
                                    if l.get("health") in ("stale", "never"))[:220],
                "why": "'always-on' describes the timers, not the artifacts"})
    except Exception as e:
        return {"headline": "Runtime", "stated": "unknown", "charges": [],
                "verdict": f"could not be prosecuted ({type(e).__name__})"}
    return {"headline": "Runtime", "stated": f"{tracked} tracked loops",
            "charges": charges,
            "verdict": "no case to answer" if not charges else
                       f"{len(charges)} charge(s): scheduled is not the same as running"}


def build(today=None):
    today = today or datetime.date.today()
    crm = _load(CRM) or {}
    cases = [c for c in (_pipeline_case(crm, today), _goal_case(crm, today),
                         _agents_case(today), _loops_case(today)) if c]
    total = sum(len(c["charges"]) for c in cases)
    clean = [c["headline"] for c in cases if not c["charges"]]
    return {
        "generatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "cases": cases,
        "totalCharges": total,
        "unchallenged": clean,
        "headline": (f"{total} charge(s) against {len(cases) - len(clean)} of {len(cases)} "
                     f"headline numbers" if total else
                     "no case to answer against any headline number"),
        "note": ("Every charge is computed from the same data as the number it challenges — a "
                 "hard-coded pessimistic sentence would be decoration. A figure with no case "
                 "against it reads 'no case to answer', which is the most useful verdict here: "
                 "it means the number survived an honest attempt to undermine it. This panel "
                 "prosecutes; it does not sentence, and it never invents a worse number."),
    }


if __name__ == "__main__":
    d = build()
    print("PROSECUTION — " + d["headline"] + "\n")
    for c in d["cases"]:
        print(f"  {c['headline']}: {c['stated']}")
        print(f"    verdict: {c['verdict']}")
        for ch in c["charges"]:
            print(f"      · {ch['charge']}")
            print(f"        {ch['detail'][:130]}")
            print(f"        ({ch['why']})")
        print()
