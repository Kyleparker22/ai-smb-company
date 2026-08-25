# Walkthrough locks, round one — seven domains locked at their current state

**Locks:** Business Plan, Financial Model, CRM, HQ, Connector Console, Connector/Referral program, Agents

## Decision

the Founder and Partner B reviewed and **locked** seven domains of the Partner B walkthrough run
(`processes/partner-b-walkthrough-schedule.md`): **Business Plan · Financial Model · CRM · HQ ·
Connector Console · Connector/Referral program · Agents**.

The lock means: **what is in the repo as of this commit is the agreed baseline.** Changes to these
domains from here are changes against a settled reference rather than continued drafting, and each
should say what it is changing and why.

## Context

The run was set on 2026-08-10 as review-one-domain, lock-it-next-session across nine working days.
Business Plan, Financial Model and CRM were the Tue 8/11 session; HQ, Connector Console and the
Connector/Referral program were Wed 8/12. Agents were reviewed against fresh evidence on 2026-08-16
(`loops/_audit/2026-08-16_agents-review.md`) ahead of their Mon 8/17 lock date.

Before this entry, `dashboard/lockin.py` read **1 of 14 domains confirmed locked**. Three decisions
from 8/13 carried `Locks:` lines with free-text values (*"referral economics"*, *"connector console
scope"*, *"pipeline ladder"*) rather than the calendar's domain names, so the tracker could only rate
them *likely — unconfirmed*; four domains had no decision at all. The work had happened and the record
had not caught up, which is precisely the failure the `Locks:` convention exists to prevent.

## What this entry does and does not claim

**It records the lock. It does not reconstruct the deliberation.** These sessions were held between
the Founder and Partner B; this file was written afterwards from the schedule and the repo state, so it
deliberately does not put words in either participant's mouth about what was argued. Where a domain's
substance was decided in its own entry — `2026-08-13_one-referral-rate-card.md`,
`2026-08-13_connector-console-v3.md`, `2026-08-10_cash-structure-and-model-recalibration.md` — that
entry remains the authority on the *content*; this one establishes the *baseline date*.

## The one lock that carries a caveat: Agents

The Agents review found the runtime **paused for ~12 days** (2026-08-04 → 2026-08-16), preceded by a
5-day VPS outage and three weeks of intermittent API-credit failures, with the watchdog itself paused
and blind for five weeks. Twelve loops have not run successfully in over a month; four have never
produced anything.

**So this locks the agent roster's *design*, not its *performance*.** There is no clean month of
operation to judge performance on, and claiming otherwise would make the lock a fiction. The open
items the review raised — an off-box dead-man's-switch, auto-recharge and auto-renew on billing, and
the merge/retire pass the 08-09 audit recommended — are **not closed by this lock** and remain open.

## Options considered

- **Wait for a clean month of agent operation before locking Agents.** Rejected: it would hold the
  whole run hostage to a 30-day wait, and the roster's design is reviewable now even though its
  output is not.
- **Write one decision per domain.** Rejected as ceremony — the substance already lives in the
  per-topic decisions; what was missing was a dated baseline, and seven files saying "locked" would
  add records without adding information.
- **Chosen: one entry, seven domains, with the Agents caveat stated in the entry rather than dropped.**

## Reversibility

A lock is a baseline, not a freeze. Any of these can be reopened by a later decision that names what
changed and why — which is the normal path, not an exception. The Agents lock in particular should be
revisited once a full month of uninterrupted runtime exists, because that is the first point at which
performance becomes a fact rather than an assumption.

## Trip-wire

- **Review:** 2026-09-16
- **Overturn if:** the runtime has not sustained 30 consecutive days of scheduled operation since the
  2026-08-16 resume — in which case the Agents lock was taken on a design that has still never been
  observed working, and the roster question reopens rather than advances. Also overturn if a locked
  domain has been materially rewritten without a decision entry naming the change, which would mean
  the lock is not functioning as a baseline.
- **Check:** `loopsStale >= 8`
- **Check covers:** only the runtime-liveness half, as a proxy — `loopsStale` counts loops without a
  recent artifact and will rise if the resume did not hold. It does **not** detect undocumented
  rewrites of a locked domain; that half is prose and needs a human read of `git log` against these
  seven areas.
