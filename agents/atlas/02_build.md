# Atlas — Stage 2: Build

## Build approach
Atlas v0 is built from existing Cowork primitives (scheduled tasks + MCP connectors + workspace files) rather than from `yourco-template`, because `yourco-template` does not yet exist as code. As patterns emerge in this build, they get captured as the first scaffolding chunks of `yourco-template`.

This is the dogfooding payoff: building Atlas teaches us what the template needs.

## Components

### 1. Monday Briefing SOP
Lives at `/processes/loops/monday-briefing.md`. The source of truth for Atlas's first use case. Updated by the Founder's feedback in the artifact's "What I'd do differently next run" section.

### 2. Scheduled task
`yourco-atlas-monday-briefing` — runs Monday at 7:30am ET, after sales (7:08) and finance (7:24) have produced their artifacts. The task is a tiny launcher that loads CLAUDE.md + the SOP + the most recent sales and finance artifacts, then executes.

### 3. Triple-delivery pattern
Atlas delivers the briefing three ways simultaneously:
- **Markdown artifact** at `/loops/monday-briefing/YYYY-MM-DD.md` — canonical, queryable, version-controllable
- **Gmail draft** in the Founder's inbox — the habitual consumption surface
- **Slack post** to `#all-yourco` — ambient awareness

The artifact is the source of truth; the email and Slack are notifications.

### 4. Synthesis logic
Atlas does not redo the work of the sales and finance loops. It reads their artifacts (already produced minutes earlier on Monday morning) and synthesizes them, adding:
- Cross-cutting watchdog signals (e.g., "Finance flagged a margin concern AND sales flagged a stalled prospect — they may be related")
- This-week prioritization across both
- One paragraph framing for the week

## What gets captured into `yourco-template`
As Atlas's build settles, these reusable pieces get extracted into the future `yourco-template`:

- **The triple-delivery pattern** (artifact + email draft + Slack post) — every YourCo digital employee will likely use this
- **The scheduled-task-as-launcher pattern** — small task, SOP in version control
- **The closed-loop feedback section** ("What I'd do differently next run") — should be a template primitive
- **The watchdog-trigger format** — should standardize across all engagements
- **The exec-readout brevity rule** (≤ 800 words, ≤ 5 min read) — formatting primitive

These extractions happen during weekly iteration, not as part of v0 build.

## Build status
- [x] SOP written (`/processes/loops/monday-briefing.md`)
- [x] Scheduled task created (`yourco-atlas-monday-briefing`)
- [x] Pipeline updated (Atlas at status `build`)
- [ ] First Monday run executes successfully (Stage 4 — Monday 7:30am)
- [ ] Eval harness wired (Stage 3 — to follow)
- [ ] `contact@yourco.example.com` provisioned (manual — the Founder, not blocking v0)
- [ ] Atlas Slack bot user provisioned (manual — the Founder, not blocking v0)

## Autonomy
Governed by `processes/autonomy-matrix.md` (the standard set 2026-06-25; advancement gated on Kolby's eval-vs-reality record). Atlas is an **observe-and-report** agent: it reads OS state + sibling artifacts and emits a synthesis — it never commands another agent and never sends anything externally. So most of its surface starts at the ceiling already.

| Atlas action | Starts | Ceiling | Advances on |
|---|---|---|---|
| Read sales/finance artifacts, pipeline, cost, calendar | **R3** | R3 | inherently safe (read-only) |
| Write the briefing artifact (`loops/monday-briefing/*.md`, git) | **R3** | R3 | reversible in git |
| Slack post to `#all-yourco` / `#yourco-atlas` | **R3** | R3 | reversible internal post |
| Gmail **draft** in the Founder's inbox | **R3** | R3 | draft only; a human commits the send |
| Fire a watchdog flag / escalation | **R3** | R3 | a flag is a notification, not an action |

**Hard floor (R1, never climbs):** sending any external email (Atlas drafts; the send is gated), posting to any non-Atlas/non-digest channel, and touching any client tenant. Atlas **observes, it does not direct** — it has no rung on which it issues commands to other agents; cross-agent action is always a recommendation a human or the owning agent acts on. Per-run cost > $0.50 / weekly > $2 trips the cost watchdog regardless of rung (see `03_eval.md`).

## Known overlay decisions (deviations from a "clean" build)
- **v0 runs from the Founder's account, not Atlas's own.** Until `contact@yourco.example.com` exists, all actions are taken under the Founder's Gmail and Slack identity. The Slack summary is signed "— Atlas" by convention; the email draft is in the Founder's inbox. This is acceptable for v0; move to Atlas's own identity in v1.
- **No yourco-template means hand-built integrations.** Logged here so the template can extract the patterns.
