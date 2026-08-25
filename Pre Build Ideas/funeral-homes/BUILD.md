# Arrangement OS — funeral homes (build 25)

**Working name:** Arrangement OS · **Launch:** `prebuild-arrangement-os` · **Port:** 8845

## The idea

A funeral home's whole business arrives on the worst phone call of someone's life. The first call
must reach the on-call director in seconds; the price conversation is federally regulated (the FTC
Funeral Rule: itemized prices from the General Price List); and the paperwork chase — death
certificates, permits, insurance assignments — has hard dates a grieving family should never have
to track. Arrangement OS handles the logistics and structurally refuses everything that must stay
human.

**Buyer:** the owner/managing director. Thinks in cases, pre-need pipeline, and reputation.

## The bleeding neck

- A first call that rings to voicemail at 2am goes to the next name on the hospice's list.
- A price conversation off the GPL is an FTC violation; a bundled-only quote is too.
- Certificates and permits chased by memory while a family waits to fly a casket home.

## Modules

1. **First-call triage** (Intake) — a death notification routes to the on-call director
   **immediately** with logistics captured (place, contact, callback) and nothing else said. The
   eval's costly class is a missed first call. Grief and condolence conversations are **never**
   automated.
2. **GPL-grounded quote desk** (Sales) — every quote is itemized from the recorded General Price
   List. **No GPL on file, or an item not on it → the quote refuses.** Bundles always show their
   items. The system never drafts upsell language into an at-need arrangement.
3. **Document chase** (Operations) — certificates, permits, assignments; typed, dated, bounded
   ladder; date alerts for permits.
4. **Pre-need ledger** (Back Office) — contracts counted; funding recorded or *unmeasured*.

## Guardrails (load-bearing)

- `automate_grief_support` — **R0.** Compassion is not a template.
- `quote_off_gpl` — **R0**, structural: no recorded GPL, no numbers.
- `handle_remains_decision` — **R0.** Software never touches disposition decisions.
- `pressure_sale_at_need` — **R0.** No upsell drafts to a grieving family, ever.

## ROI model

First calls answered → their case value (never framed as "revenue per death" — case support) ·
document hours → time saved · pre-need follow-ups → revenue (their conversion) · Funeral Rule
discipline → scenario.

## Build prompt (§8)

Build `Pre Build Ideas/funeral-homes/build/` on `_kit/`. Stdlib, JSON store, 127.0.0.1:8845,
launch `prebuild-arrangement-os`. Seed "Hartwell & Sons": 2 locations, a full GPL, ~60 active
cases with document states, pre-need contracts, calls incl. first calls at hard hours. Eval costly
class = missed first call. Tests pin the GPL refusal, the itemization rule, the four R0s, the
document ladder, ROI blanks, counted automation. Tone: every surface written with restraint.
