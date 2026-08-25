# Decision — Reilly: early low-volume warmup ramp (amends launch gate 10)

**Date:** 2026-06-09
**Owner:** the Founder (decision) · Reilly (execution) · Atlas (monitoring)
**Status:** ✅ Locked
**Amends:** `/agents/reilly/02_build.md` hard launch gate 10 ("Warmup complete on the cold-email domain")

## Decision
The first landscaping batch may begin sending **before full warmup completes**, via a controlled low-volume ramp, rather than waiting for the ~July 8 full-warmup date.

## Why
- The pilot is tiny: ~14–20 emailable leads × 3 emails over 21 days ≈ 40–50 total sends. This is a trickle, not a blast.
- Industry practice: a new domain can begin a low-volume cold ramp (~5–15 emails/inbox/day) around the **2-week** mark while warmup continues underneath. The failure mode that burns domains is finishing 2 weeks then blasting hundreds at once — which this plan explicitly does not do.
- Pulls first send from ~July 8 to **~June 22** (~2.5 weeks earlier) without meaningfully raising deliverability risk at this volume.

## Guardrails (all required — this is what keeps gate 10's intent intact)
1. **Health trigger, not a date.** Start only once `getteamyourco.com` shows healthy warmup metrics in the Instantly deliverability dashboard (target ~90%+ inbox placement in the warmup pool, low spam-folder rate). The date (~June 22) is an estimate; the metric is the gate. *Atlas/Reilly cannot read the Instantly dashboard via connector — the Founder confirms health before greenlight.*
2. **Volume cap.** ≤ 10 cold sends per inbox per day during the ramp. Warmup keeps running underneath; total daily send (warmup + cold) stays stable.
3. **No volume jumps.** Never increase daily cold volume by more than ~20%/day.
4. **Top-fit first.** Email 1 goes to the highest-fit leads first (Summit Lawns, Frdm Turf, Plant This, Ethoscapes), so the earliest sends are the best-targeted.
5. **Monitor + abort.** If spam-placement or bounce rate climbs during the ramp, pause cold sends and let warmup catch up. Reilly logs reply/bounce/spam signals; Atlas surfaces them in the Monday briefing.
6. **SMS unaffected.** SMS touches remain blocked until 10DLC clears, regardless of the email ramp. First pass runs email-only if 10DLC isn't ready.

## Gate 10 — amended text
> 10. ✅ **Warmup health-gated low-volume start.** Cold sends may begin once `getteamyourco.com` warmup metrics are healthy (~90%+ inbox placement), at ≤10/inbox/day with warmup continuing underneath — not necessarily at full-warmup completion. Full-volume scale-up still waits for full warmup.

## Unchanged
Other launch gates stand: campaign approval ✅, batch approval (pending), Reed animated asset (in production), 10DLC for SMS (blocked), suppression scrub. Never send from `yourco.com` primary.
