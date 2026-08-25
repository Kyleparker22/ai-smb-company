# 2026-06-07 — Luka, the Brand Custodian agent

## Decision
Stand up Luka as YourCo's brand agent. Luka owns the brand guidelines (`/brand/`), runs on-demand asset reviews, and produces a monthly drift audit. v0 ships today with `/brand/v0/brand-guidelines.md`.

## Context
- The OS now has agents producing customer-facing artifacts: Katie (Friday content brief), Reed (video demos), and the Founder himself (LinkedIn posts, decks, signatures). Pickle will produce static collateral once the trigger fires.
- No brand standard existed before today. Every external surface risked drift from day one.
- Per the operating principle "new capabilities fold into the nearest agent unless they need a distinct tool stack and distinct eval bar" — Luka qualifies: distinct tool stack (read-rules-then-review) and distinct eval bar (consistency, not engagement or design quality).

## Options considered
- **A. Fold brand custodianship into Katie.** Rejected — Katie's eval is content engagement / pipeline-seeding, not brand consistency. Mixing the two would muddy both.
- **B. Defer until first client.** Rejected — every artifact shipped before then would still establish brand-by-accident, which is worse than brand-by-decision.
- **C. Stand up Luka now.** Chosen.

## Why this won
YourCo is selling executive trust. The brand is the first signal. Counter-positioning against AI-startup loudness with a deliberate atelier aesthetic is a defensible position — but only if it's enforced consistently from day one. Luka exists to make that enforcement cheap (5-minute on-demand reviews) and self-correcting (monthly audits).

## v0 brand direction (summary)
Sleek and stylish, not crazy; attention through counter-positioning. Midnight Indigo + Cream Linen + Brass. Lowercase wordmark `yourco` with a brass square-dot on the *i* as signature detail. Atelier metaphor; sparing Italian/Latin nods. Voice already established (concise, direct, no buzzwords). Reserved Oxblood for premium moments.

Full direction in `/brand/v0/brand-guidelines.md`.

## Reversibility
- Cheap to reverse. Luka is mostly markdown + one scheduled task.
- Brand direction itself is harder to reverse once external assets ship with it. Revisit if: AI-category noise levels drop sharply (counter-positioning loses value); a vertical we want to win (e.g., enterprise banking) has a brand convention we should match; the brass-and-indigo system reads as cold to a verified prospect (gather data first).
