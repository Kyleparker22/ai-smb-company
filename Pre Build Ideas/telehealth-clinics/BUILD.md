# Encounter OS — multi-state telehealth clinics (build 75)

**Working name:** Encounter OS · **Launch:** `prebuild-encounter-os` · **Port:** 8898

## The idea

What separates a telehealth clinic from every other clinic is not the medicine — it is that **the
patient's location decides who is allowed to see them**, and the scarce resource is clinician
minutes rather than leads. A telehealth clinic scales by throughput and by coverage, and it dies by
routing one patient to a clinician who was not licensed where that patient was sitting.

*(Related but distinct from build 74: **Encounter OS + the product-trust module = Protocol OS**.
Most peptide clinics are telehealth clinics; a general telehealth clinic has no product-trust
problem and a single-site peptide clinic has no licensure problem.)*

**Buyer:** platform operator. Thinks in clinician utilisation, states covered, and completed visits.

## The bleeding neck

- **Licensure routing**, done by hand in a spreadsheet, at speed, by a coordinator.
- **Coverage gaps** — patients in states where nobody on the roster is licensed. Invisible, and the
  actual growth constraint.
- **The leak between paying and attending**, which in telehealth is bigger than the one before
  payment and almost nobody measures.
- **Documentation** — the note is the only artifact that survives a complaint.

## Modules

1. **Licensure-aware routing** (Operations) — the standout. An unlicensed clinician is *structurally
   absent* from the candidate list; the router **refuses** rather than degrade, and there is no
   "best available anyway" path for anyone to click under pressure. An **inactive licence is not a
   licence**.
2. **Async triage → a prepared chart** (Operations) — urgent signals stop the async flow entirely;
   everything else becomes a chart with **every unanswered question named**.
3. **Paid-but-unseen recovery** (Sales) — the measured leak, with drafts at the gate.
4. **Documentation defensibility** (Company Brain) — seven required elements; an encounter missing
   any of them **cannot be closed by anyone**.

## Guardrails (load-bearing)

- `route_unlicensed` — **R0, unpromotable.** The clinic-ending failure, designed out at the query.
- `close_undocumented` — **R0.** Not a nag; a hard stop.
- `clinical_advice` — **R0.**
- Eval costly class: **routing to a clinician not licensed in the patient's state.**

## ROI model

Paid-but-unseen recovered → revenue · clinician minutes returned by prepared charts → time saved
(*never* silently converted to revenue — whether minutes become visits is a staffing decision) ·
coordination hours → time saved · coverage gaps closed → scenario · an unlicensed encounter never
happening → scenario.

## 10-minute demo

Board (states where you have patients and nobody licensed — usually the first thing they have never
seen) → Licensure routing: route someone in a covered state, then someone in California and watch it
**refuse with no fallback**, then note the NY clinician who is licensed but inactive → Async intakes:
the self-harm narrative stops the flow → Documentation: try to close an encounter missing its
assessment → Paid, not seen → ROI.

## Build prompt (§8)

Build `Pre Build Ideas/telehealth-clinics/build/` on `_kit`. Stdlib, JSON store, 127.0.0.1:8898,
launch `prebuild-encounter-os`. Seed "Northline Telehealth": 7 clinicians across 8 covered states
with one INACTIVE licence as the trap, ~180 patients including a real minority in uncovered states,
intakes spanning urgent and routine with some incomplete answers, encounters spanning paid-unseen /
seen / documented / undocumented. Eval costly class = an unlicensed route called routable. Tests pin
that an inactive licence never counts, that a refusal offers no candidates at all, that every routed
candidate genuinely holds the licence, the urgent async stop, the documentation hard stop, and every
ROI blank.
