---
name: create-skill
description: Add a new skill to yourco's skill library. Use whenever you (any agent, any loop) solve something reusable — a procedure of 3+ steps that a future run would otherwise have to be re-told or re-derive. Also use when the Founder says "make that a skill."
---

# create-skill — the meta-skill

## When a skill is the right container
Ask which of the three memory surfaces fits:
- A **choice** was made (scope, stack, pricing, moat) → `decisions/YYYY-MM-DD_slug.md` (see `log-decision`)
- A **pattern** was observed that should adjust behavior → `learnings/<domain>/` (see `write-learning`)
- A **procedure** was worked out that will be executed again → a skill, here.

Rough test: if the artifact's natural form is numbered steps someone follows, it's a skill. If it's "we noticed X, so do Y differently," it's a learning.

## How
1. Create `.claude/skills/<kebab-name>/SKILL.md`.
2. Frontmatter: `name` (same as folder) + `description`. The description is the **trigger** — write it as "Use when…" so a future agent scanning the library knows instantly whether it applies.
3. Body, kept thin:
   - **When** — trigger conditions, and any conditions where it does NOT apply
   - **Steps** — the procedure, numbered; split repo steps from host/VPS steps if both exist (headless loops can't touch the host)
   - **Gotchas** — the mistakes this skill exists to prevent
   - **Canonical doc** — if an SOP already covers it (in `processes/`, `runtime/`, etc.), point there and include only the delta. Never duplicate a procedure into two files — the skill is the pointer, the doc is the truth.
4. **Register it everywhere a skill is declared — there are two, and step 4 used to name only one.**
   - `.claude/skills/_README.md` — a one-line entry under "Current skills."
   - **`dashboard/skills.py` §TRACE** — `slug: (artifact-glob | None, expected-days | None, trigger)`.
     **Miss this and HQ still lists the skill, but with a blank trigger and verdict `unmeasurable`** —
     it looks like a skill nobody can measure rather than one nobody registered. If the skill produces
     a distinctive artifact, give the glob; if it genuinely leaves no trace, pass `None` deliberately.
     The trigger string is what the Founder reads to remember the skill exists, so write it as the moment,
     not the topic ("A service is needed and has no MCP", not "CLI building").
   - The skill *counts* in `00_README.md`, `07_RULES.md` and `START-HERE.html` are self-declaring
     (`#count: dirs .claude/skills/*`) and need no edit — but run `python3 runtime/doc_claims.py`
     to confirm, because one of them was a hand-typed number until 2026-08-24 and had drifted by two.
5. Commit (headless loops: the run's normal commit+push covers it; the VPS and Cowork share this repo).

## Gotchas
- Don't write a skill for something done once that won't recur — that's log noise, not a skill.
- Don't embed secrets, tokens, or host paths that belong in env files.
- Headless constraint: loop runs have **no Bash** (approval gate). A skill whose steps need shell commands must mark them as Cowork/host-only steps.
