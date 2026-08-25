# Product 1 — Wedding OS for Couples (DTC)

> Shared engine, agents, autonomy rungs and legal fences: [`SPEC.md`](SPEC.md). This file covers only
> what is different about selling to the couple directly.
>
> **Sequence: build this third.** Not because it's weakest as a product — it's the one with the story —
> but because its acquisition economics are the worst of the three and are **solved by arriving through
> products 2 and 3** rather than bought.

---

## The buyer

The engaged couple, usually with **one of them acting as de facto project manager**. First-time buyer
of every single thing they are about to purchase. No reference prices, no vendor relationships, no idea
what "normal" looks like on a contract.

**Their job-to-be-done, in their words:** *"I don't know what I'm doing, there's too much of it, and
I'm terrified of getting ripped off or forgetting something that can't be fixed."*

Note that this is three jobs — **competence, capacity, and protection** — and the third is the one no
existing product serves.

---

## The positioning wedge — aligned incentives

This is the sharpest argument in the whole offering, and it is structural rather than technical.

**The Knot, Zola and WeddingWire are advertising businesses.** Their revenue comes from vendors paying
for placement and leads. They are therefore *structurally incapable* of telling a couple:

- "This vendor is priced above market for what's included."
- "These three never replied to you, so stop waiting."
- "That contract's overtime clause is unusual and will cost you $900 on the night."

A product **paid by the couple** can say all three. That is not a feature the incumbents have declined
to build — it is one their business model forbids. It is also the honest answer to *"why would I pay
when The Knot is free?"*: **free means the vendors are the customer, and you are the product.**

Human planners have aligned incentives too — and cost $4,000–12,000. This sits underneath that, at a
price point where the alternative is "no help at all," which is what most couples actually have.

---

## What's different about the product

Everything in `SPEC.md` §4 is in scope — this is the buyer with no one else to do any of it. The
surface and emphasis differ:

| | |
|---|---|
| **Surface** | A single-wedding board: countdown, budget tracker, per-category status, the comparison tables, and an **approval queue** (the couple approves anything at R1) |
| **Scout matters most here** | They have zero vendor relationships. In products 2 and 3 the client already knows the market; here the system *is* the market knowledge. |
| **Tone** | Reassurance is a product requirement, not a nicety. The system should reduce anxiety visibly — "here's what's handled, here's what's next, nothing is overdue." |
| **The do-today box** | Borrowed from the audit SOP: 2–3 things they can do themselves this week. Proves the system touched *their* wedding. |
| **Explicit day-of handoff** | The product **recommends hiring a day-of coordinator** (~$800–1,500) and hands them the best run sheet they've ever received. See `SPEC.md` §2 — never claim to replace this. |
| **Support burden** | Highest of the three. Unsophisticated, emotionally invested, one-shot, and every question is urgent to them. |

---

## Pricing — and the ladder problem

**A couple will never pay a $3,000/mo retainer.** Planning runs 9–18 months; that's $27–54k against an
average total US wedding budget in the low-to-mid $30k range. The monthly model does not survive
contact with this buyer.

**The unit must be a fixed per-wedding engagement fee.**

| Anchor | Price |
|---|---|
| Full-service human planner | $4,000–12,000, or 10–15% of budget |
| Day-of coordination only | $800–1,500 |
| **Proposed: Wedding OS for Couples** | **~$2,500–4,500 one-time**, possibly tiered by wedding budget |

⚠️ **This is off the locked ladder entirely.** `pricing/v0/os-tiers.md` sets a $3,000/mo Core floor and
forbids inversion. A one-time DTC fee isn't on that ladder — the same is true of yourco Care — but that
is **Polo's ruling to make explicitly**, not an assumption to smuggle through. *(Open decision D3.)*

### ⚠️ The margin question is the gate

Per wedding the system runs dozens of vendor conversations, parses dozens of documents, and — the part
that actually costs — **consumes yourco operator time on every R1 approval gate.** In products 2 and 3
the client absorbs that labour. Here yourco pays for it, against one-time revenue.

**Model this before writing a line of code.** It is the single number that decides whether this product
exists. If a wedding needs six hours of operator attention, $3,000 is a services business with thin
margin, not an AI product.

---

## Acquisition — the real problem, and the real answer

**A couple buys once, never renews, and cannot be upsold.** Every acquisition dollar must be repaid
inside a single transaction. There is no retention line. This is the worst LTV shape in DTC and it is
worse than yourco Care, which at least has a relationship lasting years.

Two things partially rescue it:

**1. Weddings are socially dense.** Bridesmaids get engaged. Guests are a pre-qualified audience
watching the wedding go well. There is a genuine referral loop here that most one-time purchases lack —
and referral is the only channel whose economics work for a single-transaction product.

**2. Products 2 and 3 are the distribution channel.** A venue books 80 couples a year. A planner books
25 and turns away more. Both have couples they cannot serve or don't want. **That is warm,
pre-qualified, near-zero-CAC distribution** — and it is the entire reason this product is sequenced
third rather than first.

| Channel | Verdict |
|---|---|
| **Through venues / planners** | ✅ The answer. Warm, near-zero CAC, pre-qualified. |
| **Referral from prior couples** | ✅ Works economically; slow to start (n=0 flywheel). |
| Organic social / wedding content | ⚠️ Huge audience, but converting attention to a $3k purchase is hard. |
| The Knot / Zola listings | ⚠️ Paying the incumbent whose model you're attacking. |
| **Paid social** | ❌ Brutal for a one-time purchase with no LTV. Not the opener. |

---

## Risk profile — highest of the three

Everything in `SPEC.md` §6 applies, and two are materially worse here:

- **§6.1 sender liability** — yourco is an unknown third party contacting vendors on a consumer's
  behalf. In products 2 and 3 the sender is a known local business with a reputation.
- **§6.7 vendor relations** — an unknown AI cold-contacting 40 vendors in one metro gets identified
  fast, and the blacklist failure mode is live. Per-wedding sending identity, metro volume caps and
  disclosure are mandatory, not optional.

Plus **§6.8 emotional stakes** at their sharpest: a missed deposit deadline loses the venue and there
is no retry. The R1 floor on anything touching a booked vendor is not a starting posture here — it
should be expected to be permanent.

---

## What must be true

1. **Margin clears at ~$3,000/wedding** including operator approval time. *Gating — model first.*
2. **CAC lands under ~$300–400**, which realistically means the channel is products 2 and 3, not paid.
3. **Couples will trust an AI with this.** Untested. The emotional-stakes objection is real and may be
   decisive for a segment of the market.
4. **Vendors will engage with it** and the market doesn't turn hostile (§6.7).
5. **Polo rules on off-ladder DTC pricing** (D3).

---

## Phase 0 questions for couples

**The full field guide is [`phase0-couple-interviews.md`](phase0-couple-interviews.md)** — recruiting,
the retrospective-interview discipline, all 15 questions with listen-fors, the tally sheet, kill
criteria, and the D1 synthesis across all three buyers. Single source; no second copy here.

Three things from it that belong in this spec, because each can change what gets built:

- **⚠️ The timing mismatch.** A couple would buy this at week one and doesn't feel the pain until
  month three. The purchase decision is made at the moment of *least* willingness to pay, and by the
  time they're drowning they've already decided against help and are sunk-cost committed to DIY. If
  confirmed (Q4, Q11), **product 1 cannot be sold directly at the moment of need** — which makes the
  venue channel not merely cheaper CAC but the only viable route.
- **Happy-ending bias is the methodological risk.** The day went well, so the year is remembered
  fondly. The antidote is artifacts, not questions — have them open the actual email folder and count.
- **Question 13 decides whether the product exists** — *would you have let software email vendors in
  your name?* Expect the answer to split at "booked vs not yet booked," which is exactly the R1
  boundary in `SPEC.md` §5.
