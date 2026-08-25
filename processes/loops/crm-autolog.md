# Loop — crm-autolog (David): Gmail/Calendar → pending CRM activities, confirm-to-save

**Cadence:** weekdays 08:15 ET (`yourco-crm-autolog.timer`) · **Owner:** David · **Output:** `crm/_pending-activities.json` + a dated note in `loops/crm-autolog/`.

## Why
The CRM's activity log is manual, so real touches (emails, booked calls) go unrecorded and deals look stale
(or worse, ARE stale and nobody can tell which). This is the Attio-borrow from `crm/_backlog.md`: records
that build themselves from the inbox — **with a human confirm gate**, never silent writes.

## Inputs
- Gmail (runtime connector, read-only use here) — threads from the last 2 weekdays involving any email
  address that appears on a CRM contact (`crm/data.json` → contacts[].email).
- Calendar (if the connector is live on the runtime; otherwise skip silently) — events in the last 2
  weekdays with CRM-contact attendees.
- **Granola meeting notes (Cowork/Mac sessions only — the MCP is not on the headless runtime; note its
  absence honestly and move on).** When available, this is the answer to "what actually happened in the
  meeting": list recent meetings, match titles/participants against CRM companies + contacts, and draft a
  `type: meeting` pending activity whose summary comes from the real notes (2–3 factual lines: what was
  discussed, what was decided, the next step). **Hard filter: only meetings that match a CRM company or
  contact.** the Founder's Granola also contains unrelated ventures and legal/personal matters (OtherVenture et al.)
  — those are NEVER read, summarized, or referenced in this workspace (hard-separation rule, CLAUDE.md).
  A title that doesn't clearly match a CRM record is skipped without opening it.
- The CRM itself, to match companies/contacts and to avoid proposing an activity that already exists
  (same date + companyId + similar summary).

## Method
1. Step 0 per the loop contract (learnings + skills).
2. Pull CRM contact emails. Scan recent Gmail threads (and Calendar events, if available) for matches.
3. For each real interaction, DRAFT a pending activity: `{id, date, type: email|call|meeting, companyId
   (or companyName if fuzzy), who, summary (1 line, factual), source: "autolog gmail|calendar <date>"}`.
4. Merge into `crm/_pending-activities.json` — never duplicate an existing pending item (match on
   date+companyId+type) and never touch `crm/data.json` directly. **The human confirms in the CRM UI**
   ("Pending — confirm to save"); confirm appends to activities, dismiss discards.
5. Write a dated one-paragraph note to `loops/crm-autolog/` — how many scanned/proposed/skipped.

## Failure / empty handling (pre-revenue honesty)
- No matching threads → write the dated note saying "quiet — nothing to propose" and stop. Do not fabricate.
- Gmail connector unavailable → say so in the note; do not guess.
- Ambiguous match (email on 2+ contacts) → propose with companyName and both candidates named in the summary.

## What it may NOT do
Never write `crm/data.json`. Never send, reply, label, or delete mail. Never create calendar events.
Read + propose only — the approval gate is the CRM UI confirm.
