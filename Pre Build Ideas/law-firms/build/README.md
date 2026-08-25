# Case OS — build 6 of 10

Pre-built vertical AI OS for plaintiff-side law firms (PI primary).
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py                      # 310 matters, 607 records requests, 935 leads
python3 test_case_os.py              # 70 assertions, every one a refusal
```

Launch name **`prebuild-case-os`** (port 8826, 127.0.0.1 only).

## What it is

"Sandoval Boateng Injury Law" — six attorneys, four paralegals, 310 matters, eight invented medical
facilities each with its own records quirks. Four modules: **24/7 intake**, **the records engine**,
**demand assembly**, **client status** — plus the docket board.

## The UPL rule, applied

`legal_advice` is declared **R0 / never promotes**. "Do I have a case?", "what's my case worth",
"should I settle", "whose fault is it", "what are my chances" — all routed to a licensed attorney
**unanswered**, and the reply says what it refused to do. Eval: recall on legal questions reported
alone, 1.0, zero missed. Sending the fee agreement and drafting a demand also never leave the gate.

**R0 is not a slow yes.** A refusal never becomes a row with an Approve button next to it — that
would tell a buyer a human can click past the prohibition. This was a real flaw found while
verifying: `legal_advice` was appearing in the approval queue. Fixed in the shared kit, so all six
builds inherit it, and every suite now pins it.

## The conflict check runs first

Before any substantive conversation, against current clients and open matters. A hit stops
everything — **no facts are taken and no advice is given**. It works well enough that it caught the
seeded demo leads whose names collided with randomly generated opposing parties, which is why the
demo leads now carry names outside the generator's pools.

## Screening refuses to guess

The screener reads the firm's **own written criteria** and nothing else. A lead with no incident
date cannot be evaluated on the statute, so the whole screen returns `human_review` with the
unevaluable criterion named — it does not assume, and it does not decline. Every decline records
its reason, so the firm can audit its own screening later; the cases you turned away are the half
nobody measures. Statute proximity calls itself a **DATE ALERT, not legal advice**, in the string a
user actually sees.

## A PDF arriving is not a file being whole

`verify_production()` compares what arrived against what was requested: late start dates, early end
dates, missing billing, no stated date range, illegible pages, wrong patient (critical). An agent
**cannot** mark a production complete with a gap outstanding. The eval measures the
false-"complete" rate alone, because that error produces a demand built on a partial file.

## A fact without a citation is omitted

`build_chronology()` writes only entries carrying an exhibit and page. Anything else is listed as
**unsupported** and left out — never written anyway. The billed total sums only what can be pointed
to, the header reads `[FOR ATTORNEY REVIEW]`, and if the file is incomplete the draft says so above
the fold.

## Numbers

- **Average case fee is the firm's own**, and the line says on its face that a published settlement
  statistic will not be borrowed — contingency outcomes are wide and lumpy.
- **Records cycle time is cash timing, not revenue.** A faster file resolves sooner; it does not
  make the case worth more.
- **Screening quality is a SCENARIO** — you cannot count cases you did not take. The recorded
  decline reasons are the evidence, not the number.
- **Completeness is unknown, not 0%**, for matters with no records requests: 120 of 294 on the
  seeded docket.

## 10-minute demo

1. **The docket** — 294 open, 22 with the statute inside 90 days, six with no contact ever recorded.
2. **Intake** — take the conflicted call: stopped before a single fact is taken. Then the
   "what's my case worth" call: routed, no number given. Then the one with no incident date:
   human review, criterion named. Then the out-of-state one: declined with a recorded reason. Then
   the 11:40pm rear-ender: qualifies, retainer held at R1.
3. **Records** — 261 open, median age 56 days, and the incomplete productions with their specific
   gaps.
4. **Demand** — pick a matter at 66% complete: the warning above the fold, the cited chronology, the
   omitted entries, and a billed total that counts only what can be cited.
5. **Trust & audit** — `legal_advice` at R0 with no approve button, both evals, the log.

## What this does not do yet

- **No integrations.** Filevine/Litify/Clio, e-signature, telephony and records-retrieval vendors are
  adapter seams. No fax.
- **Productions are metadata, not documents.** A real deployment reads inside the PDF.
- **No litigation, no discovery, no calendaring rules.** Statute proximity is arithmetic on a stored
  date and explicitly not a tolling analysis.
- **No PHI infrastructure.** Records are PHI; live deployment needs counsel review.
- **Nothing is sent.**
