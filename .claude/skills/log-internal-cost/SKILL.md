---
name: log-internal-cost
description: Log token + tool spend for work on yourco ITSELF to finance/token_spend.md — the OS, the site, offerings, prototypes, agents, the app. Invoke at the END of any session that built or materially updated something internal. The client-side twin is log-build-cost; this is everything that is not a client. Owner of the roll-up - Charles.
---

# log-internal-cost

## Canonical doc
`finance/token_spend.md` (the ledger) + CLAUDE.md §"Token economics". `log-build-cost` handles
client engagements and explicitly hands internal spend here — this skill is the other half of
that sentence, which existed as an instruction with no procedure behind it.

## Why this exists (the gap it was written to close)
`Pre Build Ideas/` is **577 files and 108 commits, built entirely in August 2026** — almost
certainly the largest single build in the company's history. It has **zero rows** in
`finance/token_spend.md` and no `cost.md` anywhere in it. Nobody decided not to track it; there
was simply no procedure, so it did not happen.

That matters beyond bookkeeping. yourco is pre-revenue and absorbing every dollar of model spend.
The one thing the ledger can prove — *what did we spend, on what, and did it move anything?* — is
exactly the question a partner, a lender or a future the Founder will ask. An untracked build is
speculative inventory bought with real money and recorded nowhere.

## When
1. **End of an internal build/update session** — the OS, HQ, the CRM, the app, the site,
   `offerings/`, `Pre Build Ideas/`, agents, runtime. If you shipped a commit today, this applies.
2. **A tool cost lands that is not attributable to a client** — Higgsfield credits, an API top-up,
   a subscription renewal, a domain.
3. **A large one-off** — a benchmark sweep, a model bake-off, a mass regeneration. Log it the day
   it happens; these are the ones that vanish.
4. **Charles's monthly close** (`finance-close`) rolls the ledger up. This skill feeds it.

## Three categories that get skipped, and shouldn't (the Founder, 2026-08-23)

**Negative results.** A benchmark that picked no winner, a prototype that got rejected, an
approach abandoned after two days. That spend bought *information* — usually the most expensive
kind, because you only learn it by paying for it. Log it, and where a `rejections/` entry exists,
name it in the description so the cost sits next to the decision it justified. A rejections entry
with no price on it understates how much the "no" was worth.

**Pre-signature client work.** Already covered as the `discovery` phase in `log-build-cost`, and
worth saying out loud because the instinct is to wait until someone signs. It is **CAC evidence
whether or not the deal closes** — arguably more useful when it doesn't, because that is the
number Polo needs to price against. Sample Client has 26 rows and is still unsigned; that is the
pattern working.

**Tool credits.** Higgsfield, API top-ups, ElevenLabs, Descript, Vapi, domains. Individually too
small to feel worth a row — collectively **most of the recurring burn**, and the category that
caused a real outage: the org ran out of API credits on 2026-07-30 and the runtime went dark for
twelve days before anyone connected the two. Log the renewal the day the receipt lands.

The through-line: the spend that goes unlogged is never the big obvious build. It is the spend
that doesn't feel like a project — a failed experiment, an unsigned prospect, a $14 renewal.

**Not this skill:** anything under `clients/<name>/` → `log-build-cost`. Headless loop runs are
already captured automatically in `loops/_agentops/runs.jsonl` from `claude -p --output-format
json` — do not double-count them here; reference the journal instead.

## Steps
1. Open `finance/token_spend.md` and append ONE row per spend event to the ledger table:
   `| month | engagement | model | description | est_cost | date | source |`
2. Fill `engagement` with the internal area **and mark it internal**, matching existing rows:
   `property-os (internal offering)`, `runtime (VPS loops)`, `atlas (internal)`,
   `app (internal platform)`, `pre-build-ideas (internal inventory)`.
3. `description` says **what was built**, not what was spent on. A row reading "Cowork session"
   is worthless in three months; "71 industry prototypes, builds 62–71, 1,180 assertions" is not.
4. Get the number honestly, and say in `source` how you got it:
   - `metered` — the Anthropic Admin cost API (`/api/anthropic-cost`), or a tool invoice
   - `est.` — a session self-report (`/cost`) or a stated rough estimate
   - An honest `est.` beats a fake `metered`. Never invent precision: write `~$40`, not `$41.87`.
   - If you genuinely cannot get a number, write `TBD` **and say what would produce one**. A `TBD`
     with a route to an answer is a real record; a blank is a hole.
5. Commit with `runtime/commit-scoped.sh` scoped to `finance/token_spend.md`, or fold it into the
   session's own scoped commit.

## Gotchas
- **Cowork session tokens are not auto-attributable.** The self-report at session end IS the
  capture mechanism. That is the whole reason this skill exists — do not skip it because the
  number is rough.
- **Units.** The Admin API's `cost_report` returns **cents**. This was published once as dollars
  and was 100× high (caught by the Founder, 2026-07-06). Divide before you write.
- **Do not double-count the runtime.** Loop spend is metered org-wide *and* journaled per run. One
  row per month for `runtime (VPS loops)` citing the meter, not a row per loop.
- **Internal is not free.** The instinct is to log client work carefully and wave internal work
  through because "it is just us." Internal work is where the money has actually gone: pre-revenue,
  n=0 clients, and the largest build to date is internal.
- **A negative result is worth a row.** A benchmark that picked no winner, a prototype that got
  rejected — that spend bought information. Log it, and where it fits, link the `rejections/` entry.

## The machine backstop
`runtime/cost_reconcile.py` compares metered API spend against what the ledger explains, month by
month, and `runtime/consistency-check.py` fails when the gap exceeds $15 or when a month has real
commits and zero rows. It reconciles **API to API only** — Cowork sessions are $0 marginal on the
Max plan and never reach the meter, so including them would manufacture a discrepancy. Run it any
time: `python3 runtime/cost_reconcile.py`.

⚠️ Cowork being $0 marginal is a billing fact, not permission to skip the row. The ledger's real
job is recording **where the effort went**, and zero-cost is not zero-value.

## Backfill
`Pre Build Ideas/` (Aug 2026) and this workspace's own August sessions are missing. They will not
reconstruct exactly. Add one honest `est.` row per wave with the commit range as evidence, rather
than leaving the largest build in the company's history absent from its finances.
