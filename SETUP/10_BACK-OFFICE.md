# 10 — Back office

> **Build step 10.** Nothing here is done yet. Where this page shows a filled-in value, that is
> the source company's — replace it with yours.

## Money

- `finance/token_spend.md` — model spend, reconciled against metered Anthropic billing by a
  consistency invariant that warns on the gap.
- `clients/<client>/cost.md` — per-engagement, appended via `.claude/skills/log-build-cost/`.
  **Charles rolls both up** at the weekly pulse (capture-gap check) and the monthly close (phase
  totals, margin per client).
- `finance/readouts/` — the monthly close.
- `finance/yourco-financial-model.xlsx` — 5-year model. An **assumption-stated model, not a forecast**,
  and the plan says so in those words.

## Compliance and counsel

`processes/counsel-gates.md` is **the only place gate state lives** (Ray owns it). Eighteen items as of
2026-08-25. The ones that matter most:

- **#14** — the operating agreement at 50/35/15, with its D10–D12 blockers.
- **4c** (connector program) — bounty on non-revenue events + recruit-at-R1 + uncapped depth. **No
  connector may be recruited until §A/§B clear.**
- **#17** — the data-handling posture. yourco is Claude-only, runs client work through its own VPS, and
  **has no written answer** on training exclusions, retention, or where client data sits. The first
  sophisticated buyer will ask. `agents/rafi/data-ownership-posture.md` states the question and the
  five things to verify at source — deliberately without the answers, because asserting a provider's
  terms from memory is a trust event, not a rounding error.
- **#18** — Remotion licensing, conditional; nothing uses it today.

`processes/launch-gate.md` is the master gate holding every external surface. ⚠️ As of 2026-08-25 it
has **not been updated in 51 days** and four fields still read "the Founder to fill." An unmaintained tracker
reads exactly like a maintained one, which is why the invariant nags.

## Standing obligations — the three things with a date and a cost

Watched by `runtime/consistency-check.py`. None of them files anything; they refuse to let a date or a
state pass unnoticed.

| Obligation | What is watched | State on 2026-08-25 |
|---|---|---|
| **FL annual report** | due 1 Jan – 1 May yearly, $138.75, **automatic $400 penalty** past 1 May | silent until 1 Jan 2027; first report due **1 May 2027** |
| **Insurance** | *not a renewal date — there is no policy.* Fires when a client reaches signed/live while nothing is bound | unbound, no live client, so quiet |
| **10DLC** | stalls, not renewals: warns when the newest dated status is >30 days old and not complete | ⚠️ **stalled 70 days** (newest status 2026-06-16, blocked on Privacy Policy + T&C URLs) |

⚠️ **The insurance one is the sharp one.** `processes/contracts/engagement-agreement.md` §13 already
represents that yourco "will maintain" GL + E&O + Cyber coverage, softened only by a bracketed
`[[Once obtained]]`. **Signing a client on that language with no policy behind it is the exposure** —
which is why the trigger is a client going live, not a calendar date. `insurance-plan.md` says the
same thing in its own words: coverage must be in force before the first client goes live.

⚠️ **A note on how these checks read a document.** The 10DLC check reads completion **only** from the
newest dated `Status (...)` line, never from prose elsewhere in the file. The first version searched
the whole document, matched `✅ 10DLC brand approved` out of a *future* checklist ("you're cleared
when these are true"), and reported 10DLC complete while it was blocked. **A target state read as a
current state is the worst failure one of these can have** — it is silent, and it says "safe."

## Insurance, contracts, people

- `finance/legal-docs/insurance-plan.md`
- `processes/contracts/` — engagement agreement, proposal/SOW. **Counsel-gated; check the gate tracker
  before using one.**
- `processes/payments.md`, `processes/10dlc-sending-infra-setup.md` — messaging infrastructure, which
  has its own registration requirements and lead times.

## The rhythm

`05_operating_rhythm.md` — the cockpit manual: the daily and weekly rhythm, what only the Founder does, and
the 10-minute morning. `daily-logs/` holds the per-session handoff note; write one at the end of any
working session (`.claude/skills/daily-log/`).

## Done when

**your first month is closed: spend logged, and a counsel-gate tracker with at least one row.**

If you cannot point at that, the step is not finished — do not move on.
