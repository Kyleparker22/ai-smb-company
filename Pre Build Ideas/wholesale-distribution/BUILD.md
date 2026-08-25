# 8 · Wholesale Distribution & Job-Shop Manufacturing — **Quote Desk OS**

*Pre-build. Not built, not sold, no client. See `../_README.md` for the shared build contract.*

## 1. The idea in one paragraph

A distributor or job shop wins on two clocks. The first is **quote turnaround**: an RFQ arrives as an email with a PDF, a spreadsheet, or a photo of a parts list; someone has to decode it, find each item in the catalog, check what this customer paid last time, check the current cost, and build a quote — and while that takes two days, a competitor answers in four hours and takes the order. The second is **order entry**: the PO comes back as another PDF and gets keyed into the ERP by hand, which is where the wrong quantity, the wrong ship-to, and the discontinued part number get in. **Quote Desk OS** automates both — RFQ parsing to line-matched draft quote with margin guardrails, and PO ingestion to ERP order with an exception queue — and then adds the thing nobody does: a quote follow-up and **win/loss margin ledger** that tells the owner which discounts actually bought business.

## 2. Who buys it

The **owner or GM** of a $5M–$60M distributor, custom fabricator, or job shop — industrial supply, electrical/plumbing supply, packaging, machining, sheet metal, printing — running NetSuite / Epicor / SAP Business One / Fishbowl / Global Shop, with an inside-sales desk of 2–12 people. They know their quote-to-order ratio and their turnaround time, and they have been told "we lost it on lead time" for years.

## 3. The bleeding neck

- **RFQ decoding.** Every customer sends a different format: a PDF, an Excel with their own part numbers, an email body list, a photo of a handwritten sheet, a drawing. Mapping those to our SKUs is skilled, slow, and done by the person who happens to know that customer.
- **Quote latency.** Days, when the winner answers in hours.
- **Manual PO entry.** Re-keying an order from a PDF into the ERP: slow, and the source of the most expensive errors in the business (wrong quantity, wrong revision, wrong address, superseded part).
- **Margin drift.** Discounts get given to close a deal and never get analyzed. Nobody knows which concessions bought volume and which just gave away margin.
- **Quote follow-up.** Quotes go out and sit. The desk moves to the next RFQ.

## 4. What we build

**Pillars:** Sales (2) + Operations (5) + Back Office (6). **Form factors:** headless automation (parsing and entry) + embedded surface (the quote desk and margin ledger).

| Module | What it does | Autonomy start |
|---|---|---|
| **RFQ parser** | Ingests email bodies, PDFs, spreadsheets and photos; extracts line items with quantity, unit, spec and customer part number; maps to our catalog using catalog data, customer-specific cross-references, and prior purchase history — **with a confidence per line**. Low-confidence lines go to a human queue, never into a quote. | R2 for high-confidence lines only |
| **Quote builder** | Prices from the cost file plus the customer's agreement/tier, applies margin floors and approval thresholds, flags substitutions and lead-time risk, and produces a draft quote for approval. | R1 for anything below margin floor or involving a substitution |
| **PO ingestion** | Parses the returned PO, reconciles it line-by-line against the quote, and writes the order — with any discrepancy (price, quantity, revision, ship-to, terms) held in an exception queue rather than resolved by guessing. | R2 for exact matches, R1 for every discrepancy |
| **Quote follow-up** | Every quote reaches a recorded terminal state — won, lost-with-a-reason, expired — with a bounded, personalized ladder. Loss reasons are structured, because that's what feeds the ledger. | R1 → R2 |
| **Margin ledger** | Win/loss by customer, by product family, by discount depth and by turnaround time — answering "did faster quoting or deeper discounting win us more?" from our own recorded data. | — |

**Integrations:** ERP (NetSuite / Epicor / SAP B1 / Fishbowl), email, EDI seam, the cost/price file, and the customer cross-reference table.

## 5. The ROI model (assumption-stated)

```
Quote capacity   = RFQs/wk × hours per quote saved × loaded desk rate  → and RFQs quoted that previously weren't
Win rate         = turnaround hours reduced × win% sensitivity (from THEIR OWN ledger, once it has data)
Order-entry time = POs/wk × minutes each × loaded rate
Error avoidance  = order errors/mo × avg cost per error (rework + freight + credit)
```

The win-rate line is the biggest number and the least honest to assert up front — it must render `unmeasured — needs 90 days of quote outcomes` until their own ledger can compute it. Saying so out loud in the demo is a stronger sales move than showing a fabricated lift.

## 6. The demo path (10 minutes)

1. Quote desk: 14 RFQs today, 9 auto-drafted, 3 in the human queue with the specific low-confidence lines highlighted, 2 needing margin approval.
2. A messy RFQ — a PDF with the customer's own part numbers — parsed, mapped through the cross-reference, one line flagged as a discontinued part with a substitution proposed and held for approval.
3. A returned PO reconciled against the quote: price matches, quantity differs on line 4 → exception, not an order.
4. The margin ledger: discount depth vs. win rate by product family, with one cell blank because the sample is too thin.
5. Event log, rungs, counted automation rate, line-matching eval score with false-match rate broken out.

## 7. Guardrails

**No quote is sent without human approval below the margin floor, and no substitution is ever made silently** — a substituted part is a proposal with the spec difference named. **No order is written from a discrepant PO.** Line-matching confidence is measured and reported; below threshold the system refuses to guess, because a wrong part number shipped is a return, freight both ways, and a damaged relationship. Customer pricing agreements are confidential and never used to price another customer.

---

## 8. The prompt

> Copy everything below into a fresh chat in this workspace.

---

**Build a pre-built vertical AI OS prototype for wholesale distributors and job-shop manufacturers. Working name: Quote Desk OS.**

Build it into `Pre Build Ideas/wholesale-distribution/build/`. This is an yourco pre-build: a demoable prototype on synthetic data, not a production system, not connected to any live ERP. Read `CLAUDE.md`, `processes/ai-os-modules.md` and `processes/autonomy-matrix.md`, then read `Pre Build Ideas/property-management/build/core.py` and mirror its architecture and honesty rules exactly.

**The business you are modelling.** An $18M industrial distributor with light fabrication: ~6,000 SKUs across a handful of product families, ~400 active customers with tiered pricing agreements, ~90 RFQs/week arriving as email bodies, PDFs, spreadsheets and photos, an inside-sales desk of five, running Epicor. Build a real catalog with costs, list prices, customer tiers, superseded/discontinued parts, customer-specific part cross-references, and lead times. An inside-sales manager should recognize their own inbox in the seed.

**Two clocks are the product: quote turnaround and order entry. Build these five:**

1. **RFQ parser.** Ingest email bodies, PDFs, spreadsheets and photo-of-a-list inputs. Extract line items — quantity, unit of measure, spec, customer part number — and map each to our catalog using catalog data, the customer cross-reference table and that customer's purchase history. **Emit a confidence per line.** Lines below threshold go to a human queue with the ambiguity named; they never enter a quote silently. Line-matching accuracy, including false-match rate, is measured and shown.
2. **Quote builder.** Price from the cost file plus the customer's agreement and tier, apply margin floors and approval thresholds, flag lead-time risk, and propose substitutions for discontinued parts **with the spec difference named** — never silently. Produce a draft for approval; anything below the margin floor or containing a substitution is R1.
3. **PO ingestion.** Parse the returned PO and reconcile line-by-line against the quote. Any discrepancy — price, quantity, revision, ship-to, terms, date — holds the whole order in an exception queue with the specific delta shown. An order is never written from a discrepant PO, and a test must prove it.
4. **Quote follow-up.** Every quote must reach a recorded terminal state (won / lost-with-structured-reason / expired) via a bounded personalized ladder. The structured loss reason is what makes the next module work, so make capturing it easy and mandatory.
5. **Margin ledger.** Win/loss analysed by customer, product family, discount depth and turnaround time — answering "did faster quoting or deeper discounting win more?" from recorded outcomes only, with thin samples shown blank rather than computed.

Plus the **quote desk board**: today's RFQs, what auto-drafted, what is queued for a human and why, what needs margin approval, and average turnaround — counted from the event log.

**Confidentiality rule, in `core.py`:** one customer's pricing agreement is never used to price another customer, and the code should make that structurally hard rather than relying on discipline.

**Architecture.** Python stdlib only. `core.py` holds every rule: catalog and cross-reference models, the line-matching scorer and its confidence thresholds, pricing/tier/margin-floor logic, substitution rules, PO reconciliation and discrepancy typing, the quote state machine and follow-up cadence, and the autonomy matrix. `agents.py` holds the agents with a declared rung per action. `seed.py` generates the distributor at any scale (`--rfqs 90 --weeks 52`) including genuinely messy RFQs (customer part numbers, abbreviations, ambiguous units, a discontinued part, a photo-transcription case), POs with realistic discrepancies, and a year of quote outcomes with structured loss reasons. `data/` is a JSON store. `app/` is the surfaces on a stdlib server bound to `127.0.0.1`; add the `.claude/launch.json` entry and verify it responds.

**The two honesty rules, enforced in `core.py`:** (1) any number not computable from recorded events returns `None` with a `_missing` reason and renders as `unmeasured — <reason>`; (2) every state change appends to an immutable event log with actor and rung, and the automation rate is counted from it.

**ROI panel:** quote capacity, order-entry time, and error avoidance computed from the distributor's own inputs with arithmetic on screen, labelled a MODEL. **The win-rate line must render `unmeasured — needs 90 days of recorded quote outcomes` until their own ledger can compute it** — do not substitute an industry statistic, and make that refusal a visible part of the demo. Staff-time savings reported separately from revenue.

**Moat layer:** approval gate as the R1 floor on every quote below margin floor, every substitution, every discrepant PO and every customer-facing message; an eval harness scoring line-matching against a labelled set you generate, with **false-match rate reported separately** because a wrongly matched part ships, returns, and costs freight both ways; audit log view; rung promotion only on a recorded streak.

**Data:** synthetic only — invented customer and manufacturer names, obviously fake part numbers, no outbound network calls. Stub the ERP, email, EDI and the cost-file feed behind adapter interfaces; a missing adapter reports `cannot-simulate`, a blocker, not a pass.

**White-label:** the demo distributor's brand only — no yourco name, logo, or agent names on any customer-facing surface.

**Tests:** `test_quote_desk.py`, stdlib asserts, pinning: a low-confidence line never enters a quote; a substitution never happens without an approval event and a named spec difference; a discrepant PO never becomes an order; one customer's pricing cannot price another; the win-rate ROI line returns `None` until outcomes exist; a thin margin-ledger cell returns `None` with a reason; the event log is append-only.

**Deliverables:** the running build, the launch.json entry, a build `README.md` with the 10-minute demo script (quote desk board → a messy PDF RFQ parsed with one line queued and one discontinued part proposed → a PO reconciled to an exception on line 4 → the margin ledger with an honest blank → event log), and an honest "what this does not do yet." Report the test count, the line-matching eval score with false-match rate, and everything it refuses to compute.

Do not send anything, do not deploy, do not use a real company's, customer's or manufacturer's name.
