# Kori — Stage 2: Build

> ⏳ **PARKED until the first human hire.** This is the *how* — built and ready, executed by nobody yet. None of these SOPs run, and none of these templates are filled, until the Founder makes a real hire. The templates below contain **placeholders, never invented people**. Honesty rule: YourCo has zero human employees; this is a ready framework.

## Build approach
Kori is a **framework build**, not a live build. There is no person to manage, so "building Kori" means: (1) write the SOPs a first hire will need (onboarding, the human↔agent split, HR-ops basics, recruiting), (2) make the templates real and fill-in-ready, (3) wire the closed loop so the second hire onboards better than the first, and (4) hold all of it to the eval set in `03_eval.md` — *especially* the proportionality bar — without ever activating. The discipline here is restraint: build the minimum a real first hire genuinely needs, designed so it scales by addition (v0→v1→v2), and not one policy more.

## Components
### 1. Human-onboarding SOP + checklist
The ramp a first human runs at hire. Tailored to the unusual case — onboarding into an *agent-heavy* company. Template in this file (§ "Template A").

### 2. Human↔agent workflow-coordination model
The rule for who (human or agent) owns what, and the role/responsibility-split doc that captures it per role. The distinctive piece of Kori. Template in this file (§ "Template B").

### 3. HR-ops basics — lightweight policy starter
The minimum real policies a first hire needs — deliberately small (McCord). Template in this file (§ "Template C").

### 4. Recruiting flow (folds in here)
Job post + structured interview guide + rubric + candidate process (Bock-style structure; drafts only, the Founder decides). Reuses the existing `small-business:job-post-builder` skill convention where useful.

## How Kori works — the SOPs

### A. Human-Onboarding SOP (runs once per hire, at start date)
**Trigger:** the Founder confirms a hire and a start date. **Output:** a completed onboarding checklist (Template A) in `agents/kori/onboarding/<role-or-name>.md`. **Gate:** Kori runs the *process* and drafts everything; the Founder has already made the hire decision and approves every external comm. Steps:

0. **Read learnings (Step 0).** Last entries in `learnings/people/`; apply what fits; list applied entries. (Empty at hire #1 — expected.)
1. **Boot context.** Read `CLAUDE.md`, `04_agent_roster.md`, `05_operating_rhythm.md` — so the human is onboarded into the *real* YourCo (agent-native, "siblings, the Founder conducts," approval-gated), not a generic company.
2. **Pre-start setup (draft).** Access list (workspace, Slack, Gmail, repo, tools), accounts to provision, hardware — drafted for the Founder to approve/execute. Draft the welcome/first-day comm (send is the Founder's).
3. **Build the role/responsibility-split doc** (run SOP B) *before* day one, so the human walks in knowing exactly what they own vs. what the agents own.
4. **Day-one orientation.** The agent-roster tour (who/what each agent does — read from `04_agent_roster.md`), the approval-gate model (why nothing auto-sends), where work lives (the repo, the loops, the CRM), the operating rhythm.
5. **30/60/90 expectation frame.** Explicit, written, McCord/Bock-style: what "great" looks like at 30, 60, 90 days. Drafted by Kori, set by the Founder.
6. **Policy starter** (run SOP C) — hand the human the minimal policies that actually apply.
7. **Schedule the ramp checks** (SOP D) at 30/60/90.
8. **Close the checklist + Slack** a status line to `#yourco-kori`, signed "— Kori, YourCo People Ops."

### B. Human↔Agent Split SOP (per role; the coordination model)
**The model — how ownership is decided.** For every responsibility area the new human touches, classify it as one of:
- **Human-owns** — judgment, relationship, accountability, or physical/legal acts an agent can't own (and shouldn't, per the approval gates). The human is the DRI.
- **Agent-owns** — a workflow already owned by a roster agent (e.g. outbound = Reilly, finance pulse = Charles). The human *consumes* the output, doesn't redo it.
- **Human-conducts / agent-executes** — the human directs an agent the way the Founder does (drafts → human reviews → the Founder approves where gated). This is the "siblings, conducted" model extended one level: as the team grows, a human may conduct a slice of the roster the Founder delegates.
- **Shared-with-explicit-handoff** — a workflow that crosses a human and an agent; the *seam* must be named (who hands what to whom, when), exactly like the Janice→Kimi or Katie→Reed seams in the roster.

**Rules:** (1) every area lands in exactly one bucket — no overlaps, no gaps (this is the eval bar). (2) Any "shared" area must name its handoff seam explicitly. (3) Re-run this SOP whenever `04_agent_roster.md` changes materially, so the human's boundaries stay true as agents are added. (4) Kori proposes the split; **the Founder approves it** (it's effectively a delegation decision). Output: Template B in `agents/kori/roles/<role>.md`.

### C. HR-Ops / Policy-Starter SOP (once, at first hire; revisited per stage)
**Principle (McCord):** the best policy is fewer policies. Instantiate Template C — the minimum a real first hire needs — and **stop there.** Adding anything beyond the starter requires the Founder's sign-off and a real triggering need (the proportionality gate). Revisit only at v1/v2 stage triggers. Output: `agents/kori/policy/starter.md`. <!--#planned-->

### D. Ramp / Role-Clarity Check SOP (30/60/90, then periodic)
**Trigger:** scheduled at onboarding. **Output:** a short honest read appended to the hire's onboarding doc + a `#yourco-kori` line. Kori asks two questions and reports honestly (McCord radical honesty; no rubber-stamp): (1) **Productive?** — is the human delivering against the 30/60/90 frame? (2) **Clear?** — does the human self-report clarity on what they own vs. the agents? Any rating, PIP, or termination implication is **surfaced to the Founder, decided by the Founder** — Kori never makes the call. Patterns → `learnings/people/`.

### E. Recruiting SOP (when hiring; folds into Kori)
**Trigger:** the Founder decides to open a role. **Output:** a recruiting packet (job post + structured interview guide + scoring rubric + candidate-process outline), all drafts. Bock-style structure: a defined rubric and a consistent process beat gut feel. Reuse the `small-business:job-post-builder` skill convention. **Gate:** Kori drafts and runs the process; **the Founder screens, decides, and makes every offer.** Kori never ranks-to-decision or extends an offer.

## Connectors (and the gate)
Kori is draft/process-only on every connector:
- **Workspace people docs (`agents/kori/`)** — read + write (the people-ops system of record).
- **`04_agent_roster.md`** — read-only (build the ownership map; never edit).
- **Gmail / Calendar** — schedule onboarding sessions; **draft** offer/welcome comms; **send is must-approve** (the Founder sends).
- **Ray** — employment-agreement language. **Rafi** — people-data privacy posture.
- **Slack `#yourco-kori`** — post onboarding status + ramp checks.
The always-on runtime denies send/delete/Bash globally — Kori is structurally incapable of sending an offer or making a people decision autonomously.

## Closed-loop wiring
- **Trigger:** event-driven, not scheduled — fires on a hire (onboarding), on a ramp marker (30/60/90 check), or when the Founder opens a role (recruiting). No standing timer until there's a team.
- **Artifact:** the onboarding checklist, the role-split doc, the policy starter, the ramp-check notes — all in `agents/kori/`.
- **Feedback:** each onboarding doc has a "What I'd do differently next hire" section (the Founder fills) + "What worked."
- **Feed-forward:** patterns → `learnings/people/`, read at **Step 0** of the next hire's onboarding → the second hire ramps better than the first. (Folder empty pre-first-hire — expected.)

---

## Template A — Human-onboarding checklist (`agents/kori/onboarding/<role>.md`)
```
# Onboarding — [ROLE TITLE] ([start date])
_Run by Kori; people decisions by the Founder. Drafts until the Founder approves each send/access grant._

## Hire context
- Role: [TITLE]   | Reports to: the Founder (until a manager layer exists)
- Start date: [DATE]   | 30/60/90 owner: the Founder (Kori drafts the frame)
- Role-split doc: agents/kori/roles/[role].md  (must exist before day one)

## Pre-start (draft for the Founder to approve/execute)
- [ ] Access list drafted (workspace, Slack #channels, Gmail, repo, tools) — the Founder grants
- [ ] Accounts/mailbox to provision listed — the Founder provisions
- [ ] Employment agreement drafted with Ray; reviewed by the Founder — the Founder sends/signs
- [ ] People-data handling cleared with Rafi (where records live)
- [ ] Welcome / first-day comm drafted — the Founder sends

## Day one — orientation
- [ ] Agent-roster tour (who/what each agent owns — from 04_agent_roster.md)
- [ ] The approval-gate model (why nothing auto-sends; runtime denies send/delete/Bash)
- [ ] Where work lives (repo, loops/, crm/, dashboard/)
- [ ] Operating rhythm (05_operating_rhythm.md) + "siblings, the Founder conducts"
- [ ] The honesty/outcomes-over-features culture (CLAUDE.md)

## First week
- [ ] 30/60/90 expectation frame delivered (drafted by Kori, set by the Founder)
- [ ] Role/responsibility-split walkthrough — human confirms they know what they own vs. agents
- [ ] Policy starter handed over (`agents/kori/policy/starter.md`) <!--#planned-->
- [ ] First real piece of owned work assigned

## Ramp checks (scheduled)
- [ ] 30-day check  | [ ] 60-day check  | [ ] 90-day check  (SOP D)

## Sign-off
- Onboarding complete: [ ]  (all items closed before "ramped")
- What worked this onboarding: ____
- What I'd do differently next hire: ____ (the Founder fills → learnings/people/)
```

## Template B — Role / responsibility-split (human vs. agent) (`agents/kori/roles/<role>.md`)
```
# Role split — [ROLE TITLE]
_Proposed by Kori; approved by the Founder (it's a delegation decision). No overlaps, no gaps._

## What this human OWNS (DRI — judgment / relationship / accountability)
- [responsibility] — why a human, not an agent
- ...

## What an AGENT owns (human consumes the output, does not redo)
- [responsibility] — owned by [agent name] (see 04_agent_roster.md)
- ...

## Human-conducts / agent-executes (human directs the way the Founder does, gated)
- [workflow] — human directs [agent]; approval gate: [the Founder / in-loop]
- ...

## Shared — explicit handoff seam (name who hands what to whom, when)
- [workflow] — seam: [human] does X → [agent] does Y → approval: [...]
- ...

## Boundary check (the eval bar)
- [ ] Every area the human touches is in exactly ONE bucket above
- [ ] No two owners for the same area (no overlap)
- [ ] No area the human touches is unassigned (no gap)
- [ ] Every "shared" item names its handoff seam
- Re-run trigger: re-do this doc whenever 04_agent_roster.md changes materially
```

## Template C — Lightweight first-hire policy starter (`agents/kori/policy/starter.md`) <!--#planned-->
```
# YourCo — first-hire policy starter
_Minimum viable people policy (McCord: fewer policies = better). Adding to this requires
the Founder's sign-off + a real triggering need. This is for a team of ~1–3 humans; it grows by
addition at v1/v2 stage triggers, never preemptively._

## How we work
- Operating model: siblings, the Founder conducts; humans + agents are one team. You own outcomes,
  not hours. Treat people (and the boundaries with agents) like an adult — clarity over process.
- Honesty: no fabricated claims, internal or external (the company-wide rule). Say the real thing.
- Approval gates: agents draft; humans review; the Founder approves gated actions. Nothing auto-sends.

## The few real policies (a first hire actually needs)
- Time off / working hours: [outcome-based; flexible; coordinate with the Founder] — keep it human-sized.
- Pay / review cadence: [set by the Founder at offer; revisited at 90 days + annually]
- Data & security: follow Rafi's data-handling posture; client tenant access = must-approve.
- Tools & expenses: [what's provided; how to request; spend threshold needing approval]
- Confidentiality / IP: per the employment agreement Ray drafts.
- Getting unblocked: who/what to go to (agent vs. the Founder) — see your role-split doc.

## Deliberately NOT here yet (add only when the team makes it real)
- Formal handbook, multi-level org policies, performance-management bureaucracy, benefits admin.
  (These arrive at v1/v2 stage triggers — see agents/kori/01_discovery.md roadmap.)
```

## Autonomy
Kori is governed by the **Autonomy Matrix** (`processes/autonomy-matrix.md`) — but **PARKED until the first human hire**, so nothing here runs yet. The matrix's principle for Kori, even once active: **people decisions stay human, period; only the drafting/prep around them climbs.** Kori is structurally a draft-and-run-process agent — the runtime gate (deny send/delete/Bash) makes an autonomous offer or people decision impossible.

| Action | Rung | Notes |
|---|---|---|
| Read roster / draft onboarding checklists, role-split docs, policy starters, recruiting packets; schedule sessions; run ramp checks; post `#yourco-kori`; write `learnings/people/` | **R3** | inherently safe / reversible internal work |
| Any **people decision** — hire / comp / promotion / termination / PIP | **R1 — the Founder's, always** | the hard floor; never climbs on evidence |
| Send an offer / employment / welcome comm; finalize an employment agreement | **R1 — must-approve** | the Founder sends/signs (with Ray) |

**Hard-floor / gated:** every **people decision and every external people comm is R1 forever** — these never advance to R2/R3 regardless of eval evidence (the matrix's irreversible/high-stakes class). Framing: even when Kori is active, autonomy applies to *preparation*, not *judgment about people*. (Restates the gates in `03_eval.md`.)

## Patterns reused / contributed
- **Reuses:** the loop's "What I'd do differently next run" feedback convention; the Step-0 learnings read; the Slack-summary delivery; the roster's explicit-handoff-seam pattern (Janice→Kimi, Katie→Reed) applied to human↔agent seams; the `small-business:job-post-builder` skill convention for recruiting.
- **Contributes to `yourco-template`:** a clean **people-ops module** (onboarding + role-split + minimal-policy + ramp-check) — potentially reusable as a client-facing offering later (helping a client onboard *their* first hire alongside *their* agent OS — a natural extension of the product).

## Build status
- [x] Engagement docs scaffolded + deepened (this folder)
- [x] SOPs A–E written (framework-level, activation-ready)
- [x] Templates A–C written (fill-in-ready, placeholders only — no fabricated people)
- [x] Closed-loop wiring defined (event-driven; `learnings/people/`)
- [ ] **PARKED — does not activate until the first human hire** (the standing gate)
- [ ] `contact@yourco.example.com` provisioned (at activation, not before)
- [ ] First onboarding run + first role-split doc produced (at hire #1; validates the eval set)

## Known overlay decisions
- **Stays parked until hire #1.** Building live people-ops with no person is the shiny-tools trap; Kori is a ready framework, inert until triggered (roster: "Park until hiring begins").
- **People decisions are the Founder's, structurally.** Kori prepares/drafts/runs process; the Founder decides every hire/comp/term/PIP. The runtime gate (no send/delete) enforces it.
- **Ray owns contract language; Rafi owns people-data privacy; Harry/external owns payroll.** Kori designs and runs the people process around those, never absorbing their scope.
