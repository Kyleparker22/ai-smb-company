# See it Work — agents by type, not names/verticals (2026-06-23)

> **Owner: Webb.** Reworked `demos.html` per the Founder: the demos should show **agent types**, not named or vertical-specific employees. Consistent with the function-only-naming direction (agents are internal-named; external = function) and the horizontal positioning (no per-trade framing). Committed with the site push; staged/internal.

## What changed
- **Replaced the 12 named, vertical-specific employees** (Sage/landscaping, Remy/dental, …) with **10 agents identified by type** — no names, no verticals:
  **Receptionist · Lead Responder · Booker · Quote Follow-up · Support · Knowledge Q&A · Reputation · Dispatcher · Billing & AR · Safety-Gated Intake.**
- Each still **plays in action** (the text-thread demo): the phone header shows the *type* + a neutral scenario ("a missed call, after hours"); the panel shows what the type does; the conversations are vertical-neutral but still concrete.
- The picker chips now show **icon + type** (single line), not name + vertical.
- Each demo is chosen to surface a distinct moat point: instant reply, speed-to-lead, no-show reduction (deposit + reminder), quote persistence, the **approval gate** (refund → human), the **honesty gate** (Q&A admits "I don't know"), review-timing + complaint routing, urgency triage, **approval-gated billing**, and the **safety guardrail** (never gives medical/legal/financial advice → escalates).
- Copy: hero → "See the agents in action." / "Ten of the agents we build…"; CTA → "These are individual agents. Your AI OS runs them together."; meta description de-verticalized.

## Verification
10 type chips render; default (Receptionist) renders; full play tested (6 bubbles + 2 callouts + system line + closer); **0 console errors**; no residual names/verticals in body text.

## Note
The data object was renamed `EMPLOYEES → AGENTS`; the phone/play engine is unchanged. Vertical-specific *scenarios* were genericized but remain illustrative (a concrete exchange per type), not trade offerings.
