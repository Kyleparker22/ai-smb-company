# ledger — JSONL record schema (verbatim from `offerings/self-proving-invoice/SPEC.md` §3.1)

Append-only JSONL, one file per month (`ledger/YYYY-MM.jsonl`), written by the same hooks that run the moat layer. Every line is a single JSON object with a `record_type` field naming one of the five types below, plus the fields defined for that type. IDs are unique within the engagement; `ts` is ISO-8601 with timezone.

## The five record types

```
action_record   {id, ts, module, pillar, action_type, autonomy_tier,      -- R0–R3 at time of firing
                 outcome_class,            -- completed | approved+sent | escalated | rolled_back
                 approval {approver, ts} | null, eval_ref | null, links[]}
eval_record     {id, ts, module, gate_name, result,                        -- pass | fail
                 sample_size, notes, action_ids[]}
incident_record {id, ts, severity, module, what_happened, caught_by,      -- watchdog|eval|human|client
                 impact, remediation, resolved_ts}                         -- written even when impact = none
outcome_record  {id, ts, outcome_name,                                     -- the audit-scoped outcomes this engagement exists to deliver
                 metric {name, value, source, period} | qualitative_note,
                 evidence_links[]}
autonomy_event  {id, ts, module, action_type, from_tier, to_tier,
                 evidence: streak_summary, approved_by}
```

## Example lines (illustrative shape, not real data)

```jsonl
{"record_type":"action_record","id":"a-2026-09-0001","ts":"2026-09-03T14:12:09-04:00","module":"intake","pillar":"Intake","action_type":"draft_reply","autonomy_tier":"R1","outcome_class":"approved+sent","approval":{"approver":"[[CLIENT APPROVER]]","ts":"2026-09-03T14:40:02-04:00"},"eval_ref":"e-2026-09-0002","links":["audit-trail/..."]}
{"record_type":"eval_record","id":"e-2026-09-0002","ts":"2026-09-03T14:12:11-04:00","module":"intake","gate_name":"reply-accuracy","result":"pass","sample_size":25,"notes":"","action_ids":["a-2026-09-0001"]}
{"record_type":"incident_record","id":"i-2026-09-0001","ts":"2026-09-10T09:02:44-04:00","severity":"low","module":"scheduling","what_happened":"calendar webhook retried 3x before success","caught_by":"watchdog","impact":"none","remediation":"retry budget raised; eval case added","resolved_ts":"2026-09-10T09:31:00-04:00"}
{"record_type":"outcome_record","id":"o-2026-09-0001","ts":"2026-09-30T17:00:00-04:00","outcome_name":"[[AUDIT-SCOPED OUTCOME]]","metric":{"name":"[[metric]]","value":0,"source":"[[client system / count / qualitative+label]]","period":"2026-09"},"evidence_links":[]}
{"record_type":"autonomy_event","id":"au-2026-09-0001","ts":"2026-09-21T08:00:00-04:00","module":"intake","action_type":"draft_reply","from_tier":"R1","to_tier":"R2","evidence":"streak_summary: 40/40 approved unmodified over 21 days","approved_by":"the Founder"}
```

## Rules restated at the schema level
- **Append-only:** a correction is a new record whose `notes`/body references the superseded `id` — never an edit or delete.
- **`incident_record` is written even when impact = none** — the absence-of-incidents claim on the invoice depends on this plus the watchdog heartbeat.
- **`outcome_record.metric.source` is required** for any numeric metric; qualitative outcomes use `qualitative_note` and render labeled as qualitative.
- **`autonomy_tier` is the tier at time of firing**, not current — history must read true.
