# Contract — [[CLIENT NAME]]

> **The executed-contract register for this engagement.** `processes/contracts/` holds the
> *templates*; this file records what this client actually signed. Created 2026-08-07 —
> before it existed, nothing anywhere captured a signature date, a term, or a renewal
> deadline, and the Clients view had no contract status to read.
>
> **Why this file and not a folder of PDFs:** the Engagement Agreement §3 **auto-renews
> monthly unless either party gives 30 days' written notice**, and §2 gives YourCo the right
> to suspend an account **15 days past due** after written notice and a 5-day cure. Both are
> date-driven rights you can only exercise if the dates are written down. At 15 clients that
> is 15 rolling notice windows. **A renewal date not captured at signature is captured never.**
>
> Fill this the day the envelope completes — not later. Countersigned PDFs go in
> `attachments/`; this table is the machine-readable index over them.
> Owner: **Ray** (accuracy of terms) · **the Founder** (signs) · **Janice** (fills at onboarding).

## The register

| Field | Value |
|---|---|
| Status | [[draft-sent / partially-signed / **executed** / terminated]] |
| Agreement | [[Engagement Agreement / MSA + SOW]] · version [[processes/contracts/engagement-agreement.md @ commit]] |
| Signed | [[YYYY-MM-DD]] · by [[client signatory, title]] |
| Effective | [[YYYY-MM-DD]] |
| Initial term | [[month-to-month / 3 months]] from go-live |
| Renews | [[auto-monthly / auto-annual / does not auto-renew]] |
| Notice required | [[30]] days' written notice |
| Notice deadline | [[YYYY-MM-DD — the LAST day to give notice before the next auto-renew; recompute each renewal]] |
| Build fee | [[$X one-time, due on signing]] |
| Retainer | [[$X/mo]] · [[net 0 / on receipt]] · [[ACH / card]] |
| DPA | [[not required / signed YYYY-MM-DD / pending]] |
| BAA | [[not required / signed YYYY-MM-DD / pending]] |
| Mutual NDA | [[signed YYYY-MM-DD / superseded by the Agreement]] |
| Counsel-reviewed | [[no — counsel gate #1 open / yes, by <firm> on YYYY-MM-DD]] |
| DocuSign envelope | [[envelope id — the connected DocuSign account is the source for status]] |
| Countersigned PDF | [[attachments/<file>.pdf]] |

## Deviations from the standard template
> Anything negotiated away from `processes/contracts/engagement-agreement.md`. If nothing was
> changed, write "none" — an empty section is ambiguous, "none" is a fact.

- [[none]]

## Renewal / notice log
> One line per renewal or notice event. Append-only.

| Date | Event | Next notice deadline | Note |
|---|---|---|---|
| [[YYYY-MM-DD]] | [[executed / auto-renewed / notice given / terminated]] | [[YYYY-MM-DD]] | |

## Payment standing
> Charles updates at monthly close. §2: >10 days late accrues interest; >15 days past due
> permits suspension after written notice + 5-day cure.

| As of | Invoiced | Paid | Days past due | Action taken |
|---|---|---|---|---|
| [[YYYY-MM-DD]] | | | | |
