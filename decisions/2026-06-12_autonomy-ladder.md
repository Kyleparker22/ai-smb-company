# Decision — The Autonomy Ladder (toward fully-autonomous client builds, without the Founder)

**Date:** 2026-06-12 · **Owners:** Brett (strategy) + Kolby (the enabler) + Kimi (who runs it) · **Status:** settled principle; phase advancement is data-gated

## The goal (the Founder)
The internal process of building a client's AI employee should run **100% autonomously — without the Founder in the loop.** No the Founder bottleneck on the build.

## The reframe that makes it safe *and* achievable
"No human element" precisely means **"no *the Founder*."** Two humans exist in an engagement — the Founder (YourCo) and the **client**. The goal removes *the Founder*, not all controls. The gates don't get deleted; they **migrate off the Founder** onto two things that scale: the **eval gate** (Kolby) and the **client's own approval** (in their own tenant).

## The core split
- **The build = fully autonomous, now.** Discovery synthesis, scaffolding from `yourco-template`, writing prompts/logic/config, wiring connectors, running internal evals, iterating, drafting the go-live note + client brief — **no the Founder.**
- **The irreversible, client-facing moments = gated** (go-live inside the client's tenant; sending to the client's customers; signature). These need *a* gate — but the gate migrates from the Founder → (eval gate + the client's own go-live approval) as eval evidence earns it.

## What never leaves a human — and it's the *client*, not the Founder
- The client **authorizes access** to their own systems (tenant/number/data). Their action by definition.
- The client **owns go-live** in their own business (at Phase 3, *they* approve — not the Founder).
- The client is **sender-of-record** for messages to their customers (CAN-SPAM/TCPA). Their compliance, not the Founder's bottleneck.

None of those is the Founder. So "autonomous without the Founder" is fully compatible with them.

## The ladder (autonomy is earned on eval evidence, never assumed)
- **Phase 0 — Build autonomy (active now):** everything up to go-live runs without the Founder. the Founder's only role is the irreversible client-facing gates below.
- **Phase 1 — Supervised go-live (first engagements):** the build is autonomous; **the Founder approves go-live + client-facing sends**, *expressly to generate the eval track record* — Kolby logs whether "passed eval" reliably predicted "worked in the real world, zero incidents."
- **Phase 2 — Spot-check:** once the evals demonstrably predict real-world success, the Founder reviews **exceptions + a sample**; routine go-lives proceed on eval-pass + client sign-off.
- **Phase 3 — the Founder fully out:** the **eval gate + watchdogs + the client's own go-live approval** are the controls. the Founder is 100% out of the build loop.

## Advancement criteria (Kolby measures; the Founder sets the threshold)
Advance a phase only when the data earns it — e.g. **N consecutive engagements where eval-pass predicted real-world success with zero post-go-live incidents.** Kolby tracks eval-vs-reality per engagement; the Founder locks the threshold to advance. Any incident resets/holds the phase.

## The enabler (and the one real caution)
**Hardening Kolby's eval gates is the literal path to Phase 3** — the more rigorous and *predictive* the evals, the sooner the Founder is removable. Conversely, **removing the Founder on day one — before any eval track record exists — is the one move that could kill the moat**: the first unsupervised agent that goes live and sends something wrong to a client's customers destroys the executive trust that *is* the business. Autonomy is earned on eval data; that's why the first engagements keep a gate — to prove the gate is safe to drop.

## What this changes in the OS
- `processes/discovery-to-48h-build.md` — adds an **"Autonomy ladder"** section recasting "What the Founder approves" as phase-dependent.
- Kolby (`agents/kolby/` + `processes/eval-rubric.md`) — owns the **eval-vs-reality track record** that gates phase advancement; eval rigor is now explicitly the autonomy enabler.
- Kimi (`agents/kimi/`) — runs the build at the current phase's autonomy level.
