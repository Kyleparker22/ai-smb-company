# 20-industry campaigns + target spec

> The turnkey plan to prospect ~20 industries (500 US prospects each, 1 per company, owner-level, with email) and the tailored campaign per industry. **Sourcing is gated on a Vibe credit spend (the Founder's call — see `pricing` note below); campaigns + targeting are built free here.** Sending stays gated until launch (email-first, no cold SMS, FTSA — Rafi). Owners (split 2026-06-15): **Reilly** = targeting + sourcing + campaign ops; **Michelle** = the per-vertical messaging/copy/angles. Master sequence + merge vars: `sequence-copy.md` (Michelle); engine: `proof-led-outbound-engine.md`.

## Sourcing spec (apply to every industry)
Vibe `fetch-entities` → `export-to-csv`, per industry:
- `entity_type: prospects` · `number_of_results: 500` · `max_per_company: 1`
- `prospect_country_code: ["US"]`
- `company_size: ["1-10","11-50"]`  *(owner-operated SMBs — the ICP)*
- `job_title: ["owner","owner op","the owner"]` (+ `president`, `founder` where useful) — the decision-maker
- `has_email: true` → then **enrich** for the email values (extra credit cost)
- **Qualification pass:** NAICS over-includes (~40% noise: wholesalers, e-comm, enterprise). Over-pull slightly and cut anything that isn't an owner-operated *service* business that takes inbound customer calls.

## Cost (per `show-pricing-plans`, 2026-06-13)
~1 credit/row export + enrichment for emails → **~20k credits for all 20×500 with emails ≈ Elite ($649.99)**. Start smaller to validate (Boost $90/3k ≈ 3 industries; Ultra $200/8k ≈ 8). Credits valid 365 days. **the Founder purchases; the agent cannot.**

## The 20 industries — NAICS + the pain + the Touch-1 hook
Touches 2–4 (the math · the trust · the breakup), the SMS, and the CAN-SPAM footer all inherit `sequence-copy.md`. Each Touch-1 leads with a **personalized demo** of *their* business (`prospect-demo.html` style).

| # | Industry | NAICS | The pain (the hook) | Touch-1 subject |
|---|---|---|---|---|
| 1 | Landscaping / lawn | 561730 | Misses calls on the job site → lost estimates | `built an AI front desk for {{company}}` |
| 2 | HVAC / plumbing | 238220 | After-hours emergencies go to voicemail | `{{company}}'s after-hours calls, answered` |
| 3 | Roofing | 238160 | Storm-surge leads die in voicemail | `every roofing lead {{company}} misses` |
| 4 | Electrical | 238210 | Service calls missed while on a job | `an AI dispatcher for {{company}}` |
| 5 | General contractor / remodel | 236118 | Bids stall; inquiries unanswered for days | `{{company}}: never lose a remodel lead` |
| 6 | Dental | 621210 | Missed calls = lost new patients; insurance Qs | `more new patients for {{company}}` |
| 7 | Chiropractic | 621310 | New-patient calls go unanswered | `{{company}}'s front desk, 24/7` |
| 8 | Veterinary | 541940 | Anxious owners can't get through | `an AI front desk for {{company}}` |
| 9 | Optometry | 621320 | Booking + recall calls missed | `keep {{company}}'s chairs full` |
| 10 | Physical therapy | 621340 | Referrals lapse without fast intake | `book {{company}}'s referrals faster` |
| 11 | Auto repair | 811111 | Phone rings while under a hood | `{{company}}: stop missing service calls` |
| 12 | Auto dealer | 441110 | Inbound + trade inquiries slip | `an AI BDC for {{company}}` |
| 13 | Restaurant | 722511 | Reservations + catering inquiries missed | `catering leads {{company}} is missing` |
| 14 | Fitness / gym | 713940 | Membership inquiries go cold | `turn {{company}}'s inquiries into members` |
| 15 | Hair / nail salon | 812112 | Booking calls during appointments | `{{company}}'s booking line, always answered` |
| 16 | Spa / med-spa | 812199 | Consult inquiries lost; no after-hours | `more booked consults for {{company}}` |
| 17 | Real estate | 531210 | Buyer/seller leads need instant response | `respond to {{company}}'s leads in seconds` |
| 18 | Law firm | 541110 | Intake calls missed; conflict-checked intake | `an AI intake coordinator for {{company}}` |
| 19 | Accounting / CPA | 541211 | Season overflow; client calls missed | `{{company}}: handle season overflow` |
| 20 | Insurance agency | 524210 | Quote requests + service calls slip | `quote requests {{company}} is losing` |

> **Sub-vertical rider (2026-07-05):** when a **Restoration** campaign is stood up from the 50-list, include **crime scene / biohazard cleanup** operators in its pull — same insurance-paid, 24/7-emergency-intake pitch, too small a niche for its own campaign (`decisions/2026-07-05_boring-business-verticals.md`).

## Run order (when funded)
1. Pull industry 1–3 (Boost-tier validates quality + the qualification pass).
2. Confirm clean → enrich emails → into CRM (`source: "Vibe — <industry> US"`).
3. Pre-generate personalized demos (Mode A) for each.
4. Stage the per-industry campaign in Instantly — **paused** until launch.
5. Scale to the remaining industries.

> Honesty + compliance: sourcing is internal prep; nothing sends until OtherVenture clears + Rafi clears CAN-SPAM/TCPA/FTSA. Email-first; no cold SMS.
