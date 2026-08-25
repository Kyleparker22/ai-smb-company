# 2026-07-22 — Named demo persona on 1:1 surfaces; role-generic on the website

## Decision
The named client-facing **demo persona** (e.g. **Reese**, Quinn, Sage) is **deliberately kept on 1:1 surfaces** — outbound copy, the prospect demo, and the proposal — while the **horizontal website stays role-generic** (function labels only: "Front desk & intake", per the 2026-06-23 function-only sweep). **Demo personas are NOT internal-agent names** and are **exempt** from the "agent names are internal-only" external-surface rule.

## Context
The promptfoo pre-send-gate spike (`agents/kolby/promptfoo-spike.md`) flagged "Reese" in canonical outbound Touch 2/3 as an internal-agent-name violation. That was a **false positive**: Reese is the sanctioned landscaping demo persona (`agents/reilly/outbound-demos/prospect-demo.html`, `agents/pickle/collateral/proposal.html`, `processes/outbound/sequence-copy.md`), not a roster agent (Reese is absent from `04_agent_roster.md`). But it exposed a real ambiguity: the 2026-06-23 sweep stripped persona names from the *website* (`agents/webb/pages/2026-06-23_function-only-alignment-sweep.md`) yet outbound/demo/proposal kept "Reese" — deliberate or drift? the Founder ruled: **deliberate.**

## Options considered
- **Keep the split (chosen)** — persona on 1:1 surfaces, role-generic website.
- Role-generic everywhere — extend the sweep to outbound/demo/proposal (rejected: loses the "your employee has a name" warmth exactly where it lands).
- Named persona everywhere incl. website (rejected: re-introduces person-names on the horizontal surface the sweep deliberately made role-generic).

## Why
A named persona reads as *"your employee"* and lands best in a **1:1, personalized** context (a demo built for one prospect, a proposal to one owner, a cold email that already shows their branded front desk). The **horizontal website** speaks to "any business in any industry," where a specific person-name is noise — a role label ("Front desk & intake") generalizes cleanly. The two rules aren't in tension; they're matched to surface intent. And the distinction it forces — **demo persona ≠ internal agent** — is correct: Reese/Quinn/Sage are product-facing personas we *show clients on purpose*; Reilly/Kolby/Bella/etc. are internal team agents that stay internal.

## Reversibility
Label-level and cheap to revisit: if outbound A/B shows persona-named copy underperforms role-generic (once outbound is live post-OtherVenture), flip the 1:1 surfaces to role labels — a copy sweep of the three surfaces + the demo. The website side is unaffected either way.

## Downstream (swept same session)
- `agents/kolby/promptfoo-spike/promptfooconfig.deterministic.yaml` — agent-name check **scoped to the internal roster only**, demo personas (Reese/Quinn/Sage) excluded, greeting line stripped so prospect first-names that collide with the roster (David/Jim/Ray/…) don't false-positive. Proven: Reese PASS, prospect "David" PASS, "Reilly" in body FAIL.
- `processes/outbound/pre-send-eval-gate.md` dim 4 — persona carve-out made explicit + linked here.
- `agents/kolby/promptfoo-spike.md` — the false-positive corrected in the record.
