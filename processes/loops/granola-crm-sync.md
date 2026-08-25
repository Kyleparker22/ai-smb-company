# Loop — granola-crm-sync (David): meeting notes → CRM, same day, autonomy-tiered

**Runs as a Cowork scheduled task on the Founder's Mac** (weekdays, every 2h 9a–5p ET) — NOT a VPS loop: the
Granola MCP only exists on the Mac. **Owner:** David. **State:** `crm/_granola-processed.json` (processed
Granola meeting ids). **Output:** direct CRM writes + a dated note in `loops/granola-crm-sync/` (only on
runs that processed something) + one Slack line per meeting to `#yourco-david`.

## Why
Meetings were the one CRM input with no capture path — Granola already transcribes them; this closes the
loop the same day instead of relying on a voice-note habit.

## Method
1. `list_meetings` (Granola MCP) for the last 3 days. Diff against the processed-ids state file.
2. **Hard filter before opening anything:** a meeting is in-scope ONLY if its title/participants match a
   CRM company or contact (`crm/data.json`). the Founder's Granola also holds other ventures and legal/personal
   matters (OtherVenture et al.) — those are NEVER opened, summarized, or referenced in this workspace
   (hard-separation rule, CLAUDE.md). Unmatched = mark id processed, move on, don't open.
3. For each in-scope meeting, `get_meetings` → write the CRM updates in these autonomy tiers
   (`processes/autonomy-matrix.md` — control on the reliability layer, not day-one full autonomy on
   consequential actions):
   - **AUTO (write directly):** append a `type: meeting` activity — `summary` (2–3 factual lines),
     `notes` (the fuller Granola note, condensed — never the raw transcript), `source: "granola <date>"`,
     `who`, `companyId`. Auto-touch `lastTouch` on the company, contact, and open deal (same as
     hand-logged activities). Fill-blanks-only on contact fields the notes surface (e.g. a phone number).
   - **AUTO (visible):** set/refresh the deal's `nextAction`/`nextDate` when the notes contain an explicit
     commitment ("send the proposal Friday"). Factual extraction only — no invented next steps.
   - **SUGGEST ONLY (R1 floor until the streak rule earns it up):** stage changes, deal value changes,
     creating new companies/deals. Put the suggestion in the Slack line ("Suggest: Sample Product
     proposal → build — they agreed to start") — the Founder/David applies it in the UI in one click.
   - **NEVER:** delete anything, overwrite human-entered fields, send anything external.
4. All CRM writes through the locked path (`dashboard/melanie.crm_lock()` + `_atomic_dump` +
   `write_mirror`) — never a bare overwrite.
5. Update the state file, write the dated note (meetings processed / skipped-unmatched count — never the
   content of unmatched meetings, not even titles), Slack one line per logged meeting, and commit via
   `runtime/commit-scoped.sh` scoped to: `crm/data.json crm/data.js crm/_granola-processed.json
   loops/granola-crm-sync`.

## Empty/failure handling
- No new meetings → update nothing, write nothing, exit quietly (the task-run history is the heartbeat).
- Granola MCP unavailable → exit with one line noting it; don't guess.
- Ambiguous match (could be 2+ companies) → log the activity with `companyId: null` +
  both candidates named in the summary, and flag in the Slack line.

## Relationship to crm-autolog (the 08:15 VPS loop)
Granola meetings are THIS loop's job (direct write, same day). The VPS autolog covers Gmail/Calendar into
the pending strip and must skip any meeting already present in activities (match date+companyId+type).
