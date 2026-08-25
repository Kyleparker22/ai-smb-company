# Kemba — Stage 2: Build

## Build approach
Kemba is largely a **codify-what-exists** build, not a from-scratch one. The substrate already exists (template scaffold, 15+ runtime loops, connectors, approval gate, registry). The 2026-06-25 deep-build of 11 agents (`decisions/2026-06-25_agent-roster-deep-build.md`) *already executed the agent-building pipeline manually*. Building Kemba means: (1) turn that manual pipeline into a repeatable, governed **Agent Factory** SOP; (2) name an owner for the template + runtime + web infra; (3) hold the substrate to overlay-only + versioning discipline; (4) wire the Factory into the governance the moat already runs on (the Founder approves · Rafi sanctions · Kolby evals). Lowest-risk because the proof already happened — Kemba documents the road, it doesn't pave it for the first time.

---

# THE AGENT FACTORY (the centerpiece)

The governed pipeline that turns "we might need an agent for X" into a built, wired, sanctioned agent — or a documented FOLD-IN / DEFER. **Propose-and-scaffold under human + Rafi + Kolby governance; never autonomous agent-creation.** Five steps.

> **The one-line invariant:** Kemba *proposes and scaffolds*. the Founder *approves* every new agent. Rafi *sanctions* it in the registry. Kolby *evals* it before it runs. Kemba never self-deploys, never widens a connector scope, never enables a timer.

## Factory Step 1 — The "should-this-exist?" GATE (go / no-go)
The first and most important step is a *brake*, not an accelerator. Before any research or scaffolding, run the request through the lean-roster rubric and emit **BUILD / FOLD-IN / DEFER** with reasons. The default posture is *don't build* — BUILD must be earned on all three axes.

**The three-axis BUILD test (all three must be YES):**
1. **Distinct tool stack?** — Does the capability need connectors / a tool surface that no existing agent owns? (If it's "more of what Reilly/Atlas/Charles already touch," it's not distinct.)
2. **Distinct eval bar?** — Does "good" mean something a different way than any existing agent's eval set measures? (Research quality ≠ deliverability ≠ margin accuracy ≠ brand-fit. If an existing agent's rubric already captures "good" here, it's not distinct.)
3. **Real trigger firing now?** — Is there a near deal, a first hire, a live client, or a recurring manual task crossing a threshold (Step 2)? Or is this preemptive "we might want it someday"?

**The decision:**
- **BUILD** — all three YES. Proceed to Steps 2→5.
- **FOLD-IN** — the capability is real but fails axis 1 or 2: it lacks a distinct stack *or* a distinct eval bar. Output: *which existing agent absorbs it*, and a one-line scope addition for that agent's `_README` (per the roster rule: "Research → inside Reilly; analytics/monitoring → inside Atlas; orchestration → Atlas's future role"). No new agent.
- **DEFER** — the capability would pass axes 1+2 but axis 3 fails (no trigger / preemptive). Output: the *named trigger* that would flip it to BUILD, and whether to deep-build it **activation-ready-but-dormant** (the 2026-06-25 pattern — full docs, doesn't run until the trigger fires) or leave it as a roster line. Building unproven agents that run is the shiny-tools trap; activation-ready-but-dormant is the sanctioned compromise.

**Output:** an **Agent Build Request + go/no-go decision record** (template below), logged in `decisions/YYYY-MM-DD_<name>-go-no-go.md`. The record is the artifact even when the answer is no — a documented FOLD-IN/DEFER is a successful Factory run.

## Factory Step 2 — The "when-to-build" recommender
Axis 3 of the gate, expanded. A BUILD trigger is a **real, present signal**, not an aspiration. The sanctioned trigger classes (from `04_agent_roster.md` "prove the unit before adding the next"):
- **A near deal** — a prospect close enough that delivery capability must exist (e.g. Kimi/Janice activate as a deal nears close).
- **A first-of-its-kind event** — first signed client (Janice/Kortney), first invoice (Harry), first human hire (Kori), first contract in flight (Ray), first client data / procurement ask (Rafi).
- **A recurring manual task crossing a threshold** — a chore the Founder (or an agent) does by hand often enough that it clears the lean-roster bar *and* has a distinct stack/eval. (Threshold heuristic: recurring ≥ weekly, costs real founder attention, and isn't absorbable by an existing agent.)
- **A capacity ceiling** — an existing agent's scope is overloaded to where splitting it improves both halves (e.g. the 2026-06-15 Reilly→Michelle split: the machine vs. the message became two distinct eval bars).

**Not triggers (→ DEFER):** "competitors have one," "it would be cool," "we might scale into it," "the roster has a slot for it." A roster line is a *map, not a build queue*.

**Output:** folded into the go/no-go record — the trigger named, its class, and whether it is firing *now* or is a future flip-condition.

## Factory Step 3 — The research + build pipeline
Only for a BUILD (or an activation-ready DEFER). This is the codified 2026-06-25 deep-build.
1. **Research the domain + expert lineage.** Identify the real industry authority the agent mirrors (the `04_agent_roster.md` lineage table is the precedent — every agent is grounded in a named expert/methodology, e.g. Charles→Skok, Bella→Goldratt+Block, Kemba→Skelton & Pais). Use WebSearch + the workspace context. The lineage is load-bearing: it's the methodology the agent follows and the "why this is grounded, not improvised" for executive trust.
2. **Scaffold `clients/<name>/` from the template.** Create `_README.md` (tight charter) + `01_discovery.md` + `02_build.md` + `03_eval.md` using the **new-agent scaffold skeleton** (below) — the exact heading structure the 2026-06-25 builds hold, so every agent passes the same structure bar. Fill from the research + the request context. **No fabricated clients, metrics, or live state** — pre-revenue is reported as pre-revenue; trigger-gated agents are documented as dormant-until-trigger.
3. **Define eval gates — with Kolby.** Draft the agent's eval set (test cases · scoring rubric · hard gates · red-team failure modes · the "good" metric) in `03_eval.md`. Kemba scaffolds the harness shape; **Kolby owns the eval bar** and reviews/finalizes it. An agent does not run until Kolby has eval'd it.
4. **Identify connectors/tools + handoffs.** Map what the agent needs to read/draft, and which agents it hands off to/from (the capability-boundary seams: e.g. Bella→Janice→Kimi, Janice→Kimi, Charles↔Harry). This feeds the wiring checklist (Step 4).
5. **Update the roster + lineage table** (`04_agent_roster.md`) — *drafted by Kemba, the orchestrator/the Founder commits the shared-file edit.* Kemba proposes the row + the lineage entry; it is not Kemba's to commit unilaterally (shared file).

## Factory Step 4 — The wiring checklist (drafts-vs-host tagged)
The agent is scaffolded; now connect it. **Every step is tagged `[DRAFT]` (Kemba does it — read/draft/propose, inside the gate) or `[HOST]` (a human action on the server / in an external console — the Founder, or Rafi for sanction).** The whole point of the tagging is that Kemba *cannot* and *must not* perform a `[HOST]` step.

| Wiring item | What it is | Tag |
|---|---|---|
| **Connectors** | The MCP/tool scopes the agent reads/drafts. Kemba *proposes* the minimal set, all **read/draft-only** by the gate (allow Read/Write/Edit/Slack-post/Gmail-draft+read; **never** send/delete/Bash). | `[DRAFT]` proposes scope |
| **Widen the approval gate** | If the agent needs a *safe* tool not yet in `~/.claude/settings.json` `allow`. | `[HOST]` the Founder edits the gate; never add send/delete/pay |
| **Slack channel** | `#yourco-<name>` per the per-agent channel pattern + listener allowlist. | `[DRAFT]` proposes the channel + map entry / `[HOST]` invite the bot, create the channel |
| **Registry sanction** | Add the agent's prompt/timer/service/channel/connector scope to `runtime/agent-registry.json` — the *act of sanctioning*. | `[DRAFT]` Kemba proposes the registry delta / `[HOST]` **Rafi commits the sanction on the Founder's approval** |
| **systemd loop/timer** | If scheduled: write `runtime/prompts/<loop>.md` + the `.service`/`.timer`, pick the slot. | `[DRAFT]` Kemba writes the prompt + reference unit files / `[HOST]` install to `/etc/systemd/system/`, `daemon-reload`, `enable --now` |
| **Handoffs** | The to/from seams with other agents, documented in both `_README`s. | `[DRAFT]` documents the seam |
| **Identity / mailbox** | `<name>@yourco.com`. | `[HOST]` the Founder provisions; agent runs under the Founder's identity until then (the Atlas/Charles/Reilly v0 pattern) |
| **Eval sign-off** | Kolby runs the eval set before first live run. | `[HOST]` Kolby evals; gate to "runs" |
| **the Founder's approval** | The agent exists only because the Founder approved it. | `[HOST]` the sanctioning approval |

**Output:** the **agent wiring checklist** (template below), every row tagged, attached to the build. Kemba executes the `[DRAFT]` rows and hands the `[HOST]` rows to the Founder/Rafi/Kolby as a punch list.

## Factory Step 5 — Closed-loop wiring + roll-back into the template
- **Trigger:** on-demand (a new agent/capability request) + after the first 1–2 engagements produce extractable patterns.
- **Artifact:** the go/no-go record (`decisions/`), the scaffolded `clients/<name>/` set, the wiring checklist.
- **Feedback:** after a Factory run, capture "what the gate got right/wrong" and "where the scaffold needed hand-editing" — if the scaffold needed the *same* hand-edit twice, that's a **missing abstraction in the skeleton** → fix the skeleton.
- **Feed-forward:** patterns → `learnings/platform/`, read at **Step 0** of the next Factory run (e.g. "agents in the delivery cluster always need the Janice→Kimi handoff documented"; "the go/no-go gate keeps getting asked to build research agents — reinforce 'research folds into Reilly'").
- **Template roll-back:** the **"fork = missing abstraction"** rule. If building an agent (or an engagement) required forking the template instead of overlaying, capture it in `decisions/`, fold the abstraction into `yourco-template`, **bump the version in `CHANGELOG.md`**, and the next build starts ~80% done. The template only gets stronger; it never forks.

---

# THE TEMPLATES (the actual artifacts)

## Template A — Agent Build Request + go/no-go decision record
File: `decisions/YYYY-MM-DD_<name>-go-no-go.md`
```
# Agent Build Request — <proposed name / capability> — go/no-go

**Date:** YYYY-MM-DD · **Requested by:** <who/what surfaced it> · **Decided by:** the Founder
**Prepared by:** Kemba (Agent Factory)

## The request (one line)
<What capability is being asked for, in outcome terms.>

## The go/no-go GATE (three-axis BUILD test — all three must be YES to BUILD)
1. **Distinct tool stack?**  YES / NO — <reason; which connectors no existing agent owns>
2. **Distinct eval bar?**    YES / NO — <reason; how "good" here differs from every existing agent's rubric>
3. **Real trigger firing now?** YES / NO — <the trigger + its class, or "preemptive">

## The when-to-build signal (axis 3, expanded)
- Trigger class: near-deal / first-of-kind / recurring-manual-threshold / capacity-ceiling / NONE
- Firing now, or future flip-condition? <state which, and the named condition>

## DECISION:  BUILD  /  FOLD-IN  /  DEFER
**Reasoning:** <why, against the three axes + the lean-roster rule>

### If FOLD-IN
- Absorbing agent: <name>
- One-line scope addition for its _README: "<...>"

### If DEFER
- Named trigger that flips it to BUILD: <...>
- Activation-ready-but-dormant (deep-build now, runs at trigger)?  YES / NO

### If BUILD
- Expert lineage to research: <named authority/methodology>
- Cluster / handoff seams: <which agents it hands off to/from>
- Proceed to scaffold (Factory Step 3) + wiring checklist (Factory Step 4)

## Governance acknowledgement
Kemba proposes/scaffolds only. This decision is the Founder's; a BUILD requires Rafi's registry sanction
and Kolby's eval before the agent runs. No timer enabled, no connector widened by Kemba.
```

## Template B — New-agent scaffold skeleton (the 01/02/03 headings a new agent gets)
Every BUILD gets these four files, matching the 2026-06-25 structure bar. Headings below are the required structure; a scaffold that omits a heading fails the structure eval (`03_eval.md` EC).
```
clients/<name>/_README.md   — tight charter:
  # <Name> — <Role> Agent
  <one-paragraph what-it-owns>  ·  > **Boundary:** <vs. its nearest siblings>
  ## Lineage — who <Name> mirrors    (the named expert/methodology + YourCo fit)
  ## What <Name> owns
  ## Context <Name> draws on (source of truth)
  ## How <Name> runs                 ## Approval gates                ## Status

clients/<name>/01_discovery.md:
  # <Name> — Stage 1: Discovery
  ## Client  ## Executive sponsor  ## The problem <Name> owns
  ## The outcome (one sentence)  ## Where <Name> sits
  ## Inputs → Outputs  ## The constraint <Name> relieves
  ## <Lineage> frame   ## First use case
  ## Outcome the executive can repeat in one sentence
  ## Systems <Name> touches (v0)  ## Inherited
  ## Success criteria (eval set v0 — full harness in 03_eval.md)
  ## Approval pattern  ## Digital employee identity
  ## Scope — IN (v0)  ## Scope — OUT  ## v0→v1→v2 roadmap  ## Risks

clients/<name>/02_build.md:
  # <Name> — Stage 2: Build
  ## Build approach  ## Components  ## Inherited vs new
  ## Patterns reused / contributed   ## How <Name> works — the SOPs (step-by-step)
  ## Connectors (and the gate)       ## Closed-loop wiring
  ## Template(s) — the actual artifacts the agent produces
  ## Build status (checklist)        ## Known overlay decisions

clients/<name>/03_eval.md:
  # <Name> — Stage 3: Eval / gates / watchdogs
  ## Eval set (v0)                   ## Approval gates
  ## Watchdogs (runtime guards)      ## Concrete eval cases (the harness — EC-1..n with fixtures)
  ## Scoring rubric                  ## Hard pass/fail gates
  ## Red-team / failure modes (and the guard)
  ## The metric that defines 'good'  ## Pre-go-live checklist  ## Iteration plan
```
**Non-negotiables baked into the skeleton:** a named expert lineage; honest pre-revenue/dormant state (no fabricated clients/metrics); the approval pattern with explicit must-approve gates; a closed-loop feedback + feed-forward step; clear capability boundaries vs. nearest siblings.

## Template C — Agent wiring checklist (connectors · channel · registry · timer · handoffs)
File: `clients/<name>/wiring-checklist.md` (attached to the build)
```
# <Name> — wiring checklist   (tag every step: [DRAFT]=Kemba, inside the gate · [HOST]=human action)

## Connectors (proposed scope — read/draft-only by the gate)
- [ ] [DRAFT] Propose minimal connector set: <list>  (allow: Read/Write/Edit/Slack-post/Gmail-draft+read)
- [ ] [HOST]  Widen the approval gate IF a new *safe* tool is needed (the Founder edits ~/.claude/settings.json; NEVER add send/delete/Bash/pay)

## Slack channel
- [ ] [DRAFT] Propose #yourco-<name> + add to runtime/slack-channels.md map
- [ ] [HOST]  Create the channel + invite the bot + add to the listener allowlist

## Registry sanction (the act of sanctioning)
- [ ] [DRAFT] Propose the runtime/agent-registry.json delta (prompt/timer/service/channel/connector)
- [ ] [HOST]  RAFI commits the sanction in agent-registry.json on the Founder's approval (Kemba does NOT commit it)

## systemd loop/timer (only if scheduled)
- [ ] [DRAFT] Write runtime/prompts/<loop>.md + reference .service/.timer + pick the slot
- [ ] [HOST]  Install to /etc/systemd/system/, daemon-reload, enable --now <timer>

## Handoffs
- [ ] [DRAFT] Document the to/from seams in this agent's _README and the counterpart's

## Identity
- [ ] [HOST]  Provision <name>@yourco.com  (runs under the Founder's identity until then)

## Gates to "runs"
- [ ] [HOST]  FOUNDER approves the agent exists
- [ ] [HOST]  KOLBY evals the agent's set before first live run
- [ ] [DRAFT] Reconciliation watchdog confirms live runtime == registry (no un-sanctioned artifact)

## Sign-off
Built/scaffolded by Kemba (Factory) · Sanctioned by Rafi · Eval'd by Kolby · Approved by the Founder
```

---

# KEMBA'S OTHER PLATFORM DUTIES (the rest of the substrate — brief, the Factory is the centerpiece)

## D1. `yourco-template` upkeep + pattern extraction
The golden client scaffold (`clients/_yourco-template/`). Per `03_internal_platform.md` it owns: the agent harness, eval/watchdog scaffolding, standard integrations (Gmail/Outlook/calendar/CRM hooks), approval-flow primitives, exec-reporting primitives. **Overlay-only, never forked.** After each engagement, Kemba extracts the reusable parts → folds into the template → bumps `CHANGELOG.md` → logs in `decisions/`. The **"fork = missing abstraction"** rule is the discipline: any fork-pressure becomes the next version's upgrade. The 2026-06-25 build noted a clean finance/bookkeeping module from Charles as a candidate template contribution — that extraction is Kemba's job.

## D2. The always-on runtime
Owns the headless execution substrate (`runtime/`, `runtime/run-loop.sh`, systemd units, the approval-gate reference, connectors). Keeps it documented + reproducible; owns the migration of remaining loops/connectors following the proven Monday-briefing pattern. **All behavior-changing runtime acts are `[HOST]`** — enabling a timer, installing a service, widening the gate, inviting a bot. Kemba writes/drafts the prompts + reference units; the host install is human. Standing input: the credit-death failure (`learnings/ops/2026-06-18_runtime-silent-credit-death.md`) + the API-independent alarm — the runtime's single-point-of-failure that Kemba guards.

## D3. The eval / watchdog / approval scaffolding
The reliability primitives every loop + engagement inherits — the moat layer made concrete. Kemba maintains the harness; Kolby runs the evals on it. In the Factory, Kemba scaffolds a new agent's eval *shape*; Kolby owns the bar.

## D4. Web infrastructure (hosting / DNS / uptime / domains)
Handed off from Webb 2026-06-15 — infra is infra. `yourco.com` + `getteamyourco.com` hosting, DNS, uptime/monitoring, domains. **Webb owns the pages; Kemba owns the plumbing.** **DNS/hosting/domain changes = must-approve** (`[HOST]`) — Kemba drafts the change + the rollback plan; the Founder approves before it's live.

## Connectors (and the gate)
Kemba is read/draft/propose-only on every connector — structurally incapable of a host action in v0:
- **Workspace files** (`clients/_yourco-template/`, `runtime/`, `clients/<name>/`, `decisions/`, `learnings/`) — read + write (the substrate + scaffolds).
- **WebSearch** — research the domain + lineage for a BUILD.
- **Slack `#yourco-kemba`** — post the platform/Factory summary, signed "— Kemba, YourCo Platform."
- **Proposes** registry deltas (Rafi commits), connector-scope widenings (the Founder edits the gate), timer installs (host), DNS changes (must-approve). Kemba never sends/deletes, never runs Bash on the production host, never commits a sanction, never enables a timer.

## Closed-loop wiring (Kemba's own loop)
- **Trigger:** on-demand (agent/capability request, infra task) + after the first 1–2 engagements (pattern extraction).
- **Artifact:** the go/no-go record + scaffold + wiring checklist (Factory); the template `CHANGELOG.md` bump + `decisions/` entry (extraction); drafted runtime/infra changes with `[HOST]` steps flagged.
- **Feedback:** "what the gate / scaffold got wrong" after each Factory run; "what forked" after each engagement.
- **Feed-forward:** `learnings/platform/`, read at Step 0 of the next Factory/extraction run.

## Autonomy
Governed by `processes/autonomy-matrix.md` (standard set 2026-06-25). Kemba has a **dual role** here: like every agent it sits on rungs, but as the Agent Factory it is also the agent that **wires the autonomy matrix into every agent it builds**. Both halves below.

### Kemba's own actions
Kemba is structurally **propose-and-scaffold** — read/draft/document inside the gate, no `[HOST]` action ever. That maps cleanly onto the matrix: its surface is R3, and the `[HOST]` line *is* the R1 floor.

| Kemba action | Starts | Ceiling | Advances on |
|---|---|---|---|
| Read substrate/roster/request, WebSearch the domain+lineage | **R3** | R3 | inherently safe |
| Draft the go/no-go record, scaffold `clients/<name>/`, draft the wiring checklist + registry delta (`[DRAFT]`) | **R3** | R3 | reversible in git; nothing goes live from a draft |
| Extract patterns into `yourco-template` (versioned in `CHANGELOG.md` + logged) | **R3** | R3 | overlay-only, reversible |
| Slack post to `#yourco-kemba` | **R3** | R3 | reversible internal post |

**Hard floor (R1 `[HOST]`, never climbs for Kemba):** enable a systemd timer / install a service, widen any connector scope in the approval gate, **commit a registry sanction** (Rafi's act on the Founder's approval), any DNS/hosting/domain change, provision a mailbox. Kemba **self-deploying** (enabling a timer or committing a sanction itself) is the cardinal governance breach (`03_eval.md` EC-9). Autonomy ends at the drafted checklist.

### The Factory wires the matrix into every new agent (Kemba's standard-propagation duty)
The Agent Factory is **how autonomy-by-default reaches every new agent.** Every BUILD carries the matrix from birth:
- **New agents start gated.** The scaffold skeleton (`02_build.md` Template B) and the proposed connector set default to **read/draft-only** (allow Read/Write/Edit/Slack-post/Gmail-draft+read; **never** send/delete/Bash) — i.e. unproven/irreversible actions begin at **R1**, exactly as the matrix's hard rule requires. The over-scoped-connector watchdog blocks any proposed scope above draft (EC-6).
- **The autonomy matrix is part of the scaffold.** A Factory-built agent's `02_build.md` includes its own `## Autonomy` section (this is now part of the structure bar) mapping its actions → starting rung → advancement evidence → hard floor — drafted by Kemba, with the eval bar owned by Kolby.
- **Rung changes are sanctioned, not auto.** Just as a new agent only "runs" after the Founder approves + Rafi sanctions the registry + Kolby evals, a later **rung climb** is sanctioned the same way: Kolby's eval evidence proposes it, the Founder sets the threshold, Rafi reflects the widened scope in `agent-registry.json`. Kemba proposes; it never widens a rung itself.

## Build status
- [x] Substrate exists (template scaffold + 15+ runtime loops + connectors + approval gate + registry watchdog)
- [x] The agent-building pipeline proven manually (2026-06-25 deep-build of 11 agents)
- [x] Engagement docs scaffolded + deepened (this folder) — the Factory codified as SOP
- [x] Factory templates written (Build Request/go-no-go · scaffold skeleton · wiring checklist)
- [ ] Roster row + lineage entry for Kemba reflect "built" (shared-file edit — orchestrator/the Founder commits)
- [ ] `contact@yourco.example.com` provisioned (`[HOST]` — the Founder; runs under the Founder's identity meanwhile)
- [ ] First live Factory run on a real agent request → confirmed against `03_eval.md`
- [ ] `#yourco-kemba` channel + registry entry (`[HOST]` — on the next runtime sanction)

## Known overlay decisions
- **v0 runs under the Founder's identity** until `contact@yourco.example.com` exists (the Atlas/Charles/Reilly v0 pattern); Slack signed "— Kemba, YourCo Platform."
- **The Factory is propose-and-scaffold, full stop.** Even when the pipeline is fully codified, Kemba never crosses a `[HOST]` line. Autonomy ends at the scaffold + the drafted checklist.
- **Registry sanctioning stays Rafi's act** (`decisions/2026-06-22_agent-registry-governance-watchdog.md`); Kemba provides the hook + proposes the delta. The roster edit (`04_agent_roster.md`) is a shared-file change committed by the Founder/the orchestrator, not Kemba unilaterally.
- **Template changes are versioned + logged** in `CHANGELOG.md` + `decisions/`; the template is never forked.
