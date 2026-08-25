#!/usr/bin/env python3
"""Agent payroll — every agent gets a cost line, and the rung gets a budget.

THE GAP THIS CLOSES.  Every yourco agent has an owner, a rung, a Slack channel, and (since
2026-08-13) a review date. **None has a cost.** "yourco absorbs the model spend" is the business
model, and the OS could already bill a *client* (`runtime/session_tokens.py`, `clients/*/cost.md`)
while being unable to answer "what does Mario cost per month, and what did he produce?" So
`dashboard/vacancies.py` proposes retiring an agent on the grounds that it produced nothing —
with no idea whether that costs $0.02/month or $40.

It also supplies the eighth of Atomicwork's eight agent-governance dimensions — identity, access,
skills, budget, performance, lifecycle, governance, collaboration. yourco had seven. **Budget** is
the missing one, and it is the one control class the R2/R3 "no-human" stack in
`processes/autonomy-matrix.md` never had: eval gate, guardrails, watchdog, rollback, kill switch —
no spend cap.

WHERE THE MONEY DATA COMES FROM, and what it honestly cannot say:

  loops/_agentops/runs.jsonl   per-RUN cost from `claude -p --output-format json`. Ground truth.
                               Written by runtime/run_journal.py from runtime/run-loop.sh. Starts EMPTY —
                               historical JSON went to gitignored host-local logs and is gone.
  loops/_anthropic/latest.json DAILY API TOTALS ONLY. It is the envelope, never the breakdown:
                               a day's total cannot be divided among agents without inventing
                               percentages, so this file is used to compute what is UNATTRIBUTED
                               and for nothing else.
  runtime/session_tokens.py    the Founder's Claude Code sessions. Deliberately EXCLUDED — that is the
                               founder building, not an agent running, and merging the two would
                               make every agent look expensive in exactly the month the Founder built a lot.

FIVE HONESTY RULES (tests in runtime/test_agentops.py):

1. **Never split the daily total.**  Attributed and unattributed are reported side by side and
   never summed into a per-agent figure. Same stance as session_tokens' attributed/shared/
   unattributed split, for the same reason.
2. **An agent with no priced run costs `unpriced`, not $0.**  A $0 line reads as free.
3. **A budget here REPORTS; it does not enforce.**  Nothing in this file can stop a run mid-flight
   — the cap fires on the *next* read. Calling it enforcement would be a fake control, and a fake
   control is worse than a missing one because it stops anyone from building the real one.
4. **Cost-per-artifact is refused unless both sides are real.**  No priced runs, or no artifacts,
   → the ratio is `None` with the reason, never a divide-by-something-small.
5. **A silent agent is reported as silent even when it is cheap.**  Cheap and useless is still
   useless; the cost column exists to make `retire` quantitative, not to excuse dormancy.

CLI
  python3 runtime/agent_payroll.py                 # the payroll, 30d
  python3 runtime/agent_payroll.py --days 7 --json
  python3 runtime/agent_payroll.py --budgets       # caps, breaches, and what has no cap
"""
import os, re, sys, json, argparse, datetime

CODE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("YOURCO_DATA_ROOT") or os.path.dirname(CODE)
sys.path.insert(0, CODE)
from ledger import Ledger  # noqa: E402
import run_journal  # noqa: E402

RUNS = "loops/_agentops/runs.jsonl"
REGISTRY = os.path.join(CODE, "agent-registry.json")
ANTHROPIC = os.path.join(ROOT, "loops", "_anthropic", "latest.json")
LOOPS_DIR = os.path.join(ROOT, "loops")
PROMPTS = os.path.join(CODE, "prompts")

DEFAULT_DAYS = 30
DATED = re.compile(r"^(\d{4}-\d{2}-\d{2})")


def _registry():
    try:
        return json.load(open(REGISTRY, encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def budgets():
    """Per-agent monthly USD caps, from the registry (Rafi-owned, so the governance watchdog
    sees a cap change as drift — a budget nobody can change silently)."""
    return _registry().get("agent_budgets", {}) or {}


def loop_agents():
    """Every sanctioned loop -> its agent, parsed from the prompt's own first line."""
    out = {}
    for fn in _registry().get("sanctioned_prompts", []):
        loop = fn[:-3] if fn.endswith(".md") else fn
        if loop.startswith("_"):
            continue
        out[loop] = run_journal.agent_for(loop)
    return out


def artifacts(loop, since, root=LOOPS_DIR):
    """Dated artifacts a loop produced in the window — the OUTPUT side of the ledger."""
    d = os.path.join(root, loop)
    if not os.path.isdir(d):
        return {"count": 0, "last": None, "dir_exists": False}
    dates = []
    for fn in os.listdir(d):
        m = DATED.match(fn)
        if m:
            try:
                dates.append(datetime.date.fromisoformat(m.group(1)))
            except ValueError:
                pass
    return {"count": sum(1 for x in dates if x >= since),
            "last": max(dates).isoformat() if dates else None, "dir_exists": True}


def build(days=DEFAULT_DAYS, today=None):
    today = today or datetime.date.today()
    since = today - datetime.timedelta(days=days)
    raw = Ledger(RUNS).project()
    runs = [e for e in raw["events"] if e.get("kind") == "run"
            and (e.get("ts") or "")[:10] >= since.isoformat()]

    per_loop = {}
    for r in runs:
        b = per_loop.setdefault(r.get("loop") or "(unknown)",
                                {"runs": 0, "errors": 0, "cost": 0.0, "priced": 0, "unpriced": 0})
        b["runs"] += 1
        b["errors"] += 1 if r.get("status") != "ok" else 0
        if isinstance(r.get("cost_usd"), (int, float)):
            b["cost"] += r["cost_usd"]; b["priced"] += 1
        else:
            b["unpriced"] += 1

    caps, la = budgets(), loop_agents()
    per_agent = {}
    for loop, agent in sorted(la.items()):
        key = agent or "(unmapped)"
        a = per_agent.setdefault(key, {"agent": key, "loops": [], "runs": 0, "errors": 0,
                                       "cost_usd": 0.0, "priced_runs": 0, "unpriced_runs": 0,
                                       "artifacts": 0, "last_output": None})
        a["loops"].append(loop)
        m = per_loop.get(loop)
        if m:
            a["runs"] += m["runs"]; a["errors"] += m["errors"]
            a["cost_usd"] += m["cost"]; a["priced_runs"] += m["priced"]
            a["unpriced_runs"] += m["unpriced"]
        art = artifacts(loop, since)
        a["artifacts"] += art["count"]
        if art["last"] and (a["last_output"] is None or art["last"] > a["last_output"]):
            a["last_output"] = art["last"]

    rows = []
    for a in per_agent.values():
        a["cost_usd"] = round(a["cost_usd"], 4)
        cap = caps.get(a["agent"])
        # Rule 4: the ratio is refused unless BOTH sides are real.
        if not a["priced_runs"]:
            cpa, cpa_why = None, "no priced run in the window"
        elif not a["artifacts"]:
            cpa, cpa_why = None, "no artifact in the window — a cost per nothing is not a rate"
        else:
            cpa, cpa_why = round(a["cost_usd"] / a["artifacts"], 4), None
        if not a["priced_runs"]:
            verdict = "unpriced"                       # rule 2 — never $0
        elif cap and a["cost_usd"] > cap:
            verdict = "over-budget"
        elif not cap:
            verdict = "no-budget"
        else:
            verdict = "within"
        rows.append({**a, "budget_usd": cap,
                     "pct_of_budget": round(100 * a["cost_usd"] / cap, 1) if cap else None,
                     "cost_per_artifact": cpa, "cost_per_artifact_refused": cpa_why,
                     "verdict": verdict,
                     # Rule 5: silence is reported regardless of price.
                     "silent": a["artifacts"] == 0})
    rows.sort(key=lambda r: (-r["cost_usd"], r["agent"]))

    # Rule 1: the envelope, never the divisor.
    env, env_note = None, None
    try:
        ant = json.load(open(ANTHROPIC, encoding="utf-8"))
        env = ant.get("cost30d") if days >= 30 else ant.get("cost7d")
        if env is not None and days not in (7, 30):
            env_note = f"envelope is the {30 if days >= 30 else 7}d API total; window is {days}d — not comparable"
    except (OSError, ValueError) as e:
        env_note = f"API total unavailable ({type(e).__name__})"
    attributed = round(sum(r["cost_usd"] for r in rows), 4)

    return {
        "window_days": days, "since": since.isoformat(),
        "agents": rows,
        "attributed_usd": attributed,
        "api_envelope_usd": env,
        "unattributed_usd": (round(env - attributed, 4) if isinstance(env, (int, float))
                             and env_note is None else None),
        "envelope_note": env_note,
        "store_exists": raw["exists"], "bad_lines": raw["bad"],
        "no_data_reason": (None if runs else
                           "No runs recorded yet. runtime/run-loop.sh writes to the journal from its next "
                           "firing; nothing before that can be backfilled (host-local gitignored logs). "
                           "Until then every agent reads `unpriced` — which is the honest state, "
                           "not a zero."),
        "enforcement": ("REPORTING ONLY. A cap here fires on the next read; it cannot stop a run "
                        "in flight. Enforcement would need a pre-flight check inside runtime/run-loop.sh."),
        "excluded": "the Founder's Claude Code sessions (runtime/session_tokens.py) — founder building, not agent running.",
    }


def render(p):
    out = [f"Agent payroll — last {p['window_days']}d (since {p['since']})", ""]
    if p["no_data_reason"]:
        out += ["  " + p["no_data_reason"], ""]
    out.append(f"  {'agent':<12}{'runs':>5}{'cost':>10}{'budget':>9}{'arts':>6}  verdict")
    for r in p["agents"]:
        cost = f"${r['cost_usd']:.2f}" if r["priced_runs"] else "—"
        bud = f"${r['budget_usd']:.0f}" if r["budget_usd"] else "—"
        flag = "  ⚠ silent" if r["silent"] else ""
        out.append(f"  {r['agent']:<12}{r['runs']:>5}{cost:>10}{bud:>9}{r['artifacts']:>6}  "
                   f"{r['verdict']}{flag}")
    out += ["", f"  attributed: ${p['attributed_usd']:.2f}"]
    if isinstance(p["api_envelope_usd"], (int, float)):
        out.append(f"  API total (the envelope, never divided): ${p['api_envelope_usd']:.2f}")
        if p["unattributed_usd"] is not None:
            out.append(f"  unattributed: ${p['unattributed_usd']:.2f}  "
                       f"— reported, never split across agents by invented percentages")
    if p["envelope_note"]:
        out.append(f"  ⚠ {p['envelope_note']}")
    out += ["", "  " + p["enforcement"], "  Excluded: " + p["excluded"]]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Agent payroll — per-agent cost and budget.")
    ap.add_argument("--days", type=int, default=DEFAULT_DAYS)
    ap.add_argument("--budgets", action="store_true", help="caps, breaches, and what has no cap")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    p = build(a.days)
    if a.json:
        print(json.dumps(p, indent=2)); return
    if a.budgets:
        caps = budgets()
        print(f"Budgets (runtime/agent-registry.json §agent_budgets) — {len(caps)} set\n")
        for r in p["agents"]:
            if r["budget_usd"]:
                print(f"  {r['agent']:<12} ${r['cost_usd']:>7.2f} / ${r['budget_usd']:<6.0f} "
                      f"({r['pct_of_budget']}%)  {r['verdict']}")
            else:
                print(f"  {r['agent']:<12} no cap set")
        print("\n  " + p["enforcement"])
        return
    print(render(p))


if __name__ == "__main__":
    main()
