# Barbershop / Salon AI Front Desk — Margin Model (internal)

**Date:** 2026-07-21 · **Requested by:** Reed (demo + economics) · **Status:** planning model, NOT locked pricing
**Demo:** `index.html` in this folder · serve via `Reed-salon-voice-demo` (:8797)

> ⚠️ Salon/spa is **banded but not locked** in `pricing/v0/vertical-ranges.md` (bottom band). Per Reilly's quoting rule, Polo must lock `pricing/v0/salon-barbershop.md` before anyone quotes a real prospect. Numbers below are planning assumptions, not sourced stats — do not put any of them on an external surface. <!--#planned-->

## The use case
AI voice agent replaces (or extends) the human front desk at a barbershop/salon: answers every inbound call 24/7, books/reschedules into the real calendar, sends SMS confirmations + reminders, screens spam, escalates refunds/complaints to the owner behind the approval gate. Stack per the locked voice platform decision: **Vapi + Twilio + ElevenLabs** (`decisions/2026-06-08_Reed-production-stack.md`).

## COGS per shop (monthly run cost)

Per-minute all-in (Vapi platform ~$0.05 + STT/LLM/TTS pass-through ~$0.05–0.09 + Twilio ~$0.01): **$0.11–0.15/min · planning number $0.13/min.**

| Shop profile | Calls/mo | Avg min | Voice min/mo | Voice $ | SMS + number | **COGS/mo** |
|---|---|---|---|---|---|---|
| Solo / 2–3 chairs | ~400 | 2.0 | ~800 | ~$105 | ~$20 | **~$125** |
| Typical 4–6 chairs (central case) | ~700 | 2.2 | ~1,550 | ~$200 | ~$30 | **~$230** |
| Busy multi-chair salon | ~1,300 | 2.5 | ~3,250 | ~$420 | ~$55 | **~$475** |

SMS = confirmation + reminder per booking at ~$0.008/msg. Excludes yourco-side ops labor (weekly iteration/eval/watchdog — mostly agent time; reserve ~$150–250/mo effective if you want a conservative net line).

## Revenue & gross margin (Polo's v0 bottom-band anchor)

Anchor (à-la-carte, first employee): **$1,000 onboarding + $1,000–2,000 setup one-time + $1,500/mo retainer.**

| Shop profile | Retainer | COGS | **Gross margin** |
|---|---|---|---|
| Solo | $1,500 | ~$125 | **~92%** |
| Central case | $1,500 | ~$230 | **~85%** |
| Busy salon | $1,500 | ~$475 | **~68%** |

- Net of a $200/mo ops-labor reserve, central case still contributes **~$1,050–1,100/mo per client (~72%)**.
- **Setup economics:** first build is real hours; from the second shop on, template amortizes — token cost per build ~$50–150, so the $1–2k setup fee is mostly margin.
- **OS graduation (the flagship path):** front desk + no-show/waitlist recovery + review harvester + rebooking campaigns = a **Core OS at ~$3,000/mo**; COGS ~$400–700 → **~80% gross** at materially higher contribution per logo.

## The client-side math (the pitch, kept qualitative externally)
- Human front desk: $15–18/hr × open-hours coverage ≈ **$2,900–3,600/mo fully loaded** — one call at a time, off nights/Sundays, misses calls whenever hands are busy.
- AI front desk at $1,500/mo ≈ **half the cost, 24/7, unlimited simultaneous calls** — or it keeps the human on the floor doing revenue work instead of answering the phone.
- Recovery math (assumption, not a sourced stat): a cut is $35–60, color/treatment $100–250 — a handful of after-hours or busy-hands saves per week covers the retainer on its own.

## Guardrails that ARE the moat here
- No card numbers by voice — deposits go out as a payment link by SMS (prohibited-action class).
- Refunds/complaints/pricing exceptions → drafted + held for owner approval (R1 floor; autonomy earned per the matrix).
- Spam/robocall screen so junk minutes don't burn COGS.

## Watchpoints
- TTS (ElevenLabs) dominates per-minute cost — evaluate cheaper premium voices at scale; every provider price drop is pure margin (the model-upgrade dividend).
- Shops sustaining >4,000 voice min/mo pull gross under ~65% → volume clause or steer to OS pricing.
- Multi-location = OS territory from day one (top of implementation band per `vertical-ranges.md`).
- Before any real campaign: Polo locks the vertical file; the Founder approves.
