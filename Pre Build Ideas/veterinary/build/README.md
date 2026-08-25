# Visit OS — build 13

Pre-built vertical AI OS for small-animal veterinary practices.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py             # ~2,400 patients, 400 appointments, waitlist, messages
python3 test_visit_os.py    # 43 assertions
```

Launch name **`prebuild-visit-os`** (port 8833, 127.0.0.1 only).

## What it is

"Brookhollow Veterinary Clinic" — 3 DVMs, $2.8M. Four modules: **message triage**,
**lapsed-patient reactivation**, **slot backfill**, **the counted board**.

## The refusals it is organised around

**The crisis stop.** Nine typed emergency signals — toxin ingestion, GDV signs, the blocked cat,
breathing, collapse, seizure, hit-by-car, heavy bleeding, pale gums — each routing to a human
immediately with the ER instruction verbatim: *"go to the nearest emergency animal hospital now —
do not wait for a reply here."* Nothing is assessed. Eval recall 1.0, zero missed; the eval names
the stake: *A MISSED EMERGENCY IS A DEAD PATIENT.*

**A deceased patient can never receive a reminder.** The unforgivable failure of this vertical is
designed out twice: the reactivation query only sees `status == "active"`, and `reminder_plan`
re-checks at send time. A waitlist row pointing at a deceased patient is blocked with the reason
named. `contact_deceased` is R0.

Also: `clinical_answer` R0 (dosing/"is this normal" → a DVM, unanswered), `qol_conversation` R0
(euthanasia talk gets no automated reply of any kind), a bounded 3-touch reminder ladder, a
backfill rate that refuses below 10 cancellations, and **safety routing is never monetized** — the
ROI line for it is the operator's number or blank.

## 10-minute demo

Board → Inbox (chocolate → ER instruction; dosing → routed unanswered; QoL → human, gently) →
Reactivation (deepest-lapsed first, the structural exclusion in the banner) → Backfill (cancel the
demo slot, see the ranked waitlist and the blocked deceased row) → ROI → Trust.

## What this does not do yet

- **No integrations.** PIMS (Avimark/Cornerstone/ezyVet), SMS, phones are adapter seams.
- **Triage is deterministic pattern-matching** — right for the crisis stop (auditable, biased on
  purpose), brittle for how pet owners actually write. A real deployment puts a model behind the
  routine path and leaves the emergency half exactly as it is.
- **No medical records, no dosing, no advice — by design, permanently.**
- **Nothing is sent.**
