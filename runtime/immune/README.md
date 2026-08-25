# runtime/immune — the immune-system review gate (doc + structure only; no daemon yet)

**What this is:** the central description of how anonymized cross-client pattern candidates become network-wide vaccinations. Source of truth for the design: `offerings/immune-system/TEMPLATE-HOOKS.md` (and `offerings/immune-system/SPEC.md`). The per-tenant hooks ship in `clients/_yourco-template/learnings/` (pattern-candidates outbound queue + vaccinations inbound feed). **Nothing here auto-runs** — when the sweep loop gets built it follows `.claude/skills/add-runtime-loop/` and gets registered in `runtime/agent-registry.json` like every other loop; until then the copy step is manual/session-driven.

## The central structure (repo root, not template)
- `learnings/_network/candidates/` — the review inbox. Candidates arrive here from tenant `pattern-candidates/` queues via the copy sweep, with the tenant tag replaced by an **opaque engagement ID**. This copy is the ONLY path across a tenant boundary, which makes it the natural chokepoint for the machine screen (consistency-check invariants below).
- `learnings/_network/vaccinations/` — the published feed of record: `YYYY-MM-DD_slug.md`, candidate schema + severity + "what every OS should change."
- `learnings/_network/REVIEW-LOG.md` — the gate's append-only audit trail: one row per candidate.

## The review gate — human, R1 permanently
Propagation across clients is **human-approved, always**. This is the `processes/autonomy-matrix.md` "stays gated by design" class: no eval streak, no evidence record, no future promotion ever moves it past R1. A pattern that spreads to every client OS is the highest-blast-radius write in the company; the gate is the product, not overhead.

Three screens, in order, each with a veto:
1. **Kolby — pattern quality.** Real pattern vs one-off; general vs client-specific. Rejects `rejected-not-general` or merges `merged-duplicate`.
2. **Rafi — leakage.** Anything failing the tenant-isolation rules (`clients/_yourco-template/learnings/pattern-candidates/_SCHEMA.md` — identities, amounts, content, reverse-identifiable structure, credentials/config) → `rejected-leakage`, back with reason. Rafi owns the reverse-identifiability judgment; when in doubt, generalize further or reject. Anonymized-at-the-edge does NOT exempt a candidate from this screen — two independent screens; neither trusts the other.
3. **the Founder — publication approval.** Signs the release of every vaccination.

Every candidate gets a disposition row in `REVIEW-LOG.md`: **approved / rejected-leakage / rejected-not-general / merged-duplicate**. Every vaccination must trace to a row; every row to a candidate. No approval, no spread — there is no auto path.

## Publication + propagation
Approved → published to `learnings/_network/vaccinations/` → each live client's loops read their `vaccinations/` feed at Step 0 and record absorption in their `_applied.md` (`n/a` + why when inapplicable). Severity `high` additionally triggers immediate re-runs of affected client loops; otherwise propagation rides normal loop cadence — daily loops mean network-wide absorption within hours, and the `_applied.md` ledgers make that a checkable claim.

## Machine backstop (to add to `runtime/consistency-check.py` per the standing rule)
Deterministic and dumb by design — backstops Rafi, never replaces him:
- **Leak screen:** scan `learnings/_network/candidates/` + `vaccinations/` for `$`-amounts, `@`-emails, phone patterns, active client names (from `clients/` dir listing minus `_yourco-template`), and URLs into client systems → any hit = drift, publication blocked pending human review.
- **Provenance:** every file in `vaccinations/` has a matching `REVIEW-LOG.md` row.
- **Coverage staleness:** any `high` vaccination not acknowledged in every live client's `_applied.md` within its window → drift.

## Hard rules
- No auto-propagation — the human gate is permanent.
- The raw incident never crosses the boundary — evidence pointers resolve only in-tenant.
- **Contract first:** no tenant-derived candidate crosses the boundary until that client's signed agreement carries the cross-client-pattern clause (rides counsel gate #1, `processes/counsel-gates.md`).

**Owners:** Kemba/platform (structure; the Founder holds) · Kolby (candidate quality) · Rafi (isolation) · the Founder (publication).
