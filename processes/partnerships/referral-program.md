# Referral program — the performance-only sales force (v1, 2026-06-30)

> ⚠️ **Staged — nothing external until launch + counsel. The multi-level override (below) is a HARD STOP until Ray + outside counsel clear it.** A referral force that costs nothing until it produces paying clients, and pays more the more it produces. Owner: **Bird** (program) + **Polo** (numbers) + **Charles** (payouts) + **Ray** (agreement + MLM structure) + **the Founder** (lock). Recruitment muscle: **Sadie** (community) + **Reilly** (outreach). Supersedes `rev-share-model.md → Mode 1`; white-label Mode 2 unchanged. Numbers locked 2026-06-30: `decisions/2026-06-30_referral-program-v1.md`.

## One rate card (v3, 2026-08-13 — supersedes the Type 1 / Type 2 split)
**Anyone who refers earns the same escalator.** The old split paid a client a flat **$100/mo credit** and a connector **10/12.5/15%** of referred MRR. That flat rate was really *10% of a $1,000/mo deal* and was never re-based when the **$3,000 Core floor** landed — so by 2026 the identical referral paid a connector **$300/mo** and a client **$100/mo**. Nobody decided that; it was an artifact, and it was invisible to everyone except the person being underpaid. Decision: `decisions/2026-08-13_one-referral-rate-card.md`.

What differs now is only **how** it is paid:

| Who refers | Rate | Paid as |
|---|---|---|
| **A client** | the escalator | **credit against their own bill**, floored at $0 — then **cash** on anything above it |
| **A connector** (not a client) | the escalator | cash |
| **A client who churns** | the escalator | cash — they keep earning on referrals that are still live |

**Why credit-then-cash, not a cap.** Capping at the bill was considered and rejected: a $1,000/mo client hits the ceiling at ~3 referrals, which makes the 6+ and 11+ tiers unreachable for exactly the person you most want referring. Most client-connectors never overflow, so most never become a 1099 payee — only the ones earning more than their own bill do, and by then it is obviously worth the paperwork.

**A client becomes a full connector on their first referral** (the Founder, 2026-08-13) — including the downline and the 1% override. ⚠️ This is a deliberate widening of the counsel-gated MLM exposure from a recruited sales force to the **client base**; see counsel gate item 4c.

## Referral modes — Introducer / Sourcer (v2, 2026-08-11)
A **referral** carries a mode. A **person does not** — the same connector introduces one owner and sources another, and both are normal, so this is a per-referral field (`meta.referralMode[<companyId>]`, default `introducer`) set by yourco and read-only to the connector. Decision: `decisions/2026-08-11_connector-program-v2.md`.

| Mode | The connector | The approach is made by |
|---|---|---|
| **Introducer** | Introduces an owner they know | The connector |
| **Sourcer** | Submits a name + contact, no introduction | **yourco** |

⚠️ **Do not name either mode "Partner."** Partner already names the 11+ active-client commission tier below; two meanings across the console, the statements and the agreement is the drift `change-one-sweep-all` exists to stop.

## The submission bounty (Sourcer mode) — $25 + $25
Paid **on top of** any commission the same contact later earns:

| Event | Pays | Who confirms |
|---|---|---|
| Contact submitted **and verified** as a real, reachable business owner | **$25** | yourco, within **24–48h** — Bird owns the queue at the console's `/verify` |
| That contact **books a real conversation** (sit-down/audit — the ladder's own R1 evidence) | **$25** | The booking in the CRM |
| That contact becomes a paying client | the escalator below | Charles, at close |

⚠️ **Accrued, not payable.** `BOUNTY_PAYABLE` is False and every surface says so — nothing is paid until launch **and** counsel clear §A/§B, exactly as with the override. The amounts live once, in `crm/connector_statements.py`; the ledger is `bounties()` beside `books()`. **Never restate a figure here that the code does not hold.**

**Still open — the Founder's numbers, not an agent's:**
- Per-connector submission cap per **[[month]]** — mechanism is live (`meta.connectorSubmissionCap`); unset renders as *unset*, never as a guessed default.
- What exactly counts as a **[[verified contact]]** — the operator judgement standard behind the $25.
- Whether the booked-call $25 **[[stacks with / nets against]]** the first commission payment.

**Provenance is required, and it is a legal field.** On a Sourcer contact yourco is the caller, so TCPA / FL FTSA / CAN-SPAM attach to **yourco** — the submission form requires *how you know them* and records whether the owner is expecting contact (yes / no / unknown). Bought, scraped, or copied lists are rejected. Duplicates are detected on business/email/phone: one referrer per business, ever, first logged submission wins. Counsel: checklist items **4c** and **17a**.

## The connector structure (Type 2) — a tiered escalator
Recurring commission on the **referred client's monthly retainer, on collected revenue only**, rate set by the connector's count of **currently active (paying)** referred clients:

**Tier is set by live referred MRR (changed 2026-08-13, `decisions/2026-08-13_connector-console-v3.md`).** It used to band on *active client count*, which only works when deal sizes are tight — yourco's run $3k→$10k+, so a connector with 3 × $10,000 clients earned **10%** while one with 6 × $1,000 clients earned **12.5%**. The bigger producer paid the lower rate, and the program quietly rewarded referring the smallest businesses available.

| Tier | Live referred MRR | Recurring rate | ≈ Core clients | Applies to |
|---|---|---|---|---|
| **Referrer** | $0 – 14,999 | **10%** | up to 5 | their whole active book |
| **Senior** | $15,000 – 29,999 | **12.5%** | 5 – 10 | their whole active book |
| **Partner** | $30,000+ | **15%** | 10+ | their whole active book |

- **Round Core multiples.** $15,000 is 5 × the $3,000 Core floor; $30,000 is 10 × (the Founder set the upper band 2026-08-13).
- **⚠️ Slightly looser than the old count rule, deliberately.** The count thresholds were **6** and **11** actives — $18,000 and $33,000 of Core-floor revenue. The MRR bands sit one client below each, so an all-Core book reaches 12.5% at 5 clients instead of 6 and 15% at 10 instead of 11. That is a small real comp change in the connector's favour; **do not describe the move to MRR as like-for-like.**
- **The point of the change is the skew, not the thresholds.** A connector with 3 × $10,000 clients now out-earns one with 6 × $1,000 clients. The count rule had that backwards.
- **The rate lifts the whole book, not just the next client.** Cross $15,000 and every client pays 12.5%; cross $30,000 and every client pays 15%.
- **Tier is set by *live* revenue.** A churn that drops the book below a threshold moves the rate back until it recovers — connectors are paid to keep referred clients happy, not just to dump leads.
- **One computation.** `connector_statements._tier()` is asked about `tier_input()`; the console, the statement and Charles's payout cannot band on different numbers. `basis: "count"` in `meta.referralTiers` preserves the legacy rule for anything scored under it.
- **Residual for the life of each active account** — a referral becomes a compounding income line.

## Recruiter override — FULL DOWNLINE (multi-level)
A connector who brings *another connector* into the program earns **1%** of the **client revenue produced by their entire downline** — the connectors they recruited, the connectors those connectors recruited, and so on, all the way down. A connector can build a team and earn a slice of all of it on top of their own book. *(Chosen 2026-06-30, over the prior one-level cap.)*

**Who may recruit, and when the override pays — changed 2026-08-11 (`decisions/2026-08-11_connector-program-v2.md`).** Recruiting moved from **R2 → R1**: a connector may build a downline once **one referral has reached a real conversation**, and the override is **payable at R1 as well**. The old rule (a live client retained 90 days) made recruiting unreachable — with zero signed clients, nobody could ever recruit anyone. ⚠️ **Note what this removed:** the active-book qualification was the non-depth guardrail offered to counsel in place of the depth cap the Founder declined, so **no active-book qualification remains anywhere in the design**. That is the substance of checklist item **4c**, and it is a live question, not a settled one.

> ⚠️ **THIS IS A MULTI-LEVEL (MLM) STRUCTURE — counsel-gated, hard stop.** Unlimited override depth puts this under FTC + state MLM rules. What keeps it on the right side of the line: the override pays **only on real client revenue** a downline connector produces — **never for the act of recruiting**, and there is no buy-in. But it **cannot be offered to anyone** until **Ray + outside counsel** structure it: an **income-disclosure statement**, a **Partner/Referral Agreement**, and any depth/earnings guardrails counsel requires. Per-client load is modest at shallow depth (a client two levels down: 15% connector + 1% + 1% = ~17%) but compounds with depth — counsel sets the bound.

**Worked example (Lucas's network).** Lucas (5 clients, $18k/mo → Referrer 10% = $1,800) recruits John (3 clients, $10k/mo → 10% = $1,000); John recruits 2 connectors (2 clients each, $10k/mo each → 10% = $1,000 each). Overrides at 1% of downline client revenue: John earns $200 (on his 2 connectors' $20k); Lucas earns $300 (on his whole downline's $30k). Totals/mo: **Lucas $2,100 · John $1,200 · each sub-connector $1,000 = $5,300** on **$48,000** of network revenue (**~11%**). *(Note: under the 1–5 Tier-1 band, Lucas's 5 clients sit at 10%; he reaches 12.5% at 6.)*

## Equity track — top connectors (INTERNAL — not on the site; discussed 1:1; counsel-gated)
Not marketed. Raised only with a connector who's becoming a real distribution channel and wants ownership in what they're building. **Revenue = net-retained referred-client revenue over a trailing 12 months** (collected revenue from referred clients still active at measurement — not gross-booked).

| Trailing-12-mo referred revenue | Equity grant |
|---|---|
| ≥ $500k | **0.5%** |
| ≥ $750k | **1.0%** |
| ≥ $1.0M | **1.5%** |

**Program cap: yourco gives away at most 15% of the company across the entire connector-equity track.** Once 15% is committed, the track closes to new grants.

**Proposed mechanics (the Founder + counsel to finalize — these guardrails are what make the numbers safe):**
- **One grant per connector, set by their highest trailing-12-mo band — not additive, not repeated annually.** Hitting $1M once = 1.5% (not 0.5+1+1.5), and not 1.5% every year. Climbing $500k→$1M tops the connector up to the higher band.
- **Vests over 3–4 yrs, tied to retained revenue** — unvested equity claws back if the referred book churns below the band. Equity rewards durable channel, not a one-year spike.
- **Discretionary equity-incentive plan, not an entitlement printed in the commission agreement.**

> ⚠️ **SECURITIES GATE (bigger than the MLM gate).** Granting equity to non-employee referrers for revenue is securities + tax territory: needs an equity-incentive plan, a 409A valuation, the right securities exemption, and cap-table modeling. **Ray + outside counsel + the cap table before a single grant is discussed as real.** Until then this is directional, not a promise. Decision: `decisions/2026-06-30_rep-equity-track.md`.

## Why the margin holds
- **Recurring product, high margin.** The retainer is mostly margin once delivery is automated (yourco absorbs the low SMB token cost). A rate off a recurring, high-margin line is affordable in a way a one-time cut on a thin sale isn't.
- **Pay on collected revenue only.** Nothing on unpaid invoices or churned clients.
- **Bounded escalator.** Direct tops out at 20%; the override is 1% per downline level (counsel caps depth). **The higher 10/15/20 + multi-level override needs a fresh net-margin check vs the financial model (Charles + Polo) before lock** — this is a real margin step-up from the old 3/5/10.
- **Quality + delivery stay in-house** — a connector can't damage the thing that retains the client.

## Worked examples (AI OS retainers — the $3k / $5k / $10k bands, per the Core→Command tiers)
- **3 active @ $3,000 (Referrer, 10%):** ~$900/mo recurring.
- **6 active @ $5,000 (Senior, 12.5%):** ~$3,750/mo recurring.
- **12 active @ $10,000 (Partner, 15%):** ~$18,000/mo recurring — a real income line, paid only because they brought twelve paying clients. *(Updated 2026-07-05 from the old Tier-1 single-agent retainers to the OS bands — the OS is the unit of sale.)*

## The connector journey
1. **Apply / join** — short form; connector gets a referral link + code, signs the (counsel-cleared) Partner agreement, W-9 on file.
2. **Refer** — warm intro or link/code; the referred company is tagged to that connector in the CRM at first contact.
3. **yourco closes, builds, operates, owns** — the connector stays hands-off.
4. **Credit** — when the client signs and the first payment clears.
5. **Payout** — the **2nd Friday of each month** on revenue collected by the buffer close (clients billed the 1st, +3 days), at the connector's current tier (+ any full-downline override); late collections roll to the next run.

## The intro motion — one link, three sentences, any pain (v1.1, 2026-07-21)
A connector's whole job is the intro — never selling, never explaining AI. Each connector gets a **personalized link** (their referral code baked in → the "see yours" demo + audit booking) and a 3-sentence script with the **pain slot swapped to fit the owner** — this is *never* limited to missed calls:

> "You know how you [PAIN]? My guy builds an AI setup that handles that — here's a 2-minute demo with your name on it. Worth a look?"

**Pain variants** (pick what the connector actually hears from that owner):
- *keep missing calls when you're on a job* (intake)
- *take three weeks to get a quote out* (slow quoting/proposals)
- *do admin at 9pm instead of seeing your kids* (drowning in paperwork)
- *lose jobs because nobody followed up* (follow-up leakage)
- *go dark after 5pm while customers shop around* (after-hours)
- *chase invoices for months* (billing/AR)
- *can't answer "how's the business actually doing"* (owner visibility)

Every link routes to the **audit** — the audit does the selling and the diagnosing; the connector just opens the door. (Michelle owns the script variants; Webb owns the personalized-link surface.)

## Connector activation (v1.1 — the metric is activation, not signup)
Referral programs die from partners who never refer, not from bad comp. Every connector:
1. **Warm-map session (first week):** in the onboarding call, list **5 businesses** they know with a pain from the list above, pick **1**, and send that intro *the same week* — with help drafting it live on the call.
2. **Activation metric: first referral ≤ 30 days.** Tracked per connector in the CRM Referrals view.
3. **Dormancy nudge:** no referral activity for **45 days** → Bird surfaces it with a fresh, forwardable story (see go-live celebration below) — a reason to reach out, never a guilt nag. *(Runs as part of Bird's land-and-expand scope when the program activates.)*

## The delivery loop feeds the program (v1.1)
- **Day-30 client ask:** at day 30 of every live client, the weekly readout includes the referral ask — *"who are two other owners who should see this?"* (`02_delivery_loop.md` §5). Type 1 ($100/mo credit) and Type 2 (connectors) compound: the strongest connector is a thrilled client, and a thrilled client's own bookkeeper/agent is the warmest connector recruit.
- **Go-live celebration:** every 48h go-live becomes a short, client-approved story (what was drowning them → what runs itself now) pushed to the connector network as forwardable material. **Speed is the recruiting asset.** White-label rule applies: no client name unless the client approves.

## Attribution rules — v0 (written BEFORE connector #1 signs; **the Founder locks**, counsel reviews with the agreement)
The #1 thing that poisons referral programs at scale is a credit dispute handled ad-hoc. The rules, in advance:
1. **Credit = first logged touch.** The CRM `referrer` tag is set at the referred company's **first contact** — via the connector's link/code, or a named intro the connector **logs before or same-day** (email/Slack to yourco). Retroactive claims honored up to **[[7 days]]** after first contact, with evidence of the intro; after that, no.
2. **One referrer per company, ever.** Collisions (two connectors, or client-referrer + connector) → first logged touch wins, whole company. No splits — splits breed disputes.
3. **Attribution window: [[6 months]]** from logged intro to signed engagement. Expired → a fresh logged intro restarts it (same or different referrer).
4. **Whole-retainer, whole-life:** commission rides the referred client's full retainer as it grows (expansion included), while the client is active — per the escalator. No commission on one-time build fees *(unless the fast-start bounty is adopted — still open, `2026-06-30` decision)*.
5. **Self-referral:** nobody earns commission on their **own** bill. A company never refers itself, and the CRM's payout engine drops any such row. *(This replaces the old rule, which routed self-referrals onto the Type-1 credit path — that path no longer exists.)*
6. **Advisors vs connectors:** dual-role people earn commission only on deals sourced through their **connector** profile (`decisions/2026-07-06_advisors-connectors-taxonomy.md`); house/Advisor-worked deals don't pay the escalator.
7. **Disputes:** the Founder decides, decision logged as a CRM activity on the company, and any rule clarified as a result is added here — **forward-only**; no retroactive re-crediting.

## Attribution + tracking
- David's CRM tags the referrer on the company (`referrer: "<name/code>"`) at first contact.
- Charles computes each connector's active-client count, tier, and monthly commission (direct + full-downline override) from collected revenue, and runs payouts.
- **Monthly statements (built 2026-07-21):** `python3 crm/connector_statements.py --write` renders one transparent per-connector statement (actives · tier · rate · per-client commission · next-tier nudge · bill credit vs cash split) to `crm/statements/YYYY-MM/`. Charles runs it at the monthly close; visible fairness is the dispute-prevention layer for the attribution rules above.
- **Built — the Referrals view in the CRM** (David): each connector, their active clients, tier, referred MRR, and commission owed (direct + override), with a totals strip + "N more → next tier" nudge. Recruiter links (`+ set recruiter`, stored in `D.meta.repRecruiters`) now drive the override computed across the **full downline**. Rates + override configurable via Edit-tiers (`D.meta.referralTiers`, default **10/12.5/15 + 1% override** (verified in `crm/data.json` meta 2026-07-05)). **Client-referral ($100/mo credit) tracking is a CRM enhancement to add when the program activates.**

## Terms (counsel to finalize — Ray)
> 📄 **Counsel-prep drafts ready:** `processes/partnerships/legal/` — Partner Agreement, Income Disclosure Statement, and the MLM/FTC counsel-review checklist (all DRAFT, for outside counsel + the Founder).
- **Collected-revenue-only**; nothing on unpaid or churned.
- **Clawback** on a refund/chargeback within the first **[[60]] days**.
- **Cadence (locked 2026-07-05, `decisions/2026-07-05_billing-and-commission-cadence.md`):** clients auto-pay the **1st** → **3-day collection buffer** → commissions paid the **2nd Friday of the same month** on collected revenue; late collections roll to the next run. 1099 issued; W-9 before any payout.
- **MLM compliance (the gating item):** income-disclosure statement, no recruiting bonus, real-product-revenue-only, depth/earnings guardrails — **Ray + outside counsel** before a single connector is offered the downline override.
- **Compliance.** Connectors are independent + must not spam (CAN-SPAM/TCPA in the agreement; Rafi gate); no deceptive claims; yourco can terminate.
- **yourco owns the client relationship + the price.** Connectors don't quote, contract, or set pricing.

## Relationship to the rev-share model
The evolved **Mode 1 (referral partner)** from `rev-share-model.md` — its flat 15%/10% is replaced by this escalator. **Mode 2 (white-label)** is unchanged.

## Decisions — LOCKED 2026-06-30 (`decisions/2026-06-30_referral-program-v1.md`), amended 2026-08-11 (v2)
- ~~Two types: client **$100/mo credit** · connector escalator.~~ **Superseded 2026-08-13 — one rate card for everyone who refers; a client takes it off their own bill first, cash above it.**
- ✅ Connector tiers **10% / 12.5% / 15%** at 1–5 / 6–10 / 11+, whole active book.
- ✅ Override: **full downline (multi-level), 1%** — ⚠️ counsel-gated before offered.
- ✅ **v2:** referral **modes** (Introducer / Sourcer), per referral, never per person.
- ✅ **v2:** submission bounty **$25 verified + $25 booked call** — ⚠️ accrued, not payable; counsel item 4c.
- ✅ **v2:** recruiting **and** override payability move to **R1** — ⚠️ removes the active-book qualification.
- ✅ **v2:** connectors are yourco's **primary growth lever** (`processes/demand-generation.md`).
- 🟡 Equity track (internal, not marketed): $500k/$750k/$1M trailing-12-mo → 0.5/1/1.5%, 15% program cap — ⚠️ **securities-gated** (`decisions/2026-06-30_rep-equity-track.md`).
- ⬜ Still to lock (the Founder + Polo + Ray): fast-start build-fee bounty (yes/no), clawback window + post-exit tail, the **MLM legal structure** (Ray + outside counsel — the gating item), the **equity-incentive plan + 409A + securities review**, net-margin check (Charles/Polo).
