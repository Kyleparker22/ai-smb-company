# ledger/ — the per-client outcome ledger (self-proving-invoice substrate)

**What this is:** the append-only JSONL eval ledger every engagement captures **from day one**, so month 1's invoice has month 1's data. The monthly Self-Proving Invoice (`offerings/self-proving-invoice/SPEC.md`) is a render step over this data; the moat layer (eval · approval · audit log) writes it as exhaust of acting — no end-of-month reconstruction, ever. The Receipts (`../receipts/`) reads the same trail.

**Files:** one per month — `ledger/YYYY-MM.jsonl`. One JSON object per line, one of the five record types in `_SCHEMA.md`. The generator loop (builds at first billable month) reads a month's file, aggregates, and renders the R1 invoice draft; every invoice line footnotes its ledger IDs.

## The four rules that make it invoice-grade (spec §3.1 — non-negotiable)
1. **Append-only** — corrections are new records referencing old IDs, never edits. No admin path rewrites history, including for yourco.
2. **Write-at-source** — the runtime hooks write records as a side effect of acting; if a hook failed and records are missing, the invoice states the gap — we never backfill from memory.
3. **Incidents are mandatory** — an `incident_record` is written even when impact = none. A month with zero incidents renders an explicit attested "zero incidents" line generated from the *absence* of records plus the watchdog's I-was-running heartbeat — silence from a dead watchdog must not render as a clean month.
4. **Outcome metrics name their source** — client system, count, or qualitative + label. No number without provenance; the generator refuses to render an outcome line lacking a source field.

## What this data is for (and is not)
The lines **prove; they never price.** The retainer is flat — the ledger answers "was it worth it," not "what does it cost." Action counts never become a meter. Customer PII stays out of invoice/console rollups (aggregate only).

## Wiring on clone
- The build (`../02_build.md`) hooks every module's act/approve/eval/incident paths to append here — capture is automatic at scaffold time, not retrofitted.
- Autonomy promotions (`../autonomy-matrix.md` streak rule) write an `autonomy_event` at the moment of promotion.
- Charles reads this at monthly close; the invoice generator (when built) runs at the same cadence.
