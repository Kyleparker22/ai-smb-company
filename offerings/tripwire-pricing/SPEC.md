# Trip-Wire Pricing — Build Spec

**Working name:** Trip-Wire Pricing (frontier #24)
**Author:** the Founder
**Stack:** the existing decision trip-wire machinery (`dashboard/tripwires.py` + the `## Trip-wire` section format in `decisions/_TRIPWIRES.md`) pointed at **modules instead of decisions** · the per-module eval ledger as the evaluator · a clause in the engagement agreement · a line on the client console and the monthly invoice
**Status:** Spec — roadmap row #24. Build trigger: **first signed client**, and ⚠️ **counsel + Polo before any proposal carries it**.
**Pillar / form factor:** cross-cutting commercial layer over every module; form factor 2 (headless monitor) with a console + invoice face.

---

## 1. Concept

Every software vendor's incentive at renewal is for the client not to look too closely. Shelfware is the most profitable state a SaaS line item can be in, which is why no vendor has ever built the thing that tells you to stop paying.

Trip-Wire Pricing inverts it. **Every module ships with a kill condition written at sale time**, in the engagement agreement, in the client's own terms: the specific, measurable condition under which this module is not doing its job. The module monitors its own trip-wire, the client hears about it from yourco *first*, and **billing for that module pauses until it is fixed**.

> *"This module is $1,800/mo. Its trip-wire: if you override its drafts more than 15% of the time for three consecutive weeks, it isn't working. We'll tell you before you notice, and we'll stop billing it until it is."*

The machinery already exists and is already trusted internally: yourco's own decisions carry trip-wires that report their own expiry against live facts, evaluated on the HQ Evidence door. This points that discipline at the commercial relationship.

**The centrepiece is that it is checkable.** A guarantee that depends on a vendor's judgement of its own performance is marketing. A trip-wire is a named metric, a named threshold, a named window, and an automatic consequence — which is why it can be believed by someone who has been burned before, and why it is worth more than any case study yourco does not yet have.

## 2. Why it's never been done

The closest existing shapes all stop short. **SLAs** cover uptime — whether the software was *available*, never whether it was *useful* — and pay out in service credits after the customer complains. **Outcome-based pricing** exists in pockets but prices the upside; nobody prices the downside with an automatic trigger. **Money-back guarantees** are one-shot, at churn time, and adjudicated by the vendor.

Two preconditions make this buildable, and yourco is unusual in having both. First, **the module must be able to measure its own usefulness** — which requires the eval/approval/audit layer that exists here because autonomy is earned on evidence (`processes/autonomy-matrix.md`). Override rate, gate pass rate, and time-to-approval are already recorded; a vendor without the moat layer has nothing to hang a trip-wire on. Second, **the vendor must be structurally willing to bill less**, which is only rational for a firm selling a decade-long operated relationship rather than a monthly licence. The first is technical, the second is strategic, and the intersection is roughly empty.

## 3. Build shape

| Piece | What it is | Notes |
|---|---|---|
| Trip-wire schema per module | `metric · threshold · window · consequence · evaluator` — stored beside the module definition in the engagement, mirroring `decisions/_TRIPWIRES.md`'s format | Written **at sale time**, in the proposal, not retrofitted later |
| Metric library | The small set of things that honestly indicate a module isn't working: override/rejection rate · usage falling to zero · gate failure rate · queue age · time-to-first-approval · volume handled vs promised | Deliberately small. A metric nobody can compute is not admissible as a trip-wire. |
| Evaluator | Extends the `tripwires.py` pattern: evaluate each module's wire against the live eval ledger, weekly | Reports on the client console + into the monthly close |
| Client notification | The client is told **first**, in plain language, with the number and the window | Never discovered by the client in a dashboard they had to check |
| Billing consequence | Module-level billing pauses; the retainer is decomposed per module so a pause is arithmetic, not negotiation | Requires the invoice to be module-itemised — which the Self-Proving Invoice (#4) already needs |
| Remediation clock | A stated window to fix, then either resumption with the client's agreement, or the module is withdrawn and permanently unbilled | No silent resumption |

**Effort band:** M — the evaluator is small (the pattern exists), but the **contract and invoice decomposition is the real work**, and it is Polo + Ray's, not an engineering task.

## 4. Moat fit

- **It sells the moat's byproduct.** Override rate and gate pass rate exist because autonomy is earned on evidence. This turns yourco's internal reliability instrumentation into the client's contractual protection.
- **It is the pre-revenue trust substitute.** With zero case studies, the strongest available claim is not "it works" but "here is what happens, automatically, if it doesn't."
- **No-code cannot follow, and neither can most agencies:** without an eval layer they cannot measure the trigger, and without an operated retainer they cannot afford the consequence.
- **It disciplines yourco.** A module that would trip its own wire does not ship — which is the correct pressure to put on a solo founder's build queue.
- **Interlocks:** Self-Proving Invoice (#4) is the same ledger arguing the other direction (what was delivered); the Churn Tripwire (#29) is this pattern pointed at the relationship rather than the module; the Reversibility Guarantee (#28) is its endgame (if it keeps tripping, leaving is easy and rehearsed).

## 5. Gates / compliance

- **⚠️ NEW COUNSEL GATE (#16) — billing-pause and service-credit language.** An automatic billing consequence is a contractual term with revenue-recognition and enforceability implications. Ray + counsel draft; **no proposal carries a trip-wire clause until it clears.** Rides the gate #1 legal-suite package.
- **Polo owns the commercial shape** — module-level decomposition of the retainer, what "pause" means against a bundled price, and the floor below which pausing is uneconomic.
- **No trip-wire on a metric yourco cannot compute from its own records.** A wire that depends on the client's self-report is unenforceable and, worse, invites a dispute about measurement at the exact moment trust is thin.
- **Thresholds are set conservatively and never widened after a wire fires** — moving the line post-hoc is the one action that would convert this from a guarantee into a trick, and it is prohibited in the agreement itself.

## 6. Pricing frame *(Polo locks; illustrative only)*

Not a priced add-on — a **property of every module**, and a reason the retainer holds its price rather than a discount on it. The commercial trade is explicit: yourco accepts pause risk on each module in exchange for a retainer that does not get renegotiated line by line every quarter. Expected cost is modelled at first-ten-clients scale before it appears in a proposal; a firm with no eval history cannot yet know its own trip rate, and that unknown is stated to the Founder rather than guessed.

## 7. Activation trigger (build)

**First signed client**, with the clause drafted and counsel-cleared *before* the proposal that signs them — this cannot be retrofitted onto a live engagement without renegotiation. The evaluator can be template-built ahead of that (hooks-predate-clients rule), and the metric library can be finalised now against yourco's own module evals.

## 8. What we will NOT do

- **No trip-wire we cannot measure ourselves.** No client self-reporting, no vibes, no "if you're not happy."
- **No moving a threshold after a wire fires.** The number is fixed at sale time. Renegotiating the line at the moment it triggers is the exact dishonesty this replaces.
- **No silent trips.** If a wire fires and the client was not told before the invoice, the module is unbilled for that period regardless — the notification duty is the product.
- **No burying it in terms.** The trip-wire appears in the proposal in plain language, not in an appendix.
- **No trip-wires on the reliability layer itself.** Eval, approval gates, and audit logging are not modules that can be paused; they are the floor.
- **No using a trip as an upsell moment.** A fired wire produces a fix or a withdrawal, never a pitch for a bigger tier.
- **No marketing the guarantee before counsel clears the clause** (gate #16), and no public claim of it pre-launch.
