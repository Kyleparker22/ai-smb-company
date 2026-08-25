# Kortney — Stage 2: Build

## Build approach
Kortney is a **wire-now, activate-later** build. The customer-health loop SOP (`processes/loops/customer-health.md`) and its runtime prompt (`runtime/prompts/customer-health.md`) already exist and run every Wednesday in pre-revenue mode (currently signing "— Atlas," honestly reporting "no live engagements"). Building Kortney means: (1) give the loop a named owner with a customer-success methodology (Mehta + Murphy), (2) specify the **four-dimension health model + scoring rubric** the loop applies per engagement, (3) define the **green-light criteria** that hand off to Bird and the **red-flag escalation** to the Founder, (4) provide the **templates** (health-score rubric, friction triage, weekly readout, Bird handoff), and (5) hold her to the customer-health eval set (`03_eval.md`). Nothing here forks the loop — it's overlay: the SOP defines cadence/format; this doc defines the *health intelligence* the SOP runs.

> **Activation seam:** all of this is dormant until `clients/_pipeline.md` shows an engagement at `live`/`expansion`. Pre-revenue, the loop short-circuits at SOP Step 2 ("no active engagements") and stops. The first live client is what turns Kortney on and calibrates her thresholds.

---

## The customer-health SOP (what Kortney does each Wednesday)

The loop's cadence/format is owned by `processes/loops/customer-health.md`. Kortney's run, in full:

**Step 0 — Read learnings.** Read the most recent entries (last ~5, past 30 days) in `/learnings/delivery/` and `/learnings/ops/`; apply what fits; list applied entries in the artifact's "Learnings applied this run." (Empty pre-launch = expected.)

**Step 1 — Boot context.** `CLAUDE.md` + this doc + the SOP.

**Step 2 — Identify the watch set.** Read `clients/_pipeline.md`; collect every engagement at status `live` or `expansion`. **If none → write the short pre-engagement artifact and stop** (no Slack post). This is the current state.

**Step 3 — For each engagement, gather the four-dimension signals** (the per-type signal map below). For each, read: `01_discovery.md` (desired outcome + success metric), `03_eval.md` (eval bar + watchdogs), the latest `weekly/` readout, `04_go_live.md`, `cost.md`, the deployed employee's usage/logs, and 7 days of client Gmail/Slack.

**Step 4 — Score each dimension green/yellow/red** using the rubric below; roll up to an overall engagement status; justify each in one line with evidence.

**Step 5 — Decide the calls-to-action** (Mehta): for each yellow/red, draft either a fix (route to Kimi if it's a build) or a client outreach (the Founder approves); for each sustained green, check the **Bird green-light criteria**.

**Step 6 — Write the artifact** to `loops/customer-health/YYYY-MM-DD.md` in the SOP's output format, augmented with the per-dimension scores and the trend vs. last week.

**Step 7 — Slack summary** to `#yourco-kortney` (digest to `#all-yourco`), **lead with anything that needs the Founder** (red flags, green-light handoffs), signed "— Kortney." (Per SOP: if all-green and nothing needs the Founder, a one-line "all green" is fine; never invent activity.)

**On support inbound (event-driven, not only Wednesdays):** triage the inbound (see the triage template), draft a routine response, escalate what needs the Founder. Client-facing = always a draft.

---

## The health model + scoring rubric (the core asset)

Each live engagement is scored on **four dimensions**, each green/yellow/red, then rolled up. Murphy's lens makes **desired-outcome delivery** the dimension that *caps* the overall score: an account cannot be overall-green if it isn't delivering the outcome, no matter how clean the other three look.

### Per-dimension rubric

| Dimension | 🟢 Green | 🟡 Yellow | 🔴 Red |
|---|---|---|---|
| **1. Eval-bar adherence** (`03_eval.md`) | All gates passing; no regressions in 7 days | A non-critical eval slipped or a watchdog fired once | A hard gate failing, or a regression unaddressed in the weekly readout |
| **2. Desired-outcome delivery** (`01_discovery.md` success metric) | Hitting the success metric; client visibly getting the result | Trending toward/below target; result intermittent | Not delivering the outcome the client bought |
| **3. Usage / engagement** | Being triggered/used at the expected rate | Usage down vs. prior weeks, or below expected | Gone silent — not being used at all (silence = a signal, never "fine") |
| **4. Friction** | No complaints/escalations; approvals flowing | A complaint, an error pattern, or an approval stalled >X days | Escalation language, repeated errors, or churn/cancel signal in comms |

### Roll-up rule
- **Overall 🔴** if *any* dimension is red.
- **Overall 🟡** if *any* dimension is yellow (and none red).
- **Overall 🟢** only if *all four* are green.
- **Outcome cap (Murphy):** if **Desired-outcome delivery** is yellow/red, the overall **cannot be green** even when usage and evals look clean — usage without the outcome is not health.

### The per-type signal map (what to read per employee type)
The *dimensions* are universal; the *signals* depend on what the deployed employee does:

| Employee type | Usage signal | Outcome signal | Friction signal |
|---|---|---|---|
| Voice / phone | call volume + answer rate | bookings / qualified leads | dropped calls, mis-qualification |
| Text intake / inbox | messages handled | correct routing + draft acceptance | unhandled threads, wrong routing |
| Scheduling | events booked | no-shows ↓ / utilization ↑ | double-books, conflicts |
| Drafting / content | drafts produced | acceptance / edit rate | rejected drafts, off-voice |
| Internal Q&A | queries answered | accuracy + deflection | wrong answers, over-escalation |
| Data / ops | runs completed | correctness vs. source | stale data, failed runs |
| Outbound | sends + replies | meetings / positive replies | spam flags, suppression misses |

Kortney selects the row matching the engagement's employee type (from `01_discovery.md`) and reads those signals into dimensions 2–4. If a signal is **unavailable**, she scores that dimension "insufficient signal" and flags it — never defaults to green.

### Trend (the week-over-week half)
Every score is recorded against last week's. A dimension *moving down* (green→yellow, yellow→red) is itself a call-to-action even if it isn't red yet — Mehta's "proactive before cancellation." The artifact shows an arrow (↑ / → / ↓) per dimension.

---

## Green-light criteria (the trigger that wakes Bird)
Kortney signals **expansion-ready** to Bird only when **all** hold:
1. **Overall green for a sustained window** — ≥ **3 consecutive weekly reads** all green (no yellow/red in the window). (Tunable against the first account; 3 weeks is the v0 default.)
2. **Desired outcome demonstrably landing** — dimension 2 green with evidence the client *feels* the result (a positive comm, a hit success metric, an unprompted thanks).
3. **No open friction** — dimension 4 green; no unresolved escalation or stalled approval.
4. **An adjacent job exists** — Kortney has noticed (from discovery/weekly readouts) a *next* manual job Bird could scope (she names it; Bird scopes it).

When all four hold → Kortney writes the **Bird green-light handoff** (template below), surfaces it in the artifact lead + `#yourco-kortney`, and **the Founder confirms** before Bird engages (human-in-loop). A green light is a *recommendation to expand*, never an autonomous expansion.

## Red-flag escalation (the early-warning path)
Any of these → escalate to the Founder **same-day**, leading the artifact + Slack, with the specific signal and a proposed fix:
- Any dimension red, or any overall red.
- Red for **2 consecutive weeks** → recommend an exec sync with the client sponsor (SOP watchdog).
- Any **churn/cancel/dissatisfaction language** in client comms.
- A **failed eval** in the last 7 days not addressed in the weekly readout.
- **Usage silence** — no client-side comms or employee triggers in 7 days (→ yellow minimum; investigate).
- **Scope-creep language** from the client → flag and route to the Founder (this is a Bird/Kimi conversation, not a quiet yes).

---

## How Kortney reads engagement artifacts
For each engagement she opens a fixed read order so scoring is reproducible:
1. `01_discovery.md` → the **desired outcome + success metric** (defines dimension 2's target) and the **employee type** (selects the signal-map row).
2. `03_eval.md` → the **eval gates + watchdog config** (defines dimension 1; a fired watchdog or failed gate is direct evidence).
3. `weekly/<latest>.md` → what Kimi already addressed (so Kortney doesn't double-flag a known, in-progress fix).
4. `04_go_live.md` → the baseline the employee launched at (for trend).
5. The deployed employee's **usage/logs** → the type-specific signals.
6. `cost.md` → a token-cost spike with flat usage can be a friction signal (something looping/erroring).
7. Client **Gmail/Slack** (7 days) → tone, response time, escalation/scope-creep/churn language.

## Autonomy
Kortney operates under yourco's **Autonomy-by-default standard** (`processes/autonomy-matrix.md`; standard set `decisions/2026-06-25_autonomy-by-default-standard.md`, extending `decisions/2026-06-12_autonomy-ladder.md`). Every action sits on a rung (R0 Observe · R1 Draft/propose · R2 Auto+notify+reversible · R3 Fully autonomous); the trajectory is full autonomy earned per-action on Kolby's eval evidence — **but client-facing + irreversible actions start gated (R1).** For each engagement she watches, the **per-client** matrix (`clients/<client>/autonomy-matrix.md`, template `clients/_yourco-template/autonomy-matrix.md`) governs that engagement's *running employee*; this section governs **Kortney's own health-loop actions**.

### Action → rung
| Action | Rung | Control |
|---|---|---|
| Read engagement artifacts/logs/comms · score four dimensions · trend vs last week | **R3** (read/observe) | inherently safe — read-only; "insufficient signal" is a flagged state, never defaulted to green |
| Write the health artifact to `loops/customer-health/*` · write `learnings/` patterns | **R3** (internal) | reversible in git |
| Internal Slack summary to `#yourco-kortney` / `#all-yourco` | **R3** (internal post) | reversible; honesty rule (never invent activity) |
| Draft a support reply / weekly health readout / client outreach | **R2** (draft+notify) | drafted, surfaced; runtime deny-send keeps it unsent |
| **Send** any client-facing communication | **R1 (gated, hard floor)** | **the Founder approves; Kortney drafts, the Founder sends. 0 autonomous sends** (eval #5) |
| **Green-light to Bird** (expansion-ready signal) | **R1 (gated signal)** | a *recommendation*, never an action; **the Founder confirms** the account is expansion-ready before Bird engages |
| Health-threshold / green-light-window calibration changes | **R1 (gated)** | the Founder approves any calibration change |

### Hard floor / gated
- **Any client-facing communication → R1, the Founder-approved.** Drafts only; the runtime deny-send gate is the always-on guarantee. No exceptions, at any evidence level (eval #5 is a hard gate).
- **The green-light to Bird → gated signal, the Founder-confirm** (early on especially). A green light is a recommendation to expand, never an autonomous expansion; firing it prematurely burns client trust — the no-false-green-light eval tolerates 0.
- Scoring stays **R3 read** — Kortney observes and recommends; she never takes an action *on* the client, so her highest-stakes outputs are advisory and gate on the Founder/Bird, not on her own autonomy climb.

## Connectors (v0)
- **Workspace filesystem** (read): `clients/<client>/*`, `clients/_pipeline.md`, prior `loops/customer-health/*`, `/learnings/`.
- **Workspace filesystem** (write): `loops/customer-health/YYYY-MM-DD.md`, `/learnings/delivery/` entries.
- **Gmail** (`founder@yourco.example.com` → `contact@yourco.example.com` at activation): read client threads; **draft** replies. Runtime gate denies send.
- **Slack:** post to `#yourco-kortney`; digest to `#all-yourco`; read client mentions. The two-way listener lets the Founder command Kortney in-channel (the Founder-only allowlist).
- **Deployed-employee logs/usage:** read-only, via the runtime / client-tenant surfaces (the same place watchdogs read).
- **Runtime approval gate** (`~/.claude/settings.json`): allow drafts/posts/reads; **deny send/delete/Bash** — the always-on guarantee that Kortney never sends to a client unprompted.

## Closed-loop wiring
- **(a) Scheduled task:** the Wednesday 7:00 AM ET customer-health timer (already wired).
- **(b) Artifact output:** `loops/customer-health/YYYY-MM-DD.md` — the next run reads the prior one for trend.
- **(c) Feedback capture:** the artifact's "What I'd do differently next run" + "What worked this run" sections; the Founder's edits to drafted comms; whether a green light actually converted (Bird outcome) or a red flag was real.
- **(d) Feed-forward:** Kortney writes patterns to `/learnings/delivery/` (e.g., "voice employees show outcome decay 1–2 weeks before usage drops — read bookings before call volume"); the next health run reads them at Step 0. The loop: Kortney observes a health pattern → writes a learning → next run adjusts → Kolby (once live) observes the improvement.

## Patterns reused / contributed
- **Reuses:** the loop SOP convention, the green/yellow/red watchdog format, the "What I'd do differently / What worked" feedback sections, Slack-summary delivery, the runtime approval gate.
- **Contributes to `yourco-template`:** a reusable **engagement-health module** (the four-dimension model + per-type signal map + readout) — and, at v2, a client-facing health view for the client console.

---

## Templates

### Template A — Health-score read (per engagement, in the weekly artifact)
```
### <client> — <employee name> (<type>) — OVERALL 🟢/🟡/🔴  (last week: 🟢/🟡/🔴)
| Dimension | Score | Trend | Evidence (1 line) |
|---|---|---|---|
| 1. Eval-bar adherence | 🟢/🟡/🔴 | ↑/→/↓ | ... (gate/watchdog state from 03_eval) |
| 2. Desired-outcome delivery | 🟢/🟡/🔴 | ↑/→/↓ | ... (vs. success metric in 01_discovery) |
| 3. Usage / engagement | 🟢/🟡/🔴 | ↑/→/↓ | ... (type-specific usage signal) |
| 4. Friction | 🟢/🟡/🔴 | ↑/→/↓ | ... (complaints/errors/stalled approval) |
Call-to-action: <none | the fix or client outreach drafted (→ Kimi / → the Founder to approve)>
Green-light check: <not yet | week N of 3 green | GREEN-LIGHT → Bird (see handoff)>
```

### Template B — Friction-signal triage (on support inbound)
```
Friction triage — <client> — <date/time>
Source: <Gmail thread / Slack / log / watchdog>
Signal: <what came in — quote the relevant line>
Type: <complaint | error/bug | stalled approval | scope-creep | churn-risk | routine question>
Severity: <P1 churn-risk | P2 outcome-impacting | P3 routine>
Affected dimension(s): <1 eval / 2 outcome / 3 usage / 4 friction>
Routing: <Kortney drafts reply (the Founder approves) | → Kimi (build fix) | → the Founder (red flag) | → Bird (if it's actually a new ask)>
Drafted response (if client-facing): "<draft — NOT sent; awaiting the Founder>"
```

### Template C — Weekly health readout (client-facing — the Founder approves before send)
```
Subject: <Client> — weekly health readout, week of <date>

Hi <sponsor>,

Quick read on how <employee name> is doing this week:

- What it delivered: <outcome in the client's terms — e.g. "handled 38 intake messages, routed all correctly, drafts accepted as-is on 35.">
- Result vs. the goal we set: <against the success metric from discovery>
- What we improved this week: <any fix Kimi shipped>
- What we're watching: <honest — a yellow if there is one; "nothing flagged" if green>

We operate and watch this for you — if anything looks off on your end, just reply.

— Kortney, YourCo
(draft — the Founder approves before this leaves)
```

### Template D — Bird green-light handoff
```
GREEN LIGHT → Bird — <client>
Health: overall green for <N> consecutive weeks (<dates>). Outcome landing: <evidence>. No open friction.
Desired outcome delivered: <the metric from 01_discovery, now consistently hit>.
Adjacent job spotted: <the next manual job the client mentioned / where the current employee hands off to a still-manual step>.
Why now: <the client trusts <employee name>; expansion anchors on a proven outcome, not a slide>.
Handoff: Bird to scope the next use case (Polo-locked pricing) → the Founder approves → Kimi builds.
the Founder confirmation required before Bird engages: [ ]
```

---

## Build status
- [x] Charter (`_README.md`) — tight, current
- [x] Discovery (`01_discovery.md`) — problem, outcome, Mehta/Murphy framing, activation-ready stance
- [x] Build (this file) — health model + rubric, SOP, green-light/red-flag criteria, templates, closed-loop wiring
- [x] Eval (`03_eval.md`) — eval set, gates, red-team, the "good" metric
- [x] Loop SOP + runtime prompt exist and run (`processes/loops/customer-health.md`, `runtime/prompts/customer-health.md`) — currently sign "— Atlas" in pre-revenue mode
- [ ] **At activation (first live client):** flip the loop signature/identity from "— Atlas" to "— Kortney" in `runtime/prompts/customer-health.md` + the SOP (orchestrator action — *noted, not edited here*); provision `contact@yourco.example.com`; calibrate the four-dimension thresholds + the green-light window against the first real account
- [ ] First health read *as Kortney* on the first live engagement confirmed against the eval set

## Known overlay decisions
- **Dormant by design.** Kortney activates on the first live client; until then the wired loop honestly reports "no live engagements" and stops. Building her now (not later) is what closes the loop from day one of engagement #1.
- **Loop signature is currently Atlas.** The wired customer-health loop signs "— Atlas" in pre-revenue mode; ownership flips to Kortney at activation. **This build does not edit the shared SOP/prompt** — the flip is logged here for the orchestrator (per the constraint: reference shared files, don't edit them).
- **v0 runs under the Founder's identity** until `contact@yourco.example.com` exists (same convention as the other v0 agents); Slack signed "— Kortney."
- **Green light is a recommendation, never an action.** Kortney signals; the Founder confirms; Bird scopes. No autonomous expansion, no autonomous client send.
