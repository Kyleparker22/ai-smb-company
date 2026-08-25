---
name: headless-gate-blocks-in-session-instrumentation
description: On the headless runtime, loop-contract python commands run IN-SESSION are Bash-gate-denied; only wrapper-run scripts survive. An absent _agentops store file means the writer never ran, not "no events yet."
metadata:
  type: project
Triggers:
  - a loop reports "learning_triggers.py / rejections.py / failure_traces.py couldn't run (Bash denied)"
  - reading or judging the emptiness of a loops/_agentops/ store (failures/reviews/approvals/provenance)
  - assessing whether the 2026-08-13 agent-substrate instrumentation is actually producing evidence
  - any run about the headless approval gate, ~/.claude/settings.json, or Bash permissions
---

**The pattern.** The loop contract (`runtime/prompts/_loop-contract.md`) mandates five *in-session* commands — `learning_triggers.py` (Step 0), `rejections.py` (anti-library), `failure_traces.py --record` (anti-spin stop), `run_journal.py --checkpoint`, `provenance.py`. The host approval gate (`~/.claude/settings.json`) **denies `Bash`**. So inside `claude -p` on the runtime, **none of them run.** The only agentops writer that survives is `run_journal.py --record`, because `runtime/run-loop.sh:88` runs it in the *shell wrapper*, outside the gated session — which is why `runs.jsonl` (cost) fills while `failures.jsonl` / `reviews.jsonl` / `approvals.jsonl` / `provenance.jsonl` **don't even exist as files.**

**Why it matters / how to apply:**
- **Don't read an absent `_agentops/` store as "empty but waiting."** A missing store *file* means its writer never successfully ran. Glob `loops/_agentops/` and check which files exist before repeating the substrate README's "all four start empty, and that is correct — read in ~30 days." For the four in-session stores that framing is false while the gate stands (`absence-is-invisible-to-this-os` applies: prove the emptiness, don't read it as health).
- **The Bash wall is not a footnote — it's a live reliability gap.** Every loop since 2026-08-16 footnotes "couldn't run the script." Stop restating it as boilerplate; it means the 08-13 substrate is running degraded headless. Surfaced as an initiative move 2026-08-20 (`loops/initiative/2026-08-20_headless-gate-blocks-agentops-instrumentation.md`) with options A (scoped `Bash(python3 runtime/*.py:*)` allowlist — but `deny` outranks `allow`, so the blanket `"Bash"` must be *removed*, a posture change that needs a decision-log entry) / B (wrapper-ize the pre-run pieces) / C (relabel the stores "cannot-write headless"). Until the Founder picks one, do the Step-0 / anti-library work **by hand** and say so.
- **Circular trap to name, not hit:** the contract says a missing-input stop must run `failure_traces.py --record`. When the missing input *is* Bash, you cannot record it — name it in the artifact instead (the contract's own fallback), and don't loop trying.

Related: [[anti-library-hand-check-needs-glob]] · [[absence-is-invisible-to-this-os]] · [[loop-liveness-blindspot]]
