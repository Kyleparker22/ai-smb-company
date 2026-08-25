---
name: scaffold-engagement
description: Turn an Audit into a client engagement folder at ~80% in one command — clone the golden template, pre-fill discovery from the diagnosis, seed the demo kit. Use at delivery Stage 0 (first real call held OR proposal sent — whichever comes first) or whenever a new clients/<name>/ folder is needed.
---

# scaffold-engagement

## Canonical pieces
`runtime/scaffold_engagement.py` (the scaffolder) · `clients/_yourco-template/` (the golden template — client logic is overlay only) · `02_delivery_loop.md` Stage 0 (when a client folder may be created).

## Steps
1. Confirm Stage 0 is actually met: **a first real call happened** (discovery conversation with a live prospect) **or** a proposal is out — whichever comes first (the Founder 2026-08-07). No folder for a cold/warm lead that hasn't talked to us — those stay CRM rows.
2. Get the audit JSON (the object Bella fills in `clients/_yourco-template/audit-report/index.html`), or fall back to flags.
3. Dry-run first (default):
   ```
   python3 runtime/scaffold_engagement.py --audit audit.json
   ```
4. Review the plan, then commit it:
   ```
   python3 runtime/scaffold_engagement.py --audit audit.json --commit
   ```
   (No audit file: `--client "YourCo Landscaping" --vertical Landscaping --first-build "AI Front Desk" --commit`.)
5. Post-scaffold: add the deal to `crm/data.json` + `clients/_pipeline.md`, start `clients/<slug>/cost.md` for token tracking, **fill the "How the OS works this client" agent map in the new `_README.md`** (who owns CRM/pricing/eval/guardrails/counsel/cost/loops for THIS client — pattern in `clients/sample-client/_README.md`), and follow `processes/onboarding.md`.

## Gotchas
- **Cowork/local only** — headless loops have no Bash (approval gate), so a loop can flag "engagement needs scaffolding" but never run this itself.
- The scaffolder deliberately stops at ~80%: tenant integration, eval against the client's criteria, and the approval gate are Kimi's human+build work — that remaining 20% **is the moat**; don't try to automate it away.
- Template improvements go to `clients/_yourco-template/` (and get a decision-log entry) — never patch one client's copy with something every future client needs.
