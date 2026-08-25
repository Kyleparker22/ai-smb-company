# Assay OS — build 72

**Run:** `prebuild-assay-os` (`.claude/launch.json`) → http://127.0.0.1:8895
**Seed:** `python3 seed.py` · **Tests:** `python3 test_assay_os.py` (79 assertions)
**Data:** JSON under `data/`, synthetic. `ASSAYOS_DATA_ROOT` relocates it (the suite uses a temp dir).

Rivermark Analytical — a six-person third-party testing lab, ~240 samples on the book.

## What it is

Four modules on `_kit`: **sample intake with chain of custody**, **specification grading**,
**certificate release**, and the one that matters — **a public verification lookup**.

## The refusals it is organised around

**A missing measurement is never a pass.** `INDETERMINATE` is a first-class grade. The single most
profitable dishonesty available to a testing lab is letting an unmeasured line read as a clean one,
so the grader names what it did not measure and refuses to call it anything.

**An analytical value is never edited.** `alter_result` and `backdate_coa` are R0 and permanently
unpromotable. A correction is a **new certificate that supersedes the old one**, and the old token
still resolves — reporting itself as superseded. Deleting it is how a lab loses the argument about
what it said and when.

**A certificate is never released without a named human.** `release_coa` is R1 with
`never_promote`, so no streak of any length promotes it — the test asserts that at a streak of
9,999. A **draft has no token and no hash**, so a leaked draft cannot pose as an issued certificate.

**The lab never says anything is safe.** `interpret_for_health` is R0. Every certificate and every
lookup carries the same scope sentence: this reports what was measured in the submitted sample, and
it is not a safety assessment, a fitness-for-use opinion, or medical advice.

## The verification surface (the point of the build)

Release mints a token and a **sha256 over the exact reported values**. Anyone holding a certificate
can look the token up and get one of four answers: **genuine** (issued here, unchanged),
**superseded** (issued, then replaced — ask for the current one), **unknown** (never issued by this
lab), or **genuine but the stored values no longer hash to what was released** — reported loudly as
compromised. An unknown token leaks nothing about any real record.

This is the same architecture as Sample Product, pointed at a certificate instead of a storm date.

## 10-minute demo

Board (in flight, median turnaround counted from the sample log) → In flight → draft a certificate
on a sample with a **broken custody chain** and watch it refuse, naming the missing steps → release
a clean one and get a token → **Public lookup**: paste the token (genuine), then invent one
(unknown) → Certificates → supersede a released certificate and look the *old* token up again →
Trust: ask "is 97% pure safe to inject?" and watch it refuse by class → ROI → the eval, where the
costly class is a failing sample graded as passing.

## What this does not do yet

- **No instrument integration.** Parsing real HPLC/MS output is the first adapter seam; results
  here are seeded, not acquired.
- **No LIMS, no billing, no shipping.** Adapter seams.
- **The hash proves the certificate matches this lab's record — nothing more.** It cannot prove the
  sample came from the lot the client claims, and this build does not pretend otherwise.
- **Grading is deterministic against a published spec** — correct for this job, and deliberately
  not a model.
- **No regulatory content.** Compounding eligibility and RUO rules move fast and are not encoded
  anywhere here (`offerings/peptide-telehealth-os/SPEC.md` §6).
- **Nothing is sent.**
