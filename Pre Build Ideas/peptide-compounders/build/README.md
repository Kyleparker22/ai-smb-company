# Provenance OS — build 73

Pre-built vertical AI OS for peptide compounders and suppliers.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py                  # 8 SKUs, 48 batches, 48 upstream certs, 12 source changes
python3 test_provenance_os.py    # 62 assertions
```

Launch name **`prebuild-provenance-os`** (port 8896, 127.0.0.1 only).
`PROVOS_DATA_ROOT` relocates the store; the suite uses a temp dir.

## What it is

Four modules on `_kit`: the **rulebook watcher**, **batch packet assembly**, **upstream certificate
verification**, and **complaint intake**.

## The refusals it is organised around

**It never says you are compliant.** `assert_compliance` is R0 and unpromotable. The watcher reports
*relevance* — this change names something on your list, and here is the word that matched — and says
so in the same sentence every time. A monitoring tool that says "compliant" is selling a
determination it cannot make.

**An adverse event is captured, never assessed.** `assess_adverse_event` is R0. The reply tells the
reporter plainly that the system cannot give medical advice and points to emergency care. The record
carries `assessed: false`, and the non-assessment is written to the log as a refusal.

**A batch record is never edited.** `alter_batch_record` is R0 — it is the inspection artifact.

**A packet is never complete by omission.** Seven required records *and* a verified upstream
certificate. `release_batch` is R1, unpromotable, and refuses over any blocker.

## What this does not do yet

- **No source integration.** Real Federal Register / state-board feeds are the first adapter seam;
  changes here are seeded.
- **The watcher matches words, not meaning.** Right for the auditable first pass and deliberately
  over-inclusive; a real deployment puts a model behind the *ranking* and leaves the flagging bias
  exactly as it is.
- **No regulatory content is encoded.** No eligibility list, no claim rules — those move fast and
  belong to counsel (`offerings/peptide-telehealth-os/SPEC.md` §6).
- **No ERP, no batch execution system, no e-signature.** Adapter seams.
- **Nothing is sent.**
