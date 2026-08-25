# 2026-08-10 — Three members at 50/35/15: the Founder · Partner B · Partner C

## Decision (the Founder)
yourco admits **two** partners rather than one, at **the Founder 50% · Partner B 35% · Partner C 15%**. This supersedes the 50/50 single-partner structure that `decisions/2026-08-05_partner-oa-profits-interest-spv.md` and OA draft v4 were built on. Both partners are moved to `teamRole: partner` in the CRM (still `prospect` status — nothing is papered), and the operating agreement is restated as **v5**.

## Context
The partner admission has been planned as 50/50 since 2026-07-20, with the OA reaching counsel-ready v4 on 2026-08-05 (D2 profits interest, D9 Founder SPV under Holdco). the Founder named the two partners and the split on 2026-08-10 while revising the financial model. Partner B was already in the CRM as a Connector at prospect stage with a Session 1 walkthrough prepared for him; Michael Partner C was in the CRM as a prospective connector added 2026-08-07. Neither was a member of anything.

## Why v5 was a restatement and not an edit
v4's own **§3.8(b)(v)** requires that any admission changing the Member count carry "a concurrent written amendment restating the governance, deadlock, Referee, shotgun, and buy-sell mechanics for the new Member count — **admission without that amendment is void**." A find-and-replace on the percentages would have produced a document that voided itself. Every mechanism built for exactly two parties had to be re-derived: the ROFR and Article 10 options needed allocation and over-allotment steps, the phantom-unit cost moved from 50/50 to pro rata, notices needed a multi-party clock rule, insurance went to three lives, and the shotgun had to be deleted outright.

## The thing the Founder needs to look at first
**50/35/15 does not give the Founder control, and it does not remove deadlock.** The Founder holds exactly half; the two partners together hold exactly half. Concretely:
- the Founder cannot pass any reserved matter alone. A 50% holder in a Florida LLC blocks; it does not act.
- Whenever Partner B and Mike agree with each other, the company is back in a 50/50 tie — the exact condition v4's entire deadlock apparatus existed to survive. The tie was not removed, only re-staffed.
- Under unanimous consent, the 15% holder has a full veto on every reserved matter. Under majority, 15% is the swing vote between the other two.

If the intent was the Founder-controls-the-company, this cap table does not deliver it and the split needs to change (51/34/15, or economics at 50/35/15 with voting drawn differently). If the intent was genuine three-way partnership, it does deliver that, and D10–D12 are what make it work. **That is the Founder's call and it is deliberately left open rather than assumed.**

## Three new blocking decisions (created by the structure, not by the drafting)
- **D10 — voting threshold on reserved matters.** Unanimous (everyone including the 15% holder gets a veto) · supermajority ≥66% (no two members can act alone) · simple majority >50% (the Founder plus either partner carries; the two partners at exactly 50% still cannot). Until this is chosen, §7.4 has no operative meaning.
- **D11 — deadlock end-game.** The v4 shotgun is **deleted**: "buy mine or sell me yours at my price" has no honest three-party form, and leaving it in would have been a clause that reads as if it functions. Options drafted: Referee-final · multi-party sealed-bid auction · Founder casting vote on defined categories · dissolution ladder. **Until one is chosen the agreement has no end-game**, which is worse than v4's imperfect one.
- **D12 — is Mike symmetric with Partner B?** v5 drafts him symmetric by default because that is the conservative reading. Nothing in the workspace records what Mike is contributing, what his lane is, or whether his commitment is full-time. If it is not service, his profits-interest analysis changes and §4.1, Schedule C-1, Schedule D and §10.1(i) each need a second version.

## Consequences already swept
- **Gate #14 regressed from 🟠 counsel-ready to 🔴.** It was the closest gate to clearing; it is now the furthest, by the Founder's own change. Worth stating plainly rather than burying: this decision cost the OA its counsel-ready status.
- **Referee risk is now asymmetric.** Sample Contact is the §9.2A Referee. He is family to the Founder Principal and (per the CRM's "Brother" relationship field on Partner B) plausibly to Partner Principal A as well — meaning Partner Principal B may be asked to accept a tie-breaker related to the other two. v5 flags this as load-bearing for enforceability and asks counsel whether Mike needs a veto on the Referee's identity.
- **Independent counsel must be separate for each partner** (§19.7) — two partners with different stakes sharing one lawyer is its own conflict.
- Insurance goes from two lives to three (~1.5× cost), not yet in the financial model.
- The financial model now carries an ownership block (the Founder 50 / Partner B 35 / Mike 15) and an EBITDA allocation memo, marked NOT PAPERED.

## Reversibility
Fully reversible today — nothing is signed, no entity is formed, no Units exist, and both partners are `prospect` in the CRM. The cost of reversing is the drafting time already spent. **After signing it is effectively irreversible**: unwinding a member admission means a buyout at Fair Value under Article 10, with tax consequences on both sides. The entire value of deciding D10–D12 now rather than later is that this is the last moment the structure is free to change.

## Trip-wire
- **Review:** 2026-09-10
- **Overturn if:** D10, D11 and D12 remain unanswered a month on — an unanswerable governance question usually means the split itself is wrong, not that the drafting needs another pass. Also overturn if Mike's contribution, once written down, turns out not to be substantially-full-time service, since the 15% profits interest was priced on the assumption that it is.
- **Check:** `counselGatesBlocked >= 6 and not OtherVentureCleared`
- **Check covers:** only that the gate backlog has not cleared. Whether D10–D12 were actually answered is not machine-visible — no store records a decision that has not been written — so a firing check is a prompt to reread this file against the OA's pre-signing checklist, never a verdict.
