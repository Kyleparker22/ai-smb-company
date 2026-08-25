# The Calibration Wager — Build Spec

**Working name:** The Calibration Wager (frontier #25)
**Author:** the Founder
**Stack:** no new runtime — `crm/wager.py` (built 2026-08-08): append-only store at `crm/_wagers.jsonl`, ten standard questions, 90-day settle window, direction-aware scoring
**Status:** **BUILT** — roadmap row #25. Tested open → measure → settle end-to-end 2026-08-08.
**Pillar / form factor:** Sales (pillar 2) feeding the Audit; form factor 3 (a conversation + a scored document).

---

## 1. Concept

A proposal asks a prospect to believe a claim about their business. The wager asks them to make ten claims about their own business, in writing, and then measures them.

At the audit conversation the owner answers ten questions they are certain about: *out of every ten inbound calls, how many go unanswered? what percentage of your quotes turn into paid work? how many days from invoice to money in the account? how many hours a week do you personally spend on admin?* Their answers are recorded, in their numbers, before anything is instrumented. Ninety days later the conversation is not "did you like the pitch" — it is **"here is where you were wrong about your own company, by how much, and in which direction."**

The instrument reports the systematic lean, not just the errors: **optimistic** (they believed the business was doing better than it was) or **pessimistic**, computed per question from whether higher or lower is better for that metric. In the reference run, five of five measurable predictions came back optimistic at a median 75% error — which is the finding, not the arithmetic.

`crm/calibration.py` measures yourco's own forecasting bias. This measures the owner's. Same discipline, opposite subject — and running both is what makes it defensible rather than condescending: we score ourselves on the same axis, publicly, in the trust ledger.

## 2. Why it's never been done

The pieces are all old and nobody has assembled them for a sale. **Forecasting calibration** is a well-developed field (Tetlock, Brier scoring, prediction markets) applied to forecasters, analysts and traders. **Business benchmarking** compares an owner to an industry average, which every owner correctly discounts as "that's not my market." **Diagnostic consulting** tells the owner what's wrong, which triggers the defence every consultant has met: *you don't know my business.*

The wager routes around that defence completely, because the benchmark is the owner's own stated belief and the scorer is their own records. There is no industry average to argue with and no consultant's opinion to reject — only the gap between what they said and what their books say. Nobody sells it because almost nobody can *measure* the follow-up: it requires instrumenting the business, which is the very thing being sold. For yourco the measurement is a byproduct of delivery. For everyone else it is a separate project nobody would fund.

## 3. Build shape

| Piece | What it is | Status |
|---|---|---|
| The ten questions | `missed_calls · quote_hours · quote_close_rate · followup_rate · ar_days · repeat_revenue · top_source_share · owner_admin_hours · margin_spread · first_responder`, each with unit and a `betterIsHigher` flag | **built** — the flag is what makes "optimistic" computable rather than rhetorical |
| Capture | `--open <dealId> --answers` → append-only record with settle date and tolerance; refuses unknown question keys and empty prediction sets; must bind to a real CRM deal | **built** |
| Measurement | `--measure <wagerId> --actuals` → append-only; refuses actuals for questions never predicted | **built** |
| Settlement | `--settle` → per-question error %, held/missed against tolerance, direction, median absolute error, systematic lean | **built** |
| Refusals | No settlement before the settle date (`--force` marks the output); **unmeasured questions are reported unmeasured, never wrong** | **built** |

**Effort band:** XS — ten questions in a conversation, and a settle run 90 days later. The real cost is instrumenting the actuals, which delivery does anyway.

## 4. Moat fit

- **It is the only "trust me" a pre-revenue firm can honestly make**, because the thing being tested is the owner, not yourco's track record.
- **It manufactures a dated checkpoint** the deal cannot drift past — the structural answer to the stall that is currently yourco's #1 commercial failure.
- **It generates the baseline everything else needs.** The ten answers *are* the audit's before-picture, which the Re-Audit (#31) measures against at renewal and the Leak Meter (#16) instruments continuously.
- **It sells the moat sideways:** discovering that four of ten calls go unanswered when the owner said one is not an argument for AI — it is an argument for *measurement*, which is the layer yourco owns.
- **Interlocks:** the Mirror Close (#21) names the unknown rung; the wager measures it. Trust Ledger (#1) carries yourco's own calibration on the same axis, which is what makes asking the owner fair.

## 5. Gates / compliance

- **No counsel gate.** Ten questions in a 1:1 conversation; no send, no publication, no scale.
- **Their figures are confidential** — tenant-isolated, never used as an example, named or anonymised, without written permission.
- **Never framed as a test the owner fails.** The delivery rule is that yourco states its own measured calibration bias first, from the trust ledger, and then asks. A wager offered by a party unwilling to be scored is a trap.
- **No industry benchmarks** in the settlement document — the comparison is their prediction versus their records, full stop (and the 12–18-month sourced-stats rule would apply to any external figure anyway).
- **No wager without a path to measurement.** If yourco cannot instrument a question within the window, it is not asked. Asking a question we cannot settle manufactures a debt we will default on.

## 6. Pricing frame

**Not priced.** It runs inside the Audit as a capture step and settles inside the engagement (or, if they didn't proceed, as an unpaid honest follow-up — which is its own strong second-touch). Charging for it would make yourco the vendor of the scoreboard it is also playing on.

## 7. Activation trigger (build)

**None — built.** Its *use* trigger is any audit conversation. Two operational notes: (1) it can be opened against a prospect who has **not** signed, which is what makes it a conversion instrument rather than a delivery ritual; (2) the settle date is only honoured if the actuals get measured, so opening a wager for a prospect who does not proceed requires either an agreed lightweight measurement or not opening it at all.

## 8. What we will NOT do

- **Never score an unmeasured question as wrong.** If yourco failed to instrument it, the settlement says so and names it as our failure. This is enforced in code and is the single rule that keeps the instrument honest.
- **Never settle early.** A 90-day question read at day 30 is a guess wearing a scoreboard. `--force` exists for testing and stamps the output.
- **Never edit a prediction after the fact.** The store is append-only; corrections supersede and are visible.
- **Never use it to embarrass.** The settlement is delivered as a finding about measurement, not a verdict about the owner — and yourco's own calibration goes on the table first.
- **Never ask a question we cannot settle.**
- **No benchmark smuggling** — no "the industry average is…" anywhere in the document.
- **No contingent claim attached to the outcome.** We do not promise to fix a specific gap by a specific amount because the wager exposed it; the wager measures, the audit prices, the proposal states assumptions.
