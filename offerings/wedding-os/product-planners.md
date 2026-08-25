# Product 2 — Wedding OS for Planners (B2B)

> Shared engine, agents, autonomy rungs and legal fences: [`SPEC.md`](SPEC.md). This file covers only
> what is different about selling to a wedding-planning business.
>
> **Sequence: build this first.** Fastest path to a signed client, cleanest fit with the existing
> pricing ladder, lowest risk profile, and the client absorbs the approval labour — which is what makes
> the margin work while the eval layer is still young.

---

## The buyer

A wedding planner or coordination business running **20–30 weddings a year**, usually the owner plus
one or two assistants, frequently just the owner. They charge $4,000–12,000 per wedding for full
service, or $800–1,500 for day-of coordination.

This is a **textbook yourco client**: an SMB owner-operator whose day is consumed by exactly the
repetitive coordination labour the engine automates, with a P&L that can support a retainer, and a
buying decision made by one person with no procurement process.

**Their job-to-be-done:** *"I'm at capacity. I'm turning work away or working 70-hour weeks, and most
of what fills my day isn't the part clients actually value me for."*

---

## ⚠️ The qualification question that decides every deal

**Is this planner capacity-constrained or demand-constrained?**

- **Capacity-constrained** — more inquiries than they can serve, turning weddings away. The OS converts
  directly into revenue. Strong ROI, easy sale.
- **Demand-constrained** — the calendar has gaps and the real bottleneck is *booking* couples, not
  serving them. **The OS as scoped does not help them**, and they should not be sold it.

This is the single most important discovery question in the product, and getting it wrong produces a
churned client who was never a fit. **A demand-constrained planner is not a lost deal — it is a
different sale** (their Marketing and Sales pillars: inquiry response, proposal turnaround, social
presence). Route accordingly rather than forcing the fit.

---

## What's different about the product

| | |
|---|---|
| **The multi-wedding console is the product** | 25 weddings at different stages simultaneously. The cross-wedding view — what's overdue anywhere, what needs approval today, which vendors are unresponsive across all active weddings — is the primary surface. Product 1's single-wedding board is a detail view here. |
| **Scout matters less** | They already know their market and have preferred vendors. The value shifts hard toward **Outreach** (chasing) and **Normaliser** (comparing), plus **Critical path** across a portfolio. |
| **The vendor knowledge base is theirs** | `SPEC.md` §7 compounds inside their business, in their metro, on their preferred list. Strong retention mechanic — leaving means losing it. |
| **White-label, mandatory** | The couple sees the planner's brand. yourco does not appear (external-surface rules; this bit us on Sample Product). |
| **They own the approval gate** | The planner reviews R1 items. Their judgment, their relationships, their reputation — and **yourco's operator cost drops accordingly.** |
| **Day-of stays theirs** | They *are* the day-of coordinator. No awkward limit to explain — the thing the engine can't do is the thing they're keeping. |

---

## Positioning — capacity, never replacement

The first objection is *"is this going to replace me?"* Answer it before it's asked, and answer it
truthfully:

> The parts of the job that are actually you — the taste, the relationships, the calm on the day, the
> couple trusting you — are the parts that don't automate. What we take is the 200 hours a year of
> chasing florists for a reply and turning eleven quotes into something comparable. **You don't do
> fewer weddings. You do more of them, and less of the part you hate.**

The honest arithmetic: a planner doing **25 weddings at ~$6,000 grosses ~$150k**. If the OS lets them
run **45–50**, that's ~$275–300k on the same headcount. That delta is the entire sale, and it only
exists if they're capacity-constrained.

---

## Pricing — fits the ladder cleanly

Per `pricing/v0/os-tiers.md`, with no inversion problem and no Polo ruling required.

| Rung | Scope | Price |
|---|---|---|
| **On-ramp** (land here) | Chase + Normalise only — the two §1 failures, nothing else | **$1,500/mo** floor + $1,000–2,000 setup |
| **Core** | Adds critical path, contract flagging, guest/RSVP | **$3,000–4,000/mo** + $2,000–2,500 |
| **Suite** | Adds their *business* — inquiry response, proposals, invoicing, social | **$5,000–6,500/mo** |

**Land on the on-ramp, expand to Core.** This is the "lead high, land anywhere" doctrine working as
designed: open with the full OS, and landing on the first module is a good outcome, not a failed one.

⚠️ **Honest pricing tension:** $3,000/mo is $36k/yr — roughly **24% of a 25-wedding planner's gross**.
That is steep, and it is only justifiable against the capacity delta above. For a planner at that size
the **$1,500 on-ramp is the realistic entry point**, with Core arriving after volume grows. Pricing the
opener at Core risks a no that the on-ramp would have turned into a yes.

---

## The expansion path

A planning business has all eight pillars, and wedding delivery is one of them. Land on delivery,
expand across the business:

| Pillar | Their version |
|---|---|
| **Intake** | Inbound inquiry response and qualification *(often their real bottleneck)* |
| **Sales** | Proposal generation and follow-up |
| **Marketing** | Instagram/Pinterest content, portfolio, review generation |
| **Customer** | The couple-facing experience between meetings |
| **Operations** | ← **the wedding engine lands here** |
| **Back Office** | Invoicing, vendor payments tracking, contracts |
| **Company Brain** | The vendor knowledge base (§7) |
| **Training** | Onboarding assistant coordinators |

This is the standard yourco motion — and it's why a planner is a better first client than a couple:
**a couple is one transaction; a planner is an account.**

---

## Risk profile — lowest of the three

- **§6.1 sender liability** — materially lower. A known local business with an existing vendor
  relationship is the sender, on their own domain.
- **§6.7 vendor relations** — largely dissolves. The planner has a reputation with those vendors and an
  ongoing relationship to protect; they will not permit extractive negotiation because *they* bear the
  consequence.
- **§6.4 UPL fence** — unchanged and still applies to contract flagging.
- **§7 data fence** — sharper: one operator now sees many couples' negotiated prices. Aggregate
  intelligence is fine; cross-leaking a specific couple's price is not.

**New risk, specific to this product:** the planner's client relationships *are* their business. A
message from the OS that lands badly with a couple damages an asset that isn't yourco's. White-label
plus the R1 floor on couple-facing communication is the control.

---

## Competitive / incumbent

Planners commonly pay for **Aisle Planner, HoneyBook, Dubsado or Honeybook-adjacent CRMs** — and
typically half-use them.

This is a direct application of the audit's **build-vs-rent teardown lens**: surface the angry invoice,
ask which screens their team actually touches, quantify the annual cost. But note the fence — those
tools are **systems of record**, which the teardown's own qualification filter says to **disqualify
from replacement**. So: **overlay, don't displace.** The OS does the work; their CRM keeps the record.
Trying to replace it loses their data and burns the relationship.

---

## What must be true

1. **The target planner is capacity-constrained, not demand-constrained.** *The qualifying question.*
2. **A solo planner will pay $1,500–3,000/mo.** Real money at their size; the capacity delta has to be
   credible to them, not just to us.
3. **The capacity actually converts** — more throughput only pays if the demand is there to fill it.
4. **Overlay-on-existing-CRM works** technically and doesn't create double entry.
5. **They'll let the OS touch couple-facing communication** — or will they insist on drafting those
   themselves, which changes the labour math?

---

## Phase 0 questions for planners

**The full field guide is [`phase0-planner-interviews.md`](phase0-planner-interviews.md)** — recruiting,
interview discipline, all 14 questions with listen-fors, the tally sheet, and pre-committed kill
criteria. It is the single source; do not maintain a second copy of the questions here.

Two things from it worth carrying in this spec, because they decide whether this product exists:

- **Question 7 is the qualifier** — *"if you could do twice the weddings next year without hiring,
  would you have the couples to fill them?"* Yes = capacity-constrained = a real prospect. No = the
  product as scoped does not help them.
- **⚠️ The likeliest kill finding** — "vendors don't reply" may be a *couple* problem, not a *planner*
  problem. A planner who has sent a florist $40k of business gets a same-day reply. If that holds, the
  highest-value agent in the system has no value to this buyer, and couples are the buyer with the
  pain while planners are the buyer with the money — a materially different answer to D1.
