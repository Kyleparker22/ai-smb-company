# Ratio OS — child care centers (build 24)

**Working name:** Ratio OS · **Launch:** `prebuild-ratio-os` · **Port:** 8844

## The idea

A multi-site child care operator lives under two absolutes — the state staffing ratio and the
release-of-child rule — and one economic engine, the waitlist. Ratio OS counts the ratios from
recorded attendance (never estimates), makes an unauthorized release *unspeakable* by software,
and runs the enrollment funnel that pays for all of it.

**Buyer:** the owner/director. Thinks in licensed capacity, ratios, and the waitlist.

## The bleeding neck

- Ratio violations found by a licensing inspector instead of a dashboard.
- "Her uncle is picking her up today" handled by whoever answered the phone — the industry's
  nightmare scenario starts exactly there.
- Waitlist families lost to silence while a classroom seat sits empty.

## Modules

1. **The pickup rule** (Company Brain) — a release check against the child's recorded authorized
   list. Not on the list → **refused**; a pickup-change message never auto-approves anyone — it
   opens a human verification task (photo ID + parent phone verification per policy). The eval's
   costly class is a missed pickup-change/incident signal.
2. **Ratio board** (Operations) — per room, per hour: children checked in vs staff clocked in vs
   per-state ratio rules that name themselves a default. Missing attendance records → the ratio
   is *unmeasured and says so*, never assumed compliant.
3. **Message triage** (Intake) — pickup changes and incidents (nothing drafted on an injury),
   illness questions (exclusion rules routed, not answered), enrollment inquiries (tour drafts).
4. **Waitlist funnel** (Sales) — counted: inquiries → tours → offers → enrolled; tour drafts R1.

## Guardrails (load-bearing)

- `confirm_unlisted_pickup` — **R0.** Software never authorizes a release; humans verify per the
  written policy.
- `respond_to_incident` — **R0** for drafts; injuries get a human call, nothing in writing.
- `answer_medical_exclusion` — illness rules are surfaced as policy text, never as advice.
- Ratios are computed from records or refused — `estimate_ratio` R0.

## ROI model

Seats filled from the waitlist → revenue (their tuition) · ratio-violation exposure → scenario ·
front-desk hours → time saved · the pickup discipline → scenario (never a saving).

## Build prompt (§8)

Build `Pre Build Ideas/child-care/build/` on `_kit/`. Stdlib, JSON store, 127.0.0.1:8844, launch
`prebuild-ratio-os`. Seed "Little Elm Learning Centers": 3 centers, ~340 children with authorized
pickup lists, rooms with age groups, attendance and staff clock-ins (one room missing records),
messages incl. pickup changes and incidents, a waitlist. Eval costly class = missed
pickup/incident signal. Tests pin the release refusal, the never-auto-approve rule, ratio
refusals, the R0s, ROI blanks, counted automation.
