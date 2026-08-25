# Eval — Twenty CRM as a client-facing OS component (operated CRM deliverable)

**Date:** 2026-06-18 · **Owners:** the Founder + Kimi (build patterns) + Kemba (runtime/hosting) · **Status:** **candidate — eval-gated** (not a commitment; validate before it's load-bearing on a client)

## The question
A clean setup guide (Twenty open-source CRM + Claude over MCP) surfaced a strategic fit. Two layers, kept separate:
1. **Internal CRM:** unchanged — stays native (`crm/`, David). Settled in `decisions/2026-06-14_crm-build-vs-buy-attio.md`. Twenty is *not* a reason to revisit that; the native CRM *is* the OS (one git-backed source of truth all agents read/write). This note is **not** about our own pipeline.
2. **Client deliverable (new):** today our SMB engagements run intake/booking/follow-up but we have **no defined answer for where the client's pipeline lives.** That's a gap. Twenty is a strong candidate to fill it as an **operated CRM** we deploy and run for clients.

## Why Twenty fits the moat almost exactly
- **Runs one-click on Hostinger** — the *same* stack we already operate the always-on runtime on (`runtime/README.md`). No new vendor, same ops surface, Docker/compose we already understand.
- **Native MCP server on every workspace** → the client's digital employees (our agents) operate the client's CRM directly — read leads, draft follow-ups, log activity, advance stages. *That is the moat*: the client never touches it; yourco owns reliability/eval/approval on top.
- **Open-source / self-hosted = data ownership** and no $80–100/seat Salesforce/HubSpot tax passed to an SMB. We absorb a trivial hosting cost (the token-economics model: we eat infra, client gets an outcome).
- **Custom objects/fields, Kanban, automations, dashboards out of the box** — the commodity CRM substrate, already mature (45k GitHub stars), so we don't rebuild it.

## The build-vs-deploy call (the Founder's open question: deploy Twenty, or build our own like yourco's native?)
**Recommendation: deploy + operate Twenty for clients. Do *not* build a bespoke client CRM from scratch.** And reframe the "as good or better than Twenty" bar:

- **Our native CRM works *because it is the OS*** — a single git-backed file every yourco agent parses directly. A *client's* CRM has none of those properties: it's a standalone, multi-tenant, per-client deliverable; the client's own staff may glance at it; it must scale to thousands of records, want drag-drop Kanban, and run isolated per client. That's exactly where JSON-in-git breaks and exactly Twenty's strength.
- **Building + maintaining a multi-tenant CRM per client is a CRM-company's full-time job.** Doing it ourselves would pull focus from the moat (operating the OS) into competing with a mature open-source project — the self-serve-SaaS drift trap in a new costume. We don't win by out-building Twenty's CRM.
- **The "as good or better" bar belongs on the operating layer, not the CRM.** The moat is never "we built the CRM" — it's "we *operate* it reliably with eval + approval + the client console on top." Twenty is the commodity substrate; **our agents + gates + reliability are what must be better than anyone else's.** Match Twenty by *using* it; win on the layer above it. Bespoke needs become custom objects/fields *on* Twenty, not a from-scratch system.
- **When we'd build instead (the only triggers):** multi-tenant isolation, branding, or clean data-portability prove unworkable on Twenty in eval; or a vertical needs a data model Twenty genuinely can't express. Default until then: deploy + operate.

This mirrors the internal decision one layer up: *native where it’s the OS; benchmark-and-deploy where it’s a commodity substrate we operate.*

## What to validate before it touches a client (the eval gate)
- **Multi-tenant isolation** — one Twenty instance per client vs. one shared. Per-client Docker on Hostinger is cleanest for data isolation + the pause/resume billing model; confirm cost/ops at ~5–10 instances.
- **Agent-operability over MCP** — drive a full loop headless from our runtime (read cold deals → draft follow-ups → log activity → advance stage) under the approval gate (drafts/writes confirm-to-save; **no auto-send**, same posture as David/Melanie). Scope the MCP API key to a limited read-write role, never admin (their guide's own advice — it's our gate philosophy).
- **Branding** — can it present white-labeled / client-branded enough, or does it read as "a Twenty install"? Affects whether it's client-facing or a back-office tool the agents run.
- **Pause/resume** — clean per-client pause/resume to match Ready-to-Hire billing (`decisions/2026-06-16_two-motions-productized-employees.md`, the open platform item). A Docker instance is easy to stop/start.
- **Data portability / exit** — client owns their data; clean export if they leave (open-source helps here).
- **Bulk-write safety** — confirm before any mass/destructive write (the guide flags this; it's already our gate).

## How it would package
- A standard **OS build-stack component** (alongside Vapi for voice) — *not* a tool we "subscribe" to; an open-source substrate we self-host + operate. Goes into Kimi's golden build patterns once eval clears.
- Could also surface as a **Ready-to-Hire-adjacent / OS-add-on** ("operated CRM, run by your employees") once **Polo** prices the operating retainer. The software is ~free; we charge for the operated reliability layer, consistent with the model.

## Owners
**Kimi** (golden build pattern once eval clears) · **Kemba** (Hostinger hosting + per-client isolation + pause/resume) · **David** (informs the data model from internal CRM experience; does *not* own client instances) · **Polo** (prices the operated offering) · **the Founder** approves. Eval against `processes/eval-rubric.md` before any client deployment.

## Status
Candidate logged 2026-06-18. Eval-gated — staged behind the launch-gate + a real engagement that needs it, like everything external. The internal CRM is untouched. Lift cheap patterns into the native CRM regardless (see `crm/_backlog.md`).
