# 2026-07-20 — Advisory panel: simulated expert review as a skill + Brett quarterly duty

## Decision
The "virtual review panel" (named AI + business minds channeled against yourco's current state)
becomes a **standing capability**: a skill (`.claude/skills/advisory-panel/`) invocable **on-demand
before major decisions** (the higher-value mode), plus a **quarterly full-panel run owned by Brett**
(first Friday of Jan/Apr/Jul/Oct, inside his existing ideas loop — no new timer, no new agent).
**Not monthly.**

## Context
the Founder ran the exercise twice in one session (AI-minds panel, then sales/business-minds panel) and
both produced genuinely action-shaped output — the Client Owner re-approach (Voss/Challenger), the
paid-audit-always rule, the autonomy novelty axis, the moat-backed guarantee, the scaffold audit.
He asked: build it as a one-off, or a monthly agent responsibility?

## Options considered
- **Monthly loop** — rejected: strategy state changes slower than ops state; by run #2–3 a monthly
  panel rediscovers the same findings ("sign the client, raise prices, open the funnel") and decays
  into skimmed noise. Also duplicates Brett's weekly ideas loop and the periodic five-reviewer OS
  audit (`loops/_audit/`).
- **One-off (don't systematize)** — rejected: the procedure took real derivation (panel selection by
  decision type, framework grounding, diff contract, convergence-only reporting) and will recur —
  the exact skills-discipline test.
- **Skill + quarterly Brett duty + on-demand** — chosen. On-demand runs are event-driven (a real
  decision at stake = fresh input = non-generic output); quarterly gives a floor; Brett is the
  natural owner (advisory-only role, already runs a four-lens persona engine — Levels/Graham/Thiel/
  Balaji — this is that machinery scaled up).

## The binding rules (in the skill; the two that are policy, not procedure)
1. **Diff contract:** every run reads the prior `loops/_advisory/` artifact first and may only
   report new/escalated/resolved/reversed findings. Restating standing findings = violation.
2. **Internal-only, hard rule:** simulated perspectives from public frameworks are a *thinking
   tool*. No external surface (site, proposal, post, deck) may ever state or imply these people
   reviewed, endorsed, or advised yourco — that is fabricated endorsement. Added to CLAUDE.md's
   external-surface rules in this change.

Retire test: two consecutive runs that change no decision → Brett recommends retiring or
re-rostering the panel.

## Artifacts
- Skill: `.claude/skills/advisory-panel/SKILL.md` (+ index line in `_README.md`)
- Baseline artifact (the founding runs, condensed, 9 convergences + rated actions):
  `loops/_advisory/2026-07-20.md`
- Brett wiring: quarterly step in `processes/loops/brett-ideas.md` + line in
  `runtime/prompts/brett-ideas.md`
- Guardrail: fabricated-endorsement line in CLAUDE.md §External-surface rules
