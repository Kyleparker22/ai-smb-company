# Client folder created at first call (Stage 0 trigger moved earlier)

**Date:** 2026-08-07 · **Decided by:** the Founder

## Decision
A prospect gets a `clients/<slug>/` folder (cloned from `_yourco-template`, per the `scaffold-engagement` skill) at **first real call or proposal sent — whichever comes first**. Previously: proposal-sent or signed. Every new folder carries the **"How the OS works this client" agent map** in its `_README.md` from day one — agents help through the entire per-client process.

## Context
Same-day cluster of structure calls (see `2026-08-07_southern-cut-one-platform.md` and the clients/→agents/ split): the Founder standardized "one client, one folder, agents mapped end-to-end" across sample-client / sample-realty / prospect-a, then set the creation trigger: "when I either have the first call or a proposal sent to a prospect, they get a folder created for everything to go to."

## Options considered
1. Keep proposal-sent-or-signed (old rule) — but first-call artifacts (call notes, transcripts, demo prep) were landing homeless or in meetings-tool limbo until a proposal existed.
2. **First-call-or-proposal-sent (chosen)** — the folder exists the moment artifacts start existing.
3. Folder for every warm lead — rejected: leads with no conversation stay CRM rows; folders for non-conversations is clutter.

## Why
Meetings/transcripts/demos begin at the first call, and the OS only compounds if artifacts land somewhere from minute one (Sample Client's 8/6 meeting digest proved the value of same-day capture). The scaffolder makes creation ~free, so the old "wait for a proposal" economy bought nothing.

## Reversibility
Trivial — move the trigger back in `02_delivery_loop.md` §0 + `scaffold-engagement` + CLAUDE.md if folder clutter from no-show prospects ever outweighs capture value. Dead prospects' folders `git mv` to `_archive/`.

## Surfaces updated in this commit
`02_delivery_loop.md` §0 · CLAUDE.md delivery-loop line · `.claude/skills/scaffold-engagement/SKILL.md` (trigger + post-scaffold agent-map step) · `clients/_yourco-template/_README.md` (agent-map stub added) · `clients/sample-realty/BUILD-NOTES.md` (stale trigger note).
