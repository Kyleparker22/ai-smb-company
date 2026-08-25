# Agent roster deep-build — 11 agents brought to full operating docs

**Date:** 2026-06-25
**Decision:** Deep-build all remaining in-build + scaffold agents in one pass, to full `discovery/build/eval` operating documentation (the Charles structure), grounded in each agent's expert lineage. the Founder's call (chose "deep-build all 11 now").

## What was built
Each agent's `clients/<name>/` folder now has `01_discovery.md` (problem · outcome · constraint, in the lineage's framing), `02_build.md` (the operating SOP + actual templates + closed-loop wiring + handoffs), and `03_eval.md` (test cases · scoring rubric · hard gates · red-team failure modes · the "good" metric), plus a tightened `_README.md` charter.

| Agent | Function | Lineage | Status now | Activation |
|---|---|---|---|---|
| Charles | Finance | David Skok | Built | Scheduled (live-ready) |
| Mario | Answer-engine visibility (AEO/GEO) | AEO/GEO + Sheridan | Built | Live at website launch |
| Bella | Audit lead | Goldratt + Block | Built | Live at website launch |
| Michelle | Outbound copy | Braun + Shleyner | Built | On campaign |
| Webb | Web ops / site | Krug + Wiebe | Built | Live-ready (launch-gate) |
| Janice | Onboarding | Lincoln Murphy | Built | **Trigger: first signed client** |
| Kimi | Delivery (48h build) | Eric Ries | Built | **Trigger: deal near close** |
| Kortney | Customer health | Mehta + Murphy | Built | **Trigger: first live client** |
| Bird | Expansion | Jason Lemkin | Built | **Trigger: Kortney green light** |
| Harry | Back-office / AR | Michalowicz | Built | **Trigger: first invoice** |
| Kori | People ops | McCord + Bock | Built (parked) | **Trigger: first human hire** |

## Principle held
The 6 trigger-gated agents were built **activation-ready, not activated** — full docs that fire the moment their trigger hits, with **no fabricated clients, metrics, or live state** (YourCo is pre-revenue; Sample Client is unsigned). This respects the roster's "prove the unit before adding the next" rule: the *capability* is ready; it doesn't *run* until a real trigger fires.

## Reconciliations made (same pass)
- **`dashboard/data.json`** — promoted all 11 agent statuses to `built` (fixes the prior dashboard-vs-roster mismatch where Janice/Kimi/Kortney/Bird/Harry/Kori showed `scaffold` while the roster said "Built 2026-06-11").
- **`04_agent_roster.md`** — updated the 5 in-build Status cells to Built (2026-06-25) + added a deep-built note to the Planned-agents table.
- **`processes/audit-sop.md`** — fixed a stale owner line that still named **Kimi** as the Audit runner; it's **Bella** (Audit Lead) who runs it → hands the converted engagement to Kimi (Bella flagged this during the build).

## Open follow-ups (flagged by the builders; not blocking)
1. **Michelle's copy docs** (`agents/reilly/copy-structure.md`, `processes/outbound/sequence-copy.md`) are hers by ownership but still live at historical paths; relocating under `agents/michelle/` is an optional cross-file move. Also two sequence structures (proof-led 4-touch = live default; v2 6-touch = methodology) coexist — reconcile to one canonical doc if desired.
2. **Kortney's loop** (`runtime/prompts/customer-health.md`) signs "— Atlas" in pre-revenue mode; flip the signature/identity to "— Kortney" at first-live-client activation.
3. **`demo-prep` loop** — staged-off and its premise (per-vertical hero videos / funnel) was parked under horizontal positioning; due for a **revise-or-retire** call rather than "arm later."
4. **`processes/audit-sop.md`** still references the parked online Revenue Leak Snapshot + per-vertical landing pages (parked to `_parked/` under horizontal positioning) — a separate SOP refresh.

## What did NOT change
The **agent registry** (`runtime/agent-registry.json`) is unchanged — it sanctions runtime artifacts (prompts/timers/services/connectors), and this pass added none (only `clients/<name>/` docs). No new loops, timers, or connector scopes were introduced.
