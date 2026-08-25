# 2026-06-07 — Agent operating model: siblings, the Founder conducts

## Decision
Atlas, Reilly, and Reed operate as **siblings**, not a hierarchy. **the Founder is the conductor** — he triggers Reilly (by naming a vertical) and Reed (by requesting an asset), and approves all gated actions. Atlas **observes and reports** (Monday briefing, cost rollup, watchdogs) but does **not** dispatch or direct the other agents. We do **not** elevate Atlas to orchestrator until Reilly and Reed have each proven out solo — correct, accurate, and reliable.

## Context
With Reilly and Reed freshly scaffolded, the question came up of whether Atlas should run and direct them. Tempting (single pane of glass), but neither Reilly nor Reed has executed a real run yet. Adding an orchestration layer on top of unproven agents would stack unvalidated complexity and make failures harder to localize.

## Options considered
- **Atlas as orchestrator/manager now** — Atlas dispatches + monitors Reilly/Reed. Rejected for now: premature; can't orchestrate what isn't proven; risks masking which agent/stage failed.
- **Siblings, the Founder conducts (chosen)** — each agent independently triggered, gated, and evaluated; the Founder holds the baton; Atlas stays observability-only.

## Why
- **Prove the units before the system.** Each agent must demonstrate it works correctly and accurately on its own before anything coordinates them. Localized failure = faster debugging = the reliability moat.
- **Keeps the moat intact.** Per-agent eval gates and approval flows stay crisp; no monolith creep.
- **Human approval unchanged.** Reilly still never sends without the Founder; Reed never publishes without the Founder; Atlas still never acts, only reports.

## Reversibility
Fully reversible — this is sequencing, not a permanent stance. **Revisit (elevate Atlas to a thin orchestration + observability layer, not a monolith) when:** Reilly has run ≥3 clean campaigns and Reed has shipped ≥1 approved, accurate demo, and both hold their eval targets. At that point, log a follow-up decision and update Atlas's discovery/roadmap.

## Implications for the docs (as of now)
- No "Atlas dispatches Reilly/Reed" wiring exists or should be added yet.
- The one sanctioned cross-agent link remains **Reilly → Reed** (asset request for touch 2).
- Atlas's v1/v2 roadmap (engagement-health watchdog, cost rollup) stays observability-scoped, consistent with this decision.
