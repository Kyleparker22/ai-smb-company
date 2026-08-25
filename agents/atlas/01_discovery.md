# Atlas — Stage 1: Discovery

## What this agent is
Atlas is the dogfood digital employee that proves YourCo's delivery model on YourCo itself.

## First use case
**Monday Morning Briefing.** Every Monday by 7:30am ET, Atlas delivers a single executive-readable briefing to the Founder covering: pipeline state, this week's calls, finance pulse, watchdog signals, and the recommended actions for the week.

## Outcome the executive can repeat in one sentence
"Atlas makes sure the Founder's Monday morning starts with a 5-minute read that tells him exactly what to do this week — without him needing to open any other tool."

## Systems Atlas touches (v0)
- Gmail (`founder@yourco.example.com`) — read inbox; create a draft email for the Founder with the briefing
- Google Calendar — read next 7 days
- Google Drive — read workspace files
- Slack (`yourcoworkspace.slack.com`) — post the briefing summary to `#all-yourco`
- Workspace markdown files — read pipeline, finance ledgers, prior loop artifacts

## Success criteria (eval set v0)
1. **Reliability** — briefing delivered by 7:30am ET every Monday. Target: 95% on-time over rolling 4-week window.
2. **Completeness** — briefing contains all required sections (pipeline state, calls, finance pulse, watchdog signals, recommended actions, open questions). Target: 100%.
3. **Brevity** — briefing read time ≤ 5 minutes (≤ 800 words). Target: 100%.
4. **Watchdog accuracy** — Atlas correctly fires every active watchdog trigger that should fire (no misses) and doesn't fire watchdogs that shouldn't (no false positives). Target: 100% recall on test set; <5% false positive rate.
5. **Actionability** — the Founder takes at least one action from the recommended actions list. Target: weekly. Measured by the Founder checking off an action in the next week's briefing.

Full eval harness will live in `03_eval.md`.

## Approval pattern
- **Full autonomy** for: producing the Monday briefing artifact, posting to `#all-yourco` Slack, creating draft emails in the Founder's Gmail.
- **Human-in-loop** for: sending any email to anyone outside YourCo, posting to Slack channels other than `#all-yourco`, any action with cost > $1.
- **Human-must-approve** for: touching any client tenant, sending invoices, executing financial transactions, any LinkedIn or X post.

## Digital employee identity
- **Name:** Atlas
- **Email:** `contact@yourco.example.com` (alias of `founder@yourco.example.com`, active 2026-06-09 — "Send mail as" enabled in Gmail)
- **Slack identity:** signs as "— Atlas, YourCo Ops" in `#all-yourco` posts (posts via the Founder's Slack user for v0; dedicated Slack App can be added later when external visibility justifies)
- **Signature:** "— Atlas, YourCo Ops"

## Scope — what's IN (v0)
- Monday Morning Briefing (this use case — the first surface of the monitoring function)
- **Analytics & monitoring (owned function)** — agent health, eval status, and watchdog signals across all YourCo agents/engagements; per-engagement token-cost rollup; cross-cutting signal detection. The Monday briefing is how this surfaces today; it expands as more agents come online (see `03_internal_platform.md` and `04_agent_roster.md`). Atlas observes and reports — it does not direct other agents (see decision `2026-06-07_agent-operating-model.md`).
- Reading workspace files and connectors
- Drafting the Founder-facing communications

## Scope — what's OUT (parked for v2+)
- Sending external emails
- Touching any client tenant
- Financial transactions or invoice sending
- Public posts (LinkedIn, X, blog)
- Acting on any actions that the briefing recommends (Atlas writes; the Founder acts)

## v0 → v1 → v2 roadmap
- **v0 (this engagement):** Monday Morning Briefing only. Source of truth for what Atlas does.
- **v1 (account expansion):** Atlas runs the customer/engagement health watchdog when first client goes live. Same pattern, new use case.
- **v2:** Atlas tracks per-engagement token cost across all live engagements and produces a monthly cost rollup that informs pricing decisions.

## Estimated build time
~2 hours, building on top of the four loops that already run. Most of the work is the synthesis SOP and the email-draft integration.

## Risks
- **Pre-revenue thinness.** With no clients yet, several sections of the briefing will be empty. Mitigation: Atlas explicitly reports what's empty rather than padding — empty is a signal too.
- **Session dependency.** Scheduled tasks run when Cowork is open. If closed Monday morning, runs on next launch. Mitigation: the Founder leaves Cowork open Sunday night, or moves to Claude Code's always-on equivalent in the future.
- **Email-draft permissions.** Gmail MCP can create drafts; verify on first run. If blocked, fall back to writing the briefing to the artifact and Slack only.
