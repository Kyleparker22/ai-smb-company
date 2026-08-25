# Monday Morning Briefing (Atlas's first use case)

## Cadence
Every Monday at 7:30am ET. Runs after sales (7:08) and finance (7:24) loops have produced their artifacts.

## Goal
A single 5-minute executive read that tells the Founder exactly what to do this week. Delivered three ways: workspace artifact, Gmail draft, Slack post.

## Inputs (read every run)
1. `CLAUDE.md` — company context
2. `agents/atlas/01_discovery.md` and `03_eval.md` — Atlas's own scope and eval criteria (so Atlas is held to its own standard)
3. Today's sales artifact at `loops/sales/YYYY-MM-DD.md`
4. Today's finance artifact at `loops/finance/YYYY-MM-DD.md`
5. Most recent prior briefing at `loops/monday-briefing/` — for "What changed" and feedback the Founder left
6. Gmail — unread threads from the weekend (last 60 hours) that look like real signal (not vendor noise)
7. Calendar — next 7 days

## Steps
0. **Read recent learnings.** Before anything else, read the most recent entries (last ~5, past 30 days) in `/learnings/ops/` for patterns that apply to this run, and apply what fits. List the entries you applied in the artifact's "Learnings applied this run" line. (An empty folder means nothing to apply yet — expected pre-launch.)
1. **Boot context.** Read CLAUDE.md, Atlas's discovery and eval docs, today's sales + finance artifacts.
2. **Read prior briefing's feedback.** If the Founder filled in "What I'd do differently next run" in last Monday's briefing, incorporate it explicitly.
3. **Cross-cutting watchdog scan.** Look for signals that span both sales and finance (e.g., finance flagged margin concern AND sales flagged a stalled prospect on the same account → these may be related and should be paired in the briefing).
4. **Synthesize this week.** Produce a 5-section briefing (see format). Lead with anything that changed materially this week; lead with watchdogs if any fired.
5. **Triple delivery:**
   - **Artifact:** Write to `loops/monday-briefing/YYYY-MM-DD.md`.
   - **Email draft:** Create a draft in `founder@yourco.example.com` with subject `Monday Briefing — YYYY-MM-DD` and body = the artifact content. Do not send.
   - **Slack post:** One paragraph (4-6 lines max) to `#all-yourco` summarizing the top 1-2 actions for the week. Signed "— Atlas".

## Output artifact format
```
# Monday Briefing — YYYY-MM-DD

## What changed this week
(One paragraph. If anything materially shifted vs last week, lead with it. If quiet week, say so.)

## Pipeline state
(Pull from today's sales artifact. One paragraph or a short table — keep tight.)

## This week's calls
(Pull from today's sales artifact. Bullet per call: date, time, who, purpose.)

## Finance pulse
(Pull from today's finance artifact. Lead with fired watchdogs if any. Otherwise: cash, MRR, runway in one line. Logging gaps in one line. Per-engagement margin if any.)

## Watchdog signals
(Cross-cutting signals only. If individual loops fired their own watchdogs, mention which and where to read.)

## Recommended actions (this week)
1. ... (highest-leverage move)
2. ...
3. ...
4. ...
5. ...
(Anchored on moat or pipeline. Each action one line, with the "why" in parens.)

## Open questions for the Founder
(Anything Atlas couldn't decide. Empty if nothing.)

## What I'd do differently next run
(Empty — for the Founder to fill before next Monday. This is the closed-loop mechanism.)

## What worked this run
(1-2 things that landed harder than expected. Future runs read this too — this is how wins get amplified, not just mistakes avoided.)

## Learnings applied this run
(The `/learnings/ops/` entries that influenced this run. "None" if nothing applied.)

---
— Atlas, YourCo Ops
```

## Brevity rule
The artifact MUST be ≤ 800 words. If you're going over, cut detail — the underlying loop artifacts have the depth; the briefing is the synthesis. If a reader needs more, they can read the linked loop artifact.

## Watchdog handling
- If any cross-cutting watchdog fired this week, lead the briefing with it.
- If individual loops fired watchdogs, list them in "Watchdog signals" with a one-line summary and a link to the loop artifact.
- If the Founder's feedback flagged a miss last week, lead with the correction.

## Failure modes
- **Missing inputs.** If today's sales or finance artifact doesn't exist (loop didn't run), note this at the top of the briefing and produce what you can from the connectors directly.
- **Empty week.** If YourCo is pre-pipeline and nothing happened, say so honestly — the briefing should be 200 words, not 800 padded. Honest emptiness is more useful than fabricated motion.
- **Email draft creation fails.** Fall back to artifact + Slack only; log the failure in `cost.md` for diagnosis.

## Feedback capture
the Founder fills in "What I'd do differently next run" mid-week. Next Monday's run reads it and incorporates. Same closed-loop discipline as every other loop.
