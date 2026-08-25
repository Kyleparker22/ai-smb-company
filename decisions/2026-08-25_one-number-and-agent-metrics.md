# The one number, and the number each agent owns

**Date:** 2026-08-25 · **Decided by:** the Founder · **Built by:** Atlas (HQ) + Rafi (registry) + Charles (KPIs)

## The finding, which arrived four separate ways in one day

On 2026-08-24 eight unrelated inputs were triaged (`loops/_triage/2026-08-24_frameworks-kpis-batch.md`).
Four of them independently pointed at the same defect:

| Input | How it said it |
|---|---|
| The 9×9 Mandala goal grid | The grid is built around **one centre cell**; the 81 are downstream of it |
| OKR | **One** Objective. Not nine. |
| An AI-native agency system map | *"Every Role Owns a Number"* and *"Reports Outcomes, Not Activity"* |
| yourco's own WBR work (2026-08-13) | All nine goal metrics are **outputs the Founder cannot move on a Tuesday** |

> **yourco had nine goal metrics — which is zero goals — and twenty-seven agents, none of which
> owned a number.**

Verified rather than assumed: `runtime/agent-registry.json` had no metric, kpi or target field of any
kind, and `dashboard/server.py` carried nine co-equal `GOAL_METRICS`.

Four independent routes to a gap the OS had half-found is the strongest signal a triage batch has
produced. Ten of the thirteen frameworks in that batch were skipped; this is what was worth building.

## The decision

**One north star: `liveClients`.** The other eight metrics remain tracked, remain true, and become
explicitly **supporting**. Declared once, in `dashboard/goals.json` → `northstar`, which is **the Founder's**
file — Melanie may propose a change and may never adopt one.

**`liveClients` over `mrr`**, because MRR at brotherhood pricing ($1,000/mo against a $3,000 Core
floor) measures the discount as much as the business. **Over `dealsInMotion`**, because a board can
be busy without ever signing — 3 in motion and 34 on the bench is precisely that shape. Every one of
the remaining eight either feeds live clients or protects the runway to reach them.

**Every agent owns exactly one number**, declared in `runtime/agent-registry.json` →
`agent_metrics.agents` and computed live by `dashboard/northstar.py`. The definitions sit in Rafi's
sanctioned registry deliberately — the same reasoning that put `agent_budgets` there: a number an
agent owns should not be quietly editable, and the governance watchdog sees a change to it as drift.

**The nine KPIs are defined now and refuse until they mean something** —
`finance/kpi-definitions.md` (reasoning) + `dashboard/kpis.py` (arithmetic) +
`finance/actuals.json` (inputs).

## What we deliberately did NOT do

- **No 13th HQ tab.** Both panels ride on doors that already exist (Agents, Commercial → Finance).
  `dashboard/hq_usage.py`'s whole argument is that HQ should get *smaller*; adding a door to announce
  a simplification would have been the joke writing itself.
- **No activity counts standing in for outcomes.** Every agent has a loop artifact that could have
  been counted, and counting it would have produced 27 green numbers by lunchtime. Only Atlas owns
  loop liveness, because liveness genuinely is its job. The other 21 read blank, and **the blank list
  is the deliverable.**
- **No projection.** "At the current rate you reach 5 live clients on <date>" is the most useful
  sentence a north star can produce and the easiest to fake. At a rate of zero it is a division, not
  a forecast, and the module says so instead.
- **No targets on the nine KPIs.** A target for a metric never measured is a wish. These get targets
  after three months of real readings.
- **No auto-fixing the 21 gaps.** Each names its own missing input; closing them is scheduled work,
  not a side effect of this change.
- **We did not adopt the 9×9 grid.** yourco's failure mode is not too few planned actions — it is 3
  deals in motion, 0 signed, ~20 loops, 27 agents and 24 surfaces. A grid generating 64 more actions
  is the wrong medicine for this illness. **The centre cell was the half worth stealing.**

## What it found on day one

- **6 of 27 agents own a computable number.** The other 21 cluster into five root causes:
  **7** blocked by a loop that writes prose where it could write a number · **6** by client #1 · **5**
  by one missing CRM field · **2** by the launch-gate · **1** by having no monitoring at all. The
  clustering is the actionable half — "seven loops should emit a number alongside their memo" is an
  afternoon; a list of 21 metrics is a project nobody starts.
- **Atlas: 59%.** Sixteen of 27 sanctioned loops are inside cadence. The runtime alarm fires on
  failed runs and never on silence, so this is the first place that number has been stated as a
  number.
- **Kemba's gap and the client SLA's gap are the same gap.** Nothing in `runtime/` measures
  availability, which is also what `processes/contracts/sla.md` promises and cannot yet verify. One
  missing thing, two consequences.
- **2 of 9 KPIs compute**, and both carry caveats louder than their values.
- **A correction:** the triage artifact said *37 deals in motion*. Thirty-seven is the **total**; 34
  are on the `pre-convo` bench and **3** are in motion. Corrected in the artifact. Same class of
  error as the 2026-08-13 stage-rename drift, and caught the same way — by computing it instead of
  repeating it.

## Follow-up, same day — the prose cluster is closed (7 → 6 computed, 1 awaiting)

The largest cluster was seven agents whose loop *already produced* the number and then wrote it into
a memo nothing could read. Fixed in `dashboard/loop_metrics.py`, and the work re-diagnosed three of
the seven:

| Agent | Number | Mechanism | Now |
|---|---|---|---|
| Ray | Open counsel gates | **derived** | **20** — the gate table was already parsed by `refresh.py` *and* `board.py`. Not a prose problem at all; no metric had pointed at it. |
| Brett | Recommendations adopted | **derived** | **43%** — 9 of 21 memos cited by a decision or rejection |
| Melanie | Initiatives adopted | **derived** | **0 of 11**, and labelled a **floor** |
| Rafi | Open registry drift | **extracted** | **4** — from the watchdog's own report |
| Kolby | Eval pass rate | **extracted** | **100%** (19 of 19) — and flagged **⚠ STALE**, 44 days on a 7-day loop |
| Mario | Citation-presence | **extracted** | **0%** — correct while nothing is published |
| Luka | Cleared on first review | **extracted** | **awaiting** — see below |

**Derived vs extracted is a real distinction, and HQ shows which.** Derived means computed from files
that already exist; nothing has to run first and nothing can go stale. Extracted means read back out
of the artifact a run wrote — safe only because these are **SOP-mandated structures**, not prose: the
eval scoreboard's header is byte-identical across all six runs and the AEO score has sat under the
same heading since the first one. The same pattern `board.py` already uses on `counsel-gates.md`.

**Three things this deliberately does not do.** No store, no schedule, no second copy — the numbers
are already in git and a store would have needed a writer, a cadence and a staleness policy to hold
them. No backfilling. And **no prose parsing**: a structure that does not parse reports a *parse
failure*, never a zero, because 0 looks like an answer and blank does not.

**Three SOPs became contracts** (`eval-review`, `aeo-geo`, `brand-audit`), each carrying a warning at
the structure that is now read, and the general rule went into `_loop-contract.md`, which every loop
reads: keep the shape, write the honest figure including zero, never state a number this run did not
measure.

**Luka is the one that stayed blank, and the blank is the finding.** A first-time-pass *rate* needs a
denominator, and his own 2026-08 audit records **zero assets queued for pre-ship review, two months
running** — the brand custodian is catching drift after ship rather than at it. Inferring that count
from a sentence is exactly the fragility being removed, so the SOP now requires a `## Review volume`
line and the metric reads `awaiting` until the next monthly run writes one. **A rate over zero
reviews is undefined, not 100%.**

**A third state was added** — `awaiting` (a real source declared, nothing readable right now) is now
distinct from `unmeasured` (nothing wired at all). Collapsing them would hide a broken extractor
inside the same blank as the metrics nobody has built.

**Where the board stands: 12 of 27 computed, 1 awaiting, 14 unmeasured** — 6 waiting on client #1,
5 on one CRM field, 2 on the launch-gate, 1 on monitoring that does not exist.

## Follow-up 2 — the CRM cluster (5 → 2 computed, 2 awaiting an event, 1 re-diagnosed)

Five agents owned a number the CRM could not answer. Building it re-diagnosed three of the five,
which is now the pattern: **the useful output of naming a gap is finding out it was the wrong gap.**

| Agent | Was diagnosed as | What it actually was | Now |
|---|---|---|---|
| **Jim** | needs an age stamp on Board rows | **Wrong.** His own open-loops queue has carried `Waiting since` per row all along, and `board.py` already parsed it. | **75 days** |
| **Sadie** | `promote_intent.py` doesn't stamp a source | **Wrong.** It has written `source: "sadie intent (…)"` since July. Nothing had ever come through it. | **0** — and the zero is the finding |
| **Katie** | needs a channel field | **Half right.** The field was missing *and* the binding constraint is the launch-gate. | refuses, naming the gate |
| **Bella** | needs an `Audit delivered` activity type | Correct. | awaiting the first audit |
| **Pickle** | needs an artifact link on activities | Right in substance, wrong in place — deals already carried `artifacts`; what they lacked was a **type**. | awaiting the first piece registered |

**Three things were added to the CRM.** `meta.sourceChannels` + `company.channel` / `channelSource` —
the controlled answer to *which channel produced this company*, because every intake path already
wrote its own free-text string (`"instantly (replied)"`, `"sadie intent (reddit)"`, `"audit intake
form"`) and the only way to ask was prefix-matching prose, which is the exact fragility this whole
sweep was removing. `Audit delivered` as an activity type — the front door of the entire motion, and
nothing counted one. And `collateral` as an artifact type, so *did this one-pager reach a buyer* is a
query rather than a memory.

**The backfill contains no judgment.** `channelSource` is `recorded` (stamped at intake), `restated`
(a faithful rename of what `source` already said) or `inferred` (a judgment). **Nothing is
`inferred`** — and `founder-sourced` is deliberately *not* `warm-network`: it says who typed the row
and claims nothing about how the Founder knows them. The two companies whose `source` was blank were left
unset, because there was nothing to restate.

**Coverage is a refusal condition.** A channel rate computed while most rows carry no channel is a
lie with a denominator, so every channel metric refuses below 80% and says how many rows it saw.
All four intake paths now stamp, and an invariant fails if one stops.

**Two refuse rather than report a confident zero, for different reasons.** Pickle's 0% would claim
the linking habit exists and failed — it does not exist yet. Katie's 0 would read as a verdict on the
content when the truth is that nothing has been published. **Sadie's zero is real and is reported**,
because refusing everywhere would be its own dishonesty: the path has been live and stamped since
July, and listening has produced nothing.

**Where the board stands: 14 of 27 computed, 4 awaiting, 9 blank** — 6 on client #1, 3 on the OtherVenture
gate (Katie joined Michelle and Webb), and 1 on monitoring that does not exist.

## Follow-up 3 — the six waiting on client #1

**No amount of building produces a customer.** So the question was never "how do we make these read a
value" — it was: *when client #1 finally lands, will these compute, or will the data already have
been destroyed, never captured, or scoped to something the agent cannot move?* For three of the six
the answer was no.

**The one that could only be fixed before the fact.** `deal.stageSince` records only the **current**
stage's entry date — the moment a deal advances, the previous one is overwritten. Nothing else
recorded it: there were **zero** stage-change activities in the entire log. So *days from signature
to go-live* (Janice) and *days from discovery to go-live* (Kimi) would have been unmeasurable **after
client #1 too** — by the time anyone asked, the answer would already be gone. `deal.stageHistory` now
appends on every move, through one writer, guarded by an invariant. History before today is genuinely
lost for existing deals and the metrics say so rather than filling it in.

**Two were scoped to someone else's outcome.** Reed's was *"assets that appeared in a **won**
deal"* — a production agent graded on whether the Founder closes. **Re-scoped to reach**: an asset that got
in front of a prospect did its job; what happens next is the sales agent's number. Pickle was
re-scoped the same way in the CRM cluster, and the two now share one blocker — *nothing is registered
on the deal where it was used* — which is **one habit, not two problems.**

**One needed no customer at all.** Polo's *"proposals at a locked band"* is quotable before anything
is signed, `deal.priceEvents` has carried one since 2026-08-13, and `pricing/README.md` holds the
locked table. It reads **0 of 1: the only price ever quoted sits below every band, including the
on-ramp floor.** That is precisely the failure the metric exists to catch, and it was in the data the
whole time.

> ⚠️ **The first version of that parser read `$3` out of "cap 3, then graduate"** and passed the
> $1,000 brotherhood rate as *inside* the on-ramp band — a false green on the one metric whose whole
> job is catching an off-band price. Fixed, and both the test suite and the consistency watchdog now
> guard the parse.

**Three are honestly just waiting**, and their meters are installed and empty on the `agent_budgets`
principle — *a meter installed afterwards measures nothing that already happened*:
`finance/actuals.json.invoices` (Harry) and `deal.health` (Kortney), plus the two go-live clocks.
**An unscored live client is not counted as healthy**, and an invoice still inside its terms is
neither on-time nor late.

**Where the board stands: 15 of 27 computed, 9 awaiting, 3 unmeasured** — and the three genuinely
unmeasured are Kemba (no uptime monitoring exists) and Michelle + Webb (the launch-gate).

## Follow-up 4 — runtime availability, measured from beats that never arrive

The last unmeasured metric that was nobody else's blocker. Kemba owned *runtime uptime (%)* and
**nothing in the repo measured availability** — which was also precondition #1 of the client SLA,
whose own §6 says an unmeasured month reads as a **miss**. The absence of this instrument was a
standing failure, not a gap.

**The design is one idea.** A log records what happened while the box was working, so a log can
never record an outage. `runtime/heartbeat.sh` writes one line every 15 minutes and nothing else, and
`dashboard/uptime.py` computes **beats received ÷ beats expected** — so *a missing line is the
outage*, not a hole in the record. Absence is the measurement. That is the same lesson
`learnings/ops/2026-08-07_absence-is-invisible-to-this-os` cost three dark days to learn.

**Pure shell, zero API calls**, on the same reasoning as `runtime-alarm.sh`: the runtime has gone
dark twice from a dead credit balance, and the one instrument that must keep working during an
outage cannot depend on the thing that is out.

**Four refusals, each a lie it would otherwise tell:**
1. **It will not claim uptime before monitoring existed.** The window clips to the first beat. The
   most tempting first reading of any monitor is *"100%, all-time"*, and it is always false.
2. **No percentage off a handful of beats** — at a 15-minute beat, 99.5% and 97% are three beats apart.
3. **Paused is not down.** A deliberate stand-down is *available and idle*, reported as a separate
   `serving` figure, so a planned pause cannot read as an outage and an outage cannot hide behind
   "we meant to".
4. **A fresh gap at the tail may be sync lag, not downtime**, and it says which.

**Two details that would each have quietly broken it.** `Persistent=false` on the timer — a
persistent timer fires catch-up runs after downtime and would **back-fill the exact gap the
instrument exists to expose**, so the outage would erase its own evidence. And the store is
`loops/_health/`, **not** `loops/_runtime/`, which is gitignored — and being gitignored is precisely
why none of this was ever visible from the Mac.

**It does not duplicate Atlas.** Atlas measures whether the *work landed* (artifacts inside cadence);
this measures whether the *substrate could run at all*, on a clock that does not care whether
anything was scheduled. Loop liveness at 59% cannot tell a dead box from dead loops. Together they can.

**⚠ It reads `unmeasured`, and will until the Founder enables the timer on the VPS** — a host action nobody
in this session can take. That is the honest state: built, committed, guarded by five invariants and
sixteen assertions, and **not yet running**. The SLA precondition is therefore **half closed** — the
mechanism exists, its subject does not: what this watches is yourco's own runtime, and there is no
client deployment to watch.

**Where the board ends: 15 of 27 computed, 10 awaiting, 2 unmeasured** — Michelle and Webb, both on
the launch-gate, and neither is a build.

## Follow-up 5 — the last two, and the bugs that were waiting for the gate to open

Michelle owns *positive reply rate*, Webb owns *bookings from the site*, and **a gate is not
something a metric can fix**. So the question was the client-#1 question again: *the day the gate
clears, will these compute — or will the first campaign and the first bookings arrive unattributed?*
Both would have.

**There was no way to say a reply was good.** `seqStatus` had one undifferentiated `replied`, so the
number outbound copy is judged on everywhere was **not expressible in yourco's own record**.
Instantly classifies interest already (`instantly.py::_is_warm`) — but that lived in a vendor's
database, and a number that disappears with a subscription is not owned. `replied-positive` /
`replied-negative` now exist here, and **the legacy `replied` counts toward contacted and never
toward positive**: a vocabulary change must not promote old rows into wins.

**`runtime/promote.py` — the only path cold leads enter the CRM by — got three things wrong**, and
every one would have fired on the first real campaign: a `prospect` stage **retired in the
2026-08-07 ladder restructure** (so each promoted lead lands off the board), a nested
`seq: {status}` that nothing reads, and no `stageHistory`.

**Then the new invariant found two more, including the worst one.** `promote_intent.py` and
`intent_server.py` carried the dead stage — and so did **`site_intake.py`, the audit intake form:
the front door of the entire motion was creating every lead on a rung that no longer exists.**
Caught by machine, not by eye, within a minute of the check existing.

**Every Calendly link on the site was bare.** A booking from the site was indistinguishable from one
out of an email, a connector, or a pasted URL. All **61 links across 24 pages** now carry
`utm_source=site` plus the page, which Calendly passes through to the booking record — and `Booking`
is an activity type distinct from `Meeting`, because `contact.nextMeeting` holds only the *next* one
and the second booking would erase the first.

**Both metrics still refuse, and name the gate.** A `0` would read as a verdict on the copy and on
the site when neither has been allowed to run — the same call made for Katie. An unreadable OtherVenture
tracker is treated as **closed**: never assume permission.

**The board is now 15 computed, 12 awaiting, 0 unmeasured.** Every agent has an instrument. What is
left is not engineering: 4 need client #1, 3 need a first business event, 3 need the launch gate, 1
needs a host install, 1 needs a monthly loop to run once.

## Follow-up 6 — the three waiting on a first business event

**This one cannot be closed by building, and saying so is the finding.** Bella needs an audit
delivered; Reed and Pickle need an asset put in front of a prospect. I checked whether any of the
three had *already happened and simply gone unrecorded* — the re-diagnosis that closed most of the
earlier clusters — and none had. Sample Realty's `audit-report/` is still the shipped **"YourCo
Landscaping"** sample. Sample Client has three meetings and **zero artifacts**. The only artifacts in
the CRM are Kimi's delivery builds on Sample Realty, none typed `collateral` or `video`.

So what got fixed is the two reasons these would stay blank anyway:

**1. The recording step now lives where the doing is described.** The prose cluster's lesson was
that a loop producing a number and writing it into a memo is the same as not producing it — this is
the human version. `processes/audit-sop.md` gains **Step 6: log `Audit delivered` the moment the
report is in their hands** — including when the answer was *"we can't help you"*, because **a
conversion rate that quietly drops the ones that didn't sell is not a conversion rate.** Reed's
and Pickle's build docs gain the same one-line definition of done: *register it on the deal*.
Guarded, so it cannot be quietly dropped.

**2. The Board can now say that nothing has been shown.** A metric reading blank is invisible in
exactly the way `absence-is-invisible-to-this-os` describes, so the Board carries a row:
**11 produced assets — 8 collateral, 3 published videos — and not one registered on a deal, with 3
deals in motion to have shown them in.** It fires only when there are live conversations to show
them *in*, because producing assets before there is an audience is a sequencing choice, not a
defect. And it offers *"these assets are not fit for these conversations"* as a real answer —
**silence and a decision are different states**, and only one of them is information.

**Reed's and Pickle's numbers are blocked by one habit, not two problems**: nothing is registered
on the deal it was used on. Both channels that would carry Reed's work — Reilly's Email 2 and the
site — are behind the launch-gate, but **a video shown on a call is not gated**, and that is the
fastest route from refused to real.

## Trip-wire
- **Review:** 2026-11-25
- **Overturn if:** `liveClients` stops being the constraint — either because clients are landing and
  the binding limit becomes delivery capacity or cash, or because the company changes shape (a
  vertical product, a partner-led motion) such that a different single number governs. Also overturn
  if the per-agent metrics are still 21-of-27 unmeasured at review, which would mean the definitions
  were an artefact rather than a plan.
- **Check:** `liveClients >= 3`
- **Check covers:** only the first clause. Whether a *different* number should govern is a judgment
  no fact in the OS can make, and the 21-of-27 half is visible on HQ → Agents but is not expressible
  in the check language. A firing check is a prompt to re-read this page, not a green light.
