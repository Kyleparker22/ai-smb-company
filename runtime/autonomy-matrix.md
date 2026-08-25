# Autonomy Matrix — yourco's own OS (internal instance)

> **Status: LIVE REFERENCE** — yourco's own instance of the standard in `processes/autonomy-matrix.md`. Rungs here are claims about yourco, not clients.

> yourco runs the standard (`processes/autonomy-matrix.md`) **on itself first** — the proving ground before any client trusts unattended autonomy. Reflects the live approval gate (`runtime/headless-settings.reference.json` + the host `~/.claude/settings.json`) as the **R1 floor**. Owners: Kolby (advancement) + Rafi (controls) + the Founder (kill switch + threshold). Standard set 2026-06-25 (`decisions/2026-06-25_autonomy-by-default-standard.md`).

## Current rungs (2026-06-25)
| Action | Current rung | Ceiling | Advance when |
|---|---|---|---|
| Read / Glob / Grep / WebSearch | **R3** | R3 | — (inherently safe) |
| File Write / Edit (in git) | **R3** | R3 | — (reversible) |
| Slack post (agent channels + digest) | **R3** | R3 | — (reversible) |
| Gmail read / search | **R3** | R3 | — |
| Calendar read | **R3** | R3 | — |
| Calendar create/update (the Founder's own holds) | **R2** | R3 | 2 wks · 0 conflicts/errors → R3 |
| Gmail label / archive / mark-read | **R2** | R3 | 4 wks Jim · 0 mis-archives → R3 |
| **Gmail send** | **R1 (gated)** | R2 | Kolby eval record + the Founder threshold; external sends climb first to R2 (auto+notify+reversible) |
| **Instantly batch send (outbound)** | **R1 (gated)** | R2 | pre-send eval gate record (`loops/outreach-eval/`, spec `processes/outbound/pre-send-eval-gate.md`) + the Founder threshold; OtherVenture-gated until launch — every batch needs a dated PASS artifact, the Founder clicks send |
| **Delete / destroy** | **R1 (gated)** | R1 | stays gated by design |
| **Bash (shell)** | **R1 (denied)** | R1 | stays denied — closes the gate-bypass hole |

## The path
The gate (`deny send / delete / Bash`) is the **R1 floor, not the ceiling.** As Kolby's weekly eval-vs-reality record accumulates zero-incident runs, the Founder advances specific actions — **Gmail-send → R2** (auto + notify + reversible window) is the first candidate once Jim's drafting has a clean track record. Any incident holds/resets. This is the **same climb we sell clients**, proven on us first — which is why "we run yourco on its own agents" is a real proof, not a slogan.

## Streak ledger (Kolby updates each Sunday eval-review; the Founder promotes)
Per the streak rule (`processes/autonomy-matrix.md` §Advancement, 2026-07-05): a promotion needs **N consecutive clean evals with real uses**; any incident resets the streak to zero. Kolby owns the counts below (the one part of this file he edits — counts only, never rungs); rung changes stay the Founder's.

| Action (climbing) | From → to | Threshold | Streak (clean weeks · uses) | Last incident / reset |
|---|---|---|---|---|
| Calendar create/update (the Founder's holds) | R2 → R3 | 4 clean wks · ≥10 uses (per rungs table: min 2 wks) | **1 · 2** — first counted wk (07-06→07-12): Brett warm-sends block (07-06) + Jim Nick-POC hold (07-07), both placed clean, 0 conflicts/errors | — |
| Gmail label / archive / mark-read | R2 → R3 | 4 clean wks · ≥10 uses | **1 · ≥10** — first counted wk: inbox-triage Mon–Fri, ≥10 archives/labels (07-10 alone = 7), **0 mis-archives** (Hostinger failed-payment alert correctly left un-archived) | — |
| Gmail send (Jim, external) | R1 → R2 | 8 clean wks · ≥20 clean drafts (draft-vs-outcome) | 0 · 0 — no new external drafts this wk (inbox 100% vendor noise, 4-wk prospect drought); 18 carried drafts all gated/unsent | — |
| Instantly batch send (outbound) | R1 → R2 | 6 consecutive PASS-gated batches sent clean (0 spam complaints · 0 brand incidents · reply rate in band) | 0 · 0 — pre-launch (launch-gate); counting starts at launch | — |

*(A clean week with zero real uses doesn't advance the streak — the action must have fired. Ledger opened at zero on 2026-07-05: prior clean runs predate streak tracking, so the count starts honest rather than reconstructed.)*

*Kolby review — 2026-07-05 eval-review: ledger opened today; this week's uses (06-29→07-03) predate the opening → not retroactively counted, per the principle above. Counts confirmed at 0·0 (no reconstruction). First counted window = 07-06 → 07-12, first tally at the 07-12 eval. Observed-but-uncounted this week: Gmail label/archive had a clean real-use week (Jim, ~5 daily runs, 0 mis-archives) — expect it to start accruing toward its R3 threshold once counting opens. Calendar create/update: zero real uses (no hold placed). No promotion recommendation.*

*Kolby review — 2026-07-12 eval-review (first counted window, 07-06→07-12): **Calendar create/update → 1·2** (Brett + Jim holds, clean). **Gmail label/archive → 1·≥10** (0 mis-archives; the discriminating correct call — leaving the Hostinger failed-payment alert un-archived — is itself evidence the labeler isn't blindly sweeping). **Gmail send → 0·0** (no new external drafts; drought inbox). **Instantly → 0·0** (pre-launch). No streak crossed its threshold (all need ≥4 clean weeks; this is week 1) → **no promotion recommendation.** Note: the watchdog's own 3-day timer self-outage (07-07→09) and the crm-autolog 07-10 no-fire are runtime/timer failures, **not** action-execution incidents on any tracked climbing action → they do **not** reset these streaks (different failure domain — flagged as coverage in the eval artifact, owner the Founder/platform).*

## The two new promotion inputs (2026-08-13)
Both apply to every row above, and both are wired but empty by construction today — which is the honest state, not a gap.
- **Calibration** (`python3 runtime/agent_calibration.py --gate "<action>" --agent <name>`): a promotion needs the streak **and** a calibration record. yourco has **0 resolved forecasts**, so every gate currently returns `insufficient-evidence` — neither a pass nor a fail. Agents start placing bets with `runtime/trust_ledger.py --forecast "<subject>" --p <0-1> --agent <name>`, resolved later; five per agent makes the gate answerable.
- **Decaying approvals** (`python3 runtime/decaying_approval.py`): only **Calendar create/update** and **Gmail label/archive** are at R2 and therefore decay-eligible at all. Gmail send and Instantly batch send are R1 and are refused by the eligibility check itself — silence on those means **no**, permanently, until they climb on their own evidence.

## What stays gated regardless of evidence
- **Bash / shell** on the runtime (the load-bearing deny — an agent that can shell can bypass every other control).
- **Hard delete / destroy** of data.
- Anything a future host change would make irreversible without a rollback path.
