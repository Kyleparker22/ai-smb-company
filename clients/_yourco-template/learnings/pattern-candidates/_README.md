# pattern-candidates/ — OUTBOUND queue (immune-system hook)

Anonymized cross-client pattern candidates awaiting central review. Written by this client's watchdogs / error sweeps / eval runs when a failure pattern looks plausibly cross-client (scam wave, integration break, model regression, guardrail near-miss). Format + isolation rules: `_SCHEMA.md` in this folder — **anonymize at the edge; the raw incident stays in the tenant** (it goes in the normal client learning, not here).

A runtime sweep copies new candidates to `learnings/_network/candidates/` for the human review gate (Kolby → Rafi → the Founder; `runtime/immune/README.md`). No approval, no spread. Empty pre-go-live is expected.
