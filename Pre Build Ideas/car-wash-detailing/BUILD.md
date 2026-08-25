# Shine OS — car wash & detailing (build 38)

**Working name:** Shine OS · **Launch:** `prebuild-shine-os` · **Port:** 8858
**Synthetic operator:** "Brightline Wash Co." — 3 tunnel locations + a detail bay, ~8,000 members.

## The bleeding neck
A membership wash is a small gym: failed cards nobody re-runs, cancellations slow-walked into
chargebacks and attorney-general complaints, and the damage claim — "your wash broke my antenna" —
answered defensively by a shift lead instead of procedurally by evidence. Details die by weather.

## Modules
1. **Message triage** (Intake) — damage claim · cancellation (the clock starts NOW) · membership
   billing · detail booking/reschedule.
2. **Damage-claim protocol** (Operations) — verbatim log at R2 + a camera-footage pull task +
   a human calls within 24h. Software never argues physics ("our brushes couldn't do that").
3. **Cancellation clock** (Back Office) — Member OS pattern: processing at request, per-state
   window config, the save offer a SEPARATE row that never delays processing.
4. **Dunning ladder** (Back Office) — failed membership cards, 3 stepped touches, threat check.
5. **Weather reschedule** (Customer) — booked details on a rained-out day get honest drafts with
   the next two open slots.

## Guardrails (load-bearing)
- `deny_damage_claim` — **R0.** Software logs, pulls footage, and schedules the call; a human
  decides, with the footage.
- `delay_cancellation` — **R0.** Processed, not negotiated.
- `threaten_in_dunning` — **R0**, forbidden-language check on every draft.
- Membership charges after a recorded cancellation request are structurally impossible.

## ROI (typed)
Failed payments recovered (counted × avg dues) · details rescheduled vs lost (counted) · desk
hours (time_saved) · the chargeback/AG file (scenario).

## Demo path
Board → damage claim (logged verbatim, footage task, no denial) → cancel (clock + separate save
row) → dunning copy per step → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the damage claim.
