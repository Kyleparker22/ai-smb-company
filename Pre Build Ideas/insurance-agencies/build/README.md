# Renewal OS — build 4 of 10

Pre-built vertical AI OS for independent P&C insurance agencies.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py                      # 4,200 policies, 2,800 households, 24 months
python3 test_renewal_os.py           # 61 assertions, every one a refusal
```

Launch name **`prebuild-renewal-os`** (port 8824, 127.0.0.1 only).

## What it is

"Hollinger & Kwan Insurance" — 11 people, four producers, eight invented carriers, 4,200 policies
across 2,800 households, ~58% mono-line. Five modules: **renewal watchtower**, **remarket packet**,
**COI desk**, **mono-line finder**, **claims touch**.

## Three prohibitions, as rules

**No coverage advice, no quoting, no binding, no statutory notices.** All four are declared in the
matrix at **R0 / never promotes** — a buyer can read the prohibition rather than trust it, and a
test proves no streak promotes them. Every material client draft opens `[FOR PRODUCER REVIEW —
<name>]`.

**A price comparison cannot render without its coverage diff.** `comparison_sheet()` returns
`renderable: False` when the quote comes back without a coverage schedule, and `present_comparison`
never leaves the gate. The demo shows both halves: the same policy, quoted 14% cheaper, refused
with no schedule — then shown with one, where the saving turns out to be a doubled deductible, ACV
roof settlement and water backup dropped. That is the trade a price-only comparison hides.

**A non-standard certificate is never auto-issued.** Additional insured, waiver of subrogation,
primary/non-contributory, notice endorsements, per-project aggregate, completed operations, blanket
— all hard stops. So is a *first* certificate for a holder (nothing to match against) and
*unreadable* attached language, because unreadable is not the same as routine. Eval: recall on
`non_standard` reported alone, 1.0, zero missed.

## Other refusals

- **A coverage change with a flat premium is still material.** That is the one clients discover at
  claim time.
- **An unknowable change is material by default** — no expiring premium on file means a human owns
  it, not a guess.
- **A carrier that states no reason yields `unknown`**, and the draft says "we are asking them
  before we call you."
- **A producer under ten renewals is not rated** — the retention number would be noise.
- **The cross-sell scorer physically reads six permitted factors** (lines held, tenure, prior
  declines, recorded life events, claim-free years, premium). A test poisons a household with age,
  gender, ZIP, language, marital status and credit band and asserts the score does not move. Missing
  data is stated in the reasons, never defaulted.
- **The persistency multiplier is on the face of the ROI line**, marked COMPOUNDS, with "set it to 1
  for the one-year answer". It is the number that makes this offering look large and the easiest
  place to lie.
- **No silent truncation** — the queue says "showing the 80 closest of 487".

## 10-minute demo

1. **The book** — retention 86.9% overall and by producer, $4.1M premium at risk in 90 days,
   mono-line share, COI turnaround.
2. **Renewals** — the material queue. Find the home policy at **+23%** where the deductible doubled
   and roof settlement dropped to ACV, with the cause named and the producer's call already drafted.
3. Hit **Remarket** on it — see the refused comparison, then the one with its schedule.
4. **Certificates** — 18 routine issued at R2, the additional-insured/primary-non-contributory
   request stopped with its language quoted.
5. **Mono-line** — the permitted-factor list, then the ranked households with per-household reasons.
6. **What it's worth** — four lines, persistency visible, certificate time kept out of the revenue
   subtotal.
7. **Trust & audit** — four R0 never-promote rows in the matrix, the eval, the append-only log.

## What this does not do yet

- **No integrations and no carrier-portal access.** AMS360/Epic/EZLynx, carrier download, email and
  e-signature are adapter seams. A real credentialed portal connection needs a written compliance
  assessment first — the prototype does not attempt one.
- **Carriers, rules and coverage schedules are invented.**
- **No rating, no forms, no policy documents.** The build reads a diff; it does not produce a policy.
- **Claims touch is a draft for a producer**, not a claims service.
- **Nothing is sent.**
