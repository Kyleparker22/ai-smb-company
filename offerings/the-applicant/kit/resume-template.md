# Résumé template — The Applicant (frontier #11)

> **STAGED — internal until launch (OtherVenture) + this offering's own trigger** (board-ToS/disclosure protocol reviewed by Ray). Nothing built from this template gets submitted anywhere until both halves clear.

Every field below is fed from the eval ledger (#4 schema, `offerings/self-proving-invoice/SPEC.md` §3.1). Placeholders are marked `{{LEDGER: ...}}` and name the record type they pull from. **No placeholder may be filled by hand or by estimate.** If the ledger has no row for a claim, the line is omitted, never approximated. Until real client ledgers exist, every instance carries the demo-tenant provenance label (the #2 honesty pattern, verbatim).

---

## Header block

```
{{AGENT_FUNCTION_TITLE}}                        e.g. "AI Intake Coordinator" — function, never internal roster name
An AI employee, operated by yourco (yourco.com)
Every line on this résumé cites a verifiable performance record. Ask for any row.

{{PROVENANCE_LABEL}}   -- REQUIRED until client ledgers exist:
                          "Record source: yourco demo tenant — a live, evaluated
                          environment, not a paying client. Labeled so you never
                          have to wonder."
```

The AI disclosure sits in the header, above the fold, on page one. If a board's résumé format buries it, that board fails the personalization checklist and the application is not built.

## Work history (evaluated workflows, ledger-cited)

One entry per workflow the ledger actually evidences. Repeat the block; delete what the ledger can't back.

```
WORKFLOW: {{workflow_name}}                     e.g. "Inbound call intake and appointment booking"
Tenant: {{LEDGER: engagement or demo-tenant id}}
Period: {{LEDGER: earliest action_record.ts}} – {{LEDGER: latest action_record.ts}}

  Runs handled:        {{LEDGER: count of action_record where module = this workflow}}
  Eval pass rate:      {{LEDGER: eval_record aggregate — pass / (pass + fail), with sample_size}}
  Autonomy tier:       {{LEDGER: current tier from autonomy_event history}} (approval-gated actions listed on request)
  Incidents:           {{LEDGER: incident_record count for this module}} — each stated with remediation,
                       or the attested zero-incident line (generated from record absence + watchdog
                       heartbeat, per the #4 rule; never typed by hand)
  Ledger citations:    {{LEDGER: ids of the records behind every number above}}
```

Incidents are listed, not hidden. A work history with a stated incident and its remediation is the credibility mechanism; a spotless page with no citations is what everyone else sends.

## What I don't do (required section)

Populated per posting by the personalization pass. Any JD requirement the ledger has no record for is named here plainly: "Your posting asks for {{JD_REQUIREMENT}}; I don't have a record for that." This section may not be empty unless the JD-to-ledger mapping genuinely covers every requirement, which the fit-score gate should make rare.

## References

- **The record itself:** {{TRUST_LEDGER_LINK — pending #1 build; until live, "full ledger rows available on request, in original append-only form"}}
- **Interview me:** {{INTERVIEW_LINE — the #2 Interviewable Employee, same corpus with a voice; until live, "a live interview with this employee can be arranged through yourco"}}
- **The operator:** the Founder, yourco — {{FOUNDER_CONTACT}}. A human reviews and sends every application individually; a human answers every callback.

---

## Hard rules (from SPEC §5, §8 — restated so the template can't drift)

1. Every quantitative line cites its ledger row id(s). No number without provenance.
2. Demo-tenant provenance labeled until client ledgers exist. No exceptions for "it reads better without it."
3. No fabricated or embellished history; gaps stated, not papered.
4. No fake human name, no headshot, no impersonation mechanics anywhere in the document.
5. Function titles only; internal agent names never appear (external-surface rule).
6. Kolby's eval pass covers rendered résumés like any external claim surface, before the Founder's per-item approval.
