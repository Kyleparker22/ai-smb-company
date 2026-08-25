---
name: anti-library-hand-check-needs-glob
description: When Bash is gate-denied, check the anti-library by Glob-ing rejections/ for the LIVE file list — never a remembered/prior-run list, which goes stale silently.
metadata:
  type: feedback
---

Triggers: anti-library check, clearing rejections, proposing an idea, agent:brett, agent:melanie, loop:source-watch, skill:tool-triage, bash denied, gate-denied

**When:** any loop that must clear the anti-library (`rejections/`) before proposing — Brett, Melanie's initiative, advisory panels, source-watch, tool-triage — on a run where `python3`/Bash is gate-denied so `runtime/rejections.py` can't run.

When Bash is denied, `rejections.py` can't run, so the anti-library gets checked "by hand." The failure mode: reusing a **remembered file list** from a prior run's artifact instead of reading the directory live. `rejections/` grows — a new entry added between runs is invisible to a carried list, and the miss is silent (the check still *reads* like it happened).

**Concrete miss this exposed:** the 2026-08-17 and 2026-08-18 initiative runs both hand-listed **7** rejection files. On 2026-08-16, `rejections/2026-08-16_bookie-agent-back-office.md` had already been added (making 8) — a **gambling-adjacent** rejection directly relevant to the 08-18 run's own Sample Contact (sports-betting picks creator) analysis. The 08-18 Dayton scope note was written without ever seeing the most on-point prior reasoning in the repo (EIN/Stripe contagion, the can-clear-vs-can't-clear line, "tout/handicapper needs its own triage"). The 08-19 run caught it only because it Glob'd instead of remembering.

**Why:** the anti-library is only a guardrail if it reflects the current directory; a stale hand-list defeats it while looking diligent.

**How to apply:** Bash denied → run `Glob rejections/*.md` (and `learnings/**` for Step 0) to get the **live** list, then read the relevant files in full. Never carry a file count/list forward across runs as if it were current. If a prior run's artifact states "N rejection files," re-derive N this run rather than trusting it. Links: [[cross-session-drift]], [[loop-liveness-blindspot]].
