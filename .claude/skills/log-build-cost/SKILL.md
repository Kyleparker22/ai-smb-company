---
name: log-build-cost
description: Log per-client token + tool spend to clients/<client>/cost.md, broken down by phase (discovery / build / tools / run). Invoke at the END of any session that did real work for a client engagement, when a tool/credit purchase lands for a client, and at Charles's monthly close for the roll-up. Owner of the roll-up - Charles.
---

# log-build-cost

## Canonical doc
`clients/_yourco-template/cost.md` (the ledger format) + CLAUDE.md §"Token economics" (why we track: yourco absorbs the spend; margin = retainer − run cost).

## When
1. **End of a client-work session** (Cowork or headless): you built, scoped, or produced something for a `clients/<client>/` engagement → append what the session spent.
2. **A tool cost lands** for a client (subscription, credits, telephony, one-time registration) → append it the day it's known.
3. **Charles's monthly close** (`finance-close` loop): roll the ledger into the phase-totals table + the Monthly run cost row, and flag any engagement whose run cost approaches its retainer.

## Steps
1. If `clients/<client>/cost.md` doesn't exist, copy it from `clients/_yourco-template/cost.md` and fill the pricing line.
2. Classify the spend into ONE phase:
   - **discovery** — audit, scoping, proposal, demos built to sell
   - **build** — implementation work through go-live (prototypes, evals, videos for the engagement)
   - **tools** — third-party $ (Vapi/Twilio/ElevenLabs/Higgsfield credits, keys, registrations); note one-time vs recurring in the What column
   - **run** — post-live operation (loop tokens, API metering, SMS volume)
3. Get the number honestly and mark the Evidence column:
   - `metered` — Anthropic console usage for the engagement's API key, a tool invoice, Twilio/Higgsfield dashboards
   - `est.` — session self-report (Claude Code `/cost`, or a stated rough estimate like "~2 hrs heavy session ≈ $X")
   - An honest `est.` beats a fake `metered`. Never leave Evidence blank; never invent precision (write "~$5" not "$5.13" if you don't know).
4. Append ONE row per spend event to the Ledger table. Append-only — never rewrite history rows.
5. Commit via `runtime/commit-scoped.sh` scoped to the cost.md (or fold into the session's normal scoped commit).

## Gotchas
- **Cowork session tokens are not auto-attributable per client.** The self-report at session end IS the capture mechanism — that's why this skill exists. Don't skip it because the number is rough.
- **Products with their own API keys** (e.g. Sample Product's verify layer) CAN be metered — prefer a per-engagement Anthropic key at go-live so the console gives real per-client numbers. Say so in the ledger's Evidence column.
- Internal agents (Reed, Atlas, loops working on yourco itself) are NOT client cost — that's `finance/token_spend.md`, Charles's own log.
- Pre-signature spend (Sample Client today) still gets logged under **discovery** — it's CAC evidence for Polo's pricing even if the deal never signs.
- The client NEVER sees any of this. cost.md stays internal; nothing from it goes on a client surface or invoice breakdown.
