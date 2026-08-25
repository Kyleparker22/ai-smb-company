# /processes/loops/

SOPs for the four recurring closed loops. Each loop has a corresponding scheduled task that loads its SOP and executes it. The SOP is the source of truth — refine it directly to change a loop's behavior.

- `sales.md` — Monday 7:00 AM ET — pipeline review and weekly action plan
- `finance.md` — Monday 7:15 AM ET — cash, runway, logging gaps — **owned by Charles** (no longer Atlas)
- `advisor.md` — monthly (1st) + on-demand — strategic advisory + drift detection — **owned by Brett**
- `customer-health.md` — Wednesday 7:00 AM ET — friction signals in active engagements
- `content.md` — Friday 7:00 AM ET — weekly content brief and ready-to-post drafts

## Closed-loop mechanism
Every artifact a loop produces ends with a "What I'd do differently next run" section. When the Founder fills it in, the next run reads it and incorporates the feedback. That is the entire learning mechanism — keep it simple and use it consistently.

## SOP convention
Each SOP follows the same structure: Cadence, Goal, Inputs, Steps, Output artifact format, Watchdog triggers, Feedback capture. When a loop matures, version the SOP — don't rewrite it in place without leaving a note.

## Loop ownership
Loops are migrating from Atlas to named specialist agents as those agents are built (see `/04_agent_roster.md`). Current ownership:
- **finance.md → Charles** (handed off 2026-06-07)
- **advisor.md → Brett** (new monthly loop, 2026-06-07)
- **content.md → Katie** (handed off 2026-06-07)
- **sales.md, customer-health.md → Atlas** (until Reilly/Kortney take them on)

Atlas remains the observability layer: it *reads* every loop's artifact for the Monday briefing and monitoring, but it owns only the loops not yet handed to a specialist. Slack summaries are signed by whichever agent owns the loop. This is intentional dogfooding — the AI OS is itself staffed by YourCo digital employees.
