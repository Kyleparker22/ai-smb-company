# vaccinations/ — INBOUND feed (immune-system hook)

Approved network patterns this OS must absorb — published centrally from `learnings/_network/vaccinations/` after the human review gate (`runtime/immune/README.md`), as `YYYY-MM-DD_slug.md` files carrying the candidate schema plus severity + "what every OS should change."

Every loop for this client reads this folder at **Step 0** (alongside the client's own `learnings/` domain), applies what fits its stack, and records the result in `_applied.md`. Severity `high` triggers immediate re-runs of affected loops; otherwise propagation rides the normal loop cadence. A vaccination that doesn't apply is still recorded — `n/a` + why — so coverage is auditable, not assumed.
