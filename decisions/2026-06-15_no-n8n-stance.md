# 2026-06-15 — Why yourco doesn't build on n8n (FAQ + stance)

## Decision
**We do not build yourco's product or runtime on n8n.** Our substrate stays **Claude (Claude Code) + git + Python connectors + systemd**, with eval gates, the approval gate, and the learnings loop. n8n is a fine *visual workflow* tool; it's just the wrong layer for where our moat lives, and building on it would put us in the lane our thesis exists to avoid. (Recurring question — captured so it's not re-litigated. Consistent with the framework-adoption stance: *borrow patterns, not dependencies.*)

## Why
1. **Wrong layer.** n8n excels at deterministic if-this-then-that glue. yourco sells *agentic* work (model judgment) wrapped in **reliability + eval + observability + approval + executive trust** — the layer *above* what n8n does. The product is the moat layer, not the plumbing.
2. **We already own a stronger substrate.** Agents as code + markdown SOPs + eval harnesses + an approval gate, version-controlled in git and observable, are more programmable, testable, and *ownable* than a proprietary node graph. Real version control + real evals are awkward in a visual model.
3. **The no-code trap is literally our thesis.** `01_company.md`: the durable moat is the reliability layer "no-code operators cannot deliver." Build the business *on* n8n and our logic lives in n8n's graph format → we *become* the commoditizing operator we're built to out-class.
4. **One system of record.** Mixing n8n graphs with code-agents splits the source of truth and makes uniform eval/approval/observability harder. Git is the single substrate.

## The honest nuance (not heresy)
n8n is a legitimate option for **deterministic plumbing** — webhooks, schedulers, simple API chaining — the stuff we hand-roll with Python connectors + systemd. We declined it there too, because our plumbing is simple, observable, already-owned, and keeps one system of record. But: if a *client engagement* needs heavy visual integration wiring, n8n is fine as a **per-engagement tool** (overlay, not core). We just don't build yourco's brain on it.

## Evidence it's the commoditizing layer
The well-marketed "AI OS" creator products (e.g. **CharlieOS** — `agents/brett/competitive-watch.md`) are, under the hood, **Claude Code + n8n + GoHighLevel** bundles sold as a one-time install. That's exactly the no-code-operator layer our moat sits above — same tools, but they hand the client the reliability burden. We keep it. Same reason we don't lead with n8n.

## When to revisit
If a future need is genuinely pure deterministic integration glue at a scale where hand-rolled connectors become a maintenance drag *and* it can sit cleanly outside the eval/approval substrate — reconsider n8n as plumbing only, never as the agent brain.

## Trip-wire
- **Review:** 2026-12-01
- **Overturn if:** a future need is genuinely pure deterministic integration glue, at a scale where hand-rolled connectors become a maintenance drag, *and* it can sit cleanly outside the eval/approval substrate — then n8n as plumbing only, never as the agent brain.
- **Check:** _none — "maintenance drag at scale" is not a number this OS holds._
