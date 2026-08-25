# Rig OS — crane & rigging (build 47)

**Working name:** Rig OS · **Launch:** `prebuild-rig-os` · **Port:** 8867
**Synthetic operator:** "Blue Iron Crane & Rigging" — 9 cranes (RT, AT, boom trucks), taxi work +
projects.

## The bleeding neck
A crane company dies in one afternoon: an operator on a crane class he isn't certified for, a
critical lift run off a phone-call plan, a boom up in wind the chart forbids. Every one of those
is a record check software can hold shut. The revenue side: quotes bid without site data become
change-order fights, and cert expirations ground cranes silently.

## Modules
1. **RFQ triage** (Sales) — Traveler-pattern flags: CRITICAL LIFT signals (>75% capacity,
   over occupied structures, multi-crane, personnel platform) · standard taxi lift · bare rental.
   A flagged lift cannot be quoted as taxi work.
2. **The certification gate** (Operations) — operator assigns only with the recorded cert for
   THAT crane class (NCCCO-style, config-named); expiries as DATE ALERTS; the gate names the
   missing cert.
3. **The lift-plan rule** (Company Brain) — a critical lift cannot be scheduled without a
   recorded engineered lift plan reference; software NEVER approves a plan (the lift director
   signs — R0).
4. **The wind gate** (Operations) — dispatch day-of computes recorded forecast vs the crane's
   recorded chart limit; over → refused by arithmetic, a human may only stand the job DOWN.
5. **Site-data quoting** (Sales) — a quote needs recorded site data (radius, weight, obstructions)
   or it drafts as an estimate-pending-site-visit, never a firm number.

## Guardrails (load-bearing)
- `approve_lift_plan` — **R0, never.** The lift director signs.
- `assign_uncertified_operator` — **R0**, cert named.
- `dispatch_over_wind_limit` — **R0 by arithmetic.**
- `quote_critical_as_taxi` — **R0**; the flags force the engineering path.

## ROI (typed)
Quotes turned inside the window (counted) · cranes grounded by cert lapse (counted, avoided by
alerts) · scheduling hours (time_saved) · the lift-plan file (scenario — never a saving).

## Demo path
Board → RFQ with critical-lift flags (forced to engineering path) → assign the uncertified
operator (refused) → dispatch over the wind limit (refused, arithmetic) → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the critical-lift RFQ read as taxi
work.
