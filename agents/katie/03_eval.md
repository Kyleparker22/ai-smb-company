# Katie — Stage 3: Eval / gates / watchdogs

## Eval set (v0)
Run on each weekly content brief.

### 1. On-voice
- **Test:** Drafts read like the Founder — concise, direct, outcomes-framed, no buzzword salad, no emoji unless organic.
- **Target:** 100% pass the style guide.
- **Measurement:** Style-guide checklist per piece; the Founder's edits tracked as the ground truth.

### 2. Moat-anchored
- **Test:** Every piece sells the moat layer (reliability/eval/observability/trust), never the tooling.
- **Target:** 100%.
- **Measurement:** Each piece names which moat angle it advances.

### 3. Ready-to-publish
- **Test:** Drafts need a yes, not a rewrite.
- **Target:** the Founder publishes ≥1 piece/week with minimal edits.
- **Measurement:** Edit distance between draft and what's published; publish count.

### 4. Non-repetition
- **Test:** Theme differs from the prior 2 weeks; follow-up angles generated.
- **Target:** 100%.
- **Measurement:** Compare against the last two `loops/content/` artifacts.

### 5. Distinctiveness
- **Test:** "If anyone selling AI consulting could have written it, reject it."
- **Target:** 0 generic pieces shipped.
- **Measurement:** Distinctiveness check per piece before it ships.

## Approval gates
Mapped to the rung model in `02_build.md §Autonomy` (standard: `processes/autonomy-matrix.md`).
- **Pick theme, draft content, write artifact, post internal `#all-yourco` notice** → full autonomy (**R3**).
- **Publish anything externally** (LinkedIn/X/newsletter/blog) → **human-must-approve (R1)**; advances to **R2** (auto + notify + reversible) on Kolby's clean eval record, capped there.
- **Any claim about results/clients/metrics** → human-in-loop (**R1 hard floor** — pre-revenue: none unless real + approved).

All gate decisions logged in `gates/` with a one-line audit trail.

## Watchdogs (runtime guards)
- **Generic-content watchdog:** a draft that could've been written by any AI-consulting account → reject and redraft.
- **Repetition watchdog:** same theme as either of the last 2 weeks → vary it.
- **Overclaim watchdog:** any fabricated result, metric, or case study → block (none until real + approved).
- **Off-moat watchdog:** a piece that sells tooling instead of the moat → rewrite.

## Pre-go-live checklist
- [x] Eval set defined (this file)
- [x] Content loop SOP exists
- [ ] First brief produced as Katie, judged on-voice + distinct by the Founder
- [ ] Confirm publish gate holds (drafts only until the Founder says go)

## Iteration plan
- After each week: feed the Founder's edits back as voice-calibration; tighten the style guide.
- Once publishing connector lands (v1): track engagement/inbound by theme; double down on what works.
- When Reed demos and Pickle case studies exist: repurpose them into multi-format campaigns (v2).
