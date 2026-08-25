#!/usr/bin/env python3
"""yourco — the one number, and the number each agent owns.

WHY THIS EXISTS. On 2026-08-24 three unrelated inputs — the 9x9 Mandala grid's centre cell, OKR's
single Objective, and "Every Role Owns a Number" off an AI-native agency system map — arrived at the
same finding, and the WBR work had already reached it from a fourth direction:

    yourco had NINE goal metrics, which is zero goals,
    and TWENTY-SEVEN agents, none of which owned a number.

Both halves are fixed here, and they are one fix rather than two. A north star with nothing laddering
to it is a poster; per-agent numbers with no shared apex is a scoreboard for a game nobody named.

WHAT IT REFUSES TO DO
1. **It never stores a number.** Every value is computed per call from crm/data.json,
   finance/actuals.json or the loops/ artifacts. The registry stores the *definition*; this module
   does the arithmetic; nothing writes a result anywhere.
2. **It will not extrapolate from zero.** "At the current rate you reach the target on <date>" is the
   most useful sentence a north star can produce and the easiest one to fake. With no live clients
   there is no rate, and a projection off a rate of zero is a division, not a forecast — so it says
   so instead.
3. **Did-it-run is not an outcome.** Only Atlas may own loop liveness, because liveness IS its job.
   Every other agent whose only countable trace is "the loop fired" is reported as UNMEASURED with
   the one missing thing named, rather than dressed in an activity count. That is why 21 of 27 agents
   are honestly blank today, and why the blank list is the useful output of this file.

WHAT THE GAPS ACTUALLY ARE. The 21 unmeasured agents are not 21 problems. They cluster into five
root causes, and `blockers()` reports the clustering, because "seven agents are blocked by prose that
should be data" is an afternoon of work, while a list of 21 metrics is a project nobody starts.

Read-only. GET /api/northstar · CLI: python3 dashboard/northstar.py
"""
import os, sys, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))          # CODE
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
# Playground switch, same shape as dashboard/server.py: code stays under HERE, DATA moves. A module
# that resolved goals.json off HERE would read the sandbox and write live.
# Enforced by playground/check_isolation.py.
ROOT = os.environ.get("YOURCO_DATA_ROOT") or REPO           # DATA
DATA_DIR = os.path.join(ROOT, "dashboard") if os.environ.get("YOURCO_DATA_ROOT") else HERE

# The registry and the agents/ roster are CODE, not tenant data — the sandbox runs the real agents
# against synthetic customers, so it must see the real roster.
REGISTRY = os.path.join(REPO, "runtime", "agent-registry.json")
AGENTS_DIR = os.path.join(REPO, "agents")
ACTUALS = os.path.join(ROOT, "finance", "actuals.json")
GOALS = os.path.join(DATA_DIR, "goals.json")

# Trailing window for the flow metrics (companies touched, conversations held). A flow number with
# no window on it is meaningless, and the window is stated everywhere the number is.
WINDOW_DAYS = 28


def _load(p):
    try:
        with open(p) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


# ---- the metric implementations ------------------------------------------------------------
# Each returns (value, unit, note) or (None, unit, why-not). Adding a metric means adding it here
# AND naming its source in the registry's agent_metrics.sources — consistency-check.py enforces
# that the two agree, so a metric cannot claim a source that does not compute.

def _flow(key):
    """A CRM-activity input over the trailing window, via wbr.count_inputs — one implementation of
    'what happened this month', shared with the WBR door rather than re-derived."""
    import wbr
    end = datetime.date.today() + datetime.timedelta(days=1)
    start = end - datetime.timedelta(days=WINDOW_DAYS)
    counts = wbr.count_inputs(start, end)
    if key not in counts:
        return None, "", f"wbr.count_inputs has no key {key!r}"
    return counts[key], f"in the last {WINDOW_DAYS} days", None


def _goal(key):
    import server
    cur = server.goals_currents()
    if key not in cur:
        return None, "", f"goals_currents has no key {key!r}"
    v = cur[key]
    return v, "now", (None if v is not None else cur.get("_marginNote") or "not computable")


def _next_action_coverage():
    """Share of IN-MOTION deals carrying a next action. Bench deals are excluded deliberately: a
    relationship row with nothing scheduled is not a defect, and counting it would make the number
    move whenever the bench grows."""
    import server
    crm = _load(os.path.join(ROOT, "crm", "data.json")) or {}
    deals = [d for d in (crm.get("deals") or []) if server._in_motion(d)]
    if not deals:
        return None, "%", "no deals in motion — a percentage of nothing"
    have = sum(1 for d in deals if (d.get("nextAction") or "").strip())
    return round(have / len(deals) * 100), "%", f"{have} of {len(deals)} in motion"


def _connectors_onboarded():
    """Connectors who are provisioned and past the first training gate. Zero today, and a COMPUTED
    zero — the distinction matters, because an assumed zero cannot become a one by itself."""
    crm = _load(os.path.join(ROOT, "crm", "data.json")) or {}
    internal = [c for c in (crm.get("contacts") or []) if c.get("kind") == "internal"]
    pool = [c for c in internal if c.get("teamRole") == "connector"]
    on = sum(1 for c in pool if c.get("teamStatus") == "active")
    return on, "onboarded", f"{len(pool)} tagged as connectors, {on} active"


def _loop_liveness():
    """Share of sanctioned, timer-backed loops whose latest artifact is inside twice its cadence.
    Cadences, folder->timer aliases and the archive exceptions all come from dashboard/board.py —
    one definition of 'is this loop alive', not two that can disagree."""
    import board
    loops_dir = os.path.join(ROOT, "loops")
    try:
        names = sorted(os.listdir(loops_dir))
    except OSError:
        return None, "%", "loops/ unreadable"
    reg = _load(REGISTRY) or {}
    import re as _re
    sanctioned = {_re.sub(r"^yourco-|\.timer$", "", t) for t in (reg.get("sanctioned_timers") or [])}
    tracked, fresh = 0, 0
    for n in names:
        if n in board.SKIP_DIRS or not os.path.isdir(os.path.join(loops_dir, n)):
            continue
        timer = board.DIR_TO_TIMER.get(n, n.lstrip("_"))
        if timer not in sanctioned:
            continue
        stem, _ = board._latest_report("loops/" + n)
        tracked += 1
        if stem is None:
            continue
        age = board._age(stem)
        if age is not None and age <= board._cadence_for(n) * 2:
            fresh += 1
    if not tracked:
        return None, "%", "no sanctioned timer-backed loop folders found"
    return round(fresh / tracked * 100), "%", f"{fresh} of {tracked} sanctioned loops inside cadence"


def _runway_months():
    a = _load(ACTUALS) or {}
    cash = (a.get("cash") or {}).get("onHand")
    burn = (a.get("burn") or {}).get("monthlyFixed")
    if cash is None or burn is None:
        return None, "months", "finance/actuals.json is missing cash or burn"
    if not burn:
        return None, "months", "burn is zero — runway is undefined, not infinite"
    conf = (a.get("burn") or {}).get("confidence")
    return round(cash / burn, 1), "months", f"${cash:,.0f} / ${burn:,.2f}/mo (burn: {conf})"


METRICS = {
    "conversationsHeld": lambda: _flow("conversationsHeld"),
    "companiesTouched": lambda: _flow("companiesTouched"),
    "activeConnectors": lambda: _goal("activeConnectors"),
    "nextActionCoverage": _next_action_coverage,
    "connectorsOnboarded": _connectors_onboarded,
    "loopLiveness": _loop_liveness,
    "runwayMonths": _runway_months,
}
# The seven that existed only as prose (2026-08-25) — three derived from files that already
# existed, four read back out of SOP-mandated structures in the artifact each loop already writes.
# Kept in their own module because their failure mode is different: a heading can be renamed, and
# every one of them reports a parse failure as a parse failure rather than as a zero.
# How each number is arrived at, shown on HQ beside the value. The seven implemented directly above
# carry theirs here; the later modules ship their own. Every row must have one — a reader looking at
# a number deserves to know whether it was computed from live records, derived from files that
# already existed, or read back out of an artifact a run wrote, because those fail differently.
MECHANISM = {
    "conversationsHeld": "crm",
    "companiesTouched": "crm",
    "activeConnectors": "crm",
    "nextActionCoverage": "crm",
    "connectorsOnboarded": "crm",
    "loopLiveness": "derived",       # loops/ artifacts vs the sanctioned timers — no run required
    "runwayMonths": "finance",
}
try:
    import loop_metrics
    METRICS.update(loop_metrics.METRICS)
    MECHANISM.update(loop_metrics.MECHANISM)
except Exception:                       # a broken extractor must not blank the whole board
    loop_metrics = None
# The five that needed the CRM to record something it never had (2026-08-25) — a controlled channel
# vocabulary, an `Audit delivered` activity type, and a `collateral` artifact type. Three of the
# five were re-diagnosed on the way: Jim's and Sadie's numbers already existed, and Katie's real
# blocker is the launch-gate rather than the schema.
try:
    import crm_metrics
    METRICS.update(crm_metrics.METRICS)
    MECHANISM.update(crm_metrics.MECHANISM)
except Exception:
    crm_metrics = None
# The six waiting on client #1 (2026-08-25). No amount of building produces a customer, so the
# question was whether these would compute WHEN one lands — and for three of the six the answer was
# no: the stage clock was being overwritten, two were scoped to whether the founder closes, and one
# needed no customer at all.
try:
    import client_metrics
    METRICS.update(client_metrics.METRICS)
    MECHANISM.update(client_metrics.MECHANISM)
except Exception:
    client_metrics = None
# Runtime availability (2026-08-25) — the last unmeasured metric that was nobody else's blocker.
# A log cannot record an outage, so this is computed from beats that never arrived.
try:
    import uptime as uptime_view
    METRICS.update(uptime_view.METRICS)
    MECHANISM.update(uptime_view.MECHANISM)
except Exception:
    uptime_view = None
# The last two, both behind the launch-gate (2026-08-25). A gate is not something a metric can fix
# — but the first campaign and the first bookings would have arrived unattributed, and that is.
try:
    import gate_metrics
    METRICS.update(gate_metrics.METRICS)
    MECHANISM.update(gate_metrics.MECHANISM)
except Exception:
    gate_metrics = None


# ---- the north star -------------------------------------------------------------------------
def north_star():
    """The one number, its target, and an explicit refusal to project from a standing start."""
    import server
    goals = _load(GOALS) or {}
    ns = goals.get("northstar") if isinstance(goals.get("northstar"), dict) else {}
    key = ns.get("metric")
    if not key:
        return {"declared": False,
                "refusal": "No north star is declared. Set goals.json -> northstar.metric — it is "
                           "the Founder's to set and nothing else in the OS may set it."}
    payload = server.goals_payload()
    per = payload.get("period") or {}
    cur = (payload.get("current") or {}).get(key)
    qt = ((payload.get("quarters") or {}).get(per.get("quarter")) or {}).get("targets", {}).get(key)
    yt = ((payload.get("year") or {}).get("targets") or {}).get(key)

    # The projection, and the reason there isn't one. A rate of zero does not extrapolate; saying
    # "on track" or "12 months away" off no movement at all is the exact failure this refuses.
    proj = None
    if not cur:
        proj = {"value": None,
                "refusal": f"{key} is at {cur if cur is not None else 'unknown'} — there is no rate "
                           f"to project from. A date derived from zero movement is arithmetic, not "
                           f"a forecast."}
    elif qt:
        proj = {"value": None,
                "refusal": "Projection needs a history of this metric moving. One data point is a "
                           "position, not a trend — see the 6-12 series on WBR."}
    return {
        "declared": True,
        "metric": key,
        "label": {"liveClients": "Live clients", "mrr": "MRR"}.get(key, key),
        "current": cur,
        "targetQuarter": qt, "quarterLabel": per.get("quarterLabel"),
        "targetYear": yt, "yearLabel": per.get("yearLabel"),
        "quarterPctElapsed": per.get("quarterPctElapsed"),
        "yearPctElapsed": per.get("yearPctElapsed"),
        "gapQuarter": (qt - cur) if (qt is not None and cur is not None) else None,
        "projection": proj,
        "why": ns.get("why"), "setBy": ns.get("setBy"), "setOn": ns.get("setOn"),
        "supporting": ns.get("supporting") or [],
        "changeRule": ns.get("changeRule"),
    }


# ---- the ladder ------------------------------------------------------------------------------
def _registry_block():
    reg = _load(REGISTRY) or {}
    return reg.get("agent_metrics") if isinstance(reg.get("agent_metrics"), dict) else {}


def owners():
    """Every agent (and the Founder), the number it owns, and the number itself where one can be computed.

    An entry is one of exactly two states. `computed` carries a value the OS derived just now.
    `unmeasured` carries no value and MUST carry `needs` — the single missing thing — because a
    metric with no value and no named gap is a wish."""
    blk = _registry_block()
    rows = []
    for who, spec, kind in ([(k, v, "human") for k, v in (blk.get("humans") or {}).items()] +
                            [(k, v, "agent") for k, v in (blk.get("agents") or {}).items()]):
        row = {"who": who, "kind": kind, "owns": spec.get("owns"), "label": spec.get("label"),
               "ladders": spec.get("ladders"), "why": spec.get("why"),
               "source": spec.get("source"), "state": "unmeasured",
               "mechanism": MECHANISM.get(spec.get("owns")),
               "value": None, "unit": None, "note": None,
               "needs": spec.get("needs"), "blockedBy": spec.get("blockedBy")}
        fn = METRICS.get(spec.get("owns")) if spec.get("source") != "unmeasured" else None
        if spec.get("source") != "unmeasured" and fn is None:
            row["note"] = (f"declares source {spec.get('source')!r} but northstar.METRICS has no "
                           f"implementation for {spec.get('owns')!r}")
        elif fn is not None:
            try:
                v, unit, note = fn()
            except Exception as e:                      # a broken source reports itself, never a 0
                v, unit, note = None, None, f"source failed: {type(e).__name__}: {e}"
            # THREE states, not two. `awaiting` means a real source is declared and implemented
            # and returned nothing — either the input has not been produced yet or its format
            # moved. Both mean "wired but not readable right now", which is a different fact from
            # "nothing is wired at all", and collapsing them would hide every broken extractor
            # inside the same blank as the metrics nobody has built.
            row.update(value=v, unit=unit, note=note,
                       state="computed" if v is not None else "awaiting")
            if v is None and not row["needs"]:
                row["needs"] = note
        rows.append(row)
    return rows


def blockers(rows=None):
    """The 21 gaps, clustered by root cause. This is the actionable half of the file: seven agents
    blocked by a loop that writes prose instead of a number is one afternoon; a list of 21 metrics
    is a project nobody starts."""
    rows = rows if rows is not None else owners()
    CAUSE = {
        "awaiting-first-reading": "Wired and readable — the number appears the next time the loop "
                                  "that produces it runs. Nothing to build.",
        "awaiting-first-event": "The instrument exists and the business event has not happened yet. "
                                "Nothing to build and nothing to wait on but the work itself.",
        "extractor-broken": "A source IS declared and implemented and returned nothing. Either the "
                            "artifact's format moved or the run never wrote it — the note says "
                            "which. This is the one cluster that is a defect rather than a gap.",
        "no-client-yet": "Waiting on client #1. Nothing to build — these compute themselves the day "
                         "a deal goes live, which is the whole point of defining them now.",
        "prose-not-data": "The loop already produces the number and writes it into a memo. Each is "
                          "one line of JSON alongside the artifact it already generates.",
        "missing-crm-field": "One field or one activity type short. Cheapest fixes on the list.",
        "launch-gate": "Blocked by the launch gate, not by engineering — nothing to measure until "
                        "the thing is allowed to run.",
        "no-monitoring": "Nothing measures it at all. Same gap the client SLA has.",
        "awaiting-host-install": "Built, committed and unrunnable from here — the unit has to be "
                                 "enabled on the VPS, which is the Founder's hand. Nothing to build.",
    }
    out = {}
    for r in rows:
        if r["state"] == "computed":
            continue
        # An `awaiting` row that never declared a gap is an extractor that broke, not a plan.
        k = (r.get("blockedBy") or ("extractor-broken" if r["state"] == "awaiting"
                                    else "unclassified"))
        b = out.setdefault(k, {"cause": k, "meaning": CAUSE.get(k, "unclassified"),
                               "agents": [], "count": 0})
        b["agents"].append({"who": r["who"], "metric": r["label"], "needs": r["needs"]})
        b["count"] += 1
    return sorted(out.values(), key=lambda b: -b["count"])


def coverage(rows=None):
    rows = rows if rows is not None else owners()
    agents = [r for r in rows if r["kind"] == "agent"]
    try:
        on_disk = sorted(n for n in os.listdir(AGENTS_DIR)
                         if os.path.isdir(os.path.join(AGENTS_DIR, n)) and not n.startswith("_"))
    except OSError:
        on_disk = []
    named = {r["who"] for r in agents}
    return {
        "agents": len(agents),
        "agentFolders": len(on_disk),
        "missing": sorted(set(on_disk) - named),      # an agent nobody assigned a number to
        "orphan": sorted(named - set(on_disk)),       # a number assigned to an agent that is gone
        "computed": sum(1 for r in agents if r["state"] == "computed"),
        "awaiting": sum(1 for r in agents if r["state"] == "awaiting"),
        "unmeasured": sum(1 for r in agents if r["state"] == "unmeasured"),
        "direct": sum(1 for r in agents if r["ladders"] == "direct"),
        "enabling": sum(1 for r in agents if r["ladders"] == "enabling"),
    }


def build():
    rows = owners()
    return {
        "generated": datetime.datetime.now().isoformat(timespec="seconds"),
        "northStar": north_star(),
        "owners": rows,
        "blockers": blockers(rows),
        "coverage": coverage(rows),
        "windowDays": WINDOW_DAYS,
        "note": ("Definitions live in runtime/agent-registry.json -> agent_metrics (Rafi's sanctioned "
                 "baseline, so a number an agent owns cannot be quietly changed). The north star "
                 "lives in dashboard/goals.json -> northstar (the Founder's). Values are computed here, per "
                 "call, and stored nowhere."),
    }


def main():
    p = build()
    ns = p["northStar"]
    print("\n=== THE ONE NUMBER =====================================================")
    if not ns.get("declared"):
        print("  " + ns["refusal"])
    else:
        print(f"  {ns['label']}: {ns['current']}   target {ns['targetQuarter']} "
              f"({ns['quarterLabel']}, {ns['quarterPctElapsed']}% elapsed) · "
              f"{ns['targetYear']} ({ns['yearLabel']})")
        if ns.get("projection") and ns["projection"].get("refusal"):
            print("  projection: " + ns["projection"]["refusal"])
    c = p["coverage"]
    print(f"\n=== WHO OWNS WHAT ({c['computed']} computed · {c['awaiting']} awaiting · "
          f"{c['unmeasured']} unmeasured · {c['direct']} direct · {c['enabling']} enabling) ===")
    for r in p["owners"]:
        val = (f"{r['value']}{'%' if r['unit'] == '%' else ''}" if r["state"] == "computed" else "—")
        print(f"  {r['who']:<10} {r['label'][:44]:<45} {val:>8}  "
              f"{'' if r['state'] == 'computed' else '(' + (r.get('blockedBy') or '?') + ')'}")
    print("\n=== WHY THE BLANKS ARE BLANK ===========================================")
    for b in p["blockers"]:
        print(f"  {b['count']:>2}  {b['cause']:<18} {b['meaning']}")
        for a in b["agents"]:
            print(f"        · {a['who']}: {a['needs']}")
    if c["missing"]:
        print("\n  !! agents with no number assigned: " + ", ".join(c["missing"]))
    if c["orphan"]:
        print("  !! numbers assigned to agents that no longer exist: " + ", ".join(c["orphan"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
