# 2026-06-07 — SMS added as channel 2 to Reilly's outbound stack

## Decision
Add **SMS as channel 2** in Reilly's multi-touch outbound. Tool: **Instantly Hyper CRM tier ($97/mo)** — same vendor as email, integrated sequences, in-product 10DLC support. Per-vertical channel selection joins pricing as a Polo decision; SMS approved for landscaping/hardscaping in this same session.

## Context
- Reilly is pre-first-run. Adding SMS now (before scale) is cheaper than retrofitting after she's running email-only campaigns.
- Lead vertical (landscaping/hardscaping) has owner-operator buyers who are mobile, on-site, and text-native. Email reaches them but is slower than texts in their day-to-day operating mode.
- Multi-channel email + SMS produces 30–40% higher response rates per Instantly's own published data.
- Compliance posture has hardened since Feb 2025 (10DLC enforcement) and FL is a high-litigation state for SMS — adding SMS to the stack means hardening Reilly's pre-send gates first, not last.

## Options considered

### Tool
- **JustCall** ($29–89/user/mo, 2-user minimum) — rejected. Powerful but solo-founder unfriendly minimum; another vendor / login / billing line.
- **Salesmsg** ($25–249/mo credit-based) — rejected. Credit-based pricing is operationally noisier than flat; separate billing and reconciliation.
- **Aloware** ($30/user/mo per seat) — rejected. Per-seat overhead even for solo; integrated calling features YourCo doesn't need at v0.
- **Twilio (direct)** — rejected. Maximum flexibility, but Reilly would have to build the orchestration we'd otherwise get from Instantly.
- **Instantly Hyper CRM ($97/mo)** — **chosen.** SMS steps interleave into the same sequences as email; 10DLC handled in-product; no new vendor; no MCP/API wiring beyond what Reilly already does for Instantly email.

### Architecture
- **Separate SMS pipeline parallel to email** — rejected. Defeats the purpose of multi-channel; sequencing across channels requires shared state.
- **Email-first with SMS interleaved** — **chosen.** SMS touches are *inside* the email sequence, sharing prospect state, reply tracking, suppression list, and approval gate.

### Channel applicability
- **SMS everywhere** — rejected. Cold-texting wealth management or law firm decision-makers clashes with executive-trust positioning and creates real compliance risk in high-litigation verticals.
- **SMS per vertical** — **chosen.** Channel selection joins pricing as a Polo per-vertical decision. Verticals approved for SMS: landscaping, roofing, hardscaping, real-estate brokerages, plumbing/HVAC. Verticals NOT approved for SMS at v0: law firms, wealth management, insurance/adjusting.

## Why this won
- **Single-tool architecture preserved** — Reilly's pipeline stays clean; adding SMS doesn't restructure her stages, just adds steps inside one existing tool.
- **Compliance handled in-product** — 10DLC registration shepherded by Instantly rather than self-managed; STOP keyword handling configurable; opt-in/opt-out tracked.
- **Per-vertical gating protects the brand** — formal-communication verticals stay text-free; trade/services verticals get the channel their buyers actually prefer.
- **Cadence lift is real** — Day-3 SMS after Day-1 email is a known multi-channel pattern; trade owners respond to texts faster than email.

## Compliance gates — non-negotiable, hard pre-send
1. **10DLC brand + campaign registration complete** (sending domain `mail.yourco.com`, 1–4 week lead time, carrier-approved)
2. **STOP opt-out keyword** in every message (single-word unsubscribe)
3. **Sender identification** in every message ("the Founder at YourCo —" or equivalent)
4. **DNC list scrub** before every batch
5. **FTSA (Florida Telephone Solicitation Act) legal review** for first FL batch — Florida is high-litigation, B2B carve-out is narrower for mobile recipients (which landscapers almost always have). Ray reviews when Ray is built; until then, outside counsel one-time review.
6. **Per-vertical Polo lock** — Reilly cannot send SMS into a vertical that doesn't have SMS approved in its Channels section.

## Suggested landscaping cadence (v0)
| Day | Channel | Purpose |
| --- | --- | --- |
| 1 | Email | Intro + moat positioning |
| 3 | SMS | "Sent you an email yesterday — did it land? — the Founder, YourCo" |
| 7 | Email | One concrete outcome (e.g., "Janice in St. Pete saves 14 hrs/week on intake") |
| 10 | SMS | Different angle, different time of day |
| 14 | Email | Soft CTA — 15-min call |
| 21 | SMS | Break-up — "Last one from me. Worth a quick reply?" |

Six touches over three weeks. Every text ≤ 160 chars, signed, opt-out clear.

## Cost impact
Reilly's Instantly tier moves from email-only (~$37–97/mo depending on plan) to **Hyper CRM at $97/mo flat.**

## Reversibility
- **Reversible:** drop the Hyper CRM tier and revert to email-only.
- **Harder to reverse:** 10DLC brand registration ties to the sending domain — pick `mail.yourco.com` once and don't churn.
- **Revisit if:** FL FTSA risk produces enforcement action; SMS deliverability craters; Instantly's SMS feature proves underbuilt; a vertical's actual response rate doesn't justify the $97/mo tier.

## What this unlocks
- **Reilly v0 SMS stage** — interleaved into existing email sequence; gated by 10DLC + FTSA review.
- **Polo's scope expansion** — per-vertical channel selection joins pricing.
- **Landscaping cadence design** — six-touch multi-channel over 3 weeks.
- **Vertical playbook pattern** — `/pricing/v0/<vertical>.md` now carries pricing *and* channels; each new vertical Polo locks comes with channel approvals.

## Sources reviewed
Instantly SMS feature docs + Hyper CRM tier announcement; B2B SMS Strategy & Compliance 2026 (Prospeo); 10DLC platform compliance comparison (Beconversive 2026); JustCall 2026 pricing; Salesmsg pricing; Aloware platform overview; FL FTSA 2023 amendment summary (independent legal review pending Ray).
