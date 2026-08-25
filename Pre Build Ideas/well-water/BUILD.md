# Well OS — well drilling & water treatment (build 52)

**Working name:** Well OS · **Launch:** `prebuild-well-os` · **Port:** 8872
**Synthetic operator:** "Blue Ridge Well & Water" — drilling rigs + treatment service book,
~400 households on service contracts.

## Why this industry (the overlooked test)
Nobody markets AI to well drillers. Yet the business is two intertwined state machines — a
drilling job (permit → drill → pump test → water test → completion report to the state) and a
recurring treatment book (filters, UV lamps, softeners on service clocks) — run today on paper
tickets and the owner's memory. Health stakes ride on every water test.

## The bleeding neck
"Is my water safe?" — the question every customer asks and the one thing software must never
answer on its own. A potability verdict belongs to an accredited lab report, cited by reference,
or it does not exist. The quiet leaks: service-due treatment systems nobody calls (a UV lamp a
year past due is sterilization theater), permits/completion reports filed late (state fines),
pump-test results promised from memory, and quotes with no recorded well log behind them.

## Modules
1. **Job pipeline** (Operations) — permit → drill → pump test → water test → state report, with
   per-county permit clocks as DATE ALERTS (config-named defaults).
2. **The lab rule** (Operations) — `declare_water_safe` R0: potability statements only CITE a
   recorded lab report (id + date + result); no report → "we don't know yet, the lab does."
3. **Treatment service book** (Back Office) — every installed system carries its consumable
   clocks (filter/lamp/media, recorded intervals); due systems get a bounded reminder ladder;
   "protected" is never claimed past the clock.
4. **Intake triage** (Intake) — no-water emergency (a dry house is a P1) · water-quality worry
   (the costly label: possible contamination reads first) · service due · quote ask.
5. **Well records** (Company Brain) — depth, casing, yield, static level per well, cited in
   every quote; a quote with no recorded log is refused ("we measure, then we price").

## Guardrails (load-bearing)
- `declare_water_safe` — **R0, never-promote.** The lab report speaks or nothing does.
- `downgrade_contamination_worry` — **R0**; a "my water smells/tastes wrong" message never gets
  a soothing auto-reply — record, escalate, human.
- `claim_protection_past_clock` — **R0**; an overdue UV lamp is never "still fine."
- `quote_without_well_log` — refused with the reason; outward quotes R1.

## ROI (typed)
Treatment renewals recovered (counted from the service book) · missed-service revenue (counted
due list × recorded ticket) · permit fines avoided (scenario) · office hours (time_saved).

## Demo path
Board (due clocks, permit alerts) → "is my water safe" → the lab-citation answer vs the refusal →
overdue UV lamp reminder ladder → quote refused without well log → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the contamination worry.
