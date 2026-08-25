# 01 — Entity, EIN, and money

> **Build step 01.** Nothing here is done yet. Where this page shows a filled-in value, that is
> the source company's — replace it with yours.

> ⚠️ **A record, not advice.** This is what one Florida LLC actually did. Your state, your partners,
> and your tax situation change the answer. Get counsel before you file anything.

## Your entity — fill this in as you go

**This is your company, not a copy of anyone else's.** Nothing below is done yet. Record each value in
`finance/legal-docs/business-info.md` as you obtain it; every vendor in later steps asks for one of them.

| Thing | Your value | Where it gets recorded |
|---|---|---|
| Operating legal name (banking, W-9s, 10DLC) | ☐ | `finance/legal-docs/business-info.md` |
| State-filed legal name, if different | ☐ | same |
| Trade / brand name | ☐ | `brand/` |
| Entity type | ☐ | business-info |
| State of formation | ☐ | business-info |
| Date of formation | ☐ | business-info |
| EIN | ☐ | keep the CP-575 letter — the IRS will not reissue it |
| Registered agent | ☐ | business-info |
| Business bank account | ☐ | opened after the EIN |
| Operating agreement | ☐ | `finance/legal-docs/operating-agreement-DRAFT.md` |
| Insurance | ☐ | `finance/legal-docs/insurance-plan.md` |

The placeholder name throughout this repo is **`YourCo`** in every casing — `YourCo`, `yourco`,
`YOURCO`, plus `yourco.example.com` and `YOURCO LLC`. Replace all of it in one pass per
`RENAME-THIS-FIRST.md`, ideally before you write anything new on top.

## The name mismatch — why it was left alone

Florida has the entity as **YourCo LLC**; the IRS CP-575G says **YOURCO LLC**. the Founder decided
on 2026-06-08 **not to correct either record**, because the mismatch is non-blocking in practice: use
the IRS name for banking, tax, and 10DLC, and the state name only where a state filing demands it.

The fix, if a vendor ever balks: FL Articles of Amendment (~$25, ~1 week) to drop "Ventures", **or** an
IRS name-correction letter. Both are cheap; neither was worth doing pre-revenue. **This is the pattern
to notice** — a known imperfection, decided deliberately, written down with its remedy and its trigger,
rather than either fixed reflexively or forgotten.

## Order of operations, and why

1. **Entity first.** Nothing else can be opened in the company's name. Florida was chosen because it
   is where the founder is — no foreign-qualification fee, no out-of-state registered agent.
2. **EIN second**, directly from the IRS, free. It is the key every vendor asks for. It cannot be
   applied for until the entity exists.
3. **Bank account third.** Needs the EIN and the formation document. Everything downstream — Stripe,
   the VPS, the model bills — needs a business account, and mixing personal and business money in a
   single-member LLC is the thing that undermines the liability shield.
4. **Everything else.** Domain, tooling, vendors. All of it asks for one of the three above.

## The actual filing steps — what yourco did, in order

> **Fees and deadlines below were verified at source on 2026-08-25** against
> [Florida's Division of Corporations](https://dos.fl.gov/sunbiz/start-business/efile/fl-llc/).
> **They change.** Re-check before you file rather than trusting this page — a stale fee is a rejected
> filing. Still a record, still not advice: this is the sequence one company followed.

### Step 1 — Decide the state, and the registered agent

Florida, because that is where the founder is. Forming out-of-state (Delaware being the usual
temptation) means you *also* foreign-qualify in your home state — two filings, two fees, two annual
obligations — and it buys nothing unless you are raising institutional money.

A **registered agent** is a real address in the state that accepts legal service during business
hours. It can be you if you are comfortable with your address being public record and you are
reliably there. A commercial agent runs roughly $50–300/yr and keeps your address off the filing.

### Step 2 — File the Articles of Organization

Online at [sunbiz.org](https://dos.fl.gov/sunbiz/start-business/efile/fl-llc/), card or prepaid
account. Mail with a check is possible and slower.

| Line item | Fee | Required? |
|---|---|---|
| Articles of Organization | **$100.00** | yes |
| Registered Agent Designation | **$25.00** | yes |
| **Mandatory minimum** | **$125.00** | — |
| Certified Copy | $30.00 | optional |
| Certificate of Status | $5.00 | optional |

Filings are processed in the order received; confirmation arrives by email for online filings.
**yourco's filing was effective 22 April 2026.**

⚠️ **The optional two are usually worth $35.** A bank or a vendor occasionally asks for a certified
copy or a certificate of status, and ordering them later is slower and more annoying than checking
two boxes now.

⚠️ **This is where yourco's name mismatch was created.** The state record reads *YourCo LLC*
and the IRS letter reads *YOURCO LLC*. Whatever name you type here is what the state has forever
unless you amend. **Type the name you intend to bank under.**

### Step 3 — Get the EIN, free, directly from the IRS

**[irs.gov](https://www.irs.gov/businesses/small-businesses-self-employed/apply-for-an-employer-identification-number-ein-online)
— it is free and takes about ten minutes.** Do not pay a service for this; the paid EIN services are
reselling a free government form.

You cannot apply until the entity exists, and every vendor downstream asks for it.
yourco's letter is `finance/legal-docs/IRS_CP575G_EIN_letter.pdf`. **Keep the CP-575 letter** — it is
the document banks and payment processors ask to see, and the IRS will not reissue it (they issue a
147C confirmation instead, which is a slower conversation).

### Step 4 — Open the business bank account

Needs the EIN letter and the formation document, and sometimes the certified copy from step 2.

**Do this before spending a dollar on the business.** In a single-member LLC, mixing personal and
business money is the specific behaviour that undermines the liability shield you just paid $125 for.
Every vendor below — the VPS, the model bills, the domain — should be paid from this account from day
one, because reconstructing the split later is worse than doing it now.

### Step 5 — The operating agreement

Florida does not require one. **Write one anyway**, and if there is ever more than one member, have
counsel write it. yourco's is `finance/legal-docs/operating-agreement-DRAFT.md` — **v5, still
unsigned**, with open blocks. See the partner section below for what happens when this is treated as
a formality and then suddenly is not.

### ⏰ Step 6 — The recurring obligation nobody sets a reminder for

**The Florida annual report is due between 1 January and 1 May, every year, at $138.75.**

**Miss 1 May and there is an automatic, non-negotiable $400 penalty** — $538.75 total. It is not
discretionary and it is not appealable.

**An LLC formed at any point in 2026 files its first annual report between 1 January and 1 May 2027.**
So for yourco, formed 22 April 2026: **the first annual report is due by 1 May 2027.**

**This is now watched.** A consistency invariant (added the same day this page was written) stays
silent until 1 January 2027, then warns every run with the days remaining until a filing is recorded —
and switches to *past due* language after 1 May. To silence it, file at sunbiz.org and note it in
`finance/legal-docs/business-info.md` (a line containing "annual report", the year, and "filed"), or
drop the receipt at `finance/legal-docs/annual-report-<year>.pdf`. **It records nothing and files
nothing** — filing is the Founder's; the check only refuses to let the date pass unnoticed.

## The partner change, and what it did to all of this

The company was formed **single-member**. On **2026-08-10** the Founder admitted two partners —
**the Founder 50 / Partner B 35 / Mike 15** — which turned a simple single-member LLC into a three-member entity
and made the operating agreement load-bearing rather than a formality.

**Consequences you should understand before copying this shape:**
- **the Founder has no control at 50%.** That is a real governance fact, not a rounding error.
- The OA is **v5 and unsigned**, with open blocks. Its own gap list includes **#8 "the undefined
  lane"** — *"substantially full time" against no written duties means Service Failure never fires* —
  whose fix is Schedule C-1 lane definitions that are still unanswered.
- The whole instrument sits behind **counsel gate #14** (`processes/counsel-gates.md`).
- ⚠️ This is why the role coach (`crm/coach.py`) **refuses to train partners**: writing partner duties
  would author Schedule C-1 by the back door, without counsel. See `06_THE-AGENTS.md`.

**Read `finance/legal-docs/counsel-review-TEMPLATE.md` before touching the OA.** It is the review
that produced the open-issue list.

## Money in, money out

- **Revenue: $0.** Sample Client is at Proposal, unsigned. Nothing has been billed.
- **Spend** is tracked two ways and both matter: `finance/token_spend.md` for model cost (the business
  model is that yourco absorbs it and the client never sees a token), and `clients/<client>/cost.md`
  per engagement via the `log-build-cost` skill.
- **The reconciliation is automated and it fires.** A consistency invariant compares metered
  Anthropic spend against what the ledger explains and warns on the gap — as of 2026-08-25 it reads
  *"$X metered, $Y explained → $Z unaccounted."* That warning is the system working.
- **Payments infrastructure**: `processes/payments.md`.
- **The financial model** (5-year, assumption-stated, explicitly *not* a forecast):
  `finance/yourco-financial-model.xlsx`, with the narrative in `06_business-plan.md`.

## What is deliberately NOT here

No account numbers, no EIN digits, no banking credentials, no card details. They live in
`finance/legal-docs/` and a password manager. **A setup guide that contained them would be the single
worst file in the repo** — it is the one document guaranteed to be copied, shared, and pasted.

## Done when

**a filed entity, an EIN letter saved in `finance/legal-docs/`, and a business bank account you can pay a vendor from.**

If you cannot point at that, the step is not finished — do not move on.
