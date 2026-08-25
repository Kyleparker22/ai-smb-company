# Portfolio-report privacy note — Patronage (frontier #13)

> **STAGED — internal until launch (OtherVenture) + this offering's own trigger** (launch). This note is the working rulebook for the report compiler and the sponsor-facing statement of the wall. The wall is enforced **in the compiler**, not by editorial discipline (SPEC §3.2).

## The wall, stated once

The sponsor is often the business's bank or insurer, an entity with underwriting interest in exactly the operational data yourco now sees. So the rule is absolute: the sponsor receives **aggregate, portfolio-level reporting only.** No per-business metrics, no usage or outcome data attributable to a named business, no ranked lists, no "which of my borrowers is struggling," and no answering questions about a named business — in reports, in renewal negotiations, or verbally. Each business's engagement data belongs to that business under its standard agreement. The sponsor's check buys no window into it. One leak ends every future sponsorship and most future client trust.

## The aggregation floor (compiler-enforced)

- **Minimum reporting cohort: 5 sponsored businesses** per reported figure. *(Working value — this is the compiler's config, set before the first report ships; it may only ever be raised. The spec's named failure case is a cohort of three being de-anonymizable.)*
- Any slice below the floor **aggregates up or is omitted.** The compiler never renders it; there is no manual override field.
- Slicing dimensions (industry, geography, module type, cohort month) are checked against the floor **after** slicing. A report on a 25-business portfolio can still produce a 3-business slice; that slice merges upward or drops.
- Cohort sizes are stated on every figure (credibility gate: no aggregate without its n).
- Complementary disclosure is checked: if reporting "12 of 14 activated," the 2-business remainder is itself below the floor but is not attributable to named businesses, so it may stand; any construction that lets the sponsor subtract its way to a named business's row may not.

## What a report contains

Modules live (count), activation rate, aggregate outcome evidence with ledger-backed provenance, aggregate continuation rate post-term, and anonymized pattern notes written so no business is identifiable by description ("a services business in the cohort" only if the cohort holds several; otherwise the note is cut).

## What a report never contains

Per-business rows in any form. Quotes attributable to a business without that business's written consent. Financial or operational detail that would inform underwriting on an identifiable business. Struggle signals of any kind ("some businesses lag" is the maximum resolution, and only above the floor).

## Handling sponsor pressure

Questions about a named business get one answer, every time: "That's [business]'s data, not ours to share — ask them." Escalation, bigger checks, or renewal leverage don't change the answer; a sponsor whose real goal is portfolio surveillance is declined per SPEC §8. Log the exchange on the sponsor's CRM record so the pattern is visible at renewal.
