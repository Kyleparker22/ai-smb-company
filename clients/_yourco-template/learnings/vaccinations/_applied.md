# vaccinations — per-client application ledger

**Append-only.** One row per vaccination, added when a loop absorbs it (or determines it doesn't apply). This ledger is what makes "every client protected within hours" a checkable claim instead of a slogan — and later, Trust-Ledger material (counts only). The consistency-check coverage-staleness invariant reads this file: any `high`-severity vaccination not acknowledged here within its window = drift.

| Vaccination ID (filename) | Date absorbed | What changed (guardrail row / eval case / prompt adjustment — or `n/a` + why) | Applied by (loop/agent) |
|---|---|---|---|
