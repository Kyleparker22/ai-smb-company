# Decision — Notion / n8n / Make stance (no-code & automation tooling)

**Date:** 2026-06-11 · **Owners:** Brett (strategy) + Kemba (platform) · **Status:** settled (revisit trigger below)

## Question
Should YourCo adopt Notion, n8n, or Make — internally or in client deployments?

## Decision
**No to all three as core systems**, with one narrow bounded exception.

- **Internally:** No. The OS *is* the git repo + markdown + the native CRM/dashboard. Notion would create a second source of truth (breaks single-source/closed-loop discipline). n8n/Make would be a parallel automation layer we can't eval/observe/approval-gate as rigorously as code — strictly worse than Claude Code + systemd + the agent loops we run today.
- **In client deployments:** Do **not** build the digital employee *on* Make or n8n. That makes YourCo a no-code agency — the exact thing it counter-positions against — and you cannot deliver rigorous evals, observability, and approval gates inside brittle visual flows. Building the brain there **undermines the moat**.

## The bounded exceptions
- **n8n (not Make)** as an optional **integration/glue layer** when a specific client's stack needs many SaaS APIs stitched fast and coding each would threaten the 48h go-live. Chosen over Make because it's self-hostable, git-versionable, and code-extensible — fits "YourCo owns reliability." Rule: **a wrench, never the workshop** — it sits *under* YourCo's eval/approval/observability umbrella, owned and instrumented by YourCo, never the substrate the employee lives in.
- **Notion** only if a *specific client* already lives in it and wants their engagement workspace there — a client-preference accommodation, not an YourCo system.

## Why (the moat test)
The moat is reliability + eval + observability + approval + enterprise integration + executive trust — explicitly *not* tooling ("tooling itself is nobody's moat"). n8n/Make are the no-code layer commoditizing operators use; adopting them as the substrate dilutes the one thing that's defensible. The test for any tool is not "is it useful?" but "does it strengthen or dilute the moat?"

## Revisit trigger
If hand-coding integrations becomes the bottleneck that threatens the 48h go-live promise, reach for **n8n-as-glue** first (still under the eval/observability umbrella). The moat isn't "written in Python" — it's the trust layer wrapping whatever's underneath; code-native wins by default because it makes that layer easiest to deliver.

## Trip-wire
- **Review:** 2026-12-01
- **Overturn if:** hand-coding integrations becomes the bottleneck that threatens the 48h go-live promise — then reach for n8n-as-glue first, still under the eval/observability umbrella.
- **Check:** _none — this trigger is a judgment about delivery friction, and no metric in the OS stands in for it honestly._
