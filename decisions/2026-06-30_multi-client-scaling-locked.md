# Decision — Multi-client scaling: the 3 calls, LOCKED

**Date:** 2026-06-30 · **Owner:** the Founder (decides) + Kemba (builds) + Rafi (controls) · **Status:** LOCKED · **Supersedes the open items in** `decisions/2026-06-23_multi-client-scaling-open-items.md`

Pulled forward (vs. "decide at client #2") so they're not made under fire during a sign-on surge (`processes/delivery-surge-playbook.md`). These firm up the lean recommendations from the open-items doc into standing policy. Implementation lands as the first client does — Kemba builds it into onboarding/runtime; the *policy* is set now.

## 1. Per-client API keys + billing isolation — LOCKED: per-client from client #1
Each engagement gets its **own scoped API credentials** (Anthropic + any per-client service keys), not a shared key.
- **Why:** clean **cost attribution** (margin-per-client is the metric that matters); **blast-radius containment** — one client's runaway spend or a billing failure can't take the others down (the shared-credit-balance death already happened once, `learnings/ops/2026-06-18_runtime-silent-credit-death.md`); **independent rate-limit headroom** so a surge of 5 doesn't throttle each other.
- **Always-on regardless:** auto-reload + the API-independent alarm on every billing account.
- **Builds:** Kemba bakes per-client key + cost-attribution scaffolding into onboarding; Janice provisions it per client.

## 2. Per-client runtime isolation — LOCKED: shared runtime + strict overlay isolation (default); isolated compute by exception
The default is **one shared runtime** with isolation that is **logical, not physical**: separate `clients/<client>/` overlays, separate tenant credentials, separate eval/approval/cost-tracking per engagement.
- **Exception:** isolated compute per client **only when data sensitivity or procurement requires it** (regulated / PII / SOC 2 / GDPR — e.g. Conduit/immigration, caregiving). **Rafi's compliance posture is the trigger**; Kemba builds it when called.

## 3. Multi-tenant vs bespoke — LOCKED: core OS is bespoke/isolated per client; multi-tenant is a per-vertical-product call only
The **core boutique offering stays bespoke** — a per-client isolated overlay on the shared golden template (maximum fit + isolation; the moat lives here).
- **Multi-tenant software is decided per vertical product** (e.g. the Conduit IEN-immigration spec, `decisions/2026-06-18_conduit-ien-immigration-offering.md`), never the default for the core. One codebase / many firms is a different economics + isolation model that gets its own decision when a vertical is actually built.

## What changes in the OS
- `03_internal_platform.md` "Multi-client architecture" → open items now LOCKED (points here).
- `processes/launch-runbook.md` scale-readiness cluster → items locked.
- `dashboard/data.json` `scaleReadiness` → status locked.
- `decisions/2026-06-23_multi-client-scaling-open-items.md` → superseded by this.
- Surge handling: `processes/delivery-surge-playbook.md`.
