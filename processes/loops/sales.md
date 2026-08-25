# Sales / Pipeline Loop

## Cadence
Every Monday at 7:00 AM ET.

## Goal
Surface what the Founder should do this week to grow YourCo's pipeline. Given current pre-revenue state, this loop is more "build pipeline" than "manage pipeline." That tilt will reverse as deals land.

## Inputs (read every run)
1. `CLAUDE.md` — company context (mandatory)
2. `clients/_pipeline.md` — current pipeline state
3. Most recent prior artifact in `loops/sales/` — for diff and any feedback the Founder left in "What I'd do differently next run"
4. Gmail (`founder@yourco.example.com`) — last 7 days, looking for real prospect signal (not vendor newsletters)
5. Calendar — next 7 days

## Steps
0. **Read recent learnings.** Before anything else, read the most recent entries (last ~5, past 30 days) in `/learnings/sales-copy/` and `/learnings/ops/` for patterns that apply to this run, and apply what fits. List the entries you applied in the artifact's "Learnings applied this run" line. (An empty folder means nothing to apply yet — expected pre-launch.)
1. **Boot context.** Read CLAUDE.md and `_pipeline.md`.
2. **Read last week's feedback.** Open the most recent `loops/sales/*.md` and incorporate any notes the Founder left.
3. **Scan inbox.** Filter Gmail for the last 7 days. Identify threads from real humans that sound like prospect signal — questions about AI implementation, agents, consulting, automation, outcomes. Newsletters, SaaS vendor marketing, transactional emails (Calendly confirmations, Slack codes, OneDrive welcomes) are noise. Ignore them.
4. **Scan calendar.** Identify any prospect/discovery calls, blocked prospecting time, sales activities in the next 7 days.
5. **Update pipeline.** If new prospects surfaced from inbox, append them to `_pipeline.md` under "Prospects" with source, last touch date, suggested next action. If existing prospects went silent >14 days, flag them — recommend a final outreach or moving to "parked."
6. **Synthesize the week.** Produce 3-5 specific moves the Founder should make this week, prioritized. Every move should either deepen the moat (reliability/eval/observability/trust artifacts) or build pipeline (outbound, follow-up, content shipped).
7. **Write artifact** at `loops/sales/YYYY-MM-DD.md` (today's date).
8. **Slack summary** — post 3 lines to `#yourco-atlas` on `yourcoworkspace.slack.com`, signed "— Atlas."

## Output artifact format
```
# Sales/Pipeline Loop — YYYY-MM-DD

## What changed since last run
(One paragraph diff vs. last week. First run: "First run.")

## Pipeline state
- Prospects: N — (named list)
- Discovery: N — (named)
- Proposal: N
- Build: N
- Live: N
- Expansion: N

## This week's calls
(From calendar: date, time, who, purpose)

## Recommended actions (this week)
1. ...
2. ...
3. ...

## Open questions for the Founder
(Anything blocking that needs his decision)

## What I'd do differently next run
(Empty — for the Founder to fill before next Monday)

## What worked this run
(1-2 things that landed harder than expected. Future runs read this too — this is how wins get amplified, not just mistakes avoided.)

## Learnings applied this run
(The `/learnings/sales-copy/` and `/learnings/ops/` entries that influenced this run. "None" if nothing applied.)
```

## Watchdog triggers
- No new prospects identified for 2 consecutive weeks → flag in the artifact lead; recommend an outbound push.
- Any prospect sitting in "discovery" stage >2 weeks → recommend pushing to proposal or parking.
- Pipeline value declining week-over-week → escalate at the top of the artifact.

## Feedback capture
The final section ("What I'd do differently next run") stays empty when Atlas writes the artifact. When the Founder adds notes there before the next Monday, next week's run reads them. That is the entire closed-loop mechanism.
