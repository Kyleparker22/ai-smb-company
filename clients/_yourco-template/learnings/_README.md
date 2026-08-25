# learnings/ — this client's learnings domain (immune-system hooks)

**What this is:** the per-client mirror of the internal substrate (`learnings/_README.md` at repo root — same entry format, same Step 0 discipline, same lifecycle). Everything here is **client-scoped**: patterns observed operating *this* client's OS, read by *this* client's loops at Step 0.

**Plus the two network hooks** (`offerings/immune-system/TEMPLATE-HOOKS.md` — the install source of truth):
- `pattern-candidates/` — **OUTBOUND queue.** Anonymized-at-the-edge candidates awaiting central review. Schema + tenant-isolation rules: `pattern-candidates/_SCHEMA.md`. The raw incident never leaves the tenant — only the structural pattern does, and only after human review.
- `vaccinations/` — **INBOUND feed.** Approved network patterns this OS must absorb. Application ledger: `vaccinations/_applied.md`.

## Wiring rule
Every loop prompt for this client (error sweep, watchdogs, any engagement loop) names **two** Step-0 sources in its footer — this `learnings/` domain AND `vaccinations/` — via the same loop-contract mechanism every internal loop follows (`runtime/prompts/_loop-contract.md`). A vaccination counts as absorbed only when the loop lists it under "Learnings applied this run" and the behavior change lands (guardrail row, eval case, prompt adjustment).

## The flow (sense → review → inoculate)
1. **Sense (in-tenant):** a watchdog / error sweep / eval run spots a plausibly cross-client failure pattern → writes a normal client learning here AND, separately, a candidate to `pattern-candidates/`, already anonymized per `_SCHEMA.md`.
2. **Queue:** a runtime sweep copies new candidates to `learnings/_network/candidates/` (repo root) with the tenant tag replaced by an opaque engagement ID — the ONLY path across the tenant boundary.
3. **Review (human, R1 forever):** Kolby (pattern quality) · Rafi (leakage) · the Founder (publication). Gate doc: `runtime/immune/README.md`. No approval, no spread — there is no auto path.
4. **Publish:** approved patterns land in `learnings/_network/vaccinations/` and flow into every client's `vaccinations/` feed.
5. **Inoculate:** this client's loops read `vaccinations/` at Step 0, apply what fits, record it in `vaccinations/_applied.md` (`n/a` + why when it doesn't apply — coverage is auditable, not assumed).

## Hard rules (carried by the template)
- No auto-propagation — the human gate is permanent (R1 by design; `processes/autonomy-matrix.md` "stays gated by design" class).
- Anonymize at the edge AND re-screen at the gate — two independent screens; neither trusts the other.
- The raw incident never crosses the boundary — evidence pointers resolve only in-tenant.
- Contract first: no tenant-derived candidate crosses the boundary until the cross-client-pattern clause is in this client's signed agreement (rides counsel gate #1, `processes/counsel-gates.md`).
- Fold-back rule: improvements discovered here go back to `_yourco-template` (Kemba), never forked per client.
