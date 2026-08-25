# Decision — referral program structure (tiered recurring escalator)

**Date:** 2026-06-14 · **Owner:** the Founder + Polo (numbers) + Bird (program) + Charles (payouts) · **Status:** ⚠️ **UPDATED 2026-06-30** — numbers raised to **10/15/20**, **two partner types** added (client $100/mo credit + rep escalator), and the override went **full-downline (multi-level)**: see `decisions/2026-06-30_referral-program-v1.md`. *(This doc = the original v0 shape + rationale.)*

## Decision
Build the referral program as a **performance-only sales force paid a recurring, volume-tiered cut** of each referred client's monthly retainer. Rate rises with the rep's count of active (paying) referred clients and applies to their whole active book: **3%** at 1–4 clients, **5%** at 5–9, **10%** at 10+ (set 2026-06-14; the steeper climb to the 10% top tier pulls reps to grow their book). Residual for the life of each active account, on collected revenue only. Full spec: `processes/partnerships/referral-program.md`.

## Context
the Founder wants a no-risk channel that only costs money when it produces paying clients, and that pulls reps to bring more. A flat referral commission already existed (`rev-share-model.md → Mode 1`, 15% build / 10% retainer). the Founder's tiered escalator is a sharper version aimed at a broad referral force, not just agency partners. This decision supersedes the flat Mode 1 numbers; Mode 2 (white-label) is unchanged.

## Why this shape
- **Tier on *active* clients, applied to the whole book.** Matches the Founder's "10% of the total monthly" intent, makes the 4→5 and 9→10 jumps feel like real rewards, and ties the rep's rate to retention — a churned client can drop them a tier, so they care that referrals stay happy, not just that they signed.
- **Recurring, not a one-time bounty.** Turns a referral into a compounding income line and keeps reps engaged. The retainer is high-margin recurring, so 10% off the top is affordable in a way a one-time cut on a thin sale isn't.
- **Pay on collected revenue only; cap at 10%; quality stays in-house.** Protects margin and the moat. The rep introduces; yourco closes, builds, operates, and owns the relationship and the price.

## Recruiter override (added 2026-06-14)
A rep who recruits another rep earns **1%** (configurable) on the clients that recruited rep brings in, residual while active. **One level only**, paid **on client revenue, never on the act of recruiting** — the two things that keep it clear of FTC pyramid rules. Max payout per client stays bounded (10% direct + 1% override = 11%). **Ray reviews the multi-level structure before it's offered.** Built into the CRM Referrals view (`D.meta.repRecruiters` + a 1% override default in `D.meta.referralTiers`).

## Open decisions (the Founder + Polo to lock)
- Confirm tiers/rates (5/7/10 at 1–4 / 5–9 / 10+) and the whole-book escalator.
- Fast-start one-time build-fee bounty (5–10%) vs pure recurring.
- Clawback window (30/60/90 days) and post-exit commission tail.
- Counsel: the Referral Agreement (Ray) + the W-9/1099 payout flow (Charles/Harry).
- Net-margin-after-commission check against the financial model (Charles/Polo).

## Built (operational)
The Referrals view in the CRM (David) is live: each rep, their active clients, current tier, referred MRR, and monthly commission owed, with rates configurable via Edit-tiers (`D.meta.referralTiers`, default 3/5/10). A company carries a `Referrer` field; active clients = referred companies whose deal is Live.

## Reversibility
Easy pre-launch — it's a staged proposal with no reps recruited. Once reps are signed, rate changes only apply going forward (existing agreements honor their terms), so lock the v0 numbers deliberately before recruiting.

## Launch posture
Built and staged. No rep recruited and no economics communicated until the launch-gate clears and the Founder locks the numbers.
