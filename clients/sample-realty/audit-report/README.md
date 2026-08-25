# Audit Report — deliverable template

The branded report a client receives at the end of the AI Audit (`processes/audit-sop.md`). Config-driven like the demo-kit: **Kimi edits the `AUDIT` object** at the top of `index.html` per client — everything else renders from it. No build step.

## How to use
1. Copy `audit-report/` into the prospect's folder (or fill in place for a one-off).
2. Edit the `AUDIT` config: `client`, `vertical`, `headline`, `bigNum`/`bigLabel` (the dollar leak), `bottlenecks[]` (top 1–3, each with money/freq/drain/fix scores 1–5 + a `heat` % bar), `math` (the dollar-cost calc, shown), `roadmap[]` (phased agents), and `firstBuild` (the 48-hour go-live + the offer).
3. Open in a browser → **Print → Save as PDF** for the client copy (it's print-styled).
4. **the Founder approves** before it's sent (brand + claims, no fabricated numbers — `processes/audit-sop.md` guardrails).

## What's in it
Headline bottleneck + the dollar figure → bottlenecks ranked with the 4-axis scores → the math on #1 (shown so they can check it) → the prioritized agent roadmap → the proposed first build + the offer (audit fee credits the build on a minimum 6-month engagement).

The shipped sample is a **landscaping** audit ($9k/mo missed-call leak) — replace it per client. Pricing is never in the report as a number beyond the client's own ROI math; the build proposal/fee is handled per `pricing/v0/audit.md` (Polo).
