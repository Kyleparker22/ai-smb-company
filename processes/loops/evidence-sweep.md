# Loop — evidence-sweep (Kolby): keeping the Evidence door honest

**Cadence:** Sunday 16:30 ET (`yourco-evidence-sweep.timer`, live on the VPS) — deliberately **before**
the 17:00 eval review, so the eval can read what this produced · **Owner:** Kolby (QA/eval) ·
**Output:** `loops/_trust/` + `loops/_twin/` stores updated, plus a written artifact ·
**Prompt:** `runtime/prompts/evidence-sweep.md` · **Step 0 learnings:** `learnings/qa-eval/`, `learnings/ops/`

## Why
The Evidence door (HQ) makes claims nobody else checks: how much control the OS has absorbed, whether
it would notice a fault, whether a settled decision has quietly expired, and which work has no owner.
Those claims decay silently unless something maintains them. This is that something.

**Its job is to keep the numbers TRUE, not to make them look good.** A sweep that reports a worse
posture than last week has done its job correctly. This is the loop most at risk of grading its own
homework, so that sentence is the standard.

## Method — five mechanical steps, then one written artifact
1. **Backfill the trust ledger** — `python3 runtime/trust_ledger.py --backfill-loops`. Idempotent.
   "Nothing new" is a valid result and means no loop wrote anything this week — itself worth reporting.
2. **Sweep overdue drills** — `python3 runtime/trust_ledger.py --sweep`. Any drill past its detection
   window with no verdict becomes **UNDETECTED**. Do not re-arm it and do not quietly close it: a
   missed drill is a finding and gets its own heading in the artifact.
3. **Run the automated drill** (`runtime/drills/`).
4. **Refresh the DRI twin** (`runtime/dri_twin.py`) — four decision classes can never qualify; that is
   by construction, not a gap to close.
5. **Evaluate the trip-wires** — `decisions/` entries carrying a `## Trip-wire` section, against live
   facts. A fact nobody measures reads `unmeasured` and must never be reported as passing.

Then write the artifact: what moved, what regressed, what is now undetected, and what the numbers
cannot support.

## Guardrails
- **Never improve a number by changing how it is measured.** If a metric needs a definition change,
  that is a proposal to the Founder, in the artifact — not a silent edit.
- **Refusals are output.** "This cannot be evaluated because X is missing" is a correct result;
  `python3 runtime/test_evidence.py` (219 assertions) exists to enforce exactly that.
- Reports and updates its own stores only. It does not promote autonomy rungs — Kolby evidences,
  the Founder promotes (`processes/autonomy-matrix.md`).
