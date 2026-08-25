# Decision — the Evidence door: five things the OS can prove about itself

**Date:** 2026-08-07 · **Owners:** the Founder (call) + Atlas (HQ) + Kolby (sweep) · **Status:** built and live in HQ

## The call
HQ gains a seventh door, **Evidence**, holding five new views. Each answers a question the OS
could not previously ask about itself, and each is built on the same principle: **it refuses to
state a number its inputs don't support.** The refusals are the product. An honest "we can't say
yet, and here is exactly what's missing" is worth more than a confident number nobody can check —
and it is the only version that survives contact with a buyer's diligence.

| View | The question | Why nobody else can build it |
|---|---|---|
| **Trust ledger** (+ calibration + immune drills) | How much control has the OS absorbed, at what rung, and would it notice a fault? | Requires per-action evidence, a rung model, and deliberately-induced faults — the moat layer, made countable |
| **Trip-wires** | Which settled decisions has live data now contradicted? | Requires decisions to live as files next to the metrics that would refute them |
| **Time machine** | What did HQ say on any past date, and which commit + which agent moved this number? | Requires the company's numbers to live in git. SaaS silos keep a current value and a chart; they cannot name the commit |
| **DRI twin** | How much of the Founder's judgment has the OS actually learned, per class? | Requires predictions recorded *before* the call, and a decision log to learn from |
| **Vacancies** | Which work has no owner — absorb, activate, or hire? | Requires the whole company's open work to be one machine-readable inventory (The Board) |

## Why these five, and why now
The moat claim — reliability, eval, observability, approval, executive trust — has been true and
unquantified. Kolby's eval reviews measure the OS while it behaves; the autonomy matrix records
which actions run unattended. Neither answers *how much control has moved off the human*, and
nothing at all answered *would we notice if this broke*. Both are the questions a serious buyer
reaches within two meetings, and both are answerable here because yourco's entire company is a
git repo where the workforce is agents and every action leaves an artifact.

The trust ledger and the immune drills ship as one thing on purpose: a trust number that nobody
stress-tests is a self-report, and drills are what convert it into a record.

## The honesty rules (each guards against a specific way this could lie)
1. **Priced or not at all.** Control cost uses a declared per-loop basis with a stated
   confidence. Nothing is `measured` — every entry is `estimated`, and measured hours stay **0**
   until a real time study runs. Unpriced actions are counted and excluded from the hours, never
   averaged in. (Same stance as the Clients view rendering `~$15–25` as a range plus an unpriced
   count rather than a fake midpoint.)
2. **Silence is a miss.** A drill past its detection window with no verdict scores **UNDETECTED**,
   never "pending". Not noticing is the failure being tested for.
3. **A rate needs a sample.** One detected drill reads "1 of 1", not "100%". Calibration publishes
   no Brier below 5 resolved forecasts. No composite trust score until every input exists — the
   missing ones are named instead.
4. **The evidence store outranks the prose.** The trust ledger joins itself against Kolby's
   hand-written streak table and reports `supported` / `DISAGREEMENT` / `unverifiable`. On day
   one: 1 supported, 3 unverifiable — an instrumentation gap, stated as such rather than papered
   over.
5. **Empty by construction.** The twin starts at zero. Backfilling predictions against decisions
   already made would score it on hindsight — the fabricated-completeness failure the loop
   contract calls the cardinal sin. Same reason Kolby opened the streak ledger at zero.
6. **Absence is not zero.** A git revision where `crm/data.json` didn't exist returns *absent*,
   not `$0` — the company hadn't started measuring, and a zero there would be a claim about a
   past that didn't happen.
7. **Ambiguity refuses.** A trip-wire check mixing `and` with `or` is refused rather than
   evaluated under a guessed precedence. A check that can't be evaluated is reported as an
   **error**, never silently read as "did not fire".

## What is deliberately NOT automated
- **Drills are inert and operator-placed.** Only `schema_drift.py` runs unattended, because it
  provably touches nothing real (temp copies of the CRM). An autonomous fault-injector wired
  into live systems is exactly the day-one high-blast-radius autonomy
  `processes/autonomy-matrix.md` says never to build.
- **Trip-wires are transcribed, not invented.** A trip-wire encodes when one of the Founder's strategic
  calls dies. The seven seeded ones transcribe revisit conditions the decision files already
  state in their own words. The other 87 decisions are reported as `uncovered` — a to-do list
  for the Founder, not a gap for an agent to fill.
- **The twin never decides.** A class that clears every threshold reads "would qualify — the Founder's
  call". Four classes (legal-gate · publish-send · spend · client-commitment) can **never**
  qualify at any accuracy: category exclusions, mirroring the autonomy matrix's "what stays
  gated regardless of evidence". Prediction accuracy is not authority.
- **Vacancies propose, never create.** No agent is made, no roster edited, no task filed. New
  functions are left **unnamed** — naming agents is the Founder's.

## What it surfaced on day one
- 233 actions backfilled from committed loop artifacts; **~25.2h estimated** control absorbed
  across 53 priced actions, **180 unpriced** and excluded; pricing coverage 23%.
- The streak-table audit: Gmail label/archive **supported** by evidence (11 recorded ≥ 10
  claimed); the other three climbing actions **unverifiable** — the ledger has no coverage of
  them, so the counts can be neither confirmed nor contradicted.
- Trip-wires: 7 of 94 decisions covered, **0 fired** — a real result, evaluated live.
- Vacancies: **0 hire, 0 activate, 4 absorb** — every domain with piled-up work already has a
  live owner (Rafi/legal 20 open · Atlas/runtime 19 · Reilly/outbound 6 · Charles/money 5). The
  finding is scope and cadence, not headcount.
- The first immune drill passed: four CRM mutations, every consumer degraded to 0/None with no
  fabricated value.

## Two bugs the build caught in itself
- The vacancy detector's first version matched agents by keyword against their whole role+scope
  blob, and put **Reilly (outbound) in charge of Legal and Runtime** — a long scope paragraph
  matches almost any domain. Fixed by matching owners on the short **role** line, with scope as
  a labelled weak fallback. Now pinned by a test.
- `git log --reverse --max-count=1` reported the repo start as *today*: git applies `max-count`
  **before** reversing. Fixed to read the root commit. Also pinned by a test.

## Cost and honest caveats
- The time machine walks git history. A cold pack made a 56-commit blame take ~20s; batching the
  reads through one `git cat-file --batch` brought it to ~0.5s warm. Cached 5 min, bounded at 150
  commits, and it says so when the walk is truncated.
- **This is internal instrumentation.** It sharpens the story and it will matter in diligence,
  but it does not sign Client Owner. Runway and the first signature still outrank it.
- Trip-wire coverage at 7% is the honest number, and it stays low until the Founder writes the rest.

## Trip-wire
- **Review:** 2026-11-07
- **Overturn if:** the Evidence door stops being maintained — the sweep loop goes stale, or the
  refusals get quietly relaxed into confident numbers to make the posture look better. Either
  makes it worse than not having it, because it would then be a trusted surface that lies.
- **Check:** `drillsUndetected > 0`
- **Check covers:** the immune half only — a drill the OS failed to catch. Ledger staleness and
  loosened refusals are caught by the sweep artifact and by `runtime/test_evidence.py`, not by a
  metric.

## Where it lives
`dashboard/{trust,tripwires,timemachine,twin,vacancies}.py` (read) ·
`runtime/{ledger,trust_ledger,dri_twin}.py` + `runtime/drills/` (write) ·
stores in `loops/_trust/` + `loops/_twin/` · format doc `decisions/_TRIPWIRES.md` ·
loop `runtime/prompts/evidence-sweep.md` (Kolby, Sun 16:30 ET) ·
tests `runtime/test_evidence.py` (54 assertions).
