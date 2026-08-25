# Charles — Stage 2: Build

## Build approach
Charles is a **handoff build**, not a from-scratch one. The finance loop SOP, the four ledgers, and one real artifact already exist — they ran under Atlas. Building Charles means: (1) give the loop a named owner, (2) formalize the monthly close as his, (3) hold him to a finance-specific eval set, and (4) keep Atlas as a pure observer that reads his output. Lowest-risk live build in the roster because the substrate is already in place.

## Components
### 1. Finance Pulse loop
`processes/loops/finance.md` — Monday AM. Now runs as Charles (signature, ownership updated). Reads the four ledgers + inbox, computes state, flags gaps + watchdogs, writes `loops/finance/YYYY-MM-DD.md`, posts to `#all-yourco`.

### 2. Ledger system of record
`/finance/revenue.md`, `expenses.md`, `token_spend.md`, `runway.md` — created 2026-06-07, already populated with real figures (Google Workspace $8.73; Apollo $50 cancelled 2026-06-06). Charles keeps these current; they are the books.

### 3. Monthly close
`/finance/monthly_close.md` ritual — first Monday of each month. Charles reconciles, updates `runway.md`, computes per-engagement margin, and writes `readouts/YYYY-MM.md` for the Founder to sign.

### 4. Tax-prep handoff (v0 = drafts)
Quarterly-estimate and year-end 1099 packets prepared as CPA-ready drafts. No filing.

## Inherited vs new
- **Inherited from Atlas:** finance loop SOP, the 2026-06-07 finance artifact, the ledgers.
- **New for Charles:** named ownership + signature, the eval set (`03_eval.md`), monthly-close ownership, the Atlas↔Charles boundary (Charles owns books; Atlas observes).

## Patterns reused / contributed
- **Reuses:** the loop SOP convention, the closed-loop "What I'd do differently next run" feedback section, the watchdog-trigger format, Slack-summary delivery.
- **Contributes to `yourco-template`:** a clean **finance/bookkeeping module** (ledgers + pulse + close + readout) — likely reusable as a client-facing finance digital employee later.

## How Charles works — the SOPs

### A. Weekly Finance-Pulse SOP (Mon ~7:15 AM ET)
Canonical SOP: `processes/loops/finance.md`. Runtime prompt: `runtime/prompts/finance.md` → `runtime/run-loop.sh finance`. Output: `loops/finance/YYYY-MM-DD.md`. Steps as Charles runs them:
0. **Read learnings (Step 0).** Last ~5 entries in `/learnings/finance/` + `/learnings/ops/`; apply what fits; list applied entries in the artifact. (Folders may be empty pre-launch — expected.)
1. **Boot context.** Read `CLAUDE.md` + `finance/README.md` for current positioning/conventions.
2. **Logging-gap check.** Is each ledger current as of last week? See gap-detection rules below.
3. **Inbox scan.** Gmail invoice/receipt/payment/payroll/vendor threads, last 7 days → list anything that should be logged but isn't. Cross-read `learnings/ops/` events (e.g. the credit-death event left *no* Gmail receipt yet had a money consequence).
4. **Compute current state.** Cash, MRR, burn, runway — methods below.
5. **Per-engagement margin.** Per live/expansion client: `revenue collected − token spend − allocated overhead`. Flag negative/trending-negative. "No active engagements" when pre-revenue.
6. **Apply watchdogs.** (See `03_eval.md`.) If any fired, lead the artifact with it.
7. **Write artifact** in the template below.
8. **Slack** — 3 lines to `#yourco-charles`, signed "— Charles, YourCo Ops"; lead with a fired watchdog.
**Gate:** read/compute/write/post + draft only. No email send, no payment, no filing.

### B. Monthly-Close SOP (first Mon of month)
Canonical SOP: `finance/monthly_close.md` (lives next to the ledgers; `processes/loops/finance-close.md` is a discoverability pointer). Runtime: `runtime/prompts/finance-close.md` → `runtime/run-loop.sh finance-close`; timer `yourco-finance-close.timer`. Outputs: `finance/readouts/YYYY-MM.md` (exec one-pager) + `loops/finance-close/YYYY-MM-DD.md` (run record). Target ≤30 min once data is in place. Steps:
1. **Revenue check** — every invoice issued last month logged in `revenue.md`; paid dates accurate.
2. **Expense check** — pull card/bank statements; log missing `expenses.md` entries with category; reconcile each booked recurring line against the actual charge (this is where the Canva $15→$18 and Instantly $97-vs-$316 deltas got caught).
3. **Token/model spend** — confirm `token_spend.md` rollup matches the model-API bill (the Anthropic top-up). This is YourCo's largest variable cost — reconcile it explicitly.
4. **Runway update** — set cash on hand from the bank statement (the Founder supplies), compute net = `revenue − (expenses + token_spend)`, update MRR, recompute burn + runway in `runway.md`; append a `History` row.
5. **Per-engagement margin** — full margin per active client; anything negative/trending gets a note in that client's folder + a readout line.
6. **Decisions** — anything off (margin collapse, expense creep, runway shortening) → a dated `/decisions/` entry.
7. **Exec readout** — write `readouts/YYYY-MM.md` (template below). Charles drafts; the Founder signs.
8. **Feed-forward** — if a pattern emerged, write a `learnings/finance/` entry the next pulse reads at Step 0.
**Gate:** same as the pulse — reconcile and report; never file or pay.

## Ledger schema (system of record)
Markdown tables in `/finance/`; ~90% of QuickBooks with zero migration debt. Charles keeps these current; they ARE the books.
- **`revenue.md`** — `| month | client | description | amount | invoice_date | paid_date | status |`. Revenue recognized when invoiced; `paid_date` separate. Maintains running MRR / MTD / YTD. (Today: empty — pre-revenue, $0.)
- **`expenses.md`** — `| month | vendor | category | description | amount | date | status |`. Categories: `model_spend`, `tooling`, `professional_services`, `marketing`, `ops`, `other`. Carries a "Recurring monthly costs" block + a notes log for anomalies/TBDs.
- **`token_spend.md`** — `| month | engagement | model | description | est_cost | date | source |`. Maps to `model_spend`. Largest variable cost; reconciled to the API bill at close.
- **`runway.md`** — `Current snapshot` table (cash / MRR / burn / runway) + a `History` table appended each close.

## Cash / MRR / burn / runway calc method
- **Cash on hand** — *not computed*; the Founder supplies from the bank statement (human-in-loop). Charles flags it as TBD until set rather than guessing.
- **MRR** — sum of recurring retainers across live engagements in `clients/_pipeline.md` (signed only — a sent proposal like Sample Client's $1,000/mo is *pipeline*, not MRR, until signed). Today: **$0**.
- **Monthly burn** — rolling 3-month average of `expenses.md` + `token_spend.md`; pre-revenue, use the booked recurring subtotal + known usage. Always report **booked burn** and **corrected burn** separately when anomalies/TBDs exist (the Jun 22 pulse pattern), so the gap between "what the ledger says" and "what's really going out" is explicit.
- **Runway (months)** = `cash on hand ÷ monthly burn`. Uncomputable without cash → report "not computable, needs cash figure," never fabricate. Leads the artifact when <6.
- **Per-engagement margin** = `revenue collected − token/model spend − allocated overhead`; gross-margin % = margin ÷ revenue. The Skok health bars (margin ≥50%, LTV:CAC ≥3, payback <12mo) are applied once revenue exists; reported N/A pre-revenue.

## Gap-detection rules
A "logging gap" is any money event that should be in a ledger but isn't. Charles surfaces (never silently fixes destructively) by these rules:
1. **Inbox vs ledger** — every invoice/receipt/payment/vendor thread in the last 7 days must have a matching ledger row; unmatched → gap.
2. **Recurring-charge drift** — a booked recurring line whose actual charge differs from the booked amount → reconcile-this-week gap (Canva $15→$18; Instantly $97 vs $316).
3. **TBD amounts** — any ledger row with `amount: TBD` for a tool that has now billed → resolve gap.
4. **Cross-read ops events** — a `learnings/ops/` event with a money consequence but no Gmail receipt (e.g. the Anthropic credit top-up) → gap.
5. **Logging silence** — a week with no `revenue.md`/`expenses.md` entries while engagements are live → watchdog flag.
6. **Backfill items** — known historical un-logged charges (HighLevel $297/mo) stay listed as open gaps but are *flagged-not-chased* once the Founder defers supplying data.

## Tax-prep handoff (v0 = CPA-ready drafts, never filing)
Two packets, drafts only, gated:
- **Quarterly estimate** — pull YTD net from the ledgers, estimate quarterly liability, draft a one-pager for the CPA. Charles computes; **the Founder/CPA file.**
- **Year-end** — categorized P&L from `expenses.md`/`revenue.md`, 1099 candidate list (any contractor paid ≥ threshold), receipts index. Output: a clean handoff folder a CPA can work from.
Aligns with the `finance:tax-prep` skill convention. **Gate: prepare and hand off; never file.**

## Connectors (and the gate)
Charles is read/report/draft-only on every connector:
- **Gmail (`founder@yourco.example.com`)** — `search`/`read` only for receipts/invoices/payments. **Draft** reminders allowed; **send is must-approve** (Harry sends post-revenue).
- **Slack `#yourco-charles`** — post the pulse summary. (Digest also flows to `#all-yourco`.)
- **Workspace ledgers/artifacts** — read + write (the books).
- **v1 (on graduation trigger):** a real bank/QuickBooks feed for auto-reconciliation — still report-only; money movement stays must-approve.
The always-on runtime denies send/delete/Bash globally — Charles is structurally incapable of moving money in v0.

## Autonomy
Charles runs on yourco's **Autonomy-by-default standard** (`processes/autonomy-matrix.md`; standard `decisions/2026-06-25_autonomy-by-default-standard.md`). Every action sits on a rung (R0 Observe · R1 Draft/propose · R2 Auto+notify+reversible · R3 Fully autonomous); the default trajectory is full autonomy, earned per-action on Kolby's eval evidence — but **money-movement + irreversible actions are hard-capped at R1 and never run unattended.** Charles's design principle is *he reports; he never moves money* — so his ceiling is deliberately read/report, not execute.

| Action | Rung | Ceiling | Control / note |
|---|---|---|---|
| Ledger reads · state compute · per-engagement margin · gap analysis | **R3** | R3 | inherently safe (read/observe); auto on the pulse |
| Write pulse artifact + monthly readout (in git) | **R3** | R3 | reversible in git |
| Slack post (`#yourco-charles` + `#all-yourco` digest) | **R3** | R3 | reversible internal post |
| **Numbers surfaced to the Founder** (cash/MRR/burn/runway/margin) | **R3** | R3 | read/report — but every figure passes the **no-fabrication eval gate** (`03_eval.md` hard gates 1–4: traced to a source, recompute-matched, runway honesty); honesty over completeness |
| Draft an invoice/AR reminder (no send) | R1 | R2 | climbs only on Harry/Kolby eval record; **send stays gated** |
| **Send any invoice / record or execute any payment / move money** | **R1 — hard floor** | R1 | money movement; never auto, never unattended — Harry executes post-revenue, the Founder commits |
| **File anything with a tax authority** | **R1 — hard floor** | R1 | irreversible/regulated (financial); draft-for-human/CPA-review only |
| Set cash-on-hand in `runway.md` | R1 | R1 | human-in-loop — the Founder supplies the bank figure |

**Hard-floor / gated actions (never climb on evidence):** any invoice send, any payment or money movement, any tax filing. These are R1 by design per the matrix's money-movement + irreversible/regulated-advice rows — the runtime's structural deny on send/delete/Bash is the backstop. Reporting actions are R3; *executing* on money is the one thing Charles never does. New/unproven actions start R1 and climb only on Kolby's zero-incident eval record; any incident holds or resets the rung.

## Closed-loop wiring
- **Trigger:** Mon finance pulse (after sales) + first-Mon monthly close — scheduled on the runtime.
- **Artifact:** dated `loops/finance/YYYY-MM-DD.md` + monthly `finance/readouts/YYYY-MM.md`.
- **Feedback:** the artifact's "What I'd do differently next run" (the Founder fills) + "What worked this run."
- **Feed-forward:** patterns written to `learnings/finance/`, read at **Step 0** of the next run → behavior adjusts. (Folder empty today — expected pre-launch; the Jun 22 run is the live example of reading `learnings/ops/` to catch the biggest money item of the week.)

## Template — weekly pulse readout (`loops/finance/YYYY-MM-DD.md`)
```
# Finance Pulse — YYYY-MM-DD

## Watchdogs fired
(If any — lead with these. Otherwise: "None.")

## Current state
- Cash: $X (as of YYYY-MM-DD) | or "TBD — the Founder to supply"
- MRR: $X
- Estimated burn: $X/mo booked | $Y/mo corrected (anomalies/TBDs)
- Runway: N months | or "not computable — needs cash figure"

## Logging gaps to fix this week
(Entries that should be in a ledger but aren't — by gap-detection rule)

## Per-engagement margin
(One line per live client: revenue − token spend − overhead = margin (%); "no active engagements" if pre-revenue)

## What to do this week
(Specific, ordered actions — log expense X, reconcile Y, set cash in runway.md, etc.)

## What I'd do differently next run
(Empty — for the Founder to fill before next Monday)

## What worked this run
(1–2 wins to amplify; future runs read this too)

## Learnings applied this run
(/learnings/finance/ + /learnings/ops/ entries that influenced this run; "None" if none)
```

## Template — monthly-close packet (`finance/readouts/YYYY-MM.md`)
```
# YourCo Finance Readout — YYYY-MM
_Charles drafts; the Founder signs. Read in 60 seconds._

## Headline
(One line: the single most important money fact of the month.)

## Cash & runway
- Cash on hand (close date): $X
- Net for the month: $X  (revenue $X − expenses $X − model spend $X)
- Monthly burn: $X/mo   | Runway: N months

## Revenue & MRR
- MRR: $X   (Δ vs last month: $X)
- Revenue this month: $X   | YTD: $X
- (Pre-revenue: "No revenue yet — $0 MRR.")

## Unit economics (Skok lens — N/A until revenue)
- Gross margin / engagement: $X (%)  | blended: %
- CAC: $X  | LTV: $X  | LTV:CAC: x  | CAC payback: N mo
- Retention / NRR: %

## Per-engagement margin
(Table: client | revenue | model spend | overhead | margin | margin %)

## Expenses this month
(By category: model_spend / tooling / professional_services / marketing / ops / other; flag creep)

## Watchdogs & decisions
(Anything that fired; links to /decisions/ entries opened)

## Reconciliation status
- Revenue reconciled: Y/N | Expenses vs statement: Y/N | Token spend vs API bill: Y/N
- Open logging gaps carried forward: (list)

## Next month — watch list
(What Charles is watching: TBD tiers, expiring trials, margin trends)
```

## Build status
- [x] Ledgers exist and populated (`/finance/`)
- [x] Finance loop SOP exists (`processes/loops/finance.md`); close SOP at `finance/monthly_close.md` + pointer
- [x] Engagement docs scaffolded + deepened (this folder)
- [x] SOP ownership handed to Charles (signature + refs updated)
- [x] Pipeline + roster updated (Charles → live/in-build)
- [x] Running live as Charles — pulses through 2026-06-22 in `loops/finance/`, signed "— Charles, YourCo Ops"
- [ ] `contact@yourco.example.com` provisioned (manual — the Founder, not blocking v0; runs under the Founder's identity meanwhile)
- [ ] Cash-on-hand set in `runway.md` by the Founder (unblocks runway math — the standing #1 blocker)
- [ ] First monthly-close run as Charles → readout in `finance/readouts/` confirmed against eval

## Known overlay decisions
- **v0 runs under the Founder's identity** until `contact@yourco.example.com` exists (same as Atlas/Reilly/Reed v0); Slack signed "— Charles, YourCo Ops" by convention.
- **Atlas stays the reader, not the owner.** The Monday briefing continues to read `loops/finance/*` — now authored by Charles. No orchestration; siblings, the Founder conducts (decision `2026-06-07_agent-operating-model.md`).
- **Handoff logged** in `decisions/2026-06-07_charles-finance-agent.md`.
