# Brett — Stage 3: Eval / gates / watchdogs

## Eval set (v0)
Run on each advisory memo (monthly or on-demand).

### 1. Grounding (anti-fabrication)
- **Test:** Every external claim has a source URL; every internal claim names the OS artifact it came from.
- **Target:** 100% — 0 unsourced claims.
- **Measurement:** Spot-check each claim against its citation.

### 2. Actionability
- **Test:** the Founder adopts ≥1 recommendation per memo.
- **Target:** ≥1 per memo.
- **Measurement:** Next memo checks whether prior recommendations were acted on (visible in decisions/, pipeline, or OS changes).

### 3. Evenhandedness
- **Test:** Each recommendation presents the tradeoff / counter-case, not one-sided advocacy.
- **Target:** 100% of recommendations.
- **Measurement:** Review: does each rec state what it costs or risks?

### 4. Drift detection
- **Test:** Correctly flags moves toward parked directions (self-serve SaaS) or over-building (agents/tools without a live trigger); no false alarms on settled decisions.
- **Target:** 100% recall on real drift; 0 false flags on decisions already logged with reasoning.
- **Measurement:** Against `decisions/` + the CLAUDE.md "what's parked" section.

### 5. Brevity & ranking
- **Test:** Memo readable in ≤7 minutes; recommendations ranked (3–5), not an undifferentiated list.
- **Target:** 100%.
- **Measurement:** Length + structure check.

## Guards (Brett has no action gates — he can't act — so these are quality guards)
> Autonomy per `processes/autonomy-matrix.md` and the `## Autonomy` section in `02_build.md`: Brett's whole surface (read/research/memo/post) is R3, with **no action rung** — so these are quality guards, not autonomy gates. The scope guard below is the enforcement of his "advise-only" hard floor.

- **Unsourced-claim guard:** any claim without a citation is cut before the memo ships.
- **Settled-decision guard:** Brett does not reopen a logged decision unless he states the *new* information that justifies revisiting it.
- **Yes-man guard:** a memo with no risks and no uncomfortable recommendation fails review — advisor value requires honest friction.
- **Scope guard:** if a memo proposes that Brett *do* something (edit a doc, direct an agent), that's flagged as out-of-scope — Brett recommends, the Founder/another agent executes.

## Pre-go-live checklist
- [x] Eval set defined (this file)
- [ ] First memo produced and judged grounded + useful by the Founder
- [ ] Confirm Brett respects `decisions/` (doesn't re-litigate settled calls)

## Iteration plan
- After each memo: track which recommendations the Founder adopted and, later, whether they worked — the real measure of an advisor.
- Build the living competitive/landscape file (v1) once there's enough external signal to maintain.
- Add scenario modeling (v2) when Charles has real revenue/cost data to quantify tradeoffs.
