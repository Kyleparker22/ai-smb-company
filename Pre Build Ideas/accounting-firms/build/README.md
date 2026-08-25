# Close OS — build 5 of 10

Pre-built vertical AI OS for CPA, bookkeeping and tax firms.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py                      # 230 clients, 367 engagements, 2,776 open items
python3 test_close_os.py             # 52 assertions, every one a refusal
```

Launch name **`prebuild-close-os`** (port 8825, 127.0.0.1 only).

## What it is

"Callender Iyer Raghavan" — 14 people, three partners, both rhythms (the monthly close book and the
season spike). Three engines: **the chaser**, **the intake classifier**, **the scope ledger** — plus
the partner board.

## The structural refusal

**An engagement may not sit in a vague "in progress".** `advance()` raises if you try to move an
engagement into a live state without naming its blocker, and `"in progress"` is not in `STATES` at
all. The partner board's entire value is that every row answers *who is holding this up*; one
unnamed blocker turns it back into a to-do list. On the seeded firm, all 330 live engagements name
one — median blocker age 12 days, worst 45.

## The chase, and what it refuses to chase

- **Never chases something already received.**
- **Never chases a dependent item whose dependency isn't met** — an 8879 isn't chased before a draft
  return exists, and a draft return isn't chased while client items are outstanding. A chase for
  something the client cannot produce is how a chaser becomes the thing everybody mutes.
- **One ladder step per item per run.** Firing every overdue step at once would send a client five
  messages in a minute the first time this is pointed at a neglected backlog. (It did, before it was
  fixed.)
- **The ladder ends at a partner task**, not a fifth email.
- Nudges list only what is still open, and never repeat an item twice in one message.

## Documents: a mismatch is flagged, never filed

Wrong year, wrong entity, and "a 1099 arrived but nothing open asked for one" are all **flagged**
with the reason. Unreadable filenames (`IMG_4471.jpg`, `scan.pdf`) go to a human queue below the
confidence threshold rather than into a client's folder. The eval measures exactly one thing — the
false-match rate — because a document filed to the wrong entity is worse than one not filed at all.
**Nothing is ever deleted**: `delete_document` is declared R0 / never-promote, and a correction is a
new event with both states in the log.

## The scope ledger, and the ambiguity it refuses to resolve

A scope event **cannot exist without a citation** to the engagement letter's own language. Three
ways it declines to log one:

1. **No clause speaks to it** → a partner decides, the system does not assert.
2. **The letter covers it** → not scope creep.
3. **The clause speaks both ways** → *"Routine questions arising from the work above are included.
   Planning and advisory engagements are separate."* A keyword match cannot tell which side "can I
   deduct the truck" lands on, so it surfaces the ambiguity instead of resolving it. This was a real
   bug: the build was confidently logging billable scope creep off a clause that arguably covered
   the question.

## Numbers

- **Chase time is counted per MESSAGE, not per item** — bundling eleven open items into one message
  *is* most of the saving, so counting per item double-counts it. (Per-item read $467k/yr of staff
  time at a 14-person firm; per-message reads $16k.)
- **Weekly volumes are counted over the last seven days**, not derived by dividing a standing
  backlog by four.
- **Cycle time is labelled CASH CONVERSION, NOT REVENUE on its face** and subtotalled separately.
- **Recovered scope is the honest headline** and stays blank until the ledger has events.

## 10-minute demo

1. **Partner board** — 330 live engagements, every one naming its blocker, sorted by what blows a
   deadline first; 119 blocked *on us*, which is the half most dashboards hide.
2. **The chase** — messages in flight, the escalations, and the held-back list with reasons.
3. **Documents** — filed / flagged / human-queue, and per document what it read and why it acted.
4. **Scope ledger** — paste *"We just formed a new LLC for the rental, and can I deduct the truck?"*
   Watch it route the tax question unanswered, log the new entity against the bookkeeping clause,
   and **decline** to call the deductibility question scope creep because the clause is two-sided.
5. **What it's worth** — four lines, three kinds, never summed.
6. **Trust & audit** — `answer_tax_question` and `delete_document` at R0, the eval, the log.

## What this does not do yet

- **No integrations.** Karbon/Canopy/TaxDome, QBO/Xero, email and the document store are adapter
  seams.
- **Matching is filename + metadata**, not document content. A real deployment reads inside the PDF.
- **No tax software, no preparation, no review.** This build moves the *work around* the return.
- **§7216 posture is stated, not implemented.** Live deployment needs counsel review of taxpayer
  information handling; the prototype uses synthetic records.
- **Nothing is sent.**
