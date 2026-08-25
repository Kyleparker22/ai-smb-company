# YourCo Internal Platform

Two components. Both are versioned. Both compound. They are what let a 1-to-few-person consultancy carry 10+ active clients without melting.

> **Scope of this doc:** `yourco-template` and Atlas — the two things that make *client delivery* scale. The platform has grown past those two since this was written; §"The rest of the platform" at the bottom names what else exists and where each is documented. This page stays the delivery-scaling doc rather than becoming a second CLAUDE.md.

---

## `yourco-template`

The golden client template. Every engagement starts here.

### What the template owns
- agent harness and orchestration
- eval harness scaffolding (test runners, fixture management, scoring)
- watchdog scaffolding (drift, cost, error-pattern, out-of-scope detectors)
- standard integrations: Gmail/Outlook tenant onboarding, calendar, common ERP/CRM hooks
- approval flow primitives (request-approval, log-decision, audit-trail)
- executive-readable reporting primitives (one-pager generator, weekly readout)

### What the template does NOT own
Anything client-specific. Client logic is overlay on top of the template, never a fork.

### Rule
If a build requires forking the template instead of overlaying, that is a missing abstraction. Capture it in `decisions/` and roll it into the next template version. The template only gets stronger.

### State (filled 2026-08-23 — these were "the Founder to fill in" placeholders since June)
- **Version: v1.1**, last touched 2026-08-18. Owner: Kemba. Versioned in
  `clients/_yourco-template/CHANGELOG.md`; 49 files.
- **Known missing abstractions: none captured yet — and that is a fact about our evidence, not about
  the template.** The rule above says a fork reveals a missing abstraction, but abstractions are only
  discovered by real engagements, and **no client has reached Build.** v1 and v1.1 were both *frontier
  hooks installed ahead of clients* (understudy, consent form), not gaps extracted from delivery.
  Expect the first real gap list from Sample Client's build, not before.
- **Next upgrade: whatever the first engagement forces.** Deliberately not a roadmap — pre-client
  template roadmapping is how you build abstractions nobody needed.

---

## Atlas

YourCo's ops agent. Atlas does for YourCo what the digital employees do for clients — but for YourCo's internal ops. Atlas is itself an YourCo digital employee.

### What Atlas owns
- **Monitoring** across all active engagements — agent health, eval status, watchdog signals
- **Triage** of watchdog signals — severity-rank, route to the right place, ack
- **Cost tracking** per engagement — token spend, by client, by use case, with trend
- **Alerting the Founder** when something needs his attention, and resolving silently when it doesn't

### Why Atlas exists
A solo founder cannot watch ten agents at once. Atlas is the watcher. Without Atlas, scaling past three concurrent engagements is the breaking point.

### State (filled 2026-08-23)
- **Live:** three loops carry `Owner: Atlas` — `monday-briefing`, `sales`, `watchdog`. Newest briefing
  artifact 2026-08-17. Docs in `agents/atlas/` (discovery/build/eval/go-live + `cost.md`).
- **Mocked / not real yet:** the per-engagement cost rollup and the eval-status monitor both assume
  live clients. With zero clients they have nothing to roll up — they are written, not exercised.
- **Known gap, and it is the honest one:** Atlas is described here as the watcher that makes 10 clients
  survivable, and **that claim is untested at n=0.** What Atlas demonstrably does today is report on
  yourco's own loops. Treat "Atlas scales delivery" as designed, not proven.
- **Atlas's own eval set:** `agents/atlas/03_eval.md` (71 lines). Kolby audits it — the watcher is
  itself watched, which is the point.
- **Cost budget:** the watchdog thresholds in `03_eval.md` (flag a run > $0.50, a week > $2) are
  acknowledged in the roster as outdated but not absurd. Real per-run cost now lands in
  `loops/_agentops/runs.jsonl`; org-wide spend reconciles via `runtime/cost_reconcile.py`.

---

## Naming convention for digital employees
Each digital employee gets a real name (not "Agent 1") and a real email address in the client's tenant. Names should feel like teammates — recognizable, memorable, professional. Atlas is the in-house example. The naming choice itself is part of the executive-trust layer.

---

## Multi-client architecture — how it scales to 10+ without melting

> The question every founder asks: *"At 10 clients, where does each client's AI live, how do I keep them separate, and do I have to worry about token cost?"* This is the answer. Added 2026-06-23 (from a founder walk-through). Status: the model is **designed now, hardened as real clients arrive** — Kemba owns building it (see `04_agent_roster.md`).

### Two layers — each client engagement lives in two places
1. **The client's tenant (their world) → identity + data.** Each agent gets *its own email/identity inside the client's own Google/Microsoft tenant*, wired to *their* calendar, CRM, phone line (Vapi/Twilio for voice). The client's data stays in the client's accounts — yourco is a **scoped, client-approved guest**, not a warehouse holding everyone's data.
2. **yourco's runtime (your world) → the brain + the reliability layer.** The agent's reasoning, orchestration, eval gates, watchdogs, approval flow, observability, and cost tracking run on **yourco-managed compute** (today: the always-on runtime — `runtime/`, `decisions/2026-06-09_always-on-runtime.md`). **This is what "yourco owns the infrastructure" means** — not hosting their data; owning and operating the *reliability layer*. The defining principle holds: the client never touches a token, a model, or a server.

A client's "AI" is therefore **their tenant (identity/data) + the yourco runtime (brain/reliability), connected by scoped connectors** — not a single box.

### How clients stay separated
**One golden template, client logic as overlay** (above). Isolation comes from:
- **Separate tenants** — each client's own accounts, never a shared data pool.
- **Separate credentials/connectors** — per-client tenant access, client-approved + scoped.
- **Separate overlay** — `clients/<client>/` holds that client's config, logic, eval set, and `cost.md`; `yourco-template` is shared + versioned and **never forked**.
- **Separate eval + approval gates + cost tracking** per engagement (Atlas rolls up).

### Token / cost — a managed cost, not a scaling cliff
- **yourco absorbs the model spend; the client never sees it** (the business model — see CLAUDE.md "Token economics"). The flat retainer must be priced (Polo) to cover spend **with margin**.
- **Track per engagement** in `clients/<client>/cost.md` (ledger rows by phase — discovery/build/tools/run — via the `log-build-cost` skill); **Charles rolls it up** at the weekly pulse (capture-gap check) + monthly close (phase totals, margin). Atlas still monitors yourco's internal/own-OS spend (`finance/token_spend.md`). The metric that matters is **margin per client** (retainer − spend), not raw token count.
- **No hard wall at 10 clients** — the API bills usage, so you scale by *managing spend*, not hitting a ceiling. The real things to manage: (a) cost attribution → margin, with watchdogs flagging a runaway agent before it eats a month; (b) API rate-limit / billing tier as volume grows; (c) the **billing-failure mode** — a shared credit balance dying takes every client down at once (this already happened — hence auto-reload + the API-independent alarm, `learnings/ops/2026-06-18_runtime-silent-credit-death.md`).

### Scaling decisions — LOCKED 2026-06-30
The three scaling calls are now **locked** (pulled forward so a sign-on surge doesn't force them under fire) — `decisions/2026-06-30_multi-client-scaling-locked.md`:
1. **Per-client API keys / billing isolation** — **LOCKED: per-client from client #1** (clean cost attribution + blast-radius containment + rate-limit headroom; auto-reload + the API-independent alarm stay on every account).
2. **Per-client runtime isolation** — **LOCKED: shared runtime + strict overlay/credential isolation by default; isolated compute only by exception** (regulated/PII/procurement — Rafi's trigger).
3. **Multi-tenant vs bespoke** — **LOCKED: core OS stays bespoke/isolated per client; multi-tenant is a per-vertical-product call only** (e.g. Conduit, `decisions/2026-06-18_conduit-ien-immigration-offering.md`).

Surge handling (multiple clients signing at once): `processes/delivery-surge-playbook.md`.

---

## The rest of the platform (added 2026-08-23)

Everything above predates July. These were built after, and each is documented at its own source —
listed here so nothing operates unknown, **not** duplicated, because a copy drifts.

| Piece | What it is | Canonical source |
|---|---|---|
| **The agent substrate** | Eleven changes to how agents remember, cost, prove and decide: trigger-scoped learnings, the anti-library, the run journal (per-run cost capture), provenance-typed context, failure-traces→skill-patches, agent payroll, R1.5, calibration-gated autonomy, decaying approvals | `decisions/2026-08-13_agent-substrate-upgrade.md` · stores in `loops/_agentops/` |
| **YourCo HQ, twelve<!--#count: match dashboard/index.html /data-v="([a-z-]+)"/--> doors** | The command dashboard. `The Board` = what's open · `WBR` = the inputs you control + the case against · `Evidence` = what the OS can prove about itself · `Partners` = the three-partner view | `dashboard/_README.md` · `CLAUDE.md` §Folder map |
| **Client instrumentation** | Pre-go-live simulation, client trip-wires, the counterfactual twin — the same instrumentation pointed at the *client* rather than at yourco | `runtime/pregolive.py` · `runtime/client_tripwires.py` · `runtime/counterfactual.py` |
| **The playground** | A synthetic yourco the real code runs against — same `crm/server.py` and `dashboard/server.py` via `YOURCO_DATA_ROOT`, so the sandbox cannot drift from the product | `playground/_README.md` |
| **`Pre Build Ideas/`** | 71 industry prototypes — demo-before-Audit inventory. Adjacent to the template: each is designed to be *overlaid* per client, never shipped as-is | `Pre Build Ideas/_README.md` |
| **Safe concurrent commits** | `runtime/commit-scoped.sh` — stages only named paths under the repo lock. Multiple sessions and loops share one clone; a bare `git add -A` buries another session's work | `07_RULES.md` §Git |
| **The security model** | The deny-list, autonomy rungs and last drill result, read from live config. A control with no drill behind it reads *untested*, never *proven* | `dashboard/security_model.py` |

**How to keep this section honest:** it is a pointer table, so the only way it goes wrong is by going
short. When you build a platform-level capability, add a row. `runtime/consistency-check.py` flags this
doc if it sits untouched for 30 days while `runtime/` keeps moving — which is exactly how the 47-day
gap that prompted this section got caught.
