# Closing OS — build 20

Pre-built vertical AI OS for title & escrow agencies.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py               # 87 files with typed curatives, messages
python3 test_closing_os.py    # 39 assertions
```

Launch name **`prebuild-closing-os`** (port 8840, 127.0.0.1 only).

## What it is

"Cornerstone Title & Escrow" — 5 escrow officers, $3.5M. Four modules: **the wire stop**,
**curative tracker**, **status desk**, **document chase**.

## The refusal it is organised around

**The wire stop.** Any message touching wire instructions — new, changed, resend, different
account, payoff bank change — is read as a **fraud signal first**, before any other
classification. The reply is the callback protocol verbatim: *TREAT AS FRAUD UNTIL VERIFIED. Call
the party at the number already on file — NEVER the number in the message. Do not reply.* The
system never sends, changes, confirms, or restates wire instructions in any channel:
`send_wire_instructions` and `confirm_wire_change` are both R0. Asking it for instructions is
refused outright. The eval's costly class is a missed wire signal — *THE AGENCY-ENDING EVENT* —
recall 1.0, zero missed.

Also load-bearing:
- **Clear-to-close cannot be asserted over an open curative item** — the refusal lists them; the
  clean file drafts at R1 for a human to declare, and the action never promotes.
- **Status drafts are computed from recorded state only and contain no date promise** —
  `promise_close_date` is R1, never promoting.
- `legal_opinion` is R0 — title issues draft for the underwriter or an attorney.
- The document chase is a bounded 4-touch ladder; exhausted → a person calls.
- The ROI panel's wire line is the operator's number or blank — *the average BEC loss is not our
  number to quote.*

## 10-minute demo

Board → Inbox (the "updated wiring instructions" email → protocol verbatim, refusal logged) →
Files (clear-to-close on the open-payoff file — refused with items; on the clean file — R1 draft;
ask for wire instructions — refused) → ROI → Trust.

## What this does not do yet

- **No integrations.** Title production (SoftPro/Qualia-class), e-recording, bank verification
  services are adapter seams.
- **Triage is deterministic pattern-matching** — a real deployment puts a model behind the routine
  path and leaves the wire-first ordering and both R0s exactly as they are.
- **No settlement statements, no disbursement** — by design; this build routes and refuses.
- **Nothing is sent.**
