# yourco-template — CHANGELOG

> Owner: **Kemba**. Every change to the golden template is versioned and logged here (and material ones in `decisions/`). The template is the paved road — change it deliberately, never per-client (client logic is overlay only).

## v0 — 2026-06-10
- Initial scaffold created (`clients/_yourco-template/`): `_README.md`, `01_discovery.md`, `02_build.md`, `03_eval.md`, `cost.md`, `go-live.md`.
- Paired with the onboarding runbook (`processes/onboarding.md`, Janice) and the build playbook (`processes/discovery-to-48h-build.md`, Kimi).
- Written for the landscaping/intake voice use case (Vapi + Twilio + Calendar + ElevenLabs + CRM log); generalizes to other verticals as overlay.

## How to version
- **Patch** — wording/checklist fixes, no structural change.
- **Minor** — a new reusable section/pattern extracted from an engagement.
- **Major** — a change to the delivery method or the file structure itself.
Log the version, date, what changed, and why. Extracted-from-engagement patterns name the engagement.
