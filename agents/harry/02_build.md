# Harry — Stage 2: Build

## Build approach
Harry is an **activation-ready build**: every SOP, template, ledger mapping, and gate below is wired now, but nothing fires until the trigger (first invoice / first revenue). This is deliberate — when engagement #1 signs, the back office must run on day one, not be invented under pressure. The substrate Harry writes into (`finance/` ledgers, `clients/<client>/` folders) already exists and is owned by Charles for reporting; Harry adds the **transactional-execution layer** on top: the invoice generator, the AR tracker + chase cadence, the bookkeeping-entry discipline, the vendor tracker, and the filing convention. Lowest-risk because Harry reuses Charles's ledger schema verbatim and adds only *doing* on top of *reporting*.

## Components
### 1. Invoicing + AR engine
The core. Reads the locked fee from `clients/<client>/cost.md` + the signed agreement → generates an invoice → stages it for the Founder → tracks it in the AR tracker → stages tone-matched follow-ups on the agreement's late-payment cadence → records the payment in `revenue.md` on receipt. SOP **A** below.

### 2. Bookkeeping data-entry discipline
Every money event (invoice issued, payment received, vendor charge) becomes a clean row in the correct Charles ledger with the correct category. Harry writes; Charles reconciles at close. SOP **B** below.

### 3. Vendor / subscription admin
A tracker of every recurring + usage tool with renewal dates, amounts, and a waste flag (duplicate/unused → cancel candidate). SOP **C** below. (The Instantly duplicate-billing Charles caught is the canonical case this prevents.)

### 4. Document filing
Signed contracts → `clients/<client>/` + `finance/legal-docs/`; invoices → `clients/<client>/invoices/`; receipts indexed for the close. SOP **D** below.

## Inherited vs new
- **Inherited / shared with Charles:** the four ledgers (`finance/revenue.md`, `expenses.md`, `token_spend.md`, `runway.md`) and the `finance/README.md` conventions — same system of record. Harry writes into them using the *existing* schema; he does not restructure them.
- **New for Harry:** the invoice template + generator, the AR tracker + chase cadence, the vendor/subscription tracker, the per-client `invoices/` filing convention, the named ownership of the *send-the-invoice / chase-it / record-it* loop that Charles explicitly defers to him (`agents/charles/02_build.md` §Connectors: "Harry sends post-revenue").

## Patterns reused / contributed
- **Reuses:** the ledger schema + categories, the Step-0 learnings convention, the watchdog-trigger format, the Slack-summary delivery, the must-approve gate language — all consistent with Charles so the finance function reads as one coherent system.
- **Contributes to `yourco-template`:** a clean **AR / invoicing + back-office module** (invoice template + AR tracker + chase cadence + vendor tracker) — directly reusable later as a *client-facing* back-office digital employee (one of the 8 OS pillars: Back Office, per `processes/ai-os-modules.md`). Harry built for YourCo's own books is the prototype of a sellable module.

---

## How Harry works — the SOPs

### A. Invoicing + AR cycle SOP (the core loop)
Fires when a billing trigger hits: a build fee comes due (on signing or go-live per the agreement), a monthly retainer hits its billing day (billed **in advance**), or an expansion closes (new build fee + retainer step-up — Bird's upsell). Steps as Harry runs them:

0. **Read learnings (Step 0).** Last ~5 entries in `learnings/finance/` + `learnings/ops/`; apply what fits; list applied entries in the run record. (Empty pre-activation — expected.)
1. **Confirm the engagement is live.** Check `clients/_pipeline.md` — bill **signed** engagements only. A sent proposal (Sample Client today) is pipeline, **not** invoiced.
2. **Read the locked fee.** From `clients/<client>/cost.md` (Janice's recorded build fee + retainer + billing day) cross-checked against the signed agreement §2. **Never invent an amount;** a missing/ambiguous fee → flag to the Founder, stop.
3. **Check for a duplicate.** Scan `clients/<client>/ar-tracker.md` — is there already an open or paid invoice for this period/item? If yes → do not generate; flag. (Duplicate-invoice guard.)
4. **Generate the invoice** from the template below, pulling YourCo's entity details from `finance/legal-docs/business-info.md`, the next sequential invoice number, the correct amount/period/terms.
5. **Stage it for the Founder.** Save to `clients/<client>/invoices/INV-<n>.md`, draft the send email in Gmail (do **not** send), and surface it in the Slack summary + the AR tracker as `status: staged — awaiting the Founder send`. **GATE: Harry does not send.**
6. **On the Founder's approval + send:** mark the invoice `sent` in the tracker with the sent date; write the revenue row to `finance/revenue.md` (revenue recognized on invoice; `paid_date` left open). 
7. **Track to payment.** Watch the AR tracker / payment connector (when wired) / Gmail for the payment confirmation. On payment: set `paid_date` + `status: paid` in both the tracker and `revenue.md`; file the payment receipt.
8. **Chase if late** (the AR follow-up sequence, below): on the agreement's cadence (interest accrues after 10 days; suspension possible after 15 with notice + 5-day cure — `engagement-agreement.md` §2), stage a tone-matched reminder. **GATE: Harry drafts/stages the reminder; the Founder sends.**
9. **Run record + Slack.** Write what was staged/sent/collected; post a 3-line summary to `#yourco-harry` signed "— Harry, YourCo Ops"; lead with anything overdue.
**Gate (whole SOP):** read / compute / draft / stage / record only. **No external send, no payment.**

### B. Bookkeeping data-entry SOP
Every money event → a clean ledger row. Runs on each transaction (and as a sweep on the Monday cadence, feeding Charles's pulse).
1. **Income** (invoice issued / payment received) → `finance/revenue.md` row: `| month | client | description | amount | invoice_date | paid_date | status |`. Recognize on invoice; fill `paid_date` on payment.
2. **Vendor / tooling charge** → `finance/expenses.md` row: `| month | vendor | category | description | amount | date | status |` using the categorization map below.
3. **Model / token spend** → `finance/token_spend.md` row: `| month | engagement | model | description | est_cost | date | source |` (category maps to `model_spend`).
4. **Flag, never guess.** A charge Harry can't confidently categorize → log with `category: REVIEW` + a note, and surface to Charles, rather than mis-file it.
5. **Hand to Charles.** These rows are Charles's close inputs; Harry writes them clean, Charles reconciles against statements at month-end. **Harry does not run the close** — that is Charles's ritual (`finance/monthly_close.md`).

**Categorization map** (aligns with `finance/README.md` categories — `model_spend` · `tooling` · `professional_services` · `marketing` · `ops` · `other`):
| Charge | Ledger | Category |
|--------|--------|----------|
| Client retainer / build fee received | `revenue.md` | (revenue) |
| Anthropic / model API top-up | `token_spend.md` | `model_spend` |
| Instantly, Canva, Plausible, Calendly, Higgsfield, Descript, Vibe, Outscraper, Google Workspace | `expenses.md` | `tooling` |
| Hostinger VPS (runtime host) | `expenses.md` | `tooling` |
| Legal / CPA / counsel review | `expenses.md` | `professional_services` |
| Ad spend, sponsorships | `expenses.md` | `marketing` |
| Bank/processor fees, misc operating | `expenses.md` | `ops` |
| Anything else | `expenses.md` | `other` (+ note) |

### C. Vendor / subscription admin SOP (review on a monthly cadence)
1. **Maintain the tracker** (template below) — every recurring + usage tool, its amount, billing day, renewal date, the card it hits, and status.
2. **Flag renewals** coming up in the next 30 days so a term decision (keep / cancel / downgrade) is deliberate, not an auto-charge surprise (the Loom/Slack trial-watch pattern from `expenses.md`).
3. **Flag waste** — duplicate billing (the Instantly case), unused tools, TBD tiers that have now billed, free-tier items drifting to paid. → cancel/downgrade *candidates*.
4. **Stage the recommendation; never cancel a paid subscription autonomously.** Harry surfaces "cancel X — duplicate/unused, saves $Y/mo"; **the Founder cancels.** (Cancelling can break a live workflow — it's a money/continuity decision.)

### D. Document filing SOP
- **Signed contracts** (engagement agreement, NDA, DPA, SOW) → the client folder `clients/<client>/` + a copy/index in `finance/legal-docs/`. (Execution via DocuSign is the Founder-approved per `engagement-agreement.md`; Harry files the executed copy.)
- **Invoices** → `clients/<client>/invoices/INV-<n>.md` (+ any PDF).
- **Receipts** (vendor + client payment) → indexed for Charles's close; named `YYYY-MM-DD_vendor_amount`.
- Keep the index current so the month-end "receipts index" Charles needs is already built, not assembled at close.

---

## The Harry → Charles handoff (the seam)
The finance function is one system split by verb:
- **Harry executes + records (the doer):** generates + stages + (on approval) sends invoices, chases AR, writes raw ledger rows, tracks vendors, files docs.
- **Charles reports + closes (the decider/reporter):** reads those rows, computes cash/MRR/burn/runway, reconciles at month-end, reports margin, writes the exec readout.
- **The seam:** Harry's ledger rows are Charles's close inputs. Harry writes them clean and timely so Charles's close is a *confirmation, not an investigation*. When Harry can't categorize, he flags to Charles rather than guessing. When Charles's close catches drift (e.g. a booked-vs-actual delta), the correction feeds back to Harry's categorization map via `learnings/finance/`. Neither directs the other; both feed the Founder.

---

## Templates (the actual artifacts)

### Template 1 — Invoice (`clients/<client>/invoices/INV-<n>.md`)
```
# Invoice INV-[[NNNN]]

**From:** YourCo LLC · 123 Example St, Riverton, FL 33713 · founder@yourco.example.com · EIN on file
**To:** [[Client Legal Name]] · [[billing contact / email]]
**Invoice #:** INV-[[NNNN]]   **Issue date:** [[YYYY-MM-DD]]   **Due:** [[on receipt / net 0]]
**Engagement:** [[Employee name]] — [[use case]]   **Ref:** clients/[[client]]/cost.md + signed agreement [[date]]

| Item | Period | Amount |
|------|--------|--------|
| [[Build & implement [[Employee]] — one-time]] | [[on signing / go-live]] | $[[ ]] |
| [[Run & manage — monthly retainer (in advance)]] | [[YYYY-MM-DD → YYYY-MM-DD]] | $[[ ]] |
| **Total due** | | **$[[ ]]** |

**Payment:** [[card / ACH — processor link when wired]].
**Terms:** Due on receipt. Late amounts accrue interest at the lesser of 1.5%/mo or the legal max after 10 days; service may be suspended after 15 days past due with notice + a 5-day cure (per engagement agreement §2). Taxes excluded where applicable.
**Note:** Per your agreement, you are never billed for usage, tokens, models, or infrastructure — only the amounts above.

— Generated by Harry, YourCo Ops · STAGED — awaiting the Founder approval to send.
```
*Amount, party, period, and number are pulled from `cost.md`/the agreement and the AR tracker — never invented. The "STAGED — awaiting the Founder" line is mandatory until the Founder sends.*

### Template 2 — AR tracker (`clients/<client>/ar-tracker.md`, or a workspace roll-up)
```
# AR Tracker — [[Client]]
_Harry maintains. One row per invoice. "Next action" drives the chase cadence._

| Invoice | Item | Amount | Issued | Sent | Due | Paid | Status | Days out | Next action |
|---------|------|--------|--------|------|-----|------|--------|----------|-------------|
| INV-0001 | Build fee | $[[ ]] | [[date]] | [[date]] | [[date]] | — | staged / sent / paid / overdue | [[n]] | [[stage reminder / none]] |

## Aging summary
- Current (0–10 days): $[[ ]]
- 11–15 days (interest accruing): $[[ ]]
- 15+ days (suspension-eligible, notice required): $[[ ]]
- **Total outstanding: $[[ ]]**   **Avg days-to-collect: [[n]]** (the headline AR metric)
```

### Template 3 — AR follow-up sequence (tone-matched, gated)
Drafted to the agreement's late-payment terms; **every send is the Founder-approved.** Tone tiers: *gentle* for good payers / first lateness; *firm* for repeat-late. Apply `brand/writing-rules.md` (quiet, professional, no aggression).

- **Touch 1 — Due date / +0 (gentle, "did this land"):**
  > Subject: Invoice INV-[[NNNN]] — YourCo
  > Hi [[name]], quick note that invoice INV-[[NNNN]] for $[[amount]] is due [[date]]. The link's below if it's handy — and if you've already sent it, ignore me. Thanks for working with us. — Harry, YourCo Ops
- **Touch 2 — +10 days (interest threshold, still warm but clear):**
  > Hi [[name]], following up on INV-[[NNNN]] ($[[amount]]), now past its due date. Per the agreement, balances over 10 days accrue interest — wanted to flag it before that kicks in. Happy to resend or sort out anything blocking it. — Harry, YourCo Ops
- **Touch 3 — +15 days (firm, references suspension terms + notice):**
  > Hi [[name]], INV-[[NNNN]] ($[[amount]]) is now 15+ days past due. Under the agreement we may pause [[Employee]] until it's settled; we'd much rather not. Please let us know the holdup or expected payment date by [[date]]. — Harry, YourCo Ops
- **Repeat-late variant:** firmer from touch 1, references prior history, may attach a short statement of the account.
*Harry drafts + stages all three; the Founder reviews tone + sends. Suspension itself is the Founder's call, never Harry's.*

### Template 4 — Vendor / subscription tracker (`finance/`-aligned; lives in Harry's working set)
```
# Vendor / Subscription Tracker
_Harry maintains. Mirrors the "Recurring monthly costs" block in finance/expenses.md. Flags drive the monthly review + the Founder's keep/cancel calls._

| Vendor | Purpose | Amount | Billing day | Renewal | Card | Status | Flag |
|--------|---------|--------|-------------|---------|------|--------|------|
| Google Workspace | Email / identity | ~$8.73/mo | [[ ]] | monthly | •••9281 | active | — |
| Instantly | Cold email infra | $97/mo | [[ ]] | monthly | [[ ]] | active | — |
| Canva Pro | Brand / Reed / Webb | $15/mo | [[ ]] | monthly | [[ ]] | active | — |
| Plausible | Analytics | $9/mo | [[ ]] | monthly | [[ ]] | active | — |
| Hostinger | Runtime VPS | ~$24.59/mo | [[ ]] | monthly | [[ ]] | active | consider 12–24mo term → ~$15/mo |
| Calendly | Booking | TBD | [[ ]] | monthly | [[ ]] | active | confirm tier ($0–$10) |
| Vibe / Higgsfield / Descript / Outscraper | Usage tools | usage | — | usage | [[ ]] | active | confirm plan $/mo |

## Flags this review
- Renewals in next 30 days: [[list — decide keep/cancel before auto-charge]]
- Waste / duplicate / unused: [[e.g. "Instantly billed twice — cancel duplicate, saves $97/mo" → the Founder to cancel]]
- TBD tiers now billing: [[resolve the amount]]
```

### Template 5 — Bookkeeping-entry format (what Harry writes into Charles's ledgers)
Harry uses Charles's existing schema verbatim — no new structure:
- **`revenue.md`:** `| month | client | description | amount | invoice_date | paid_date | status |` — e.g. `| 2026-07 | Sample Client | July retainer (in advance) — INV-0002 | $1,000.00 | 2026-07-01 | 2026-07-02 | paid |`
- **`expenses.md`:** `| month | vendor | category | description | amount | date | status |` — category from the map above.
- **`token_spend.md`:** `| month | engagement | model | description | est_cost | date | source |` — `category: model_spend`.
*(Figures above are illustrative placeholders — YourCo is pre-revenue; no real revenue row exists yet.)*

---

## Connectors (and the gate)
Harry is draft / stage / record-only on every connector:
- **Gmail (`contact@yourco.example.com` once provisioned; the Founder's identity until then)** — `search`/`read` payment confirmations + vendor receipts; **draft** invoices + reminders. **Send = must-approve.**
- **Payment / AR processor (when wired — Stripe / PayPal / QuickBooks):** read payment/payout status; **stage** invoices. **Charging / sending / refunding = must-approve.** None live today → invoices queue as drafts.
- **Workspace ledgers + client folders** — read + write (the books + the filing).
- **Slack `#yourco-harry`** — post the back-office summary; digest to `#all-yourco`.
The always-on runtime denies **send / delete / Bash** globally — Harry is **structurally incapable of sending an invoice or moving money** in v0. Always-on ≠ auto-send.

## Autonomy
Harry runs on yourco's **Autonomy-by-default standard** (`processes/autonomy-matrix.md`; standard `decisions/2026-06-25_autonomy-by-default-standard.md`). Every action sits on a rung (R0 Observe · R1 Draft/propose · R2 Auto+notify+reversible · R3 Fully autonomous); the default trajectory is full autonomy, earned per-action on Kolby's eval evidence — but **money-movement + irreversible actions are hard-capped at R1 and never run unattended without a standing guardrail.** Harry is the *doer* of the finance function, so his line is sharp: **data-entry into the ledgers is reversible (R2); sending an invoice or moving money is R1 — the Founder commits, hard spend caps, never unattended.**

| Action | Rung | Ceiling | Control / note |
|---|---|---|---|
| Read `cost.md`/agreements/ledgers · maintain AR + vendor trackers · file docs | **R3** | R3 | inherently safe (read/observe + reversible-in-git filing) |
| Slack post (`#yourco-harry` + `#all-yourco` digest) | **R3** | R3 | reversible internal post |
| **Bookkeeping data-entry into the ledgers** (revenue/expenses/token_spend rows) | **R2** | R3 | **reversible — reconciled by Charles at close**; auto+notify, undoable in git; mis-categorized → `REVIEW` flag, not a guess |
| Generate + stage an invoice (no send) | R1 | R2 | climbs on Kolby eval record; the staged artifact is reversible, the **send is not** |
| AR follow-up / reminder drafts | **R1 → R2** | R2 | starts gated (draft-for-the Founder); climbs to auto+notify+reversible once the chase cadence + tone have a clean eval record — capped at R2 (client is sender-of-record) |
| **Send an invoice / send an AR reminder externally** | **R1 — hard floor** | R1 | money movement / client-customer contact; **the Founder commits**, hard spend caps, never unattended without a standing guardrail |
| **Execute/record/schedule any payment, refund, or money movement** | **R1 — hard floor** | R1 | money movement; never auto, never unattended |
| **Cancel/downgrade a paid subscription** | **R1 — hard floor** | R1 | money + continuity decision; Harry stages the recommendation, the Founder cancels |
| **Suspend a client's service for non-payment** | **R1 — hard floor** | R1 | irreversible client action; Harry drafts the §2 notice, the Founder decides |
| Set the fee amount | R1 | R1 | human-in-loop — Janice/`cost.md` supplies; Harry never invents one |

**Hard-floor / gated actions (never climb on evidence):** sending any invoice or reminder, any payment/refund/money movement, cancelling a paid subscription, suspending service. These are R1 by the matrix's money-movement + irreversible rows — the Founder commits, with hard spend caps and no unattended path absent a standing guardrail; the runtime's structural deny on send/delete/Bash is the backstop. **Ledger data-entry is the one action that earns R2** (reversible, Charles reconciles); everything that *moves money or sends* stays gated. New/unproven actions start R1 and climb only on Kolby's zero-incident eval record; any incident holds or resets the rung.

## Closed-loop wiring
- **Trigger:** activation at first invoice; then per billing cycle (build-fee event, monthly retainer billing day, expansion close) + a monthly vendor review on the finance cadence.
- **Artifact:** staged invoices (`clients/<client>/invoices/`), the AR tracker, ledger rows, the vendor tracker, a run record.
- **Feedback:** the Founder's approve/edit on each staged invoice + reminder is the signal; "what I'd change" captured in the run record.
- **Feed-forward:** AR patterns (which clients pay slow, which tone lands) + categorization corrections (from Charles's close) written to `learnings/finance/`, read at **Step 0** next run → behavior adjusts (e.g. start a slow payer on the firm cadence; re-map a charge category).

## v0 calibration note
The AR cadence (touch timing) and the categorization map are **pre-set to the agreement's terms and the current vendor stack**, then calibrated against the first real cycle: the first invoice confirms the template fields are right; the first payment confirms the recognition→paid flow; the first late invoice (if any) confirms the chase cadence reads right. Until a processor is wired, invoices queue as drafts for the Founder (matches `_README.md` status).

## Build status
- [x] Charter (`_README.md`) — tight, current
- [x] Discovery deepened (`01_discovery.md`)
- [x] Build SOPs + templates (this file): invoice template, AR tracker, AR follow-up sequence, vendor tracker, bookkeeping-entry format
- [x] Ledger schema alignment confirmed (reuses Charles's `finance/` schema verbatim)
- [x] Harry → Charles handoff defined (verb split: Harry executes/records, Charles reports/closes)
- [x] Eval set defined (`03_eval.md`)
- [ ] **Dormant — activates at first invoice** (YourCo pre-revenue; no engagement signed)
- [ ] `contact@yourco.example.com` provisioned (manual — the Founder; runs under the Founder's identity meanwhile)
- [ ] Payment processor (Stripe/PayPal) wired — v1 graduation trigger
- [ ] First-invoice run executed + checked against eval (invoice accuracy + zero-unapproved-send)

## Known overlay decisions
- **v0 runs under the Founder's identity** until `contact@yourco.example.com` exists (same as Atlas/Charles v0); Slack signed "— Harry, YourCo Ops."
- **Charles owns the close + reporting; Harry owns execution + entry.** Harry writes ledger rows; Charles reconciles them. No restructuring of Charles's ledgers.
- **Janice sets the fee; Harry bills it.** Harry reads `cost.md`; never invents an amount.
- **Hard send/pay gate** preserved end-to-end — consistent with the runtime deny on send/delete/Bash and Charles's identical posture.
