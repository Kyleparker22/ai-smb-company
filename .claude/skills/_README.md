# .claude/skills/ — yourco's skill library

Reusable **procedures** any agent (Cowork session or headless loop) can invoke instead of being re-told how. Skills are the how-to complement to the two other institutional-memory surfaces:

- `decisions/` — what we **chose** and why (settled calls)
- `learnings/` — what we **observed** in practice (behavior-adjusting patterns)
- `.claude/skills/` — what we know **how to do** (repeatable procedures with trigger conditions)

## Format
One folder per skill, `SKILL.md` inside, YAML frontmatter with `name` + `description`. The `description` is the trigger — write it so an agent scanning the list knows exactly when the skill applies. Claude Code auto-discovers these for every session against this repo, including the headless VPS runs (the repo is git-synced; skills ride along).

## The rule (matches the loop contract)
- **Before working (Step 0):** check whether a skill already covers the task. If one does, follow it — don't re-derive the procedure.
- **After working (feed-back):** if you solved something reusable — a procedure with 3+ steps you'd otherwise have to be re-told — write it as a skill (see `create-skill/`). One-off observations go to `learnings/`; choices go to `decisions/`.

## Style
Skills are **thin**. Trigger + steps + gotchas + a pointer to the canonical doc. If a canonical SOP exists (e.g. `runtime/agent-wiring-checklist.md`), the skill points at it and adds only what the doc doesn't say. Never fork the truth into two places — if the procedure changes, update the canonical doc and keep the skill as the pointer.

## Current skills
- `create-skill` — how and when to add a skill to this library (the meta-skill)
- `wire-new-agent` — create/activate an agent end-to-end (docs → roster → Slack → listener → registry)
- `add-runtime-loop` — put a new recurring loop on the 24/7 VPS runtime
- `run-coaching-session` — put a connector or advisor through authored drills, judge against the rubric, record it. You judge; `crm/coach.py` keeps score
- `design-surface` — decide palette/type/layout **before** writing CSS; calibrate utilitarian vs editorial treatment. Defers to `brand/DESIGN.md`, never copies it
- `build-cli-connector` — reach a program that has **no MCP**: pick the delivery path first (artifact · wrapper-injection · MCP), because a headless loop cannot shell out
- `deploy-vps-daemon` — deploy a long-running daemon/connector on the VPS without the known gotchas
- `scaffold-engagement` — audit → client engagement folder at ~80% in one command
- `promote-warm-lead` — graduate an Instantly warm reply into the native CRM
- `log-decision` — write a decision-log entry in the house format
- `write-learning` — write a learnings/ entry in the house format
- `daily-log` — end-of-session handoff note in `daily-logs/`
- `tool-triage` — evaluate an external tool/repo/**or piece of content** (article, transcript, book, operator philosophy) for yourco (the "what are your thoughts on X?" procedure)
- `show-surface` — put a local surface on the Founder's screen or into a sendable link (launch.json → start by name → verify → screenshot)
- `wire-credentialed-connector` — land any new API key/OAuth credential: env path + scopes up front, live verify, register
- `log-build-cost` — log per-client token + tool spend to `clients/<client>/cost.md` by phase (discovery/build/tools/run); Charles rolls up at monthly close
- `log-internal-cost` — log spend on yourco ITSELF (the OS, site, offerings, `Pre Build Ideas/`, agents, the app) to `finance/token_spend.md`; the non-client twin of `log-build-cost`. Written 2026-08-23 after finding the 577-file `Pre Build Ideas/` build had **zero** cost rows.
- `log-build-session` — journal the **time + the steps** of a client build (`runtime/build_journal.py`) so the next one is estimable; `--stop` emits the log-build-cost ledger row, so the two never drift
- `advisory-panel` — simulated expert review panel (named AI/business minds vs current state); on-demand before major decisions + Brett quarterly; convergences-only, internal-only
- `promote-intent-signal` — graduate a Sadie intent signal into the CRM (identity + vendor check, then company/deal + Hot List pill); the ONLY path a signal becomes a CRM row
- `visual-brand-qa` — vision-model pass/fail QA of any generated visual against `brand/DESIGN.md` + the credibility gate, before it routes to the Founder (producers invoke at hand-off; Kolby spot-checks weekly)
