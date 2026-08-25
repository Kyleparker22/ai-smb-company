# Loop — outreach-eval (Kolby): the pre-send gate on a staged batch

> ⚠️ **ON DEMAND BY DESIGN — no timer, and there should not be one.** A batch must be fully staged
> (campaign created, leads staged, `demo_urls` written) before this gate means anything. Scheduling it
> would produce verdicts on batches that do not exist.

**Trigger:** a Slack command or Cowork ask naming one campaign · **Owner:** Kolby (QA/eval) ·
**Output:** `loops/outreach-eval/YYYY-MM-DD_<campaign-slug>.md` + a 3–5 line post to `#yourco-kolby` ·
**Spec:** `processes/outbound/pre-send-eval-gate.md` (this SOP is the procedure; the spec is the rubric)

## Why
**No dated PASS artifact for the exact staged batch, no send.** This is the required input to any
outbound send — the point in the system where the reliability layer actually blocks something.

## Inputs (all of them, every run)
1. `processes/outbound/pre-send-eval-gate.md` — mechanical checks M1–M8 + the six outbound-adapted dimensions
2. **The mechanical pre-pass JSON** — `loops/outreach-eval/<date>_<slug>.mechanical.json`, produced by
   `python3 runtime/instantly.py --eval-batch "<campaign>"`. Needs Bash, so Reilly or the Founder runs it locally.
   **If it is absent or older than the latest staging, STOP.** Write a partial artifact naming the missing
   input and ask for the pre-pass. Never reconstruct M1–M5 by hand or fabricate around it.
3. `processes/outbound/sequence-copy.md` · `brand/writing-rules.md` + `brand/v0/brand-guidelines.md`
4. `processes/launch-gate.md` + `processes/counsel-gates.md` — gate state for dimension 6 (**read, never edit**)
5. `crm/data.json` and prior `loops/outreach-eval/` artifacts — cross-checks and prior failure modes

## Method — error analysis FIRST, scoring second
House standard (mirrors Hamel Husain / Shreya Shankar): read the rendered copy and the lead sample,
note every problem in plain language, group into failure modes, **count them** — *then* score the six
dimensions 2/1/0. **Any 0 = batch FAIL.** Judgments are binary-leaning; when unsure, fail it and surface it.

Sampling per the spec: all touches as rendered previews, judgment read on `min(10, all)` leads, widen on
any sample failure. **The failure-mode table matters more than the score.**

## Deliver
1. The artifact, in the spec's format — **Verdict: PASS / FAIL on the top line**, batch identity, the
   failure-mode table, six-dimension scores with the specific line or lead per flag, the M1–M8 checklist,
   the gate readout, and on FAIL the fix list naming its owner.
2. The Slack summary — verdict first; Honesty/fabricated-familiarity and gate violations above all else.
3. On PASS that later sends clean, it counts toward the `Instantly batch send` streak in
   `runtime/autonomy-matrix.md` — **counts only, never rungs**, updated at the weekly eval review.

## Guardrails
- **Reports only.** Never edit the copy, the campaign, another agent's SOP, or anything in Instantly.
  Kolby scores; Reilly/Michelle fix; the Founder sends.
- **A PASS is voided by any later copy edit or re-stage** — say so in the artifact, so nobody sends on
  a stale PASS.
