# Plat OS — land surveyors (build 53)

**Working name:** Plat OS · **Launch:** `prebuild-plat-os` · **Port:** 8873
**Synthetic operator:** "Meridian Land Surveying" — 2 field crews, 1 licensed PLS, ~60 open jobs.

## Why this industry (the overlooked test)
Survey firms are 3–10 person shops drowning in title-company deadlines, and no AI vendor has
ever knocked. The pipeline (request → deed/record research → fieldwork → drafting → PLS review →
sealed plat) runs on email and a whiteboard; closings slip because nobody tracked which of 60
jobs blocks a closing on Friday.

## The bleeding neck
The seal. Only the licensed surveyor's judgment — sealed, on the record — makes a boundary real;
any software that "confirms" a line before the PLS reviews it is practicing surveying without a
license. And the closing-date ladder: a survey that misses a closing costs the client's deal and
the firm's title-company relationship, the referral source that feeds everything.

## Modules
1. **Job pipeline** (Operations) — research → field → draft → PLS review → sealed, with the
   CLOSING DATE as the master clock; the board ranks by days-to-closing, blockers named.
2. **The seal gate** (Operations) — `state_boundary_conclusion` R0: no boundary/encroachment
   statement leaves software; drafts route to the recorded PLS; "sealed" only with the seal
   record (number + date). Structural: no code path marks a plat final without it.
3. **Record research chain** (Company Brain) — every job carries its cited instruments (deed
   book/page, prior plats, POBs); a draft citing nothing is refused ("a boundary without its
   chain is an opinion").
4. **Title-company desk** (Sales/Intake) — status asks answered from the pipeline record;
   deadline-risk flagged to a human BEFORE the closing week; quote asks priced from recorded
   comparable jobs (acreage/type) or refused.
5. **Field-to-office handoff** (Back Office) — crew day sheets (points, control, obstructions)
   recorded same-day; a job with fieldwork but no day sheet reads incomplete, never assumed.

## Guardrails (load-bearing)
- `state_boundary_conclusion` — **R0, never-promote.** The PLS seals or nobody does.
- `mark_plat_sealed` — needs the recorded seal reference; no path without it.
- `promise_closing_date` — R1, and only from the pipeline's own recorded stage clocks.
- `quote_without_comparables` — refused; outward replies R1.

## ROI (typed)
Closings kept (counted deadline-hit rate once measurable) · jobs/crew-week throughput (operator
lift) · research hours returned (time_saved) · the lost-title-company scenario (never a number).

## Demo path
Deadline board (closing-ranked) → "where's my survey" answered from record → encroachment
question refused + routed to PLS → research chain citation → sealed-without-seal refusal → trust.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the boundary/encroachment question.
