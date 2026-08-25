# The Re-Audit — Build Spec

**Working name:** The Re-Audit (frontier #31)
**Author:** the Founder
**Stack:** no new machinery — Bella re-runs the standard Audit (`processes/audit-sop.md`) against the now-instrumented business, differenced against the day-one baseline that the first Audit produced by construction · the Calibration Wager's ten answers (#25) and the Spend Teardown's inventory (#23) are the baseline's spine · output is a comparison document plus a fresh bottleneck
**Status:** Spec — roadmap row #31. Build trigger: **first renewal window** (baseline is captured at the first Audit, so nothing is needed now but discipline).
**Pillar / form factor:** cross-cutting; form factor 3 (a document, walked through).

---

## 1. Concept

A renewal date is a defend-the-price conversation, and it is the conversation the vendor loses. The client arrives having privately relitigated the spend; the vendor arrives with usage statistics; both sides argue about whether the last twelve months were worth it, which is an argument about the past that the vendor is structurally positioned to lose because the client has already decided.

Replace the renewal with a **re-audit**. Bella runs the same diagnostic that opened the relationship, against a business that is now instrumented, and produces three things:

1. **Movement against the day-one baseline** — the same axes, measured rather than estimated, including anything that got worse.
2. **The pillars yourco has not touched** — of the eight (`processes/ai-os-modules.md`), which remain unaddressed and what they are costing.
3. **The next bottleneck** — named, quantified, and possibly not an yourco problem at all.

The renewal becomes a discovery call, which is the conversation yourco wins. And the baseline exists **by construction**: audit-first means every engagement opened with exactly this diagnostic, so the comparison requires no foresight — only the discipline not to throw the first one away.

## 2. Why it's never been done

Two things exist near this and neither is it. **QBRs** report vendor activity — tickets closed, uptime, features shipped — which answers "what did you do" rather than "what is true about my business now," and every client knows the difference. **Business reviews from consultancies** are new engagements sold separately, priced separately, and therefore scoped to justify themselves.

The re-audit is different because the *same* diagnostic runs twice against the *same* axes, and the second run is honest about regressions. Almost no vendor can do the first part: their opening artifact was a sales document, not a measurement, so there is nothing to difference against. And almost none would do the second: reporting that a metric got worse during your engagement is not a natural act for a renewal conversation.

yourco can do both because the Audit is the product's front door rather than its brochure, and because the honesty posture is the differentiator being sold. The instrument only works for a firm whose opening diagnostic was real.

## 3. Build shape

| Piece | What it is | Notes |
|---|---|---|
| Baseline capture | Already happens: the Audit's quantified bottlenecks, the wager's ten answers (#25), the spend inventory (#23), the go-live readiness scores | The only new discipline is **preserving it verbatim** and never retro-editing it |
| Re-run | The same audit questions, now answerable from instrumentation instead of estimates | Same SOP, same axes — a changed axis makes the comparison meaningless |
| Difference | Per axis: baseline → now, measured, **including regressions**, with what moved it | `dashboard/timemachine.py` supplies the "which commit / which agent moved this number" provenance |
| Untouched pillars | Of the eight, which remain unaddressed; what each is costing, in their numbers | This is where expansion lives, arrived at diagnostically |
| Next bottleneck | Named and quantified; explicitly allowed to be something yourco does not sell | Credibility depends on this being genuinely possible |
| Estimate-vs-actual | Where day-one *estimates* proved wrong now that the thing is measured — yourco's own calibration, published to the client | The strongest trust move in the document |

**Effort band:** S–M per client — it is a re-run of an existing SOP, with the differencing being the new work.

## 4. Moat fit

- **It converts the weakest recurring conversation into the strongest.** Renewal becomes discovery, which is where the operated model expands naturally.
- **It only works if the opening artifact was real** — a structural advantage over anyone whose "audit" was a scoped sales exercise.
- **It publishes yourco's own estimation error.** Showing where day-one estimates were wrong, measured, is the same calibration discipline the wager asks of the client and the trust ledger asks of yourco. Asking the client to be scored while never being scored is the asymmetry that would break the whole family of instruments.
- **The eight pillars give expansion a map** rather than a pitch: untouched pillars are visible, quantified, and the client chooses.
- **Interlocks:** Calibration Wager (#25) and Spend Teardown (#23) are the baseline; Vacancy Expansion (#30) is the finer-grained sibling run inside a pillar; Ghost Quarter (#15) projects forward where this measures back; Exit-Asset (#3) consumes the same before/after evidence.

## 5. Gates / compliance

- **No counsel gate.**
- **Regressions are reported.** A re-audit that only shows improvement is a marketing document; the first time a client independently notices an unreported regression, every prior number becomes suspect.
- **Measured is labelled measured; estimated is labelled estimated.** Day-one figures were estimates and must not be silently reported as if they had been measurements — that would manufacture a flattering delta out of a methodology change.
- **No axis changes between runs** without stating the change and showing both. Moving the goalposts mid-comparison is the quiet version of the same dishonesty.
- **Attribution honesty:** where a number moved for reasons other than yourco (a good season, a hire, a market shift), the document says so. Claiming the whole delta is the fastest way to lose a client who knows their own business.

## 6. Pricing frame *(Polo)*

**Included in the operated retainer** — it replaces the renewal conversation rather than adding a billable engagement. Modules that result from it price at standard bands. Charging for the re-audit would reintroduce the incentive to scope it toward findings that justify its own fee, which is exactly the corruption that makes ordinary vendor business reviews worthless.

## 7. Activation trigger (build)

**First renewal window** for the live version — but the **baseline discipline starts at the first Audit**, which is now. Concretely: any audit run from today forward must preserve its quantified bottlenecks, wager answers, and spend inventory verbatim and immutably, because a re-audit against a baseline that was tidied up later is worthless. That is the only thing needed before the first renewal exists.

## 8. What we will NOT do

- **Never suppress a regression.**
- **Never present a day-one estimate as if it had been measured** to manufacture a favourable delta.
- **Never change the axes between runs** without showing both versions and saying why.
- **Never claim the full delta** where other causes contributed.
- **Never withhold the next bottleneck because yourco can't sell it.** If the biggest remaining constraint is a hire, a price change, or a supplier problem, that is what the document says.
- **Never let it become a renewal-pressure device** — no expiring offers attached, no "sign by" dates riding on the diagnosis.
- **Never re-audit without the original baseline.** If the baseline was lost or edited, the document says the comparison cannot be made honestly and reports the current state only.
