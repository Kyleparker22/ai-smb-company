# Delivery surge playbook — when multiple clients sign at once

> What to do when N clients sign close together and all want to go live fast. The honest capacity model + the staged play that lands them all **without melting the bottleneck or risking the moat.** Owners: Kimi (delivery) + Janice (onboarding) + Bella (audits) + the Founder (the gate, until autonomy is earned). Created 2026-06-30.

## The core truth
The OS is *designed* for many clients (golden template + per-client overlay — `03_internal_platform.md`). The constraint is **proven throughput, not architecture.** Early on the binding constraints are **the Founder's approval bandwidth** (the autonomy ladder keeps him gating go-lives until eval evidence earns them down) and **the empty eval track record**. So: land them all, but **stage delivery — never force simultaneous *unsupervised* go-lives.**

## Capacity model (what's realistic, by maturity)
| Stage | Concurrent true-48h builds | Why |
|---|---|---|
| **Now (0 proven, pre-revenue)** | **1–2** | the Founder gates every go-live; playbook unproven; the first build hardens the template |
| **After 1–2 proven** (eval record forming) | **2–3** | template hardened; Janice/Kimi/Kortney activated + hardened on real work |
| **After the ladder climbs** (eval evidence earns autonomy) | **several in parallel** | go-lives need less/no the Founder; Kimi runs builds at higher rungs |

**"5 live in one week" is a later-stage capability** — it arrives when the eval track record + activated delivery chain + locked scaling infra are in place, not on day one.

## The play (when M clients sign in a week)
1. **Audit-first, all of them, in parallel.** Run the **free Audit** (Bella) for every signee immediately — it's diagnostic, not a build, so it scales in parallel, it's revenue *now*, and it scopes + qualifies each. This is the pressure valve: it proves momentum without forcing M simultaneous builds.
2. **Triage by fit + readiness.** Rank by: simplest/most-reversible first use case · client provisioning readiness · lowest stakes. The cleanest 1–2 enter the true 48h build; the rest queue.
3. **Build in sequence, not parallel (early).** 1–2 true 48h builds at a time; as each proves out, the next starts. The first build's template improvements speed every subsequent one.
4. **Honest client framing.** *"Your audit's done; your build is scheduled for [date]."* Deliberate onboarding reads as premium, not slow. Never promise simultaneous go-lives you can't safely deliver.
5. **Gate every go-live** (early): the Founder approves anything customer-facing — this is the eval-evidence generator, not bureaucracy.
6. **Watch the shared-infra failure modes** (now handled by the locked scaling decisions): per-client API key/billing so a shared balance dying can't take all M down, rate-limit headroom, cost-per-client attribution.

## Roles in a surge
- **Bella** — runs all the audits in parallel (the throughput-friendly front door).
- **Janice** — the onboarding pipeline: provisions tenants/creds/mailboxes (client-gated → sequence it).
- **Kimi** — the builds, sequenced at the current autonomy rung; hardens the template each time.
- **Kortney** — health on the ones that go live; catches issues before they spread.
- **Atlas** — watches cost + health across all engagements (a surge is exactly when the rollup matters).
- **the Founder** — the gate on go-lives (until the ladder earns it down) + the threshold-setter.

## The levers that raise surge capacity (do these to make "5 in a week" real)
1. **Prove the playbook on the first 1–2** (Sample Client first) — the template + eval set that makes the rest fast.
2. **Climb the autonomy ladder** — Kolby's eval-vs-reality evidence earns go-lives off the Founder (the real throughput unlock). See `processes/autonomy-matrix.md`.
3. **Lock the scaling infra** — done 2026-06-30 (`decisions/2026-06-30_multi-client-scaling-locked.md`): per-client API keys/billing · shared-runtime-with-overlay-isolation · bespoke-per-client.
4. **Activate + harden Janice/Kimi/Kortney** on real engagements.

## The one rule
**Never force M simultaneous *unsupervised* go-lives before the eval track record exists.** One unproven agent saying the wrong thing to a client's customer in week one damages the trust that *is* the business — across all M at once. Stage it; the discipline is the moat.
