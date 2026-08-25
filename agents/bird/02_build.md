# Bird — Stage 2: Build

## Build approach
Bird is an **activation-ready dormant build**: the full expansion SOP, the three working templates (scorecard, proposal, scope-handoff), the connectors, and the eval set are all in place — but Bird does **not run** until Kortney greenlights the first account. This mirrors Kortney's and Kimi's "built, no-op until first engagement" pattern. Building Bird means: (1) write the SOP that turns a green light into a ranked, priced, outcome-justified proposal; (2) provide the templates; (3) wire the connectors and the hard gates; (4) wire the closed loop. Nothing here invents an account or a number — the worked examples are explicitly illustrative.

## Components
### 1. The expansion SOP
The motion from Kortney's green light → ranked opportunity → scoped + priced proposal → Kimi handoff. Detailed below (§"How Bird works").

### 2. The three templates
- **Expansion-opportunity scorecard** (mapped to the 8 pillars / OS tiers) — §Template A.
- **Upsell / renewal proposal** (outcome-anchored, Polo-locked pricing) — §Template B.
- **Bird→Kimi scope handoff** (the clean build spec) — §Template C.

### 3. The renewal motion
Flag renewals early, prep the retention conversation anchored on delivered outcomes (from Kortney's trend) — §"Renewal motion."

### 4. Connectors + hard gates
Read-only on Kortney's reads + engagement folders + pricing; draft-only on Gmail; post-only on Slack; the two hard gates (client-facing = approve; Polo-locked prices only).

## Patterns reused / contributed
- **Reuses:** the loop-SOP convention (Step 0 read-learnings → boot → work → write → Slack), the closed-loop feedback section, the Slack-summary delivery, the `clients/<client>/` folder convention, the approval-gate pattern (draft → the Founder approves → act). Reuses Kortney's health artifact as its trigger input and Polo's pricing references as its only price source.
- **Contributes to the system:** a clean **land-and-expand module** — the scorecard + proposal + scope-handoff trio — likely reusable as a client-facing "growth/renewal employee" later (Pillar 2, pattern #12 "Renewal & upsell rep"). When the first expansion lands, the pattern gets a `learnings/expansion/` write-up.

## How Bird works — the SOPs

### A. Expansion SOP (fires on Kortney's green light; runs per healthy account)
**Trigger:** Kortney signals an account has held **green** for a sustained window (defined with Kortney at activation — a single good week is not enough). Until then Bird is dormant and the correct output is "no live accounts yet — dormant."

0. **Read learnings (Step 0).** Last ~5 entries in `learnings/expansion/` + `learnings/sales-copy/` + `learnings/delivery/`; apply what fits; list applied entries in the artifact. (Folders may be empty pre-launch — expected.)
1. **Confirm the gate.** Re-read Kortney's latest `loops/customer-health/*` for this account. **Green and sustained?** If not green → **stop**, log "not expansion-eligible — <reason>," route back to Kortney. (Hard gate; this is eval test #5.)
2. **Boot account context.** Read the engagement folder: `01_discovery.md` (adjacent jobs the client *named but didn't buy*), `02_build.md` (what's deployed), `03_eval.md` (the proven outcome the client now trusts), go-live + weekly readouts (what's working, in the client's own words), `cost.md` (margin headroom — don't propose something that craters margin).
3. **Map the next roles.** Lay the **8 pillars** (`processes/ai-os-modules.md`) over this account: which pillar is the deployed employee in, and what are the adjacent un-automated jobs? Cross-reference the **26 employee shapes** (`clients/_yourco-template/employee-patterns.md` + `employee-patterns-tier2.md`) for the concrete next role. Sources of candidates: (a) jobs the client named in discovery, (b) the manual step the current employee hands off to, (c) the next pillar on the OS ladder, (d) **the weak links already visible on the audit's connected picture** (`processes/audit-sop.md` §Step 4a) — the Audit drew the client's business as objects + links and dollar-flagged more than one leak; the un-fixed links *are* the pre-scoped expansion backlog.
4. **Score each candidate** on the scorecard (Template A): **Outcome value × Evidence client needs it × Build feasibility × Margin fit** → a leverage rank. **Highest-leverage, not easiest-sale.**
5. **Confirm the price.** Pull the number from a **Polo-locked row only** — `pricing/v0/os-tiers.md` (OS ladder, graduation, Command overage) / `vertical-ranges.md` (per-vertical bands + per-employee marginal) / `landscaping-hardscaping.md` (anchor). Apply the graduation rule (no re-charged implementation; expansion = setup fee + **retainer step-up**; 4th coordinated employee → re-paper as an OS). **If no locked row covers it → flag to Polo/the Founder; do NOT invent a number.** (Hard gate; eval test #2.)
6. **Draft the proposal** (Template B) — outcome-anchored, tied to the result the client already trusts the first employee for, Polo-locked pricing, framed as a step-up not a re-sale. **Frame it as the next link on the client's own picture** (`processes/audit-sop.md` §Step 4a): the Audit already showed them this link and its cost, so the pitch is *"want us to fix the next one?"* — a continuation of a diagnosis they already agreed with, never a new pitch. Where the write-back loop has surfaced fresh evidence since go-live (e.g. the deployed employee keeps handing off to the same manual step), lead with that — the system itself found the next leak. Draft only.
7. **Write the scorecard artifact** + the drafted proposal to `clients/<client>/expansion/`.
8. **Slack** — needs-the Founder summary to `#yourco-bird` (digest to `#all-yourco`), signed "— Bird, YourCo Ops": the account, the recommended next role, the locked price, "proposal drafted — your approval to send."
9. **On the Founder's approval** → finalize the proposal for send (the Founder sends), and write the **Bird→Kimi scope handoff** (Template C) so Kimi can start the build.
10. **Feed-forward.** When an expansion lands (or is declined), write a `learnings/expansion/` entry the next run reads at Step 0.

**Gate:** read/score/write/post + draft only. **No client-facing send; no unlocked price; no build.**

### B. Renewal motion (ahead of each renewal date)
1. **Surface the date.** From the SOW/agreement (`processes/contracts/`) + the CRM; Bird flags upcoming renewals early (default ~60 days out, tuned at activation).
2. **Pull the evidence.** From Kortney's health trend + the engagement's `03_eval` + weekly readouts: the outcomes delivered since signing (hours saved, leads recovered, drafts accepted — whatever the proven success metric is).
3. **Prep the retention brief** — a renewal conversation anchored on *delivered outcomes*, not on the renewal itself. Where the account is green and expansion-eligible, fold in the next-use-case proposal (renewal + expand is the strongest moment).
4. **Draft any client-facing renewal comm** → the Founder approves → the Founder sends.
**Gate:** same — outcome-anchored, locked pricing, drafts only.

## Templates

### Template A — Expansion-opportunity scorecard (`clients/<client>/expansion/scorecard-YYYY-MM-DD.md`)
```
# Expansion Scorecard — <Client> — YYYY-MM-DD
_Bird drafts. Health-gated: only run on a Kortney-green account._

## Gate check
- Kortney status (latest health read): GREEN / sustained since <date>  [REQUIRED — if not green, stop]
- Deployed employee + pillar: <employee> (Pillar N — <name>)
- Proven outcome the client now trusts: <the 03_eval success metric, in the client's words>
- Margin headroom (from cost.md): <ok / tight — note>

## Candidate next roles (scored)
| Candidate (pillar · pattern #) | Outcome value (1-5) | Evidence client needs it (1-5) | Build feasibility (1-5) | Margin fit (1-5) | Leverage rank |
|---|---|---|---|---|---|
| <e.g. Follow-up rep (P2 · #10)> | | | | | |
| <e.g. Review & reputation (P4 · #14)> | | | | | |
| ... | | | | | |

_Leverage = Outcome value × Evidence × Feasibility × Margin fit. Rank highest-leverage first — NOT easiest sale._

## Evidence per top candidate
- **What the client said** (discovery / readouts): "<quote or note — the job they named but didn't buy>"
- **Where the current employee hands off** to a still-manual step: <the seam>
- **The outcome to anchor on**: <result they already trust → the bridge to the next>

## Recommendation
- **Next role:** <candidate> — because <leverage reason>.
- **OS-ladder position:** <on-ramp / Core / Suite / Operation / Command> — adding this moves them <from → to>.
- **Polo-locked price:** <number + the exact pricing/v0/ row it traces to> — step-up: <setup (if any) + retainer Δ>.

## Learnings applied this run
(/learnings/expansion/ + /sales-copy/ + /delivery/ entries that influenced this; "None" if none)
```

### Template B — Upsell / renewal proposal (`clients/<client>/expansion/proposal-YYYY-MM-DD.md`)
```
# Expansion Proposal (DRAFT — the Founder approves before send) — <Client> — YYYY-MM-DD
_Bird drafts. Client-facing = must-approve. Pricing = Polo-locked rows only._

## To
<Client contact, role>

## The result so far (anchor)
Since <go-live date>, your <employee> has <delivered outcome — the proven 03_eval metric, honest numbers from the real account; no fabrication>.

## The next step (outcome, not feature)
The natural next move is a <next role> — because <the manual job it removes / the result it adds>, tied directly to what <employee> already does for you.
- What it does: <one concrete sentence>
- The outcome you'd get: <hours saved / revenue captured / risk removed>

## What changes
- This is a **step-up, not a new project**: <per the graduation rule — no re-charged implementation; setup (if any) + retainer step-up; or "this is your 4th coordinated role — let's make it one OS">.
- **Investment:** <Polo-locked number + step-up> — traces to <pricing/v0/ row>.
- **Live in ~48h** once approved; same reliability/eval/approval layer you already have.

## What stays the same
You never touch tokens, models, or infrastructure. We own reliability and ongoing improvement; you get the outcome.

## Next step
<single clear CTA — a 15-min scope call / a yes to proceed>

---
APPROVAL: [ ] the Founder approved to send   |   Pricing source row: <pricing/v0/...>
```

### Template C — Bird→Kimi scope handoff (`clients/<client>/expansion/scope-handoff-YYYY-MM-DD.md`)
```
# Scope Handoff: Bird → Kimi — <Client> — YYYY-MM-DD
_Created only AFTER the Founder approves the proposal. Complete enough for Kimi to start with no round-trips._

## Account
- Client: <name> · tenant: <ref> · existing employee(s): <list + pillars>
- Kortney status at handoff: GREEN (sustained since <date>)

## The new employee to build
- **Role / pattern:** <employee> — Pillar N (<name>), pattern #<n> from employee-patterns(-tier2).md
- **Tier / OS-ladder move:** <on-ramp add / graduate to Core / etc.>
- **Desired outcome (the success metric):** <one sentence — what "working" means>
- **Why now:** <the evidence from the scorecard>

## Build spec
- **Stack / connectors needed:** <from the pattern's stack line, tailored to this client's tools>
- **Inputs it reads / actions it takes:** <...>
- **Approval rules (what must never auto-send/auto-act):** <client's existing gate + any new>
- **Handoffs:** <where it picks up from / hands to the existing employee>
- **Eval bar to define (03_eval for this employee):** <the gates Kortney will then watch>

## Commercials (locked + approved)
- Price: <Polo-locked number> (row: <pricing/v0/...>) · approved by the Founder YYYY-MM-DD
- Step-up structure: <setup (if any) + retainer Δ> · re-papered as: <new SOW line / OS graduation>

## Notes / risks for the build
<margin headroom, integration gotchas, anything Kortney flagged>
```

## Autonomy
Bird is governed by the Autonomy Matrix (`processes/autonomy-matrix.md`) — every action sits on a rung (R0 observe · R1 draft/propose · R2 auto+notify+reversible · R3 fully autonomous); the default trajectory is full autonomy, **earned per action on Kolby's eval evidence**, never switched on. Bird's read/score/draft work is internal and reversible (high-rung); the one externally-consequential action — a **client-facing proposal** — stays gated by design.

| Action | Start | Ceiling | Advance when |
|---|---|---|---|
| Read health reads / engagement folders / pricing, score opportunities (internal) | **R3** | R3 | inherently safe |
| Write scorecard / scope-handoff / draft proposal / renewal brief, Slack post to `#yourco-bird` (internal, git-reversible) | **R3** | R3 | reversible |
| **Client-facing proposal / renewal comm** (a quote to a live account) | **R1 (gated)** | R1–R2 | climbs only on Kolby's eval-vs-reality record + the Founder's threshold; high-stakes (executive trust + revenue) — most of this class stays gated by design |
| **Quote a price** | **R1 (gated)** | R1 | stays gated — **Polo-locked rows only**; no locked row → flag, never invent |

**Hard floor / gated by design:** every client-facing proposal requires **the Founder's approval before send** (the Founder sends — Bird is structurally send-incapable; the runtime denies send/delete/Bash). Prices come **only from Polo-locked rows**. Expansion fires **only on Kortney's sustained green light**. These three (client-facing approval, locked-price-only, health-gate) are hard gates that do not advance on eval evidence — they are the floor that keeps an unproven upsell from straining executive trust (`03_eval.md` hard gates #2/#5; same pricing/approval floor yourco proves on its own runtime, `runtime/autonomy-matrix.md`).

## Connectors (and the gate)
Bird is read/score/draft/post-only on every connector:
- **Workspace (read):** `loops/customer-health/*` (Kortney's reads — the trigger), `clients/<client>/*` (the engagement), `pricing/v0/*` (the only price source), `processes/ai-os-modules.md` + `employee-patterns*.md` (the role menu), `learnings/*`.
- **Workspace (write):** `clients/<client>/expansion/*` (scorecard, proposal draft, scope handoff, renewal brief) + `learnings/expansion/`.
- **Gmail (`contact@yourco.example.com`):** **draft** expansion/renewal emails; **send is must-approve** (the Founder sends — Bird is structurally send-incapable; the runtime denies send/delete/Bash globally).
- **Slack `#yourco-bird`:** post the needs-the Founder summary (digest to `#all-yourco`).
- **CRM (`crm/`):** read account/deal context; expansion logged as a new SOW/scope under the same agreement (David's system of record).

## Closed-loop wiring
- **Trigger:** Kortney's green light (event-driven), + a renewal-date watch (~60 days out). Dormant until the first green light.
- **Artifact:** the dated scorecard + proposal + scope-handoff under `clients/<client>/expansion/`.
- **Feedback:** the proposal's APPROVAL line (the Founder approves/kills) + the "did it convert?" note when the expansion lands or is declined.
- **Feed-forward:** patterns written to `learnings/expansion/` (what framing converted, what scorecard ranking proved right, what pricing objection surfaced), read at **Step 0** of the next run → behavior adjusts.

## Build status
- [x] Charter (`_README.md`) — tight, current
- [x] Discovery (`01_discovery.md`) — problem, Lemkin/NRR outcome, inputs/outputs, dormant-until-green-light
- [x] Build (this file) — expansion SOP + renewal motion + the three templates + connectors + closed loop
- [x] Eval set (`03_eval.md`) — test cases, rubric, hard gates, red-team, the NRR metric
- [ ] **DORMANT** — activates on Kortney's first green light (no live accounts yet — correct pre-revenue state)
- [ ] `contact@yourco.example.com` provisioned (manual — the Founder; not blocking the dormant build; runs under the Founder's identity at activation)
- [ ] Sustained-green window defined with Kortney (set at activation)
- [ ] First scorecard + proposal run against account #1 → calibrate the leverage ranking + proposal voice

## Known overlay decisions
- **Runs under the Founder's identity** until `contact@yourco.example.com` exists (same v0 convention as Atlas/Charles/Kortney); Slack signed "— Bird, YourCo Ops."
- **Kortney owns the gate; Bird owns the growth.** Bird never overrides a non-green read — siblings, the Founder conducts (`decisions/2026-06-07_agent-operating-model.md`).
- **Polo owns the numbers; Bird quotes only what's locked** — the pricing gate mirrors Reilly's and Bella's "never quote unlocked pricing."
- **Bird scopes; Kimi builds** — the approved scope handoff is the seam; Kimi's go-live gates then govern.
