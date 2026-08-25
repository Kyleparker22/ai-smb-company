# pattern-candidates — candidate schema + tenant-isolation rules

**Source of truth:** `offerings/immune-system/TEMPLATE-HOOKS.md` §3–§4, carried here verbatim so every tenant holds its own rules. Filename convention: `YYYY-MM-DD_short-slug.md`, one candidate per file. Candidates written here are **already anonymized at the edge** — a candidate that needs redaction later was written wrong.

## Candidate schema (structure only — this IS the anonymization)

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

## Tenant-isolation rules (what may NEVER leave a tenant)

Never, in any field, under any severity, including "just this once for clarity":
- **Identities** — client name, staff, customers, counterparties, vendors-as-used-by-this-client; emails, phones, handles, addresses, account IDs.
- **Amounts** — dollar figures, prices, invoice/quote values, volumes, revenue, anything financially descriptive of the client.
- **Content** — quoted emails/messages/documents/transcripts, attachments, screenshots, prompts containing client data, URLs into client systems.
- **Reverse-identifiable structure** — combinations that fingerprint the client (vertical + region + week + integration set). Rafi's screen owns this judgment; when in doubt, generalize further or reject.
- **Credentials/config** — keys, endpoints, tenant IDs, anything operational about the client's stack beyond the generic integration class ("a field-service CRM webhook", not the instance).

What MAY leave: the structural pattern — trigger shape, failure mode, detection signature, fix — exactly the schema fields above. Test: *could this candidate have been written, word for word, about a different client hit by the same pattern?* If no, it leaks.
