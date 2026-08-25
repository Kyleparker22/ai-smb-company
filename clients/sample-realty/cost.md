# Cost — [[CLIENT NAME]]

> YourCo absorbs all token/model/infra spend; the client never sees it. Track it anyway so Charles can roll up margin (revenue collected − run cost) and Polo can sanity-check the retainer covers it. Log entries via the `log-build-cost` skill — at the end of any session that did real work for this client, and at Charles's monthly close.

**Pricing in effect:** build fee [[ ]] (one-time) · monthly retainer [[ ]] · vertical ref: [[pricing/v0/<vertical>.md]]

## Ledger (append-only — one row per spend event)
Phases: **discovery** (audit/scoping/proposal) · **build** (implementation through go-live) · **tools** (third-party: subscriptions, credits, telephony, keys) · **run** (post-live operation).
Evidence: how the number was obtained — `metered` (console/API usage, invoice) or `est.` (session self-report). Never leave it blank; never fabricate precision.

| Date | Phase | What | Tokens | $ | Evidence |
|------|-------|------|--------|---|----------|
| 2026-08-04 | discovery | Website demo build-out, full day (Cowork session): real listings + galleries from Canopy portal, listings-first redesign per Kimi, detail-page template + cinematic tours, services/mortgage/closing-costs/resources pages, testimonials revamp, then the lead-gen slate — home-worth CMA magnet, results case studies + stats, ST-vs-SC comparator, neighborhoods, new-construction guide, investor analyzer, concierge widget, market-pulse/private-list/valuation homepage bands | ~1.5M (session, est.) | ~$25 (est.) | est. |
| 2026-08-04 | tools | Higgsfield seed_audio — 60s demo narration track for the High Brook narrated tour (Maya voice) | — | 5.4 credits | metered (preflight get_cost) |

### Phase totals (Charles updates at monthly close)
| Phase | Tokens | $ | As of |
|-------|--------|---|-------|
| discovery | | | |
| build | | | |
| tools (one-time) | | | |
| run (cumulative) | | | |

## Monthly run cost
| Month | Model/tokens | Voice (ElevenLabs) | Telephony (Twilio) | Other tools | Total | Retainer | Margin |
|-------|--------------|--------------------|--------------------|-------------|-------|----------|--------|
| [[YYYY-MM]] | | | | | | | |

## Notes
[[Anything that affects unit economics — call volume spikes, voice minutes, model choice. Flag to Charles if run cost approaches the retainer.]]
