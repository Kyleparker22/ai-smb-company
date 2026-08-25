# Reilly — Stage 3: Eval / gates / watchdogs

## Eval set (v0)
Run after each campaign is staged (before approval) and again after send (for outcomes).

### 1. Reliability
- **Test:** A named vertical produces a complete staged campaign (sourced + researched + sequenced + staged in Instantly) with zero manual data steps.
- **Target:** 100%.
- **Measurement:** Campaign artifact exists with all prospects carrying a research card and a full sequence.

### 2. Personalization depth (anti-hallucination)
- **Test:** Every prospect's Email 1 references ≥1 specific, verifiable company fact; 0 unverifiable/hallucinated claims.
- **Target:** 100% reference; 0 hallucinations.
- **Measurement:** Each research-card data point must carry a source URL. Stage-3 spot-check: sample 10% of sequences, verify each named fact against its source.

### 2b. Methodology conformance (v2 — locked 2026-06-08)
- **Test:** Every campaign artifact conforms to v2 commission-breath-removal structure: 3 emails + 3 SMS, Email 1 = problems + Nirvana, Email 2 = Reed video, Email 3 = reframe + release. No pricing in cold copy. CTAs in the Founder's signature only.
- **Target:** 100%.
- **Measurement:** Luka brand review at stage 3 includes conformance check against `/agents/reilly/copy-structure.md`.

### 3. Deliverability hygiene
- **Test:** No send from primary domain; SPF/DKIM/DMARC present; warmup active; one-click unsubscribe in every email.
- **Target:** 100%.
- **Measurement:** Pre-send checklist; Instantly deliverability dashboard green.

### 4. Approval discipline
- **Test:** 0 emails sent without the Founder's explicit batch approval.
- **Target:** 100% (hard gate — any violation is a critical failure).
- **Measurement:** Campaign cannot move to "launched" without a logged approval in `gates/`.

### 5. Outcome
- **Test:** Reply rate, positive-reply rate, booked-call rate per campaign.
- **Target:** Baseline set by first campaign; then improve campaign-over-campaign.
- **Measurement:** Instantly webhooks → campaign artifact rollup.

## Approval gates
These gates map to the **Autonomy Matrix** rungs (`processes/autonomy-matrix.md`; per-action rungs in `02_build.md` §Autonomy). Source/stage = R2→R3 (reversible, internal); **send/launch = R1 (gated), capped at R2** — climbs only on Kolby's eval evidence + the Founder's threshold, never to unattended R3.
- **Source / research / write / stage campaign (unlaunched)** → full autonomy (R2→R3).
- **Launch / send campaign** → **human-must-approve** (R1, the core gate; deliverability-gated).
- **Add sending domain or inbox** → human-must-approve.
- **Change ICP/vertical definition** → human-in-loop.
- **Any spend > $1** → human-in-loop.

All gate decisions logged in `gates/` with a one-line audit trail.

## Watchdogs (runtime guards)

### Hallucination watchdog
- **Trigger:** A sequence contains a company claim with no source URL on its research card.
- **Action:** Block that prospect from the staged batch; flag in the approval summary.

### Deliverability watchdog
- **Trigger:** Instantly placement score drops below threshold, bounce rate > 3%, or spam-complaint signal.
- **Action:** Auto-pause the campaign; escalate to the Founder same day.

### Domain-safety watchdog
- **Trigger:** Any attempt to stage a send from `yourco.com` primary or from a non-warmed inbox.
- **Action:** Hard block; cannot proceed.

### Cost watchdog
- **Trigger:** Per-campaign token spend > $2, or enrichment/data spend > set cap.
- **Action:** Log in `cost.md`; pause and escalate if exceeded.

### Suppression watchdog
- **Trigger:** A prospect on the suppression list (replied "no", unsubscribed, or already a contact) appears in a staged batch.
- **Action:** Remove and log; investigate dedupe step.

### State suppression watchdog (SMS — locked 2026-06-08)
- **Trigger:** A prospect with a phone number in FL, WA, OK, MD, NY, or CA appears in an SMS batch.
- **Action:** Remove from SMS batch only (keep on email batch); log. Until Ray (Legal) is built or outside counsel completes a multi-state cold B2B SMS review.

### Reed asset watchdog
- **Trigger:** A campaign reaches stage 4 staging without a Reed asset registered in `/agents/Reed/_asset_registry.md` for the vertical.
- **Action:** Hard block; cannot stage Email 2 without the GIF preview + Loom URL.

### Methodology watchdog (v2)
- **Trigger:** A campaign artifact contains pricing in any touch, a CTA link in any email body (Calendly/website should be in the Founder's signature only), or deviates from the 3-email + 3-SMS structure.
- **Action:** Hard block; route back to copywriting stage with `/agents/reilly/copy-structure.md` reference.

## Pre-go-live checklist
- [x] Eval set defined (this file)
- [x] Cold-email sending domain (`getteamyourco.com`) provisioned via Instantly; 2 mailboxes; warmup running (cleared ~2026-07-08)
- [x] SPF/DKIM/DMARC handled by Instantly done-for-you flow
- [x] Copy methodology v2 written (`/agents/reilly/copy-structure.md`)
- [x] Multi-state SMS suppression list locked (FL, WA, OK, MD, NY, CA)
- [x] First campaign drafted + Luka-reviewed + the Founder-approved (`/agents/reilly/campaigns/2026-06-08_landscaping-us-national-batch-1.md`)
- [x] First Reed asset request filed (`/agents/Reed/requests/2026-06-08_landscaping_email2-demo.md`)
- [ ] 10DLC brand + campaign approved (blocked on orphaned Twilio bundle conflict)
- [ ] Reed's landscaping demo script approved + produced + registered
- [ ] First batch sourced + the Founder-approved
- [ ] Warmup cleared on `getteamyourco.com`
- [ ] STOP keyword + suppression list scrub wired into stage 1
- [ ] Approval gate proven on first live campaign (campaign held un-launched until approval)

## Iteration plan
- After each campaign: update eval with any new failure mode surfaced.
- Reply data feeds ICP refinement (lost/ignored reasons → tighten vertical).
- When personalization + deliverability + approval scores hold steady across 3 campaigns, extract the pipeline into `yourco-template` as the sellable SDR pattern (v2).
