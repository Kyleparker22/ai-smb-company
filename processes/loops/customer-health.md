# Customer / Engagement Health Loop

## Cadence
Every Wednesday at 7:00 AM ET.

## Goal
Catch friction in active client engagements before the client says something. This loop is the moat made visible — proving the digital employees YourCo deploys are doing their jobs and that YourCo is watching.

## Inputs (read every run)
1. `CLAUDE.md`
2. `clients/_pipeline.md` — find all clients at status `live` or `expansion`
3. For each live/expansion client: `clients/<client>/weekly/` — read the most recent readout, and `<client>/03_eval.md` for eval state
4. Most recent prior artifact in `loops/customer-health/`
5. Gmail — emails to/from each client's domain in the last 7 days
6. Slack — search for mentions of each client's name in the last 7 days

## Steps
0. **Read recent learnings.** Before anything else, read the most recent entries (last ~5, past 30 days) in `/learnings/delivery/` and `/learnings/ops/` for patterns that apply to this run, and apply what fits. List the entries you applied in the artifact's "Learnings applied this run" line. (An empty folder means nothing to apply yet — expected pre-launch.)
1. **Boot context.**
2. **Identify active engagements.** If none, produce a short artifact ("No active engagements; loop will activate when first client goes live") plus a recap of what setup is needed when the first engagement starts. Done — skip Slack post.
3. **For each active engagement, gather signals:**
   - Latest weekly readout
   - Gmail tone and response time (any escalation language? Any silence?)
   - Failed evals or watchdog triggers from `03_eval.md`
   - Any scope-creep language in recent comms
4. **Assign status per engagement: green / yellow / red.** Justify each in one line.
5. **Write artifact** at `loops/customer-health/YYYY-MM-DD.md`.
6. **Slack summary** — only if any engagement is yellow or red. If all green, skip Slack to reduce noise. Signed "— Atlas."

## Output artifact format
```
# Customer Health — YYYY-MM-DD

## Summary
- Green: N (named)
- Yellow: N (named)
- Red: N (named)

## Per engagement
### <client name> — <green/yellow/red>
- Evidence: ...
- Recommended action: ...

(Repeat for each)

## What I'd do differently next run
(Empty — for the Founder to fill)

## What worked this run
(1-2 things that landed harder than expected. Future runs read this too — this is how wins get amplified, not just mistakes avoided.)

## Learnings applied this run
(The `/learnings/delivery/` and `/learnings/ops/` entries that influenced this run. "None" if nothing applied.)
```

## Watchdog triggers
- Any engagement red for 2 consecutive weeks → escalate; recommend an exec sync with client sponsor
- Any engagement silent (no client-side comms in 7 days) → yellow at minimum
- Any failed eval in the last 7 days that wasn't addressed in the weekly readout → red
- Any client raising scope-creep language → flag, route to the Founder in artifact lead

## Pre-engagement handling
While there are no live engagements: produce a short status artifact, no Slack post, and use the space to remind the Founder what setup is required when the first engagement starts (digital-employee name + email, eval set, watchdog config, weekly-readout schedule).
