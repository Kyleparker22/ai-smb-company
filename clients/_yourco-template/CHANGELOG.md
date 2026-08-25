# yourco-template — CHANGELOG

> Owner: **Kemba**. Every change to the golden template is versioned and logged here (and material ones in `decisions/`). The template is the paved road — change it deliberately, never per-client (client logic is overlay only).

## v1.1 (minor) — 2026-08-07
- Frontier hooks installed ahead of clients (Kimi; rows #7/#3/#16 — hooks-predate-clients rule): `understudy/` (client-owned role-handbook + signed-consent templates, R0 shadow-config stub; activation = client decision → R1), `exit-asset/` (diligence-pack skeleton that fills over the engagement's life — generated at sale time, never reconstructed), and the Leak Meter console band (`client-console-leak-meter.html` + `leak-config.json` + `leak-events.jsonl`; deterministic pricing, unsigned assumptions render counts-only "no approved assumption", demo state ships zero events / all unsigned).
- Understudy consent form carries a DRAFT banner — counsel gate #1 must clear the language before first use; FL voice capture excluded until counsel.

## v1 (minor) — 2026-08-07
- Frontier substrate installed (Kemba; rows #8/#4/#17 — hooks predate clients by design):
  - `learnings/` — immune-system hooks per `offerings/immune-system/TEMPLATE-HOOKS.md` (`pattern-candidates/` outbound + `vaccinations/` inbound + `_applied.md`); central review gate documented at `runtime/immune/README.md`, inbox/feed at `learnings/_network/` (repo root). Human-approved propagation, R1 permanently.
  - `ledger/` — self-proving-invoice outcome-ledger schema per `offerings/self-proving-invoice/SPEC.md` §3.1 (append-only JSONL, five record types, capture from day one).
  - `receipts/` — evidence-packet template + `assemble.py` stub per `offerings/the-receipts/SPEC.md` (append-only, gaps-as-gaps, no selective assembly).
- Pending wiring (not in this change): build-checklist hooks in `02_build.md`, consistency-check invariants (leak screen / provenance / coverage staleness), the candidate copy sweep loop. Contract-first rule: no candidate crosses a tenant boundary until counsel gate #1 clears.

## v0 — 2026-06-10
- Initial scaffold created (`clients/_yourco-template/`): `_README.md`, `01_discovery.md`, `02_build.md`, `03_eval.md`, `cost.md`, `go-live.md`.
- Paired with the onboarding runbook (`processes/onboarding.md`, Janice) and the build playbook (`processes/discovery-to-48h-build.md`, Kimi).
- Written for the landscaping/intake voice use case (Vapi + Twilio + Calendar + ElevenLabs + CRM log); generalizes to other verticals as overlay.

## How to version
- **Patch** — wording/checklist fixes, no structural change.
- **Minor** — a new reusable section/pattern extracted from an engagement.
- **Major** — a change to the delivery method or the file structure itself.
Log the version, date, what changed, and why. Extracted-from-engagement patterns name the engagement.
