# Decision — Agent registry + reconciliation watchdog (a "Vanta for our own agents")

**Date:** 2026-06-22 · **Owner:** the Founder · **Status:** Approved — internal-first v0
**Origin:** the Founder's question to Brett ("an agent that watches the OS so no AI/agents enter without my knowledge — like Vanta"). Full advisory: [loops/advisor/2026-06-22_agent-governance-watcher.md](../loops/advisor/2026-06-22_agent-governance-watcher.md).

## Decision
**Approve the control; decline the headcount.** Build an **agent registry** (the sanctioned list) + a **reconciliation watchdog** (diffs live runtime against that list and alerts on any delta). It is a *governance control*, **not a new named agent** — it folds into **Rafi** (it's literally his NIST *Detect* function), with hooks from **Kemba**, surfaced by **Atlas**. No 23rd sibling.

Scope it **internal-only for v0** (protect our own OS). The **client-facing attestation** version is deferred — not parked — to a clear trigger (below).

## Why (the real gap)
`04_agent_roster.md` is today our registry of sanctioned agents, but **nothing reconciles reality against it.** An agent in this OS is concretely: a `runtime/prompts/*.md` + a systemd timer + commit access + a connector scope in `~/.claude/settings.json`. Any of those could be added — by a future hire, a careless session, a compromised token, or just forgetting to log it — and **no automated control would catch it.** At 15 loops + two-way Slack + Gmail/Calendar connectors, and especially once client tenants exist, "I didn't know that agent existed" goes from unlikely to inevitable. This is exactly continuous control monitoring (Vanta's purpose): drift detection against a known-good baseline.

## Why it's on-thesis (not shiny-object)
The moat is *"reliability + eval + observability + approval + enterprise integration + executive trust."* An agent registry/attestation is **that layer made provable** — and a **sellable** one: a client never gets an agent in *their* tenant without sanction, with an audit trail for procurement. No-code operators can't offer that. It strengthens focus rather than diluting it.

## Ownership (a control, owned — not a new body)
Per the roster rule ("fold into an existing agent unless it needs a distinct tool stack AND a distinct eval bar"; a registry watcher needs neither):
- **Rafi owns it.** Vanta analogue exactly — control register + drift detection + audit readiness. His `processes/compliance-posture.md` register becomes the agent registry's home.
- **Kemba provides the hooks** — he owns the runtime/agent execution environment; the manifest of timers/prompts/connectors lives where he already works.
- **Atlas surfaces the signal** — "unsanctioned agent detected" is one more watchdog line in the Monday briefing; no command authority added.
- **The approval gate stays the enforcement teeth.** Creating an agent ultimately means a commit + a settings change, both already routed through the Founder. The watchdog **detects and alerts**; the Founder remains the only one who sanctions.

## Coherent action (smallest version first)
1. **Registry manifest (~½ day):** one machine-checkable list of every sanctioned agent → its prompt file, its timer, its connector scopes. The roster already has ~90% of this; formalize it.
2. **v0 reconciliation watchdog:** a scheduled job that diffs *live* runtime (systemd timers, `runtime/prompts/`, the `settings.json` connector allowlist, crontab) against the manifest and **alerts on any delta** — new timer, new prompt, widened connector scope, new commit author. Read-only, inside the gate. Surfaced in the **Monday briefing** (and `#yourco-rafi`).
3. **Client-tenant attestation (deferred):** extend the same check to client-side agents + an exportable procurement audit trail — the sellable version.

## Now / Next / Watch
- **Now:** registry manifest + v0 internal watchdog under Rafi. Low cost, real risk reduction, reinforces the moat.
- **Next (trigger = first client tenant signs):** client-facing attestation + audit export.
- **Watch — the one real risk: governance theater.** A watcher nobody reads is *worse* than none — it manufactures false confidence. Mitigation: the alert must land on a surface the Founder already reads (**the Monday briefing**), not a new dashboard to ignore. The control only counts if the alert is seen and acted on.

## Explicitly NOT happening
- **No new named agent.** This does not spin up a standalone "governance" sibling, and it does **not** trigger building Rafi as a full standalone agent ahead of his activation trigger — it runs as a control under Rafi's existing v0 until client data forces full activation.

## Next steps
- Rafi: formalize the registry manifest + build the v0 watchdog job (read-only, briefing-surfaced).
- Roster (`04_agent_roster.md`): one-line Rafi scope addition noting he owns the agent registry + reconciliation watchdog.
- Kemba: expose the live-runtime manifest hook (timers/prompts/connectors) for the diff.

## Related
[[2026-06-22_agent-governance-watcher]] (Brett's advisory) · `agents/rafi/_README.md` · `processes/compliance-posture.md` · `04_agent_roster.md` · `CLAUDE.md` (the moat).
