# Multi-client scaling — open items to lock before client #2

**Date:** 2026-06-23
**Status:** ⚠️ **SUPERSEDED — LOCKED 2026-06-30** in `decisions/2026-06-30_multi-client-scaling-locked.md` (pulled forward so a sign-on surge doesn't force them under fire). This doc is kept for the options + rationale that informed the locks. *(Was: OPEN — deferred to client #2.)*
**Owner:** the Founder decides; Kemba (platform/runtime) builds. Context: `03_internal_platform.md` → "Multi-client architecture."

## Why deferred (not decided now)
Pre-revenue, one engagement in flight (Sample Client, unsigned). Deciding per-client isolation/billing before a real client is the "shiny tools" trap — over-engineering for scale that doesn't exist yet. The architecture is *designed*; these three calls get *locked* the moment a 2nd client makes them real. Recording them now so they aren't discovered late.

---

## 1. Per-client API keys / billing isolation
**Question:** one shared Anthropic (and Vapi/Twilio/etc.) key across all clients, or a key per client?

- **Shared key (today, v0):** simplest; fine at 1 engagement. Risks at scale: a single billing failure ("credit balance too low") takes **every** client down at once (already happened — `learnings/ops/2026-06-18_runtime-silent-credit-death.md`); cost attribution is by tagging/`cost.md` only; one client's runaway eats the shared rate limit.
- **Per-client key/billing:** clean cost attribution, blast-radius containment, independent rate-limit headroom, and a clean story for "you never see the tokens." More setup + key management overhead.
- **Lean recommendation:** stay shared through engagement #1; **move to per-client keys (or per-client cost-attribution at minimum) at #2**, with auto-reload + the API-independent alarm kept on the shared/billing account regardless.

## 2. Per-client runtime isolation
**Question:** all clients' agents run on one shared runtime (isolated by config/credentials/overlay), or isolated compute per client?

- **Shared runtime + overlay isolation (today):** matches the "one golden template, client logic as overlay" model; cheapest; the separation is logical (separate `clients/<client>/`, creds, tenants), not physical.
- **Isolated compute per client:** stronger blast-radius + data-handling posture (matters for regulated/PII-heavy clients — e.g. Conduit/immigration, caregiving); more infra to run.
- **Lean recommendation:** shared runtime + strict overlay/credential isolation by default; **isolated compute only when a client's data sensitivity or procurement requires it** (Kemba's call when extracting template patterns; Rafi's compliance posture informs it).

## 3. Multi-tenant vs bespoke per client
**Question:** is the deliverable an isolated bespoke OS per client, or genuine multi-tenant software?

- **Bespoke OS (default for the core boutique offering):** per-client isolated overlays on the shared template. Maximum fit + isolation; the moat lives here.
- **Multi-tenant (for productized verticals):** e.g. the Conduit IEN-immigration spec is multi-tenant by design (`decisions/2026-06-18_conduit-ien-immigration-offering.md`, open: "multi-tenant vs bespoke"). One codebase, many firms — different economics + isolation model.
- **Lean recommendation:** keep the **core OS bespoke/isolated**; treat **multi-tenant as a per-vertical-product decision** (decided when a vertical like Conduit is actually built), not a default for the core.

---

## Trigger / revisit
Lock #1 and #2 **before onboarding client #2**; lock #3 **per vertical product** as each is built. Re-open if a regulated client (PII/SOC2/GDPR) signs first — that pulls #2 forward. When decided, supersede this with the locked calls + update `03_internal_platform.md`.
