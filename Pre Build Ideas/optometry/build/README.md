# Exam OS — build 27

Pre-built vertical AI OS for optometry practices.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py            # ~8,200 patients, exams, purchases
python3 test_exam_os.py    # 33 assertions
```

Launch name **`prebuild-exam-os`** (port 8847, 127.0.0.1 only).

## What it is

"Clearwater Eye Care" — 2 doctors, $2.6M. Four modules: **message triage**, **recall engine**,
**capture board**, **Rx discipline**.

## The refusals it is organised around

**The ocular-emergency stop.** Five typed emergencies — flashes/floaters with a curtain (retinal
detachment), chemical splash (with the irrigate-now instruction verbatim), sudden vision loss,
trauma/foreign body, painful red eye with contact wear (keratitis) — each routing immediately with
the *right* instruction per type. Eval costly class = missed emergency (*PERMANENT VISION LOSS ON
A TIMELINE OF HOURS*), recall 1.0.

**The Rx discipline, in all three directions.** A reorder against an expired Rx is refused — *an
exam renews a prescription, not a message* — and offers the exam instead; no expiry recorded reads
refused, never assumed current. `modify_rx` is R0. And `withhold_rx` is R0 too: per the FTC
Eyeglass Rule posture, the patient's prescription is the patient's — a release request drafts
promptly, the system never withholds.

Also: clinical questions unanswered, the recall ladder bounded (3 × 30-day), the capture rate
counted with a floor of 40 exams (*the walkouts are the leak*).

## 10-minute demo

Board → Inbox (the curtain message → same-day instruction; the expired reorder → refused + exam
offered; the Rx request → release drafted) → Recall → ROI → Trust.

## What this does not do yet

- **No integrations.** EHR (RevolutionEHR/Crystal-class), optical POS, contact-lens distributors
  are adapter seams.
- **Triage is deterministic pattern-matching** — a real deployment puts a model behind the routine
  path and leaves the emergency stop and Rx rules exactly as they are.
- **Nothing is sent.**
