# Flue OS — chimney sweeps & hearth services (build 56)

**Working name:** Flue OS · **Launch:** `prebuild-flue-os` · **Port:** 8876
**Synthetic operator:** "Hearthstone Chimney Co." — 3 techs, ~1,900 households on file, brutal
Sept–Jan season.

## Why this industry (the overlooked test)
Chimney sweeps are the classic overlooked trade: seasonal crush, safety stakes (house fires,
carbon monoxide), a national inspection standard (NFPA 211 levels 1/2/3) — and software that is
a shoebox of invoices. No AI vendor has ever pitched a sweep.

## The bleeding neck
"Safe to burn." A family asks it every October, and the only honest answer cites the recorded
inspection — level, date, findings, tech. Software that reassures without the record is a house
fire with a chat log. The quiet leaks: the annual-sweep book nobody re-calls (the entire
recurring revenue base), creosote stage-3 findings softened into "could use a cleaning,"
CO/flue-gas complaints queued behind routine sweeps, and the season booked chaotically while
February sits empty.

## Modules
1. **Household book** (Company Brain) — every chimney's history: sweeps, inspection levels,
   findings, liner/cap state; due-for-annual counted; the recall ladder is the revenue engine
   (bounded, seasonal-aware — offer February to smooth the crush).
2. **The burn-verdict rule** (Operations) — `declare_safe_to_burn` R0: the recorded inspection
   is cited (level + date + findings) or the answer is "book the inspection"; a stage-3
   creosote or flue-blockage finding is never softened in any draft (forbidden-language check).
3. **Intake triage** (Intake) — CO alarm / smoke-in-house reads FIRST (evacuate script — an
   active CO event is 911, not a booking); chimney fire aftermath (level 3 required, recorded
   rule); routine sweep; quote ask.
4. **Season scheduler** (Back Office) — capacity by tech-day; October overflow offered the
   recorded off-season discount instead of silently lost.
5. **Report & invoice** (Operations) — the inspection report drafts from recorded findings with
   photos referenced; invoice cites the recorded card.

## Guardrails (load-bearing)
- `declare_safe_to_burn` — **R0, never-promote.** The recorded inspection speaks or nothing does.
- `soften_hazard_finding` — **R0**; stage-3/blockage/CO language survives verbatim into every
  draft (tested).
- `co_event_as_booking` — **R0**; the evacuate-and-call-911 script is the whole reply, always.
- Outward drafts R1; the recall ladder bounded with cooldowns.

## ROI (typed)
Annual recall revenue (counted due-book × recorded ticket) · season smoothing (counted October
overflow × off-season capture, operator lift) · the house-fire file (scenario) · office hours
(time_saved).

## Demo path
Due-book board → "is it safe to use the fireplace" → citation vs book-the-inspection → CO alarm
message → evacuate script → stage-3 finding preserved in the report draft → February offer →
trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the CO / smoke event.
