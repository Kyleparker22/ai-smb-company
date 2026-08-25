# Sample Client: one platform — Design Studio is the client view, Field-to-Quote is the engine

**Date:** 2026-08-07 · **Decided by:** the Founder

## Decision
The Same-Day Design Studio and the Field-to-Quote platform are one product: a single platform (`clients/sample-client/platform/`, :8804) whose internal tabs are the engine (measurements, 2D board, quote, scope, approvals, catalog) and whose **Design Studio tab is the client-facing presentation view** — client-safe by construction. The standalone Design Studio page (:8799) retires to sales-demo artifact status; "Same-Day Design Studio" survives as the client-facing brand name, "Field-to-Quote" as the internal engine name.

## Context
Both were built separately: the Design Studio page (July) as the cinematic pitch of the concept on the Donovan Pl backyard; the Field-to-Quote platform (2026-08-07, from the 8/6 meeting spec) as the working tool. the Founder asked whether they're the same thing and chose immediate merge over keeping them parallel.

## Options considered
1. Keep separate until v2 (demo each as its own surface at next week's walkthrough) — safer for the deadline, but cements a split that isn't real.
2. **Merge now (chosen):** the platform gains a Design Studio client view rendering only client-safe data (renders, plan, tier prices, ballpark range, scopes) from the same project state; photos/renders upload into the project; "Present full screen" mode for on-site/in-office presentation.

## Why
One project record, two audiences — the render the homeowner falls in love with and the line items Colton prices must never drift apart, and a single data model is the only way to guarantee that. It also matches the meeting's sales motion: rep presents on-site from the same tool the office quotes from. The client/internal boundary is enforced in the compiler-not-policy way (the client renderer simply has no access paths to cost/margin/labor/flags), which is the moat pattern.

## Reversibility
Low stakes to revisit: the :8799 page still exists untouched as the marketing narrative. If a fully separate homeowner-facing web product is ever needed (e.g. a link clients open at home), it forks from the client-view renderer — the boundary is already drawn in code.

## Guardrail carried forward
The client view must NEVER render: costs, margins, crew-days, difficulty multipliers, approval flags, supplier pricing, or field-verify warnings. Any future feature lands on the internal side by default and is explicitly promoted to the client view.
