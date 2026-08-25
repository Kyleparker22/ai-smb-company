# Decision — native CRM + David (CRM/RevOps agent)

**Date:** 2026-06-10 · **Decider:** the Founder (directed in chat) · **Status:** 🟢 built

## What
A workspace-native CRM at `/crm/` (sleek yourco/Apple-design dashboard + a git-tracked data file) and a new agent, **David**, who owns it.

## Why
`clients/_pipeline.md` was a lonely markdown file nobody formally owned. Sales needs a real system of record with good process tracking, owned by an agent that keeps it clean. David = data hygiene, dedup, freshness, enrichment, the pipeline report, and the Granola meetings/notes capability. A distinct tool + distinct job justify a dedicated agent (the roster's bar for a new agent).

## Design
- **Native, not SaaS.** A `crm/data.js` source of truth (`window.CRM_DATA`) + `crm/index.html` dashboard (pipeline kanban, contacts, companies, activity, metrics) in the locked brand palette. Loads via `<script>` so it opens from `file://` with no server. Read-optimized; David does the writes; live in-UI editing is a future upgrade (needs a small backend to persist).
- **Stages:** prospect → discovery → proposal → build → live; closed = won / lost / parked.
- **Relationship to `_pipeline.md`:** David keeps the markdown pipeline in sync as the agent-readable mirror (Reilly/Jim/Bird/Atlas read it); `/crm/` is the rich record + UI.
- **David's lineage:** Jacco van der Kooij (*Winning by Design* — sales as a measurable process) + the RevOps single-source-of-truth discipline.

## Note on "tools are OK"
the Founder clarified yourco is fine adopting external tools (e.g. QuickBooks for Charles, coming). The CRM was still built native by choice — a sleek owned CRM fits the moat and the design better here. The workspace-native default is a preference, not a rule.

## Revisit conditions
- If the CRM needs live multi-user editing or scales past a few hundred records, evaluate a small backend or an external CRM (HubSpot connector exists).
- Re-confirm David's hygiene loop earns its keep once real pipeline volume exists.
