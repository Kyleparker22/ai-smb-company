# Sample Client — discovery (Client Owner's spec)

> Source: Client Owner's flowchart "Installation Proposal Automation" (2026-06-05) + the meeting. Original: `attachments/Client Owner Flowchart — Installation Proposal Automation (2026-06-05).pdf`.

## The job to automate
When an **Installation** proposal is signed in Aspire, a lot of early-stage coordination kicks off by hand — deposit request to the client, material orders to suppliers, scope notices to subcontractors, then chasing all of it until the job is greenlit. Client Owner wants a digital employee to run that, with a human approving anything that leaves the building.

## Trigger + filter
- **Trigger:** Aspire webhook, `status = Signed`.
- **Filter:** Installation only — `division = "Installation"` in the line items. Maintenance / mowing / cleanups are ignored (STOP).

## What the employee does on a signed installation proposal
1. **Parse the proposal** (Claude): client, total, materials, SUBs.
2. **Check Google Calendar:** pull the project window + dates.
3. **Split into three branches** — client, suppliers, subcontractors:

**Client (deposit)**
- Apply tier logic to the total (≤$10K / mid / $150K+) → correct deposit ask.
- Draft the deposit email **+ SMS**.
- **Charlene approves** the draft.
- On approval, email + SMS sent to the client simultaneously. Deposit due via Zelle / check / card.

**Suppliers (materials)**
- Categorize materials by type + quantity.
- Route delivery: **shop** (small / packaged) vs **job site** (bulk / pallets).
- Draft one supplier order email each (qty + address + needed-by date).
- **Client Owner approves** the supplier drafts.
- Sent; replies tracked; summary back to Client Owner.

**Subcontractors**
- Detect SUB items (`cost_category = SUB`).
- Draft a sub email per sub (scope + calendar start-window).
- **Client Owner approves** the sub draft.
- Sub notified for job approval + dates; sub confirms availability + rate.

4. **Project greenlit** when deposit + materials + sub are all confirmed → **all-clear** ("greenlit — all systems go") email to Charlene + Client Owner. Anything stuck too long gets flagged daily.

## The actors (approval roles)
- **Charlene** — approves client-facing messages (deposit email/SMS).
- **Client Owner** — approves supplier + sub messages; gets the summaries.
- **Noah** — estimating (relevant to use case 2, the instant-range concept).

## Non-negotiables (set expectations early)
- Nothing reaches a client, supplier, or sub without a human approval (one tap from the phone).
- Every dollar amount is computed by tested code, never by AI.
- Duplicate-proof: one signed proposal can never double-send a deposit.
- Ships with a test suite that proves it works before it touches a real customer.

## Related
- The build plan + stack: `03_setup-plan-and-tech.md`.
- A second, larger opportunity surfaced in the meeting: hardscape instant-range quoting → `04_instant-range-concept.md`.
