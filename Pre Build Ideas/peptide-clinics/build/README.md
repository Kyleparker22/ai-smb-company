# Protocol OS — build 74

Pre-built vertical AI OS for cash-pay peptide / longevity clinics.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py               # ~260 patients, protocols, messages, labs
python3 test_protocol_os.py   # 85 assertions
```

Launch name **`prebuild-protocol-os`** (port 8897, 127.0.0.1 only).
`PROTOOS_DATA_ROOT` relocates the store; the suite uses a temp dir.

## What it is

Four modules on `_kit`: **inbox triage**, **the refill cycle**, **quiet after a dose change**, and
**labs waiting**. The board leads with retention because that is where a cash-pay program business
actually makes its money.

## The refusals it is organised around

**The exclusion is structural, not a filter.** A patient who discontinued for a medical reason, had
an adverse event, opted out, transferred or died is never loaded by `contactable()`. Every outreach
list is built from that query, so there is no code path where someone forgets to apply the filter —
and `draft_refill_nudge` refuses again at the door. Belt and braces, because this is the failure
that ends a clinic.

**No clinical advice, ever.** `clinical_advice`, `adjust_dose` and `interpret_labs` are R0 and
unpromotable at any streak. The refusal is *said to the patient* and still carries the emergency
instruction.

**The quiet-after-a-change list carries no draft.** Deliberately. A patient who went silent after a
dose change needs a person, and shipping a template there would be the wrong kind of automation.

## A bug worth recording

The suite caught `\b(reschedul|titrat|wheez)\b` — a trailing `\b` after a *prefix* can never match,
because there is no word boundary between "wheez" and "ing". Every prefix now carries `\w*`
explicitly. It is written into the source as a comment because the failure mode is silent: it
downgrades an emergency to admin and looks like working code.

## What this does not do yet

- **No EHR, pharmacy, payments or SMS.** Adapter seams.
- **Triage is deterministic pattern-matching** — right for the urgent stop (auditable, biased on
  purpose), brittle for how patients actually write. A real deployment puts a model behind the
  routine path and leaves the urgent half exactly as it is.
- **No dosing, no protocols content, no clinical logic — permanently.**
- **Nothing is sent.**
