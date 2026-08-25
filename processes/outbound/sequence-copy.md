# Proof-led outbound — the sequence copy (Instantly-ready, PAUSED)

> Finished, mail-merge-ready copy for the 4-touch proof-led sequence (`proof-led-outbound-engine.md`). Load into Instantly as a campaign, **kept paused** — nothing sends until OtherVenture clears + Rafi clears CAN-SPAM/TCPA. **Copy owner: Michelle** (split from Reilly 2026-06-15); **Reilly loads + stages it** via `instantly.py --create`. Lead-with-the-demo, never the pitch.

## Merge variables (map these in Instantly)
| Variable | Source | Fallback |
|---|---|---|
| `{{first_name}}` | enriched contact (Vibe export) | `there` |
| `{{company}}` | CRM company name | `your business` |
| `{{vertical}}` | CRM vertical | `local service businesses` |
| `{{demo_url}}` | per-prospect demo (`prospect-demo.html?p=<slug>`) | — *(required; no demo, no send)* |
| `{{calendar_url}}` | `https://calendly.com/the Founder-yourco/30min` | — |
| `{{glassbox_url}}` | `…/try-to-break-it.html` | — |
| `{{sender}}` | the Founder | — |

> Instantly fallback syntax: `{{first_name|there}}`. Every email carries the CAN-SPAM footer (physical address + one-click unsubscribe). SMS only to consented numbers with STOP (TCPA).

---

## Touch 1 — Day 0 · the demo (the whole point)
**Subject A:** `built an AI front desk for {{company}}`
**Subject B:** `{{company}}'s missed calls, handled`

```
Hi {{first_name|there}},

I run yourco — we build AI employees for {{vertical|local service businesses}}.

I put together a 60-second working demo of an AI front desk for {{company}}. It
answers your calls, qualifies the job, and books the estimate — in your voice:

{{demo_url}}

If it's useful, I can have a real one live at {{company}} in 48 hours — catching
every call you'd otherwise miss, nights and weekends included.

Worth a quick look?

— the Founder
the Founder · yourco · founder@yourco.example.com
{{unsubscribe}} · YourCo LLC, 123 Example St, Riverton, FL 33713
```

## Touch 2 — Day 3 · the math
**Subject:** `the math on {{company}}'s missed calls`

```
Hi {{first_name|there}},

Did the demo make sense? Here's the part most owners don't love:

Even a handful of missed calls a week — at your average job value — is real money
going straight to voicemail. Reese catches them 24/7, qualifies, and books the
estimate while you're on the job.

The 60-sec demo for {{company}}, again: {{demo_url}}

Want to see the real thing? 15 minutes: {{calendar_url}}

— the Founder
{{unsubscribe}} · YourCo LLC, 123 Example St, Riverton, FL 33713
```

## Touch 3 — Day 6 · the trust (kill the fear)
**Subject:** `is it reliable? (fair question)`

```
Hi {{first_name|there}},

The #1 thing owners ask me: "will an AI embarrass me with a customer?"

Fair. So here's how Reese is different from a chatbot:
 • It never quotes a price — that stays your call
 • Anything unusual routes straight to you
 • You approve anything customer-facing before it sends

Exactly how we keep it reliable: {{glassbox_url}}
And the demo for {{company}}, in case you missed it: {{demo_url}}

— the Founder
{{unsubscribe}} · YourCo LLC, 123 Example St, Riverton, FL 33713
```

## Touch 4 — Day 10 · the breakup
**Subject:** `should I close your file?`

```
Hi {{first_name|there}},

I don't want to clutter your inbox, so this is my last note.

If the timing's off for {{company}}, just say the word and I'll close it out — no
hard feelings.

If you do want an AI front desk live in 48 hours, here's my calendar:
{{calendar_url}}

Either way, the demo's yours to keep: {{demo_url}}

— the Founder
{{unsubscribe}} · YourCo LLC, 123 Example St, Riverton, FL 33713
```

## SMS (optional · consented numbers only · TCPA)
**After Touch 1, only where there's a number + consent:**
```
Hi {{first_name|there}}, the Founder w/ yourco — made {{company}} a 60-sec demo of an AI
front desk: {{demo_url}}  Worth a look? (reply STOP to opt out)
```

## Pre-send checklist (Reilly, at launch)
- [ ] Every contact has a real `{{demo_url}}` (pre-generated, Mode A). No demo → hold.
- [ ] Sending domain warmed; CAN-SPAM footer + unsubscribe live (Instantly handles).
- [ ] SMS numbers consented + 10DLC registered (`processes/10dlc-sending-infra-setup.md`) — Rafi sign-off.
- [ ] Replies route to David → CRM stage move; positive replies → the Founder for discovery.
- [ ] **OtherVenture cleared.** Until then: campaign stays **paused**.
```
