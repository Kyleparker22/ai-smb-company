# Pre-send eval gate (outbound batches)

> **Owner: Kolby** (scores) · **Reilly** (requests + fixes) · **the Founder** (approves the send).
> The rule in one line: **no Instantly batch gets sent without a dated PASS artifact from this gate.**
> This closes the one gap in the outbound engine: copy is staged paused in Instantly, but nothing scores the *rendered batch* (copy × leads × merge vars) before the Founder's send click. The gate is the moat applied to our own outbound — the same standard we sell.

## Where it sits in the staging flow
The existing flow (`processes/outbound/proof-led-outbound-engine.md`, `runtime/instantly.py`):

1. Source (Vibe) → qualify → CRM (`runtime/sourcing.py`)
2. `instantly.py --create` — campaign from `sequence-copy.md`, DRAFT/PAUSED
3. `instantly.py --stage` — leads into the campaign
4. `instantly.py --write-demos` — per-lead `{{demo_url}}` merge vars
5. **→ THE GATE (this doc) ←** — Kolby evals the staged batch, writes the artifact
6. the Founder reviews artifact + gates checklist → presses send in the Instantly UI (the one human action)

The gate runs **after** step 4 (merge vars must exist to be evaluated) and is a **required input to** step 6. Re-staging leads or editing copy after a PASS voids the artifact — re-run the gate.

## Trigger
**Event-triggered, not a timer** (activation-gated, like the per-client error sweep — there is nothing to eval until a batch is staged, and nothing sends until the launch-gate clears anyway).
- Reilly (or the Founder) requests it when a batch is fully staged: in Cowork, or via `#yourco-kolby` ("eval batch <campaign>").
- Post-launch, if batches become weekly-regular, promote to a runtime loop via `.claude/skills/add-runtime-loop/` — same prompt, timer-fired, self-gating on "is there a staged un-evaled batch."

## What Kolby reads
- `processes/eval-rubric.md` — the six-dimension standard (this gate is an *adaptation* of it, per the rubric's own client-adaptation precedent; the rubric itself is unchanged)
- `processes/outbound/sequence-copy.md` — the canonical Touch 1–4 + SMS copy
- `brand/writing-rules.md` + `brand/v0/brand-guidelines.md` — voice bar
- `instantly.py --leads "<campaign>"` output — the staged leads + who has a `demo_url`
- `crm/data.json` — dedupe + status cross-check
- `learnings/qa-eval/` + `learnings/outbound/` (Step 0 domains)
- Prior artifacts in `loops/outreach-eval/` (drift)

## Two layers: mechanical, then judgment
**Error analysis first** (per the rubric's method): read rendered samples, note problems plainly, group into failure modes, count. Then score.

### Layer 1 — mechanical checks (binary, scriptable; any fail = batch FAIL)
| # | Check | How |
|---|---|---|
| M1 | Campaign is DRAFT/PAUSED | `--campaigns` status |
| M2 | Every lead has non-empty `first_name`, `company_name`, `email` | `--leads` output |
| M3 | Every lead has a `demo_url` merge var | `--leads` output |
| M4 | Sampled `demo_url`s resolve (HTTP 200) **and** render that lead's business name | fetch N ≥ 10 (or all if ≤ 10) |
| M5 | No lead already `sent/replied/booked/dead` in the CRM or present in a prior campaign | cross-check `crm/data.json` + prior batch artifacts |
| M6 | Batch size ≤ the approved cap for this batch | Reilly's staging note |
| M7 | Opt-out mechanism present in the copy; sender identity is real (the Founder, yourco, reply-to works) | copy read (CAN-SPAM floor) |
| M8 | SMS touches only if Rafi's TCPA/10DLC gate is cleared | `processes/counsel-gates.md` |

*(Build note: M1–M5 belong in `instantly.py --eval-batch "<campaign>"` as a mechanical pre-pass that emits a JSON summary Kolby reads — small addition, same stdlib style. Until built, Kolby runs them by hand from `--leads` output.)*

### Layer 2 — the six dimensions, outbound-adapted (2/1/0 each; any 0 fails the batch)
1. **Grounding / accuracy** — every claim in the rendered copy is real for *this* lead: the demo exists and is theirs, the ROI math uses stated-assumption numbers, "live in 48 hours" is a commitment we can keep. *(0: a demo link that 404s or shows the wrong business; any invented fact about the prospect.)*
2. **Honesty / credibility gate** — pre-revenue rules hold: no fabricated metrics, testimonials, client counts, or manufactured familiarity ("loved your recent post" with no post). "I built this for you" only where the demo is verifiably built. *(0: any fabricated proof — the cardinal rule, and the exact failure mode that kills cold outreach trust.)*
3. **SOP & format adherence** — rendered touches match canonical `sequence-copy.md` (no silent drift between the file and what Instantly will send); sequence timing/order intact; merge vars render (no `{{company_name}}` leaking raw). *(0: staged copy diverges from the canonical file, or a raw merge var in a rendered preview.)*
4. **Brand voice** — `brand/writing-rules.md`: plain words, em-dash cap, read-aloud test, lowercase `yourco`, outcomes not features. External-surface rules: **no internal agent names** (function only — "an AI front desk," never the internal roster: Reilly/Kolby/Bella/etc.), **no prices** (proposals only). **Persona carve-out (`decisions/2026-07-22_persona-on-1to1-surfaces.md`):** the **client-facing demo persona** (Reese/Quinn/Sage) is **allowed** on 1:1 surfaces (outbound, prospect demo, proposal) — it is *not* an internal-agent name. Only `04_agent_roster.md` names are banned here. Note the collision trap: prospect first-names rendered into the greeting (David/Jim/Ray/…) may match roster names — judge by context, don't auto-fail a greeting. *(0: a banned word, an **internal-roster** agent name in the body, or a price in outbound copy.)*
5. **Actionability** — one clear CTA per touch; the ask is small and specific; subject lines honest and concrete. *(0: competing CTAs or a deceptive subject.)*
6. **Closed-loop & gates** — campaign paused; the send checklist is actually satisfiable: launch-gate (`processes/launch-gate.md`), domain warmup ≥ 90%, Polo's pricing lock for the vertical, Rafi where SMS; leads deduped (M5); batch logged so replies can graduate via `promote-warm-lead`. *(0: any gate not cleared, or an unlogged batch — a gate violation is also a security flag.)*

**Scoring mechanics are the house standard:** sum/12; 11–12 clean; 8–10 acceptable with flags; ≤7 or any 0 = FAIL. When unsure, fail it and surface it.

### Sampling
- **Copy:** 100% — all 4 touches (+ SMS if present), read as rendered previews, not just the source file.
- **Leads:** mechanical checks (M2–M5) on 100%; judgment read on rendered previews for min(10, all) leads, random. Any judgment failure in the sample → widen the sample before scoring; a second failure of the same mode → batch FAIL with the mode named.

## The artifact
`loops/outreach-eval/YYYY-MM-DD_<campaign-slug>.md`:
- **Verdict: PASS / FAIL** (top line), batch = campaign name + lead count + staging date
- Failure-mode table (taxonomy + counts — this matters more than the score)
- Six-dimension scores with the specific line/lead for every flag/fail
- Mechanical checklist M1–M8 (✓/✗ each)
- Gate checklist state (OtherVenture / warmup / pricing / Rafi) as read from the tracker docs
- Fix list for Reilly/Michelle, if FAIL

Plus a 3–5 line summary to `#yourco-kolby`, fails first, owning agent named — same format as the weekly eval review.

## Who blocks (the Kolby constraint, preserved)
Kolby **scores and reports only** — he does not block, edit copy, or touch Instantly (unchanged from `eval-rubric.md`). The blocking is procedural: **the send checklist in `proof-led-outbound-engine.md` requires a dated PASS artifact for the exact staged batch.** No artifact or a FAIL → the Founder doesn't send; Reilly/Michelle fix and re-request. A PASS voided by later edits (copy change, re-stage) must be re-earned.

## Autonomy climb (why this gate is the product, not overhead)
This is the R1 floor for the `send outbound batch` action under the Autonomy Matrix. The eval-vs-reality record this gate produces — did PASS batches perform cleanly (no spam complaints, no brand incidents, reply rates in band)? — is exactly the evidence that earns the action up rungs on the streak rule:
- **R1 (now):** every batch → gate → the Founder approves → the Founder sends.
- **R2 (earned):** clean streak per the ledger → PASS batches auto-send with notify + pause-switch; FAIL still stops everything.
- **R3:** the gate itself is the approver; the Founder reads the scoreboard.
Kolby updates the streak ledger in `runtime/autonomy-matrix.md` per the existing eval-review SOP; rungs stay the Founder's. And the same gate, white-labeled, ships inside any client OS with an outbound module — we run our own standard first.

## Wiring checklist (wired 2026-07-20)
- [x] "Dated PASS artifact" rule added to `proof-led-outbound-engine.md` §6 (+ First moves step 5)
- [x] `loops/outreach-eval/` created (`_README.md` names the two artifact types)
- [x] Kolby gate prompt at `runtime/prompts/outreach-eval.md` (loop-contract footer; Step 0: `learnings/qa-eval/`, `learnings/outbound/`) — **on-demand, no timer**; promote via `add-runtime-loop` if batches become weekly-regular post-launch
- [x] `--eval-batch` mechanical pre-pass in `runtime/instantly.py` (M1–M5 → `loops/outreach-eval/<date>_<slug>.mechanical.json`; M5 = any CRM hit fails, since `crm/data.json` is warm+ only). Bash-side — Reilly/the Founder run it; headless Kolby reads the JSON and stops (missing-input) if absent
- [x] `Instantly batch send (outbound)` tracked at R1 in `runtime/autonomy-matrix.md` (rungs table + streak ledger: 6 consecutive PASS-gated clean sends → R2; counting starts at launch)
