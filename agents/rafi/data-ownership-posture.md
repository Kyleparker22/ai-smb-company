# Data ownership — the posture yourco does not yet have written down

**Status: OPEN. This document states the question and the shape of the answer. It does not yet contain
the answer, because the answer must be verified against current provider terms, not recalled.**

Raised 2026-08-24 from Gumloop's *"How enterprises control agentic AI in 2026"* (triaged in
`decisions/2026-07-05_tool-triage.md`). Owner: **Rafi** (compliance) with **Kemba** (platform).

## The question a buyer will ask

Gumloop's guide puts it bluntly to enterprise buyers: *"By working with frontier labs, am I sending my
data directly to an organization that will one day try to crush me with a competitive product?"* Their
recommended mitigations are a model-neutral platform and VPC deployment so inference never leaves the
customer's own environment.

**yourco's honest current position:**
- **Model:** Claude only. Not model-neutral. That is a deliberate quality choice, not an oversight — but
  it means the "swap providers freely" answer is unavailable to us.
- **Where client data sits:** client work runs through yourco's own VPS (Hostinger) and the repo. There
  is no per-client VPC, and no tenant-level data isolation beyond folder separation.
- **Written posture on training / retention:** **none.** Nothing in `processes/`, `01_company.md`, the
  battlecard, or the objections page answers it.

So today the answer gets improvised on the call. That is the gap.

## What has to be established before anything is written or said

Each of these is a **verify-at-source** task. Do not assert any of it from memory or from a summary —
provider terms change, and a confident wrong answer here is a trust event, not a rounding error.

1. **What the API provider's terms actually say** about training on API inputs, retention windows, and
   whether a zero-data-retention arrangement is available at yourco's tier. Read the current terms and
   cite the clause and the date read.
2. **What yourco itself retains** — repo contents, run journal, cost ledger, Slack, Gmail drafts — and
   for how long. This is knowable today by reading our own stores; nobody has written it down.
3. **Where it physically sits** — the VPS region, the repo remote, and any connector that egresses data.
4. **What a client can demand** — deletion, export, and what happens to their data at churn. The MSA /
   proposal-SOW language should match whatever we answer here.
5. **The distinction Gumloop draws and we have not**: a vendor may promise not to *train* on data while
   reserving the right to *retain* it for quality assurance. Those are different promises. Say which one
   we are actually making, and which one our provider makes to us.

## The shape of the answer (to be filled, not assumed)

A one-page, plain answer covering: what leaves the client's systems · who processes it · what is retained
and for how long · what is never used for training · what happens at churn · what we will not claim.
It belongs in the objections page and the battlecard once verified, and in the MSA once counsel reviews.

**Do not market a security claim we have not verified.** Under the no-fabricated-proof rule, an unverified
data-handling assurance is the highest-cost sentence yourco could put in front of a buyer — it is the one
a client's counsel will test. Counsel-gate this before any external use (`processes/counsel-gates.md`).

## Scope note — this is an SMB gap of a particular size

yourco sells to SMBs, most of whom will never ask. It matters anyway for three reasons: the first
sophisticated buyer *will* ask; Sample Product and Conduit both touch sensitive data (Conduit is heavy
PII by design); and the answer takes a day to establish and is permanently reusable. **This is a
one-page written answer, not a re-architecture** — resist letting it become a VPC project.
