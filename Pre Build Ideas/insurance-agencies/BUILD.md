# 4 · Independent Insurance Agencies (P&C) — **Renewal OS**

*Pre-build. Not built, not sold, no client. See `../_README.md` for the shared build contract.*

## 1. The idea in one paragraph

An independent agency's economics are retention economics: the book renews or it doesn't, and a policy lost at renewal takes its commission with it every year forever. Yet in most small agencies the renewal arrives as a carrier email nobody opened, the rate increase is discovered by the client before the producer, remarketing is a manual carrier-portal slog, certificates of insurance eat a CSR's day, and half the personal-lines book is mono-line — an auto policy with no home on it, sitting one competitor's quote away from leaving. **Renewal OS** is a watchtower over the book: it sees every renewal 90/60/30 days out, triages the rate change, assembles the remarket packet, drafts the client conversation, issues routine COIs under approval, and surfaces the cross-sell the agency already earned the right to make.

## 2. Who buys it

The **agency principal** of a 3–25 person independent P&C agency, $600k–$4M in commission, running AMS360 / Applied Epic / EZLynx / HawkSoft. They think in retention rate, and they know their book's mono-line percentage is bad without knowing the number. Highly relationship-driven and warm-intro reachable; also heavily regulated, which is why the draft-for-licensed-review pattern is the entire safety design.

## 3. The bleeding neck

- **Renewals that arrive untouched.** The carrier sends the renewal, nobody reviews it, and the first person to notice a 22% increase is the client — usually while talking to a competitor.
- **Remarketing is manual and therefore rare.** Pulling the current dec page, re-keying into three carrier raters, comparing coverage apples-to-apples: an hour a policy that nobody has.
- **COIs.** Contractors and commercial clients need certificates constantly, most of them routine and identical to the last one, all of them interrupting a CSR.
- **Mono-line exposure.** An auto-only or home-only household churns at a far higher rate than a bundled one, and the agency's own system knows exactly which households they are.
- **Claims silence.** The single highest-emotion moment in the relationship, and typically nobody from the agency checks in.

## 4. What we build

**Pillars:** Customer/Retention (4) + Sales (2) + Back Office (6). **Form factors:** headless automation (the watchtower) + embedded surface (the book board) + digital employee (the service assistant).

| Module | What it does | Autonomy start |
|---|---|---|
| **Renewal watchtower** | Every policy enters a 90/60/30 pipeline. Parses the renewal dec, diffs coverage and premium against the expiring term, classifies the change (rate, exposure, credit loss, carrier-wide action), and routes: quiet renewals get a light touch, material increases get a producer task with the conversation already drafted. | R1 → R2 for quiet renewals |
| **Remarket packet** | For flagged accounts: assembles the submission — current coverage, loss history, exposures, prior-carrier data — and produces an **apples-to-apples comparison sheet** that names every coverage difference rather than comparing price alone. | R1, always |
| **COI desk** | Routine certificates matched against a prior template and the underlying policy; issues under approval; anything with non-standard language (additional insured, waiver of subrogation, primary/non-contributory) is escalated, never auto-issued. | R1 hard floor on non-standard |
| **Mono-line finder** | Scores the book for cross-sell probability using the agency's own data — household composition, policy age, life events visible in the record — and hands the producer a ranked weekly list with the specific reason. | R1 |
| **Claims touch** | Detects a claim in the system and triggers a human-drafted, human-sent check-in at the right moments. | R1 |
| **Book board** | Retention rate by producer and carrier, renewals at risk in the next 90 days with premium at stake, mono-line %, COI turnaround — every one of them counted or blank. | — |

**Integrations:** AMS360 / Applied Epic / EZLynx / HawkSoft (policies, activities, download), carrier download feeds, email, e-signature.

## 5. The ROI model (assumption-stated)

```
Retention lift    = policies at renewal × retention pts gained × avg annual commission × persistency years
Remarket saves    = flagged increases × save% × avg commission
COI time          = certs/wk × minutes each × loaded CSR rate
Cross-sell        = mono-line households × contact% × bind% × avg added commission
```

The persistency multiplier is the number that makes this offering large and is also the easiest place to lie. The build must expose it as an editable assumption with a stated default and a visible warning that it compounds — never bury it.

## 6. The demo path (10 minutes)

1. Book board: retention by producer, 90-day renewal exposure in premium, mono-line %, one metric blank and labelled.
2. A renewal that came back +23%: the coverage diff, the classified reason, the drafted client conversation, the producer's approval.
3. The remarket packet built from it — including the comparison sheet that flags a lower deductible and a missing endorsement, not just a cheaper price.
4. A routine COI issued under approval; then one with an additional-insured request stopped and escalated.
5. This week's mono-line list with the specific reason per household.
6. Event log, rungs, counted automation rate.

## 7. Guardrails

**The AI never gives coverage advice, never quotes, never binds, and never issues a coverage opinion.** Everything material is drafted for a **licensed producer** to review and send — the same pattern as Conduit's UPL rule, and here it is licensure plus E&O exposure. Non-standard certificate language is a hard stop. No carrier-portal credential scraping without a written assessment (route to Rafi) — the demo stubs it. State-specific notice requirements (cancellation, non-renewal) are flagged for human handling, never automated.

---

## 8. The prompt

> Copy everything below into a fresh chat in this workspace.

---

**Build a pre-built vertical AI OS prototype for independent P&C insurance agencies. Working name: Renewal OS.**

Build it into `Pre Build Ideas/insurance-agencies/build/`. This is an yourco pre-build: a demoable prototype on synthetic data, not a production system, not a client deployment. Read `CLAUDE.md`, `processes/ai-os-modules.md` and `processes/autonomy-matrix.md`, then read `Pre Build Ideas/property-management/build/core.py` and mirror its architecture and honesty rules exactly.

**The business you are modelling.** An 11-person independent agency, ~$1.6M in commission, ~4,200 policies across ~2,600 households, roughly 60/40 personal to commercial lines, four producers, three CSRs, eight appointed carriers, running AMS360. Build a realistic book: policy types (auto, home, umbrella, BOP, GL, workers comp, commercial auto), premiums, effective dates spread across the year, loss histories, mono-line households, and renewal outcomes at every stage. A principal should recognize their own book in the seed.

**Retention is the entire product thesis. Build these five:**

1. **Renewal watchtower.** Every policy enters a 90/60/30-day pipeline. Parse the renewal declaration, diff coverage and premium against the expiring term, classify the change by cause (rate action, exposure change, credit/discount loss, carrier-wide filing, claim-driven), and route by materiality: quiet renewals get a light touch, material increases create a producer task with the client conversation already drafted and the *specific* reason named.
2. **Remarket packet.** For flagged accounts, assemble the submission from the agency's own data and produce an apples-to-apples comparison that names every coverage difference — deductibles, limits, endorsements, exclusions — and refuses to present a price comparison without the coverage diff attached. That refusal is a rule in `core.py`.
3. **COI desk.** Match routine certificate requests against the prior certificate and the underlying policy; issue under approval. Any non-standard language — additional insured, waiver of subrogation, primary/non-contributory, thirty-day notice — is a hard stop escalated to a human, never auto-issued, and this must be enforced by a rule and covered by a test.
4. **Mono-line finder.** Score households for cross-sell using only agency data (composition, policy age, prior quotes, life events visible in the record) and produce a ranked weekly list with the specific reason per household. No purchased data, no inference about protected characteristics — and write that constraint into the code.
5. **Claims touch.** Detect a claim in the system and stage check-ins at the right moments, drafted for a human to send.

Plus a **book board**: retention rate by producer and by carrier, premium at risk in the next 90 days, mono-line percentage, COI turnaround — each computed from recorded events or shown blank with a reason.

**The licensure guardrail is load-bearing and belongs in `core.py`, not a prompt string.** The system never gives coverage advice, never quotes, never binds, never issues a coverage opinion, and never sends a material client communication without a licensed producer's approval. State-mandated notices (cancellation, non-renewal, mid-term change) are flagged for human handling and never automated. Make the refusal visible in the demo — a prospect should watch it decline to answer "am I covered for this?" and route the question to a producer.

**Architecture.** Python stdlib only. `core.py` holds every rule: the policy and coverage model, the renewal diff and classification logic, materiality thresholds, the comparison-sheet rules, certificate standard-vs-non-standard classification, the cross-sell score, and the autonomy matrix. `agents.py` holds the agents with a declared rung per action. `seed.py` generates the agency at any scale (`--policies 4200 --months 24`) including renewals returning at every premium delta, certificates both routine and non-standard, open claims, and households at varying cross-sell readiness. `data/` is a JSON store. `app/` is the surfaces on a stdlib server bound to `127.0.0.1`; add the `.claude/launch.json` entry and verify it responds.

**The two honesty rules, enforced in `core.py`:** (1) any number not computable from recorded events returns `None` with a `_missing` reason and renders as `unmeasured — <reason>`; (2) every state change appends to an immutable event log with actor and rung, and the automation rate is counted from it.

**ROI panel:** retention lift, remarket saves, COI time, cross-sell — computed from the agency's own inputs with the arithmetic on screen, labelled a MODEL. The persistency multiplier on retention lift must be an *editable, visible* assumption with a stated default and a plain warning that it compounds across years; never bury it inside a headline number. Staff-time savings reported separately from commission.

**Moat layer:** approval gate as the R1 floor on every client-facing message and every certificate; an eval harness scoring renewal-change classification and standard-vs-non-standard certificate detection against a labelled set you generate, reporting the false-"standard" rate separately because that error is an E&O event; audit log view; rung promotion only on a recorded streak.

**Data:** synthetic only — invented carrier names, 555 phone ranges, no real people, no outbound network calls, and **no carrier-portal scraping of any kind**. Stub the AMS, carrier download, email and e-signature behind adapter interfaces; a missing adapter reports `cannot-simulate`, a blocker, not a pass. Note in the README that any real credentialed carrier-portal access needs a written compliance assessment first.

**White-label:** the demo agency's brand only — no yourco name, logo, or agent names on any client-facing surface.

**Tests:** `test_renewal_os.py`, stdlib asserts, pinning: a non-standard certificate can never be auto-issued; a price comparison cannot render without its coverage diff; the system refuses to answer a coverage question and routes it; an uncomputable board metric returns `None` with a reason; the event log is append-only; no client message sends above its declared rung.

**Deliverables:** the running build, the launch.json entry, a build `README.md` with the 10-minute demo script (book board → a +23% renewal classified and drafted → remarket comparison flagging a coverage difference → routine COI issued and a non-standard one stopped → mono-line list → event log), and an honest "what this does not do yet." Report the test count and everything it refuses to compute.

Do not send anything, do not deploy, do not use a real agency's or carrier's name.
