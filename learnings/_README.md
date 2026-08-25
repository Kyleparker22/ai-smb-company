# learnings — yourco's continuous-improvement substrate

> ⚠️ **NOT YOURS YET.** Patterns **the source company observed in practice.** Useful as examples of the format and of
what is worth writing down. Yours will be different — that is the point of the folder.


The substrate that makes yourco's agents continuously better. `decisions/` records settled calls; `learnings/` records operational patterns observed in practice that adjust how agents behave on their next run.

## The closed loop
Kolby (and any agent) observes a pattern → writes a learning entry → the relevant agents read their domain's recent entries at the start of their next run (Step 0) → behavior adjusts → Kolby observes again. This is the feed-forward step CLAUDE.md's closed-loop discipline calls for — the piece that turns Kolby's evals into behavior change instead of a grade into the void.

## What goes in
Short markdown entries, one pattern each. Filename: `YYYY-MM-DD_short-slug.md`.

## Entry format
```
YYYY-MM-DD — [short title]

Source: [which agent observed it; which artifact or event]
Pattern: [the underlying pattern — 1-3 sentences, evidence-based]
Implication: [what future runs should do differently]
Audience: [which agents / domains should read this on their next run]
Triggers: [when this should load — see below]
```

### Triggers (added 2026-08-13) — the retrieval half
`Audience:` says *who* should read it. **`Triggers:` says *when* it should load**, and it is the line the machine reads. Domain is a **filing** decision made when the entry is written; relevance is a **retrieval** decision made when a run starts — and the gap between them is the known failure: the right learning exists, in the wrong folder, and the run that needed it never saw it. (Three current entries are addressed to "any agent authoring a loop prompt" and sit in three different domains.)

A trigger is either a **phrase** — every word of it must appear in the run's context — or a **typed** trigger:

| Typed trigger | Fires when |
|---|---|
| `agent:<name>` | that agent is running |
| `loop:<name>` | that loop is running |
| `domain:<name>` | that domain is the run's declared domain |
| `skill:<name>` | the run invokes that skill |
| `path:<substring>` | the run touches a matching file path |
| `always` | every run (use sparingly — two entries have it today) |

Triggers are OR'd; the words inside one phrase are AND'd. Matching is plain token/substring matching — **no model call**, per `learnings/ops/2026-08-09_inference-only-where-judgment-is-needed.md`.

**Retrieval is `runtime/learning_triggers.py`.** It ranks trigger hits above `Audience:` name-matches above the old domain+recency read, and it **keeps the domain+recency floor** — so an entry with no `Triggers:` line is never dropped, only harder to reach. Every result names *why* it matched, reports how many matched below the display cap, and reports how many entries in the store are still running on fallback. Check the store with `python3 runtime/learning_triggers.py --check` (coverage, unknown trigger kinds, and entries past 120 days that were never marked `[absorbed]`).

## Domains (subfolders)
- `brand-voice/` — Luka
- `sales-copy/` — Reilly
- `video-production/` — Reed
- `pricing/` — Polo
- `content/` — Katie
- `finance/` — Charles
- `ops/` — Atlas (cross-cutting operations)
- `web/` — Webb
- `delivery/` — Janice / Kimi (fills when engagements land)
- `advisor/` — Brett
- `qa-eval/` — Kolby's own meta-learnings
- `compliance/` — Rafi

## Who writes / who reads
- **Writes:** any agent may write to its own domain. Kolby and Brett — the cross-cutting observers — may write to any domain.
- **Reads:** every loop reads its domain's most recent entries (last ~5, past 30 days) as **Step 0**, applies what fits, and lists what it applied in the artifact's "Learnings applied this run."

## Lifecycle
Entries are never deleted. After ~90 days, if a pattern has been internalized (Kolby sees no recurrence), mark the title `[absorbed]` — historical, no longer load-bearing.

## learnings vs decisions vs skills
- `decisions/` — what was **chosen** and why (settled, durable).
- `learnings/` — what was **observed** in practice (operational, behavior-adjusting).
- `.claude/skills/` — what we know **how to do** (repeatable procedures with trigger conditions). If a learning is really numbered steps someone will execute again, write it as a skill (`.claude/skills/create-skill/`) and let the learning point to it.

## Wiring (2026-07-05)
Every runtime loop prompt now names its Step 0 domain(s) in its footer and complies with `runtime/prompts/_loop-contract.md`, which carries the full Step 0 (read learnings + check skills) and feed-back (write learnings/skills) language. No loop is exempt.

## A note on timing
Pre-launch, most loops honestly report "quiet — no data yet," so these folders start empty. That is expected. The substrate is wired now so that the moment real volume starts — outreach, clients — the loop is already closed and patterns accumulate from day one.
