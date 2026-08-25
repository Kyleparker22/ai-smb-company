# Build — [[CLIENT]] / [[EMPLOYEE]] ([[employee type]])

> Hour 4–24. Overlay on `yourco-template`; the method is fixed, the client specifics are the overlay. The **stack is selected by employee type** — see the stack table in `processes/discovery-to-48h-build.md`. The method is the same for any type; only the connectors differ.

**Employee identity:** [[NAME]] · [[employee@client-domain / yourco alias]] · **Stack:** [[from the SOP table]]

## Build checklist (type-agnostic)
- [ ] **Provision the employee** from the template; overlay the client's logic from `01_discovery` (the system prompt / rules / fields / escalation paths).
- [ ] **Wire the chosen stack's connectors** (per the SOP's stack table for this type) — every read/write the job needs. Examples: voice → Vapi+Twilio+Calendar+ElevenLabs · text-intake → email+CRM+Calendar · scheduling → Calendar+reminders · drafting → templates/docs · Q&A → KB/RAG · data → client systems · outbound → email/SMS+compliance.
- [ ] **Configure the approval gates** — the gated actions from `01_discovery` stay human-approved (the per-engagement moat).
- [ ] **Apply brand voice + identity** to every client-facing surface.
- [ ] **Wire the watchdogs + human-fallback** (per type — see `03_eval`).
- [ ] **Cost tracking** started in `cost.md`.

## Build shape (default — interface-first + seed→live)
The standard that makes account expansion a drop-in instead of a rewrite (`learnings/delivery/2026-06-18_interface-first-build-standard.md`):
- [ ] **Contract first.** Define the shared types/interfaces before any implementation, so independent pieces (connectors, logic, delivery) build in parallel without colliding.
- [ ] **Every external touch behind an interface.** Each data source implements one shared connector contract; each output (file, Slack, email, SMS, client console) implements one `deliver()`-shaped contract. The pipeline never knows which implementation it's talking to.
- [ ] **Seed → live ladder.** Stand v1 up deterministic + local (fixture data in, file/draft out, no live keys) so it demos with zero setup; live fetch + real delivery are later implementations of the same seams, gated behind a flag — never a rewrite.
- [ ] **Fail-soft.** A live source or channel that errors/rate-limits falls back to seed/last-good/file; the run degrades, never hard-crashes.
- [ ] **Offline self-check.** Every connector/delivery gets a `--self-check` that validates config + contract with no network before going live.

## Configuration record (fill as built)
- Employee / assistant ID or link: [[ ]]
- Connectors wired (+ IDs): [[ ]]
- Systems-of-record / sink: [[ ]]
- Approval-gate line (auto vs escalate): [[ ]]

## Overlay notes
[[Anything client-specific that deviates from the template default — capture it so Kemba can fold the repeatable parts back into `yourco-template` for the next engagement of this shape.]]
