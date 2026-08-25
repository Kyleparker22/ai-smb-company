# 2026-08-07 — Phantom shares replace real equity in the connector incentive track

## Decision
The top-connector incentive becomes **phantom shares** (contractual units whose value tracks yourco
equity, settled in cash on a liquidity event) rather than **actual equity grants**. Amends
`decisions/2026-06-30_rep-equity-track.md` — the bands, the trailing-12-month net-retained revenue
measure, the one-grant-per-connector rule, the vesting/clawback conditions, and the program cap all
carry over unchanged; only the *instrument* changes. the Founder's call, 2026-08-07.

Additionally: **progress toward it is displayed in the Connector Console** — but dark by default and
per-connector enabled by the Founder (see §The display risk).

## Why the instrument change is an improvement
Issuing real stock to non-employee contractors was the heaviest part of the original design. Phantom
units avoid most of it:
- **No cap table dilution and no stock issuance** to non-employees — no new shareholders, no voting, no
  information rights, no signature blocks on future financings, no minority-holder complications at an
  exit.
- **Simpler tax path** — settled as ordinary compensation income when paid, rather than the 409A
  valuation / early-exercise / QSBS-adjacent complexity of granting actual shares to contractors.
- **Cleanly capped** — phantom units can be defined as a share of exit proceeds up to the program cap,
  which is easier to model and to close than committing a percentage of the company itself.
- **Same felt upside for the connector** — "you own a piece of what you're building" is preserved
  economically; what's removed is legal machinery neither side wanted.

**It does not remove the gate.** Phantom equity for non-employees is still deferred compensation and
may still be a security depending on structure. The hard stop from the original decision stands: **not
offered, not promised, not marketed until counsel structures it.**

## The display risk (the part that needed a design answer)
the Founder asked for the console to show *how you earn it and how close you are*. A progress bar toward
equity is materially different from a 1:1 conversation — it can read as an **offer** and as an
**earnings claim**, which is exactly what the original decision avoided by keeping the track verbal and
unmarketed. Design that lets the Founder have it without that exposure:
1. **Dark by default.** The section renders only for connectors the Founder has explicitly enabled
   (`meta.phantomTrack` — per-connector, the Founder-set, never computed and never auto-enabled).
2. **No implied promise in the copy.** It states the discretionary nature, that no units exist until a
   definitive plan document is executed, and that nothing here is a grant, an offer, or a guarantee.
3. **Progress is factual, not projective.** It shows their measured trailing-12-month net-retained
   referred revenue against the band thresholds — real numbers they can already see elsewhere in their
   ledger — never a projected payout, valuation, or dollar figure for the units.
4. **Nothing publishes.** The track stays absent from the site, the packet, and all recruiting copy —
   unchanged from the original decision.

## Counsel questions (added to the checklist)
- Is a phantom-unit plan for **non-employee contractors** a security in `[[FL]]` and target states, and
  does it change the §A pyramid analysis (is it "compensation tied to real client revenue"? — it is,
  same as the escalator, but counsel should confirm the instrument doesn't alter that)?
- 409A / deferred-compensation treatment and withholding mechanics at settlement.
- Does **displaying measured progress** to an enabled connector constitute an offer, or an earnings
  claim requiring substantiation, even with the disclaimers above?
- Does the phantom plan need its own definitive document, or can it live as an addendum to the
  Connector Agreement?

## Reversibility
High while unbuilt and unpromised: no units exist, nothing is granted, the console section is dark for
every connector until the Founder enables one. If counsel prefers the original instrument, the bands and
mechanics are unchanged — only the settlement mechanic flips back.
