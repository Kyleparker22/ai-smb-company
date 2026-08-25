# Loop — melanie-briefing: the Founder's daily "here's your day"

**Cadence:** daily, early ET (`yourco-melanie-briefing.timer`, live on the VPS) · **Owner:** Melanie
(CEO in training) · **Output:** `loops/melanie-briefing/YYYY-MM-DD.md` + a Slack post to `#all-yourco`,
signed "— Melanie" · **Prompt:** `runtime/prompts/melanie-briefing.md` · **Step 0 learnings:** `learnings/ops/`

## Why
This is the personal rundown, deliberately **not** Atlas's weekly strategic briefing and not the
initiative loop. Its whole job is that the Founder opens Slack and already knows what today needs, without
opening the CRM. It is read-only over the business: it changes nothing, it only notices.

## Inputs (read every run)
1. `crm/data.json` — deals (stage, `nextDate`, `lastTouch`, `stageSince`, owner), tasks, companies, contacts
2. `dashboard/data.json` — `company.focus`, `company.metrics`, `agents`, `loops`
3. The most recent prior artifact in `loops/melanie-briefing/` — so today doesn't repeat yesterday
   word-for-word. Continuity is the point; a briefing that reads identically five days running is noise.

## Method
1. **Compute the signals** against the run date — never a hardcoded date:
   - **Tasks due** — open (`done` false) with `due` ≤ today; flag overdue separately
   - **Deal actions due** — active deals (stage ≠ `live`) with `nextDate` ≤ today
   - **Gone cold** — active deals whose `lastTouch` (else `stageSince`) is 7+ days ago
   - **Stuck** — active deals 14+ days in the current stage
   - **Data health** — contacts missing email, deals missing owner. Mention only if it matters this week.
2. **Write 4–7 short spoken sentences** in Melanie's voice — warm, Southern, no markdown headers, no
   bullets, no jargon. Greeting → what needs the Founder today → the nearest real deadline → the single most
   important thing to do first → one encouraging line.
3. **Write the artifact**, with a one-line signals tally at the bottom for the next run to read.
4. **Post to Slack** (`#all-yourco`).

## Guardrails
- **Read-only except its own artifact.** No CRM writes, no email, ever.
- **Empty is a valid briefing.** If nothing is due or cold, say so plainly. Manufacturing urgency to
  justify the loop is the failure mode that makes a daily briefing get ignored.
- **yourco is pre-launch** — the launch-gate is 🔴 and nothing goes external. A briefing must never
  imply an outbound action is available.
- Handle missing or empty data gracefully; name a missing input rather than working around it.

## Failure modes seen
- Repeating the prior day verbatim → always read the previous artifact first.
- Reading a stale date → today is the *run* date, computed, never assumed.
