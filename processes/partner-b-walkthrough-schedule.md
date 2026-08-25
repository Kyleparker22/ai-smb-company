# Walking Partner B through yourco — a 6-session schedule

> Built 2026-08-09 for the Founder. ~12 hours across 6 sessions of ~2 hours. Partner B is being walked through
> everything yourco has built, planned, and not yet done — in the context of a possible partnership
> (`finance/legal-docs/operating-agreement-DRAFT.md`, counsel gate #14, whose open fills are *partner
> identity, C-1 lanes, Schedule B $*).

---

## THE ACTUAL CALENDAR (set by the Founder 2026-08-10) — this supersedes the 6-session sequencing below

The agreed run is **review one domain, lock it the next session** — a rolling review→lock cadence
across nine working days, not six thematic sessions. The six sessions below stay useful as the
*content* for each domain (what to open, what the honest half is); this table is the *schedule*.

| Date | Lock in | Then review |
|---|---|---|
| **Tue 8/11** | — | **Business Plan** + **Financial Model** + **CRM** (review *and* lock, all three, same day) |
| **Wed 8/12** | — | **HQ** + **Connector Console** + **Connector/Referral program** (review *and* lock) |
| **Thu 8/13** | — | **Agents** (review; lock by Mon 8/17) |
| **Mon 8/17** | **Agents** | **Sales** — process, workflows |
| **Tue 8/18** | **Sales** | **Marketing** |
| **Wed 8/19** | **Marketing** | **Software / tools / expenses / costs** |
| **Thu 8/20** | **Software / tools / expenses / costs** | **Back office** |
| **Fri 8/21** | **Back office** | **Legal** |
| **Mon 8/24** | **Legal** | **Overall organization + simplicity of the business** |
| **Wed 8/26** | **Organization + simplicity** | **Who to add to the CRM** — potential Connectors, potential Prospects |

**Where each domain's material lives** (open these, don't re-derive them):

- **Business Plan / Financial Model** — `06_business-plan.md` · `finance/yourco-financial-model.xlsx` ·
  `finance/model-assumptions.md` · `finance/runway.md`. Ownership as of 2026-08-10: **model = Charles,
  plan = Melanie, HQ mirrors the workbook**. Session 5 below is the script.
- **CRM** — `yourco-crm` (:8790); the insight layer is the differentiated half (`decisions/2026-08-07_crm-insight-layer.md`).
- **HQ** — `yourco-hq` (:8791): Overview, Board, Clients, Evidence, Goals, Loops, Trust.
- **Connector console / packet** — `yourco-connector-console` (:8807) · `yourco-connector-packet` (:8806) ·
  `decisions/2026-06-30_referral-program-v1.md` · the equity track (`2026-06-30_rep-equity-track.md`).
  ⚠️ Both the multi-level override and the equity track are **counsel-gated** — flag that at the lock,
  not after.
- **Agents** — `04_agent_roster.md` · `runtime/agent-registry.json` (canonical) · `runtime/README.md` ·
  `processes/autonomy-matrix.md`. Session 4 below is the script.
- **Sales** — `processes/audit-sop.md` · `processes/outbound/` · `02_delivery_loop.md`. Session 3 is the script.
- **Marketing** — `processes/demand-generation.md` · `processes/content/content-engine.md` ·
  `brand/writing-rules.md` · the staged site (`agents/webb/pages/yourco-site-v2/`).
- **Software / tools / costs** — `finance/expenses.md` · `runtime/connectors.md` · `processes/connections-map.md`.
- **Back office** — `processes/onboarding.md` · `offboarding.md` · `payments.md` · `finance/` monthly close.
- **Legal** — `processes/counsel-gates.md` · `processes/launch-gate.md` ·
  `finance/legal-docs/operating-agreement-DRAFT.md` + `oa-review_ray_2026-08-05.md`. Session 6 is the script.
- **CRM additions (8/26)** — `processes/outbound/warm-network.md`; add via the CRM, and remember the
  people taxonomy: **Advisors** (full-time salespeople) vs **Connectors** (referral partners); a
  dual-role person gets two profiles (`decisions/2026-07-06_advisors-connectors-taxonomy.md`).

**Standing rules for this run:**

- **Membership: the OA names three; the CRM now carries four** — the Founder / Partner B / Partner C in
  OA v5 (2026-08-10), plus **Sample Contact**, moved to prospective partner 2026-08-18 and **not in
  the OA — no allocation exists for him**. The OA (v5) and gate #14 regressed to 🔴 on the
  three-member change and have not moved since. The Session 6 text below still carries the old two-member percentages and says
  "both" in places; read it as at least three members.
  **Percentages are withheld from display across HQ and the CRM at the Founder's request (2026-08-18)** —
  they are unchanged in `decisions/2026-08-10_three-member-split.md` and the OA draft, not deleted.
- **Every lock produces a decision entry.** Use the `log-decision` skill the same day — a domain
  "locked" with nothing in `decisions/` is not locked. **Add a `**Locks:** <domain>` line to that
  decision**, naming the domain exactly as this calendar spells it (`Business Plan`, `Financial
  Model`, `CRM`, …). That one line is what HQ → **Partners** reads to mark the domain locked; a
  decision without it shows as *likely — unconfirmed*, because a title keyword match is a guess
  and this run is too consequential to track on guesses. One decision may lock several domains:
  `**Locks:** Business Plan, Financial Model, CRM`.
- **Change-one-sweep-all applies to every lock.** When a locked number or name differs from what's on
  the site / packets / CRM meta / CLAUDE.md, grep and fix every surface in the same commit, and add the
  invariant to `runtime/consistency-check.py` if a human caught it by eye.
- **Nothing locked here goes external** until the launch-gate clears (`processes/launch-gate.md`).

## The sequencing logic — read this before you schedule anything

Three principles drive the order, and they're worth understanding because the instinct is to do it
backwards:

1. **Lead with the hard truth, not the impressive machine.** The OS is genuinely remarkable and it is
   tempting to open with 27 agents and a beautiful dashboard. Don't. If Partner B sees the machine before
   he sees *$0 revenue, $0 cash, 0 clients, a paused runtime*, then when he finds those later — and he
   will — it reads as concealment, and every impressive thing before it gets re-priced. Told first, by
   you, the same facts read as candor and buy credibility for everything after.
2. **Build the "why" before the "how."** The agents only make sense once he knows what they're for.
   Product → market → machine, never machine → product.
3. **End on his decision, not on your tour.** The last session is about his lane and what he'd own.
   Everything before it is evidence for that conversation.

**Don't compress this into one marathon.** Two hours is the honest limit for absorption; six two-hour
sessions with a day between beats twelve hours in a weekend. If sessions must be back-to-back, break
between 3 and 4 — that's the natural seam between "the business" and "the machine."

---

## Session 1 — What yourco is, and where it actually stands (2h)

**Goal:** Partner B can explain yourco to someone else, and knows the worst facts before he knows the best.

| | |
|---|---|
| **Open** | `CLAUDE.md` · `01_company.md` · `processes/ai-os-modules.md` · `pricing/v0/os-tiers.md` |
| **Arc** | The thesis (intelligence is commoditizing; the edge is deployment) → the moat (reliability, eval, approval, executive trust) → the offering: **audit first → custom AI OS** → the 8 pillars → the four tiers → who it's for |
| **The honest half — do not skip or soften** | 0 clients · $0 revenue · $0 cash · ~$614/mo burn on a personal card · 3 deals past first touch, stalled 20–54 days · the runtime paused 5 days without anyone noticing · counsel never engaged · the launch-gate still undefined. Hand him `loops/_audit/2026-08-09_full-business-audit.md` and let him read the headline himself. |
| **The question he'll ask** | *"If the product is this good, why has nobody bought it?"* The honest answer — nobody has been asked, and a yes couldn't be invoiced today — is the whole reason a partner would matter. |
| **Homework** | Partner B reads the audit's five findings + `01_company.md`. |

---

## Session 2 — What a client actually gets (2h)

**Goal:** Kill the "is this vapor?" question permanently. This is the strongest session — real software.

| | |
|---|---|
| **Open** | `02_delivery_loop.md` · Sample Client's platform (`sample-client-platform` :8804) · Design Studio (`sample-client-design-studio` :8799) · Sample Product (`nick-storm-demo` :8796, `nick-crew-app` :8798) · Sample Realty (`sample-realty-tour` :8801) · the demo kit (`yourco-demo-kit` :8795) · client console (`yourco-client-console` :8792) |
| **Arc** | The delivery loop (discovery → build → eval/gates → go-live → weekly iteration → expansion) → the 8 pillars and the three form factors → **then show, don't tell**: the Field-to-Quote platform, the Design Studio, Sample Product running on Cloudflare + D1, Sample Realty's site and trust-account rebuild (which found a real $1,830 error) |
| **The point to land** | These are not mockups. Sample Product is 2,490 lines of working Python. This is what "we build and operate it" actually means. |
| **The honest half** | None of it is paid for yet. Every one of these was given free. That's the give-first doctrine working *and* the ask never being made. |
| **Homework** | Partner B clicks through the demo kit as if he were a prospect. |

---

## Session 3 — The commercial engine, and why nothing has closed (2h)

**Goal:** He understands the funnel, the three live deals, and the actual constraint. **This is the
session most likely to define his lane** — the gap is commercial, not technical.

| | |
|---|---|
| **Open** | CRM (`yourco-crm`, :8790) — Prospects, Pipeline, Clients, Referrals · `processes/audit-sop.md` · `processes/outbound/warm-network.md` · the connector console (`yourco-connector-console`, :8807) |
| **Arc** | The audit as the **free** front door (the Founder 2026-08-16; $1,000/$1,500 suspended as the return price, credit mechanic retired) → the CRM and the 25 companies → the three real deals and exactly where each sits → outbound machinery → the connector/referral program (ladder, training, glass ledger, console) |
| **The honest half** | The audit has been delivered **zero times in 62 days**. 40 of 49 contacts have no email or phone. Zero cold emails ever sent. 19 of 22 deals have never been contacted. The connector program has 0 connectors and is counsel-gated. |
| **The question to put to him directly** | *"Which of these would you own?"* Sourcing? The ask? Delivery? This is the real content of a partnership. |
| **Homework** | Partner B reads the connector packet (`yourco-connector-packet` :8806) — he's already in the CRM as a prospective connector, so it's directly relevant. |

---

## Session 4 — The OS: how one person runs all of this (2–3h)

**Goal:** The reveal — but now it lands as *leverage*, because he knows what it's for.

| | |
|---|---|
| **Open** | `04_agent_roster.md` (the new internal/client-touching/both tags) · HQ (`yourco-hq`, :8791) — Overview, Board, Goals, Reports, Loops, Trust · `runtime/README.md` · `processes/autonomy-matrix.md` |
| **Arc** | The two agent populations (yourco's 27 vs the client's pillars — start here or he'll conflate them) → dissect the agents in groups rather than one by one: **the money agents** (Charles, Polo, Harry) · **the sales agents** (Reilly, Michelle, Sadie, David, Bella) · **the make agents** (Katie, Reed, Webb, Pickle) · **the delivery agents** (Janice, Kimi, Kortney, Bird) · **the trust agents** (Kolby, Rafi, Ray, Atlas) · **the conductors** (Melanie, Jim, Kemba, Kori, Brett, Luka, Mario) → then the runtime: systemd timers, the approval gate (no send / no delete / no Bash), the loop contract, learnings as the feedback substrate → then HQ and the Board |
| **The moat made concrete** | The autonomy matrix: autonomy is earned per-action on eval evidence and lost when evidence reverses. Show the same idea applied to humans in the connector trust ladder. This is the thing no-code can't copy. |
| **The honest half** | It's paused. Five of 27 agents have never produced anything; six are dormant. The watchdog failed silently and reported "all clear" for five days. The audit recommends merging roughly a third of the roster. |
| **Homework** | None — this one's heavy enough. |

---

## Session 5 — The money (2h)

**Goal:** He can form a real opinion on whether the economics work. **If a partnership is on the table,
this is the session that matters most.**

| | |
|---|---|
| **Open** | `06_business-plan.md` (v1.2, realigned 2026-08-10) · `finance/yourco-financial-model.xlsx` · `finance/model-assumptions.md` (§7 resynced 2026-08-10) · `finance/runway.md` · `finance/expenses.md` |
| **Arc** | The plan's thesis and projections — **Target: 50 / 118 / 190 clients, $1.02M / $4.34M / $8.61M recognized revenue, $10.23M ARR run-rate at end of Y3, $4.19M EBITDA, 13 people** (resynced 2026-08-10; the $670k/$4.4M/$12M figures quoted before that date are dead) → the model as a *planning tool*: change one assumption, watch it move → the headcount plan: **one hire type, the Advisor at $10,000/mo fully loaded, hired on client load, no hire before client 51** → the principals' capacity gliding to zero by month 24 → scenarios → **the cash structure (2026-08-10): the Founder injects $50,000 alone as a repayable founder loan, all three principals paid from month 1, breakeven month 4, the Founder repaid month 5** → unit economics per client |
| **The honest half** | Total spent building all of this: **~$3,000 cash** over two months (the Founder's estimate 2026-08-10, pending receipts — it is also the figure inside the repayable loan balance, so it needs to be right). Compute consumed would have cost $11k+ at API list price but rode a $200/mo subscription. There is no conversion data, no churn data, no CAC — every one of those is an assumption with n=0, and the model labels them as such. |
| **The question he'll ask** | *"What do I have to put in?"* **As of 2026-08-10 the answer to Partner B is: no cash, and you are paid from month 1.** the Founder injects **$50,000 alone** on day one as a **repayable founder loan** of **$53,000** (incl. ~$3,000 of build spend already funded, estimate pending receipts), repaid as a lump sum in month 5 (Target) and ranking **behind** distributions, not ahead. All three principals draw $50k from month 1; there is no unpaid-founder period any more. **the Founder has a further $50,000 available if needed** → $100,000 total. Decision: `decisions/2026-08-10_cash-structure-and-model-recalibration.md`. **The $50k does not cover every case — lead with that.** Once equipment, partner expenses and conferences are charged, **Conservative runs $11,155 below zero in month 5** and Target consumes 97% of the injection. The second $50k is what makes the downside solvent, not a cushion on top of it. Nothing about the business changed — we started charging costs the model had ignored. Say it yourself; it is the line that makes the rest credible. |

---

## Session 6 — Systems, risk, and Partner B's lane (2h)

**Goal:** End on decisions, not admiration.

| | |
|---|---|
| **Open** | `runtime/connectors.md` · `processes/counsel-gates.md` · `processes/launch-gate.md` · `decisions/2026-08-09_google-to-microsoft-migration.md` · `finance/legal-docs/operating-agreement-DRAFT.md` + `oa-review_ray_2026-08-05.md` |
| **Arc** | The tool stack and what each costs → the Microsoft migration → security posture (secrets discipline, the approval gate, no live env file in git) → **the gates**: 12 counsel gates blocked, no counsel engaged, the launch-gate undefined for 35 days → then the partnership itself |
| **The partnership conversation** | The OA's open fills are exactly three: **partner identity · C-1 lanes (who owns what) · Schedule B $ (the Distribution Threshold you recover first)**. Ray's review lists 8 counsel questions that travel with it. The vesting is 4-year with a 1-year cliff on the partner side, and the 50% is structured as a **profits interest** — he shares in value created *after* the grant, not the pre-grant value. Be able to explain why that protects them both. |
| **End with** | The first 90 days: what Partner B owns, what the Founder owns, what has to be true by when. And the four actions that unblock everything — counsel, Stripe/bank, the warm sends, defining the launch-gate. |

---

## What to prepare before Session 1

- [ ] Confirm the runtime state — it's paused; decide whether to un-pause before you demo it, or explain it paused (**explaining it paused is more honest and, frankly, more impressive**)
- [ ] Have the financial model finished (`finance/yourco-financial-model.xlsx`)
- [ ] Start the surfaces you'll actually open — `./show.sh`, or `preview_start` by name from `.claude/launch.json`
- [ ] Decide *before Session 6* whether Partner B is the intended partner, or whether these sessions are how you find out. Both are legitimate; they lead to different conversations, and knowing which you're in prevents an awkward turn.

## One framing for the whole series

The temptation across twelve hours is to sell. Don't. Partner B isn't a prospect — he's someone deciding
whether to bet time on this. **The most persuasive thing available is the fact that yourco's own systems
refuse to flatter it**: the evidence door that won't state a number it can't defend, the estimator that
refuses at n<3, the audit that says the machine is ahead and the business hasn't started. Show him that
and the honesty *is* the pitch.
