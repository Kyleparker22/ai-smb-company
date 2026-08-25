# Reed — Stage 3: Eval / gates / watchdogs

## Eval set (v0)
Run on each asset before publish, and (for conversion) after Reilly uses it.

### 1. Reliability
- **Test:** A named vertical/use-case yields a published, embed-ready asset (hosted page + animated thumbnail/GIF + tracked link), registered for Reilly.
- **Target:** 100%.
- **Measurement:** Asset registry has a complete entry; thumbnail + link resolve.

### 2. Credibility (anti-vaporware — updated for animated production 2026-06-08)
- **Test:** Every workflow shown in the demo is **animated faithfully** — represents what YourCo will actually build for a paying client. No invented features, no overclaiming of speed or capabilities, no animated outcomes YourCo can't deliver.
- **Target:** 100% (0 fabricated capabilities; 0 overclaims).
- **Measurement:** Each shown workflow step maps to a real, deliverable capability in the Vapi-based intake employee pattern; reviewer (Luka or the Founder) confirms accuracy against the actual deliverable before publish.

**Original v0 standard was "0 fabricated capabilities — show only what actually runs" via real screen capture. Updated for animated production: animated illustration is honest if it accurately represents the real product. Animation does not lower the truth bar; it changes the medium of demonstration.**

### 3. Accuracy / brand
- **Test:** No overclaiming; on-brand; outcome-framed; accurate to what YourCo can deliver.
- **Target:** 100%.
- **Measurement:** Script claims checked against deliverable reality (human-in-loop in stage 1).

### 4. Turnaround
- **Test:** First reusable per-vertical asset produced in ≤ 1 working day.
- **Target:** 100%.
- **Measurement:** Production record timestamps (brief → published).

### 5. Conversion (downstream, via Reilly)
- **Test:** Email 2 with the Reed demo lifts reply / positive-reply rate vs a no-demo control.
- **Target:** Positive lift; baseline after first campaign.
- **Measurement:** Tracked-link click-through + Reilly campaign rollup.

### 6. Structural conformance (v2 — locked 2026-06-08)
- **Test:** Demo follows the 3-part story arc: problem (10-15 sec) → agent in action (35-50 sec) → outcomes (10-15 sec). End frame anchors "Live in 48 hours from signed agreement."
- **Target:** 100% — every cold-outreach demo follows the arc.
- **Measurement:** Pre-publish review: timestamps for each part fall in range; end frame present and on-spec.

### 7. Tonal conformance (v2 — locked 2026-06-08)
- **Test:** Demo is quiet and demonstrative — no voiceover salesmanship, no hype, no "BOOK NOW"-style closers. Reads peer-to-peer, not vendor-pitch.
- **Target:** 100%.
- **Measurement:** Luka reviews each demo before publish; flags any tonal drift in a pre-publish brand review.

## Approval gates
Mapped to the rung model in `02_build.md §Autonomy` (standard: `processes/autonomy-matrix.md`).
- **Script / build demo / capture / VO / assemble / stage draft** → full autonomy (**R3**, internal/reversible).
- **Publish publicly or use in external outreach** → **human-must-approve (R1 hard floor)** — the Founder reviews the final cut; stays gated by design.
- **Claims/positioning in script** → human-in-loop (**R1**).
- **Any spend > $1** → human-in-loop (**R1**).

All gate decisions logged in `gates/` with a one-line audit trail.

## Watchdogs (runtime guards)

### Credibility watchdog
- **Trigger:** A storyboard/script depicts a capability that isn't actually runnable.
- **Action:** Block; rewrite to show only real behavior; flag in approval summary.

### Overclaim watchdog
- **Trigger:** Script contains a superlative/guarantee or a claim not backed by a deliverable ("100% accurate", "fully autonomous", named results YourCo hasn't produced).
- **Action:** Block that line; route to human-in-loop.

### Deliverability watchdog (shared with Reilly)
- **Trigger:** An asset is handed to outreach as an embedded video/attachment rather than an animated GIF preview + link.
- **Action:** Hard block; only animated GIF preview + tracked link leaves for email. (A GIF is an image, not an embedded video file — this satisfies Reed's existing roster gate. See `/04_agent_roster.md` for the clarified gate language.)

### Structural drift watchdog (v2)
- **Trigger:** Cold-outreach demo script deviates from the 3-part story arc (problem → agent → outcomes) OR omits the 48-hour-from-signed-agreement end frame.
- **Action:** Block; rewrite to conform. Deviations require explicit the Founder approval logged in the production record.

### Cost watchdog
- **Trigger:** Per-asset production spend (media tools + tokens) > set cap.
- **Action:** Log in `cost.md`; pause and escalate if exceeded.

## Pre-go-live checklist
- [x] Eval set defined (this file)
- [ ] Media tool stack selected + logged
- [ ] Asset registry created
- [ ] First demo built from a real agent (candidate: Atlas) and approved
- [ ] Thumbnail + tracked link verified in a test email render
- [ ] Reilly successfully pulls the asset for touch 2

## Iteration plan
- After each asset: capture what made it credible/convincing (or not) in the production record's feedback section.
- Feed Reilly conversion data back: which demo styles lift replies → standardize those.
- When reusable demos prove lift across 2–3 verticals, build the v1 personalization layer; when that holds, extract the production pattern into `yourco-template` (v2, sellable).
