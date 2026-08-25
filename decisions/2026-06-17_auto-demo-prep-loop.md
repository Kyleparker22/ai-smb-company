# 2026-06-17 — Auto demo-prep loop: confirming the flow (with one correction)

## The flow the Founder described
"10 prospects researched → added to an Instantly campaign → that triggers Reed to create 10 demo videos →
embedded in Email 1 per prospect → the Founder approves the 10 emails. Can it be a headless VPS loop?"

## Confirmed — with one important correction
**Mostly yes — but don't render a unique bespoke *video* per cold prospect.** That's the wrong unit:
- A full realistic video per prospect is **expensive, slow, and can't clear the credibility/eval gate unattended**
  (the realistic-video gate, `2026-06-17_Reed-realistic-video-openmontage.md`, requires human review; and
  OpenMontage's CLI is **Bash-denied on the headless runtime**). Auto-rendering thousands of bespoke videos is
  cost + risk with no payoff over a cheaper personalized artifact.

**The right architecture (same outcome, scalable + gate-safe):**
1. **One excellent hero demo per *vertical*** — Reed makes it once, human-approved once (realistic, full-blown).
   The landscaper hero video, the roofer hero video, etc.
2. **A cheap, instant *personalized demo* per prospect** — the "see yours" / `prospect-demo.html?p=<slug>` page,
   generated from the prospect's own data (name, company, vertical, their numbers), wrapping the vertical hero
   video. This is data-driven and near-free — *this* is what scales to 10 or 10,000.
3. **Email 1 embeds that per-prospect `demo_url`** — already how the sequence works (`processes/outbound/sequence-copy.md`:
   Touch 1 leads with `{{demo_url}}`, "no demo, no send").

So Reed isn't rendering 10 videos on a trigger; he's produced the *vertical* video once, and the loop spins up
10 *personalized pages* (instant) pointing at it. Same felt outcome for the prospect, a fraction of the cost/risk.

## Can it be a headless VPS loop? Yes — for the PREP, not the send
A **demo-prep loop** is a clean fit for the always-on runtime:
- **Trigger:** new prospects appear in an Instantly campaign (or a fresh `sadie-intent.json` / sourcing batch).
- **Does (headless, safe):** for each prospect, generate their personalized demo (slug + data), confirm the
  vertical hero video exists (flag Reed if a vertical has none yet), write the `demo_url` merge var back to
  their Instantly record, and leave the campaign **paused**.
- **Does NOT (by gate, on purpose):** **send.** The approval gate denies send/Bash; the loop *prepares* and stages
  — **the Founder approves the campaign in Instantly**, which is the "approve the 10 emails" step. Connected ≠ auto-send.
- **Does NOT:** render bespoke per-prospect video (see correction); a missing vertical hero video is flagged to
  Reed (human-made, approved once), not auto-generated unattended.

So the honest version of the Founder's ask: *research → loop auto-builds each prospect's personalized demo + writes it into
Email 1 → campaign staged paused → the Founder one-approves the batch.* The video isn't per-prospect; the **personalization** is.

## Dependencies before this loop can run (not yet built)
- **`instantly.py`:** add (a) read leads in a campaign, (b) **write per-lead custom/merge vars** (`demo_url`). Today
  it has `warm_replies`, `create_campaign`, sequence loading — not per-lead merge-var writes.
- **The per-prospect demo generator:** `prospect-demo.html?p=<slug>` fed by CRM/enrichment data — overlaps the
  "Instant Employee — Mode B" generation endpoint already on the launch runbook (`processes/launch-runbook.md`).
- **Vertical hero videos:** Reed produces one per active vertical (the 13 in `snapshot-config.js`), approved.

## Owners
**Kemba** (the loop) · **Reilly** (campaign staging) · **Webb** (the demo generator / Mode B) · **Reed** (the
per-vertical hero videos) · **the Founder** approves the staged batch. Loop SOP + prompt drafted now
(`processes/loops/demo-prep.md`, `runtime/prompts/demo-prep.md`); **systemd activation waits on the dependencies +
the launch-gate** (no live outbound until then anyway).

## Status
Design set 2026-06-17. Staged. The loop's value is real but it's **gated behind the demo generator + the Instantly
merge-var write + launch** — sequenced after the core launch, not a reason to slow it.
