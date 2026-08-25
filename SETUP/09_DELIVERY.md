# 09 — Delivery: audit to AI OS

> **Build step 09.** Nothing here is done yet. Where this page shows a filled-in value, that is
> the source company's — replace it with yours.

## The loop

discovery → build → eval/gates/watchdogs → 48h go-live → weekly iteration → account expansion.
Full SOPs: `02_delivery_loop.md`.

**Stage 0 — when a client folder gets created:** first real call *or* proposal sent, whichever comes
first. Skill: `.claude/skills/scaffold-engagement/`.

## The Audit — the product demo

`processes/audit-sop.md`. Roughly a week, ~4–6 hours of the client's time. The diagnostic call runs
**five question blocks** in order: the money map, the time map, the breakage map, the readiness check,
and — added 2026-08-24 — **the control map**.

Block E is the one that gets skipped for time. Don't. Every answer has a mechanical destination:
what it must never touch becomes the deny-list, what needs checking becomes the R1 floor, and
**"what would you need to see before you'd let it do this without asking?" becomes the promotion
criterion, in the client's own words.** That single answer converts "trust us" into a condition the
client set themselves.

Never say *autonomy*, *guardrail*, or *governance* on that call. Ask it in the owner's language.

**Numbers, not adjectives.** Every dollar figure is computed from the client's own inputs with the
arithmetic shown. "Slow" and "a lot" are not findings.

## Scoping — the eight pillars

Intake · Sales · Marketing · Customer · Operations · Back Office · Company Brain · Training
(`processes/ai-os-modules.md`). Every bottleneck maps to one; that mapping is what turns "they're
drowning" into a scope.

Modules ship in **three form factors**: a digital employee, a headless automation, or an **embedded AI
surface** (a client-facing AI product). "No agent attached" is a shape, not a gap.

Tiers by scope: **Core** (~3 agents) · **Suite** (~5) · **Operation** (~7) · **Command** (up to 10).
Agent count is an *included guide*, **not a per-agent meter**. Polo owns the bands; advisors scope,
they do not quote.

## The client folder

Everything for a client lives in `clients/<name>/` — proposals, demos, platforms, meetings, cost
ledger. The golden template is `clients/_yourco-template/`, and **client logic is overlay only**.
Each `_README` carries the "how the OS works this client" agent map.

Before go-live: `runtime/pregolive.py` fires injected data states at a client agent with the network
blocked by construction. It calls itself **a smoke test, not an eval set** — and no adapter reads
*cannot-simulate*, which is a blocker, not a pass.

## The first engagement

**Sample Client** — hardscaper, the Client Owner. The engagement *is* the Design Studio / Field-to-Quote
platform. Integration board green since 2026-08-18. **At Proposal stage, unsigned, pre-revenue.**
the Founder runs engagement #1 personally to harden the playbook, then it hands to Janice/Kimi.

## The token economics

yourco absorbs the model spend; the client never sees a token. **That is the business model, not a
bug.** A high token bill is good news if outcomes are landing — it means expensive headcount was
replaced on both sides. Log it per session with `.claude/skills/log-build-cost/`.

⚠️ Bain (June 2026): token consumption grew **4.5×** year-over-year while per-token price fell only
half, so effective cost-per-task stayed flat. The absorbed-spend model gets *harder*, not easier, as
agents take on more. The cost ledger is load-bearing, not hygiene.

## Done when

**you have run the audit conversation once, start to finish, with a real owner.**

If you cannot point at that, the step is not finished — do not move on.
