---
name: daily-log
description: Write the end-of-session handoff note in daily-logs/ so the next session picks up with zero re-explaining. Use at end of any working session, or when the Founder says "wrap up" / "end of day" / "log today."
---

# daily-log

## Steps
1. File: `daily-logs/[C] YYYY-MM-DD.md` (today's date; if one exists for today, update it rather than creating a second).
2. Frontmatter:
   ```
   ---
   author: claude
   type: daily
   date: YYYY-MM-DD
   status: [session ongoing | session closed]
   ---
   ```
3. Body — `# Session Log — <Weekday, Month D YYYY>`, one bold summary line, then:
   - **What We Worked On** — bullets, plain language
   - **What Was Built or Changed** — concrete artifacts, files, systems
   - **Decisions Made** — with pointers to `decisions/` entries written
   - **Open Threads / Next Session** — what the next session should pick up first
4. Note whether the work is committed/pushed (the runtime syncs from `main` — uncommitted work is invisible to the VPS).

## Gotchas
- The log is a **handoff**, not a diary — write for the next session's Step 0 skim: what's load-bearing, what's unfinished, what's waiting on the Founder.
- Anything strategic that changed should already live in `CLAUDE.md`/`decisions/`/`learnings/` — the log points there, it is not the system of record.
