# yourco CRM — workspace-native, owned by David

The single source of truth for yourco's revenue relationships: companies, contacts, deals (the pipeline), and activity. Workspace-native — own the data, git-tracked, no SaaS to babysit — with a sleek dashboard in the yourco/Apple design language.

## What's in here — 49<!--#count: files crm/*--> files, grouped

The previous version of this list covered **5**. Everything below is real and reachable — there are
**no orphaned modules** in this folder (checked 2026-08-23 by import graph, not by grep).

### The core — the data and the two ways to reach it
| File | What it is |
|---|---|
| `data.json` | **The source of truth.** `{stages, companies, contacts, deals, closed, activities, tasks, …}`. Git-diffable. |
| `data.js` | Auto-generated mirror so `index.html` opens statically. **Never hand-edit** — `server.py` regenerates it. Verified byte-identical 2026-08-23. |
| `server.py` | The backend: serves the dashboard + a read/write API over `data.json` (`:8790`). |
| `index.html` | The dashboard — pipeline, contacts, companies, activity, metrics. Editable when the backend runs. |
| `mcp_server.py` | The MCP surface. `MCP.md` documents it. **No tool writes, sends or spends** — pinned by a test. |

### The insight layer — seven reads a CRM row cannot produce
Each is served at `/api/insight/<key>`. This is the differentiated half of the CRM.

| Insight | Module | What it answers |
|---|---|---|
| `ghost` | `ghost.py` | Where every deal would be at your own median velocity |
| `spread` | **`adversarial.py`** ⚠️ | Two opposed readers, one evidence bundle — a wide spread means *we* are the only party moving it |
| `calibration` | `calibration.py` | Your own forecasting bias, measured |
| `warmpath` | `warmpath.py` | Which single relationship, warmed this week, unlocks the most pipeline |
| `promises` | `promises.py` | Sold-vs-delivered drift, as promise debt |
| `mirror` | `mirror.py` | The buyer's own ladder, and where our stage overreaches it |
| `autonomy` | `autonomy.py` | % of *pipeline-moving* work running without you |

⚠️ **`spread` is the one insight whose module is not named after it** — it lives in `adversarial.py`.
That break in the convention is why it reads as missing.

### Command-line tools — run by hand, nothing imports them
**~1,700 lines that were undocumented until 2026-08-23.** All seven run today; each takes `-h`.
Not orphans — deliberate tools with no home in the UI yet.

| Tool | `python3 crm/<x>.py` gives you |
|---|---|
| `antipipeline.py` | The deals the CRM recommends you **decline** |
| `autopsy.py` | Why a deal died, diagnosed rather than mourned |
| `capacity.py` | The supply-side constraint the forecast pretends does not exist |
| `counterparty.py` | The buyer's copy of the record, and their right to dispute it |
| `decision_pl.py` | `decisions/` graded against what actually happened *(113 decisions, 19 measurable)* |
| `mirror_close.py` | Our own read of the deal, handed to the buyer |
| `wager.py` | A calibration bet with the owner on their own self-knowledge |

### Supporting modules
`blocks.py` (what is blocking each deal) · `capacity.py` · `conversation.py` · `expansion.py` ·
`history.py` (as-of reconstruction) · `pricing_power.py` · `enrich_waterfall.py` (enrichment order).

### The connector program — 9<!--#count: files crm/connector_*.py--> modules
`connector_ladder` (rung computation — **the authority**, never re-derived elsewhere) ·
`connector_approvals` · `connector_calibration` · `connector_escrow` · `connector_ghost` ·
`connector_perks` · `connector_statements` · `connector_training` (the training GATE: what you may
read, and whether your training lets you hold the rung your evidence earned) · `connector_writes`
(the write path the console shares).

### The role coach — `coach.py`
Practice, as opposed to curriculum, and **role-generic rather than connector-specific** — which is why
it does not carry the `connector_` prefix. Serves authored drills from each role's
`*-training/_drills.json`, tracks who practised what, and computes growth areas. Deterministic
throughout: it selects and scores, an **agent** judges free-text answers against the authored rubric.
Records carry `by="agent"|"self"` and the two never merge — a self-mark cannot clear a judged miss.
**Partners are refused by design** (their duties are undefined — the OA's open gap #8); the refusal
states its own unblock condition. Consumed by `.claude/skills/run-coaching-session/` and by the
Connector Console's Practice section.

### Tests — (run `python3 crm/test_connector_v3.py`) + (run `python3 crm/test_insights.py`) + (run `python3 crm/test_connector_bounty.py`) checks, all passing
`test_insights.py` (100) · `test_connector_v3.py` (76) · `test_connector_bounty.py` (39).
Run any directly: `python3 crm/test_insights.py`.

### State files — caches and queues, not sources of truth
`_pending-activities.json` (autolog awaiting confirm) · `_promise-candidates.json` ·
`_deal-spread.json` · `_outcomes.json` · `_agent-escalations.json` · `_granola-processed.json` ·
`_attribution-log.jsonl` · `_ghost-cache.json` *(gitignored — derived, rebuilt from git history)*.

### Docs and telemetry
| File | What it is |
|---|---|
| `_README.md` | This file. |
| `_backlog.md` | The CRM's own backlog — what David has not built yet. Feeds HQ's Board. |
| `MCP.md` | The MCP surface contract. |
| `telemetry.jsonl` | Dashboard usage events (which panels get opened). Append-only. |

### `integrations/`
`instantly_sync.py` + `instantly-last-sync.md` + `instant-employee-capture.md`.

## How to use it
- **Edit (live):** `python3 crm/server.py` → open **http://127.0.0.1:8790**. Add / edit / move / delete deals, contacts, companies, and activities right in the UI; every change auto-saves to `data.json` (and regenerates `data.js`).
- **Quick read-only view:** open `crm/index.html` directly (uses the `data.js` mirror).
- **David** reads/writes `data.json` programmatically — hygiene, the pipeline report, and the tool syncs (see `agents/david/integrations.md`).

## Schema

Read from `data.json` on 2026-08-23. The previous table omitted **22 live fields**, most of them
added by work that shipped after it was written — the referral program, the advisors/connectors
taxonomy, and the WBR's created-at tracking.

| Collection | Fields |
|---|---|
| `companies` | id · name · vertical · size · `sizeNote` · location · `domain` · source · **`channel` / `channelSource`** · status · `statusNote` · owner · archived / archivedOn / archivedWhy · **`createdAt` / `createdAtSource`** · **`referrer` / `referredByCompany`** |
| `contacts` | id · name · companyId · role · `title` · email · phone · nextMeeting · lastTouch · status · `statusNote` · **`kind`** · **`teamRole` / `teamStatus`** · `sourcedBy` · `linkedContactId` |
| `deals` | id · name · companyId · useCase · stage · buildFee · retainer · value · nextAction · nextDate · lastTouch · owner · `health` · `priceEvents` · `seqStatus` / `seqTouch` · **`artifacts[]`** (id · name · **`type`** · status `built`/`shown`/`reacted` · date · link · reaction) |
| `closed` | id · name · companyId · outcome (`won`/`lost`/`parked`) · value · why · when · `closedDate` |
| `activities` | date · type · companyId · `contactId` · who · summary · `notes` · nextAction · `_granolaId` |

**The ones worth knowing about:**
- **`createdAt` / `createdAtSource`** — when a company entered the pipeline, and whether that date was
  *recorded* or *inferred*. The WBR's "new prospects added" counts only `recorded`, because inferring a
  creation date would let the metric flatter itself.
- **`kind` · `teamRole` · `teamStatus`** — the Advisors/Connectors taxonomy
  (`decisions/2026-07-06_advisors-connectors-taxonomy.md`). A dual-role person gets two profiles.
- **`referrer` / `referredByCompany`** — referral attribution, feeding the connector escalator.
- **`_granolaId`** — dedupe key for the Granola meeting sync; leading underscore = machine-owned.
- **`channel` / `channelSource`** *(added 2026-08-25)* — **which channel produced this company**,
  from the controlled list in `meta.sourceChannels`. `source` stays as the human detail; `channel` is
  the answer a metric can use. Every intake path already wrote its own free-text string
  (`"instantly (replied)"`, `"sadie intent (reddit)"`, `"audit intake form"`), so the only way to ask
  the question was prefix-matching prose — and prefix-matching prose is the exact fragility the
  2026-08-25 metric work was removing. `channelSource` is **recorded** (stamped at intake) ·
  **restated** (a faithful rename of what `source` already said, no judgment added) · **inferred**
  (a judgment — say so, and any metric may exclude it). Nothing in the current data is `inferred`,
  and **`founder-sourced` is deliberately not `warm-network`**: it says who typed the row and claims
  nothing about how the Founder knows them. The channel metrics refuse below **80% coverage** — a channel
  rate computed while most rows carry no channel is a lie with a denominator.
- **`Audit delivered`** *(activity type, added 2026-08-25)* — the report is in the prospect's hands.
  The Audit is the front door of the whole motion and nothing counted one until now, so its
  conversion to an engagement was *unknowable* rather than merely unknown. Bella's owned number.
- **`artifacts[].type`** *(added 2026-08-25)* — from `meta.artifactTypes`. `collateral` is the one
  that matters: it makes "did this one-pager ever reach a buyer" a query (`shown`/`reacted`) instead
  of a memory. `built` deliberately does not count. Pickle's owned number.
- **`Booking`** *(activity type, added 2026-08-25)* — a slot was **booked**, deliberately distinct
  from `Meeting` (one was **held**). `contact.nextMeeting` holds only the *next* one, so without this
  the second booking erases the first and bookings were uncountable the same way stage history was.
  Webb's owned number, and the site's Calendly links now carry `utm_source` so the attribution
  survives the click.
- **`Audit requested`** *(activity type, added 2026-08-25)* — someone asked for the free Audit.
  Separate from `Audit delivered` on purpose: a request that never became an audit is a different
  failure from an audit that never became an engagement.
- **`seqStatus` / `meta.seqStatuses`** *(added 2026-08-25)* — `replied` split into
  **`replied-positive`** and **`replied-negative`**. Until then a reply's *quality* existed only in
  Instantly's database, so "positive reply rate" was not expressible in yourco's own record — and a
  number that disappears with a subscription is not owned. The legacy `replied` is retained, counts
  toward **contacted**, and never toward **positive**: a vocabulary change must not promote old rows
  into wins.
- **`deal.stageHistory`** *(added 2026-08-25)* — see `meta.stageHistoryNote`. Every intake writer
  now starts the clock, checked by `runtime/consistency-check.py`, which found **five** of them
  creating deals on the retired *prospect* rung — removed from the ladder in the
  2026-08-07 restructure.

## Sales process — the stage ladder

**Defined in `data.json` → `stages`. That is the source of truth; this table is a reading of it.**

| # | Stage | Exit criterion |
|---|---|---|
| 1 | `pre-convo` | A real conversation held — business + decision-maker identified |
| 2 | `discovery` | Pain named + data shared + bottleneck quantified in $ |
| 3 | `demo-proposal` | Signed |
| 4 | `signed-onboarding` | Build scoped + access in hand |
| 5 | `build-implementation` | Feature-complete against the scoped modules |
| 6 | `testing` | Eval gate PASS + verified against what we'd actually send |
| 7 | `live` | Terminal — the engagement stays here; a new module is a new deal |
| — | `parked` | Re-open trigger fires |

Closed outcomes: **won / lost / parked** — every `lost` needs a `why` (feeds ICP refinement).

> ⚠️ **This table was wrong on 5 of 7 stages until 2026-08-23.** It read
> *prospect → discovery → proposal → build → live*: `prospect` had become `pre-convo`, `proposal`
> `demo-proposal`, `build` `build-implementation`, and `signed-onboarding`, `testing` and `parked`
> were missing entirely. **That is not a cosmetic drift** — the same rename in August left a stale
> `BENCH_STAGES` in `server.py` and HQ reported **21 deals / $24,000** when the real number was 3.
> `runtime/consistency-check.py` now diffs this table against `data.json` on every run.

### "In motion" means two things, and both surfaces now say which (2026-08-25)

The rename above left one more thing unswept, and it survived twelve days: **`pre-convo` is a
working rung here and a bench in HQ.** So `_motion()` counted 37 deals in motion while
`dashboard/server.py` counted **3** — and the number that reached a triage memo was the CRM's.

Neither definition is wrong for its purpose. The board should show a Pre Convo row, because it is
work you do. The *metric* should not count a deal nobody has spoken to as moving — the stage's own
exit criterion is "a real conversation held."

**What changed is the label, not the behaviour.** No card moved. The Pipeline KPI reads **"Open on
the ladder"** and names HQ's stricter count on the card; the Today card breaks the same total into
*past Pre Convo · Pre Convo · parked*. `runtime/consistency-check.py` now fails if the two
definitions diverge *and* the CRM stops saying so — or if they converge and the note is left behind.

**David owns a number because of this work:** *in-motion deals carrying a next action* (100% today,
3 of 3). Every agent now owns exactly one — `runtime/agent-registry.json` → `agent_metrics`, computed
by `dashboard/northstar.py`, rendered on HQ → Agents. Decision:
`decisions/2026-08-25_one-number-and-agent-metrics.md`.

## Owner: David
David keeps the CRM **clean, current, deduped, and enriched**, and reports the pipeline. See `agents/david/`. He also keeps `clients/_pipeline.md` (the lightweight markdown pipeline the other agents read — Reilly, Jim, Bird, Atlas) **in sync** as the agent-readable mirror; this `crm/` is the rich record + UI.

## Example data
`data.js` ships with example landscaping records (`example:true`) so the dashboard demonstrates well. David clears them on the first real entry — no fabricated pipeline survives contact with real data.

## v3.3 (2026-08-11) — Contacts → Network is now the warm-path MAP
The old Network tab drew the graph's *shape* — 17 people on a ring — which told the Founder nothing he didn't
already know. Rebuilt as a rendering of the router's own model (`warmpath.py`), so the picture and the
Today card can never disagree: **every number on it comes from `/api/insight/warmpath`, none is recomputed
in the browser.**
- **Node size** = the pipeline warming that person unlocks *today* (the counterfactual delta, not centrality).
  The top mover carries a ring. People are ordered by that value from 12 o'clock, so the eye lands on the move.
- **Edge weight + colour** = current warmth after the 120-day decay; **dashed = never touched**, which is a
  data gap and is drawn as one rather than as a confident middle value.
- **Outer boxes** = the company each person routes to. Solid with the money when the CRM row carries a value,
  faint outline when it doesn't — the router can't price what nobody valued, and says so instead of guessing.
- **Click anyone** for their route, warmth, last touch, and what they unlock.
- **"What the map can't route"** names the companies with nobody in the graph at all — *unmapped*, not cold.

Also: a global **+ Add** in the sticky header (Log Activity · Schedule Task · Add Contact · Add Pipeline),
reachable from every tab at any scroll position.

## v3.2 (2026-08-11) — retiring a company (archive, never delete)
`companies[].archived: true` drops a company out of every **active** surface — the table, every company
picker, the hot list, the intro queue, the map, the network, the tab counts, and **both payout paths**
(`buildRepPayouts` and the client-credit calc: a retired company neither earns nor grants). It stays in
`byId`, so a parked or closed deal that points at it still resolves by name. One helper, `liveCos()`,
is the single definition — display and selection go through it; lookup, dedupe and name-matching keep
the full list on purpose.

**Retire, don't delete.** Deleting a company that a closed deal references creates exactly the dangling-
pointer class the Monday watchdog now guards against on contacts. The Companies table shows a
*"Show N retired"* toggle with the reason and date, so retired reads as history rather than as gone.
`dataHealth()` flags the contradiction — a retired company with a deal still on the board.

**First use:** `c17` "Partner B" (a *person* tracked as a company, vertical "Connector") + deal `d17`
"Partner B — connector". Both predate his admission as a 35% partner on 2026-08-10; the deal was
parked into `closed[]` with the reason, the company archived. A partner's standing is the OA, not a
bench referral deal.

## v3.1 (2026-08-11) — next call/meeting on contacts, and people-per-company
- **`contacts.nextMeeting`** — a per-person next call/meeting, set with the **native OS date+time picker** (`<input type="datetime-local">`), never typed. Stored as a local wall-clock string (`2026-08-13T14:30`) on purpose: a meeting is at 2pm wherever both people are, and storing UTC would let the value drift on any re-serialise. `contacts.lastTouch` became a date picker in the same pass — it was a free-text field holding ISO dates.
- **Where it surfaces:** a *Next call / meeting* column on the Contacts table (relative labels — Today 2:30pm · Tomorrow · Thu 2:30pm · Aug 20 — with past in oxblood and inside-36h in solid indigo) · a **Next calls & meetings** card on Today, soonest first, with a separate line for dates that came and went uncleared · the soonest meeting per company on the Companies table.
- **Several people under one company** was always supported by the data model and was never discoverable. Now: the Companies table carries a **People** count (hover for the names) and a **`+`** that opens a new contact **pre-filled with that company**; the Contacts list **sorts by company** and indents a company's second and later people under the first (`↳ same company`). No schema change — this was a UI gap, not a data one.

## v3 (2026-08-07) — the insight layer: seven reads a CRM row can't produce
Seven modules that answer questions the record itself can't. Each is a standalone script (run it, read
the report) **and** a server endpoint (`GET /api/insight/<key>`) the dashboard fetches. All seven refuse to
produce a number they can't defend — that refusal is the design, not a limitation. Decision:
`decisions/2026-08-07_crm-insight-layer.md`. Regression suite: `python3 crm/test_insights.py` (62 assertions,
runs against a copy — never touches the live CRM).

| Module | What it answers | Where it shows |
|---|---|---|
| `ghost.py` | Where every deal would be **today** at your own median velocity, reconstructed from every committed revision of `data.json`; the gap, priced | Pipeline → **Ghost** (scrub bar replays any past board) · report `p-ghost` |
| `adversarial.py` | Two readers, one evidence bundle, opposed priors — the **spread** between them. Prosecution counts only buyer-side action inside a 21-day intent window; defence counts the whole record | board chip · dossier · Today "Contested" · report `p-spread` |
| `calibration.py` | Your **own** forecasting bias, measured: predictions captured at every stage move, graded on resolution, then used to correct the weighted forecast | dossier "Prediction" · Today "Your calibration" · report `p-calib` |
| `warmpath.py` | Which **single** relationship, warmed this week, unlocks the most pipeline — a counterfactual re-solve of the whole network, not a centrality score | Today "Warm one relationship" · report `p-warm` |
| `promises.py` | Sold-vs-delivered drift as **promise debt**; scanner proposes candidates from activities + client docs, a human accepts | dossier · Today · client console · report `p-promise` |
| `mirror.py` | The **buyer's** ladder beside ours, and where our stage assumes a step they haven't cleared (**overreach**) | Pipeline → **Mirror** · board chip · dossier · report `p-mirror` |
| `autonomy.py` | What share of **pipeline-moving** work ran without you, and what each CRM action needs to climb its rung | header metric (click for the ladder) · report `p-auto` |
| `mirror_close.py` | The **buyer-facing** rendering of `mirror.py` — their ladder plus *where we got ahead of them*, handed over unedited. Same `compute()`, second person, and it names our own exposure when a `cost.md` ledger exists against an unsigned deal. **Refuses on an unmapped deal.** | `--deal <id\|name>` → text or `--html`; not a UI surface — a document a human hands over. Offering: `offerings/mirror-close/SPEC.md` |
| `wager.py` | The **calibration wager** — ten predictions the owner makes about their own business, settled at 90 days against their records, with the systematic lean (optimistic/pessimistic) computed. Append-only at `_wagers.jsonl`. **Won't settle early; reports unmeasured as unmeasured, never wrong.** | `--questions` · `--open` · `--measure` · `--settle`. Offering: `offerings/calibration-wager/SPEC.md` |

**Honesty rules these share.** The ghost prices a deal only when every rung on its path has ≥3 measured
occupancies — otherwise it shows the position and says the cost is not claimed. Calibration applies no bias
correction below 5 resolved predictions in a segment. The mirror never infers a buyer step from our own stage.
Promises enter the ledger only when a human accepts them. The autonomy dial measures; Kolby evals; the Founder promotes.

**Refreshed by** `runtime/deal_agents.py` (already on the runtime): it now also runs the adversarial reads and
exports the promise ledger to each client folder. The ghost is computed on demand and cached against the
`data.json` HEAD sha (`crm/_ghost-cache.json` <!--#planned-->, gitignored).

**Read-only mode.** `index.html` opened as a file has no backend, so every insight panel shows a note instead of
a number. The spread is the exception — `adversarial.py` mirrors a compact copy onto `deals[].spread`, so the
board chip survives.

## v2.1 (2026-08-07) — the working-pipeline release
- **Tabs:** Today · Pipeline · **Contacts** (client people, with People | Companies | Network toggle) · **Internal** (the team: advisors/connectors + the Referrals cockpit) · **Reporting** · More (map, activity, tasks).
- **Pipeline** is a HubSpot-style board on the real ladder (Pre Convo → Discovery → Demo and Proposal → Signed & Onboarding → Build & Implementation → Testing → **Live**, plus Parked). **Live is terminal** — an expansion is a NEW DEAL on the same company, opened at Demo and Proposal via **+ Expansion** on the client card and carrying `expansionOf`. `expand` was a rung until 2026-08-13; its exit was *"loops back to Demo and Proposal"*, i.e. a cycle in a one-way ladder, which polluted every velocity and conversion number and forced every "is this a paying client" read to say `live OR expand`. `decisions/2026-08-13_live-terminal-expansion-is-a-deal.md`.): drag a card between columns or hit ► to advance; every move confirms the exit criteria, stamps stageSince/lastTouch, asks for the new next action, and logs a stage activity. Column headers show count + $ total + the exit.
- **Reporting** = 10 preset reports (pipeline value, funnel + time-in-stage, the bench, activity volume, artifact heat, proof ledger, source performance, warm-network coverage, deal-agent activity, weighted forecast) + a custom builder (dataset × group-by × metric × stage filter) with saved reports persisted in data.json → `reports`.
- Under the hood (v2, same day): stage ladder w/ exit/staleDays/owner in `stages`; deals carry `artifacts` (built→shown→reacted), `twin`, `nextDraft`, `agentLog`, `heatNote`; `graph.edges` = the family graph; `dispatch` = agent build queue; POST `/t` + GET `/api/heat` = artifact telemetry; `runtime/deal_agents.py` + `runtime/prompts/deal-agent.md` = one micro-agent per deal (draft-only, forever).
