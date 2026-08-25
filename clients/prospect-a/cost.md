# Cost to operate — Prospect A storm-alert system

*yourco's monthly cost to run this (what Nick pays is separate — Polo prices).*
*Ledger discipline from 2026-07-06: append spend events to the Ledger below via the `log-build-cost` skill (phases: discovery / build / tools / run); the estimates further down remain the operating-cost model.*

## Ledger (append-only — one row per spend event)
| Date | Phase | What | Tokens | $ | Evidence |
|------|-------|------|--------|---|----------|
| 2026-07-06 | build | **Pre-ledger backfill** — storm engine, verify layer, crew app, Cloudflare preview, auto-publisher (multiple sessions, June–July 2026). Tokens not captured at the time; ledger starts today. | unknown | unknown | est. — pre-ledger, do not invent |
| 2026-07-05 | discovery | Nick follow-up video (49s, white-label, Higgsfield + Maya VO) — credits from yourco's shared Higgsfield Plus plan | — | ~shared-plan credits | est. |
| 2026-07-28 | build | Nick's fix list: address-search Nominatim fallback (property/history/canvass), canvass county-seat fallback sampling (67-seat data file), policy watch-list keyword scanner, inline owner-PIN dialog (prompt() broke in webviews), bun.lock CI repair; 4 deploys, all verified live | ~1.5M | ~$8 | est. — Cowork session, not metered |
| 2026-07-28 | build | Learning loop shipped (storm_log history, house-attr capture, field-truth taps, profile multipliers -> feed/canvass/ROI, verdict self-scoring); INGEST_URL cut over to production host | ~800k | ~$5 | est. — Cowork session, not metered |
The point of this engagement's economics: **the value is the verification layer, not
expensive compute.** The engine is deterministic Python — it uses ~$0 in AI tokens.

## Monthly operating cost (yourco's side)
| Line | Cost | Notes |
|---|---|---|
| **AI / model tokens** | **~cents–low-$/day** | The pull + cross-verify + score engine is rule-based (~$0). The **AI verification layer** (`verify_ai.py`, added per Nick's "read all the reports" ask) does cost tokens — it reads the raw report remarks per storm to judge credibility + claim-grade. A few storms/day × ~1–2k tokens. Default `claude-opus-5`; production volume → `VERIFY_MODEL=claude-sonnet-5`/`claude-haiku-4-5` (far cheaper, plenty for reading remarks). A token bill that stops wasted crew trips + strengthens claims is money well spent. See `VERIFICATION.md`. |
| **Infrastructure** | **~$0 marginal** | Rides the always-on VPS we already run for the whole OS (~$15–30/mo total, shared across every agent/loop). Nick's loop is one more systemd timer. |
| **NOAA / NWS data** | **Free** | The insurance source of record — no cost, ever. |
| **Xweather (Vaisala)** | **$0 to yourco** | Nick has his own developer key. His account covers it (tiers range free → paid for high volume). |
| **HailTrace / Hail Maps** | **$0 to yourco** | Only if added — on Nick's own subscriptions, not ours. (May be droppable — see below.) |
| **Twilio SMS** | **~$5–25/mo** | The only real variable. Number ~$1.15/mo + A2P 10DLC campaign fee (~$2–10/mo) + ~$0.011/text all-in. E.g. 25 roofers × ~12 storm days = ~300 texts ≈ **$3–4/mo** in messages. |

### Bottom line
**~$15–40/mo** to operate — Twilio SMS plus modest AI-verification tokens (the
layer that reads the reports so Nick doesn't chase false storms). Both scale with
roster size and storm frequency, not with anything expensive. Still high-margin:
the token spend that prevents a single wasted multi-crew trip pays for months of
verification. The moat is reliability/verification, and now it's earning its tokens.

*One-time: A2P 10DLC brand + campaign registration (~$20 one-time + vetting), required before any US business SMS.*

## Source-scope decision (2026-06-30)
Nick: *"Vaisala Xweather might be enough honestly."* Likely right — **NOAA (free,
insurance record) + Xweather (his key: live alerts + hail/wind)** is a strong,
cheap two-source stack. HailTrace + Interactive Hail Maps stay wired as
"ready to connect" but are **not needed for v1** unless validation shows an
Xweather hail gap. Test: plug in his Xweather key, confirm it catches the 1.25"
hail week NOAA missed (The Villages / Kissimmee / Bunnell). If yes → ship on two
sources. Lower cost, fewer integrations, uses what Nick already pays for.
