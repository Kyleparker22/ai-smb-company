# runway.md

Updated at each monthly close (first Monday of each month). Source of truth for cash, MRR, burn, and runway.
See `/finance/README.md` and `monthly_close.md`.

## Current snapshot — as of 2026-08-05 (the Founder supplied cash)
| metric | value | notes |
|--------|-------|-------|
| Cash on hand | **$0** — supplied by the Founder 2026-08-05 | The #1 carried blocker is closed, and the answer is the hard one: the company holds no cash. Consistent with the observed pattern (Jun 1 card decline · Jun 16–18 credit lapse · Jul 9+20 Hostinger failures · Jul 10–12 Descript failures · the API balance hit zero ~Jul 30 and killed the 08-03 close). **The API is no longer dark** — credits restored 2026-08-04, and the meter reads `connected: true` with $80.02/30d as of 08-21. |
| **Runway** | **0.0 months** | = $0 ÷ any burn. The company is **cash-insolvent against ~$614.22/mo of obligations** and is operating only to the extent the Founder personally funds charges as they arrive. |
| MRR | $0 | Pre-revenue, no active engagements. |
| Monthly burn (fixed recurring) | **~$614.22/mo** (all confirmed subs) → **~$503/mo** if the duplicate Instantly Hypergrowth is cancelled and Granola downgrades | ⚠ **Restated 2026-08-03 (+$200):** the Claude **Max 20x** subscription ($200/mo, first receipt Jul 27) was off-book, so every figure published through the 07-27 pulse understated fixed burn by ~48%. Full line: Google $8.73 + Instantly $291 + Canva $18 + Plausible $9 + ElevenLabs $6 + Tailscale $8 + Hostinger $24.49 + Descript $35 + Granola $14 + Anthropic Max $200. **Plus API/token spend + usage tools.** |
| Confirmed June cash out | **$405.73** | Receipt-sourced; excludes Anthropic top-up (amount TBD) + TBD tiers. See `readouts/2026-06.md`. |
| Prior runway line (June close) | was "not computable" | Superseded by the $0 figure above. |

> ⚠ **BURN IS MATERIALLY UNCERTAIN AS OF 2026-08-17.** Five recurring renewals in the Aug 8–10 window — Instantly $291, Granola $14, ElevenLabs $6, Hostinger $24.49, Descript $35 (**$370.49, or 60% of fixed burn**) — produced **no receipt and no failure notice**. Every one of these vendors emailed a receipt in July, so the silence is real signal, but it points two opposite ways: either the triage below **was executed** (→ floor ~$268/mo) or the charges **failed silently** against card ••2296 (Citi past-due notice Aug 4, collections notice Aug 7). **The $614.22 figure is retained as the last *confirmed* number and has deliberately NOT been restated on absence** — per `learnings/ops/2026-08-07_absence-is-invisible-to-this-os`, silence is not clearing evidence in either direction, and a burn figure encoding a flattering guess is worse than one encoding a known unknown. One card-statement lookup settles it. Full analysis: `loops/finance/2026-08-17.md`.

## Burn triage — recommended at $0 cash (2026-08-05; the Founder executes the cancellations, Charles books them)
With zero cash, every non-essential dollar of the ~$614.22/mo fixed burn is borrowed from the Founder personally. Recommended cuts, largest first — **~$343/mo → ~$271.22/mo**:
| Action | Saves | Rationale |
|---|---|---|
| Cancel BOTH duplicate Instantly subs → keep ONE ($97) | **$194/mo** | 3 subs ($291) for a sending machine that is OtherVenture-gated from sending anything. One keeps the domain warmup + staged campaigns alive. (The known duplicate alone is $97; the second Hypergrowth-vs-CRM call is the Founder's.) |
| Descript — cancel (it's already failing to bill) | **$35/mo** | Reed's assembly tool; video production is paused by reality. Re-subscribe when a production is actually scheduled. |
| Granola → free tier | **$14/mo** | Was "staying free" per the 2026-06-09 note; the Business charge contradicts it. |
| Plausible — pause | **$9/mo** | Analytics for a site with no launched traffic; script wasn't even installed. |
| **Keep (essential):** Google Workspace $8.73 · Hostinger VPS $24.49 (**pay the overdue bill — 2 failures; suspension = whole-OS-dark**) · Tailscale $8 · one Instantly $97 · Canva $18 · ElevenLabs $6 · Claude Max $200 (the compute this session runs on) | | ≈ **$362/mo floor** — or ≈ $271/mo if Canva/ElevenLabs also pause (Reed-stack, same logic as Descript) |
| ~~API top-up + **auto-reload on a funded card**~~ → ✅ **DONE 2026-08-04** | one-time | Receipt-confirmed at the 08-17 pulse: **#2972-0375-0610 $20.00 one-time credits + #2501-4380-3148 $15.70 "Auto-recharge credits."** The auto-reload the runtime died twice without is now **on**. ⚠ The caveat in this row still stands and was the right one: the increment is $15.70, one loop run costs $4.42, and the card it bills threw a past-due notice Aug 4 — **auto-reload on an underfunded card relocates the failure rather than removing it.** Size the increment + confirm the funding source. |

## How to update
At each monthly close: set cash on hand from the bank statement, pull net from `revenue.md` − (`expenses.md` + `token_spend.md`), update MRR if any engagements are live, then recompute burn and runway.

## History
| close_date | cash | mrr | burn | runway_months |
|------------|------|-----|------|---------------|
| 2026-08-05 (the Founder supplied) | **$0** | $0 | ~$614.22/mo fixed (pre-triage) | **0.0** |
| 2026-07-06 (June close) | TBD | $0 | ~$146.73–$340.73/mo fixed + model spend TBD | not computable (cash unset) |
| 2026-08-24 (**July close**, 21d late) | $0 (dated 2026-08-05; the 07-31 figure was never captured) | $0 | $537.00 paid + $20.15 API in July; $83.98 failed | **0.0** |
