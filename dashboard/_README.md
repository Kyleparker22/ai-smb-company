# YourCo HQ — the company dashboard

The cockpit: every part of yourco on one screen — company overview, agent health, pipeline, finance, delivery, compliance, and the runtime loops. Sleek, tabbed, and **live** (auto-refreshes; aggregates the OS's real data). Owned by **Atlas** (BI).

## Files
- `board.py` — **The Board** (added 2026-08-07): every open item in the OS in one list, aggregated live from the files their own owners already keep — `loops/open-loops/` (needs you) · `loops/gap-audit/` (what's missing) · `processes/counsel-gates.md` + `launch-gate.md` (blocked) · `crm/data.json` (deals, bench, tasks) · `crm/_backlog.md` + `processes/automation-roadmap.md` + `offerings/_frontier-roadmap.md` (backlog) · `loops/*/` vs `runtime/agent-registry.json` (loop liveness + wiring drift). Every item is normalized to `{title, detail, lane, state, owner, age, next, source}`; **nothing is hand-maintained**, so the Board cannot rot independently of its sources. When a source *is* stale, that is rendered as a fact in the freshness strip rather than silently trusted — the 2026-08-07 gap audit's core finding is that this OS fails by not noticing absence. Gained `unshown_assets()` on 2026-08-25: **produced assets that have never been registered on a deal as shown** — the one habit blocking both Reed's and Pickle's owned numbers, and a fact no other surface states, because a metric reading blank is invisible. Fires only when there are deals in motion to have shown them in, and offers *"not fit for these conversations"* as a real answer, since silence and a decision are different states. Read-only; `python3 dashboard/board.py` prints the same payload to a terminal.
- `clients.py` — **the Clients view** (added 2026-08-07, from the Founder's "six months out, 15 clients — where do I look for status, finances, contracts?"; the answer was *nowhere* — the Delivery tab renders delivery **agents**, and `data.json` has no clients key). One row per engagement folder, joining `crm/data.json` (stage, value, touch, next action) · `cost.md` (spend ledger) · `ledger/*.jsonl` (actions, evals, incidents, outcomes, promotions) · `contract.md` (the executed-contract register) · `finance/revenue.md` (invoiced/paid) · unfilled `[[PLACEHOLDER]]` count. **Honest at zero live clients:** with nothing signed it scores **go-live readiness** against the customer-health loop's own pre-engagement requirements, and the same card switches to green/yellow/red health the day a deal reaches `live` — no rebuild. **Never invents a number:** ledger rows like `~$15–25` and `unknown` are reported as a range plus an unpriced count, and margin renders *why* it isn't computable rather than a blank.
- `data.json` — the dashboard's own data (company stage + focus, all agents + status, loops, compliance gates, flywheel state). Atlas maintains it.
- `refresh.py` — the **derived layer** (added 2026-07-05; closes the 07-04 audit finding that `data.json` is hand-maintained and rots): derives loop health (every sanctioned timer × its latest committed `loops/` artifact → on-time / stale / never), the live autonomy ladder (parsed from `runtime/autonomy-matrix.md`), master-gate status (OtherVenture + counsel-gates rollup), and the 7-day git pulse. `server.py` recomputes it on every poll; `python3 dashboard/refresh.py` also writes the `derived` block into `data.json` for static/committed views. Read-only — the registry and the repo stay the source of truth.
- `melanie.py` — **the CRM shared brain** (1,016 lines, the largest module here). Backs Melanie's
  read/write access to `crm/data.json` from HQ: advisory file locks, atomic writes (tmp + replace),
  enrichment, and citations on anything she asserts. Two agents and a human share one JSON file, so
  every write goes through here rather than through `json.dump` in five places.
- `finance.py` — `/api/finance`. Serves `finance_model.json` read-only to the **Financial Model**
  door. The workbook (`finance/yourco-financial-model.xlsx`) is the source of truth; this never
  computes, it mirrors — see `runtime/finance_model_sync.py` for the direction of flow.
- `finance_model.json` — that mirror. Written by `runtime/finance_model_sync.py`, read by
  `finance.py` and by `runtime/consistency-check.py`, which cross-checks `06_business-plan.md` §8
  against it so the plan cannot drift from the model unnoticed.
- `northstar.py` — **the one number, and the number each agent owns** (added 2026-08-25). Three
  unrelated inputs on 2026-08-24 — the 9x9 grid's centre cell, OKR's single Objective, and "Every
  Role Owns a Number" — arrived at one finding the WBR work had already half-found: *nine co-equal
  goal metrics is zero goals, and 27 agents owned no numbers.* Both halves are one fix. The apex is
  declared in `goals.json` (the Founder's); the per-agent definitions in `runtime/agent-registry.json`
  (Rafi's, so a number an agent owns cannot be quietly changed); this module does the arithmetic and
  **stores nothing**. Three refusals are load-bearing: it will not extrapolate from a rate of zero,
  **did-it-run is not an outcome** (only Atlas may own loop liveness, because liveness is its job),
  and an unmeasured metric must name the one thing missing. **12 of 27 agents own a computable number
  today**, 1 awaits a first reading, 14 stay blank in four clusters — and that clustering is the
  actionable half. Renders on
  **Agents**; `python3 dashboard/northstar.py` prints the same payload.
- `kpis.py` — **the nine KPIs, computed or refused** (added 2026-08-25). NRR · LTV · CAC · LTV:CAC ·
  churn · burn multiple · EBITDA · operating cash flow · retention. **Seven of the nine are undefined
  at n=0**, so each carries its refusal *and* the precondition that clears it — six of them client
  #1. Two compute, and both carry caveats louder than their values (fixed burn has been materially
  uncertain since 2026-08-17; neither number prices the founder's time). Inputs come from
  `finance/actuals.json`, never parsed out of prose. Definitions and reasoning:
  `finance/kpi-definitions.md`, cross-checked against this module by the consistency watchdog.
  Renders on **Commercial → Finance**.

- `loop_metrics.py` — **the seven numbers that existed only as prose** (added 2026-08-25, closing the
  largest cluster above). Two mechanisms, and HQ shows which: **derived** = computed from files that
  already exist, so nothing has to run first and nothing can go stale (Ray's counsel gates — already
  parsed by `refresh.py` *and* `board.py*`, which means "blocked by prose" was the wrong diagnosis;
  Brett's and Melanie's adoption, counted off the citation graph over `decisions/` + `rejections/`).
  **Extracted** = read back out of the artifact a run wrote, safe only because these are
  *SOP-mandated* structures — the eval scoreboard header is byte-identical across all six runs and
  the AEO score has sat under one heading since the first. **The rule that makes extraction honest:
  a structure that does not parse reports a parse failure, never a zero.** No store, no schedule, no
  backfill — the numbers are already in git. Luka's stays blank because his own audit records zero
  pre-ship reviews, two months running: a rate over zero is undefined, not 100%, and the zero is the
  finding.

- `crm_metrics.py` — **the five that needed the CRM to record something it never had** (added
  2026-08-25). Working through them re-diagnosed three: **Jim's** number was already in his own
  open-loops queue (`Waiting since` per row, parsed by `board.py` all along) — **75 days**;
  **Sadie's** `promote_intent.py` has stamped its own source since July, so her **0** is real rather
  than missing; **Katie's** binding constraint is the launch-gate, not the schema. What the CRM
  genuinely gained: `company.channel` / `channelSource` on a controlled `meta.sourceChannels`
  vocabulary (every intake path wrote its own free-text `source`, so asking *which channel produced
  this company* meant prefix-matching prose), the `Audit delivered` activity type — the front door of
  the whole motion, and nothing counted one — and a `collateral` artifact type, so *did this
  one-pager reach a buyer* is a query rather than a memory. **The backfill contains no judgment**
  (`restated`, never `inferred`; `founder-sourced` is deliberately not `warm-network`), and every
  channel metric **refuses below 80% coverage** — a channel rate computed while most rows carry no
  channel is a lie with a denominator.

- `client_metrics.py` — **the six waiting on client #1** (added 2026-08-25). No amount of building
  produces a customer, so the question was whether these compute *when* one lands — and for three the
  answer was no. **`deal.stageSince` holds only the current stage**, so every prior transition date
  was overwritten on the next move and nothing else recorded it (zero stage-change activities in the
  log): days-to-go-live would have been unmeasurable *after* client #1 too. `deal.stageHistory` now
  appends through one writer, invariant-guarded. **Reed was re-scoped** off "appeared in a *won*
  deal" — a production agent graded on whether the founder closes — onto reach, the boundary of what
  he controls; he and Pickle now share one blocker rather than two. **Polo needed no customer at
  all**: `priceEvents` + the locked band table in `pricing/README.md` read **0 of 1**, the only price
  ever quoted sitting below every band. ⚠️ The first band parser read `$3` out of *"cap 3, then
  graduate"* and passed that quote as in-band — a false green on the one metric that exists to catch
  an off-band price; the suite and the watchdog now guard the parse.

- `uptime.py` — **runtime availability, computed from beats that never arrived** (added
  2026-08-25). A log records what happened while the box was working, so a log can never record an
  outage; `runtime/heartbeat.sh` writes one line every 15 minutes and this computes **received ÷
  expected**, making absence the measurement. Four refusals carry it: it will not claim uptime for
  time before monitoring existed (the window clips to the first beat — *"100%, all-time"* is the
  most tempting and most false first reading any monitor gives), it will not compute a rate off a
  handful of beats, **paused is not down** (a stand-down is available-and-idle, reported separately
  as `serving`), and a fresh tail gap is labelled sync lag rather than an incident. Deliberately not
  a duplicate of Atlas: Atlas measures whether the *work landed*, this whether the *substrate could
  run at all* — 59% liveness cannot tell a dead box from dead loops. ⚠️ Reads `unmeasured` until
  `yourco-heartbeat.timer` is enabled on the VPS.

- `gate_metrics.py` — **the last two, both behind the launch-gate** (added 2026-08-25). A gate is
  not something a metric can fix, so the work was making sure the first campaign and the first
  bookings do not arrive unattributed — and they would have. `seqStatus` had one undifferentiated
  `replied`, so *positive reply rate* was not expressible in yourco's own record (Instantly holds the
  classification, and a number that disappears with a subscription is not owned); the legacy value
  now counts as contacted and **never** as positive. `runtime/promote.py` wrote a retired stage, a
  nested `seq` object nothing reads, and no `stageHistory` — and the invariant written alongside it
  immediately found **four more writers with the same dead stage, including `site_intake.py`, the
  audit form**. All 61 Calendly links now carry `utm_source`. Both metrics still **refuse and name
  the gate**: a 0 would read as a verdict on the copy and the site when neither has been allowed to
  run.

Tests for all seven: `python3 runtime/test_numbers.py` — 145 assertions, each pinning one refusal.
- `security_model.py` — the security posture read from **live config**: the deny-list out of the
  host settings, the autonomy rungs, and the last immune-drill result. A control with no drill
  behind it reads *untested* — never *proven*. Internal until the launch-gate clears.
- `skills.py` — `/api/skills`, the **Skills** door (added 2026-08-23). Which of the 18 skills are
  actually being used, measured from the artifact each skill *creates* (`git log --diff-filter=A`),
  never from a file being modified — an earlier version measured last-modified and reported
  `add-runtime-loop` as "used today" because one commit touched all 25 loop prompts. Append-only
  ledgers are the deliberate exception: a new row IS the invocation. A skill that leaves no trace
  reads `unmeasurable`, not `unused`.
- `todo.json` — the Founder's to-do list behind `GET/POST /api/todo` (POST = full-list atomic overwrite).
  Currently empty; that is a fact about use, not a broken feature.
- `server.py` — the backend: serves the dashboard + `GET /api/dashboard`, which merges `data.json` + the derived layer with the **live pipeline** read from `crm/data.json` (David). Run it to view.
- `governance.py` — **the Partners door, governance half** (added 2026-08-10): what's agreed, what's signed, what blocks. The split (50/35/15) cross-checked against the CRM's own partner records, the OA's version + three unsigned signature blocks + its **own bracketed open fills** (`[LANE]`, `[STATE]`, `[AMOUNT]` … parsed from the document's convention, so filling a bracket clears the row), counsel gate #14 with its D10–D12 blockers and regression date, the counsel-engagement table (unfilled = no counsel engaged), the capital terms **quoted verbatim** from their decision, and the reversibility window. **Everything is quoted and cited, never restated** — equity splits and capital terms are facts with consequences, and a second copy in Python would be wrong the first time one changed. Where nothing records a fact it reads **unrecorded** and names where it would live; those checks look for a *structured* record (a decision file naming the person, a figure inside the agreement) and never a prose mention — the first version searched prose and the D12 trip-wire's own sentence *about* the absence satisfied it, hiding a real blocker.
- `advocate.py` — **the Partners door, people-loop half** (added 2026-08-10): renders whether the connector flywheel (`processes/yourco-flywheel.md` §The people loop / ADVOCATE) is actually turning. Rungs come from `crm/connector_ladder.compute()` — the same function the console and the statements use, so no rung, tier or commission is ever re-derived here. Its load-bearing distinction: **"tagged as a connector" is not "joined"** — `rungN == -1` is kept out of R0, because folding it in would report a network that does not exist (today: 21 tagged, 0 joined, 0 producing, loop has never turned). Also renders the two delivery gates that make the loop *downstream of delivery by construction* (R1 needs a real referral conversation, R2 needs a live client retained 90 days) — the panel must never imply the loop can be started by recruiting harder.
- `lockin.py` — **the Partners door, schedule half** (added 2026-08-10): the partner review→lock run from `processes/partner-b-walkthrough-schedule.md` (8/11–8/26, ten sessions, fourteen domains), tracked instead of remembered. The calendar, per-domain material links, standing rules and prep checklist are **parsed from that file on every call, never copied** — edit the schedule and this follows. Lock state is derived from `decisions/` per the schedule's own rule ("a domain 'locked' with nothing in `decisions/` is not locked"): `locked` requires a `**Locks:** <domain>` marker, while a title-keyword match reads `likely — unconfirmed` and is **never** counted as locked. Also: `slipped` when a lock date passes with nothing recorded.
- `index.html` — the tabbed UI, twelve<!--#count: match dashboard/index.html /data-v="([a-z-]+)"/--> doors: **Today · The Board · Clients · Partners · Commercial · Financial Model · System · WBR · Evidence · Skills · Search · Agents**. Polls every 15s (the Board every 60s — it reads ~10 files per build). Loops leads with derived loop health; Trust shows the live autonomy rungs; Compliance leads with the two master gates. **The Board** answers "what still needs to be worked on, and what needs to be added": five states — *needs you · blocked · missing · backlog · parked* — each a click-to-filter tile, crossed with six lanes (Commercial · Money · Legal · System · Build · Clients). The sidebar count is the needs-you total and is loaded on boot, not on first open, so it is honest before the tab is ever visited. **Evidence** and **Partners** load on boot for the same reason.

## Owners on The Board (added 2026-08-10)
Membership went to three — the Founder / Partner B / Mike, 50/35/15 — and the Board's owner field was decoration: every "needs-you" meant the Founder, so the view silently asserted a single-founder company. Every item now carries `ownerClass` (**partner · agent · unowned**, three genuinely different problems — delegated is not the same as dropped), `ownerKeys`, and a stable content-derived `key`. The Board gains owner filter chips, a per-row assign control, and a stated split ("Needs a partner: the Founder 18 · Partner B 0 · Mike 0"). A partner at zero is rendered, not hidden — that is the finding.

`assignments.json` is **the one hand-maintained input on the Board**, on purpose: who owns a thing is a decision, not a derivable fact (same shape as `goals.json` — human targets, derived currents). Written via `POST /api/board/assign` `{key, to}`; an assignment whose item is gone or renamed is listed as **stale**, never silently re-pointed.

## The Evidence door (added 2026-08-07)
Five views answering questions the OS previously could not ask about itself. Each is a read-only module with a `build()` and an `/api/` endpoint; each fails to a **named error** rather than an empty panel; and each **refuses to state a number its inputs don't support** — that refusal is the feature. Decision: `decisions/2026-08-07_evidence-door.md`.

| Module | Endpoint | Answers |
|---|---|---|
| `trust.py` | `/api/trust` | How much control has the OS absorbed, at what rung, and would it notice a fault? Trust ledger + calibration market + immune drills — and it **audits the hand-written streak table** in `runtime/autonomy-matrix.md` against recorded evidence, reporting `supported` / `DISAGREEMENT` / `unverifiable` |
| `tripwires.py` | `/api/tripwires` | Which settled decisions has live data now contradicted? Evaluates `## Trip-wire` sections in `decisions/` (format + fact list: `decisions/_TRIPWIRES.md`) |
| `timemachine.py` | `/api/timemachine` | What did HQ say on any past date, and which commit + which agent moved a metric? `git blame` for business numbers. Historical revisions run through the **live** `goals_currents(crm=…)` / `pipeline_summary(crm=…)`, so then-vs-now is never two code paths |
| `twin.py` | `/api/twin` | How much of the Founder's judgment has the OS learned, per class of decision? Starts empty on purpose — a prediction counts only if recorded before the call |
| `vacancies.py` | `/api/vacancies` | Which work has no owner — and is the answer **absorb** (a live agent owns it and it still hits the Founder), **activate**, or **hire**? Proposes only |

Writers live in `runtime/`, never here — the dashboard reads: `runtime/ledger.py` (shared append-only store), `runtime/trust_ledger.py`, `runtime/dri_twin.py`, `runtime/drills/`.
Stores (append-only JSONL; corrections are new events citing the original): `loops/_trust/actions.jsonl` · `forecasts.jsonl` · `drills.jsonl` · `loops/_twin/predictions.jsonl`.
Maintained by the weekly **`evidence-sweep`** loop (Kolby, Sun 16:30 ET → `loops/_trust/<date>.md`).
Tests: `python3 runtime/test_evidence.py` — 54 assertions, each pinning one honesty rule in place.

## Run it
```
python3 dashboard/server.py    # then open http://127.0.0.1:8791
```

## Live / integration model
Atlas aggregates the OS's real data into one view. v0 reads:
- `data.json` — agent statuses + company metrics + focus (Atlas-maintained), and
- live **pipeline** from `crm/data.json` (David's CRM).

As each connector lands (**Instantly, QuickBooks, Granola**, …), extend the aggregation in `server.py` and the relevant tab fills in automatically — finance from QuickBooks/Charles, outreach from Instantly, etc. True real-time deepens as the always-on runtime keeps the sources fresh; the UI already polls every 15s.

## Owner: Atlas
Atlas keeps `data.json` current (agent statuses, metrics, this-week's focus) as part of its ops/BI role. Pipeline is live from David; finance from Charles; compliance from Rafi; loops from the runtime. This is also the CEO-level view **Melanie** (CEO-in-training) reads to learn how the company is run.

## The WBR door (added 2026-08-13)
Amazon's weekly-business-review discipline, from `loops/_advisory/2026-08-13_hq-design.md`.

- `wbr.py` (`/api/wbr`) — **controllable inputs above the outputs.** All nine goal metrics were
  outputs; none is movable on a Tuesday. Five inputs are now counted from the CRM activity log and
  deal `stageSince` — never typed. **Row order is fixed**: the unchanging layout is the mechanism
  that lets an anomaly announce itself. Three inputs the Founder would want are **not computable** and are
  listed as such with the one field each needs (new prospects added · warm intros · referral asks —
  that last one is the connector program's leading indicator and is currently invisible). Also the
  **6-12**: trailing 6 weeks beside trailing 12 months per metric via `timemachine.as_of()`, with a
  flat series labelled flat rather than drawn as a trend.
- `prosecution.py` (`/api/prosecution`) — **HQ arguing against its own headline numbers**, from the
  same data. Every charge is computed; a hard-coded pessimistic sentence would be decoration.
  *No case to answer* is a real verdict and the most useful one. It prosecutes, it does not
  sentence, and it never invents a worse number. **It found live drift on its first run** — see below.
- `hq_usage.py` (`/api/hq-usage`, `POST /api/hq-visit`) — the two views that need HQ to remember it
  was looked at. **What changed since you last looked**: a computed cross-company delta against the
  snapshot taken at the last visit, possible only because every payload is derived and therefore
  fingerprintable (counts and hashes are stored, never payload bodies). **The panel-usefulness
  audit**: the only feature in HQ that argues for making HQ smaller — a panel never opened whose
  data never moves is proposed for removal, behind a warm-up floor of 10 visits and 14 days.
- `runtime/hqlink.py` — build a URL that opens the exact screen: `#board?state=needs-you&owner=the Founder`.
  HQ parses hash query params and applies board state/lane/owner. **A link is not an alert** — the
  loop still decides what is worth interrupting for; this only makes the destination addressable.

**The drift the prosecution panel caught on day one.** The CRM restructured its stage ladder on
2026-08-13 and the bench became `pre-convo`; `server.py`'s `BENCH_STAGES` still said `prospect`, so
HQ counted all 18 bench deals as in-motion and reported **21 deals / $24k against a real figure of
3**. Fixed, and `runtime/consistency-check.py` now fails if any CRM stage key is unknown to HQ — a
stage rename can never again silently inflate the most-quoted number in the company. Caught by
machine, not by eye, which is the first time that has happened here.


## Visual: Option 1C — the brand palette, adopted (2026-08-13)
Chosen from `_archive/hq-redesign-2026-08-13/2026-08-13-index.html` (three structure options, then three palette
options; the Founder picked **1C · Banded**). What changed in `index.html`:

- **Tokens retargeted to `brand/DESIGN.md` §1.** HQ had run since it was built on an *invented*
  neutral slate (`#232833`) with cold blue-white text — which is what made it read as "blocks of the
  same colour". Now indigo `#161B33`, warm cream `#F4EFE6`, bronze brass `#B8965A`, and real oxblood
  `#6B1E29` (previously aliased to red and used nowhere). **Token names were left unchanged on
  purpose** so every existing rule inherited the new palette with no structural edit and nothing missed.
- **Banding (idiom 4).** Every second `.view` is a light full-bleed cream band, so a door scrolls
  dark → light → dark. Light bands carry the tables — numbers read better off cream. The bleed is
  `-var(--mainpad)`, never `-100vw`, which would run under the sidebar.
- **How the band works, and why it matters:** it **redefines the tokens for its own subtree**
  (`--txt`, `--faint`, `--line`, `--surface`, `--brass`…) rather than restyling components. The first
  attempt listed ~20 component classes and left ~500 elements cream-on-cream, because HQ has ~40
  bespoke class families. Scoped token inversion flips every descendant automatically — including
  components written later that nobody remembers to add to a list.
- **Brass rationed (idiom 1).** `h2.sec` — 150 of them — went from brass to muted.
- **Panels flat** (hairline, no shadow) with `.panel+.panel` spacing.

**Contrast is measured, not eyeballed.** A WCAG pass over 3,046 elements across all eight doors:
**0 near-invisible (<2.5:1)**, 71% at full AA. The remaining 29% are 11px muted labels below 4.5:1 —
a pre-existing posture of a dense dark dashboard, not something this change introduced, and worth
its own pass.

**Two bugs found while doing it, both pre-existing:**
1. `.bd-tile` is a `<button>` and buttons don't inherit colour — the UA painted them black. The
   Board's neutral tile counts ("10 missing", "42 backlog", "9 parked") had been **black on dark and
   effectively invisible since the Board shipped**; only `.crit`/`.warn` were legible because they set
   a colour. Fixed globally with `button,select,input,textarea{color:inherit}`.
2. `.gpace.behind` sat at 2.09:1. First "fix" *lightened* it to 1.81 — the ground is light, not dark.
   Corrected by darkening it inside the band instead.
