# 2026-07-08 — The initiative loop: entity-level agency for the OS (Melanie)

## Decision
yourco gets a standing **initiative loop** — a daily run (weekdays 08:45 ET, after the morning loops
refresh the state) in which **Melanie** reads the company's goals, live state, learnings, and open
queue, and **originates up to three moves nobody scheduled** — executing the ones inside her earned
autonomy tier, escalating the rest to the Founder with reasoning. This is the missing organ between "a set of
scheduled loops" and "an entity that pursues its goals": initiative.

## Context
the Founder: "Giving our company its own soul… its own level of autonomy… its own goals and missions. Not on
a workflow level — on an entity level. It will know how to grow and understand." Analysis: the OS
already has the substrate of a functional self — identity (CLAUDE.md), behavior-changing memory
(learnings/ read at Step 0), settled will (decisions/), goals as live data (dashboard/goals.json),
self-observation (watchdogs/evals/Brett), self-modification (drift→invariant, skills library). What it
lacked was **origination**: nothing sat above the loops asking "given our goals and state, what should
yourco do today that nobody scheduled?" Melanie's roster role is literally "CEO in training" — this is
the training.

## Options considered
- **A new agent** for initiative — rejected: it's Melanie's named role; a 28th agent dilutes the org.
- **Extend Brett** — rejected: Brett is deliberately advisory-only (reflection without hands is a
  feature of his role, not a bug).
- **the Founder-triggered only** — rejected: that's the current state; initiative that waits to be asked isn't
  initiative.

## Why
The autonomy-by-default standard (2026-06-25) already says every action's default trajectory is full
autonomy earned on evidence, with control migrating to the reliability layer. The initiative loop is
that standard applied at the entity level — and it's the product thesis dogfooded ("the system keeps
learning your business and gets better over time").

## The boundary (the part that matters most)
**The company's "own goals" = the Founder's goals pursued autonomously — never goals it invents.**
- Melanie may **propose** new missions/targets; she may never self-adopt them. goals.json changes are
  the Founder's (or the Founder-approved) only.
- Initiative actions climb the same autonomy matrix as everything else: R1 floor on anything
  external-facing or novel; execute-without-asking only inside already-earned tiers (internal repo
  artifacts, drafts, prep, analysis). The approval gate (no send / no delete / no Bash on the host)
  physically bounds the loop regardless.
- Parked directions (self-serve SaaS, etc.) are off-limits even as proposals unless something material
  changed — the decisions log is the fence.
- Anti-spin per the loop contract: max 3 initiatives/day, no re-proposing a the Founder-declined item without
  new evidence, quiet days reported honestly ("no initiative worth your attention today").

## Reversibility
Disable the timer. The artifacts (loops/initiative/) remain as a record. If initiative quality is poor
(Kolby's eval review will see the accept/decline rate), it demotes to weekly or advisory-only.

## Mechanics
SOP `processes/loops/initiative.md` · prompt `runtime/prompts/initiative.md` · units
`yourco-initiative.{service,timer}` (Mon–Fri 08:45 ET) · output `loops/initiative/YYYY-MM-DD.md` +
a short Slack digest to `#all-yourco` signed Melanie · registry-sanctioned · watchdog row added.
Kolby's weekly eval-review scores initiative quality (proposed vs accepted vs declined) — the evidence
that earns the tier up, per the streak rule.
