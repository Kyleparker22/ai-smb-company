# YourCo Monthly Close Ritual

Runs on the first Monday of each month. Target: ~30 minutes once the data is in place.

## Steps
1. **Revenue check** — open `revenue.md`. Confirm all invoices issued last month are logged. Confirm paid dates are accurate.
2. **Expense check** — open `expenses.md`. Pull credit card and bank statements; log any missing entries with category. **While the ⚠ OPEN block at the top of that file stands, this step also closes it:** the pre-formation build spend inside the Founder's repayable founder loan (~$3,000, `Assumptions!B141`) is an estimate, and the statements you are already pulling are exactly what reconciles it. Supply the Anthropic top-up amounts, match May–August 2026 charges, then update the model and sweep any material change to `06_business-plan.md`, `finance/model-assumptions.md` and `decisions/2026-08-10_cash-structure-and-model-recalibration.md`.
3. **Token spend** — Atlas updates `token_spend.md` (yourco's own/internal spend). Confirm rollup matches the model-API bill.
4. **Runway update** — update `runway.md`: cash on hand, last month's net, MRR (if applicable), burn, runway in months.
5. **Per-engagement margin** — for each active client: revenue collected − token spend − allocated overhead. Source of truth is the client's `clients/<client>/cost.md` ledger (`log-build-cost` skill; phases discovery/build/tools/run): update its **Phase totals** and **Monthly run cost** row from the ledger + any metered console/tool numbers, then compute margin. A client folder with real work but no cost.md, or a month of activity with no ledger rows, is itself a logging gap — flag it. Anything negative or trending negative gets a note in that client's folder and a line in the readout.
6. **Decisions** — if anything is off (margin collapsing, expenses creeping, runway shortening), log it in `/decisions/` with date and reasoning.
7. **Exec readout** — write a one-pager at `readouts/YYYY-MM.md` the Founder can read in 60 seconds. Atlas drafts; the Founder signs.

## When a month was MISSED (added 2026-08-23 — the gap this SOP did not cover)

The close is monthly and `runway.md` depends on it, so a skipped month is not a gap you can fill later
from memory. As of 2026-08-23 `readouts/` holds **only `2026-06.md`** — July and August never closed —
and the consistency watchdog has been reporting it.

**Catch-up procedure, oldest month first, one month per run:**
1. **Never backfill from memory.** Statements, invoices and the model-API bill are the only admissible
   sources. A reconstructed month that looks complete is worse than an absent one, because the next
   close trusts it.
2. **Reconcile against dated evidence only.** Bank/card statements for that month, `token_spend.md`
   rows dated inside it, and the weekly `loops/finance/` artifacts written at the time.
3. **Anything you cannot source, write as a named gap** in that month's readout — "expenses
   unreconciled: no statement pulled" is a valid line. Do not smooth it into an estimate.
4. **Runway is computed, not carried.** `runway.md` takes cash-on-hand, which only the Founder can supply
   (`[the Founder to supply]`). Without it the readout says **runway: cannot be computed** and names the
   missing input. HQ currently shows `Runway: TBD` for exactly this reason — that is the SOP working.
5. **One month per run.** Closing three months in one pass produces one blurred reconciliation, not three.

**A missed close is itself a watchdog trigger** — see the list below.

## Watchdog triggers (escalate to the Founder the same day)
- **A month with no `readouts/YYYY-MM.md` by the 8th** (added 2026-08-23; `runtime/consistency-check.py`
  reports it, and it has been reporting it since July went unclosed)
- Any client where margin < 50% for two consecutive months
- Runway < 6 months
- Token spend on a client growing faster than revenue for that client
- Any single client > 40% of revenue (concentration risk)
