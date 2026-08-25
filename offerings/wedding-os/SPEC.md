# Wedding OS — platform spec (the shared engine)

> **Status: SCOPED, NOT DECIDED.** the Founder asked to scope this 2026-08-22, then asked for it split into
> three products by buyer. This file is the **shared engine and the cross-cutting risk layer**. The
> three products are separate specs:
>
> | Product | Buyer | Unit | File |
> |---|---|---|---|
> | **1 · Couples** | The engaged couple, direct | One-time per wedding | [`product-couples.md`](product-couples.md) |
> | **2 · Planners** | Wedding planner / coordinator business | Monthly retainer | [`product-planners.md`](product-planners.md) |
> | **3 · Venues** | Venue or venue group | Monthly retainer, per property | [`product-venues.md`](product-venues.md) |
>
> **Anti-library check:** not previously rejected. Two read-acrosses:
> `rejections/2026-06-16_self-serve-saas.md` explicitly carves out *operated* DTC (yourco Care), which
> is product 1's shape; `rejections/2026-08-16_bookie-agent-back-office.md` enforces the Core floor and
> the no-inversion rule, which product 1 collides with — see its §Pricing.

---

## 1. The insight the three products share

Wedding planning is a 9–18 month project handed to two amateurs who have never done it before and will
never do it again. Underneath every version of this offering are the same two mechanical failures:

| The failure | Why it exists | Why it's automatable |
|---|---|---|
| **Vendors don't reply** | Small owner-operators, booked out, email is their fourth priority. A couple sends 5 inquiries, gets 2 replies, and concludes those 2 are their options. | Send 40, chase every one on a schedule until it's a yes or a no. |
| **Quotes aren't comparable** | Every quote differs on inclusions, hours, staffing, overtime rate, travel, meals, service charge, tax, and what's silently excluded. | Parse into one structure and produce the apples-to-apples table. |

These two are the wedge in **all three** products. They are high-volume, unglamorous, fully
automatable, and — for the two B2B buyers — the part of the job they charge most for and enjoy least.

**Roughly 80% of the engine is shared.** What differs across the three: the surface, the buyer's job,
who owns the approval gate, the price, and the acquisition channel.

---

## 2. What it honestly cannot do

Stated first, because the credibility of all three products depends on it.

| Not automatable | Why |
|---|---|
| **Day-of coordination** | Peak human value is standing at the venue when the florist is 40 minutes late and the officiant is lost. Physical presence, real-time judgment, authority to improvise. |
| **Aesthetic judgment** | "Will this look right" is taste, and people want a human they trust holding it. |
| **Family politics** | Seating a divorced parent. Human. |
| **Signing anything** | The couple signs. Always. (§6.5) |
| **Holding or moving money** | Never. (§6.6) |
| **Legal advice on contracts** | Flag terms, never advise. (§6.4) |

**This replaces planning and coordination *labour* — the 200+ hours of research, chasing, comparing and
tracking. It does not replace a day-of coordinator.** Product 1 should actively recommend hiring one
and then hand them a better run sheet than they have ever received. Saying so is worth more than the
claim it gives up.

---

## 3. The core object: the wedding state machine

One wedding = one long-running state machine with a hard, immovable end date. Every deadline is
computed backwards from it.

```
Engaged → Budget & guest-count set → Date/venue search → VENUE BOOKED (date locks)
   → Vendor categories opened in dependency order
   → per category: shortlist → inquire → chase → quote → normalise → negotiate → contract → deposit
   → Guest list → invitations → RSVP → dietary → seating
   → Final headcount (venue deadline) → final payments → run sheet → DAY → post
```

**Venue-booked is the pivot.** Before it the date is a variable and everything is provisional; after
it the date is fixed and every other deadline is derivable. The system runs two modes either side of
that line.

> Note what this implies for sequencing: **the venue is the first domino.** That is not only a data
> fact — it is why product 3 is positioned where it is (§8).

**Per-vendor sub-state:** `identified → inquired → chasing → responded → quoted → normalised →
negotiating → contracted → deposit paid → final paid → delivered`, plus terminal `declined`,
`unavailable`, `rejected`.

---

## 4. The agents (shared across all three products)

Client-facing surfaces describe these **by function only** — no internal names, per the
external-surface rules.

| # | Function | What it does | Autonomy (§5) |
|---|---|---|---|
| 1 | **Scout** | Researches vendors in the metro; filters by style, budget band and **date availability**; shortlists with evidence (portfolio, reviews ≤18mo, price signals). | R3 — research only |
| 2 | **Outreach** | Sends the inquiry, then chases on a schedule until a yes or a no. **The highest-value agent in the system.** | R2 — bounded send |
| 3 | **Normaliser** | Parses every quote into one comparable structure. **The killer feature.** | R3 |
| 4 | **Negotiator** | Drafts counters — date flexibility, off-peak, bundling, comparable-quote leverage. **Drafts only.** | R1 |
| 5 | **Contract reader** | Flags traps: overtime, non-refundable deposits, force majeure, cancellation ladder, vendor meals, exclusivity, insurance. **Flags, never advises.** | R1 + UPL fence |
| 6 | **Critical path** | Backwards-computed timeline, deadlines, payment schedule, early tripwires. Never silent. | R3 |
| 7 | **Guest** | Guest list, invitations, RSVP chasing, dietary, accommodation, guest questions. | R2 |
| 8 | **Run sheet** | Minute-by-minute day-of schedule; distributes to vendors; confirms at 48h and morning-of. | R1 |

**Pillar mapping** (`processes/ai-os-modules.md`): Intake (1,2) · Sales (3,4) · Customer (7) ·
Operations (6,8) · Back Office (5, payment tracking) · Company Brain (§7).

**Who owns the approval gate is the biggest commercial difference between the three products.** In
product 1 yourco pays for that labour; in products 2 and 3 the client absorbs it. That single fact
drives the margin difference — see each product's Pricing section.

---

## 5. Autonomy — where the gates sit

Per `processes/autonomy-matrix.md`. A wedding is **one-shot and irreversible**, so the R1 floor is held
longer here than anywhere else in the portfolio.

| Rung | Actions |
|---|---|
| **R3 — full autonomy** | Vendor research, availability checks, quote parsing and normalisation, deadline computation, internal alerts, drafting anything |
| **R2 — bounded auto-send** | Initial inquiries to *unbooked* vendors; RSVP chasing; guest FAQ replies. Bounded by approved template, approved shortlist, and a rate cap. |
| **R1 — approval floor (stays here)** | Any negotiation message · any communication to a **booked** vendor · anything asserting the couple's budget, guest count or date · the run sheet · anything readable as a commitment |
| **Never automated** | Signing · paying · cancelling · changing the date · anything irreversible |

**The asymmetry that sets the gate:** an over-eager inquiry costs an awkward email. An erroneous
message to a *booked* vendor — wrong headcount, wrong time, implied cancellation — can destroy the
wedding, with no rollback. **Actions touching a booked vendor should be expected never to leave R1.**

---

## 6. Legal, compliance and relationship risk (applies to all three)

Counsel-gated before any real wedding, same posture as yourco Care. Ray owns; add to
`processes/counsel-gates.md`.

**6.1 yourco becomes the sender.** Outbound to vendors on someone's behalf means CAN-SPAM attaches to
us, and state mini-TCPAs (Florida's FTSA especially) attach to calls and texts. Vendors are businesses,
which helps — but many are sole traders whose business number is a mobile. Identical to connector
checklist item **4c**; treat it the same way. *Materially lower in products 2 and 3, where a known
local business is the sender.*

**6.2 AI disclosure.** Several states require disclosure of automated commercial communication
(California's B.O.T. Act being sharpest); Utah's AI Policy Act requires disclosure on request.
**Disclose regardless of law.** A vendor who discovers mid-negotiation that they've been arguing with
an undisclosed bot is a reputational event that travels fast in a tight local market.

**6.3 Call recording.** Two-party consent states require consent to record. One reason voice is not v1.

**6.4 UPL fence.** Contract review most resembles Conduit. **Flag terms, never advise.** "This deposit
is non-refundable after 30 days, which is unusual for this market" is a factual flag. "You should sign
this" or "that clause isn't enforceable" is legal advice. Enforced in the prompt *and* the output
schema, not policy alone.

**6.5 No signing authority.** The couple signs every contract personally. No power of attorney, no
agent-in-fact.

**6.6 Never touch money.** The couple pays vendors directly. Holding or forwarding deposits raises
money-transmitter licensing questions and catastrophic custody risk at wedding-deposit sizes. Track and
remind; never move a dollar.

**6.7 ⚠️ Vendor-relations risk.** Wedding vendor communities are small, local and tightly networked.
Two failure modes: **the blacklist** (an OS that negotiates extractively at scale gets identified, and
vendors start refusing anyone using it — the product's value inverts) and **the spam reputation** (40
inquiries into one metro from one identity looks like spam whether or not it is). Mitigations:
per-wedding sending identity, hard volume caps per metro per week, disclosure, and a negotiation
posture that is **firm but never extractive** — vendors are counterparties to keep, not marks.
**Products 2 and 3 largely dissolve this**, because the sender is a known local business with a
reputation to protect and an ongoing relationship with those same vendors.

**6.8 Emotional stakes.** Failure here is devastating and public. Error budgets and message tone should
be set accordingly.

---

## 7. The compounding asset

Every wedding teaches the system what no single couple could learn: which vendors actually reply and
how fast · which inclusions are standard in this metro vs. padded · real price bands by category,
season and day-of-week · who negotiates and on what · which contract terms are normal vs. predatory ·
which vendor pairings work on the day.

By wedding fifty the OS knows a local market better than most human planners. **This is the durable
asset**, and it is the reason for §8's one-metro-deep recommendation — density in one market beats
scatter across many.

⚠️ **Data fence:** this is aggregate market intelligence — price bands, response rates, contract norms.
It must never leak one couple's negotiated price to another, or expose a vendor's quote to a
competitor. Both a trust and a legal boundary, and it gets sharper in products 2 and 3 where one
operator sees many weddings.

---

## 8. How the three fit together — the recommended sequence

They are not three independent bets. Each one unlocks the next.

```
  PLANNERS  ──►  VENUES  ──►  COUPLES
  fastest yes    biggest ticket   worst CAC, solved by
  proves engine  + distribution   arriving through 2 & 3
```

**1st — Planners.** Fastest path to a signed client: a solo owner decides alone, no procurement, no
incumbent software to displace, and the price sits cleanly on the existing ladder. Critically, **the
planner absorbs the approval labour**, which is what makes the margin work while the eval layer is
still young. This is the product that proves the engine on real weddings at low risk.

**2nd — Venues.** Biggest ticket and best retention, and a venue is **a distribution channel to
couples** — every booked couple is a warm, pre-qualified lead for product 1. Longer sales cycle and
real incumbent software (§`product-venues.md`), so it wants the planner proof behind it.

**3rd — Couples.** The version with the emotional story and the worst unit economics. Its CAC problem
is **solved by arriving through products 2 and 3** rather than bought on TikTok. Build the engine for
the businesses; sell the outcome to consumers once the channel exists.

**Geography: one metro, deep.** Builds §7 density, manages §6.7 blast radius, and makes the three
products reinforce each other in the same vendor market instead of competing for attention across the
country.

---

## 9. Architecture

Deliberately boring; matches the stack already in the building.

| Layer | Choice |
|---|---|
| Orchestration | Claude API + the run-loop / approval pattern proven in `runtime/` |
| State | Postgres — `weddings`, `vendors`, `inquiries`, `quotes`, `quote_lines`, `contracts`, `deadlines`, `guests`, `payments`, `messages` |
| Vendor comms | Per-wedding email identity (product 1) or the client's own domain (products 2, 3). **Email first.** |
| Surfaces | Three, sharing one core: couple board · planner multi-wedding console · venue pipeline + coordination console |
| Documents | Contract parsing → structured terms (flag, never advise) |
| Payments | **Tracking only.** |

**Voice is not v1.** Vapi is the sanctioned stack when needed, but an AI voice negotiating with a small
vendor is the highest-risk, lowest-trust channel available and triggers §6.3. Email first.

---

## 10. Phase 0 — validate before any code

**Two weeks, no build, and it is the same Phase 0 for all three.**

- Interview **5 planners** (product 2) — field guide: [`phase0-planner-interviews.md`](phase0-planner-interviews.md)
  — plus **3–5 venue event directors** (product 3), field guide:
  [`phase0-venue-interviews.md`](phase0-venue-interviews.md) — and **8–10 recently married couples**
  (product 1), field guide: [`phase0-couple-interviews.md`](phase0-couple-interviews.md), which also
  carries the **D1 synthesis** across all three.
- Confirm the two §1 failures are the top two pains for each buyer.
- Model the margin per product, including operator approval time (the gating number for product 1).
- Get counsel's read on §6.
- **Kill criteria are real.** Any product whose margin doesn't clear, doesn't get built.

---

## 11. ⚠️ The honest note on sequencing

The 2026-08-09 audit's headline was **84 new code files against 12 commercial touches** — building kept
happening instead of selling. yourco has 0 clients, $0 revenue and $0 cash. Scoping a new offering while
the existing 31 have never been sold is that same pattern, and these four documents are an instance of
it.

That is not an argument against the idea, which is good and has an unusually crisp wedge. It is an
argument about **sequence**: run §10 first — fifteen conversations and a margin model, no code. If a
local planner will pay $3,000/mo for the capacity, that is a **client**, which is the thing yourco
actually needs.

---

## Trip-wire
Revisit when: (a) Phase 0 completes and returns a verdict; (b) yourco signs its first paying client;
or (c) **2026-11-22** — if nothing has moved by then, all four files go to `_archive/` rather than
sitting live and looking current.
