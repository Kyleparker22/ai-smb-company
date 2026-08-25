# Polo — Stage 3: Eval / gates / watchdogs

## Eval set (v0)

### 1. Coverage
- **Test:** Every vertical Reilly campaigns into has a locked price in `/pricing/v0/`.
- **Target:** 100% (Reilly's pre-campaign gate enforces).
- **Measurement:** Check at Reilly's campaign launch; logged when Reilly's first email in a vertical sends.

### 2. Research depth
- **Test:** Every pricing proposal cites ≥ 5 specific sources (industry reports, comparable services, owner forums, public pricing pages).
- **Target:** 100%.
- **Measurement:** Decision-doc review by the Founder at approval time.

### 3. Close-rate alignment
- **Test:** Locked prices produce close rates within Polo's predicted range (±20%).
- **Target:** 80% of verticals within range after 5 deals each.
- **Measurement:** Reilly's campaign close-rate data, compared quarterly.

### 4. Retention alignment
- **Test:** Locked prices produce retention within Polo's predicted range (no >25% deviation from prediction).
- **Target:** 80% within range after 6 months per vertical.
- **Measurement:** Charles's retention data, compared semi-annually.

### 5. Quarterly hygiene
- **Test:** Every quarter, every locked vertical has a review artifact in `/loops/pricing-review/`.
- **Target:** 100%.
- **Measurement:** Folder check; missing reviews trigger the stale-data watchdog.

### 6. CHANGELOG discipline
- **Test:** Every change to `/pricing/v0/<vertical>.md` has a corresponding dated CHANGELOG entry with reason and approval reference.
- **Target:** 100%.
- **Measurement:** Diff of CHANGELOG vs. file-modification history.

## Approval gates
Mapped to the rung model in `02_build.md §Autonomy` (standard: `processes/autonomy-matrix.md`).
- **Researching a vertical** → full autonomy (**R3**).
- **Drafting a pricing proposal as a decision doc** → **R1**. Proposal alone doesn't lock pricing — only an explicit the Founder approval does.
- **Updating `/pricing/v0/<vertical>.md` with an already-approved change** → full autonomy (**R3**).
- **Locking a new vertical's pricing** → human-in-loop (**R1 hard floor**). the Founder reviews the decision doc; pricing lands in `/pricing/v0/` only after explicit "approved" reply.
- **Changing a locked vertical's pricing** → human-in-loop (**R1**). Same proposal-then-approve pattern.
- **Any external pricing communication** → must-approve (**R1** — Polo doesn't talk to prospects).
- **Custom one-off pricing for a specific prospect** → must-approve (**R1** — rejects scope creep into per-deal pricing).

## Watchdogs (runtime guards)

### Scope-creep watchdog
- **Trigger:** Polo attempts to propose pricing for a specific prospect (one-off pricing), negotiate, or talk to a prospect directly.
- **Action:** Reject the action; log; surface as scope-creep in next quarterly review.

### Coverage watchdog
- **Trigger:** Reilly logs a campaign launch in a vertical not in `/pricing/v0/`.
- **Action:** Pre-block via Reilly's pre-campaign gate. If somehow bypassed, escalate immediately to the Founder.

### Margin watchdog (coordinated with Charles)
- **Trigger:** Charles's per-engagement margin report flags a vertical with sustained margin <50% across multiple clients.
- **Action:** Polo proposes a pricing adjustment for that vertical via decision doc.

### Stale-data watchdog
- **Trigger:** A locked vertical hasn't been reviewed in >120 days (i.e., quarterly review missed).
- **Action:** Surface in next available run; force-include in next quarterly review.

## Iteration plan
- After each vertical pricing lock, the Founder leaves a one-line note on Polo's decision doc: "this proposal was useful / weak because X." Next proposal incorporates.
- After each quarterly review, predicted-vs-actual ranges get updated based on real data. Over time Polo's predictions get sharper.
- After 3+ verticals locked, Polo can propose v0 → v1 promotion: pricing-build patterns extracted into a templated methodology. Promotion requires the Founder's decision-log entry.
