# Audit Report — deliverable template

The branded report a client receives at the end of the AI Audit (`processes/audit-sop.md`). Config-driven like the demo-kit: **Kimi edits the `AUDIT` object** at the top of `index.html` per client — everything else renders from it. No build step.

## How to use
1. Copy `audit-report/` into the prospect's folder (or fill in place for a one-off).
2. Edit the `AUDIT` config: `client`, `vertical`, `headline`, `bigNum`/`bigLabel` (the dollar leak), `primaryFocus` (the one-word lever the roadmap pulls: money · time · quality · risk — `processes/audit-sop.md` §Report clarity), `bottlenecks[]` (top 1–3, each with a `heat` % bar; the 4-axis scores stay internal and never enter this config), `math` (the dollar-cost calc, shown), `signalsIntro` + `signals[]` (the **signal inventory** — 4–6 data sources the business already records, what each has been telling them, which roadmap phase uses it; only sources that surfaced in this diagnosis — `processes/audit-sop.md` §Step 5), `roadmap[]` (phased agents), and `firstBuild` (the 48-hour go-live + the offer).
3. Open in a browser → **Print → Save as PDF** for the client copy (it's print-styled).
4. **the Founder approves** before it's sent (brand + claims, no fabricated numbers — `processes/audit-sop.md` guardrails).

## What's in it
Headline bottleneck + the dollar figure + the one-word primary focus → bottlenecks ranked (heat bar only — the 4-axis scoring is internal, per `processes/audit-sop.md` §Report clarity) → the math on #1 (shown so they can check it) → the signal inventory (the data they already have, and what listens to it) → the prioritized agent roadmap → the proposed first build + the offer (audit fee credits the build on a minimum 6-month engagement).

The shipped sample is a **landscaping** audit ($9k/mo missed-call leak) — replace it per client. Pricing is never in the report as a number beyond the client's own ROI math; the build proposal/fee is handled per `pricing/v0/audit.md` (Polo).

## The control map (added 2026-08-24)
`AUDIT.governance` renders **"What it can do on its own — and what stays yours"**: a never-list, a
per-action table (action · starts as · why · what moves it), and a closing line. Fill it **only** from
Block E of the diagnostic call (`processes/audit-sop.md` §Step 2E, mapped in §Step 4b). The `earns`
column is the client's answer to Q21 **verbatim** — it is the promotion criterion they set themselves.

**If the client did not answer Block E, leave `governance` out entirely.** The section removes itself.
Do not fill it with sensible defaults: that would be a fabricated claim about what the client agreed to.

Preview it with `preview_start {name:"yourco-audit-report"}` (port 8811).

