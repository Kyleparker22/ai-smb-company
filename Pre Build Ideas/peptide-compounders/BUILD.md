# Provenance OS — peptide compounders & suppliers (build 73)

**Working name:** Provenance OS · **Launch:** `prebuild-provenance-os` · **Port:** 8896

## The idea

A compounding pharmacy / peptide supplier does not fail for want of demand. It fails because the
**rulebook moves under it**, because the **paperwork that survives an inspection lives in folders
nobody can assemble under pressure**, and because **complaints arrive as clinical questions** that
software must capture perfectly and never answer.

**Buyer:** owner or QA lead. Thinks in lots, packets, and what happens if someone walks in.

## The bleeding neck

- Nobody is reading the source changes against the **actual product list** — a change that lands on
  one SKU is invisible until it is expensive.
- Batch records, stability data and upstream certificates are scattered; "inspection-ready" is a
  belief, not a measurement.
- Upstream certificates are **filed on trust** rather than checked against what was received.
- An adverse-event report needs complete capture and zero interpretation.

## Modules

1. **Rulebook watcher** (Company Brain) — the standout. Maps each source change onto SKUs by
   analyte, alias, route and claim, and **shows which word matched**. Over-inclusive on purpose.
2. **Batch packet assembly** (Operations) — seven required records + a verified upstream
   certificate. Reports what is **missing**; never complete by omission.
3. **Upstream verification** (Operations) — issuer present, analyte matches what was received, lot
   matches, purity reported, certificate unexpired. Five real failure modes, caught by comparison.
4. **Complaint intake** (Customer) — adverse event vs product quality vs other; the adverse path is
   captured, routed, and explicitly not assessed.

## Guardrails (load-bearing)

- `assert_compliance` — **R0.** No system here may state the business is compliant with anything.
- `assess_adverse_event` — **R0.** Capturing is the obligation; assessing is a clinical act.
- `alter_batch_record` — **R0.** The batch record is the inspection artifact.
- `release_batch` — **R1, never promotable**, and it **refuses over an incomplete packet**.
- Eval costly class: **a change that touches a live product, filed as irrelevant.**

## ROI model

Packet assembly hours → time saved · source-monitoring hours → time saved · upstream checking →
time saved · a rule change caught early → **scenario**. This build deliberately claims **no revenue
line at all** — it saves time and catches changes, and pretending otherwise would be inventing.

## 10-minute demo

Board (unreviewed changes, how many name your products) → Rulebook: the semaglutide change with the
matched word shown, then the sunscreen one that names nothing → Batch packets: release a lot with a
hole in it and watch it refuse, listing blockers → Upstream: check a certificate whose lot does not
match what was received → Complaints: submit a rash-and-breathing report, watch it captured, routed
and **not assessed** → Trust: ask "are we compliant?" → refused by class.

## Build prompt (§8)

Build `Pre Build Ideas/peptide-compounders/build/` on `_kit`. Stdlib, JSON store, 127.0.0.1:8896,
launch `prebuild-provenance-os`. Seed "Halden Compounding": 8 SKUs with analytes/aliases/routes/claims,
~48 batches with deliberately incomplete record sets, 48 upstream certificates including the five
failure modes, 12 source changes spanning high/medium/low and several that name nothing. Eval costly
class = a landing change filed as clear. Tests pin alias and route matching, the packet's
never-complete-by-omission rule, all five upstream failures, the adverse-event non-assessment, the
three R0s, release refusing over blockers, and the absence of any revenue line.
