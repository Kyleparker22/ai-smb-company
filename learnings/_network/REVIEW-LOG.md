# _network — immune-system review log (append-only audit trail)

One row per candidate that crosses a tenant boundary into `candidates/`. Every vaccination in `vaccinations/` must trace to a row here; every row to a candidate. Dispositions: **approved / rejected-leakage / rejected-not-general / merged-duplicate**. Gate doc: `runtime/immune/README.md`. Git history = tamper evidence — rows are never edited or deleted; corrections are new rows referencing the old.

| Date | Opaque engagement ID | Candidate (filename) | Disposition | Reviewers (quality/isolation/publication) | Published as |
|---|---|---|---|---|---|
