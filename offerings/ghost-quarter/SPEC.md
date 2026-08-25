# Ghost Quarter — Build Spec

**Working name:** Ghost Quarter (frontier #15)
**Author:** the Founder
**Stack:** simulation loop over the client's live engagement data (runtime pattern) · Claude API (driver extraction + scenario composition, retrieval-gated to the client's own records) · report renderer into the client console (`clients/_yourco-template/client-console.html` band) · feeds Boardroom (#9) agendas · methodology shared with the Audit (Bella's diagnosis layer, pointed forward)
**Status:** Spec — see `offerings/_frontier-roadmap.md` row #15. Build trigger: **first client with 60+ days of ops data.**
**Pillar / form factor:** Company Brain (pillar 7) analytics, delivered as form factor 3 (a report/console surface); no new agent.

---

## 1. Concept

Simulate the client's **next 90 days** from their real operational data, and hand them "**the quarter you're about to have**" — before they have it. The OS already watches the operation live: intake volumes and their sources, quote→close lag, invoicing and payment timing, scheduling load, the seasonal shape of demand, where approvals stall. Ghost Quarter runs that observed machine forward a quarter and names what falls out: *"on your current quote-response lag and this season's historical inquiry curve, roughly this much work doesn't get quoted in time next quarter — here is the driver, here is what it's plausibly worth"* — every leak named, every leak priced, every price labeled as the projection it is. The Audit told the client what their business *has been losing*; Ghost Quarter tells them what it's *about to lose* — **one methodology, pointed at two directions of time.** The past-facing version diagnoses; the future-facing version warns while the outcome is still changeable, which is the version an owner can actually act on.

The conversion mechanic is a single honest question at the end of every report: **"want us to prevent this version of the quarter?"** Each named leak maps to a module or an autonomy promotion the OS could ship — the Ghost Quarter is the expansion engine's agenda, written by the client's own data. And its second life is governance: the report feeds the **Boardroom** (#9) as standing agenda material — the board debates the quarter before it happens instead of postmorteming it after.

The centerpiece of this spec is not the simulation — it's the **credibility protocol** (§3.2). A projection product from the company whose entire identity is "no fabricated metrics" survives only if the line between *record* and *projection* is architecturally impossible to blur.

## 2. Why it's never been done

Forecasting for SMBs exists as two dead ends. Accountants produce financial projections — revenue lines extrapolated in a spreadsheet, disconnected from operational cause, delivered annually, ignored. Enterprise vendors sell simulation/digital-twin tooling that presumes a data warehouse, an analyst, and six figures — a stack no SMB has or will have. The missing precondition was never the math; it was the **data with causal texture**: you cannot simulate an operation you can't observe, and nobody observed SMB operations at the event level because the instrumentation would have cost more than the insight. yourco gets the instrumentation *free* — it is exhaust from an OS the client already pays for because it does the work itself; the observing layer and the operating layer are the same layer. That also produces the second unlock: **simulation with a repair path.** An analyst's forecast ends at the PDF; Ghost Quarter's operator can actually ship the module that changes the projected outcome — prediction and prevention in one vendor, which is what makes the report a sales motion instead of a document. Third unlock is cultural and is yourco's specifically: the discipline to publish projections *as* projections, assumptions inline, drivers cited — the eval-layer honesty habit applied to the future. Vendors without that habit either won't ship this (fear of being wrong) or will ship it dishonestly (precise-looking numbers, no assumptions) and burn the trust it needs. The house that never fabricates a metric is the only house that can safely sell a simulated one.

## 3. Build shape

### 3.1 The simulation pipeline

| Stage | What it does | Notes |
|---|---|---|
| Driver extraction | From ≥60 days of engagement data: volumes, rates, lags, seasonal shape, capacity ceilings — each stored as a **named driver with its evidence rows** | Retrieval-gated to the client's own records (the #2 architecture applied to analytics): a driver with no rows behind it cannot enter the model |
| Baseline projection | Drivers run forward 90 days on current behavior — "the quarter on autopilot" | Ranges, not point estimates, always; stated sensitivity to the shakiest assumption |
| Leak detection | Where the projected machine drops value: unquoted inquiries, aging receivables crossing thresholds, capacity-bound turn-aways, follow-up decay | Each leak = driver(s) + mechanism + a priced range with its arithmetic shown |
| Scenario variants | The same quarter with named interventions applied ("with quote-response handled at day-one speed, the same inquiry curve yields…") — one variant per plausible module/promotion | Variants are the conversion surface; each cites which driver it changes and why that change is achievable |
| Report + hand-offs | The Ghost Quarter report into the client console; leaks + variants into the Boardroom (#9) agenda; the "prevent this version?" conversation scheduled | Quarterly cadence, run as a standard runtime loop |

### 3.2 The credibility protocol (the load-bearing component)

Non-negotiable rules, enforced in the pipeline and the renderer, not by authorial discipline:

1. **Every simulated outcome is a labeled projection.** The renderer typographically separates the two data classes on every page — *record* (ledger-backed, cited) vs *projection* (modeled, assumption-tagged). A projection can never appear in record styling; the report template makes the violation impossible rather than discouraged.
2. **Assumptions inline, not appendixed.** Each projected line carries its assumptions at the point of the claim ("assumes inquiry seasonality matches your observed prior period; assumes current close rate holds"). No assumption, no line.
3. **≥60 days of real client data is the floor** — below it, the simulation does not run (this is the roadmap trigger, enforced in-product forever, not just at first build). No industry-benchmark stuffing to pad thin data: a driver we didn't observe is a driver the model doesn't have, and the report says which those are.
4. **Every report line links its driver.** Click a projected leak → the named driver → its evidence rows. Citations all the way down, exactly like the interview transcripts (#2) — the future is auditable back to the recorded past it was computed from.
5. **Ranges and confidence honesty.** Point-precision theater is banned; every priced leak is a range with its arithmetic shown, and the report names its own least-reliable assumption unprompted.
6. **Retrospective scoring.** Each Ghost Quarter is scored against the quarter that actually happened — the deltas published to the client in the next report, misses stated plainly. The simulation earns trust the same way the agents do: an evidence trail, including the unflattering rows (Kolby's eval pass owns the scoring).

**Data sources:** the client's own engagement exhaust exclusively — intake/CRM records, quote and invoice timelines, scheduling load, ledger rows; never cross-client data, never unlabeled industry benchmarks. **Effort band:** M — driver extraction + report schema ~3–4 days against a real engagement's data shapes; renderer rides the existing client-console surface; each subsequent client is S (drivers re-derived from their data, same pipeline).

## 4. Moat fit

- **Only the operator can ship it:** the simulation is computed from instrumentation that exists because yourco *runs* the operation — a no-code vendor or an outside analyst has neither the event-level data nor the repair path. The observing layer being the operating layer is the moat restated as analytics.
- **The expansion engine, systematized:** account expansion currently depends on noticing opportunities; Ghost Quarter turns the client's own data into a quarterly, evidence-cited expansion agenda — the Expand stage of the flywheel running as a loop instead of an instinct.
- **Trust compounds through §3.2(6):** a vendor that scores its own predictions publicly, misses included, is exercising the exact honesty muscle the Trust Ledger (#1) trained — one house discipline, another window.
- **Model-upgrade dividend:** better models extract subtler drivers and compose better scenarios from the same exhaust — the report sharpens quarterly at constant price, and says so.
- **Interlocks:** feeds Boardroom (#9) agendas (dissent needs material); the Audit shares its methodology (Bella's diagnosis layer, pointed forward — "the Audit is the past, this is the future"); leaks map to modules, closing the loop back to delivery; a mature Ghost Quarter record becomes Exit-Asset (#3) exhibit material (a business whose next quarter is modellable is a business a buyer can underwrite).

## 5. Gates / compliance

- **Credibility gate (house, absolute):** §3.2 *is* the compliance core — no simulated number may ever be presentable as a record; the no-fabricated-metrics rule extends to "no projection dressed as a measurement." Kolby's eval pass gates every report release (template conformance + citation integrity + retrospective scoring current).
- **Gate #1 scope-rider (engagement legal suite, `processes/counsel-gates.md`):** projection-disclaimer language joins the existing review batch — Ghost Quarter outputs are operational planning estimates, not financial forecasts, guarantees, or investment/valuation advice; no reliance representation. **No new gate** — rides the same counsel package (same batch as the #3/#2/#8 riders, 2026-08-06 entry).
- **Not financial advice, structurally:** the model projects *operations* (volumes, lags, capacity) and prices leaks as ranges from the client's own arithmetic; it does not project company valuation, advise on financing/investment, or produce lender-facing forecasts. If a client wants to show a Ghost Quarter to their bank, it goes with its labels intact and a written note that it is an operational planning artifact — or it doesn't go.
- **Client-data boundary:** single-tenant only — a client's simulation touches only that client's data; anything cross-client is the Immune System's (#8) anonymized-pattern lane, gated by its own consent clause, never raw drivers.
- **White-label:** the report is a client-console surface — client-branded per house rule; OtherVenture is untouched (nothing about this offering is public-facing; it exists inside signed engagements).

## 6. Pricing frame *(assumption-stated; Polo locks)*

Primary stance: **included in the upper OS tiers as a retention/expansion surface, not metered** — assumption: bundled from ~Suite upward, because its job (writing the expansion agenda, feeding the Boardroom) earns more than a line-item fee would, and unbundling it invites "skip the report, keep the OS." For Core-tier clients: available as a quarterly add-on at an assumption-stated module-band price once their data crosses the 60-day floor. Never priced per-simulation-run (the loop is cheap; scarcity-pricing it would be theater) and never priced as a percentage of "leaks found" (paying us more when the projection is scarier is an integrity-corroding incentive — see §8). All framing illustrative until first-cohort evidence; Polo locks against real tier economics.

## 7. Activation trigger (build)

**First client with 60+ days of ops data** — exactly as roadmap row #15, and the same threshold is a permanent in-product floor (§3.2(3)): the trigger isn't a launch date, it's the moment the input exists. Pre-trigger work permitted: report schema, renderer template with the record/projection separation, and the disclaimer language into the gate-#1 batch — the pipeline itself is built against the first real engagement's data shapes, not against synthetic data (a simulator tuned on invented data would violate the spec's own premise on day one).

## 8. What we will NOT do

- **No simulation under 60 days of real client data — ever**, and no padding thin data with unlabeled industry benchmarks. Missing drivers are named as missing, not imputed silently.
- **No projection presented as a record.** The typographic and structural separation of §3.2(1) is not waivable for a cleaner-looking sales page, a screenshot, or a client's request to "just show the number."
- **No point-estimate theater.** Ranges with shown arithmetic, always; no false precision, no unqualified headline number.
- **No fear-margin.** The model is never tuned to scare — no pessimism bias to juice conversion, and pricing never rewards scarier output (§6). The retrospective scoring (§3.2(6)) exists partly to catch exactly this drift, in either direction.
- **No selling inside the report.** The report names leaks and shows variants; the "prevent this version?" conversation is a separate, human, scheduled step — the artifact stays an analysis, not a brochure.
- **No financial forecasting, valuation, or investment-decision outputs** — operational projections only, with the gate-#1 disclaimer language intact on every copy that leaves the console.
- **No cross-client drivers.** One client's simulation never borrows another client's data in any form outside the #8 anonymized-pattern lane and its consent clause.
- **No memory-holing misses.** Retrospective deltas are published to the client every quarter, including the quarters we called wrong — deleting a bad scorecard row is the same sin as fabricating a metric.
