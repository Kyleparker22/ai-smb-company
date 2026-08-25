> ⚠️ **EXAMPLE — not yours.** An artifact from the source company, restored because other pages
> cite it and the reasoning would otherwise dead-end. It describes **someone else's business**.

# Advisory panel — AI OS design: what to steal, what nobody has built

**Date:** 2026-08-13 · **Mode:** on-demand, the Founder-requested · **Scope:** (1) research the best AI OS
platforms and decide what to copy; (2) 3 ideas yourco has not considered; (3) 3 ideas nobody has
built. Internal thinking tool — **no external surface may imply these people reviewed yourco.**

**Panel (8):** Karpathy (autonomy sliders, ground-truth evals) · Willison (prompt injection,
publish-the-security-model) · Weng (agent architecture: planning/memory/tools) · Amodei (gated
autonomy scaling) · Munger (moat vs revenue) · Christensen (jobs-to-be-done) · Dunford
(positioning, proof assets) · Martell (founder-time leverage).
**Left out:** the whole sales sub-panel — this run is about platform design, and the commercial
findings were run 6 hours ago (`2026-08-13_crm-product-direction.md`). Re-running them would be
repetition decay.

---

## Standing (one line each — not re-argued)

| Ref | Standing finding | Status |
|---|---|---|
| CV1 (07-21) | Proof before program — the channel amplifies proof, cannot create it | **Unchanged.** Still 0 signed |
| CV-A (08-13) | The CRM has no price instrumentation | **Unchanged**, hours old |
| CV-C (08-13) | Capacity is the binding constraint; the instrument measures demand | **Escalated below** — it is also the constraint on everything in this report |
| CV-D (08-13) | ~~Feature work displacing selling~~ | **Withdrawn** by the prior run; not revived. The launch-gate forbids selling |
| Model layer unabstracted (08-13 learning) | yourco is already multi-model, ad hoc, no seam | **Directly relevant** — Sierra's "constellation of models" is the productised version. Not re-argued here |

---

## Part 1 — the platforms, and what is worth taking

Researched 2026-08-13. Batch-triaged per `.claude/skills/tool-triage`: one-line verdicts, deep dive
only on the steals.

| Platform | The idea worth looking at | Verdict |
|---|---|---|
| **Palantir Foundry / AIP** | The **Ontology**: agents act through *the same governed action types human operators use*, permission-aware. AIP Evals sit on the ontology, not beside it | **STEAL the pattern (small).** yourco rungs *actions* in the autonomy matrix but has no single registry of "actions this OS can take" shared by human and agent. The matrix is that registry in prose — making it the machine-readable one is a half-day, and it is what lets an eval attach to an action rather than to a loop |
| **Microsoft Agent 365 + Entra Agent ID** | Agents as first-class identities with a **sponsor**, and **lifecycle expiry** — access does not outlive need | **Partly ours, one real gap.** `runtime/agent-registry.json` + the governance watchdog already do discovery and sanction. **Expiry does not exist** — see Idea 3 |
| **Salesforce Agentforce 3 Command Center** | **Testing Center**: simulate an agent at scale with *data-state injection* + AI evaluation **before go-live**; replay actions, trace decision paths | **STEAL — the strongest single item in this table.** yourco's eval is weekly and *post-hoc* (Kolby). Nothing simulates an agent against injected states before it touches a client. This is the 48-hour go-live promise's missing safety net, and `runtime/drills/schema_drift.py` is already the seed of the mechanism |
| **Sierra "Agent OS"** | Constellation of 15+ models routed by task; **outcome-based pricing** (charge on resolved outcome) | **Already surfaced today** (the model-seam learning). Outcome pricing → Polo, and it is a pricing decision not an OS feature. Not re-argued |
| **LangGraph / LangSmith** | Checkpoint every super-step → **time travel**: rewind a run, change state, branch. `interrupt` as a durable human-approval pause | **TRIGGER-GATE.** yourco built a time machine for *business metrics* today; it has none for *agent runs*. A loop that fails at 07:55 cannot be rewound and re-run from the failing step — it re-runs whole. Worth it at multi-client scale, not at one |
| **Letta** | **Agent File (.af)** — a portable serialized agent (prompt + memory + tools + config). **Sleep-time compute** — agents reorganise memory while idle. Git-based context repos | **One steal (Idea 2), one validation.** yourco's agents are already git-versioned prose, which is `.af`'s point arrived at differently. Sleep-time compute is genuinely unconsidered |
| **Braintrust / Galileo / Arthur** | Eval-first architecture; **continuous evals on production traffic**; OTel-native; policy mapping to **NIST AI RMF / EU AI Act** | **TRIGGER-GATE + one now.** Continuous eval is right and expensive; weekly is defensible at n=1 client. But **framework mapping is a sales artifact**, not infrastructure — "here is our control set mapped to NIST AI RMF" is the enterprise-buyer answer and it is a document, not a build |
| **Agentic UX consensus (2026)** | Live run view · approval queue · **activity log in plain language, not tool-call names** · confidence indicators · one-tap correction feeding the next run · **always-visible kill switch** | **STEAL — this is the "looks and display" answer.** yourco has the approval gate and the Board; the **client console** has none of these. The kill switch especially: yourco *has* one and the client cannot see it, which wastes the single most reassuring control in the product |

**What NOT to copy, and why it matters more than the steals.** Every platform above is a *tool
vendor* — they sell the layer and hand the buyer the reliability risk. yourco's entire position is
the inverse (`decisions/2026-06-11_no-code-tooling-stance.md`). Copying their **surface** is fine;
copying their **shape** — self-serve, per-seat, buyer-operated — deletes the moat. Munger's line
applies: the moat is not the dashboard, it is that yourco is liable and they are not.

---

## Part 2 — three ideas yourco has not considered

**Idea 1 — Pre-go-live simulation ("prove it before it touches a client").**
*Karpathy (ground-truth evals) · Amodei (gated scaling) · Hassabis-by-extension.* yourco promises a
named employee live in 48 hours and evaluates it **the following Sunday**. Agentforce's Testing
Center injects data states and scores behaviour *before* release. yourco already has the primitive:
`runtime/drills/schema_drift.py` mutates a copy of the CRM and asserts consumers degrade honestly.
Point that harness at a *client* agent with 20 injected states from their real intake, and the
48-hour promise stops being a speed claim and becomes a *tested* one. **Karpathy's objection, kept:**
20 hand-written states is not an eval set, it is a smoke test — call it that.

**Idea 2 — Sleep-time compute on a box that is already paid for.**
*Weng (memory architecture) · Martell (founder-time leverage).* The VPS runs ~20 loops on timers and
is otherwise idle. Letta's insight is that idle time is capacity: agents reorganise memory, compress
context, and pre-compute. yourco's analog is concrete — overnight, the runtime could pre-build every
loop's Step 0 (the `learnings/` read each prompt does at the start), compress `learnings/` domains
that have grown past useful, and pre-warm the CRM insight layer so the morning surfaces are instant.
Cost is near zero because the box is rented either way. **The honest caveat:** the runtime has been
*dark* three times on billing; adding idle spend before fixing liveness is backwards.

**Idea 3 — Agent expiry, not just agent hiring.**
*Bengio (oversight floors) · Willison (attack surface) · Munger (subtraction).* Every agent has an
owner; none has an expiry. Entra's rule is that an agent should not hold access longer than it needs
it. yourco's own audit says 5 of 27 agents have never produced anything and 6 are dormant, and the
walkthrough SOP tells Partner B the roster should probably shrink by a third. `dashboard/vacancies.py`
proposes *hiring* and nothing proposes *retiring* — a one-directional org chart. The smallest version:
every registry entry carries a review date; an agent that has produced nothing by it is proposed for
retirement, exactly as vacancies proposes activation. **This is subtraction, and it is the cheapest
of the three.**

---

## Part 3 — three things nobody has built

Novelty claim is bounded: novel against the platforms researched above and against the agentic-UX
literature as of 2026-08-13. Not a patent search.

**N1 — Trip-wires pointed at the client's decisions.**
yourco shipped decision trip-wires for itself last week: a settled decision carries the evidence that
would overturn it, checked against live data every poll. **Nobody points that at the customer.** A
client OS knows the client's operating decisions — "we quote manually", "we don't take Saturday
jobs", "we don't need a second crew" — and it knows their live numbers. The OS can hold the client's
own stated reasoning and tell them the month it expires: *"in March you decided manual quoting was
fine at 12 quotes a week. You are at 31."* Every CRM reports what happened; none reports **which of
your own past decisions reality has just contradicted.** *Christensen:* the job is not reporting, it
is being told when your model of your business went stale. This is the strongest of the three and it
is a direct extension of code that already exists.

**N2 — A live, machine-derived security model the client can read.**
*Willison's standing rule: publish your security model.* Every AI vendor publishes a trust-centre PDF
written by marketing. Nobody renders the **actual, current** control set: the deny-list read live from
the running config, the autonomy rung of every action, what the last injected prompt-injection drill
did, and the date each control was last tested. yourco can, because those are files:
`runtime/headless-settings.reference.json`, `runtime/autonomy-matrix.md`, `loops/_trust/drills.jsonl`.
A page that says *"this agent cannot send email; here is the config line that prevents it; here is
the injection drill it survived on 8/9"* is unforgeable by a competitor who does not have the
instrumentation — and it converts the moat from a claim into a URL. *Dunford:* this is the proof
asset the positioning has been missing.

**N3 — The client's counterfactual twin.**
yourco's CRM has `ghost` — where every deal would be at your own median velocity. Nobody has pointed
a counterfactual at the *customer's operations* and kept it running. At engagement start the OS
captures the client's pre-engagement baseline; from then on it maintains a shadow model of the
business **as it would be running without the OS**, updated monthly against actuals. That is the
renewal conversation as a live artifact rather than a slide: not "we saved you time," but "here is
your business without us, and here is the gap, computed from your own numbers." *Munger:* the renewal
is the whole margin, and this is the only version of the renewal argument the client cannot argue
with — because it is built from their data, not our claims. **Hardest of the three, and the honest
weakness is that a counterfactual is a model, not a measurement — it must carry that label forever.**

---

## Convergences (3+ reviewers, independent frameworks)

- **CV-E — yourco's instrumentation is now ahead of anything it has sold, and that is a positioning
  failure, not a build failure.** (Dunford · Munger · Christensen.) The Evidence door, the trust
  ledger, drills and trip-wires are genuinely differentiated and **entirely invisible to a buyer**.
  Three of the six ideas above (Idea 1, N1, N2) are the same move: point existing internal
  instrumentation at the client. The build is mostly done; the *aiming* is not.
- **CV-F — every idea here is downstream of capacity, and capacity is one person.** (Martell ·
  Munger · Graham; escalates CV-C.) Six ideas, zero clients, five lock-in domains already slipped.
  The panel's own output is the risk it is warning about.
- **CV-G — subtraction is the only item on this list that costs nothing.** (Munger · Weng ·
  Bengio.) Idea 3 (agent expiry) removes surface area, reduces the eval burden, and makes the roster
  honest. Every other item adds.

---

## Actions

| # | Action | Owner | Smallest version this week | Rating |
|---|---|---|---|---|
| 1 | **Nothing from Parts 2–3 gets built this week.** Record them; the lock-in run is mid-flight and five domains have slipped | the Founder | Read this, pick at most one for after 8/26 | **Now** (as a decision not to build) |
| 2 | **Agent expiry** — add a `reviewBy` to registry entries; the governance watchdog proposes retirement for producers of nothing | Rafi / Kemba | One field + one watchdog rule; no new surface | **Next** |
| 3 | **N2 the security-model page** — the highest ratio of moat-made-visible to build cost, and it reuses the Evidence door's renderers | Webb + Rafi | A static internal render first; nothing external until OtherVenture | **Next** |
| 4 | Pre-go-live simulation (Idea 1) · N1 client trip-wires · N3 counterfactual twin | — | — | **Later** (first client, then pick one) |
| 5 | Sleep-time compute (Idea 2) | — | — | **Park** until runtime liveness is fixed — adding idle spend to a box that has gone dark three times is backwards |

---

## Did the last run change anything?

Yes — materially. `2026-08-13_crm-product-direction.md` produced CV-A/B/C and had **CV-D withdrawn
within hours** when it turned out to have graded the Founder for not selling while the launch-gate forbids
selling. That withdrawal is why this run explicitly scoped itself to platform design and refused to
re-open commercial findings: the prior run already covers them, and the panel's failure mode is
re-litigating the same three points from new angles. Retire test: **not triggered** — this run
produced three convergences and one Now action, all new.
