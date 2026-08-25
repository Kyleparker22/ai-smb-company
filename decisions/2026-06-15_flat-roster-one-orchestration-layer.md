# 2026-06-15 — Org shape: flat doer-roster + one orchestration layer (no per-area manager agents)

## Decision
YourCo's agent org stays **flat** — a roster of accountable specialist *doers*, with **one** coordination layer forming over them: **Melanie** (CEO-in-training, the conductor-understudy) on top of **Atlas** (the thin dispatch + observability substrate, when elevated). **We do not add a "leader/manager" agent per functional area** (no Sales Lead over Reilly/David/Sadie/Bird/Michelle, no Marketing Lead, etc.).

This extends, not replaces, `decisions/2026-06-07_agent-operating-model.md` ("siblings, the Founder conducts; Atlas observes, never commands") and its Atlas-orchestrator revisit condition.

## Why not per-area manager agents
1. **Premature — it manages idle capacity.** Most agents are scaffold/in-build and haven't run. A manager layer over unproven doers is the "shiny-tools trap" the roster already warns against.
2. **Manager-agents dilute accountability.** Agent-directs-agent chains add latency, propagate errors, and blur the single-throat-to-choke clarity — the exact opposite of what the reliability moat sells. Every layer between the Founder and a doer is a new place a hallucinated instruction can travel.
3. **It doesn't remove the human gate.** If a Sales Lead directs Reilly, the Founder still approves the Lead. You add a layer and keep the bottleneck — more cost, same gate.
4. **The coordination need is real but better met by one layer.** One orchestration brain (Melanie) over a flat roster, riding Atlas's dispatch/observability, beats N middle-managers: fewer system prompts, fewer eval bars, fewer drift points, one accountable seat. Handoff sequencing (e.g., Reilly sources → Michelle writes → David logs → Bird expands) is encoded as cross-agent SOPs + the connectors, not personified into a manager.

## What we do instead
- Keep the roster flat; capabilities fold into the nearest agent unless they need a distinct tool stack *and* eval bar (the standing split test).
- Let **Melanie** mature into the single CEO-conductor (already moved under the Founder on the HQ org chart 2026-06-15) and **Atlas** elevate to a *thin* orchestrator (dispatch + monitor, never absorb logic) per its existing revisit condition.

## Revisit trigger
Reconsider a mid-layer only if a **single area exceeds ~6–8 *live* agents with dense intra-area handoffs that the central orchestrator genuinely cannot sequence.** No area is close today (most have 1–2 live). If it ever trips, prefer splitting the orchestration layer by domain before introducing per-agent managers.
