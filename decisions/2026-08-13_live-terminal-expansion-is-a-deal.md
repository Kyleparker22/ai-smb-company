# Live is terminal — an expansion is a new deal, not a stage (2026-08-13)

**Decided by:** the Founder, after asking the right question: *"once a client expands they'd go back to
Live, correct? Should Expand live as a subset of Live?"*
**Locks:** pipeline ladder
**Related:** `decisions/2026-08-13_one-referral-rate-card.md` (the credit floor, decided the same day)

## The problem, visible in the data itself

The two exit conditions as they stood:

- **Live** → *"expansion trigger — next module scoped"*
- **Expand** → *"module scoped → **loops back to Demo and Proposal**"*

A stage you exit by going **backwards** is not a rung. The ladder contained a cycle, and three
things were quietly wrong because of it:

1. **The ghost pipeline** measures forward velocity through rungs. A deal passing Demo-and-Proposal
   twice — once as new business, once as an expansion — polluted the median time-in-rung by mixing
   two motions that have nothing to do with each other.
2. **Stage conversion** (built 2026-08-13 on reached-ever) double-counted any deal that looped.
3. **The mirror** required all seven buyer steps at both Live and Expand, when a re-sale to an
   existing client has a genuinely different buyer ladder — they cleared risk, story and authority
   the first time.

The clearest tell was in the money. Every "is this a paying client" read had to say
`["live","expand"]`, and getting that pairing wrong in one place had just caused a real
underpayment (the cockpit read $0 where the statement read $300). **A value that must always be
paired with another to mean anything is not a peer on the enum — it is a modifier.**

## The decision

**Live is terminal. An expansion is a NEW DEAL on the same company**, opened at Demo and Proposal
with `expansionOf` pointing at the deal it grows.

This is what the old exit condition already said out loud — *"loops back to Demo and Proposal"* —
so the fix is to model the thing as what it is rather than as a rung it has to escape.

Entering at **Demo and Proposal**, not Discovery: the discovery already happened. What remains is
scope, price and a walkthrough.

### What this buys

- The ladder is monotonic again, so ghost velocity, stage conversion and time-in-rung are clean.
- The client stays **Live** throughout. One answer to "are they a client", so commission, MRR,
  health and retention stop needing a pair.
- **Expansion becomes forecastable pipeline.** It appears on the board (badged `↗ expansion` so it
  never reads as new business), carries a win probability, and can be predicted against. As a
  stage it was a state you could not put a number on.
- Total client value = the sum of their live deals, which is the natural reading.

### What it cost

`dealOf(companyId)` returned the *first* deal and several places assumed one deal per company.
`dealOf` keeps its name and now returns the **primary** deal — a paying one if there is one, else
the furthest along the ladder, deterministic so two renders never disagree. Anything touching money
uses `dealsOf`/`liveDealsOf`/`mrrOfCo`, which **sum**.

Migration was free: at the time of the change no company had two deals and no deal was in `expand`,
so this builds the capability before it is needed rather than retrofitting live data.

## Both of these were caught by the change, and both were real money

- **`connector_statements.py` keyed live deals by `companyId` in a dict**, so a company with two
  live deals silently kept only the last one — under-reporting exactly the client a connector
  should earn most on. Now sums.
- **Referred MRR read only the primary deal.** A referred company running an OS *and* a live
  expansion would have paid commission on the OS alone. Verified: a $3,000 OS + $1,500 expansion
  now correctly bills $4,500 of referred MRR ($450 commission, not $300).

## Agent positions on the same day

Asked before deciding (their reads, from their own charters):

- **Charles** (Skok lineage — MRR/retention/expansion) arrived at this model independently and for
  a different reason: expansion is a *revenue* motion, and you cannot compute expansion MRR or NRR
  from a stage. He needs it on its own row with its own value. Two unrelated arguments landing on
  the same fix is the strongest signal in this decision.
- **Polo** (Ramanujam lineage — price as proxy for value) wants expansion priced as a new module at
  list, which a separate deal supports naturally and a stage did not.

## Consequences applied

- `crm/data.json` — `expand` removed from `stages`; Live's exit rewritten to say it is terminal and
  that a module is a new deal.
- `crm/index.html` — `dealsOf` / `liveDealsOf` / `mrrOfCo` / `isExpansion`; `dealOf` → primary;
  `PAYING_STAGES = ["live"]`; `inMotion` now includes expansion deals (they are real sales being
  worked); Clients groups by **company** and offers **+ Expansion**; board badge.
- `crm/ghost.py` — `LEGACY["expand"] = "live"` so historical board states replayed out of git fold
  forward instead of being priced against a rung that no longer exists; `CACHE_VERSION` 5 → 6.
- `mirror.py`, `calibration.py`, `adversarial.py`, `expansion.py`, `connector_ladder.py`,
  `connector_statements.py` — `expand` retired from every stage table.
- `crm/_README.md` — the ladder line rewritten.

## Open

- [ ] The mirror's `REQUIRES` still asks all seven buyer steps of an expansion deal. A re-sale
      should arguably require fewer — they have already cleared risk, story and authority once.
      Left as-is deliberately: guessing which steps carry over is exactly the kind of inference the
      mirror exists to refuse. Set it from the first real expansion.
- [ ] Charles: expansion MRR / NRR reporting now that the data supports it.

## Trip-wire

Revisit if:

- **A company reaches 4+ live deals** — the client card and the payout row are built to list them,
  not to summarize them, and both will get unreadable.
- **An expansion is ever lost** while the parent stays live — nothing currently models a
  *partially* churned client, and the closed-deal path assumes the company is gone.
- The first expansion actually closes — check that ghost velocity did not absorb the expansion's
  Demo-and-Proposal time into the new-business median. The badge exists; the math does not yet
  segment on it.
