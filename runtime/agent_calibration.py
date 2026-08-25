#!/usr/bin/env python3
"""Calibration-gated autonomy — promote on how right an agent is about being right.

THE HOLE IN THE STREAK RULE.  `processes/autonomy-matrix.md` promotes an action after N
consecutive clean evals with real uses. That is a good rule and it cannot distinguish the two
cases that matter most:

    an agent that is reliable                  ->  clean streak
    an agent that has been lucky               ->  clean streak

Four clean weeks from an agent with no idea when it is out of its depth is exactly the profile
that produces the first bad unattended send — the incident `processes/autonomy-matrix.md` calls
the moat-killer. Calibration separates them: an agent that says "70% confident" and is right about
70% of the time knows the shape of its own competence; one that says 95% and is right 60% of the
time does not, however clean its streak looks.

So: **a promotion needs BOTH.** Streak (did it work?) AND calibration (did it know?). This module
computes the second and refuses to answer when it cannot.

WHAT IT REUSES, DELIBERATELY.  `dashboard/trust.py` already computes per-agent Brier scores from
`loops/_trust/forecasts.jsonl`, and already audits Kolby's hand-written streak table against
recorded actions. Both are imported, never re-derived — a second definition of "how calibrated is
this agent" that could disagree with HQ is exactly the drift `CLAUDE.md` §change-one-sweep-all
exists to stop.

THE THRESHOLDS ARE STARTING VALUES, AND SAY SO.  MAX_BRIER and OVERCONFIDENCE_TOLERANCE below are
chosen by analogy to the streak rule's default thresholds. They are **not** derived from yourco
data, because yourco has no resolved forecasts yet. Every output that uses them says so. The owner
(the Founder) sets and may raise them, exactly as with the streak thresholds.

FOUR HONESTY RULES (tests in runtime/test_agentops.py):

1. **Below the sample floor there is no score, and therefore no gate decision.**  The verdict is
   `insufficient-evidence` — never a default PASS, and never a default FAIL either. Both would be
   inventing a fact. It reports what is missing and how many more resolutions would answer it.
2. **Overconfidence is tested separately from Brier.**  A good aggregate Brier can hide a badly
   miscalibrated top band, and the top band is where autonomy decisions get made. An agent whose
   ≥80% claims come true materially less often than claimed is HELD regardless of its Brier.
3. **This module recommends; it never promotes.**  Promotion is the owner acting on a full ledger
   — the rule already written into the autonomy matrix. There is no `--promote`.
4. **A clean streak with no calibration evidence is reported as exactly that.**  Not as a pass.
   The whole point is that the streak alone was never sufficient.

CLI
  python3 runtime/agent_calibration.py                       # per-agent calibration standing
  python3 runtime/agent_calibration.py --gate "Gmail send (Jim, external)" --agent jim
  python3 runtime/agent_calibration.py --json
"""
import os, sys, json, argparse

CODE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("YOURCO_DATA_ROOT") or os.path.dirname(CODE)
sys.path.insert(0, CODE)
sys.path.insert(0, os.path.join(os.path.dirname(CODE), "dashboard"))
from ledger import MIN_FORECASTS, calibration_bins, refuse_reason  # noqa: E402

# Starting values, by analogy to the streak defaults — NOT derived from yourco data (see above).
MAX_BRIER = 0.15                 # 0.25 is a coin flip stated at 50%; 0.15 is meaningfully better
OVERCONFIDENCE_TOLERANCE = 0.15  # top-band claimed minus actual, above which the agent is HELD
TOP_BAND = 0.8


def _trust():
    import trust  # dashboard/trust.py — the single definition of calibration + streaks
    return trust


def per_agent():
    """Per-agent calibration standing, reusing dashboard/trust.py's computation verbatim."""
    t = _trust()
    cal = t._calibration()
    pairs_by_agent = {}
    # Rebuild the (p, outcome) pairs per agent so the top-band test can run. Same source rows
    # trust.py used; we are re-grouping them, not recomputing the score.
    raw = t.FORECASTS.project()["events"]
    fc = {e["seq"]: e for e in raw if e.get("kind") == "forecast"}
    for r in raw:
        if r.get("kind") != "resolution":
            continue
        f = fc.get(r.get("forecast"))
        if not f:
            continue
        pairs_by_agent.setdefault(f.get("agent") or "unattributed", []).append(
            (f.get("p"), r.get("outcome") == "clean"))

    rows = []
    for a in cal["byAgent"]:
        name = a["agent"]
        pairs = [(p, o) for p, o in pairs_by_agent.get(name, [])
                 if isinstance(p, (int, float)) and not isinstance(p, bool)]
        top = [(p, o) for p, o in pairs if p >= TOP_BAND]
        claimed = round(sum(p for p, _ in top) / len(top), 3) if top else None
        actual = round(sum(1 for _, o in top if o) / len(top), 3) if top else None
        over = (claimed is not None and actual is not None
                and (claimed - actual) > OVERCONFIDENCE_TOLERANCE)
        rows.append({
            "agent": name, "n": a["n"], "brier": a["brier"], "refusal": a["refusal"],
            "bins": calibration_bins(pairs),
            "top_band": {"n": len(top), "claimed": claimed, "actual": actual,
                         "overconfident": over,
                         "note": None if top else
                         f"no resolved forecast at ≥{int(TOP_BAND*100)}% confidence — the band "
                         f"autonomy decisions are made in is untested for this agent"},
        })
    return {"agents": rows, "floor": MIN_FORECASTS, "resolved_total": cal["resolved"],
            "open_total": cal["open"],
            "thresholds": {"max_brier": MAX_BRIER, "overconfidence_tolerance":
                           OVERCONFIDENCE_TOLERANCE, "top_band": TOP_BAND,
                           "basis": "starting values by analogy to the streak-rule defaults; "
                                    "NOT derived from yourco data (no resolved forecasts yet)"}}


def gate(action, agent):
    """-> the recommendation for ONE action's promotion. Recommends only (rule 3)."""
    t = _trust()
    std = per_agent()
    row = next((r for r in std["agents"] if r["agent"] == agent), None)
    n = row["n"] if row else 0

    # --- the streak half, read from the existing audit so it cannot disagree with HQ ---
    audit = t._audit(t._ledger()) if hasattr(t, "_ledger") else None
    streak = None
    if isinstance(audit, dict):
        for r in audit.get("rows", []):
            name = (r.get("action") or "").strip().lower()
            if not name:      # an empty action name would prefix-match EVERY action
                continue
            if action.lower().startswith(name[:20]) or name.startswith(action.lower()[:20]):
                streak = r
                break

    reasons, verdict = [], None
    # Rule 1: below the floor there is no decision, in EITHER direction.
    if n < MIN_FORECASTS:
        verdict = "insufficient-evidence"
        reasons.append(refuse_reason(n) or f"only {n} resolved forecasts")
        reasons.append(f"{MIN_FORECASTS - n} more resolved forecast(s) from {agent} would make "
                       f"this answerable. Until then this is neither a pass nor a fail.")
        # Rule 4: name the streak state explicitly rather than letting it imply a pass.
        if streak:
            reasons.append(
                f"the streak table claims \"{(streak.get('claimedStreak') or '—')[:70]}\" and the "
                f"ledger audit calls that {streak.get('verdict')} — but a clean streak with no "
                f"calibration evidence is NOT a pass. That gap is the whole reason this gate exists.")
    else:
        fails = []
        if row["brier"] is not None and row["brier"] > MAX_BRIER:
            fails.append(f"Brier {row['brier']} exceeds the {MAX_BRIER} bar")
        if row["top_band"]["overconfident"]:
            fails.append(f"overconfident in the ≥{int(TOP_BAND*100)}% band: claimed "
                         f"{row['top_band']['claimed']}, actual {row['top_band']['actual']} "
                         f"(tolerance {OVERCONFIDENCE_TOLERANCE}) — held regardless of Brier, "
                         f"because this is the band promotions are decided in")
        verdict = "hold" if fails else "calibration-clear"
        reasons += fails or [f"Brier {row['brier']} within the {MAX_BRIER} bar over {n} resolutions"]
        if verdict == "calibration-clear":
            reasons.append("This clears the CALIBRATION half only. The streak half is Kolby's "
                           "ledger, and promotion still needs both plus the owner's call.")

    return {"action": action, "agent": agent, "verdict": verdict, "reasons": reasons,
            "resolved_forecasts": n, "brier": row["brier"] if row else None,
            "streak": streak, "thresholds": std["thresholds"],
            "promotes": False,
            "note": "Recommendation only. Promotion is the owner acting on a full ledger "
                    "(processes/autonomy-matrix.md §Advancement) — never this module."}


def main():
    ap = argparse.ArgumentParser(description="Calibration-gated autonomy.")
    ap.add_argument("--gate", metavar="ACTION")
    ap.add_argument("--agent")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.gate:
        if not a.agent:
            ap.error("--gate needs --agent")
        g = gate(a.gate, a.agent)
        if a.json:
            print(json.dumps(g, indent=2)); return
        print(f"{g['agent']} / {g['action']}\n  verdict: {g['verdict'].upper()}")
        for r in g["reasons"]:
            print(f"    - {r}")
        print(f"\n  thresholds: {g['thresholds']['basis']}")
        print(f"  {g['note']}")
        return

    s = per_agent()
    if a.json:
        print(json.dumps(s, indent=2)); return
    print(f"Calibration standing — {s['resolved_total']} resolved forecast(s), "
          f"{s['open_total']} open, floor {s['floor']}\n")
    if not s["agents"]:
        print("  No agent has placed a forecast yet, so no agent has calibration evidence.\n"
              "  Every gate therefore returns `insufficient-evidence` — which is the correct\n"
              "  day-one answer, not a failure. Forecasts are recorded with:\n"
              "    python3 runtime/trust_ledger.py --forecast \"<subject>\" --p 0.75 --agent <name>\n"
              "  and resolved later with --resolve <seq> --outcome clean|incident.")
    for r in s["agents"]:
        b = f"{r['brier']}" if r["brier"] is not None else "—"
        print(f"  {r['agent']:<12} n={r['n']:<4} brier={b:<8} "
              + (r["refusal"] or ("OVERCONFIDENT" if r["top_band"]["overconfident"] else "scored")))
    print(f"\n  thresholds: max_brier={s['thresholds']['max_brier']}, "
          f"overconfidence_tolerance={s['thresholds']['overconfidence_tolerance']}")
    print(f"  {s['thresholds']['basis']}")


if __name__ == "__main__":
    main()
