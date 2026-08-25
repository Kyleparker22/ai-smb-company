# 2026-06-07 — Finance loop handed from Atlas to Charles

## Decision
Build **Charles** as YourCo's Finance Agent and hand him ownership of the finance loop (`processes/loops/finance.md`), the four `/finance/` ledgers, and the monthly close. Atlas stays the observability layer and *reads* Charles's finance artifact for the Monday briefing — it no longer owns the finance loop.

## Context
The finance loop ran once under Atlas (`loops/finance/2026-06-07.md`) and the ledgers were created the same morning. With the agent roster defined, finance is the lowest-risk live build: the SOP, ledgers, and a real artifact already exist, so "building Charles" is mostly formalizing ownership + a finance-specific eval set. Doing this also keeps Atlas from drifting into a do-everything monolith.

## Options considered
- **Leave finance under Atlas** — simplest, but bloats Atlas and blurs the observe-vs-own line we just drew in the operating-model decision. Rejected.
- **Build Charles now (chosen)** — formalize a named owner; Atlas reverts to pure observer/reader.

## Why
- **Keeps Atlas observability-only**, consistent with `2026-06-07_agent-operating-model.md` (siblings, the Founder conducts; Atlas observes, doesn't direct).
- **Lowest-risk first specialist build** — substrate already exists; fast proof of the "hand a loop to a named agent" pattern.
- **System-of-record clarity** — one owner for the books; `token_spend.md` is Charles's ledger, which Atlas references for cost monitoring.
- **Reuse payoff** — the finance/bookkeeping module is a strong future `yourco-template` chunk and a plausible client-facing finance digital employee later.

## Boundaries set
- **Charles owns the books** (ledgers, pulse, close, readout, tax-prep drafts). **Atlas observes** (reads the artifact, cost rollup, briefing).
- **Charles is read/report/draft only.** Any invoice send, payment, or tax filing is human-must-approve.

## Reversibility
Fully reversible — ownership can revert to Atlas by reverting the SOP header. The harder-to-reverse step (real bank/QuickBooks integration) is explicitly deferred to v1 per `finance/README.md` graduation triggers.

## Follow-ups
- Point the existing finance scheduled task at Charles's identity/SOP (currently signs as Atlas; convention only, non-blocking).
- Provision `contact@yourco.example.com`.
- the Founder to set cash-on-hand in `runway.md` so runway computes.
