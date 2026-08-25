# 2026-08-08 — The Reach/Land batch: eleven offerings aimed at the stage the board was thin at

## Decision (the Founder: "build these")
Eleven new frontier offerings are adopted and boarded as rows **21–31** in `offerings/_frontier-roadmap.md`, all chosen to attack **Reach and Land** — the two flywheel stages the board's own coverage line showed thinnest — and all designed to work **inside the launch-gate** (1:1, unbranded, nothing sent, nothing published).

**Five are built and runnable today:** Mirror Close (#21) · Simulated Company (#22) · Spend Teardown (#23) · Calibration Wager (#25) · Capacity Board (#27).
**Six are spec'd against named triggers:** Trip-Wire Pricing (#24) · Referring Agent (#26) · Reversibility Guarantee (#28) · Churn Tripwire (#29) · Expansion by Vacancy (#30) · Re-Audit (#31).

the Founder merged what had been two separate ideas — *audit the AI they already bought* and *the found-money pass* — into one instrument, and widened it: **audit the entire stack and services, not just the AI**, to find where the budget can be cleaned up. That merge is #23.

## Context
The Frontier Ten (2026-08-06) had grown to 18 boarded offerings and covered the flywheel well past the middle: five ideas at Prove, three at Expand, three at Compound. Its own coverage line showed **Reach with two and Land with one**, and both Reach ideas (The Applicant, Patronage) were gated on OtherVenture or post-launch, while the single Land idea (Business ER) was triggered on "delivery proven."

Meanwhile the live commercial state is the opposite shape: **0 signed clients, 0 MRR**, 22 deals of which 19 sit at relationship, and one at proposal — Sample Client, stalled, which the 2026-07-04 full-OS audit already named the top commercial gap. The board was strongest exactly where yourco has no clients and weakest exactly where its only problem is.

A second fact shaped the batch. All three live relationships have the same defect: **substantial delivered value, no paper, no price.** Sample Product is live and operating unpapered; Sample Realty has a site, a PM module, listing presentations and a trust-account reconciliation shipped with no proposal ever sent; Sample Client had three hours of co-design against $0 committed. The mirror had already named it — *"the free-build ratchet risk on OUR side."* Several of these offerings are aimed at that specific pathology rather than at retention in the abstract, because you cannot churn a client who does not pay.

## Options considered
- **More Prove/Expand ideas** — rejected. The board is already deep there and none of it converts a first client.
- **Reach ideas that need launch** (paid channels, published surfaces, outbound at scale) — rejected for this batch. Everything here had to be usable before OtherVenture clears, or it would join the queue of built-but-unusable machinery.
- **Retention machinery for current clients** — reframed rather than rejected. With zero paying clients, retention instruments were re-aimed at value capture (#24, #29, #31), and the ones that genuinely need a live client carry that as an explicit trigger rather than being pretended into readiness.
- **Reach/Land batch usable inside the gate (chosen)** — eleven offerings, five built the same day, six triggered.

## Why
- **It attacks the binding constraint.** Zero signed clients is not a Prove problem or an Expand problem.
- **It reuses machinery rather than adding surface.** #21 renders from the existing `mirror.compute()`; #22 fills the live demo kit through the playground's data-substitution architecture; #23, #25, #27 are new modules but read stores that already existed (build journal, CRM, eval ledger); #24 and #29 point `tripwires.py` at modules and relationships; #30 points `vacancies.py` at the client's org. Only #26 and #28 need genuinely new work.
- **Every one of them is honest by construction, and two prove it by refusing on today's data.** The Capacity Board will not quote a slot date because all three build-journal sessions are backfills rather than measured runs. The Mirror Close refuses to render for Prospect A and Sample Realty because their mirrors have never been filled in. Those refusals are the product working, and they were left visible rather than softened.

## Guardrails (load-bearing, carried in each spec's §8)
1. **Never a modelled figure presented as a delivered result.** #22 labels every generated number "modelled from what you told us, not a measured result"; the uptime slot renders "—". Pre-revenue credibility gate.
2. **Never blend evidenced and modelled money.** #23 reports three separate columns and has no field for a combined headline. Idle seats are evidenced as *idle*, not as *recoverable* — contract terms decide that.
3. **Never soften the buyer's copy relative to the internal board.** #21 renders from the same computation; there is no external-safe variant of the deal.
4. **Never score what we failed to measure.** #25 reports unmeasured predictions as unmeasured, and names it as yourco's failure, not evidence about the owner.
5. **Never quote scarcity we can't compute.** #27 refuses below three *measured* build sessions, inheriting the build journal's own threshold; backfills never count.
6. **Never ingest a referral partner's client list.** #26 runs inside the partner's tenant and returns to the partner only; yourco receives a name only when the partner makes an intro.
7. **The replaceability fence is enforced in code**, not intention: systems of record, compliance-locked tools, payments rails and network-effect products cannot be marked replaceable by an optimistic input.

## Counsel + numbering
- **New gate #16** — trip-wire billing-pause / service-credit language (Ray + counsel, rides the gate #1 package; Polo owns module-level retainer decomposition). Blocks #24 and #29's billing consequence.
- **#26 carries the AICPA §1.520 flag** already logged on 2026-07-20, and must ship **single-level** so it is not blocked behind gate #5 (MLM).
- **#28 rides gate #1** and may **narrow gate #13**: portability is promisable without resolving IP ownership, and the two must never be conflated in copy.
- **A numbering collision was found and fixed while doing this.** Two different rows in `processes/counsel-gates.md` were both numbered **13** (Sample Client postcard imagery, added 07-20; SaaS-replacement ownership/IP, added 08-07), so every "gate #13" citation in the repo was ambiguous. The postcard gate is renumbered **13 → 15** with its four citations swept; SaaS-replacement keeps #13 so the decision, `new-offering-lines.md` B7 and `audit-sop.md` stay correct. **A machine invariant now guards it** — `runtime/consistency-check.py` fails on any duplicate gate number and prints the next free one (currently #17), per the house rule that drift caught by eye becomes a check.

## Reversibility
Cheap, and asymmetric by design. The five built modules are read-only analysis over existing stores — deleting them removes nothing but themselves, and none is wired into a loop or a dashboard poll. The six specs are documents. The only sticky items are contractual: gate #16's billing-pause clause and #28's exit clause both enter engagement agreements, and once a client has been promised a rehearsed exit or an automatic pause it cannot be quietly withdrawn — which is why both are counsel-gated before any proposal carries them, rather than after.

Kill signals: the Mirror Close reads as manipulative rather than disarming in two real conversations (it is a tone-dependent instrument and the tone is the Founder's, not the tool's); the Simulated Company's generated walkthroughs get mistaken for delivered results despite the labels; or the batch pulls build capacity away from closing the three live relationships, which would make it the roadmap's own named failure mode — building instead of selling.

## Downstream (swept this session)
- `offerings/<slug>/SPEC.md` ×11 — new, house format.
- `offerings/_frontier-roadmap.md` — rows 21–31, the batch-5 section, flywheel coverage (Retain named as a stage for the first time), spec slug list.
- `processes/audit-sop.md` — the full spend teardown lens · the wager capture at Step 2 · **the baseline-preservation rule**, which is the one part of this batch that changes behaviour today.
- `processes/counsel-gates.md` — gate #16 added, postcard gate renumbered to #15, collision recorded in the changelog.
- `clients/sample-client/05_leadgen-postcards-concept.md` ×3 + `loops/open-loops/2026-08-07.md` ×1 — gate citations repointed to #15.
- `runtime/consistency-check.py` — duplicate-gate-number invariant.
- `crm/_README.md` — `mirror_close.py` and `wager.py` rows.
- `.claude/launch.json` — `yourco-prospect-demo` (:8809) for generated walkthroughs.
- New code: `crm/mirror_close.py` · `crm/wager.py` · `runtime/capacity.py` · `runtime/spend_teardown.py` · `playground/prospect.py`.

## Trip-wire
- **Review:** 2026-11-08
- **Overturn if:** three months on, none of the five built instruments has been used in a real conversation — which would mean the batch was a build-instead-of-sell episode and the roadmap's stated failure mode caught yourco anyway. Also overturn the *inside-the-gate* framing if OtherVenture clears, since the constraint that shaped every choice here would no longer bind.
- **Check:** `signedClients >= 1 or OtherVentureCleared`
- **Check covers:** the two machine-visible conditions only. Whether the instruments were actually *used* is not instrumented anywhere — no store records "the Founder handed someone a mirror brief" — so a firing check is a prompt to reread this list against what really happened, never a verdict that the batch worked.
