---
name: promote-intent-signal
description: Graduate a Sadie intent signal into the CRM as a real lead (company + prospect-stage deal owned by Reilly, signal attached as its first Hot List pill). Use when a prospect-grade signal from the daily sweep is identified as a real business worth pursuing — this is the ONLY path a Sadie signal becomes a CRM row.
---

# promote-intent-signal

## Canonical pieces
`runtime/promote_intent.py` — two lanes, only lane 2 is this skill:
- **Lane 1 (attach)** runs automatically after every sweep: signals matching companies *already* in the CRM append to their `signals[]` (Hot List pills). Not this skill.
- **Lane 2 (promote)** is this skill: a human identifies the business behind an unmatched signal, then creates the row. Mirrors `promote-warm-lead` (the Instantly gate).

## Steps
1. See the candidates (unmatched prospect-grade signals from the last 7 sweeps):
   ```
   python3 runtime/promote_intent.py --list
   ```
2. **Identify the business** — this is the human step the whole gate exists for. Open the signal URL, work out who's behind the handle (channel about-page, profile, website). Two hard filters:
   - **Vendor check:** anyone *selling* a solution (answering service, software) is a vendor, not a prospect — skip. (Zebra Go, first live sweep, is the canonical miss.)
   - **Identity check:** no real business identifiable → it stays on the board. Never create a row for an anonymous handle.
3. Dry-run, then commit:
   ```
   python3 runtime/promote_intent.py --promote --signal-url "URL" --company "YourCo Hardscapes" \
       --vertical Hardscaping --location "Yourtown" --domain yourco.com --commit
   ```
   (`--contact` / `--email` if known. Without `--commit` it shows what it would create.)
4. Result: company (source `sadie intent (<platform>)`, status `prospect`, owner Reilly) + prospect-stage deal + the signal as its first Hot List pill in `crm/data.json` (+ `data.js` mirror). Follow up per the sales loop — first touch stays approval-gated.
5. Commit via `runtime/commit-scoped.sh "crm: promote <name> from sadie signal" crm/data.json crm/data.js`.

## Gotchas
- De-duped: an existing company errors out with "use --attach" — the signal will auto-attach on the next sweep instead.
- Cowork/local only (needs Bash). The headless sweep only ever runs lane 1.
- Promotion ≠ outreach. The row entering the CRM changes nothing about the gates on touching the prospect (OtherVenture for cold, approval for everything).
- Don't hand-edit `crm/data.json` for this — the script owns id allocation and the data.js mirror.
