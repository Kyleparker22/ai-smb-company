# The Churn Tripwire — Build Spec

**Working name:** The Churn Tripwire (frontier #29)
**Author:** the Founder
**Stack:** `dashboard/clients.py` health scoring (already per-module, per-gate, latest-result-only since the 2026-08-07 fix) + the `dashboard/tripwires.py` evaluation pattern, pointed at **relationship** signals rather than decisions · the client hears first, in plain language · billing consequence shared with Trip-Wire Pricing (#24)
**Status:** Spec — roadmap row #29. Build trigger: **first live client with usage telemetry** (~30 days post go-live).
**Pillar / form factor:** Customer (pillar 4); form factor 2 (headless monitor) with a direct message to the client.

---

## 1. Concept

Churn happens in silence. A module stops getting used, overrides creep up, logins thin out, replies get slower — and none of it produces an event, so the first signal the vendor receives is the cancellation. By then the decision is weeks old and the conversation is a save attempt, which almost never works because the client has already relitigated the relationship privately and reached a verdict.

The Churn Tripwire makes the silence audible, and — the part that has no precedent — **the client hears it first**:

> *"Module 3 has been near-zero for three weeks. Either it's broken or you don't need it. Tell us which, and we'll fix it or stop billing it."*

Volunteering that a client might be paying for something they no longer use is the most retention-positive move available, and no vendor makes it. It converts the churn conversation from a save attempt at the end into a maintenance conversation in the middle, at the moment when the problem is still small and the client has not yet built a story about why the relationship failed.

## 2. Why it's never been done

Churn prediction is a mature category — health scores, usage analytics, customer-success platforms, the whole apparatus. Every implementation shares one property: **the score is for the vendor**. It fires an internal alert, routes to a CSM, and produces an intervention designed to prevent cancellation. The client never sees the number and never learns that the vendor knows.

The reason is the incentive. A vendor who tells a client "you're not using this" is proposing to reduce its own revenue, and no customer-success function has ever been compensated for that. So the entire category is instrumented to detect the risk and manage it, never to disclose it.

Two things make disclosure rational for yourco. First, the **module-decomposed retainer** (already required by the Self-Proving Invoice #4 and Trip-Wire Pricing #24) means pausing one module is arithmetic rather than losing an account. Second, yourco sells a long operated relationship in which the alternative to a paused module is not a preserved line item but an eroded relationship that ends entirely. Trading a module to keep an engagement is straightforwardly good business — it just requires the vendor to be able to *see* the module separately, which most cannot.

## 3. Build shape

| Piece | What it is | Notes |
|---|---|---|
| Relationship signals | Per module: usage falling to near-zero · override/rejection rate rising · approval latency growing · console logins thinning · unanswered yourco messages · expansion conversation stalled | Deliberately module-scoped, so the consequence is module-scoped |
| Evaluator | Weekly pass on the `tripwires.py` pattern against the live eval + activity record; wires defined per engagement at go-live | Extends existing machinery; no new store |
| Client-first notification | Plain-language message to the client naming the metric, the window, and the two options (fix it / stop billing it) | **Before** it appears in any internal review — the ordering is the product |
| Consequence | Fix, pause, or withdraw the module. Pause is arithmetic against the module-itemised invoice | Shared mechanism with #24 |
| Honest instrumentation note | The client is told at go-live exactly what is measured about their usage and why | No hidden engagement telemetry |

**Effort band:** S — the health scoring and the trip-wire evaluator both exist; this is a signal set, a message template, and a decomposed invoice.

## 4. Moat fit

- **It is the retention instrument that requires the moat to exist.** Per-module usage, override rates and approval latency are only visible because the reliability layer records them. A no-code operator cannot see any of it.
- **It converts yourco's honesty posture into money retained**, which is the argument that keeps the posture funded.
- **It surfaces product defects early.** A module going unused is usually a build that missed the workflow, not a client going cold. Finding that in week three instead of month nine is worth more than the module's revenue.
- **It protects against the invisible-success failure mode** — an OS that works becomes invisible, and invisible things get cancelled. This is the counter-pressure.
- **Interlocks:** Trip-Wire Pricing (#24) shares the consequence machinery; Leak Meter (#16) and Self-Proving Invoice (#4) argue the value side; the Re-Audit (#31) is the scheduled version of the same conversation; Vacancy Expansion (#30) is where a withdrawn module's budget honestly goes next.

## 5. Gates / compliance

- **No counsel gate for the monitoring.** The **billing-pause consequence rides gate #16** with Trip-Wire Pricing — same clause, same counsel pass.
- **Disclosed telemetry only.** What is measured about the client's usage is stated at go-live and visible on their console. Covert engagement scoring would be the exact betrayal this product claims to avoid.
- **Never used as an upsell trigger.** A fired tripwire produces a fix, a pause, or a withdrawal. Routing it to a bigger-tier pitch converts an honesty instrument into a sales trap and destroys it permanently.
- **Client hears first, always.** If a tripwire fired and the client learned about it from an invoice, the module is unbilled for that period regardless of the underlying cause.
- **No per-person surveillance.** Signals are module-level and role-level. yourco does not report on which named employee used what — that is the client's business and, in several jurisdictions, their legal exposure.

## 6. Pricing frame *(Polo)*

**Included.** It is a property of the operated retainer, and its revenue effect is negative in the short term and positive over the relationship — which is the trade yourco is explicitly making. Modelling expected pause volume before it appears in a proposal is Polo's job at first-ten-clients scale; a firm with no live client cannot yet know its own pause rate, and that unknown gets stated rather than assumed.

## 7. Activation trigger (build)

**First live client, ~30 days post go-live** — the signals need a usage baseline before a deviation means anything, and firing a tripwire against three weeks of noise would burn the instrument's credibility on its first use. The signal set and message templates are template-buildable now into `clients/_yourco-template/`.

## 8. What we will NOT do

- **Never let the client find out from an invoice.** Client-first is the product; violating it forfeits the billing for that period.
- **Never use a fired tripwire as an upsell.** Fix, pause, or withdraw — no third option that involves selling something.
- **No covert engagement telemetry.** Everything measured is disclosed at go-live and visible to the client.
- **No named-individual usage reporting.** Module and role only.
- **No firing on a baseline that doesn't exist yet.** Below the baseline window, the instrument stays quiet and says why.
- **No quiet resumption of billing** after a pause — restart is an explicit, agreed event with a stated reason.
- **No tripwire on a metric the client can't verify.** They should be able to check the claim against their own experience; a wire they cannot audit is a vendor's assertion about a vendor's own performance.
