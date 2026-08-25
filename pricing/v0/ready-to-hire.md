# Ready-to-Hire employees — pricing (v0, Polo proposes · the Founder locks)

> ⛔ **PARKED — the surface this prices does not exist on the live site.** `hire.html` and
> `hire-onboarding.html` were dialled back to `agents/webb/pages/yourco-site-v2/_parked/` on
> 2026-06-22 (`decisions/2026-06-22_website-dial-back.md`); the prices survive in `hire-config.js`
> so the catalog can be restored without re-deriving them. **Nothing below is quotable.**
>
> Read the argument below with that in mind — in particular its claim that these SKUs "NEED a
> published monthly price." That was written for a catalog page and now sits against the standing
> external-surface rule (**no specific prices on the public site**; prices go in proposals, where
> scope is real). If the catalog is ever un-parked, that conflict is the first thing to resolve,
> not a detail to discover afterwards.

> **Owner: Polo.** The off-the-shelf, subscribe-and-go single AI employees (the catalog on
> `agents/webb/pages/yourco-site-v2/_parked/hire.html`, config `hire-config.js`). Unlike the Audit + custom OS
> (no public prices), **these SKUs likely NEED a published monthly price** — transparent pricing is half
> of why subscribe-and-go converts without a call (DesignJoy, Off Menu both post theirs). Polo proposes;
> the Founder locks; the number goes into `hire-config.js` (`price` per employee). Decision:
> `decisions/2026-06-16_two-motions-productized-employees.md`; spec: `processes/off-the-shelf-employees.md`.

## The billing model (the Founder-locked 2026-06-17)
- **Month-to-month. Pause anytime (unused time rolls over). Cancel anytime. No minimum, no contract.**
  This is the low-friction entry — a minimum/contract kills the subscribe-and-go appeal. (The **custom OS**
  keeps its 6-month minimum tied to the audit credit — different motion, different commitment.)
- **Flat monthly fee per employee.** yourco absorbs all token/model/infra spend (the model, not a bug).
- **Optional annual-commit discount** (Polo's call) — a way to reward commitment without *requiring* it.
- A small **one-time setup fee** is optional (Polo) — but the friction-light story argues for $0 setup /
  baked into month one.

## What Polo prices (the catalog SKUs)
Price each by its build + run cost and the value it unlocks (most have a clear ROI from the leak math):
| Employee | What it does | Pricing notes |
|---|---|---|
| **AI Front Desk** (voice) | Answers every call, books the job | Highest value + highest run-cost (voice = Vapi/Twilio/ElevenLabs); top of the range |
| **Missed-Call Text-Back** | Auto-texts missed callers | Low run-cost, high ROI — strong entry price |
| **Review Responder** | Replies to Google/Yelp reviews | Low run-cost; price on reputation value |
| **Reminder & Recall** | Cuts no-shows, re-books lapsed | Mid; clear ROI from recovered no-shows |
| **Inbox & FAQ Responder** | Answers repetitive inbound | Low-mid run-cost |
| **Lead Intake & Booking** | Qualifies + books every lead | Mid-high; close to a front-desk in value |

## SKU prices — **🔒 LOCKED by the Founder, 2026-06-17**
Flat monthly per employee. **$0 setup** (baked into month one) to keep subscribe-and-go friction near zero.
These are now in `hire-config.js` and render on the (staged) catalog cards. **Front Desk $749 · Lead Intake
$449 · Reminder & Recall $299 · Inbox & FAQ $299 · Missed-Call Text-Back $249 · Review Responder $249.**
Reasoning below; the ratchet plan stands (raise as proof accumulates; grandfather early clients).

| Employee | First pass | **Proposed (revised)** | Why |
|---|---|---|---|
| **AI Front Desk** (voice) | $599 | **$749/mo** | Highest value + real per-minute run-cost (Vapi/Twilio/ElevenLabs). A human receptionist is $3–4k/mo — $749 is still a steal. Fair-use call cap. |
| **Lead Intake & Booking** | $399 | **$449/mo** | Near front-desk value, text-based. |
| **Reminder & Recall** | $249 | **$299/mo** | ROI from recovered no-shows + reactivated customers. |
| **Inbox & FAQ Responder** | $249 | **$299/mo** | Saves real owner/staff hours. |
| **Missed-Call Text-Back** | $199 | **$249/mo** | The easy first "yes" — but $199 read as a SaaS toy; $249 reads as an operated service. |
| **Review Responder** | $199 | **$249/mo** | Reputation + local-SEO value. |

### Why raise (Polo + Brett's view)
- **Underpricing mis-signals the category.** At a $199 floor we read like a single-feature SaaS toy, not an *operated employee that replaces headcount*. Price is positioning — too low actively undercuts the moat we sell (reliability/eval/approval). Brett (DesignJoy): every time he raised price, demand *rose* because it moved him to a new category.
- **We absorb the token/infra spend** (the model). A $199 *voice-adjacent* SKU is thin once Vapi/Twilio/ElevenLabs minutes are in — higher price = margin headroom, not greed.
- **Still anchors trivially small vs. the leak.** The Revenue Leak Snapshot shows a $5–50k/mo leak; $249–$749 to close it is a rounding error. Raising doesn't break the anchor.

### Why NOT raise much (the honest counter)
- The off-the-shelf tier's *job* is **foot-in-the-door + volume + proof generation**, not margin — **the custom OS is the margin engine.** Keep the entry an easy yes.
- **Pre-revenue, zero case studies → we haven't *earned* premium yet.** Land the first logos cheaper, get testimonials, *then* ratchet. (Also Brett: he started at **$449** and climbed to **$8k** as proof compounded.)

### The resolution: raise modestly now, then ratchet
The revised table is the modest raise. The **plan** is a deliberate price ladder — **raise as proof accumulates** (case studies, demand, waitlist), the way DesignJoy did. Build the increases into the model; don't set-and-forget. Early clients can be grandfathered to reward them for taking the bet.

- **Bundle nudge:** any **2+ employees** → small bundle discount *or* the audit→custom-OS conversation. Polo sets the mechanic.
- **Annual-commit discount:** ~2 months free on annual prepay — rewards commitment without *requiring* a minimum.
- **Locked + in the config (2026-06-17).** Prices are set in `hire-config.js` and show on the staged catalog cards; they go public when the site deploys (launch-gate). Future changes follow the ratchet plan above.

## The levers (for Polo)
- **Anchor against the leak, not the cost.** Each employee's ROI is visible from the Revenue Leak Snapshot / Missed-Money
  Meter — the price should read trivially small next to the monthly leak it closes.
- **Tiered by usage if needed** (call/message volume) — but keep the entry SKU dead-simple (one flat price).
- **The voice SKU carries real per-minute cost** (Vapi/Twilio/ElevenLabs) — price it with headroom; consider a
  fair-use cap.
- **Bundle nudge:** 2–3 employees should hint at the custom-OS up-sell (the system is where the return is).

## Standing rules
- **Transparent price on the catalog** (the exception to the no-prices rule — the Founder to confirm) — needed for
  subscribe-and-go. The Audit + custom OS stay quote-on-call.
- **Never quote a number that isn't Polo-locked.** Until locked, `hire-config.js` `price` stays `null`
  ("Pricing at launch" renders on the card).
