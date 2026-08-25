# Leak Meter — Build Spec

**Working name:** Leak Meter (frontier #16)
**Author:** the Founder
**Stack:** client console overlay (`clients/_yourco-template/client-console.html` band) · the OS event stream the modules already emit (call/intake events, quote timestamps, invoice ledger) · a small deterministic pricing engine (no LLM in the arithmetic path) · Claude API only for the plain-English line narration · the standard moat layer (audit log; the meter itself takes no actions)
**Status:** Spec — see `offerings/_frontier-roadmap.md` row #16. Build trigger: **first client console live** (needs a real event stream).
**Pillar / form factor:** Company Brain (pillar 7) instrumentation over Intake/Sales/Back Office events, shipped as form factor 3 — an **embedded AI surface** (a band on the client console; no agent attached, and that's a shape, not a gap).

---

## 1. Concept

The Audit prices what the business is losing — once, as a snapshot. The Leak Meter is **the Audit's math running continuously**: a live counterfactual band on the client console that counts and prices what *didn't* happen, from events the OS actually logged. Each missed after-hours call × the client's own average job value × a stated close-rate assumption. Each quote that went out slow × the close-rate decay the client agreed reflects their market. Each invoice aging past terms × a collection-odds decay. Every line on the meter is a real logged event with a stated multiplier attached — click any line and the trace opens: the event, the timestamp, the assumption applied, who approved that assumption and when.

**The centerpiece is the counterfactual honesty protocol.** Counterfactuals are where dashboards lie, so this one is built not to be able to: (1) **every line traces to a real logged event** — no modeled, inferred, or "typical business like yours" events, ever; (2) **every multiplier is stated and client-approved at setup** — their own average job value from their own books, their own close rates where known, an explicitly-labeled estimate where not, all recorded in a signed assumption schedule the meter displays on demand; (3) **the language is "estimated leak," never "lost revenue" as a fact claim** — the header carries the standing caption that these are estimates built on the client's own stated assumptions, and every export carries it too. The number is credible *because* it's conservative and traceable — the same honesty posture as the whole house (assumption-stated, projections labeled as projections).

**What it does commercially:** it is the anti-churn instrument. Month over month, the meter shows exactly what the retainer stands between the client and — the day the "considering cancelling" conversation happens, the counter-question is already on their own console. And it is the expansion engine: the biggest leak line the OS doesn't yet cover is, by construction, the next module's business case, priced in the client's own numbers.

## 2. Why it's never been done

Analytics products count what happened. Nobody ships a *counterfactual* meter for SMBs because the two ingredients have never coexisted: (a) a trustworthy event stream of the misses themselves — you only log the 2am call nobody answered if an AI intake layer is actually catching or observing it — and (b) an operator willing to bind every dollar figure to a client-approved assumption instead of a flattering default. Marketing-agency "missed revenue calculators" exist and are the anti-pattern: invented industry multipliers, no event trace, engineered to inflate. The moat layer is what makes the honest version possible — yourco already runs eval-grade logging on every event, so the meter is a *view*, not a new capture system. No-code operators have neither the stream nor the discipline; incumbents with the stream (phone systems, FSM software) have no incentive to price their own gaps.

## 3. Build shape

| Piece | What it is | Notes |
|---|---|---|
| Assumption schedule | Setup artifact: avg job value (from client books), close-rate by lead type (client-stated or measured), quote-speed decay curve, AR collection-odds decay, after-hours definition | Signed off by the client at onboarding; versioned; every change re-approved and dated. The meter shows "assumptions as of \<date\>." |
| Event taps | Read-only subscriptions to streams the modules already write: intake events (answered/missed, timestamp), quote lifecycle (requested → sent), invoice ledger (issued → paid) | Zero new capture. A leak type with no live stream stays **off** — no synthesized events. |
| Pricing engine | Deterministic: event × approved multiplier × decay function. Pure arithmetic, unit-tested, no LLM in the loop | The trace record (event id, multiplier version, formula) writes to the audit log per line. |
| Console band | The meter on the client console: running month/quarter estimate, per-category breakdown, per-line drill-down to the trace, the standing "estimated" caption | White-label, client brand only. Language locked by the honesty protocol; copy reviewed against `brand/writing-rules.md`. |
| Covered/uncovered split | Two columns: leaks the OS now prevents (with the same math showing avoided leak) vs. leaks still open | The uncovered column is the expansion surface; the covered column is the retention surface. Avoided-leak lines carry the identical "estimated" framing — no victory-lap fact claims. |
| Ghost Quarter feed | The assumption schedule + event-rate history export as the calibrated inputs to #15's 90-day simulations | One JSON contract; Ghost Quarter consumes, never back-writes. |

**Data sources:** the client's own OS event streams only (intake, quoting, AR), plus the client-approved assumption schedule. **Effort band:** S–M — pricing engine + console band are template-generic (~2–4 focused days into `_yourco-template`); per-client setup is S (assumption schedule interview + tap wiring, ~half a day) and largely falls out of the Audit, which already gathered the same numbers.

## 4. Moat fit

- **Proof, permanently on:** the Audit's one-time credibility becomes a standing instrument. Kolby's eval pass gets a new check: does every meter line trace to a real event and a current approved assumption? Drift on either fails the week.
- **Trust:** an operator willing to show conservative, traceable estimates — and to show the *covered* column shrinking the number — is demonstrating the exact honesty posture the moat is made of. A no-code operator's version of this is a marketing widget; that contrast is the sale.
- **Anti-churn by design:** the retainer's value is re-argued daily by the client's own data. This is the Prove stage of the flywheel made ambient (roadmap batch-4 note).
- **Model-upgrade dividend:** better models narrate leak lines and spot uncovered leak *categories* better over time; the arithmetic stays deterministic regardless — upgrades sharpen the story, never the math.
- **Interlocks:** continuous-Audit (the same math, same schedule) · Self-Proving Invoice #4 (the invoice cites the covered column) · Ghost Quarter #15 (consumes the calibrated assumptions) · Boardroom #9 (debates the biggest uncovered line).

## 5. Gates / compliance

- **No new counsel gates.** One scope-rider on **gate #1** (`processes/counsel-gates.md`, legal suite review): the engagement agreement's review should cover the assumption-schedule sign-off language and the "estimates, not guarantees" disclaimer wording — same pattern as the 2026-08-06 gate-1 scope additions.
- The meter is **internal to the engagement**: a client-console surface, not a marketing surface. Its figures never appear in yourco's external copy as outcome claims (no fabricated/implied metrics — house rule). If a client volunteers their meter as a testimonial post-launch, that's their number, their consent, gate-#1-reviewed release language.
- White-label throughout; no yourco branding, no agent names on the console band (external-surface rules).
- Read-only over event streams; the meter takes no actions, so no autonomy-matrix tier applies beyond R0-observe.

## 6. Pricing frame *(assumption-stated; Polo locks before first proposal)*

Not a separate SKU by default: the Leak Meter ships **included in the OS retainer** as console instrumentation — its job is retention and expansion, and gating the anti-churn instrument behind an upsell defeats it. Where it appears priced: as part of the Audit deliverable framing ("the Audit's math, kept running") and possibly a small standalone band (~low hundreds/mo, illustrative only) for an Audit-only client who hasn't bought a module yet — the meter then sells the first module. All figures illustrative until first-ten-clients evidence; Polo prices the bands.

## 7. Activation trigger (build)

**First client console live** — exactly as the roadmap row states. The meter needs a real event stream; before one exists there is nothing honest to meter. Template pieces (pricing engine, console band, assumption-schedule template) may be built into `_yourco-template` ahead of that per the hooks-predate-clients sequencing rule; no client-facing meter until real events flow.

## 8. What we will NOT do

- **No modeled events.** Every line traces to a logged event. No industry-average phantom misses, no "businesses like yours typically…" lines, no backfilled history from before the taps were live.
- **No unapproved multipliers.** A multiplier the client hasn't signed doesn't run. If the client won't state a close rate, that leak category shows event *counts* only, un-priced, labeled "no approved assumption."
- **No "lost revenue" as a fact claim.** The words are "estimated leak," everywhere — console, exports, conversations. The caption never gets dropped for a cleaner screenshot.
- **No fear-dial tuning.** Assumptions are never nudged upward to make the number scarier before a renewal or an upsell. The number is whatever the approved schedule produces; changing the schedule requires the client's dated re-approval.
- **No external use of client meter figures** in yourco marketing without explicit client consent and gate-#1-reviewed language — and never pre-launch (OtherVenture).
- **No new capture systems** built for the meter. It reads streams the OS already writes; a leak the OS can't see stays off the meter and is named honestly as not-yet-instrumented.
- **No actions.** The meter informs; modules act. It never auto-triggers outreach, collections, or pricing changes off its own numbers.
