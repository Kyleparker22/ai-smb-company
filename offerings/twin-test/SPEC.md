# Twin Test — Build Spec

**Working name:** Twin Test (frontier #18)
**Author:** the Founder
**Stack:** the OS intake layer (assignment point — it already touches every inbound) · deterministic randomization + power/CI math in plain Python (unit-tested; no LLM in the statistics path) · the existing event stream for outcome measurement (booked/closed, from the same taps Leak Meter reads) · Claude API for readout narration only · the standard moat layer (eval · approval · audit log)
**Status:** Spec — see `offerings/_frontier-roadmap.md` row #18. Build trigger: **first client with sufficient inbound volume for statistically honest tests** — threshold defined in §7 by this spec's own mechanic.
**Pillar / form factor:** Sales/Intake (pillars 2/1) instrumentation with a Company Brain readout, shipped as form factor 2 (headless assignment + measurement) plus a console readout card (form factor 3).

---

## 1. Concept

Every SMB price change, script change, and hours change is an uncontrolled experiment with no control group: the owner changes the quote price, something happens, and nobody can say whether the price did it or the weather did. Twin Test gives offline businesses what only web companies have had — **controlled experiments on real operations**. A proposed change (new price point, new intake script, new callback window, Saturday hours) runs on a **randomized share of inbound** while the control keeps the current way; the OS's intake layer does the assignment (it already answers/routes every inbound, so randomization is a routing rule, not new machinery); outcomes are measured on close rate / booking rate from the event stream; and the readout reports the difference **with honest confidence bounds**.

**The centerpiece is statistical honesty at small n.** SMB volume is tiny by A/B standards, and the entire failure mode of "testing" at this scale is confident noise. Twin Test's identity is refusing to produce that: an experiment that cannot honestly detect an effect the client would care about, at the client's actual volume, **does not run** — the system says so up front, with the math shown (§7). Every readout that does run carries mandatory "how sure we actually are" language: the confidence interval in plain English, what it does and doesn't rule out, and a stop-rule verdict — never a naked "B won."

The client signs an **experiment brief** before anything runs: what's being varied, on what share, for how long, what's measured, what the test can and cannot detect at their volume, and the pre-registered decision rule. Informed consent is a feature of the product, not paperwork around it.

## 2. Why it's never been done

A/B testing needed three things offline businesses never had: a randomizable assignment point, cheap outcome capture, and someone who could run the statistics honestly. Web companies got all three from their stack; an HVAC shop has none — every inbound goes to whoever answers the phone, outcomes live in a paper folder, and the "test" is a feeling. The operated AI OS supplies all three as side effects: the intake layer touches every lead (assignment point), the event stream records every outcome (measurement), and the operator owns the analysis discipline (the moat's eval culture is literally experimental method — hypothesis, evidence, threshold — pointed at the client's business instead of at the agents). CRO consultancies won't touch businesses at this volume because honest answers are slow and small; tool vendors sell dashboards that let owners fool themselves. An operator whose brand *is* calibrated honesty is the first entity with both the substrate and the incentive to do this right.

## 3. Build shape

| Piece | What it is | Notes |
|---|---|---|
| Experiment brief | Pre-registration doc, client-signed: variable, arms, split share, primary metric, minimum effect the client cares about (their number, elicited in dollars then converted), max duration, decision rule | Nothing runs unsigned. The brief is the informed-consent artifact and the anti-p-hacking artifact in one. |
| Feasibility check | The threshold mechanic (§7) run against the client's actual trailing volume and baseline rate → "this test can/cannot honestly answer your question, and here's the math" | Runs *before* the brief is offered. A failing check is delivered as a readout in itself — often redirecting to a bigger detectable change or a longer window. |
| Randomizer | Deterministic hash-based assignment at the intake layer (lead id → arm), stratified where an obvious confound is known (weekday/weekend), logged per lead to the audit trail | Assignment is auditable and reproducible; no human cherry-picking which lead got which price. |
| Arm execution | The varied treatment applied by the modules that already act: the quote engine uses arm price, the intake agent uses arm script, scheduling offers arm hours | Anything customer-facing stays within its existing autonomy tier — a new script at R1 goes out draft-approved in both arms alike. |
| Measurement + stop rules | Outcomes read from the event stream; pre-set duration/n reached → analysis runs once, per the brief. Early stop only on the brief's pre-stated harm rule (an arm clearly hemorrhaging) | No peeking-driven stops, no extending "until it's significant." |
| Readout card | Console card + one-pager: effect estimate with CI in plain English, the mandatory certainty language, the pre-registered decision rule applied, and what happens next | Narrated by LLM from the computed numbers; the numbers themselves come from the tested stats code. Methodology and cost/margin framing reuse the house margin-analyzer approach (price arms are evaluated on margin, not just close rate). |

**Data sources:** the client's own intake and outcome streams (same taps as Leak Meter — which also supplies the baseline rates for feasibility math); the client-stated minimum-meaningful-effect from the brief. **Effort band:** M — feasibility calculator, randomizer, and readout template are template-generic (~3–5 focused days into `_yourco-template`); per-experiment cost thereafter is S (brief + wiring the arm, ~half a day).

## 4. Moat fit

- **Eval culture, client-facing:** earned autonomy already runs on hypothesis → evidence → threshold. Twin Test is the same discipline sold as a product; Kolby's weekly pass extends naturally (was the brief followed? did the readout carry the certainty language? did any analysis run off-brief?).
- **The refusal is the brand:** a system that says "your volume can't answer that question honestly" is doing something no dashboard vendor will. Same posture as "estimated leak, never lost revenue" — calibrated honesty as the differentiator no-code can't fake, because faking it is their business model.
- **Compounding asset:** every readout lands in the client's Company Brain — a growing file of *tested* facts about their own market that no competitor has. Feeds Exit-Asset (#3): a business with experiment-backed pricing diligences like a company, not a guess.
- **Model-upgrade dividend:** better models design sharper briefs and narrate readouts better; the statistics stay deterministic code, immune to model churn.
- **Interlocks (per roadmap):** **Leak Meter (#16)** supplies baseline rates and volumes for the feasibility math · **Boardroom (#9)** debates experiment results — a readout is the ideal dissent artifact · **margin-analyzer methodology reused** for evaluating price arms on margin · Ghost Quarter (#15) can simulate a proposed change before the client spends real inbound testing it.

## 5. Gates / compliance

- **No new counsel gates.** One scope-rider on **gate #1** (`processes/counsel-gates.md`, legal suite review): the engagement agreement's review should cover the experiment-brief consent language and the price-variation disclosure posture (what, if anything, the client must disclose to customers about quoted-price variation in their state/industry) — riding the existing counsel package per the 2026-08-06 pattern.
- **No experiments on legally-sensitive dimensions — named, not implied:** no pricing experiment may target, segment, or foreseeably proxy **protected classes** (race, religion, sex, national origin, age, disability, familial status, or local equivalents). Randomization is by lead id only — never by neighborhood/ZIP, name, language, or any attribute that proxies protected status. Regulated-pricing industries (lending-adjacent, insurance-adjacent, housing-adjacent) get no price arms at all without a specific gate-#1 counsel read first.
- **Client-informed consent:** the signed brief is a precondition, every experiment, no exceptions — including on what the test *cannot* detect.
- Harm stop-rule mandatory in every brief; customer-facing arm content respects existing autonomy tiers (no test smuggles an unapproved script past R1).
- White-label: customers see the client's business behaving normally, never test framing or yourco branding; readouts carry the client's brand (external-surface rules). Client readout figures never become yourco marketing claims without explicit consent and gate-#1-reviewed language.

## 6. Pricing frame *(assumption-stated; Polo locks before first proposal)*

Priced **per experiment or as a testing retainer**, not per-lead (illustrative only: a setup-plus-run fee per experiment in the high-hundreds-to-low-thousands, or a monthly experimentation band inside Operation/Command tiers running a continuous queue). The feasibility check is **free/included** — charging to be told "don't run this test" poisons the honesty that is the product; it also naturally sells volume-growing modules to clients who fail the threshold. All figures illustrative until first-ten-clients evidence; Polo locks the bands.

## 7. Activation trigger (build) — and the threshold mechanic

**Trigger, exactly as the roadmap row states: first client with sufficient inbound volume for statistically honest tests, threshold defined here.** The threshold is **not a magic number** — it's computed per client, per metric, per question:

1. From the client's event stream: baseline rate **p** (e.g. trailing-90-day close rate) and inbound volume **v** (leads/week) for the segment being tested.
2. From the brief: the client's **minimum meaningful effect Δ\*** (elicited in dollars, converted to rate points), split share, and max acceptable duration **T** weeks.
3. Standard two-proportion power calculation (α = 0.05 two-sided, power = 0.8, both stated on the readout) → the **minimum detectable effect (MDE)** at n = v × T × split.
4. **The test runs iff MDE ≤ Δ\*** within the client's T. Otherwise the system reports the gap honestly — "at your volume, X weeks can only detect a swing of Y points; you told us you care about Z" — and offers the honest alternatives: a longer T, a bolder arm, or wait for volume.

The same computation defines build-trigger readiness: the first client whose volume passes step 4 for a question they actually hold activates the build. Template pieces (feasibility calculator, randomizer, brief + readout templates) may be built into `_yourco-template` beforehand per the hooks-predate-clients sequencing rule.

## 8. What we will NOT do

- **No underpowered experiments, period.** If the feasibility math fails, the test does not run — not with caveats, not "directionally." The refusal is delivered as a product, not an apology.
- **No naked verdicts.** Every readout carries the mandatory certainty language and the CI in plain English. "B won" without "and here is how sure we actually are" never ships.
- **No p-hacking machinery:** no unregistered metrics promoted after the fact, no peeking-driven stops, no extending until significance, no quiet re-slicing. The brief is the contract; deviations void the readout.
- **No experiments touching protected classes or their proxies** (§5), and no price arms in regulated-pricing domains without a specific counsel read on gate #1.
- **No testing without the client's signed brief** — and no arm the client hasn't seen. We never test on a business owner the way ad platforms test on their customers.
- **No deception of end customers beyond ordinary price/script variation** a business could lawfully do by hand: no fake scarcity, no fabricated reviews or testimonials in any arm, nothing an arm makes true only by lying.
- **No "science-washing" in external copy:** yourco marketing never cites a client readout as a general claim ("our tests raise close rates X%") — house no-fabricated-metrics rule; each readout belongs to one client, one context.
- **No yourco branding on any customer-visible surface** of an experiment (white-label rule).
