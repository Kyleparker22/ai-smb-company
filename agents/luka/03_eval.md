# Luka — Stage 3: Eval / gates / watchdogs

## Eval set (v0)

### 1. Consistency
- **Test:** When Luka returns "ship," the Founder's post-hoc audit confirms the asset matches the guidelines. When Luka returns "ship with fixes," the fixed version matches.
- **Target:** 95% agreement rate.
- **Measurement:** the Founder marks each Luka review in a weekly note: was Luka's call right?

### 2. Speed
- **Test:** Time from "Luka, review this" to returned review.
- **Target:** ≤ 5 minutes 95% of the time.
- **Measurement:** Session-time delta or Slack timestamp diff.

### 3. Specificity
- **Test:** Every review contains specific before/after fixes (or "no fixes needed"). No vague critique ("make it punchier", "improve tone").
- **Target:** 100%.
- **Measurement:** the Founder's audit log — was the feedback actionable as written?

### 4. Drift detection
- **Test:** Monthly audit catches all material drifts in the prior month's shipped content.
- **Target:** 100% recall on a the Founder-curated drift test set.
- **Measurement:** the Founder plants 1-2 deliberate drifts each month; Luka should catch them. (Test set lives in `agents/luka/eval_test_set.md` once built.) <!--#planned-->

### 5. Changelog discipline
- **Test:** Every change to `/brand/v0/brand-guidelines.md` has a corresponding dated `CHANGELOG.md` entry with reason and approval reference.
- **Target:** 100%.
- **Measurement:** Diff of `CHANGELOG.md` vs. file-modification history of brand-guidelines.md.

## Approval gates
Mapped to the rung model in `02_build.md §Autonomy` (standard: `processes/autonomy-matrix.md`).
- **Returning a brand review** → full autonomy (**R3**, advice only).
- **Posting monthly audit summary to `#all-yourco`** → full autonomy (**R3**).
- **Updating `CHANGELOG.md` with an already-approved change** → full autonomy (**R3**).
- **Proposing a guideline change** → human-in-loop (**R1 hard floor**). Luka writes the proposal in `/decisions/2026-MM-DD_brand-update-X.md`; the Founder approves before `/brand/v0/brand-guidelines.md` is edited.
- **Changing the guidelines without a proposal** → not allowed; treat any attempt as a watchdog trigger.
- **Anything customer-facing** → must-approve (**out of scope** — Luka does not publish).

## Watchdogs (runtime guards)

### Scope-creep watchdog
- **Trigger:** Luka attempts to write or rewrite original content (Katie's territory), or produces original visual designs (Pickle's territory when built), or publishes anything externally.
- **Action:** Reject the action; log the attempt; lead next monthly audit with the attempted scope creep so the Founder can decide whether to expand scope formally.

### Quality watchdog
- **Trigger:** the Founder's audit log marks Luka's reviews as wrong or unhelpful in >1 of 5 consecutive reviews.
- **Action:** Lead next review with the correction pattern. Surface in next monthly audit as a guideline-ambiguity signal — maybe the rule itself needs sharpening.

### Volume watchdog
- **Trigger:** Zero assets queued for review in 4 consecutive weeks.
- **Action:** Note in monthly audit. Either the Founder isn't shipping, or Luka isn't being used habitually. Surface as a question for the Founder, not a verdict.

### Verbose-review watchdog
- **Trigger:** A Luka review exceeds ~10 lines.
- **Action:** Trim. Luka's job is verdict + specifics, not essay.

## Iteration plan
- After each on-demand review, the Founder can leave a one-line "Luka got this right / wrong + why" note. Next review reads recent notes.
- Monthly audit is where the guidelines evolve. Luka surfaces patterns ("phrase X has been rejected 4 times — should we explicitly forbid it?"). the Founder approves additions via decision log.
- After 3 months of v0, Luka can propose v0 → v1 promotion. Promotion requires the Founder's decision-log entry and a CHANGELOG version bump.
