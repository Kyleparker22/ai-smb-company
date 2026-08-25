#!/usr/bin/env python3
"""R1.5 — a second opinion between the agent and the Founder.

THE CONSTRAINT THIS ATTACKS.  `processes/autonomy-matrix.md` runs R1 (a human commits) straight
into R2 (auto + notify). There is nothing between, so every unproven action lands in one person's
queue — and the 2026-08-13 advisory panel's own convergence was that *every idea is downstream of
capacity, and capacity is one person*.

R1.5 inserts an **independent agent with a different lens** that either clears the action to
R2-equivalent handling or escalates it to the Founder *with the disagreement stated*. This is consistent
with the autonomy standard rather than a hole in it: the standard's whole claim is that "no human
checkpoint" ≠ "no control" — the control migrates off the human onto the reliability layer. A
second independent reader is a control that does not need a person.

WHAT A CORRELATED REVIEWER CAN AND CANNOT CATCH — the honest bound, printed on every output.
Two instances of the same model share blindspots. R1.5 is therefore scoped to failure classes a
second read genuinely catches:

    completeness    a required section, source, or step is missing
    policy          it breaks a written rule (brand, gate, external-surface, provenance)
    consistency     it contradicts itself, or contradicts the artifact it cites
    provenance      it treats untrusted content as fact (runtime/provenance.py)
    arithmetic      the numbers do not add up to the claim

It does **not** catch a shared wrong premise, and it is never a substitute for eval evidence.
Anything where being wrong is expensive and a second read would not notice stays at R1.

WHERE THE JUDGMENT HAPPENS.  This module is the HARNESS, not the reviewer: eligibility, reviewer
selection, and the verdict arithmetic are deterministic here; the actual reading is a model call
made by whoever invokes it, against the prompt this emits. That split is
`learnings/ops/2026-08-09_inference-only-where-judgment-is-needed.md` applied — pay for inference
only where judgment is needed, and nowhere else in the path.

FIVE HONESTY RULES (tests in runtime/test_agentops.py):

1. **Ineligible classes are refused by LOOKUP, never by judgment.**  Money, destructive,
   config-change, regulated advice and anything customer-facing can never be cleared by R1.5,
   regardless of how good the review is.
2. **A reviewer may never be the author.**  Checked deterministically. An agent reviewing itself
   is not a second opinion, it is the same opinion twice.
3. **A `clear` is not a promotion.**  It routes ONE instance of an action; the rung is unchanged
   and only the streak+calibration ledger moves it.
4. **The scope limit is printed on every verdict.**  A reviewer that quietly implies it checked
   the premise is worse than no reviewer.
5. **An escalation states the disagreement.**  "Escalated" with no reason is just a slower R1.

CLI
  python3 runtime/second_opinion.py --request --action external-draft --author michelle \\
      --reviewer kolby --lens policy --material loops/outreach-eval/2026-08-13.md
  python3 runtime/second_opinion.py --verdict <seq> --result clear|escalate --finding "..."
  python3 runtime/second_opinion.py --status
"""
import os, sys, json, argparse

CODE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("YOURCO_DATA_ROOT") or os.path.dirname(CODE)
sys.path.insert(0, CODE)
from ledger import Ledger  # noqa: E402
import provenance  # noqa: E402

STORE = "loops/_agentops/reviews.jsonl"

LENSES = {
    "completeness": "Is any required section, source, step or artifact missing? Judge only against "
                    "what the SOP or skill in force requires — not against what you would have done.",
    "policy":       "Does it break a WRITTEN rule? Check brand/writing-rules.md, the external-surface "
                    "rules in CLAUDE.md, the approval gate, and the provenance policy. Quote the rule.",
    "consistency":  "Does it contradict itself, or contradict the artifact it cites? Check every "
                    "figure against its stated source.",
    "provenance":   "Does it restate untrusted content as fact? Anything sourced from an inbox, a "
                    "scrape, a form or a search must be quoted and attributed, never asserted.",
    "arithmetic":   "Do the numbers support the claim? Recompute every derived figure.",
}

# Rule 1: never clearable by a second read, whatever the review says.
NEVER_ELIGIBLE = {"money", "destructive", "config-change", "external-send"}
ELIGIBLE = {"internal-write", "internal-post", "external-draft", "summarize", "read"}

SCOPE_LIMIT = ("R1.5 catches completeness, policy, consistency, provenance and arithmetic failures. "
               "It does NOT catch a shared wrong premise — two reads of the same model correlate. "
               "It is not eval evidence and it does not move a rung.")


def eligible(action):
    if action in NEVER_ELIGIBLE:
        return False, (f"'{action}' can never be cleared by a second opinion — it is on the "
                       f"never-eligible list (autonomy matrix §What stays gated regardless of "
                       f"evidence). Stays at R1: the Founder commits.")
    if action not in ELIGIBLE:
        known = ", ".join(sorted(ELIGIBLE | NEVER_ELIGIBLE))
        return False, (f"unknown action class '{action}' — refused rather than guessed. Known: {known}")
    return True, None


def request(action, author, reviewer, lens, material, summary=""):
    ok, why = eligible(action)
    if not ok:
        return {"eligible": False, "reason": why, "scope_limit": SCOPE_LIMIT}
    if lens not in LENSES:
        return {"eligible": False, "scope_limit": SCOPE_LIMIT,
                "reason": f"unknown lens '{lens}' — one of {', '.join(sorted(LENSES))}"}
    # Rule 2 — deterministic, not advisory.
    if (author or "").strip().lower() == (reviewer or "").strip().lower():
        return {"eligible": False, "scope_limit": SCOPE_LIMIT,
                "reason": (f"'{author}' cannot review its own work — that is the same opinion "
                           f"twice, not a second one. Name a different reviewer.")}
    ev = Ledger(STORE).append("request", action=action, author=author, reviewer=reviewer,
                              lens=lens, material=material, summary=summary)
    return {
        "eligible": True, "seq": ev["seq"], "reviewer": reviewer, "lens": lens,
        "prompt": (
            f"You are {reviewer}, giving a SECOND OPINION on work authored by {author}.\n"
            f"Lens — judge ONLY through this one: {LENSES[lens]}\n\n"
            f"Material: {material}\n"
            f"{('Author summary: ' + summary) if summary else ''}\n\n"
            f"You are not asked whether this is a good idea, and you are not the author's editor. "
            f"Return exactly one verdict:\n"
            f"  clear    — nothing in your lens is wrong. State what you checked.\n"
            f"  escalate — something in your lens is wrong. State the finding, quote the evidence, "
            f"and name the rule or source it breaks.\n\n"
            f"An escalation with no stated finding is not an escalation. If your lens does not "
            f"apply to this material, say so and return escalate — silence must not read as clear.\n"
            f"Record with: python3 runtime/second_opinion.py --verdict {ev['seq']} "
            f"--result clear|escalate --finding \"...\""),
        "scope_limit": SCOPE_LIMIT,
    }


def verdict(seq, result, finding=""):
    if result not in ("clear", "escalate"):
        raise ValueError("result must be 'clear' or 'escalate'")
    # Rule 5: an escalation must state the disagreement, or it is just a slower R1.
    if result == "escalate" and not finding.strip():
        raise ValueError("an escalation must carry a --finding: 'escalated' with no reason is "
                         "just a slower R1, and costs the Founder the same minute it was meant to save")
    if result == "clear" and not finding.strip():
        finding = "(cleared with no stated check — weak evidence; ask the reviewer what it read)"
    ev = Ledger(STORE).append("verdict", request=seq, result=result, finding=finding)
    return {**ev, "routes_to": "R2-equivalent handling (auto + notify + reversible)"
            if result == "clear" else "the Founder, with the finding attached",
            "promotes": False, "scope_limit": SCOPE_LIMIT,
            "note": "Rule 3: this routes ONE instance. The rung is unchanged — only the "
                    "streak + calibration ledger moves it."}


def status():
    raw = Ledger(STORE).project()
    reqs = {e["seq"]: e for e in raw["events"] if e.get("kind") == "request"}
    vers = [e for e in raw["events"] if e.get("kind") == "verdict"]
    done = {v.get("request") for v in vers}
    rows = [{"seq": s, **{k: r.get(k) for k in ("action", "author", "reviewer", "lens", "material")},
             "verdict": next((v.get("result") for v in vers if v.get("request") == s), None),
             "finding": next((v.get("finding") for v in vers if v.get("request") == s), None)}
            for s, r in reqs.items()]
    return {"reviews": rows, "open": [r for r in rows if r["seq"] not in done],
            "cleared": sum(1 for r in rows if r["verdict"] == "clear"),
            "escalated": sum(1 for r in rows if r["verdict"] == "escalate"),
            "bad_lines": raw["bad"], "store_exists": raw["exists"], "scope_limit": SCOPE_LIMIT}


def main():
    ap = argparse.ArgumentParser(description="R1.5 — the second-opinion rung.")
    ap.add_argument("--request", action="store_true")
    ap.add_argument("--action"); ap.add_argument("--author"); ap.add_argument("--reviewer")
    ap.add_argument("--lens", choices=sorted(LENSES)); ap.add_argument("--material", default="")
    ap.add_argument("--summary", default="")
    ap.add_argument("--verdict", type=int); ap.add_argument("--result", choices=("clear", "escalate"))
    ap.add_argument("--finding", default="")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--lenses", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.lenses:
        for k, v in LENSES.items():
            print(f"  {k:<14}{v}")
        print(f"\n  eligible: {', '.join(sorted(ELIGIBLE))}")
        print(f"  NEVER eligible: {', '.join(sorted(NEVER_ELIGIBLE))}")
        print(f"\n  {SCOPE_LIMIT}")
        return
    if a.request:
        r = request(a.action, a.author, a.reviewer, a.lens, a.material, a.summary)
        if a.json:
            print(json.dumps(r, indent=2)); return
        if not r["eligible"]:
            print("INELIGIBLE — " + r["reason"] + "\n\n  " + r["scope_limit"]); return
        print(r["prompt"] + "\n\n  " + r["scope_limit"])
        return
    if a.verdict:
        if not a.result:
            ap.error("--verdict needs --result")
        try:
            v = verdict(a.verdict, a.result, a.finding)
        except ValueError as e:      # a refusal is a message, not a stack trace
            print(f"REFUSED — {e}")
            raise SystemExit(2)
        print(f"verdict recorded seq={v['seq']} -> {v['routes_to']}\n  {v['note']}")
        return

    s = status()
    if a.json:
        print(json.dumps(s, indent=2)); return
    if not s["store_exists"]:
        print("  No second opinions requested yet.\n\n  " + s["scope_limit"]); return
    print(f"R1.5 — {s['cleared']} cleared, {s['escalated']} escalated, {len(s['open'])} open\n")
    for r in s["reviews"]:
        print(f"  [{r['verdict'] or 'open':<8}] {r['action']} — {r['author']} -> {r['reviewer']} "
              f"({r['lens']})")
        if r["finding"]:
            print(f"        {r['finding'][:150]}")
    print(f"\n  {s['scope_limit']}")


if __name__ == "__main__":
    main()
