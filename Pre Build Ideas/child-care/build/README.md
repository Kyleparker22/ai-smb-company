# Ratio OS — build 24

Pre-built vertical AI OS for child care centers.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py             # 3 centers, 13 rooms, ~240 children, waitlist
python3 test_ratio_os.py    # 33 assertions
```

Launch name **`prebuild-ratio-os`** (port 8844, 127.0.0.1 only).

## What it is

"Little Elm Learning Centers" — 3 centers, $4.1M. Four modules: **the pickup rule**,
**ratio board**, **message triage**, **waitlist funnel**.

## The refusal it is organised around

**Software never authorizes a release.** The release check is a record lookup against the child's
authorized list — on the list, staff still checks photo ID (the check says so itself: *"a record
lookup, not an authorization"*); not on the list, refused with the rule stated, and a human
verification task opens at R2. A "my brother will pick her up" message **never auto-approves
anyone** — `confirm_unlisted_pickup` and `add_authorized_pickup` are both R0: names are added by
the enrolled parent through the written process, never on a caller's say-so. Eval costly class =
missed pickup-change/incident signal (*THE NIGHTMARE SCENARIO OF THIS INDUSTRY*), recall 1.0.

Also load-bearing:
- **Ratios are computed from recorded attendance and clock-ins or refused** — a room with no
  records is *unmeasured, never assumed compliant*; children with zero staff is over by
  definition; `estimate_ratio` is R0. Rules are per-state and name themselves a default.
- **An incident gets nothing in writing from software** — the director calls.
- **Illness questions travel with the policy text, never advice.**
- The waitlist funnel is counted (inquiries → toured → offered → enrolled) with a floor of 10.
- The ROI panel's pickup line is the operator's or blank — *the one that cannot be priced.*

## 10-minute demo

Ratios (the over room, the no-records room refusing) → Inbox (the brother message → verification,
nothing confirmed; the slide fall → nothing drafted) → Release check (try "Uncle Ray Osei") →
Waitlist → ROI → Trust.

## What this does not do yet

- **No integrations.** CMS (Procare/Brightwheel-class), check-in kiosks, subsidy portals are
  adapter seams.
- **Triage is deterministic pattern-matching** — a real deployment puts a model behind the routine
  path and leaves the pickup and incident stops exactly as they are.
- **Ratio rules are simplified shapes** — licensing replaces them per state.
- **Nothing is sent.**
