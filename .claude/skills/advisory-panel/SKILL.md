---
name: advisory-panel
description: Use when a major decision needs multi-perspective stress-testing (pricing, new offering, launch-gate, positioning, big build), or on Brett's quarterly full-company review. Simulates a panel of named AI/business minds — each grounded in their real public framework — against yourco's CURRENT state, and reports only convergences and changes. NOT for routine weekly ideas (that's Brett's normal loop) or for anything client/public-facing.
---

# advisory-panel — the simulated expert review panel

## What it is (and isn't)
A structured perspective-taking tool: channel named experts' *public frameworks* (books, essays,
talks) against yourco's actual repo state and report where independent frameworks converge. It is
**not** an oracle and **never** an endorsement — these people have not reviewed yourco, and no
external surface may ever imply they have (see the external-surface rules in CLAUDE.md). Internal
thinking tool only. Origin + first runs: `decisions/2026-07-20_advisory-panel-skill.md`,
`loops/_advisory/2026-07-20.md`.

## When
- **On-demand (the higher-value mode):** before a major decision ships — a pricing change, a new
  offering, a launch-gate call, a big platform build, a proposal that's stalling. Run the *relevant
  sub-panel only* (5–8 reviewers), scoped to that decision.
- **Quarterly (Brett):** first Friday of Jan/Apr/Jul/Oct, Brett runs the full mixed panel as part of
  his ideas loop (`processes/loops/brett-ideas.md` §Quarterly panel).
- **Retire test:** if a run's output changes no decision, say so in the artifact; two consecutive
  no-effect runs → recommend retiring or re-rostering the panel to the Founder.

## The roster (pick by decision type; rotate freely, ~5–8 for scoped runs, 12–16 for quarterly)
- **Technical/platform:** Sutton (bitter lesson / scaffold rot) · Karpathy (autonomy sliders, ground-truth
  evals) · Chollet (novelty/generalization limits) · Willison (prompt injection, lethal trifecta,
  publish-the-security-model) · Weng (agent architecture: planning/memory/tools) · Olah-Nanda
  (explainability) · Amodei (gated autonomy scaling) · Bengio (oversight floors) · LeCun (plan-free
  short-step workflows) · Hassabis (client-visible evals).
- **Sales/commercial:** Enns (paid diagnostic, never free) · Dixon-Adamson/Challenger (teach-tailor-
  **take control**) · Voss (no-oriented questions, calibrated questions) · Blount (pipeline discipline)
  · Ross (specialized outbound roles) · Rackham/SPIN (implicit→explicit need) · Hormozi (offer
  construction, moat-backed guarantee) · Dunford (positioning, vertical proof assets) · Baker
  (expertise pricing).
- **Strategy/operators:** Bezos (working backwards, flywheel) · Buffett-Munger (moat vs revenue,
  pricing power) · Thiel (distribution ≥ product) · Christensen (jobs-to-be-done) · Godin (the story
  as permission asset) · Graham (do-things-that-don't-scale, launch early) · Collins (bullets before
  cannonballs) · Cuban (sales cures all) · Huang (long-game conviction) · Sanchez (boring-business
  beachhead, equity) · Martell (founder-time leverage).

## Steps
1. **Step 0 — read the prior artifact(s).** `loops/_advisory/` newest first. The diff contract: this
   run may only report findings that are **new, escalated, resolved, or reversed** since the last
   run. Restating a standing finding verbatim is a contract violation — reference it in one line in
   the Standing table instead.
2. **Classify the decision, and say if it was named wrong** (added 2026-08-24). Before picking anyone,
   state in one line what kind of problem this actually is:

   > **distribution** (nobody knows we exist) · **product** (they know and don't want it, or want it
   > and don't stay) · **focus** (too many things, none working) · **people** (hiring, firing,
   > performance) · **risk** (expensive or hard to reverse) · **money** (pricing, spend, runway) ·
   > **positioning** (a competitor, a crowded market, being copied)

   Then **say plainly if the Founder misdiagnosed it, and quote the words in his own description that give it
   away.** A run that accepts the framing it was handed has already lost most of its value: the panel
   was assembled to answer the wrong question, expertly.

   **What this check can and cannot do — state the limit, don't oversell it.** It catches a
   *contradiction already present in the description*: "you called it growth; your own numbers say
   month-one churn." It **cannot** catch what is absent. `processes/autonomy-matrix.md` §R1.5 is
   explicit that a correlated reviewer never catches a shared wrong premise, and this panel is a
   correlated reviewer. So the check is only as good as the evidence handed to it — which makes the
   input rule below load-bearing rather than a nicety.

   **Input rule: numbers, not adjectives, and stated flat.** "Growth is slow" gives the panel nothing
   to contradict, so it re-labels the framing back and calls it analysis. "40 signups/wk → 44 over
   three months, 60% month-one churn" gives it something to disagree with. And describe the situation
   *without arguing for the preferred option* — the more a plan is sold in the telling, the more
   agreement comes back, which is the failure mode this whole skill exists to prevent. **If the
   decision hinges on a number that wasn't supplied, ask for exactly one, then proceed.**

   Note the two taxonomies are different axes and both are useful: these seven describe *what is
   broken*; `runtime/dri_twin.py` §CLASSES (pricing · scope · positioning · stack · roster ·
   legal-gate · spend · client-commitment · publish-send · process) describes *who may decide it*. A
   decision has one of each — name both when they matter.

3. **Wartime or peacetime.** One line, across all types: is yourco defending its life or extending a
   lead? Most bad advice is right-playbook-wrong-mode, and pre-revenue with an unsigned first client
   is not the same posture as a company protecting a position.

4. **Scope the panel.** Pick the sub-panel whose frameworks bear on the decision *as classified in
   step 2* — not as originally described. Say who was left out and why (one line).
5. **Ground every reviewer in current state.** Each persona's feedback must cite specific, current
   repo facts (files, numbers, pipeline state, decisions) — a review that could have been written
   without reading the repo is generic filler; cut it.
6. **Channel honestly, critiques first.** Apply each person's *actual* published framework, including
   where it contradicts yourco's choices or another reviewer. Disagreement between reviewers is
   signal — name it. No softening: the panel's job is heat.
7. **Extract convergences.** The product is where **3+ reviewers arrive at the same point from
   different frameworks**. Individual takes are the appendix; convergences are the report.
8. **End with 1–3 actionable items**, each with an owner and a smallest-version-this-week, rated
   Now/Next/Later/Park (Brett's honesty scale — most should not be Now).
9. **Write the artifact** to `loops/_advisory/<YYYY-MM-DD>[_<decision-slug>].md`: scope · panel ·
   Standing table (one-liners) · new/changed findings per reviewer (tight) · convergences ·
   actions · a "did the last run change anything?" line (feeds the retire test).
10. **Deliver.** Quarterly: Brett posts the convergences + actions to `#yourco-brett` (inside the
   approval gate; no external post, no email). On-demand in Cowork: report inline to the Founder.

## Gotchas (the mistakes this skill exists to prevent)
- **Repetition decay** — without Step 1's diff contract, every run rediscovers "sign the first
  client / raise prices / open the funnel" and the panel becomes skimmed noise.
- **Fabricated endorsement** — the #1 misuse risk. Internal artifact only; never quote the panel on
  any external surface, proposal, or social post. "What would Bezos say" is a thinking technique;
  "reviewed by a panel including Bezos" is a lie.
- **Generic-guru drift** — a persona reduced to their catchphrase adds nothing. If a reviewer's
  entry doesn't cite a repo-specific fact, delete the entry.
- **All-praise panels** — if a run produces no critique that stings, it wasn't channeled honestly;
  re-run the harshest three (Munger, Chollet, Enns are reliable heat sources).
- **Accepting the framing** (added 2026-08-24) — the panel answering the question it was handed,
  expertly, when the question was wrong. This is the failure the classification step exists to catch,
  and it is invisible in the output: a run that misdiagnoses reads exactly like a run that didn't.
  The tell is that step 2 said "yes, this is a growth problem" without quoting anything back.
- **Overselling the misdiagnosis check** — it catches contradictions *stated in the description*, not
  missing evidence. If the Founder brings no numbers, the check cannot fire, and a confident "you named it
  right" from a description containing no evidence is worth nothing. Say "not enough here to tell"
  instead; that is a real answer.
- **Headless constraint:** Brett's loop runs under the approval gate (no Bash) — the skill needs
  only file reads + one artifact write + a Slack post, all inside the gate. Keep it that way.
