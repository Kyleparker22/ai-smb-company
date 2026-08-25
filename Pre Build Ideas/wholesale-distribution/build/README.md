# Quote Desk OS — build 8 of 10

Pre-built vertical AI OS for wholesale distributors and job shops.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py                      # 44 SKUs, 12 customers, 4,681 RFQs + outcomes
python3 test_quote_desk.py           # 80 assertions, every one a refusal
```

Launch name **`prebuild-quote-desk-os`** (port 8828, 127.0.0.1 only).

## What it is

"Halstead Industrial Supply" — $18M, five inside-sales, an 18% margin floor. Four modules: **RFQ
parser**, **quote builder**, **PO ingestion**, **quote follow-up** — plus the desk board and the
margin ledger.

## Three prohibitions

**A low-confidence line never enters a quote.** Four match signals in order of trustworthiness: the
customer's own cross-reference, an exact SKU, their purchase history, description overlap. The last
is **never enough on its own** — a loose word match is capped *below* the threshold on purpose. Two
real bugs here, both caught by tests:

1. The matcher violated its own docstring — a one-word line ("valve") matched a specific SKU at 0.77
   confidence because the customer had bought it once. That is the wrong part, confidently.
2. The purchase-history boost was breaking a **size tie**. "brass ball valve threaded" resolved to a
   specific diameter because they'd bought it before. Ambiguity is now judged on the *base* overlap,
   before any history boost: two sizes of the same part are ambiguous whatever they bought last time.

**A substitution is never silent.** A discontinued part produces a *proposal* with every spec
difference named (spec, material, rating, UOM), sitting at R1 and never promoting. A discontinued
part with no successor on file proposes nothing and goes to a human.

**A discrepant PO never becomes an order.** Seven discrepancy types (price, quantity, sku, ship-to,
terms, date, uom), and **any one of them holds the whole order** — a partially-correct order shipped
is worse than one that waited ten minutes. `write_discrepant_order` is R0.

Plus: **one customer's agreement can never price another.** `price_line()` reads pricing from the
passed customer's record only — there is no argument that could cross the boundary — and
`cross_customer_price` is declared R0 so the prohibition is readable.

## The line that stays blank on purpose

The ROI panel's **win-rate lift from faster quoting** cannot be filled in from config, from a
default, or from an industry statistic. It renders `needs win_rate_lift_evidence` with the note
*"WE WILL NOT PUT A NUMBER HERE FROM AN INDUSTRY STATISTIC… about 90 days of recorded outcomes."*
The margin ledger is what eventually answers it — on the seeded year, 4,680 decided quotes bucketed
by discount depth, turnaround and product family, with thin buckets blank rather than computed.

## 10-minute demo

1. **The desk** — today's RFQs, human queue, margin approvals, median turnaround, PO exceptions.
2. **Parse an RFQ** — the messy demo PDF: their part number, a discontinued part, "misc hardware as
   discussed", a real line, "part per drawing". Quote it: **3 priced, 2 queued, 1 substitution**.
   Read the queued reasons — *"nothing in the catalog matched"* and *"two catalog items score almost
   the same (SKU-1041 and SKU-1042) — a human picks, we do not guess"*.
3. The substitution proposal with four named spec differences, waiting at R1.
4. **Purchase orders** — PO-44817 held as an exception (line 4 quantity 500 vs 50 quoted);
   PO-44818 reconciles and writes an order.
5. **Margin ledger** — win rate by discount depth and by turnaround, from recorded outcomes.
6. **What it's worth** — and the line that refuses to fill itself in.

## What this does not do yet

- **No integrations.** Epicor/NetSuite/SAP B1, email, EDI and the cost-file feed are adapter seams.
- **Parsing is text and structured rows**, not PDF or image OCR. The "photo" source is modelled as
  transcribed text; a real deployment reads the document.
- **No inventory, no availability, no lead-time promising.** Lead days are on the catalog and unused.
- **No freight, tax or terms calculation.**
- **Nothing is sent.** Every quote waits at the gate.
