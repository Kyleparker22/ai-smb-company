# Decision — Autonomy-by-default is the standard (internal + external)

**Date:** 2026-06-25 · **Owners:** Brett (strategy) + Kolby (eval/enabler) + Rafi (controls) + Kimi (runs it) · **Status:** settled standard; per-action advancement is eval-gated · **Extends:** `decisions/2026-06-12_autonomy-ladder.md`

## The call
Autonomy-by-default is now the **standard operating model for every yourco agent — our own OS and every client OS.** The default trajectory of every action is **full autonomy**, with the human's routine time trending to **zero**. The 2026-06-12 ladder removed *the Founder* from the build; this makes the same earn-it model **universal and two-sided** — it also removes the **client's** routine human, and applies it to yourco's **own internal agents**. Framework: `processes/autonomy-matrix.md`.

## What "standard" means (and what it does NOT)
- **Means:** every action is governed by the Autonomy Matrix; the goal is always the top rung; we engineer toward zero human touch; the reliability layer (eval + guardrails + observability + rollback) is the control, not a person.
- **Does NOT mean:** flipping every action to unattended today. New/unproven and irreversible actions **start gated (R1)** and climb on Kolby's eval evidence. The internal approval gate (`runtime/headless-settings.reference.json` — deny send/delete/Bash) **stays as the R1 floor** until evidence earns each action up. Making autonomy "the standard" makes the *earn-it model* universal — it does **not** delete safety. **Day-one full autonomy on high-stakes actions is the one move that kills the moat.**

## Internal = the proving ground
yourco runs the matrix on its **own** OS first (`runtime/autonomy-matrix.md`). Today: read/edit/Slack-post are autonomous (R3); Gmail-send/delete/Bash are gated (R1). As Kolby's eval-vs-reality record accumulates zero-incident runs, the Founder advances specific actions (Gmail-send → R2 first). We don't ask a client to trust unattended autonomy we haven't first earned on ourselves — the literal "we run yourco on its own agents" proof.

## Why this strengthens the moat (doesn't dilute it)
Safe full-autonomy *requires* the eval/guardrail/observability layer — exactly what no-code operators can't build. "We run it unattended **because we have the evidence to prove it's safe**, and you hold the kill switch" is the most defensible, highest-margin version of the product. yourco absorbs more risk → **premium pricing**; the contract carries an **error-budget SLA + liability terms** (Ray + Rafi).

## What this changes in the OS
- New canonical framework: `processes/autonomy-matrix.md` (rungs + controls + advancement + default starting rungs).
- Per-client instance template: `clients/_yourco-template/autonomy-matrix.md` (filled in at discovery; the client sets appetite + holds the kill switch).
- Internal instance: `runtime/autonomy-matrix.md` (yourco's own actions → rung; reflects the live gate as the R1 floor).
- **Kolby** owns the eval-vs-reality record that gates advancement; **Kimi** runs each build at its current rung; **Rafi** owns the guardrail/controls posture; **Ray** owns the liability terms; **the Founder** sets the advancement threshold + holds the internal kill switch.
- `CLAUDE.md` moat section names autonomy-by-default as the standard.

## Trigger / revisit
Per-action advancement is continuous (Kolby's weekly eval review). Revisit the *thresholds* if an incident occurs (hold/reset that action) or when the first client picks a high ceiling — that's where the SLA + liability terms get locked with Ray.

## Trip-wire
- **Review:** 2026-12-25
- **Overturn if:** the *thresholds* need re-cutting — an incident occurs on a tracked action (hold/reset that action), or the first client picks a high ceiling, which is where the SLA + liability terms get locked with Ray.
- **Check:** `trustIncidents > 0 or drillsUndetected > 0`
- **Check covers:** the incident half, read live from the Trust Ledger (`loops/_trust/`) — a recorded incident on any action, or an immune drill the OS failed to catch inside its window. The client-ceiling half fires on a signature, not a metric.
