# Off-the-shelf digital employees — what "subscribe-and-go" actually means

> The product spec behind the off-the-shelf motion (`decisions/2026-06-16_two-motions-productized-employees.md`).
> Answers the real question: **how off-the-shelf can an *operated* AI employee actually be, and where's the honest limit?**
> Owners: **Webb** (catalog + checkout) · **Janice** (the onboarding wizard + intake — it's the productized front of her onboarding job) · **Kimi** (golden build patterns) · **Polo** (SKU pricing) · **Kemba** (runtime pause/resume).

## The honest definition
"Off-the-shelf / subscribe-and-go" productizes the **purchase + onboarding**, NOT the **operation**. The client
subscribes to a *pre-scoped* employee and it's live fast — no forms, no quotes, no sales calls, no audit, **pause
anytime**. But yourco still **builds, runs, evals, gates approvals, and owns reliability** behind it (the moat,
`01_company.md`). The client buys an *outcome they don't operate* — they are NOT handed software to run. That is
the line that separates this from the **parked self-serve SaaS** (where the client absorbs the eval/reliability
risk). Same carve-out as yourco Care.

**So "off-the-shelf" = the *design is pre-done*; only the *configuration* is per-client.** A true SaaS signup
("click → instantly live, zero humans") is impossible for an operated employee, because every business has its own
phone number, calendar, services, pricing, voice, and data. What we productize is everything *except* that thin
config layer — and we make that layer a fast, guided onboarding instead of a bespoke project.

## What's fixed vs. variable (the whole trick)
| Pre-built once (the "shelf") | Configured per client (fast onboarding) |
|---|---|
| The employee's logic, flows, prompts, guardrails, eval set | Their phone number / calendar / inbox (connector auth) |
| The approval gates + reliability/observability layer | Their services list, hours, FAQ, pricing rules |
| The integration patterns (Vapi voice, calendar, CRM) | Their brand voice + a chosen voice (for voice agents) |
| The runtime + monitoring | A few business-specific answers (a short intake) |
| The transparent price | — |

If a request needs anything *outside* that config layer — custom internal-system integration, novel multi-step
workflows, deep business logic — it is **not** an off-the-shelf SKU; it routes to the **Audit → custom OS** motion.

## The productization ladder — how off-the-shelf each pattern can be
From `clients/_yourco-template/employee-patterns*.md`, scored by how little client-specific knowledge they need:

- **Most off-the-shelf (near-instant — connect + a few answers → live in hours):**
  - **After-hours / overflow receptionist** — answers, qualifies, takes a message or books. Needs: forward your number + calendar + services/FAQ.
  - **Missed-call text-back** — auto-texts every missed call. Needs: number forwarding only.
  - **Review responder** — drafts replies to Google/Yelp reviews. Needs: review-profile access + voice.
  - **Appointment reminder / recall** — reduces no-shows, re-books lapsed customers. Needs: calendar + a message template.
  - **FAQ / inbox auto-responder** — answers common inbound questions. Needs: inbox auth + an FAQ paste.
- **Medium (a slightly longer intake — live in ~a day):**
  - **Lead intake + qualification + booking** — needs their qualifying questions + booking rules.
  - **Quote/estimate assistant** — needs their pricing logic (the variable part).
  - **Follow-up / nurture sequence** — needs their offer + cadence + messaging.
- **Least off-the-shelf → route to Audit/OS (not a catalog SKU):**
  - Anything touching internal systems (their ERP/field-service software deeply), custom approvals, or multi-agent
    coordination. That's a *custom OS*, sold consultatively.

**Rule of thumb:** if onboarding is "connect 1–2 accounts + answer ≤10 questions," it's a catalog SKU. If it needs
a discovery conversation to even scope, it's the audit motion.

> **Product requirement — AI callers (added 2026-06-17).** The **AI Front Desk** must handle **AI-to-AI calls**, not
> just humans. Google's **"Ask for Me"** agent now calls local businesses for price/availability on a searcher's
> behalf (nationwide US rollout summer 2026; Invoca measured a 300%+ jump in AI pricing calls —
> `agents/brett/competitive-watch.md`). The front desk should: answer a structured pricing/availability inquiry
> crisply (accurate ranges + booking windows + lead capture), and **detect a self-identified automated caller**
> (e.g., "automated call from Google") and route it to a **deterministic pricing/availability path**. A human
> receptionist fumbles a scripted AI caller; yourco's wins the comparison Google is running — a reliability feature
> *and* a sales angle.

## The subscribe-and-go flow (target)
1. **Browse the catalog** (`employees.html` / the vertical pages) — each SKU = a named employee, what it does, a live
   "see yours" demo, and a **transparent monthly price**.
2. **Subscribe** — self-serve checkout (Stripe), flat monthly per employee, **pause anytime**.
3. **Guided onboarding (~15–30 min, no call required)** — connect accounts (calendar/inbox/number), answer the short
   intake, pick a voice (voice agents). A wizard, not a meeting.
4. **yourco stands it up** — the near-zero-touch build path (scaffolder + Kimi's golden pattern) configures + evals
   the pre-built employee against the client's inputs. **Live fast** (target: same-day for the most off-the-shelf;
   ≤48h otherwise).
5. **It runs — operated by yourco.** Client watches it work in the client console; approves anything customer-facing.
   **Pause/resume anytime** from their account.

## The constraints to be honest about (and own)
- **Connector auth is the gating step.** "Go" is as fast as the client connecting their calendar/number/inbox — the
  onboarding wizard must make that frictionless, and some clients will still need a nudge. Not literally zero-touch.
- **Voice agents need a provisioned number + voice** (Vapi/Twilio/ElevenLabs) — a few extra onboarding steps vs. a
  text agent.
- **Pause = pause the operated runtime + billing cleanly** (Kemba's per-client pause/resume — `decisions/2026-06-16_two-motions-productized-employees.md`).
- **Reliability still has to hold per client** — the pre-built eval set runs against *their* config before go-live;
  off-the-shelf does **not** mean un-evaled. The shelf is reliable *because* the pattern is proven, not because we
  skip the gate.
- **Transparent pricing is likely required** for subscribe-and-go to convert (DesignJoy/Off Menu both publish) — in
  tension with the current no-prices rule; Polo + the Founder to lock for the catalog SKUs (the custom OS + Audit stay
  quote-on-call).

## Bottom line
We can make the *purchase and onboarding* genuinely off-the-shelf — catalog → price → checkout → a short wizard →
live fast — for a **defined set of pre-scoped, high-reliability patterns**. What we never productize is the
*operation*: yourco still runs it, evals it, and owns reliability. "Subscribe-and-go" is real; "self-serve, you run
it" is the parked path we don't cross. The off-the-shelf SKU is the front door; the audit→OS is the upmarket motion;
both are marketed under one yourco brand.
