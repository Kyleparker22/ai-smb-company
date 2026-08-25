> ⚠️ **EXAMPLE — not yours.** From the source company; restored because other pages cite it.

# Initiative companion — 2026-08-20: the headless approval gate silently blocks the 08-13 agentops instrumentation

> Melanie, entity-level initiative loop. Internal analysis (decision-support). I propose; the Founder decides. Nothing here edits the gate, the CRM, goals, or any instrument — proposing only. Boundary: `decisions/2026-07-08_melanie-initiative-loop.md`.

## The finding in one line
The loop contract mandates five in-session `python3 runtime/*.py` commands; the host approval gate (`~/.claude/settings.json`) **denies `Bash`**. So on the headless runtime those commands never run — and four of the 08-13 substrate's evidence stores can *never* fill regardless of elapsed time, which the OS is currently mislabeling as "wired, unproven — read in ~30 days."

## Verified, not asserted (sources read this run)
- **`~/.claude/settings.json`** (the active host gate) — `permissions.deny` = `["Bash", gmail send, gmail delete, gmail batch_delete]`. `Bash` is **blanket-denied**; there is no scoped `Bash(...)` allow.
- **`run-loop.sh`** — line 88 runs `python3 runtime/run_journal.py --record` **in the shell wrapper**, *after* `claude -p` exits and *outside* the gated session. This is why cost capture survives the gate.
- **`runtime/prompts/_loop-contract.md`** — mandates, all *in-session* (i.e. inside `claude -p`, subject to the gate):
  - Step 0: `python3 runtime/learning_triggers.py …`
  - Anti-library (when proposing): `python3 runtime/rejections.py --check …`
  - Anti-spin stop: `python3 runtime/failure_traces.py --record …`
  - Long-run checkpoint/resume: `python3 runtime/run_journal.py --checkpoint|--resume …`
  - Untrusted input: `python3 runtime/provenance.py --wrap-file|--check …`
- **`loops/_agentops/` (Glob)** — contains **only** `_README.md` and `runs.jsonl`. `failures.jsonl`, `reviews.jsonl`, `approvals.jsonl`, `provenance.jsonl` **do not exist** — never written.
- **`loops/_agentops/runs.jsonl`** — 21 real rows, seq 1–21, 2026-08-16 → 2026-08-20, every loop, real `cost_usd`/`tokens`. Populated normally. Confirms the *wrapper-run* path works and the gap is specifically the *in-session* commands.
- **Scripts exist** (Glob `runtime/{learning_triggers,rejections,failure_traces,run_journal,provenance}.py`) — all five present, so this is a permission wall, not a missing file.
- Corroboration across loops: the 08-16→08-20 runs of open-loops (Jim), crm-autolog (David) and initiative (me) each footnote "learning_triggers.py / rejections.py need Bash, which is gate-denied." Consistent across agents ⇒ a host condition, not one session's quirk.

## Why this is real, and why it matters (not just a footnote)
1. **The contract commands the gate forbids.** The 08-13 substrate (`decisions/2026-08-13_agent-substrate-upgrade.md`) and the gate (`decisions/2026-06-09_always-on-runtime.md`, extended 06-16) were written five weeks apart and never reconciled. Every headless loop is told to run tools it cannot run.
2. **Cost capture is fine; the other four stores are not.** Because `run_journal --record` lives in the wrapper, `runs.jsonl` fills. But `failures.jsonl` (anti-spin stops → instruction patches), `reviews.jsonl` (R1.5 second opinions), `approvals.jsonl` (decaying approvals) and `provenance.jsonl` are written *in-session* — they are **empty by permission wall, not by "no events yet."** The agentops README says "all four start empty, and that is correct … first honest read ~30 days" — for these four that framing is **false on the headless box**: 30 more days changes nothing while the gate stands.
3. **The failure-trace mechanism is defeated for the one failure that recurs every run — circularly.** The contract: a missing-input stop must run `failure_traces.py --record --stop missing-input`, and "two runs stopping the same way at the same step become a patch proposal against that file at the weekly eval-review." The missing input that has recurred on **every** loop since at least 08-16 *is Bash denial itself* — and recording it requires Bash. The tool needed to report the tool's absence is the absent tool. So the exact escalation path designed to turn a recurring failure into an instruction-fix cannot fire for this failure.
4. **No one is catching it right now.** Kolby's eval-review — where failure-trace patches surface and where instrumentation health would be graded — last ran **2026-07-12** and has been paused since. So the layer that would normally flag this is dark. That is why an entity-level loop is the one surfacing it.
5. **It touches the moat, not a nicety.** yourco's pitch is that the reliability/eval/observability/approval layer is the defensible margin no-code can't build. A substrate sold as the moat's proof that silently can't run headless is a **"wired, unproven" → "wired, cannot-run-headless"** downgrade. Honest instrumentation is the product; this is worth fixing or relabeling, not carrying as a footnote.

## Anti-library check (by hand — `rejections.py` is the very tool that's blocked)
Idea: *scope-allow the agentops instrumentation scripts through the headless gate so the four stores can fill.* Checked by Glob against all 8 `rejections/*.md` (landscaping-beachhead · flat-client-referral-credit · per-vertical-funnel · detection-evasion-scrapers · openmontage · self-serve-saas · bookie-agent-back-office · _README). **Not previously rejected** — none concerns the approval gate, Bash allowlisting, or runtime instrumentation.

## Options (I propose — the Founder decides; each is his, none is mine to execute)
**A — Scoped Bash allowlist on the host gate (recommended).** In `~/.claude/settings.json`, **remove** the blanket `"Bash"` deny and allow-list exactly the instrumentation commands, e.g.:
```
"Bash(python3 runtime/learning_triggers.py:*)",
"Bash(python3 runtime/rejections.py:*)",
"Bash(python3 runtime/failure_traces.py:*)",
"Bash(python3 runtime/run_journal.py:*)",
"Bash(python3 runtime/provenance.py:*)",
"Bash(python3 runtime/second_opinion.py:*)",
"Bash(python3 runtime/decaying_approval.py:*)"
```
These scripts are **read/append-only to `loops/_agentops/`** — reversible in git, no network send, no delete, no payment — exactly the action class the gate already welcomes; they're caught only because they ride Bash and Bash is blanket-denied.
⚠️ **Honest caveat that makes this the Founder's call, not mine:** in Claude Code the `deny` list **outranks** `allow`, so a blanket `"Bash"` sitting in deny would override any scoped `Bash(...)` allow. The blanket entry must be **removed**, not sat beside the allowlist — which genuinely widens the shell surface from "no shell at all" to "an allowlisted set of commands." That is a real security-posture change and deserves a **decision-log entry**, not a silent edit. Mitigate by keeping explicit deny patterns for dangerous verbs (`Bash(rm:*)`, `Bash(git push:*)`, `Bash(curl:*)`, `Bash(npm:*)` …) so the widening is only the instrumentation.

**B — Wrapper-ize what can be batched (gate-preserving, partial).** Run the *deterministic, pre-run* pieces in `run-loop.sh` outside the session, exactly as `run_journal --record` already runs after it: `learning_triggers.py` before `claude -p` (inject its ranked output into the prompt), and optionally a `rejections.py` pre-scan. Needs **no** posture change. But `failure_traces.py --record` and `provenance.py` are inherently mid-run (they depend on what the agent hits), so B only half-solves it. Cleanest as **A for the mid-run pair + B for Step-0 retrieval**, if the Founder wants the smallest posture change that still fills all four stores.

**C — Accept and relabel (the honesty floor, if the gate stays shut now).** If the Founder won't touch the gate this cycle, the OS must stop claiming these stores are "wired, unproven — read in 30 days." Add a line to `decisions/2026-08-13_agent-substrate-upgrade.md` and `loops/_agentops/_README.md` recording that `failures/reviews/approvals/provenance` are **cannot-write under the current headless gate** (only `runs.jsonl`, wrapper-run, fills), so no one reads their emptiness in 30 days as "clean." This is the change-one-sweep-all move: the claim is duplicated in CLAUDE.md's substrate paragraph too.

## The concrete next click for the Founder
Open `~/.claude/settings.json` on the VPS (`ssh user@your-vps`), decide A / A+B / C. If A: remove `"Bash"` from `deny`, paste the allowlist above into `allow`, add the dangerous-verb denies, mirror into the repo reference copy, and log the decision (the posture change is the decision). ~10–15 min, counsel-free, host-only. If C: it's a 3-file honesty edit, ~5 min.

## What I deliberately did NOT do
Did not edit `~/.claude/settings.json` or its repo reference copy (host security posture — the Founder's, and outside this loop's outputs) · did not edit the substrate decision, the agentops README, or CLAUDE.md (Option C is *proposed*, not applied) · did not run any blocked command (I can't) · did not send anything · proposed no spend (all three options are $0). And I could not `failure_traces.py --record` this very missing-input stop — which is the finding — so I name it here, exactly as the contract's fallback directs.
