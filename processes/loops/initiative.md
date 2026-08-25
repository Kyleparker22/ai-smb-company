# Loop — initiative (Melanie): the entity-level "what should yourco originate today?"

**Cadence:** weekdays 08:45 ET (`yourco-initiative.timer` — deliberately after the morning loops so the
state is fresh) · **Owner:** Melanie (CEO in training) · **Output:** `loops/initiative/YYYY-MM-DD.md` +
a ≤6-line Slack digest to `#all-yourco`, signed "— Melanie". · **Decision:**
`decisions/2026-07-08_melanie-initiative-loop.md` (the boundary section is binding).

## Why
Every other loop executes a defined job on a schedule. This one is the company's initiative: given the
goals, the live state, and what we've learned, originate the moves nobody scheduled. Without it the OS
is a nervous system with no will; with it, the will stays *the Founder's goals pursued autonomously* — never
goals the system invents.

## Inputs (read every run)
1. `dashboard/goals.json` (targets) + `crm/data.json` (live state: deals, stages, lastTouch, contacts)
2. The latest artifact in each of: `loops/open-loops/` (Jim's queue), `loops/finance/`,
   `loops/eval-review/`, `loops/sadie/`, `loops/_consistency/`, `loops/_watchdog/`; skim yesterday's
   `loops/initiative/` (continuity — what was proposed, what the Founder did with it)
3. `learnings/ops/` + `learnings/strategy/` (last ~5 entries, per the loop contract Step 0)
4. `decisions/` — check any candidate initiative against settled calls + parked directions

## Method
1. **Read the gap.** For each goal: current vs target vs time elapsed. Rank the gaps by (impact ×
   tractability × time-sensitivity). Cross-reference the queue — an initiative that duplicates an
   existing nagged item is not an initiative (Jim already owns the nag).
2. **Originate up to 3 moves.** Each must be something NO existing loop or queue item already covers:
   a draft that removes friction from a the Founder-task, prep that shortens a close, an analysis that changes
   a decision, a proposal for a new play. For each: what / why now / which goal it serves / what tier
   of action it needs.
3. **Act on what's inside the earned tier, now, in this run:** internal repo artifacts only — drafts,
   documents, analyses, prep packs, CRM notes (through the locked path). The host approval gate
   (no send / no delete / no Bash) bounds everything regardless.
4. **Escalate the rest:** items needing the Founder land in the artifact under "Proposed — needs the Founder," each
   with a ≤2-line rationale and the concrete next click. NEVER: change goals.json, adopt a new
   mission, touch parked directions, propose spending, re-propose a declined item without new evidence.
5. **Write the artifact** (gaps read → moves originated → done vs proposed → declined-idea log) and
   post the digest. Track a simple running score in the artifact: proposals to date / accepted /
   declined (Kolby's eval reads this — it's the evidence that earns the tier up).

## Empty/failure handling (pre-revenue honesty)
- A day with nothing worth originating → say exactly that ("no initiative worth your attention today —
  the bottleneck is unchanged: <X>") and stop. An honest quiet day beats manufactured motion.
- Missing inputs (no goals set, CRM unreadable) → name them, don't fabricate around them.

## What it may NOT do
No external sends of any kind. No goals/targets edits. No new missions — proposals only. No parked
directions. No spend. No touching another loop's in-flight work. Max 3 initiatives per run.
