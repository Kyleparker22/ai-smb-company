# 2026-07-05 — Skills library + Step 0 wired into every loop

**Decision** — yourco gets a third institutional-memory surface, `.claude/skills/` (repeatable procedures with trigger conditions), and the learnings feed-forward loop is wired into **all** runtime prompts: every loop reads its named `learnings/` domain(s) + checks the skill library as Step 0, and writes back reusable patterns (learnings) or procedures (skills) before reporting done.

**Context** — An audit found the closed-loop discipline was only aspirational: 14 learnings existed but just 2 of 18 loop prompts were instructed to read them, and no skill library existed at all — agents re-derived procedures (agent wiring, VPS deploys, engagement scaffolding) every time or waited to be re-told.

**Options considered**
- Per-prompt full Step 0 language in each of the 18 prompts — verbose, drifts, 18 places to update.
- Keep learnings-only, no skills — leaves procedures (the most re-told category) uncaptured; learnings are observations, not how-tos.
- Chosen: full Step 0/feed-back language once in `runtime/prompts/_loop-contract.md` (which every prompt already complies with), one domain-naming footer line per prompt, and a thin skill library seeded from procedures already proven in production.

**Why** — One source of truth for the mechanics, per-loop specificity only where it differs (the domain). Skills are thin pointers to canonical docs (`runtime/agent-wiring-checklist.md` etc.), so the truth never forks. The library is git-synced, so headless runs get it for free. Seeded skills (9): create-skill, wire-new-agent, add-runtime-loop, deploy-vps-daemon, scaffold-engagement, promote-warm-lead, log-decision, write-learning, daily-log — every one grounded in a procedure already executed successfully, none speculative.

**Reversibility** — Fully reversible: delete `.claude/skills/`, strip the footer lines and the two contract sections. Revisit if Kolby's eval shows loops padding forced learnings/skills to satisfy the feed-back rule — the contract already says "most runs produce neither; never pad," and that line is the guard to watch.
