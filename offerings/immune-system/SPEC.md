# The Immune System — cross-client vaccination (Frontier #8)

**Status:** ARCHITECTING NOW — template hooks only (see `TEMPLATE-HOOKS.md`, the urgent deliverable). Network goes live at client #2.
**Roadmap row:** `offerings/_frontier-roadmap.md` #8 — "One client's caught failure vaccinates every client's OS."
**Owners:** Kolby (pattern review/eval) + Rafi (tenant-isolation controls) + Kemba/platform (template hooks; the Founder holds) + the Founder (publication approval).
**Extends:** `learnings/` (the existing feed-forward substrate, `learnings/_README.md`) + `runtime/consistency-check.py` (the existing invariant backstop). This is NOT a new system — it is the internal closed loop, given a tenant boundary and a review gate.

---

## 1. Concept

When any client's watchdogs catch a failure pattern — a scam wave hitting intake, an integration break (a vendor API silently changing shape), a model regression (a prompt that started drifting after an upgrade), a new social-engineering script — the **anonymized pattern, never the data,** propagates to every other client OS within hours. Client #14's Tuesday-morning scam attempt is client #3's Tuesday-afternoon guardrail. Every client's OS gets stronger every time *any* client's OS is attacked or breaks.

The pitch line: *"You don't just get an AI operations system. You get one with antibodies from every business we protect."* A solo business's defenses are only as good as what it has personally survived; an yourco client's defenses are as good as what the whole network has survived.

## 2. Why this has never been done

- **Agencies don't operate.** A build-and-hand-off shop has no watchdogs running inside client systems, so it never *sees* the failure to learn from it. yourco operates every OS — the watchdogs, evals, and error sweeps are already ours (the per-client production error sweep is activation-gated at go-live; `decisions/2026-07-05_loop-patterns-adoption.md` #4).
- **SaaS vendors see telemetry, not meaning.** They aggregate crash stats; they don't run a reasoning layer that can turn one client's incident into a *behavioral adjustment* another client's agents read at Step 0. yourco's learnings/Step-0 wiring (`runtime/prompts/_loop-contract.md`) is exactly that layer, already live internally.
- **The trust problem kills it elsewhere.** Cross-client learning smells like cross-client data leakage. Doing it safely requires a hard tenant boundary + a human review gate + an audit trail — the moat layer itself. No-code operators can't build that, so they can't offer this.
- **It must predate scale.** Retrofitting a vaccination network across N bespoke deployments loses the network — which is why the hooks go into the golden template BEFORE client #2 exists (roadmap sequencing logic #1).

## 3. Build shape

Three parts, two of which already exist:

1. **Per-client sensing (exists at go-live):** each engagement's watchdogs, eval gates, and the nightly error sweep already produce incident observations into the client's own `learnings/` domain. New: a structured **pattern-candidate** side-channel (`clients/<client>/learnings/pattern-candidates/`) where an observation the sweep flags as *plausibly cross-client* gets written in the anonymized candidate schema (see TEMPLATE-HOOKS §3).
2. **Central review gate (new, small):** candidates land in a central inbox (`learnings/_network/candidates/`). **A human approves every propagation** — Kolby screens for pattern quality + generality, Rafi screens for tenant leakage, the Founder (or the delegated reviewer) approves publication. No auto-spreading of unreviewed patterns, ever: a poisoned or wrong "vaccine" pushed to every client is the network's own worst-case failure mode.
3. **Per-client inoculation (exists as a pattern):** approved patterns publish to `learnings/_network/vaccinations/`, and each client OS carries an inbound `vaccinations/` feed that every client loop reads at **Step 0** — the identical mechanism every internal runtime loop already uses for `learnings/`. Propagation latency = the client's loop cadence (daily loops → "within hours" for anything published before the day's runs; a severity-flagged vaccination can additionally be pushed as an immediate re-run trigger).

Deterministic backstop: `runtime/consistency-check.py` gains invariants that (a) scan `vaccinations/` for tenant-identifying content classes and (b) verify every published vaccination has a matching review record. Same file, same Monday watchdog, new rows — extension, not new machinery.

## 4. Moat fit

- **It IS the moat, networked.** Reliability + eval + observability are per-client moat; the immune system makes them compound *across* clients. Each new client makes every existing client's OS measurably harder to break — a real network effect in an operated-services business, which is close to unheard of.
- **Switching cost with teeth:** leave yourco and you leave the herd immunity. Your standalone agents stop learning from anyone else's incidents the day you churn.
- **Model-upgrade dividend, squared:** upgrades flow to all clients free (CLAUDE.md §moat); vaccinations flow the same way. Two compounding streams no per-seat tool can match.
- **Feeds the Trust Ledger (#1):** "patterns caught network-wide / vaccinations shipped" is proof-surface material once real (counts only, never client detail, never before the numbers exist — no fabricated stats).

## 5. Gates / compliance

- **Tenant isolation is the load-bearing rule** — full statement in `TEMPLATE-HOOKS.md` §4. Short form: names, amounts, content, identifiers, and anything reverse-identifiable may NEVER leave a tenant; only structural patterns in the fixed candidate schema may.
- **Contract language:** the client agreement must disclose and permit anonymized cross-client pattern sharing (and its inbound benefit). Rides counsel gate #1 (legal-suite review, `processes/counsel-gates.md`) — a clause to add to the engagement-agreement package, not a new gate. Until that clause exists in a signed agreement, nothing derived from a client tenant leaves it, even anonymized.
- **Human review gate is non-negotiable** (see §3.2). The review action itself never advances past R1 on the Autonomy Matrix — publication to all clients is high-stakes by definition (`processes/autonomy-matrix.md` hard rule).
- White-label rule unaffected: vaccinations are internal plumbing; no client surface ever names another client or "where a pattern came from."

## 6. Pricing frame

Not a line item at first. The immune system is **included in every operated retainer** — it is part of why the retainer is worth premium pricing ("operated" means defended, and defended means network-defended). Polo owns whether it later becomes (a) a named inclusion used to defend price at renewal, or (b) an explicit tier feature once the network has real scale. What it never becomes: a per-vaccination or per-alert meter — metering defense creates an incentive to under-defend. Bands: `pricing/v0/` (Polo locks; no numbers invented here).

## 7. Activation trigger

- **NOW (no client, no cash):** the template hooks — `TEMPLATE-HOOKS.md` implemented into `clients/_yourco-template/` so client #1's clone (Sample Client, if it signs) is born network-ready. Cost: file structure + schema + two consistency-check invariants. This is the piece that cannot wait, because retrofit loses the network.
- **At client #1 live:** the sensing side runs for real (error sweep writes candidates); the central gate operates in "review + archive" mode — nothing to propagate to yet, but the review muscle and audit trail start honest.
- **At client #2 live:** the network exists. First real propagation = the offering's proof moment; write it up (anonymized) as the case pattern.
- **Contract clause:** blocked on counsel gate #1 before any tenant-derived candidate leaves a client tenant.

## 8. What we will NOT do

- **No auto-propagation.** Unreviewed patterns never spread — an automated wrong vaccine at network scale is worse than any single client incident.
- **No client data leaves a tenant.** Not "minimized," not "hashed" — *none*. Structural pattern or nothing (schema in TEMPLATE-HOOKS §3–4).
- **No cross-client benchmarking product.** "How you compare to other clients" is a data-leakage product wearing a trench coat; parked indefinitely.
- **No marketing the network before it exists.** Pre-client-#2 the external claim is the architecture ("built network-ready"), never implied scale. No fabricated counts.
- **No third-party pattern feed** (buying/selling threat intel). The moat is that OUR watchdogs caught it in OUR operated fleet; imported feeds dilute provenance and add licensing risk.
- **No new runtime for it.** If a piece can't be built as an extension of `learnings/` + Step 0 + `consistency-check.py`, redesign the piece.
