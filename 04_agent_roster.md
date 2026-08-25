# YourCo Agent Roster & Org Chart

> ⚠️ **Nothing in this roster exists yet.** This is the cast the source company built, kept as a
> starting shape. Every agent is marked `☐ not built` — decide which you actually need, delete
> the rest, and wire the ones you keep per `runtime/agent-wiring-checklist.md`.


The authoritative list of YourCo's digital employees — live, planned, and under consideration. Every session should boot knowing who exists, what each one does, how it's triggered, and what has to be true before the next one gets built. Keep this current: when an agent is created, promoted, or retired, edit this file.

> **Syncing an agent's docs to the always-on runtime:** one source of truth — this git repo. Edit a doc/prompt locally → **commit → push**; the VPS git-syncs it on its next run (no separate "cloud" edit). Only *behavior* changes that live outside git need a host touch: the approval gate (`~/.claude/settings.json`) and systemd timers. Full mechanics: `runtime/README.md` → "Updating an agent's docs/prompts."

## Operating model (read first)
- **Siblings, the Founder conducts.** Agents do not direct each other. the Founder triggers them and approves gated actions. (Decision: `decisions/2026-06-07_agent-operating-model.md`.)
- **Melanie is the CEO-conductor — in training, target = oversight of all agents + all areas.** The org is built around **one** orchestration layer (Melanie over a thin Atlas), **not** per-area manager agents (`decisions/2026-06-15_flat-roster-one-orchestration-layer.md`). Today she proposes / the Founder decides / agents follow the Founder; her oversight ratchets open as her calls prove aligned. Charter: `agents/melanie/_README.md`.
- **Atlas observes, never commands.** Atlas is the analytics/monitoring + reporting layer, not an orchestrator — yet. It is elevated to a thin orchestrator (the substrate under Melanie) only when the revisit condition below is met.
- **Prove the unit before adding the next.** New agents are built when there's a real trigger (a near deal, a first hire, a live client), not preemptively. Adding unproven agents is the "shiny tools" trap.
- **Lean roster.** Capabilities fold into an existing agent unless they need a distinct tool stack *and* a distinct eval bar. Research → inside Reilly. Analytics/monitoring → inside Atlas. Orchestration → Atlas's future role, not a new agent.
- **Every agent gets:** a real name + email, its own `agents/<name>/` workspace (discovery/build/eval), eval gates, an approval pattern, and a closed-loop feedback step. *(Moved out of `clients/` on 2026-08-07 — `clients/` holds clients only.)*

## Org chart (current)
```
                              FOUNDER  (founder / conductor / approver)
                                │  triggers + approves
   ┌──────────┬──────────┬──────┴───┬──────────┬──────────┬──────────┐
ATLAS      REILLY ──►  PARTNER_BON     LUKA       POLO       CHARLES    WEBB
ops /      sales /     video       brand      pricing    finance    site /
monitor    outbound    demos       custodian  strategist            publish
           │              │           │
           │ requests     │ feeds     │ reviews every external
           │ video for    │ end-frame │ asset before publish
           │ Email 2      │ to Webb's │ (Reed videos, Reilly
           │              │ landing   │ campaigns, Katie posts,
           │              │ pages     │ Webb pages, Pickle collateral)
           │              ▼
           └──── Webb embeds Reed videos on site
                 Webb builds per-vertical pages when Polo locks pricing
                 Webb publishes Katie's editorial to the SITE; Katie posts to SOCIAL
                 Katie scripts → Reed produces → Katie posts (social) / Webb publishes (site)
                 Kemba owns web infra (hosting/DNS/uptime); Webb owns the pages
                 Michelle writes the outbound copy; Reilly sources + runs the campaign

ATLAS ◄── observes & reports on all agents (no command authority)

Shared substrate (not an agent): Memory & Context Layer →
  CLAUDE.md · workspace files · crm/data.json (source of truth) · finance ledgers ·
  Reed _asset_registry.md · Reilly _suppression.md · Webb pages/ ·
  learnings/ (continuous-improvement substrate) · crm/ (David) · memory/
```

## Internal vs client — the distinction the roster used to blur (added 2026-08-09)

**There are two separate agent populations, and only one of them is on this page.**

1. **This roster (27 agents) is yourco's own internal company.** It is how a solo founder runs a
   business without headcount. **None of these agents is ever deployed into a client's tenant.**
2. **What a client buys is a bespoke OS** assembled from the 8 functional pillars in
   `processes/ai-os-modules.md` — Intake · Sales · Marketing · Customer · Operations · Back Office ·
   Company Brain · People/Training. Bella's audit decides *which* pillars and in what *sequence*;
   Kimi builds them, fit to that business. A client never meets "Reed" — they get *their* content
   agent, built for them.

Each row below is tagged:

| Tag | Meaning |
|---|---|
| 🏠 **internal** | Runs yourco the business. No client-facing role. |
| 🤝 **client-touching** | An **yourco** agent that works *on* a client account during delivery (audit, onboarding, build, health, expansion). Still yourco's agent — never handed over. Each carries a "client-facing = must-approve" gate. |
| 🏠🤝 **both → Pillar N** | Internal today, **and** the dogfooded template for that client-side pillar. This is the stated strategy: run it on yourco first, productize it second — which is also what makes the pitch honest ("we run our own company on this"). |

**Kolby is the special case:** he isn't a pillar. He's the **cross-cutting moat layer** — eval, approval
gates, observability — that *every* engagement inherits regardless of which pillars it buys. That layer
is the differentiator, not a module anyone selects.

**The counts today:** 16 internal · 4 client-touching · 7 both. Note that 5 of the 27 have never
produced an artifact and 6 are trigger-gated dormant — the audit
(`loops/_audit/2026-08-09_full-business-audit.md`) recommends merging roughly a third of them.

## What number each agent owns (added 2026-08-25)

Until now this roster said what every agent *does* and never what it *moves*. Twenty-seven agents,
zero numbers owned — the gap three separate inputs pointed at on the same day
(`loops/_triage/2026-08-24_frameworks-kpis-batch.md`).

**Every agent now owns exactly one number**, declared in `runtime/agent-registry.json` →
`agent_metrics.agents` and computed live by `dashboard/northstar.py` (HQ → **Agents**). The
definitions live in Rafi's sanctioned registry deliberately: a number an agent owns is not something
that should be quietly editable, and the governance watchdog sees a change to it as drift.

Four rules, and they are the reason the list is mostly blank today:

1. **Every agent in `agents/` must have one.** `runtime/consistency-check.py` fails otherwise — an
   agent cannot be added without someone answering what it moves.
2. **Did-it-run is not a number.** Only Atlas may own loop liveness, because liveness *is* its job.
   Everywhere else, an activity count was rejected in favour of an outcome that is currently
   unmeasurable — *Reports Outcomes, Not Activity*.
3. **An unmeasured metric must name its gap.** No value and no `needs` is a wish, not a metric.
4. **It ladders `direct` or `enabling`.** There is no third value, because an agent whose number does
   neither is a retirement question (→ `dashboard/vacancies.py`).

**Where that leaves us: 15 of 27 agents own a number the OS computes today, 12 await a real-world
event, and none is unmeasured.** Every agent has an instrument. What remains is not engineering —
4 need client #1, 3 need a first business event, 3 need the launch gate, 1 needs a host install, and
1 needs a monthly loop to run once. The clustering is the useful output; a list of
14 metrics is a project nobody starts.

The **seven blocked by prose were closed on 2026-08-25** (`dashboard/loop_metrics.py`). Three turned
out to be *derived* — the number was a fact about files that already existed and no metric had
pointed at it. Four are *extracted* from SOP-mandated structures in the artifact each loop already
writes, which made three SOPs into contracts: **if your SOP names a structure your number is read
from, keep its shape exactly, and write the honest figure including zero.** A structure that does not
parse reports a parse failure, never a zero.

The **five blocked by a missing CRM field were closed the same day** (`dashboard/crm_metrics.py`) —
and re-diagnosed three of the five. Jim's number was already in his own queue; Sadie's promotion path
has stamped its own source since July, so her zero is real; Katie's real blocker is the gate, not the
schema. The CRM gained a controlled `channel` vocabulary, an `Audit delivered` activity type and a
`collateral` artifact type. **The pattern by now: the useful output of naming a gap is finding out it
was the wrong gap.**

The **six waiting on client #1** closed last (`dashboard/client_metrics.py`), and no amount of
building produces a customer — but **three of the six would not have computed even after one
arrived.** `deal.stageSince` holds only the current stage, so every prior transition date was being
overwritten and nothing else recorded it; `deal.stageHistory` now appends on every move. Reed was
re-scoped off "appeared in a *won* deal" — a production agent graded on whether the founder closes —
onto reach. And Polo needed no customer at all: the only price ever quoted sits **below every locked
band**, which is exactly what his number exists to catch.

**Kemba's uptime was built last** (`runtime/heartbeat.sh` → `dashboard/uptime.py`), and it is the one
instrument that measures its own absence: a log can only record what happened while the box was
working, so availability is **beats received ÷ beats expected** and a missing line *is* the outage.
It reads `unmeasured` until the timer is enabled on the VPS — a host action, not a build.

**The gate-blocked pair went last** (`dashboard/gate_metrics.py`), and instrumenting them surfaced
the worst defect of the sweep: **`prospect` was retired from the ladder on 2026-08-07 and five intake
writers never swept it** — including `site_intake.py`, the audit form, which would have created every
lead through the front door of the entire motion on a rung that no longer exists. The invariant found
it within a minute of existing.

**The first-event three could not be closed by building** — no audit has been delivered and no asset
has been shown, and I checked whether either had already happened unrecorded (it had not; Parker
Realty's audit report is still the shipped sample). What was fixed is the two reasons they would stay
blank anyway: the **recording step now lives in the SOP that governs the doing**, and the Board now
**states the absence out loud** — 11 produced assets, not one registered on a deal, with 3 deals in
motion to have shown them in. A metric reading blank is invisible; a Board row is not.

**The apex they ladder to is `liveClients`**, declared in `dashboard/goals.json` → `northstar`. It is
the Founder's to set and Melanie may propose but never adopt a change to it.

## Current agents (live / in build)

| Name | Role | Trigger | Scope (owns) | Hard approval gate | Status |
|------|------|---------|--------------|--------------------|--------|
| **Atlas**<br/>🏠 **internal** | Ops / Analytics / Monitoring | Scheduled (Mon 7:30 ET) + continuous watch | Agent health, eval status, watchdog signals, per-engagement cost rollup, cross-cutting signals; Monday Briefing as the surface | Never sends external; never directs agents; touching client tenant = must-approve | **Live (v0)** — first briefing 2026-06-08 |
| **Reilly**<br/>🏠 **internal** | Sales / Outbound Ops (SDR — sourcing + campaign-ops) | the Founder names a vertical | Source (Outscraper/Vibe/SuperSearch → `runtime/sourcing.py`) → enrich → ICP/dedup/deliverability → create + stage the Instantly campaign (`runtime/instantly.py`) → reply/bounce feedback → CRM promotion (`runtime/promote.py`). Owns the suppression list + the outbound *machine*. **Copy/messaging → Michelle** (split 2026-06-15) | **No send without the Founder's batch approval**; never from primary domain | **Active (v0)** — landscaping locked; Vibe + Instantly connected; 20-lead batch sourced + campaign staged 2026-06-09; gated on warmup (~June 22) + 10DLC + batch approval |
| **Bella**<br/>🤝 **client-touching** | Audit Lead (free diagnostic front door — 2026-08-16) | A cold/skeptical prospect opts into the Audit (intake form) / the Founder assigns | Runs the AI Audit end-to-end: review intake → diagnostic-call structure → 4-axis bottleneck scoring (Money × Frequency × Owner-drain × Fixability) → dollar-quantify #1 → map to recommended agents → produce the Audit Report → hand the converted engagement to Kimi. Owns `processes/audit-sop.md` + `clients/_yourco-template/audit-report/` | Report = drafts; **the Founder approves before send**; no fabricated numbers; honest-no-sell; never quotes unlocked pricing (Polo's) | **Built — full Audit runbook + eval 2026-06-25** (`agents/bella/`); live at website launch |
| **Michelle**<br/>🏠 **internal** | Outbound Copy / Messaging | Reilly (or the Founder) needs sequence/campaign copy for a vertical | Authors the cold-outbound messaging — the multi-touch sequence copy + subject/angle variants per vertical, applying `brand/writing-rules.md`; owns the copy methodology (`agents/reilly/copy-structure.md`), `processes/outbound/sequence-copy.md`, and the messaging in `industry-campaigns.md` / `proof-led-outbound-engine.md`. Demo-led, never pitch; pricing pulled from cold copy. Eval bar: positive-reply rate + brand/claims | Drafts only — **Luka brand + Polo claims/pricing + the Founder approval before any send**; never sends from any domain | **Built — full copy SOP + eval 2026-06-25** (`agents/michelle/`); methodology + copy hers (authored under Reilly) |
| **Reed**<br/>🏠🤝 **both** → Pillar 3 (Marketing) | Content Production (all formats) | Asset request (Reilly/Katie/the Founder), per vertical/use-case | **Produces ALL content assets from Katie's scripts** — video (**animated scenes Higgsfield → AI voiceover + assembly + captions Descript**) AND rendered social visuals (carousels, Shorts covers). Registers each asset; full video + GIF preview for email embed. *Katie scripts + posts; Reed produces.* SOP: `processes/Reed-video-production.md` | **No publish without the Founder's approval**; animated GIF preview + link OK (image, not embedded video) | **Live (v0)** — first demo shipped + the Founder-approved 2026-06-09 (landscaping intake) via the Higgsfield + Descript pipeline. Animated-only stack (supersedes Canva). Production scope broadened to all content assets 2026-06-15. One open automation gap: AI-voice render still manual (see SOP) |
| **Charles**<br/>🏠🤝 **both** → Pillar 6 (Back Office) | Finance | Scheduled (Mon AM) + monthly close | Ledgers (system of record), finance pulse, cash/MRR/burn/runway, gap detection, monthly close + readout, tax-prep handoff, per-client cost-ledger roll-up (`log-build-cost`) | Reports/drafts only; **any invoice/payment/filing = must-approve** | **☐ not built** — weekly finance pulse runs on the runtime (`loops/finance/`, latest 2026-07-06); monthly close armed (`yourco-finance-close.timer`) |
| **Brett**<br/>🏠 **internal** | Advisor | Monthly (1st) + on-demand | Strategic advisory: moat status, competitive/landscape scan, ranked recommendations, drift detection | Advisory only — reads/researches/recommends; takes no other action | **☐ not built** — monthly advisor memo (`loops/advisor/`, 2026-07-01) + weekly ideas loop (`loops/brett-ideas/`) run on the runtime |
| **Katie**<br/>🏠🤝 **both** → Pillar 3 (Marketing) | Content / Social (scripting + distribution) | Scheduled (Fri AM) + per-channel cadence | **Scripts** all content (written thought-leadership for LinkedIn/X/newsletter, carousel slide copy, video hooks/scripts, event-blast copy) applying `brand/writing-rules.md`, anchored on thesis/moat → hands scripts to **Reed to produce** → **Katie posts/distributes to the social platforms** (LinkedIn/X/IG/FB/YouTube). Owns the social distribution channel; seeds inbound. *(Production of assets = Reed; site publishing = Webb.)* | Drafts only; **external publishing/posting = must-approve** | **☐ not built (drafting)** — weekly content loop runs Fri on the runtime (`loops/content/`, latest 2026-07-03); actual posting stays launch-gated |
| **Mario**<br/>🏠 **internal** | Answer-Engine Visibility (AEO/GEO) | Monthly (1st Tue, 8am ET) once live; on-demand pre-launch | yourco's presence in AI answers (ChatGPT/Claude/Gemini/Perplexity/AI Overviews): the target query set, the citation audit, the cited-set + source map, interventions by leverage, a citation-presence score. Prescribes content (→ Katie) + schema (→ Webb). SOP: `processes/loops/aeo-geo.md` | Prescribes/drafts only — **never publishes**; external content + schema ship via Katie/Webb + the Founder approval | **☐ not built 2026-07-06** — timer installed (monthly, 1st Tue 08:00 ET) + first runtime run completed same day (`loops/aeo-geo/2026-07-06.md`; flagged the closing "operated" wedge). History: the units sat never-installed on the host since June (loop silently dead after 06-14); watchdog row added so it can't die invisibly again |
| **Luka**<br/>🏠 **internal** | Brand Custodian | On-demand + monthly (1st Mon AM) | Brand guidelines (visual/voice/tone rules); on-demand "ship / ship-with-fixes / rework" reviews; monthly drift audit; brand changelog | Reviews only — never publishes; **guideline changes = in-loop**; customer-facing = must-approve | **☐ not built** — monthly brand audit runs on the runtime (`loops/brand-audit/`, first run 2026-07-06); guidelines + `brand/DESIGN.md` live |
| **Polo**<br/>🏠 **internal** | Pricing Strategist | On-demand (per-vertical build) + quarterly (1st Mon of quarter, 8:30am ET) | Per-vertical pricing research and proposals; `/pricing/v0/<vertical>.md` canonical references; quarterly pricing review against close-rate/retention/margin data; Reilly's pre-campaign pricing gate | Proposes only — **vertical pricing locks require the Founder approval**; one-off prospect pricing = must-approve; external pricing communication = must-approve | **☐ not built** — quarterly pricing review runs on the runtime (`loops/pricing-review/`, 2026-Q3 done 2026-07-06); `/pricing/v0/` live |
| **Melanie**<br/>🏠 **internal** | Conductor / HQ interface ("CEO in training") | Always-on (HQ + CRM) + weekday 07:45 briefing + **weekday 08:45 initiative loop** | The HQ dashboard voice/interface, the CRM shared brain (`dashboard/melanie.py` — locks, atomic writes, enrich, citations), the weekday morning briefing to Slack, and **the entity-level initiative loop** — originates up to 3 unscheduled moves/day from goals+state+learnings, acts within tier, escalates the rest (`decisions/2026-07-08_melanie-initiative-loop.md`) | Drafts/reads only; no external sends; **may propose missions, never self-adopt them — goals.json is the Founder's**; no command channel (conductor, not commanded) | **☐ not built** — HQ + CRM brain in daily use; briefing live; initiative loop staged 2026-07-08 (timer install pending) |
| **David**<br/>🏠🤝 **both** → Pillar 2 (Sales/Revenue) | CRM / RevOps | Scheduled (weekdays 08:05 hygiene + 08:15 autolog on the runtime; Granola sync 5×/day on the Mac) + on-demand | Owns `crm/` (companies, contacts, deals, activities, Referrals view), the hygiene automations (auto next-step, stale digest, closed-won ping), Gmail/Calendar autolog → pending, Granola meeting sync | Pending-activity **confirm in the CRM UI is the approval gate**; meeting-derived stage/value changes = suggest-only | **☐ not built 2026-07-06** — timers armed on the runtime (first fires 2026-07-07); granola-crm-sync scheduled task live |
| **Sadie**<br/>🏠 **internal** | Intent / Social listening | Scheduled (daily 09:30 ET) | Daily intent sweep — YouTube comments + Bluesky + Reddit buying signals across target verticals → `loops/sadie/`; feeds the CRM Hot List two ways (wired 2026-07-20, `runtime/promote_intent.py`): signals matching existing CRM companies **auto-attach** as Hot List pills; unmatched prospect-grade signals promote to real rows only via the human-gated `promote-intent-signal` skill (identity + vendor check — never auto-create) | Read-only listening — surfacing only; turning a signal into outreach is Reilly's gated step | **☐ not built** — daily `yourco-sadie-intent.timer` on the runtime (`loops/sadie/`, latest 2026-07-06) |
| **Webb**<br/>🏠 **internal** | Web Operations / Site Custodian (content + conversion) | New vertical locked (build vertical page) / Katie publishes (Webb publishes to site) / new campaign needs landing page / monthly site review | `yourco.com` + `getteamyourco.com` + all marketing/landing pages (build + on-page); site SEO + analytics; Calendly booking flow; per-vertical landing pages; publishing Katie's editorial content **to the site**. **Infra (hosting / DNS / uptime / domains) → Kemba** — Webb owns the pages, not the plumbing | Drafts only — **publish requires the Founder approval**; tracking scripts = in-loop; any spend > $1 = in-loop | **Active (v0)** — v0 cold landing page BUILT 2026-06-09 (`agents/webb/pages/v0-landing/index.html`, CTAs → `getteamyourco.com` confirmed); pending deploy + `/book` redirect + Luka review + the Founder approval; operating docs (discovery/build/eval) completed 2026-06-25 |

## Planned agents (named, not yet built)
Order = recommended build sequence, but each is gated on its trigger. The roster is a **map, not a build queue** — most are trigger-gated and stay unbuilt until their trigger fires.

**Deep-built 2026-06-25 (activation-ready, still trigger-gated):** Janice, Kimi, Kortney, Bird, Harry, and Kori now have full docs (discovery/build/eval) in their `agents/<name>/` folders — dormant until their trigger fires, but they activate without a rebuild. Detail: `decisions/2026-06-25_agent-roster-deep-build.md`.

| Name | Role | Build when (trigger / gate) | Scope (owns) | Notes |
|------|------|------------------------------|--------------|-------|
| **Kolby**<br/>🏠🤝 **both** → the cross-cutting moat layer every engagement inherits | QA / Eval Agent | **✅ LIVE** (trigger fired — the weekly eval-review loop runs on the runtime: `runtime/prompts/eval-review.md`, artifacts `loops/eval-review/`; + owns the **outbound pre-send eval gate**, 2026-07-05: `runtime/instantly.py --eval-batch`; + demo/video credibility evals) | Independently runs the eval harnesses *across* all agents, scores outputs, flags drift/regressions, maintains the test sets | Reports only — the moat's internal auditor |
| **Pickle**<br/>🏠 **internal** | Marketing Artifacts Agent | When there's a win to write up or sales collateral is needed (vertical one-pagers usable pre-revenue) | Designed static collateral: case studies, one-pagers, pitch decks, battlecards, visuals/infographics | Publish/external use = must-approve. Distinct output from Reed (video) and Katie (editorial posts) |
| **Jim**<br/>🏠 **internal** | Chief of Staff / Scheduling Agent | **✅ LIVE** (trigger fired — weekday open-loops chaser + daily inbox-triage run on the runtime: `loops/open-loops/`, `loops/inbox-triage/`; calendar holds via the Slack command surface) | Manage the Founder's calendar, book/reschedule the calls other agents surface, inbox triage, meeting prep, the Needs-the Founder queue (feeds the HQ tile) | External invites = in-loop. Jim = the Founder's time; Harry = back-office admin; Atlas = agent-ops monitoring |
| **Ray**<br/>🏠 **internal** | Legal / Contracts Agent | When the first contract (NDA/MSA/SOW) is in flight | Review contracts, plain-English redlines, risk flags, draft standard agreements | Advisory redlines; **signing/sending = must-approve**. Clusters with the first deal |
| **Janice**<br/>🤝 **client-touching** | Onboarding Agent | Activates on first signed client | Onboard new clients: intake requirements/credentials, provision tenant access + mailboxes, stand up the engagement folder, kick off | **Built 2026-06-11** (`agents/janice/`, generalized any-vertical/type). Hands off to Kimi. Tenant access = must-approve. the Founder holds until first engagement hardens it. |
| **Kimi**<br/>🤝 **client-touching** | Delivery Agent | Activates when a deal nears close (core product) | Runs the engagement: discovery → 48h build → go-live → weekly iteration; overlay on `yourco-template`, any vertical/employee type. Playbook: `processes/discovery-to-48h-build.md` | **Built 2026-06-11** (`agents/kimi/`, generalized). **The thing YourCo sells.** Receives the handoff from Janice. Client tenant = must-approve. the Founder holds until first engagement hardens it. |
| **Kemba**<br/>🏠 **internal** | Platform / Template Engineer Agent (all infrastructure) | After the first 1–2 engagements produce patterns to extract | Owns `yourco-template` (golden template) **+ the always-on runtime / agent execution environment** (the substrate every agent runs on): extract reusable patterns, maintain eval/watchdog/approval scaffolding, own the headless runtime migration. **+ web infrastructure (hosting, DNS, uptime/monitoring, domains) — handed off from Webb 2026-06-15: infra is infra.** Webb owns the pages; Kemba owns the plumbing they run on | Kemba *builds* the template + runtime; Kimi *uses* it per client. **DNS / hosting / domain changes = must-approve.** Runtime plan: `/decisions/2026-06-09_always-on-runtime.md` (the Founder holds until Kemba is built). Template changes versioned + logged in `decisions/`. **Agent Factory SOP deep-built 2026-06-25** (`agents/kemba/`) — the governed pipeline to build other internal agents (decide-if · when · research → scaffold → eval → register → wire), propose-and-scaffold under the Founder + Rafi + Kolby gates |
| **Rafi**<br/>🏠 **internal** | Compliance Agent | **✅ LIVE** (trigger fired — owns the weekly agent-registry governance watchdog on the runtime, Mon 07:45: `loops/_governance/`; full compliance scope still activates with client data / procurement asks) | Regulatory + security compliance: control tracking, audit readiness, data-handling/privacy posture, policy upkeep across YourCo and client engagements. **Owns the agent registry + reconciliation watchdog** (the "Vanta for our own agents": `runtime/agent-registry.json` + `agent-registry-check.py` — drift detection vs the sanctioned baseline, surfaced in the Monday briefing; `decisions/2026-06-22_agent-registry-governance-watchdog.md`) | Flags/reports only — remediation is the Founder's call. Distinct from Ray (legal agreements) and Kolby (agent-output quality) |
| **Kortney**<br/>🤝🏠 **client-touching + both** → Pillar 4 (Customer/Retention) | Customer Health / Support Agent | Activates on first live client | Friction signals in live engagements, support triage, engagement-health watchdog | **Built 2026-06-11** (`agents/kortney/`, generalized any-vertical/type — per-type health model). Maps to the Wednesday customer-health loop (wired). Green light triggers Bird. Client-facing = must-approve. |
| **Bird**<br/>🤝 **client-touching** | Expansion / Account Growth Agent **+ the connector program** (incl. **connector coaching** — `crm/coach.py`, skill `run-coaching-session`) | Activates on Kortney's first green light **— or on the first connector onboarding, whichever comes first** | Find + scope the 2nd/3rd use case inside live accounts; renewals and upsell — land-and-expand revenue. **Plus the connector program: terms, enablement, deal registration, growth, and the 24–48h submission verification queue** (`processes/partnerships/connector-console/` `/verify`) | **Built 2026-06-11** (`agents/bird/`, generalized). Pairs with Kortney; scopes → Kimi builds. Client-facing comms = must-approve; Polo-locked prices only. **Connector scope widened 2026-08-11** (`decisions/2026-08-11_connector-program-v2.md`): connectors are now yourco's **primary growth lever**, and the verification queue is a **promised SLA to someone waiting to be paid** — not a background chore. Kori owns connector people-ops, Ray the papers, Charles the payouts. |
| **Harry**<br/>🏠🤝 **both** → Pillar 6 (Back Office) | Back-office Agent | Activates post-revenue (first invoice) | Back-office execution: invoicing/AR, bookkeeping data entry, vendor/subscription admin, scheduling, document filing | **Built 2026-06-11** (`agents/harry/`, generalized any-engagement). Charles = reporting/close; Harry = transactional execution. Payments/invoices sent = must-approve. |
| **Kori**<br/>🏠 **internal** | Internal **People** Manager (employees **+ contract partners**; owns **advisor coaching** — `crm/coach.py`, skill `run-coaching-session`) | **Whichever comes first: yourco's first human hire OR the first connector onboarding** (broadened 2026-08-07) | Onboard/manage the internal team, coordinate human+agent workflows, HR ops, recruiting — **and connector people-ops: onboarding, provisioning (yourco email/Slack/console login), training progression, the ongoing people relationship** (`processes/partnerships/connector-onboarding.md`) | **Connectors are independent contractors, treated like team** (the Founder 2026-08-07) — Kori runs people-ops for them but the contractor line is preserved in every document; **Bird keeps the program** (terms, enablement, deal-reg, growth), Ray the papers, Charles the payouts. The role is named *People* Manager, not *Employee* Manager, deliberately: an internal doc reading "the Employee Manager owns our contractors" is exactly the sentence a reclassification claim would enjoy |

## Capability boundaries to keep clean
- **Bella → Janice → Kimi:** **Bella diagnoses** (the Audit — finds + quantifies the bottleneck, recommends the first build); a converted Audit's findings *are* the discovery doc → **Janice** onboards/provisions → **Kimi** builds. Bella vs Brett: Bella diagnoses a *client's* constraints; Brett advises *yourco's own* strategy.
- **Janice → Kimi:** Janice onboards and provisions; Kimi builds and iterates. The signed-deal handoff is the seam.
- **Charles vs Harry:** Charles reports and decides (statements, close, runway, strategy); Harry executes the transactional admin (send invoices, log entries, file docs).
- **Reed vs Katie vs Pickle vs Luka vs Webb (the content function-split, 2026-06-15):** the line is now **function, not format**. **Katie = scripting + social distribution** — she writes all the copy/scripts (editorial, carousel slide copy, video hooks, event-blast copy) and **posts to the social platforms** (LinkedIn/X/IG/FB/YouTube). **Reed = all content production** — he renders every asset from Katie's scripts (video AND social visuals: carousels, Shorts). **Webb = the live web surfaces** (site, landing pages) — publishes editorial *to the site*, not to social. **Pickle (when built) = designed static *sales collateral*** (case studies, one-pagers, decks, battlecards) — a distinct, positioning-driven discipline, not the social content engine; if its rendering should fold into Reed too, that's the Founder's call. **Luka = the rules everyone writes/produces within** (visual brand, voice, tone) — reviews, never authors; voice-rule conflicts go to the Founder. The chain: **Katie scripts → Reed produces → Katie posts (social) / Webb publishes (site)**, all under Luka's rules + the Founder's approval.
- **Webb vs Kemba (infra, 2026-06-15):** **Webb owns the pages** (build, content, on-page SEO, conversion, publishing); **Kemba owns the plumbing** they run on (hosting, DNS, uptime/monitoring, domains). Webb is a conversion craftsman, not a sysadmin — infra is infra, and it lives with the platform/runtime owner. DNS/hosting/domain changes = Kemba + must-approve.
- **Polo vs Charles vs Brett vs Reilly:** Polo = decides what to *charge* per vertical (research → propose → approve → lock); Charles = reports the math (revenue, costs, margin, retention); Brett = strategic advisory across all domains; Reilly = USES locked prices, cannot quote unlocked verticals. Pricing problem vs. ops problem (when margin slips) → Polo + the Founder decide. Strategic pricing questions (e.g., "should we ever do outcome-based?") escalate to Brett's monthly memo. **Reilly's pre-campaign gate: every new vertical requires Polo's locked pricing before Reilly's first send.**
- **Reilly vs Michelle (the outbound split, 2026-06-15):** **Reilly = the machine** — sourcing, enrichment, ICP/dedup/deliverability, campaign create/stage/ops, reply/bounce feedback, suppression. **Michelle = the message** — the cold-sequence copy, subject/angle variants, the demo-led narrative, applying writing-rules. Reilly runs the campaign; Michelle writes what it says. Reilly hands Michelle the vertical + target research → Michelle writes → Reilly stages it (paused) in Instantly. Different eval bars: Reilly's = deliverability/list-quality; Michelle's = positive-reply rate + brand/claims.
- **Michelle vs Katie (two writers, different surfaces):** both write applying `brand/writing-rules.md`, but **Michelle = cold outbound** (1:1 sequence copy that earns a reply) and **Katie = owned/social** (thought-leadership + posts that compound authority). Outbound persuasion vs. inbound authority — distinct crafts, distinct eval bars.
- **Bird vs Kortney vs Reilly:** Bird = grow live accounts (new use cases, upsell, renewal); Kortney = keep live accounts healthy (friction/support); Reilly = win new logos.
- **Jim vs Harry vs Atlas:** Jim = the Founder's calendar/meetings/inbox; Harry = back-office transactions/admin; Atlas = agent-ops monitoring.
- **Kemba vs Kimi:** Kemba *builds* the golden template (pattern extraction, upkeep); Kimi *uses* it to deliver each engagement.
- **Ray vs Rafi vs Kolby:** Ray = legal agreements/contracts; Rafi = regulatory & security compliance (SOC 2, GDPR, data handling); Kolby = quality of agent *outputs* (eval). Three different "are we safe?" lenses — legal, regulatory, and quality.
- **Research stays in Reilly; analytics/monitoring stays in Atlas; orchestration is Atlas's future role — not new agents.**
- New capabilities fold into the nearest agent unless they need a *distinct tool stack and a distinct eval bar*.

## Shared infrastructure (not an agent)
**Memory & Context Layer** — the substrate every agent reads/writes: `CLAUDE.md` (always-loaded), the workspace files, **`crm/data.json`** (the pipeline's source of truth — `clients/_pipeline.md` is a read-only *mirror* of it, refreshed by the pipeline-report loop; never edit the mirror), the finance ledgers, Reed's `_asset_registry.md`, Reilly's `_suppression.md`, the **`/learnings/` substrate** (operational patterns agents read/write to improve run-over-run — the feed-forward half of the closed loop), the **`/crm/`** CRM (David's system of record for revenue relationships), and the `memory/` dir. Borrowed deliberately from the multi-agent reference pattern. Formalizing this as shared context (vs. each agent keeping private state) is what keeps the roster coherent as it grows. Not a digital employee.

## Revisit condition — when Atlas becomes the orchestrator
Elevate Atlas from observer to a **thin** orchestration + observability layer (dispatch + monitor; never absorb other agents' logic) once **Reilly has run ≥3 clean campaigns AND Reed has shipped ≥1 approved, accurate demo, with both holding their eval targets.** At that point: log a follow-up decision, update Atlas's discovery/roadmap, and redraw this org chart. Until then: siblings, the Founder conducts.

## Expert lineage (who each agent mirrors)
Every built agent is grounded in a real industry authority — the methodology it follows, tied to how YourCo runs (outcomes over features, quiet authority, honesty/no-fabrication, executive trust). Full write-up lives in each agent's `_README.md` ("Lineage" section). Added 2026-06-10.

| Agent | Function | Mirrors |
|---|---|---|
| Atlas | Ops / observability | Charity Majors (observability) + Google SRE |
| Reilly | Outbound sales / SDR ops | Aaron Ross (*Predictable Revenue*) — the outbound machine + specialization |
| Michelle | Outbound copy / messaging | Josh Braun (anti-pitch outbound) + Eddie Shleyner (*VeryGoodCopy* — persuasive microcopy) |
| Bella | Audit / client diagnostic | Eli Goldratt (*The Goal* — Theory of Constraints) + Peter Block (*Flawless Consulting*) |
| Reed | Demo / video | Donald Miller (*StoryBrand*) |
| Charles | Finance / unit economics | David Skok (*For Entrepreneurs*) |
| Brett | Strategic advisor | Richard Rumelt (*Good Strategy/Bad Strategy*) + **Jeff Bezos** (+ named for the Founder's dad; chartered to keep the Founder in line) |
| Katie | Content / editorial | Ann Handley (*Everybody Writes*) + Joe Pulizzi |
| Luka | Brand custodian | Marty Neumeier (*The Brand Gap*, *Zag*) |
| Polo | Pricing | Madhavan Ramanujam (*Monetizing Innovation*) |
| Webb | Web / conversion | Steve Krug (*Don't Make Me Think*) + Joanna Wiebe |
| Ray | Legal / contracts | Kenneth Adams (*Manual of Style for Contract Drafting*) |
| Jim | Chief of staff / inbox | David Allen (*Getting Things Done*) |
| Pickle | Collateral / positioning | April Dunford (*Obviously Awesome*) + Andy Raskin |
| Kolby | QA / eval | Hamel Husain + Shreya Shankar |
| Janice | Onboarding | Lincoln Murphy (customer success) |
| Kimi | Delivery / implementation | Eric Ries (*The Lean Startup*) |
| Rafi | Compliance / security | Ann Cavoukian (*Privacy by Design*) + Bruce Schneier + NIST CSF |
| Kemba | Platform / template | Team Topologies (Skelton & Pais) + golden-path / paved-road |
| Kortney | Customer health | Nick Mehta (Gainsight, *Customer Success*) + Lincoln Murphy |
| Bird | Account expansion | Jason Lemkin (SaaStr) — land-and-expand / NRR |
| Harry | Back-office | Mike Michalowicz (*Clockwork*, *Profit First*) |
| Kori | Internal / people ops | Patty McCord (*Powerful*) + Laszlo Bock (*Work Rules!*) |
| David | CRM / RevOps | Jacco van der Kooij (*Winning by Design*) + RevOps single-source-of-truth |
| Sadie | Intent / social-listening | Marcus Sheridan (*They Ask, You Answer*) + community-led "help first" |
| Melanie Smooter | CEO (in training) | CEO mentor panel — Grove · Horowitz · Collins · Bezos · Nadella · Jobs · Buffett · Nooyi · Blakely · Musk (+ apprentice-alignment to the Founder) |

## Naming convention
Real names, not "Agent 1"; each gets an `@yourco.com` mailbox. The name is part of the executive-trust layer (see `03_internal_platform.md`). Current + planned (27, matching the folders in `agents/`): Atlas, Bella, Bird, Brett, Charles, David, Harry, Janice, Jim, Katie, Kemba, Kimi, Reed, Kolby, Kori, Kortney, Luka, Mario, Melanie, Michelle, Pickle, Polo, Rafi, Ray, Reilly, Sadie, Webb. *(David, Luka, Melanie, Polo and Sadie were missing from this list until 2026-08-23 — all five are in the tables above and have folders; the closing list simply never grew with them.)*
