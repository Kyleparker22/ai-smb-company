# The Self-Proving Invoice — Build Spec

**Working name:** The Self-Proving Invoice (frontier #4)
**Author:** the Founder
**Stack:** per-client eval ledger (JSONL in the client repo, written by the moat layer already in every engagement) · a monthly generator loop (Claude API render → HTML/PDF) · delivered via the client console + email (draft-for-approval)
**Status:** Spec + template — see `offerings/_frontier-roadmap.md` row #4. Build trigger: **first billable month.**
**Pillar / form factor:** cross-cutting (this is the moat layer made visible), shipped as form factor 2 (headless monthly loop) surfacing in form factor 3 (the client console).

---

## 1. Concept

The monthly invoice, generated **from the eval ledger**. Not a bill with a report stapled to it — one document where every line is a claim the ledger can prove: outcomes delivered this month, actions taken (by module, by autonomy tier), incidents (**zero or stated — never omitted**), evals passed, autonomy earned. Each line carries ledger IDs; a skeptical bookkeeper can trace any sentence to the raw records in the client console. **Billing = reporting.** The client's monthly "what am I paying for?" moment — the moment every retainer business dreads — becomes the monthly proof ritual.

Critical inversion, stated up front: **the lines prove; they never price.** The retainer is flat (business-plan §4 — metering re-exposes the client to the complexity we absorb and sets our incentive against theirs). The invoice total is the agreed retainer whether the ledger shows 400 actions or 4,000. The ledger data answers "was it worth it," not "what does it cost." An invoice whose total moved with the action count would be usage billing wearing a costume, and would un-make the model-upgrade dividend (an upgrade that raised the invoice is not a dividend).

## 2. Why it's never been done

Agencies invoice hours (input, unverifiable). SaaS invoices seats/usage (meter, not outcome). Nobody invoices from an eval record because almost nobody *has* an eval record — the artifact only exists where reliability/eval/observability is the operating discipline, which is precisely the layer commoditized tooling lacks. For yourco it is nearly free: the moat layer already writes every record this invoice needs; the offering is a render step over data the business model produces as exhaust. Competitors would have to build the moat layer first to copy the invoice — which is the point. It is also the per-client window onto the same substance the Trust Ledger (#1) shows publicly and the Interviewable Employee (#2) speaks aloud: one ledger, three surfaces.

## 3. Build shape

### 3.1 The ledger schema — what every client engagement must capture from day one

Ships in `_yourco-template` as `ledger/` so capture is automatic at scaffold time, not retrofitted. Append-only JSONL, one file per month (`ledger/YYYY-MM.jsonl`), written by the same hooks that run the moat layer:

```
action_record   {id, ts, module, pillar, action_type, autonomy_tier,      -- R0–R3 at time of firing
                 outcome_class,            -- completed | approved+sent | escalated | rolled_back
                 approval {approver, ts} | null, eval_ref | null, links[]}
eval_record     {id, ts, module, gate_name, result,                        -- pass | fail
                 sample_size, notes, action_ids[]}
incident_record {id, ts, severity, module, what_happened, caught_by,      -- watchdog|eval|human|client
                 impact, remediation, resolved_ts}                         -- written even when impact = none
outcome_record  {id, ts, outcome_name,                                     -- the audit-scoped outcomes this engagement exists to deliver
                 metric {name, value, source, period} | qualitative_note,
                 evidence_links[]}
autonomy_event  {id, ts, module, action_type, from_tier, to_tier,
                 evidence: streak_summary, approved_by}
```

Four rules that make it invoice-grade: (1) **append-only** — corrections are new records referencing old IDs, never edits; (2) **write-at-source** — the runtime hooks write records as a side effect of acting, no end-of-month reconstruction; (3) **incidents are mandatory** — a month with none gets an explicit attested "zero incidents" line generated from the *absence* of records plus the watchdog's I-was-running heartbeat (silence from a dead watchdog must not render as a clean month); (4) **outcome metrics name their source** (client system, count, or qualitative + label) — no number without provenance.

### 3.2 The generator

Monthly loop (runs at Charles's close cadence): read the month's JSONL → aggregate → render the house template → **R1 draft** to the Founder for approval → deliver. Template sections, in order: **Outcomes delivered** (the headline — audit-scoped outcomes with sourced evidence) · **What ran** (actions by module × tier; autonomy promotions earned this month) · **Reliability** (eval gates passed/failed, incidents zero-or-stated with remediation) · **What's next** (next module, next promotion pending) · **Amount due: the retainer, flat.** Every aggregate line footnotes its ledger IDs; the client console exposes the drill-down. **Effort band:** S — schema + hooks into the template ~2 days; generator + render ~2 days; the data pipeline already exists as the moat layer.

## 4. Moat fit

The purest expression of the moat available: proof (every line traceable), trust (an invoice that voluntarily states its own incidents is the executive-trust artifact — nothing builds credibility like self-reporting a caught failure and its fix), integration (outcome metrics pull from the client's own systems), and the retention engine in paper form — cancelling means giving up the only vendor whose bill proves itself. It makes the model-upgrade dividend *visible*: "outcomes up, incidents down, price unchanged" across months is the dividend as a chart. And it feeds the flywheel's **Prove** stage every single month without a sales motion. No-code operators cannot copy it because they have no ledger to generate it from.

## 5. Gates / compliance

- **Approval gate:** the invoice is client-facing and money-adjacent — generated as an R1 draft, the Founder (later a named approver) reviews and sends. Never auto-sent; this stays R1 longer than the evidence rule would allow, by choice, because a wrong number on an invoice is a trust-killer disproportionate to its probability.
- **No fabricated or unsourced metrics** — the generator refuses to render an outcome line lacking a source field; qualitative outcomes are labeled qualitative. House credibility gate applies to a *billing* document with extra force.
- **White-label:** the client's invoice carries yourco's identity as the vendor (correct — it's our bill) but any metrics referencing the client's customers stay aggregate; no customer PII on the invoice or console rollup.
- **Counsel gate:** none specific; invoice terms ride the engagement-agreement suite (gate #1). Tax/format mechanics are Charles + standard bookkeeping, not counsel.

## 6. Pricing frame *(assumption-stated; Polo locks)*

**Not priced. Ever.** The self-proving invoice is how every yourco retainer is billed, not an add-on — its cost is inside the retainer's margin (generation cost ≈ pennies of tokens; the capture cost is zero because the moat layer already writes the records). Its pricing effect is indirect and is the business case: it defends the retainer at renewal, justifies the top of the band in compliance-heavy verticals, and turns the monthly bill into the expansion conversation ("what's next" is a section *on the invoice*). Illustrative, not promised: if it moves retention by even a few points, it is worth more than any priced feature we could ship (business-plan §8 — retention governs long-run value).

## 7. Activation trigger (build)

**First billable month** for the generator. The **ledger schema ships in `_yourco-template` now** (roadmap sequencing #1: template design predates client #1 — retrofitting capture across live engagements loses months of record, and month one's invoice needs month one's data). Sample Client, if it signs, bills this way from invoice #1.

## 8. What we will NOT do

- **No usage-based totals.** The action counts never price. If a client asks to "just pay for what ran," the answer is the §4 argument, not a discount SKU.
- **No suppressed incidents.** An incident that touched the client renders on the invoice, full stop. An invoice month is never edited after send; corrections appear as a stated line the following month.
- **No metrics theater.** No dashboard-y vanity counts promoted to outcome lines; the Outcomes section only carries what the audit scoped as the point of the engagement. If a month delivered little, the invoice says so — a thin honest month protects the instrument that makes every fat month believable.
- **No reconstruction.** If the ledger is missing records (hook failure), the invoice states the gap; we never backfill from memory.
- **No client-side complexity.** The drill-down exists for the skeptic; the invoice itself stays one page. Billing = reporting must never become billing = homework.
