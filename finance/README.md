# /finance/

YourCo's lightweight finance system. No QuickBooks, no SaaS bookkeeping — not yet. Principle: a folder of markdown ledger entries plus a monthly close ritual gets ~90% of what QB would, with zero migration debt later.

## What's in here

20 files. The list below covered 6 of them until 2026-08-23 — including no mention that the
**Operating Agreement** lives in this folder, which is the most legally consequential document yourco has.

### The ledgers — the system of record
| File | What it is |
|---|---|
| `revenue.md` | Month-by-month revenue (client, amount, invoiced, paid). Empty: pre-revenue. |
| `expenses.md` | Month-by-month expenses (vendor, category, amount, date). |
| `token_spend.md` | Model spend by engagement — yourco's largest variable cost. Append via the `log-internal-cost` skill; reconciled against the meter by `runtime/cost_reconcile.py`. |
| `runway.md` | Cash · MRR · burn · runway. Updated at each close. |

### The close
| File | What it is |
|---|---|
| `monthly_close.md` | The SOP for the close ritual (first Monday). |
| `readouts/YYYY-MM.md` | The executive one-pager per month. ⚠️ **Only `2026-06` exists** — see below. |

### The KPIs — added 2026-08-25
| File | What it is |
|---|---|
| `kpi-definitions.md` | **The nine KPIs, each with its refusal condition.** Seven of the nine are undefined at n=0 — six need customers, and burn multiple divides by net new ARR, which is zero. They are defined *now*, with the exact precondition each is waiting on, so client #1 does not arrive to an underived formula. Owns the reasoning; `dashboard/kpis.py` owns the arithmetic; the two are cross-checked by `runtime/consistency-check.py`. |
| `actuals.json` | **The machine-readable close figures** — plus `invoices.rows`, added 2026-08-25 and deliberately empty: the instrument for Harry's *invoices paid within terms*, installed before the first invoice because a meter installed afterwards measures nothing that already happened. `paidOn: null` means outstanding, which is **not** the same as late — an invoice still inside its terms is neither.  — cash, burn, revenue, closed months, customer events. Everything actual in this folder lived in prose, so no surface could compute a KPI without a human re-reading a memo. This carries only what `runway.md` has already **confirmed**, each with its own `asOf` and `confidence`; the watchdog fails if a figure here stops appearing there. **Update it at every close, in the same pass as `runway.md`.** |

### The model
| File | What it is |
|---|---|
| `yourco-financial-model.xlsx` | The 5-year model. **Canonical**; the plan defers to it. Recalculated in Excel, never estimated. |
| `model-assumptions.md` | Every assumption written out, so the model is auditable without opening Excel. |
| `model-review_charles_*.md` | Dated reviews by Charles. Point-in-time records — do not update. |

### `legal-docs/` — undocumented until today
| File | What it is |
|---|---|
| `operating-agreement-DRAFT.md` | **The OA (v5, 490 lines).** ⚠️ DRAFT, in counsel review, **3 unsigned blocks**. Nothing here is executed. |
| `oa-review_ray_2026-08-05.md` | Ray's redline pass on it. |
| `schedule-b-valuation-worksheet.md` | The Schedule B valuation worksheet. |
| `IRS_CP575G_EIN_letter.pdf` | The EIN letter — the entity's birth certificate. |
| `business-info.md` | Entity details (address, EIN, formation). The `.docx` was archived 2026-08-24 — same content, two days older. |
| `insurance-plan.md` | The insurance plan. |

> ⚠️ These are **records, not advice**, and the OA is a **draft under counsel review** — see
> `processes/counsel-gates.md` before treating any clause as settled.

## The close: June and July are closed; August is due 2026-09-07

**July was closed 2026-08-24, 21 days late** (`readouts/2026-07.md`) — drafted from receipt evidence
only, with five gaps named rather than estimated, and unsigned pending the Founder. **August is not overdue:**
the close for month M runs the first Monday of M+1, so August's is due **2026-09-07** — and it will
not fire while the runtime is paused.

The history below is kept because the failure modes are the lesson. `readouts/` held `2026-06.md` and
nothing else for three months, and the reason it went unnoticed is two bugs that hid each other:

1. HQ's loop health had `finance-close` marked **untracked**, with the note *"audit 07-04: never wired
   on host"* — true when written, wrong since the timer landed. Untracked loops are excluded from the
   count, so HQ never scored it.
2. When that was corrected, it still read *"never ran"* — because loop health matched `YYYY-MM-DD`
   filenames and a readout is `YYYY-MM`.

Both fixed 2026-08-23. It now reads honestly: **stale, 83 days.**

**Corrected 2026-08-24 — the third cause was misdiagnosed.** This page previously said the 08-03 run
"produced nothing — a loop that runs and writes nothing." The VPS run log says otherwise: it never
ran. In 643ms it logged three failures —

```
finance-close FAILED (git pull rebase conflict)
{"result":"Credit balance is too low", "api_error_status":400, "duration_ms":643}
finance-close FAILED (exit 1)  ·  FAILED (git push, exit 1)
```

— so the model was never called and July's close simply never happened. The distinction is not
pedantic: *writes nothing* points at the prompt or the SOP, *credit exhausted* points at billing, and
only one of those was true. **Credits were restored 2026-08-04, the very next day** (`token_spend.md`;
auto-recharge on, receipt-confirmed 08-17) — but the monthly timer (`Mon *-*-1..7`) had already fired
for August, so nothing re-ran it, and with the runtime paused September will not fire either.

The standing lesson: `runtime/runtime-alarm.sh` exists precisely for credit death (it is
API-independent so it survives a dead balance) and the timer is armed with its webhook. **A missed
monthly loop needs a re-run, not just an alarm** — an alarm tells you it failed; nothing re-queues it.

## When to graduate to a real finance stack
Get a real bookkeeper and a real QB instance when ANY of these hit:
- Revenue crosses a tax/audit threshold (talk to a CPA — varies by state and entity)
- You hire even one employee or 1099 contractor on payroll
- You take on outside capital (investors, debt)
- You have ~10 active engagements (volume crosses what manual close can handle)
- You spend more than a couple hours on the monthly close

Until then: this folder is the system of record.

## Conventions
- Revenue recognized when invoiced; separate column for paid date.
- Expense categories: `model_spend`, `tooling`, `professional_services`, `marketing`, `ops`, `other`.
- Token spend tracked per engagement (Atlas's job).
- Monthly close runs on the first Monday of each month.
