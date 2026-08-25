# Property OS — an operated AI OS for residential property management

**Status: built and runnable, zero clients, zero real data.** Everything below runs;
nothing below has been sold. The portfolio is synthetic.

An operated multi-agent OS for a manager holding **20–300+ units**, now covering all
three of the job's loops: **maintenance** (intake → triage → dispatch → proof →
invoice), **leasing/turnover** (notice → make-ready → measured vacancy), and
**money** (rent → delinquency ladder → trust ledger → statements → drafted
disbursements) — plus the **Growth module** (owner-prospect pipeline, drafted
outreach, no send rail). Ten agents run it; everything a human still decides
collects in one queue that says *why* a human is required.

**The money line, stated once and everywhere:** this software ACCOUNTS for money
and PREPARES movement. It never MOVES money. Executing a transfer is permanently
R0 — a human does it at the bank and records that they did, with a bank reference.
The trust ledger is bookkeeping software, not a compliance program: state
trust-account rules bind the operator, and a counsel/CPA review gates any use with
real funds.

Fits the house model: yourco **builds and runs it**, owns the reliability / eval /
approval layer, and the client gets an outcome. Three form factors in one engagement
— an embedded AI surface (the resident app), headless automation (the agent crew),
and a digital employee (the dispatcher).

---

## Run it

```bash
cd Pre Build Ideas/property-management/build
python3 seed.py            # 6 properties · 220 units · 18 months of history
python3 server.py          # http://127.0.0.1:8813
```

Or, per house rules, use the registered launch name rather than guessing a port:
`preview_start {name: "property-os"}` — it is in `.claude/launch.json` on **:8813**.

```bash
python3 agents.py --all       # one sweep of every agent
python3 agents.py --explain   # what each action may do unattended, and why
python3 test_propertyos.py    # 272 domain assertions
python3 test_journeys.py      # 213 journey assertions (boots its own server)
python3 bench_models.py       # triage accuracy vs the deterministic floor
python3 seed.py --units 300   # top of the ICP
```

**Stdlib only.** The apps have no build step and no dependencies. `pip install
anthropic` is optional — it upgrades triage and drafting; nothing breaks without it
(see *The floor always runs*).

| Surface | URL | What it is |
|---|---|---|
| Launcher | `/` | Three doors + the live store contents |
| Resident | `/tenant.html` | Mobile PWA — file, track, rate, reopen |
| Manager | `/staff.html` | Board · approvals · leases · vendors · agents |
| Owner | `/owner.html` | Open requests, resolution time, 60-day lease tracker, referral hook |
| Pitch | `/pitch?t=<token>` | White-label performance one-pager (token from console → Leads) |
| Prospects | `/inquire` | Public listings + FIFO leasing-inquiry intake |
| Growth | `/growth` | The owner-prospect pipeline — drafts wait, humans send |

---

## What was asked for, and where it is

| Requirement | Where |
|---|---|
| Tenant submits a request with a photo, mobile | `/tenant.html` — `<input capture="environment">`, installable PWA |
| Staff assign a vendor | Staff board → drawer → ranked bench with the reasons for the ranking |
| Track `submitted → assigned → in progress → resolved` | The literal four-state tracker, everywhere. Extra nuance rides on `resolution_kind`, never on new statuses |
| Owner dashboard: open requests + avg resolution time | `/owner.html`, the two largest numbers on the page |
| Lease tracker flagging expirations within 60 days | Owner and staff, ranked by non-renewal risk |
| AI + automation throughout, 90%+ | Seven agents; the **measured** figure is ~70% and the page says so — see *The number we won't inflate* |
| One or more AI agents running it | Seven, each with an earned autonomy rung |

---

## The ten agents

| Agent | Owns | Highest rung it holds |
|---|---|---|
| **triage** | Diagnosis, priority, parts list, self-fix deflection | R3 |
| **dispatch** | Vendor selection, SLA watchdog, escalation, spend | R2 |
| **concierge** | Resident comms, scheduling, the 48-hour check-back | R2 |
| **steward** | Component ledger, capital arithmetic, prevention | R0 — proposes only |
| **retention** | Renewal risk, lease expiry, offer drafts, silent units | R1 |
| **ledger** | Owner reporting and the counterfactual | R2 |
| **collections** | Rent charges, the delinquency ladder, referral packets | R3 for charges — and the ladder DE-automates as it escalates: reminder R2 → notice R1 → plan R1 → referral R0 |
| **scout** (Growth) | Referral import, prospect briefs, the cadence nag | R3 for import; briefs R2 — and the nag targets the HUMAN, never the prospect |
| **scribe** (Growth) | First-touch/follow-up/referrer drafts, proposal shells | R1 for every draft, R0 for proposals — and there is NO send action at any rung |
| **sentinel** | Fair-housing + legal screen on everything outbound; vendor compliance | R3, and it can **veto** — growth drafts included |

Rungs are the house standard: **R0** propose · **R1** approval gate · **R2** act and
notify · **R3** act silently. Full matrix with a stated reason per action:
`agents.py --explain`, or the Agents tab.

**Three never move.** `legal_notice`, `capital_recommendation`, and `execute_payment` are permanently R0 —
not because a model can't draft them, but because serving an entry notice, committing an owner's capital, and moving other people's money are not an agent's decisions — and no eval streak ever promotes them.

**One moves fast by design: the emergency spend authority.** A P1 is a
habitability failure, and its clock outranks the approval queue — the demo board
proved the need when a P1 lock-out sat breached for five days "awaiting owner
approval" over a $412 quote. Each owner now carries two instruments: a
**standing per-job limit** (routine delegation) and an **emergency authority**
(how far the manager goes *without asking* while a P1 clock runs). Under the
authority: the spend commits at R2, the owner's notice goes out the same moment
— the notice IS the control — and a price-anomalous invoice becomes a post-hoc
review rather than a reason to leave a resident without heat. Fix first, argue
about the price afterwards. Above the authority it drops to R1 like everything
else, because "emergency" is a reason to move fast, not a blank cheque.

---

## Six things here that competitors don't do

Checked against AppFolio, Buildium, Propertyware, Latchel, TenantCloud as of the
2026 feature sets. "Nobody does this" is a claim about *published product surface*,
not about what someone has prototyped.

**1 · The unit remembers itself.** A request for "no hot water in 4B" arrives
carrying the heater's make, model, install date, every prior repair and who did it.
The vendor is told *what to bring*. First-time-fix rate is the entire economics of
maintenance, and it is decided before anyone gets in a truck. Competing products
store this data; none assemble it into the dispatch.

**2 · Non-renewal risk from maintenance telemetry.** Turnover is the largest
controllable line in the P&L — the seeded portfolio carries **$173k of exposure in a
60-day window**. The signal that predicts a move-out is sitting in the ticket history
months before the notice: SLA breaches, reopened tickets, low repair ratings, volume.
Every input is a recorded event and the drivers are returned with the score, so the
manager acts on the cause. Existing products score nothing, or score a survey nobody
answered.

**3 · Guided deflection with an escape hatch.** Photo-triage decides whether a real,
safe self-fix exists, and offers it as *"90 seconds that might save you a day"* —
never as a barrier, always with a one-tap "didn't work, send someone" that keeps the
original ticket. Latchel does human triage; nobody does photo-triage plus a vetted
card at intake. In the seeded portfolio: **40 dispatches avoided, ~$7.5k**.

**4 · Vendor assignment as a market.** Five earned signals — first-time-fix 35%,
SLA 25%, resident rating 25%, response speed 15% — with weights stated on the page.
Price is deliberately excluded: the re-dispatch costs more than the invoice. Under
five resolved jobs a vendor is **unrated**, never a score built on three data points.
Quote anomalies are flagged against *this portfolio's* median for that job class, not
a national benchmark that local labour rates make meaningless.

**5 · Component-level capital economics.** Every repair writes to an asset ledger.
When repair spend passes 55% of replacement cost, or the thing is past its service
life with a repair history, it surfaces with the arithmetic shown: *"$840 of repairs
on a $1,450 heater that is 3 years past service life; the next failure is a 2am flood
claim."* That is what gets capital approved. Small-portfolio software tracks assets;
none run the repair-vs-replace math.

**6 · The owner report shows what didn't happen.** Owners fire managers because the
only thing they ever see is a bill. The report leads with avoided cost — deflected
dispatches valued at the portfolio's own median — and labels it plainly as an
avoided-cost estimate, not a realised saving.

Also here, smaller: the **48-hour check-back** that reopens the *original* ticket
when a resident says it isn't fixed (which keeps every downstream metric honest);
**silent-unit detection** (18+ months, no requests — surfaced as a question, never a
verdict); the **fair-housing screen** on every outbound draft; and **automatic
re-routing of open jobs off a vendor whose insurance lapses**.

---

## The floor always runs

Claude does the judgment: reading photos, refining triage, writing to residents,
drafting renewals. The **deterministic rules always run first and set a floor the
model may only raise, never lower.**

Pull the API key and every emergency still routes correctly. It stops reading photos
and starts writing worse prose — it does not stop working. A maintenance dispatcher
that fails when a model endpoint is slow is a liability, not a product.

The habitability floor is the sharp edge. Residents systematically understate: *"a bit
chilly, the heat doesn't seem to be coming on"* matches no obvious keyword. When the
resident answers that they can't use heat, water, power, or a toilet, **the rules
escalate to P1 on their answer, not on our keyword coverage.** A miss there is a
habitability failure, so it is not left to a model that might be unreachable.

---

## The number we won't inflate

The brief asked for 90%+ automation. The measured figure is **~70%**, and every
surface says 70%.

It is *counted* from the append-only event log — of the actions that move work
(triage, assign, escalate, schedule, resolve, message, approve), what share ran at R2
or R3 with no human. Tenant-originated events are **excluded by design**: counting a
resident filing a request as automation is exactly how vendors get to claim 95%.

The remaining 30% is not missing automation. It is the approval queue: spend above
the owner's limit, renewal pricing, capital, and anything legal. Those are decisions,
not throughput. **Automating them is the moat-killer, not the goal** — and the number
would only reach 90% by counting things that should never be counted.

`renewal_offer` and `approve_spend_over` are the natural R1→R2 promotions once
per-action eval evidence accumulates, on the house streak rule. That would land in the
low 80s. Ninety-plus on *pipeline-moving* actions is not a target worth hitting.

---

## What it refuses to say

Every read declines to produce a number its inputs can't support, and names what is
missing instead. The UI renders that string; it never renders a fake zero.

- Under 5 resolved requests → no average resolution time
- Under 5 resolved jobs → a vendor is **unrated**, with no composite score
- No maintenance history → renewal risk is **unscored**, and the text says that is not
  the same as low risk
- No install date → component verdict is `unknown`, never a guessed age
- Under 6 comparable jobs → no quote-anomaly flag
- Under 30 pipeline-moving actions → no automation percentage

`test_propertyos.py` pins each of these. **272 assertions, all passing.** They are not
coverage tests — each one pins a refusal, because refusals are what decay silently
when somebody tunes a threshold to make a demo look better.

## Two suites, because one of them was blind

`test_propertyos.py` (134) covers the **domain**: thresholds, rungs, refusals. It
passed clean through every bug found by clicking the running app, because none of
them lived in the domain.

`test_journeys.py` (149) boots a real server on a free port against a throwaway store
and drives the **HTTP API the way the browser does**. It exists because the bugs
lived in two places the domain suite cannot see:

- **the seam** — an agent wrote `turn_cost_estimate`, the UI read `turn_cost`. Both
  sides individually correct; every renewal card rendered "turnover costs —". So the
  suite declares, per approval kind, every field the card reads, *and* scans the card
  renderer for `p.<field>` reads that the contract doesn't list — the contract can't
  silently drift from the code.
- **the click** — "Still broken" set status to `assigned` unconditionally, stranding
  a failed self-fix with no vendor, then re-offering the same card. Only a button
  press reaches that transition, so the suite presses it.

It also asserts a kind of dead code the domain suite is structurally unable to
notice: **an approval kind the UI renders but the store never produces.** `spend` was
exactly that for the entire build — wired, rung-governed, rendered, and never once
generated, because every seeded owner-approval quote resolved before "now".

Both suites are mutation-checked: reintroduce either headline bug and the relevant
assertions fail by name.

```bash
python3 test_propertyos.py    # 134 — the domain
python3 test_journeys.py      # 149 — the journeys (boots its own server)
```

---

## The second build wave (2026-08-16): the other two loops

Eight features landed in one pass, each finishing something the data model
already supported:

- **The vendor became an actor.** A magic-link job card (`/job?t=…`) — no
  account, no app. Accept, schedule, start, complete **with proof**, invoice —
  and **decline** (2026-08-17): a decline is an availability answer,
  answered immediately — the job re-ranks with every decliner excluded, moves
  to the runner-up on a **fresh link** (the decliner's dies with the swap, as
  does the replaced vendor's on an SLA swap), and if nobody dispatchable
  remains it queues a `no_vendor` approval instead of going nowhere. Links are
  **minted at assignment by the live dispatcher** (previously only the seeder
  minted them — a real assignment had no artifact to send). The unit's memory
  (make/model/history) is on the card, the timeline attributes the work to
  `vendor:`, and the 48h check-back keeps the resident as the final judge of
  "fixed."
- **Proof closes the job — photos or video, required (2026-08-17).** Completing
  from the job card without media is refused, with the reason on the button:
  the 48h check-back asks the resident if it's fixed, and the proof protects
  the vendor when it does. Video up to 60MB (mp4/mov/webm), served back on the
  manager's drawer ("Vendor proof of completion") and the resident's resolved
  card ("What the crew finished"). Staff manual resolve via `/status` remains
  the no-proof override, and it carries the staffer's name.
- **The review ask (2026-08-17).** "Yes it's fixed" no longer auto-writes a 5:
  the check-back now opens a star picker (1–5) plus an optional line, because
  the rating feeds the vendor scorecard and has to be the resident's number,
  not the button's. Reviews are stamped (`rated_at`), surface on the vendor
  bench as **"What residents said"** — stars averaged by the scorecard, words
  kept verbatim, never summarized — and a vendor with no rated jobs shows no
  reviews rather than invented ones. The 48h check-back message carries the
  ask: "thirty seconds, and it genuinely decides who we send next time."
- **Resident availability windows (2026-08-17).** Asked at intake, only when it
  can matter: the moment entry is "only when I'm home" / "call me first," the
  form offers window chips (weekday mornings/afternoons/evenings, weekends) or
  exact times — and deliberately never asks an "anytime" resident (irrelevant)
  or an emergency (any urgency "yes" hides the block; entry is now). The
  windows ride everywhere the job goes: the vendor card shows "Resident can
  do:" as one-tap picks, the staff drawer shows them beside the entry notes.
  **The confirmation rule:** a vendor picking one of the resident's own FRESH
  windows confirms instantly (R2 — both parties already said yes; recording an
  agreement, not making a decision); anything else is a **proposal** the
  resident answers in-app — nothing books until they say yes, and their no
  kills it. Honest bounds: availability is a *statement, never standing
  consent* — timestamped, stale after 14 days; stale windows are shown for
  context but never auto-confirm and never read as permission to enter.
  Matching is verbatim-only by design ("fuzzy overlap is how somebody gets
  scheduled into a slot they never offered"). No calendar sync — that is a
  real-deployment connector. 
- **Invoice-vs-quote matching.** Within 10% of the approved quote: auto-match at
  R2. Beyond it, or with no quote: `invoice_review`, unpaid until a human
  settles it. The spend control finally sees the bill, not just the quote.
- **Turnover pipeline.** notice → move-out → inspection → make-ready (template
  tasks through the same vendor market) → ready → leased. Inspection queues the
  **deposit disposition draft (R0 — a legal document on a statutory clock)**.
  Three completed turns replace the 32-day vacancy *assumption* with a
  **measured median** — the basis line on every turn-cost figure says which one
  you are reading.
- **Preventive maintenance.** The steward schedules filter changes, water-heater
  flushes, and code-required detector checks off the component ledger — and PM
  orders are excluded from replace-now evidence, because a scheduled filter
  change is not a failure.
- **Rent + the delinquency ladder.** Charges post from the signed lease (R3).
  The ladder **de-automates as it escalates**: templated reminder (R2) → firm
  notice draft (R1) → payment plan proposal (R1) → referral packet (**R0,
  drafted for counsel, never sent alone**). Late-rent history now feeds the
  renewal-risk model — the strongest move-out predictor it lacked.
- **Trust ledger.** Double-entry, append-only, unbalanced transactions raise
  rather than store. The reconciliation invariant (trust cash = owner + deposit
  liabilities, to the cent) is **checked on every money view**, and a breach
  freezes disbursement drafting with a `TRUST ALERT` at the top of the queue.
- **Statements + drafted disbursements.** The statement is the ledger grouped by
  month — it cannot disagree with the books. The batch is a **draft**: executing
  it requires a `human:` actor and a bank reference (an agent is refused by
  name, a blank reference is refused by name, an overdraw is refused before it
  happens).
- **Auth + scheduler.** Access-code login → HMAC-signed session cookie, role
  enforcement when `PROPERTYOS_AUTH=1` (a resident asking for the staff view
  gets *their own* view; job links stay token-keyed). Sweeps run on a timer
  (`PROPERTYOS_SWEEP_MINUTES`, default 15) — safe precisely because idempotence
  is a pinned test. Demo access codes: `data/config.json` → `auth.demo_codes`
  (they exist only because every person in this store is synthetic).

Building it surfaced one deadlock worth recording: `store_lock()` was not
re-entrant at the *file-lock* layer — flock blocks against your own fd — so the
first vendor action ever taken hung the server. The lock now tracks depth;
found by the journey suite's timeout, not by reading.

---

## The Fable 5 review (what a fresh read found)

When the authoring model changed, the build got a full re-review instead of a
rewrite — 4,400 working lines with a green suite is not something to rebuild for
the author's sake. The review found four real defects, each proven before fixing:

1. **The "append-only" event log lost writes under concurrency.** `load` and
   `save` each took the lock, but the load→modify→save *cycle* did not — and the
   server is threaded. Measured: 8 threads appending 320 events stored **72**.
   The log the automation rate is counted from silently dropped 77% of writes
   under load. Fixed with `store_lock()` (thread lock + an fcntl file lock, so a
   cron sweep against a live server is also safe). Pinned: the same hammer must
   now store exactly 320.
2. **The sweep was not idempotent.** Three runs sent each owner three identical
   "monthly" reports. An hourly schedule would have meant 24 a day. The report
   now fires at most once per 6 days per owner; running the sweep twice changes
   nothing, which is what makes its schedule a free choice.
3. **The compliance screen blocked the owner report for containing the owner's
   own name.** "Nakamura **Family** Trust" tripped the protected-class list.
   Fair-housing and legal-notice blocks are about resident-facing messages; the
   screen is now scoped by audience, defaulting to the strictest (tenant) when
   unlabelled. The same words to a resident still block.
4. **An approved spend stayed "awaiting owner approval" on the board.** The
   stall flag outlived the approval that resolved it.

None of these were model-quality issues; all were found by reading the code
skeptically and exercising the paths the suites didn't. The runtime-model
analysis below was written before this review and stands unchanged.

---

## Would Fable 5 be better here?

Asked directly, and the answer is **no for this workload** — first argued from
the model's properties, and since 2026-08-16 **measured against a real key**:

| engine | priority | category | under-esc | p50 | p95 | $/MTok in/out |
|---|---|---|---|---|---|---|
| **rules floor** | **89%** | 95% | 0 | ~0s | ~0s | $0 |
| claude-haiku-4-5 | 89% | 89% | 0 | 3.8s | 7.5s | 1 / 5 |
| claude-sonnet-5 | 84% | **100%** | 0 | 9.3s | 13.1s | 3 / 15 |
| claude-opus-5 | 84% | 95% | 0 | 16.8s | 20.3s | 5 / 25 |
| claude-fable-5 | 84% | **100%** | 0 | 13.9s | 19.4s | 10 / 50 |

Readings, with the sample-size caveat stated up front (**n=19: every 5% is one
case** — this separates "clearly not worth it" from "maybe", it does not rank
Sonnet against Haiku):

- **No model under-escalated, and no model beat the floor on priority.** The
  escalate-only rule makes under-escalation structurally impossible for a
  model; each one's −5% is a single extra over-escalation (a truck roll, not a
  person waiting).
- **Fable 5 tied Sonnet 5 exactly on accuracy at 3.3× the price and ~1.5× the
  latency.** The pre-benchmark verdict is confirmed by measurement. One honest
  correction to it: Fable's measured p50 was ~14s, not minutes — the
  minutes-long-turn concern belongs to hard agentic work, not schema-bound
  classification. ~14s inside a synchronous P1 request is still disqualifying
  against a floor that answers in microseconds, and the 30-day-retention / ZDR
  constraint is unchanged, so the triage import-guard stands.
- **Opus 5 — the previous default — paid the worst latency for zero measured
  gain**: the same category accuracy as free keyword matching at p95 20s.
- **The one evidence-backed change:** triage now defaults to
  **claude-sonnet-5**, the cheapest model to reach 100% on category — and
  category is what drives the parts list, the single thing a model adds over
  the floor. concierge/retention defaults are untouched: nothing measured
  prose quality, and unmeasured defaults don't get changed here.
- **Not instrumented: token spend.** `ask()` doesn't record usage, so the
  benchmark cost is not stated anywhere — adding per-call usage capture is the
  obvious next improvement to `bench_models.py`.

A follow-up worth doing before real traffic: the P1 intake path currently waits
on the triage model call before dispatching. The floor has already set the
priority by then — dispatch could go out on the floor's answer and let the
model refine category/parts on the next sweep, taking the model out of the
resident's critical path entirely.

**But three of the reasons don't need a benchmark**, because they are properties
of the model rather than of its answers:

- **Latency disqualifies it from triage.** Fable 5's thinking cannot be disabled
  and a single turn can run for minutes. Triage runs *inside the HTTP request*
  when the priority is P1, so an emergency routes on intake rather than waiting
  for the next sweep. A resident tapping submit on a flooding bathroom cannot
  wait on that. `agents.py` refuses at import if it is selected for triage.
- **Cost lands on yourco, not the client.** yourco absorbs model spend by design.
  Fable 5 is $10/$50 against Opus 5's $5/$25 — double, on a schema-constrained
  classification that runs on every request. A high token bill is fine when it
  buys an outcome; here the outcome would not change.
- **Data retention is a live compliance question.** Fable 5 requires 30-day
  retention and is unavailable under ZDR. This store holds resident names, phone
  numbers, unit numbers and photographs of the inside of their homes. That is a
  counsel question, not a preference.

**What the workload actually is.** Three model calls: triage (short text + a
photo → a fixed JSON schema, every request, latency-critical), a two-sentence
resident status note, and a renewal letter that a human edits before sending.
None of that is the long-horizon agentic reasoning Fable 5 is built for.

**What changed instead.** The model is now chosen **per task**, not globally, so
the three calls can differ and the decision is one env var:

```bash
PROPERTYOS_MODEL_TRIAGE=claude-haiku-4-5 \
PROPERTYOS_MODEL_RETENTION=claude-opus-5 python3 agents.py --all
```

Defaults are deliberately unchanged (`claude-opus-5` everywhere). Moving triage
to something cheaper is very likely correct and I did not do it, because "likely"
is not a measurement.

**The benchmark found real bugs anyway — in the floor, not in any model.** Its
first run scored the deterministic classifier at 79% priority / 84% category with
**two under-escalations**: an exterior door that "won't latch" fell through to
`other` at P3, and "a damp patch and a musty smell" tied `leak_slow` (P3) against
`mold_moisture` (P2) and lost on dict insertion order. Fixing the keywords and
making **ties resolve upward** took the floor to **89% / 95% with zero
under-escalations**. Both are pinned in `test_propertyos.py`.

That is the finding worth keeping: the honest comparison is not model-vs-model,
it is **model vs the floor**. The floor runs on every request, costs nothing,
takes microseconds, and now holds every habitability case in the eval set. A
model earns its place here only by improving category resolution and the parts
list on top of that — which is a much smaller claim than "use a bigger model".

```bash
python3 bench_models.py                                   # floor only, no key
python3 bench_models.py --models claude-opus-5,claude-sonnet-5,claude-haiku-4-5
```

---

## The growth surfaces (third wave, 2026-08-17)

Three additions, all deliberately **intake-shaped** — Property OS records demand
and shows evidence; *working* leads (sequences, pipelines, outreach) belongs to
the separate Growth module spec'd in `GROWTH_MODULE_SPEC.md`.

- **The pitch page** (`/pitch?t=<token>`): a white-label, live portfolio-performance
  one-pager — the same arithmetic as the internal dashboards with the private
  columns removed. No owner/resident/vendor names, no street addresses, no
  balances (trust reads *balanced* or *OUT OF BALANCE*, never an amount); every
  unmeasured figure renders its reason. The token is the credential; rotating it
  (console → Leads) kills every shared copy. Pinned white-label by test: the
  suite greps the payload for every seeded name and address.
- **The owner-referral hook** (owner dashboard): the ask lives on the page that
  earned it. An owner records a name + contact; recording is R3 bookkeeping,
  and `referral_outreach` sits at **R1 forever** — a referral is a name, not
  consent to be contacted by software. Owners see their own referrals' status,
  never the book.
- **Leasing-inquiry intake** (`/inquire`, public): vacant-unit listings + an
  inquiry form. The queue is **strictly FIFO** — the position number is the
  whole of the prioritisation. `growth.prospect_score()` is a tombstone that
  refuses by construction; `prospect_screening` is R0 permanently; the ack every
  prospect receives is the identical template (sameness is the fairness
  control); and the sentinel screens prospect-directed text at full resident
  strictness. Counsel-gates before any real applicant traffic, same as the rest.

## The Growth module (fourth wave, 2026-08-17 — `pipeline.py`, `/growth`)

The Sales-pillar sibling module from `GROWTH_MODULE_SPEC.md`, v1 built as
spec'd: the owner-prospect pipeline that turns recorded demand into doors.
Two agents on the shared substrate — **scout** (imports referrals, writes
briefs from recorded facts only, runs the cadence nag at the HUMAN, closes the
loop back onto referral rows) and **scribe** (drafts first touches, follow-ups,
referrer thank-yous/updates at R1, and R0 proposal shells whose pricing
brackets are always the principal's).

**Not referral-only (the Founder, 2026-08-17): the module prospects.** Sourced target
lists import in bulk (`import_targets`, R2) with **mandatory provenance** — we
don't contact people we can't say how we found — deduped, with opt-outs and
previously-lost prospects skipped-and-reported rather than silently added.
Sourced prospects get their own COLD first-touch template: provenance surfaced
for the human's review, the evidence block, an explicit opt-out line, and the
physical-address bracket commercial email requires. The discipline is built
in, not advised: the **do-not-contact ledger is permanent** (every import and
every draft refuses it by construction), and after **3 sent touches with no
reply the prospect rests** (`rest_prospect`, R2) — only a deliberate human
action revives the cadence. Silence is an answer.

The defining absence: **no send rail exists** — not a rung, not a flag. Every
message is a draft a human sends from their own mailbox and then records; the
suite pins the absence so it cannot arrive as a refactor. Three more lines
that hold: a draft may only cite figures computable from the pitch page at
draft time (a number outside the evidence refuses the draft — `numbers_ok`);
`contacted` and beyond move only on a human's say-so, because those stages are
claims about what a human did; and conversion refuses below 10 recorded
outcomes. `won` scaffolds the ops-module owner + property shell with every
default flagged for onboarding. Counsel gates (CAN-SPAM posture — MORE binding
now that outreach includes cold contacts, referral incentives, proposal
template) stand before any real prospect.

---

## Honest limits

- **Zero clients, zero real data.** Synthetic portfolio, deterministic seed. Nothing
  here is evidence that any number holds in the field.
- **Turn-cost is an assumption set**, not a measurement — 32-day vacancy, 75%-of-a-
  month leasing fee. Stated on screen so a manager can argue with the inputs. Replace
  with the client's own trailing-12 actuals before quoting them.
- **Avoided cost is a counterfactual.** No money moved. Labelled as such everywhere.
- **The fair-housing screen is a deterministic term list**, not a legal review. It
  catches the obvious and is a backstop, not counsel. Counsel-gate before any real
  resident traffic.
- **Auth is pilot-grade, off by default.** Access codes + signed cookies + role
  enforcement exist and are tested (`PROPERTYOS_AUTH=1`), but this is still
  single-tenant and localhost-bound. Multi-tenant isolation is delivery work.
- **The trust ledger and payment drafting are bookkeeping software.** Counsel/CPA
  review gates any use with real funds; state trust-account rules bind the
  operator. The system's own hard line — it cannot execute a transfer — is
  enforced in code and pinned in both suites.
- **PWA, not native.** One codebase, installs to a home screen, camera capture works.
  A native shell would add reliable iOS push (the thing that actually matters for a
  2am emergency) and background location for vendor ETAs.
- **Little's Law surprises people:** a well-run 220-unit portfolio carries ~25 open
  requests, not hundreds. A competitor dashboard showing 200 open rows at this size is
  displaying a backlog, not a feature.

---

## Where the parts live

```
core.py       every RULE: SLA matrix, triage taxonomy, vendor scoring, lease math,
              renewal risk, component economics, the autonomy matrix, the refusals
agents.py     the agents; Claude calls + the deterministic floor under each
money.py      the trust ledger, charges/payments, delinquency, statements, batches
growth.py     the pitch one-pager, owner referrals, FIFO inquiry intake,
              and the prospect_score() tombstone
pipeline.py   the Growth module: owner-prospect pipeline, scout + scribe,
              drafted-never-sent outreach, the won->ops scaffold
seed.py       the synthetic portfolio (deterministic; --units / --months)
server.py     stdlib JSON API + static host, 127.0.0.1:8813
app/          tenant · staff · owner · job · pitch · inquire + PWA shell
test_propertyos.py   272 domain/refusal assertions
bench_models.py      triage eval set — model vs the deterministic floor
test_journeys.py     213 journey + contract assertions (boots its own server)
GROWTH_MODULE_SPEC.md  the Sales-pillar module's spec + build record (v1 = pipeline.py)
data/         the JSON store (photos gitignored)
```

Next, in order: counsel gate on the resident-facing copy and the screen; real
tenant isolation + auth; then a pilot with one 100-unit operator to find out which of
the six differentiators a buyer will actually pay for.

---

## Importing a real book of business

`seed.py` invents a portfolio. `seed_parker.py` imports one from the spreadsheet a
manager already keeps, so a prospect sees their own doors, tenants and trust ledger:

```bash
python3 seed_parker.py "/path/to/Rent Account Journal 2026.xlsx"
python3 server.py
```

It expects one journal sheet with `Date · Parties · Description/Purpose · Property ·
Number · Cleared Bank · Deposits · Checks pd · Balance`, and derives properties,
units, owners, tenants, charges, payments, maintenance history and a double-entry
trust ledger from it. Demo login codes are dropped on import — they exist only
because the synthetic portfolio is synthetic.

**Real books are messy, and the importer treats that as the product rather than an
obstacle.** It folds spelling variants ("1010 Bexton" / "1010 bexton st" /
"Bexton") and near-miss typos into one house, but it refuses to guess when a name
is genuinely ambiguous (a bare street with two numbered houses on it) or when one
row names several properties at once. Everything it won't guess lands in
`data/findings.json` with the source row — undated entries, unattributable rows,
rents that vary month to month, and any property whose costs exceeded its rents.
That list is the diagnostic, and on the first real import it was the deliverable.

`data/` is gitignored, so importing real books leaves nothing in the repo. Restore
the synthetic portfolio from `data_synthetic_backup/`, or re-run `seed.py`.

**Scale note:** this platform is built for 20–300+ units. Imported against a
single-digit portfolio the maintenance, turns and leasing boards will be near-empty
and the app will correctly refuse to compute averages on thin data — lead with
**Money**, which is where a small manager's data is actually rich.

### Filling the operating boards

`seed_activity.py` adds illustrative maintenance, vendors, a turnover, approvals and
owner prospects **on top of** an import, using the operator's own units and tenants:

```bash
python3 seed_parker.py "/path/to/journal.xlsx"   # their real books
python3 seed_activity.py                         # their portfolio, in motion
python3 server.py
```

A trust journal records money, not the operating week, so after an import the
maintenance, turns and leads boards are empty and the platform reads as broken
rather than idle. This fills them so a prospect can see how the day works.

**It never touches money.** The ledger, charges and payments stay exactly as
imported — that is the part they will check line by line against their own
spreadsheet, and it has to survive that check.

Every generated record carries `illustrative: true`, and the dataset sets
`config.notice`, which `/api/notice` serves and the app renders as a banner on
**every page**: *"Real portfolio and trust ledger · maintenance, vendors, turnover
and leads are illustrative."* A demo that can be mistaken for the real ledger is
worse than no demo.

**Leases stays empty on purpose.** Lease start dates are inferred from first
payment, but terms and end dates are not in the books and are not invented — an
empty renewal radar is the honest picture and names the one sit-down the build
needs. Fabricating the exact field we tell them is missing would be the worst
possible shortcut.
