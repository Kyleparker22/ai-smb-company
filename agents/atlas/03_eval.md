# Atlas — Stage 3: Eval / gates / watchdogs

## Eval set (v0)

Every Monday after the briefing runs, the eval harness checks each of these:

### 1. Reliability
- **Test:** Did the briefing land in all three surfaces (artifact, email draft, Slack post) by 7:30am ET?
- **Target:** 95% on-time over rolling 4-week window.
- **Measurement:** Atlas logs the timestamp of each delivery in `cost.md`; weekly rollup computed.

### 2. Completeness
- **Test:** Does the briefing artifact contain all required sections — "What changed this week", "Pipeline state", "This week's calls", "Finance pulse", "Watchdog signals", "Recommended actions (3-5)", "Open questions", "What I'd do differently next run"?
- **Target:** 100%.
- **Measurement:** Section-header presence check; eval fails if any header is missing.

### 3. Brevity
- **Test:** Briefing artifact ≤ 800 words.
- **Target:** 100%.
- **Measurement:** Word count check.

### 4. Watchdog accuracy
- **Test:** Atlas correctly fires every active watchdog trigger that should fire; doesn't fire ones that shouldn't.
- **Target:** 100% recall (no missed watchdogs); < 5% false positive rate.
- **Measurement:** Manually-curated test set of 10 historical scenarios; the Founder adds 1-2 new scenarios per week as edge cases emerge.

### 5. Actionability
- **Test:** Did the Founder take at least one action from the recommended actions list within 7 days?
- **Target:** Weekly.
- **Measurement:** Atlas checks the prior week's briefing — did any "Recommended action" become a completed action (checked off, mentioned in next briefing as "done", or visible in Gmail/Calendar as having happened)?

## Approval gates
> Rungs per `processes/autonomy-matrix.md` and the `## Autonomy` section in `02_build.md`. Read/internal-write/internal-post/Gmail-draft = R3 (autonomous); external send + non-digest channels + client tenants = R1 hard floor.

- **Briefing posted to `#all-yourco`** → full autonomy.
- **Draft email created in the Founder's inbox** → full autonomy.
- **Send any email externally** → human-must-approve (Atlas does not send external email in v0).
- **Slack post to channel other than `#all-yourco`** → human-must-approve.
- **Any action cost > $1** → human-in-loop (review and approve).
- **Touch any client tenant** → human-must-approve.

All gate decisions logged in a `gates/` subfolder, with a one-line audit trail per decision.

## Watchdogs (runtime guards)

### Cost watchdog
- **Trigger:** Atlas's per-run token spend > $0.50, or weekly total > $2.
- **Action:** Log in `cost.md`; escalate to the Founder if 2 consecutive weeks over.

### Drift watchdog
- **Trigger:** Briefing artifact differs in structure (missing or extra sections) from the prior 4-week pattern.
- **Action:** Flag in next briefing's lead; the Founder decides whether to update the SOP or revert.

### Quality watchdog
- **Trigger:** the Founder adds notes to "What I'd do differently next run" that include "wrong", "missed", "incorrect", "didn't see".
- **Action:** Flag as a quality miss; next run leads with the correction.

### Silence watchdog
- **Trigger:** Briefing fails to deliver in any surface for 2 consecutive Mondays.
- **Action:** Escalate to the Founder in any channel that does work; the Founder investigates Cowork session state, scheduled task health.

## Pre-go-live checklist
- [x] Eval set defined (this file)
- [ ] Test set of 10 historical scenarios for watchdog accuracy (to be built during first 2 weeks of operation as scenarios surface)
- [ ] First Monday run produces all three surfaces successfully
- [ ] the Founder reviews first artifact and confirms readable/useful

## Iteration plan
- Every 2 weeks, Atlas updates this eval set based on what the Founder's feedback has surfaced.
- Every 4 weeks, run a full eval pass and write the result into `weekly/YYYY-MM-DD.md`.
- When eval scores plateau, that's when the template extraction happens.
