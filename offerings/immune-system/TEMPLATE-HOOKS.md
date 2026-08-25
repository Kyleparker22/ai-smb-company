# Immune System — golden-template hooks (build BEFORE client #2)

**What this is:** the exact hooks `clients/_yourco-template/` needs so every engagement is born network-ready. This is the urgent deliverable of `offerings/immune-system/SPEC.md` — the network is cheap to build into the template now and expensive-to-impossible to retrofit across bespoke deployments later. Everything here extends machinery that already runs: `learnings/` + Step 0 (`runtime/prompts/_loop-contract.md`) + `runtime/consistency-check.py`. No new runtime.

**Owners:** Kemba/platform (template edits; the Founder holds) · Kolby (candidate quality) · Rafi (isolation rules) · the Founder (publication approval).

---

## 1. Template additions (the file structure)

Add to `clients/_yourco-template/`:

```
learnings/                      # per-client learnings domain (mirror of the internal substrate)
  _README.md                    # points at learnings/_README.md conventions; client-scoped
  pattern-candidates/           # OUTBOUND queue — anonymized candidates awaiting central review
    _SCHEMA.md                  # the candidate format (§3) + the isolation rules (§4), verbatim
  vaccinations/                 # INBOUND feed — approved network patterns this OS must absorb
    _applied.md                 # per-client application ledger (§5)
```

And centrally (repo, not template): `learnings/_network/` with `candidates/` (review inbox), `vaccinations/` (the published feed of record), `REVIEW-LOG.md` (audit trail, §5).

Wiring rule: every client loop prompt (error sweep, watchdogs, any engagement loop) names **two** Step-0 sources in its footer — its own `learnings/` domain AND `vaccinations/` — via the same loop-contract mechanism every internal loop already follows. A vaccination is "absorbed" when the loop lists it under "Learnings applied this run" and the behavior change lands (guardrail row, eval case, prompt adjustment).

## 2. The flow (sense → review → inoculate)

1. **Sense (in-tenant):** a client watchdog / error sweep / eval run observes a failure pattern it judges plausibly cross-client (scam wave, integration break, model regression, guardrail near-miss). It writes a normal client learning AND — separately — a candidate to `pattern-candidates/`, **already anonymized at the edge** per §3/§4. The candidate never contains the raw incident; the raw incident stays in the tenant.
2. **Queue (cross-boundary, mechanical):** a runtime sweep copies new candidates to `learnings/_network/candidates/` with tenant tag replaced by an opaque engagement ID. This copy step is the ONLY path across the tenant boundary, so it is the natural chokepoint for the machine screen (§6).
3. **Review (human, R1 forever):** Kolby screens for pattern quality (real pattern vs one-off; general vs client-specific), Rafi screens for leakage (anything failing §4 → rejected back with reason), the Founder approves publication. Every candidate gets a disposition in `REVIEW-LOG.md`: **approved / rejected-leakage / rejected-not-general / merged-duplicate**. No approval, no spread — there is no auto path.
4. **Publish:** approved pattern lands in `learnings/_network/vaccinations/` as `YYYY-MM-DD_slug.md` (schema §3, plus severity + "what every OS should change"). Severity `high` additionally triggers immediate re-runs of affected client loops; otherwise propagation rides the normal loop cadence — daily loops mean network-wide absorption within hours.
5. **Inoculate (in-tenant):** each client's loops read `vaccinations/` at Step 0, apply what fits their stack, and record it in `vaccinations/_applied.md`. A vaccination that doesn't apply (client lacks the integration) is recorded as `n/a` — explicit, so coverage is auditable, not assumed.

## 3. Candidate schema (structure only — this IS the anonymization)

```
YYYY-MM-DD — [pattern title, no client detail]

Engagement: [opaque ID assigned centrally — never the client name in the candidate body]
Class:       scam-wave | integration-break | model-regression | guardrail-gap | data-quality | other
Trigger:     [structural description of what arrives/happens — channel + shape, no content]
Failure:     [what the OS did wrong or nearly did — behavioral, no artifacts]
Detection:   [which control caught it — watchdog rule / eval case / human catch — and the generalizable signature]
Fix:         [the guardrail/eval/prompt change that closes it, stated so any OS can apply it]
Severity:    high | medium | low   [high = active exploitation or money/reputation path]
Evidence:    [in-tenant pointer(s) — resolvable only inside the source tenant, opaque outside it]
```

The schema is the isolation mechanism, not just a format: every field is defined so that a correctly-filled candidate **cannot** carry payload. If filling a field honestly seems to require a name, an amount, or quoted content, the candidate is describing an incident, not a pattern — rewrite or don't submit.

## 4. Tenant-isolation rules (what may NEVER leave a tenant)

Never, in any field, under any severity, including "just this once for clarity":
- **Identities** — client name, staff, customers, counterparties, vendors-as-used-by-this-client; emails, phones, handles, addresses, account IDs.
- **Amounts** — dollar figures, prices, invoice/quote values, volumes, revenue, anything financially descriptive of the client.
- **Content** — quoted emails/messages/documents/transcripts, attachments, screenshots, prompts containing client data, URLs into client systems.
- **Reverse-identifiable structure** — combinations that fingerprint the client (vertical + region + week + integration set). Rafi's screen owns this judgment; when in doubt, generalize further or reject.
- **Credentials/config** — keys, endpoints, tenant IDs, anything operational about the client's stack beyond the generic integration class ("a field-service CRM webhook", not the instance).

What MAY leave: the structural pattern — trigger shape, failure mode, detection signature, fix — exactly the §3 fields. Test: *could this candidate have been written, word for word, about a different client hit by the same pattern?* If no, it leaks.

## 5. Audit trail

Three ledgers, all append-only, all git-tracked (git history = tamper evidence):
- **Source:** the candidate file in the tenant's `pattern-candidates/` (with its in-tenant evidence pointers).
- **Gate:** `learnings/_network/REVIEW-LOG.md` — one row per candidate: date · opaque ID · disposition · reviewers · published-as. Every vaccination must trace to a row; every row to a candidate.
- **Application:** each tenant's `vaccinations/_applied.md` — vaccination ID · date absorbed · what changed (or `n/a` + why). This is what makes "every client protected within hours" a checkable claim instead of a slogan — and later, Trust-Ledger material (counts only).

## 6. Machine backstop (consistency-check invariants — add per the standing rule)

Extend `runtime/consistency-check.py` (new numbered checks, same report):
- **Leak screen:** scan `learnings/_network/candidates/` + `vaccinations/` for `$`-amounts, `@`-emails, phone patterns, active client names (from `clients/` dir listing minus `_yourco-template`), and URLs into client systems → any hit = drift, publication blocked pending human review. Deterministic and dumb by design — it backstops Rafi, never replaces him.
- **Provenance:** every file in `vaccinations/` has a matching `REVIEW-LOG.md` row (no unreviewed publication can survive a Monday unnoticed).
- **Coverage staleness:** any `high`-severity vaccination not acknowledged in every live client's `_applied.md` within its window → drift.

## 7. Hard rules (restated so the template carries them)

- **No auto-propagation** — the human gate is permanent (R1 by design; `processes/autonomy-matrix.md` "stays gated by design" class).
- **Anonymize at the edge AND re-screen at the gate** — two independent screens; neither trusts the other.
- **The raw incident never crosses the boundary** — evidence pointers resolve only in-tenant.
- **Contract first:** no tenant-derived candidate crosses the boundary until the cross-client-pattern clause is in that client's signed agreement (rides counsel gate #1, `processes/counsel-gates.md`).
- **Fold-back rule:** like every template part, improvements discovered per-engagement get folded back here (Kemba), never forked per client.
