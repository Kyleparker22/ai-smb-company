# Understudy kit — quit-proofing a key role (template)

**Spec:** `offerings/understudy/SPEC.md` (frontier #7). Build trigger for client use: **first signed client** — these are the template hooks (hooks predate clients; no per-client work before a signature).
**Pillar / shape:** Company Brain (pillar 7); a named digital employee with a permanent R0 shadow loop underneath.

## What's in this kit, and the spec rule each artifact carries

| Artifact | What it is | The rule it enforces (spec §) |
|---|---|---|
| `role-handbook-template.md` | The living role handbook — **the primary deliverable, client-owned** | §1: the handbook is product #1, the agent is product #2. A client who cancels **keeps the handbook**; quit-proofing survives the engagement. Exportable, human-readable first; the agent reads the same file. |
| `consent-form-template.md` | Per-role employee consent + access-scope schedule | §5/§8: **consent is a hard precondition — no covert monitoring, ever.** Nothing connects until signed; revocation stops the loop same-day. Includes the no-surveillance-analytics promise *in the document the employee reads*. **FL voice/call capture is out of scope until counsel clears it** (two-party consent). |
| `shadow-config.yml` | Shadow-capture config stub for the weekly loop | §3/§4: shadow mode is **R0 observe-only, permanently**. Activation is never automatic — it is a **client decision** (named event + named approver) that flips the understudy to **R1 draft-for-review** on everything outward, only within the activation window. |

## Order of operations (per role, after signature)
1. Consent pack signed (employee + client authority attestation) — *counsel gate #1 must have cleared the consent language first; see the DRAFT banner on the form.*
2. `shadow-config.yml` filled and scope wired (read-only). The loop refuses to run without a signed-consent reference.
3. Shadow loop scheduled per `.claude/skills/add-runtime-loop` → maintains the handbook weekly (R0).
4. Quarterly interview works the handbook's open-questions list.
5. Activation only per the runbook block in the config: client decision, named approver, R1 floor, deactivates on return/backfill with a handover debrief.

## Hard lines (spec §8 — put them in front of the client, don't soften them)
- No shadow without the role-owner's own signed consent; we decline "don't tell them."
- Exhaust is never used for productivity scoring or performance review — continuity, not oversight.
- Never pitched or activated to eliminate the human's job while they hold it; absence events only.
- Active understudy never exceeds R2; payments, pricing commitments, HR, legal/medical/financial substance stay R1.
- No call/voice capture until the FL posture is counsel-cleared.
- "Quit-proof" is the name, not a guarantee — the open-questions list is shown, not hidden.
- White-label: client brand + client-chosen name; never "yourco," never a roster name.
