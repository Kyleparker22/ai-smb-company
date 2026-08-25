# Finance Close Loop — (pointer)

> **Owner: Charles.** The monthly close. The full SOP lives at **`finance/monthly_close.md`** (kept next to the finance ledgers it operates on — `expenses.md`, `revenue.md`, `runway.md`, `token_spend.md`). This pointer exists so the loop is discoverable alongside the other loop SOPs.

- **Runtime:** `runtime/prompts/finance-close.md` → `runtime/run-loop.sh finance-close`; timer `yourco-finance-close.timer` (monthly).
- **Output:** `loops/finance-close/<date>.md`.
- **Step 0 / format / watchdog triggers:** see `finance/monthly_close.md`.
- ⚠️ **Behind as of 2026-08-23** — `finance/readouts/` holds only `2026-06.md`; July and August never
  closed. `finance/monthly_close.md` §"When a month was MISSED" is the catch-up procedure: oldest
  month first, one per run, dated evidence only, never backfilled from memory.
