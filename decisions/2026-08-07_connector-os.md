# 2026-08-07 — The Connector OS: yourco's product pointed at its own connectors

## Decision
yourco will build a **Connector OS** — four capabilities no referral program has offered, because each
requires an AI OS, an eval/approval layer, and the give-first doctrine to exist at all. the Founder approved
all four (2026-08-07). Spec: `processes/partnerships/connector-os.md`.

1. **Connectors get agents** — a referral-spotter work tool at join; their own free digital employee
   earned at rung R1.
2. **The glass ledger** — a connector-facing console with an append-only attribution audit log.
3. **The trust ladder** — connectors earn *autonomy* on evidence, mirroring the agent autonomy matrix.
4. **The give-first arsenal** — on-the-spot personalized demo generation, **earned at R1** (the Founder: "it
   has to be earned to get that right").

## The two design calls the Founder raised
- **Console: separate surface, not the CRM.** The CRM shows every connector's book, all deals, margin,
  and internal notes — a connector may see none of it. The console is connector-facing and renders from
  the *same* `buildRepPayouts` / `connector_statements.py` computation, so the ledger and the payout can
  never disagree. Mirrors the existing CRM-internal vs client-console-external split.
- **The arsenal is a rung, not a giveaway** (the Founder's call). It folds into the ladder at R1, which also
  resolves a compliance risk and a cost risk: a generated demo is an external surface carrying yourco's
  brand, and each costs real spend — evidence gates both.

## Why
Every capability here is uncopyable by a competitor with a spreadsheet, and each solves a real defect in
the category: referrers who can't credibly describe the product (→ give them the product), opacity about
what you're owed (→ an audit log), and programs where the only progression is a bigger percentage (→
progression in agency). It is also the cleanest possible dogfood: yourco runs its own partner program on
its own operating philosophy.

## The unplanned compliance win
The ladder's **R2 gate — you may not recruit connectors until you have produced one live, retained
client of your own** — is a classic *active-book qualification*, precisely the kind of **non-depth
guardrail** counsel is now being asked to supply after unlimited override depth was locked
(`decisions/2026-08-07_override-depth-uncapped.md`; checklist item 4b). It strengthens the pyramid
defense at zero cost to the design the Founder wanted.

## Options considered
Build the console *inside* the CRM (rejected — leaks other connectors' books and margin); issue the free
digital employee at signup (rejected — cost across 25 prospective connectors pre-revenue, and value
given for enrolling complicates §A; split into work-tool-at-join + employee-earned-at-R1); ship the
arsenal to everyone (rejected by the Founder — earned).

## Reversibility
High. Every piece is additive and independently switchable; rungs are computed from CRM data, so the
ladder can be re-tuned without migration. The whole program remains counsel- and launch-gated — nothing
is offered to any connector until §A/§B clear.

## Obligations
- **Build order:** attribution log + rung computation first (internal, ungated) → console → spotter →
  arsenal → per-connector employees. Steps 2–5 wait for the gate.
- **Ray:** five new counsel questions logged in the spec — agents-as-benefits, the R2 gate, demo
  liability/apparent authority, connector-data consent, earnings-distribution publication.
- **Charles:** per-connector agent build + run cost enters the cost ledgers; the free-employee tail is a
  real recurring expense to model before R1 connectors exist at scale.
- **Polo:** unchanged pricing; note that the arsenal's demo generation is a CAC line, not a freebie.
