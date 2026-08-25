# Field OS — agricultural services (build 30)

**Working name:** Field OS · **Launch:** `prebuild-field-os` · **Port:** 8850

## The idea

A custom-application operation (spraying, spreading, agronomy) runs on chemistry, licensure, and
weather windows. Its regulatory life depends on as-applied records; its legal life depends on how
the drift complaint was handled in the first hour; and its professional line is bright: **software
never recommends a chemical or a rate** — a licensed agronomist does, off the label.

**Buyer:** the owner. Thinks in acres covered, weather windows, and the neighbor's phone call.

## The bleeding neck

- A drift complaint ("my tomatoes are curling", "bees dying since tuesday") handled casually is a
  state-investigation exhibit. Handled precisely — logged, acknowledged, escalated — it is a
  defensible file.
- An application billed without its as-applied record is unprovable work.
- A restricted-use product dispatched without a licensed applicator on the order is a violation
  before the rig leaves the yard.

## Modules

1. **Complaint & message triage** (Intake) — drift/exposure complaints (neighbor damage, bee
   kills, human/animal exposure) route to a human **immediately** with regulator-grade logging;
   the eval's costly class is a missed drift/exposure signal. Chemical questions ("what rate of
   X") route to the **licensed agronomist unanswered** — the label is the law.
2. **The as-applied gate** (Back Office) — a job bills only with its as-applied record: acres,
   product, rate, date, applicator license. Missing → **cannot bill**, the missing field named.
3. **The RUP gate** (Operations) — a restricted-use product cannot be dispatched without a
   licensed applicator recorded on the order.
4. **Job board** (Operations) — jobs aging with the operator's recorded weather-window notes.

## Guardrails (load-bearing)

- `recommend_chemical_or_rate` — **R0.** A licensed agronomist recommends, off the label.
- `bill_without_as_applied` — **R0**, structural.
- `dispatch_rup_unlicensed` — **R0**, structural.
- `assert_drift_cause` — **R0.** The system logs and escalates; it never asserts or denies
  causation — that is the investigation's job.

## ROI model

Acres billed provably → their number · complaint-file discipline → scenario · office hours →
time saved · missed-window losses → their number.

## Build prompt (§8)

Build `Pre Build Ideas/ag-services/build/` on `_kit/`. Stdlib, JSON store, 127.0.0.1:8850, launch
`prebuild-field-os`. Seed "Prairie Line Ag Services": ~180 growers, ~600 jobs incl. RUP orders
with and without licensed applicators, as-applied records present and missing, messages incl.
every complaint type. Eval costly class = missed drift/exposure signal. Tests pin the four R0s,
both structural gates, regulator-grade complaint logging, ROI blanks, counted automation.
