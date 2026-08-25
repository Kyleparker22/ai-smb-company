---
name: write-learning
description: Write a learnings/ entry — an operational pattern observed in practice that should adjust how agents behave on their next run. Use when any run surfaces a repeatable pattern, gotcha, or win that isn't a settled decision or a step-by-step procedure.
---

# write-learning

## Canonical doc
`learnings/_README.md`.

## Steps
1. File: `learnings/<domain>/YYYY-MM-DD_<short-slug>.md` — one pattern per entry. Domains: `brand-voice` (Luka) · `sales-copy` (Reilly) · `video-production` (Reed) · `pricing` (Polo) · `content` (Katie) · `finance` (Charles) · `ops` (Atlas, cross-cutting) · `web` (Webb) · `delivery` (Janice/Kimi) · `advisor` (Brett) · `qa-eval` (Kolby) · `compliance` (Rafi) · plus `ceo` / `strategy`.
2. Format:
   ```
   YYYY-MM-DD — [short title]

   Source: [which agent observed it; which artifact or event]
   Pattern: [the underlying pattern — 1–3 sentences, evidence-based]
   Implication: [what future runs should do differently]
   Audience: [which agents / domains should read this on their next run]
   ```
3. **Linking to another learning — use the full filename, including the date:** `[[2026-07-06_cross-session-drift]]`, **not** `[[cross-session-drift]]`. This repo *is* an Obsidian vault (`.obsidian/` is committed), so a link that doesn't match a filename renders unresolved and never enters the graph or backlinks. The bare-slug form is correct for **memory** files (they're named by slug) and wrong here — carrying that habit across is how 8 of 13 links ended up dangling before 2026-08-09. A link to an entry that doesn't exist yet is still fine: it marks something worth writing.
4. Any agent writes to its own domain; Kolby and Brett (cross-cutting observers) may write to any domain.
5. Loops read their domain's recent entries (last ~5, past 30 days) as **Step 0** and list what they applied in the artifact.

## Gotchas
- Evidence-based only — a learning cites the artifact or event it came from, not a hunch.
- If the pattern is really a reusable **procedure** (numbered steps), it belongs in `.claude/skills/` (see `create-skill`); a learning can point to the skill it spawned.
- Never delete entries; after ~90 days internalized patterns get `[absorbed]` in the title.
