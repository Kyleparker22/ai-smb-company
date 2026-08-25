---
name: promote-warm-lead
description: Graduate an Instantly warm reply into the native CRM as a real lead (company + contact + prospect-stage deal owned by Reilly). Use when a cold prospect replies with positive intent — this is the ONLY path sourced cold leads enter the CRM.
---

# promote-warm-lead

## Canonical pieces
`runtime/promote.py` (implements `decisions/2026-06-15_prospect-data-architecture.md`).

## Steps
1. Dry-run to see who would graduate:
   ```
   python3 runtime/promote.py                          # all campaigns
   python3 runtime/promote.py --campaign "Landscaping ST"
   ```
2. Review — positive-intent replies only; the script de-dupes against the CRM so a lead promotes once.
3. Commit:
   ```
   python3 runtime/promote.py --vertical "Landscaping" --commit
   ```
4. Result: company (status "warm — replied") + contact (status "replied") + `prospect`-stage deal owned by Reilly in `crm/data.json`. Follow up per the sales loop.

## Gotchas
- Read-only against Instantly — it never sends and never touches Instantly state. Reply handling stays human/approval-gated.
- Cold prospects stay in Instantly; the CRM is for warm+ only. Don't hand-add cold leads to `crm/data.json` — that breaks the architecture the decision locked.
- Cowork/local only (needs Bash — headless loops can flag candidates but not run it).
