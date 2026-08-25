# Encounter OS — build 75

Pre-built vertical AI OS for multi-state telehealth clinics.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py                # 7 clinicians, ~180 patients, intakes, encounters
python3 test_encounter_os.py   # 101 assertions
```

Launch name **`prebuild-encounter-os`** (port 8898, 127.0.0.1 only).
`ENCOS_DATA_ROOT` relocates the store; the suite uses a temp dir.

## What it is

Four modules on `_kit`: **licensure-aware routing**, **async triage into a prepared chart**,
**paid-but-unseen recovery**, and **documentation defensibility**.

## The refusals it is organised around

**There is no "best available anyway".** `eligible_clinicians()` excludes at the query: a clinician
without the patient's state licence is never a low-ranked option, they are absent. When nobody
qualifies, `route()` returns a **refusal that carries no candidates at all** and says plainly that
this is a licensing decision for the clinic, not a routing problem. A fallback here would be clicked
on the worst possible day.

**An inactive licence is not a licence.** The seed contains a clinician licensed in NY who is
inactive, and the suite asserts NY has zero coverage. That is the bug this module exists to prevent.

**An encounter without its note cannot be closed — by anyone.** `close_undocumented` is R0. Seven
required elements, and the refusal lists which are missing.

**Location is asked, never guessed.** A patient with no state recorded refuses rather than defaults.

## What this does not do yet

- **No EHR, video, e-prescribing, payments or licence-board integration.** Adapter seams — and the
  licence list is operator-maintained data here, not verified against any board.
- **It routes by licence and current load only.** No scheduling, no clinician preference, no
  language matching.
- **Triage is deterministic pattern-matching**, biased toward stopping. Right for the urgent half.
- **No clinical content of any kind.**
- **Nothing is sent.**
