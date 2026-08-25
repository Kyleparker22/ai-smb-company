# Inbox Triage + Day Desk Loop

> **Owner: Jim** (Chief of Staff — see `agents/jim/`). Runs and signs as Jim. **Drafts only for replies; non-destructive organizing allowed (label, archive noise, mark-read — all reversible); NEVER deletes or sends.** External invites are in-loop. The morning desk: clear the inbox, prep the day's calls, surface what needs the Founder.

## Cadence
Weekday mornings (Mon–Fri). Quiet until outreach generates real inbound; grows as replies + calls start.

## Inputs (read every run)
1. Gmail — inbound since the last run (last ~24h, or 72h on Mondays).
2. Calendar — today + the next 2 days.
3. `clients/_pipeline.md` + most recent `loops/sales/` artifact — who matters, context.
4. Most recent prior artifact in `loops/inbox-triage/`.
5. `brand/v0/brand-guidelines.md` — voice for drafts.

## Steps
0. **Read recent learnings.** Before anything else, read the most recent entries (last ~5, past 30 days) in `/learnings/ops/` for patterns that apply to this run, and apply what fits. List the entries you applied in the artifact's "Learnings applied this run" line. (An empty folder means nothing to apply yet — expected pre-launch.)
1. **Triage the inbox.** Sort inbound into: **needs the Founder** (real human / prospect / decision), **routine** (Jim can draft a reply), **noise** (vendor/newsletter/transactional — ignore). Be honest: most pre-outreach inbox is noise.
2. **Draft routine replies.** For routine items, create Gmail **drafts** (never send) in the Founder's voice. Flag anything that should be a real reply but needs the Founder's judgment.
3. **Organize / clean up (non-destructive).** Apply a `Jim/` label by bucket (`Jim/Needs-the Founder`, `Jim/Routine-drafted`, `Jim/Noise`). For items you're confident are noise, **mark read + archive** (remove the `INBOX` label — reversible, searchable, never deleted). **Never archive needs-the Founder or routine.** For recurring newsletter/vendor noise, surface the unsubscribe link + **draft** an unsubscribe (never click/send it). This is the only step that *acts* on the inbox — stay conservative; when unsure, leave it in the inbox and label only. Log every archive in the artifact (reversible in one click).
4. **Prep today's calls.** For each call on the calendar in the next 2 days: a 3-line brief — who, company/context (from pipeline + any history), and a suggested opening/agenda. Flag any external invite that still needs the Founder to confirm.
5. **Surface the short list.** What the Founder actually needs to act on today (replies to approve, calls to confirm, decisions).
6. **Write artifact** at `loops/inbox-triage/YYYY-MM-DD.md`.
7. **Slack summary** — 3–5 lines to `#yourco-jim`, signed "— Jim, YourCo Ops": the needs-the Founder short list + today's calls. Lead with anything time-sensitive.

## Output artifact format
```
# Desk — YYYY-MM-DD

## Needs the Founder today
(Replies to approve, calls to confirm, decisions. "Nothing pressing" if quiet.)

## Inbox triage
- Needs the Founder: N — (one line each) · labeled `Jim/Needs-the Founder`, left in inbox
- Routine (drafts created): N — (one line each, link the draft) · labeled `Jim/Routine-drafted`
- Noise: N — labeled `Jim/Noise`

## Organized this run (all reversible)
- Archived (noise, removed from inbox): N — (sender/subject one-liners; one-click restore)
- Marked read: N
- Unsubscribe drafts created: N — (sender; draft only, not sent)

## Today's / upcoming calls
(Per call: date/time, who, company/context, suggested agenda. "No calls" if none.)

## What I'd do differently next run
(Empty — for the Founder to fill)

## What worked this run
(1-2 things that landed harder than expected. Future runs read this too — this is how wins get amplified, not just mistakes avoided.)

## Learnings applied this run
(The `/learnings/ops/` entries that influenced this run. "None" if nothing applied.)
```

## Watchdog triggers
- A real prospect reply sitting unactioned >24h → escalate at the top.
- A booked call in the next 24h with no prep + no confirmation → flag.
- External invite drafted but awaiting the Founder >24h → flag.

## Pre-outreach handling
Until the first batch sends, the inbox is ~all vendor noise and there are no prospect calls. The loop says so honestly in two lines and stops — it doesn't manufacture activity. Its real value begins when outreach lands replies.
