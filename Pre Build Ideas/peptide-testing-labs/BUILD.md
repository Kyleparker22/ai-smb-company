# Assay OS — peptide & research-chemical testing labs (build 72)

**Working name:** Assay OS · **Launch:** `prebuild-assay-os` · **Port:** 8895

## The idea

A third-party analytical lab's product is not the instrument run — it is the **certificate**. In
this market certificates are routinely forged, recycled between lots, or edited after the fact, so
the lab's whole franchise rests on a PDF that anyone can alter and nobody can check. Meanwhile the
bench itself leaks: turnaround is the thing customers actually buy, and most of the middle of the
process is email, spreadsheets and hand-assembled documents.

**Buyer:** lab owner / lab manager. Thinks in samples per week, turnaround hours, and repeat brands.
(Live warm prospect in this shape: Sample Contact, `crm` deal `d21`.)

## The bleeding neck

- **Turnaround is the product**, and the middle of it is manual: intake, custody, result transcription,
  certificate assembly, delivery.
- **The certificate is forgeable**, which means the lab's reputation defends itself by assertion.
- **"Where's my result?"** consumes the same people who run the instruments.
- **Customers ask what the number means** — the one question the lab must never answer.

## Modules

1. **Sample intake + chain of custody** (Operations) — received → logged → aliquoted → analysed.
   An incomplete chain **blocks** the certificate; it is not a warning.
2. **Specification grading** (Operations) — deterministic against a published spec, showing its
   reasons. `INDETERMINATE` is a real grade: an unmeasured line never reads as a pass.
3. **Certificate release** (Operations) — draft → **named human releases** → token + sha256 over the
   exact reported values. A correction **supersedes**; nothing is overwritten.
4. **Public verification lookup** (embedded AI surface) — the differentiator. A stranger checks a
   token and gets genuine / superseded / unknown / compromised, and never a safety opinion.

## Guardrails (load-bearing)

- `release_coa` — **R1, never promotable.** A certificate is a public analytical claim carrying the
  lab's name. No streak promotes it.
- `alter_result` — **R0.** Analytical values are never edited by software.
- `backdate_coa` — **R0.** A certificate's dates are evidence.
- `interpret_for_health` — **R0.** Whether a substance is safe to use is not a lab's statement.
- A **draft has no token and no hash** — a leaked draft cannot pose as an issued certificate.
- Eval costly class: **a failing sample graded as passing.**

## ROI model

Throughput at the same bench → revenue · certificate production hours → time saved · status-chasing
hours → time saved · certificates your customers can verify → **scenario** (we refuse to price the
operator's brand protection with a borrowed benchmark).

## 10-minute demo

Board → In flight → draft on a broken custody chain (refused, missing steps named) → release a clean
one → **Public lookup**: real token (genuine), invented token (unknown) → supersede, then look the
*old* token up (superseded, retained) → "is 97% pure safe to inject?" (refused by class) → ROI → eval.

## Build prompt (§8)

Build `Pre Build Ideas/peptide-testing-labs/build/` on `_kit`. Stdlib, JSON store, 127.0.0.1:8895,
launch `prebuild-assay-os`. Seed "Rivermark Analytical": 12 brand clients, ~240 samples across 10
analytes, results spanning clean / off-spec / identity-failure / partial panels, custody chains
including broken ones, ~230 released certificates. Eval costly class = a FAIL graded PASS. Tests pin
the INDETERMINATE rule, the hash changing when a value changes, release being unpromotable at any
streak, custody blocking release, the four lookup answers, supersede-not-overwrite, the health
interpretation refusal, and every ROI blank.
