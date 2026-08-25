# 2026-08-13 — Connector Console v3: six builds that point yourco's own instrumentation at the connector, and tiers move to MRR

**Decided by:** the Founder, from the referral-platform competitive scan (same session).
**Locks:** connector console scope · commission tier basis
**Builds on:** `decisions/2026-08-11_connector-program-v2.md` (modes + bounty + R1) ·
`decisions/2026-08-13_one-referral-rate-card.md` (one rate card).

## The decision

Six things get built, and the commission tier basis changes.

### 1. Commission tiers band on **live referred MRR**, not active client count

the Founder asked the question directly: count, MRR, a combination, or something else. **MRR**, and the
thresholds are chosen to be backward-compatible at the Core floor.

| Tier | Live referred MRR | Rate | ≈ Core clients |
|---|---|---|---|
| Referrer | $0 – 14,999 | 10% | up to 5 |
| Senior | $15,000 – 29,999 | 12.5% | 5 – 10 |
| Partner | $30,000+ | 15% | 10+ |

*(Upper band set to $30,000 by the Founder on 2026-08-13, revised from an initially-drafted $33,000.)*

**Why count was wrong.** Count-banding is only sane when deal sizes are tight, and yourco's run
$3k → $10k+ — a 3.3× spread. Under the old bands a connector with **3 × $10,000 clients ($30k of
referred revenue) earned 10%**, while one with **6 × $1,000 clients ($6k) earned 12.5%**. The bigger
producer paid the lower rate, and the program quietly rewarded referring the *smallest* businesses a
connector could find. Nobody chose that — it is the identical failure mode
`2026-08-13_one-referral-rate-card.md` fixed for the $100 client credit: a threshold that stopped
tracking the thing it was derived from.

**Why these thresholds and not others.** Round Core-floor multiples: $15,000 is 5 × $3,000 and
$30,000 is 10 ×.

**⚠️ Correction, recorded rather than quietly fixed.** An earlier draft of this decision claimed the
MRR bands were backward-compatible with the count rule — *"an all-Core book crosses at exactly the
same places."* **That was wrong.** The count thresholds were **6** and **11** actives, which at the
Core floor is **$18,000 and $33,000**. The bands as set are one client looser at each end: an
all-Core book reaches 12.5% at 5 clients instead of 6, and (after the Founder's $30,000 revision) 15% at 10
instead of 11. So this **is** a small comp change in the connector's favour, not a like-for-like
restatement, and no surface may describe it as one. It is still worth making for the reason that has
not changed: the count rule paid the *smaller* producer more, and the MRR rule does not.

**Rejected: a combination** (e.g. count *and* MRR, or count with an MRR floor). It doubles the number
of things a connector has to track to predict their own rate, and the failure it guards against —
one enormous client carrying a tier — is not a failure: a connector who brings a single $33k client
has produced more than one who brings eleven $3k clients, and should earn more.

**Implementation:** `connector_statements._tier()` is asked about `tier_input()`, one function, so no
surface can band on a different number than the statement does. `basis: "count"` in
`meta.referralTiers` keeps the legacy rule for any data scored under it — the basis never changes
silently underneath a book.

### 2–7. The six builds

| # | What | Where |
|---|---|---|
| 2 | **Ghost, pointed at the connector** — what their book would be worth if yourco had moved every referral at yourco's *own* median pace | `crm/connector_ghost.py` |
| 3 | **The connector approves yourco's first message** to their contact, and earns their way off the gate (A0 → A1 → A2) | `crm/connector_approvals.py` |
| 4 | **Text/email intake** — submit a contact without opening the console | `runtime/connector_intake.py` |
| 5 | **Calibration** — the connector's own judgment, measured, and used to order yourco's queue | `crm/connector_calibration.py` |
| 6 | **Referral escrow** — yourco posts a bond against its own conduct, payable to the connector | `crm/connector_escrow.py` |
| 7 | **Own-OS grant at 5+ live clients** — the connector's business runs on the product | `crm/connector_perks.py` |

## Why these six

Three of them (2, 6, and the honesty rules throughout) do the same unusual thing: **they instrument
yourco's behaviour and show it to the counterparty.** Every referral dashboard in the category exists
to grade the partner; these grade us. That is only possible because yourco already has the machinery —
`ghost.py` reconstructs board history and derives medians with a refusal rule, the attribution log is
append-only, and the SLA that promises 24–48h verification is the same timestamp that proves when we
missed it.

Two of them (3 and 5) are the **Autonomy Matrix and the calibration market pointed outward at a
human**. A connector earns their way off an approval gate on evidence exactly as an agent does, and
their forecasting accuracy is measured the same way the Founder's is. Nobody else in this category can do
this because nobody else has an approval layer or an eval layer to hand over.

One (4) is a correction: the competitive scan found that **partner portals are the thing partners
don't use**, and activation is the only number that matters at n=0 connectors. The console stays as
the ledger of record; it stops being the only door.

One (7) is compensation as product adoption. At 5 live referred clients a connector has produced at
least $15,000/mo; an OS for their own business costs less than that, and it converts every future
introduction from a pitch into testimony.

## The honesty rules, because they are the design

Each build **refuses rather than guesses**, and each refusal is rendered as itself — never as zero,
because "we won't say" and "nothing" mean opposite things and the flattering one is the wrong default.

- **Ghost** states no book-level figure below 3 referrals on the board ("one or two is an anecdote,
  not a pattern"), states none where yourco's own history has not measured the stages a referral
  crossed, and states none at all if the board history is unreadable. It inherits `ghost.py`'s
  `MIN_OBS` refusal rather than re-deriving a median. It reports yourco being **fast** with the same
  prominence as slow.
- **Calibration** produces **no score** below 5 resolved predictions, and a connector cannot revise a
  call after the fact.
- **Escrow** pays for yourco's *conduct*, never for a referral that simply didn't close — and a
  contact that reached a booked call cannot be counted as "never contacted" regardless of the log.
- **Approvals** reset to A0 on any complaint; a connector can put themselves back on the gate
  permanently and that is always honoured over the earned rung.
- **Perks** separates **earned** from **provisioned**, so the gap is a visible commitment rather than
  a quiet backlog — and refuses to start a grant for a book that hasn't earned it.
- **Intake** takes identity from the channel and never from the message body, and **never invents
  provenance** — an unparseable message becomes a question, not a submission.

## What this obligates

1. **Nothing here is payable.** `ESCROW_PAYABLE` is False and `GRANT_ACTIVE` is False, joining
   `BOUNTY_PAYABLE`. Everything accrues and renders as accrued; no cash moves until launch + counsel.
2. **The escrow is a new payment class and counsel has not seen it.** It pays on *yourco's* failure
   rather than on any connector act, which is a different animal from the bounty — plausibly cleaner
   under §A (it cannot be earned by recruiting or by volume), but it is untested. Amount is
   `[[the Founder to confirm]]`, proposed at one bounty step.
3. **SMS has no transport.** The parser is channel-agnostic and the email path is wired; SMS needs a
   number and keys (`.claude/skills/wire-credentialed-connector/`). It says so rather than pretending.
4. **The own-OS grant is a real cost.** yourco absorbs the tokens and the build time for a non-paying
   system. Justified by the $15,000/mo floor that earns it — Charles should model it once a grant is
   actually close, not before.
5. **`STICKY_ONCE_EARNED` is a policy call, not a technical one.** A grant does not lapse if the book
   dips, because switching off a person's live business operations is a worse failure than the one it
   corrects. `[[the Founder to confirm]]`.
6. **Earned-depth is still NOT built.** The eXp-style "unlock override depth by producing" idea from
   the same scan was presented and **not selected**; override depth remains uncapped and payable at
   R1, and counsel checklist item **4c** is unchanged by this decision.

## Reversibility

**High on 4, 5, 6; moderate on 2, 3; low on 1 and 7.** The intake is a doorway that can be closed. The
calibration and escrow are ledgers that can stop being rendered. The ghost and the approval gate change
what a connector believes yourco owes them, which is harder to withdraw than to grant. The tier basis
is one config flag but re-banding a live book is a comp change people feel. The own-OS grant is the
least reversible thing on this page: you cannot un-give somebody a system their business now runs on,
which is exactly why it sits behind 5 live clients.

## Trip-wire
- **Review:** 2026-11-13
- **Overturn if:** the ghost read is still refusing to state a figure after a full quarter of real
  connector referrals (the medians never measure, so the section only ever apologises); **or** the
  approval gate produces a materially worse first-touch than yourco's own copy (connectors editing
  most drafts toward something that converts less); **or** the intake's parser is wrong often enough
  that connectors go back to the console anyway.
- **Check:** `activeConnectors >= 3 and signedClients >= 1`
- **Check covers:** only that real connectors and a real client exist, which is when any of these can
  be measured at all. It covers **none** of the overturn conditions themselves — refusal rates,
  edit rates and parser accuracy are not instrumented, and instrumenting them is the first follow-up
  once connector #1 is live.
