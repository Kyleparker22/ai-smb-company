# 06 — The agents

> **Build step 06.** Nothing here is done yet. Where this page shows a filled-in value, that is
> the source company's — replace it with yours.

## What an agent actually is here

Not a chatbot and not a persona. An agent is **five things**: a docs folder (`agents/<name>/`), a loop
prompt if it runs on a schedule, an entry in the sanctioned registry, a rung on the autonomy matrix
that says what it may do without asking, and — since 2026-08-25 — **one number it owns**. Miss any one
and you have something that looks like an agent and is not governed like one.

**The number is the fifth thing because for the first year there were only four.** Twenty-seven agents
and not one of them owned a metric; three unrelated inputs pointed at that on the same day
(`decisions/2026-08-25_one-number-and-agent-metrics.md`). Each agent's number lives in
`runtime/agent-registry.json` → `agent_metrics` — in Rafi's sanctioned baseline deliberately, so a
number an agent owns cannot be quietly changed — and is computed live on HQ → Agents. Four rules make
it honest: every agent in `agents/` must have one (invariant-checked); **did-it-run is not an outcome**
(only Atlas may own loop liveness, because liveness is its job); an unmeasurable metric must name the
one thing missing; and it must ladder `direct` or `enabling` to the north star, because an agent whose
number does neither is a retirement question.

Roster, scope, and approval per agent: `04_agent_roster.md`. Operating model: **siblings, the Founder
conducts** — Melanie is the conductor/CEO-in-training, not a boss.

## Wiring one — follow the checklist, do not improvise

`runtime/agent-wiring-checklist.md`: docs → roster → dashboard → **the number it owns** → channel →
listener map → registry → invite the control bot → restart. Skill: `.claude/skills/wire-new-agent/`.

It exists because wiring gets **partially** done. An agent with docs and no registry entry is invisible
to the governance watchdog; one with a channel and no listener map cannot be commanded.

## The Slack control surface

Each agent posts to its own `#yourco-<agent>` channel; the digest goes to `#all-yourco`. A Socket-Mode
listener (`runtime/slack-agent-listener.py`) lets the Founder command any agent *in its channel* and get a
reply *as that agent* — the Founder-only allowlist, approval gate preserved, injection-hardened. The control
bot is `atlas`; one app posts as every agent. Map: `runtime/slack-channels.md`.

## Autonomy — the part that is the actual business

`processes/autonomy-matrix.md`. **The default trajectory of every action is full autonomy, earned
per-action on evidence, with the human's routine time trending to zero.**

| Rung | What happens | What replaces the human |
|---|---|---|
| **R0** | read/observe only | nothing needed |
| **R1** | drafts; a human commits | the human — the floor for anything unproven or irreversible |
| **R1.5** | an independent agent with a *different lens* clears it | a correlated reviewer — see the limit below |
| **R2** | fires automatically, logged, **undoable** in a window | eval gate + rollback |
| **R3** | fires unattended; human sees exceptions only | eval gate + guardrails + watchdog + kill switch |

**"No human checkpoint" ≠ "no control."** The control migrates off the human onto the reliability
layer — which is exactly the layer no-code operators cannot build, so full-autonomy-done-right is the
premium tier, not the dilution of the moat.

**Day-one full autonomy on high-stakes actions is the named moat-killer.** R1 is the floor until
evidence earns each action up. Promotion needs a streak **and** calibration evidence — a clean streak
alone cannot tell reliable from lucky.

⚠️ **R1.5's honest limit, stated in its own doc:** a correlated reviewer never catches a shared wrong
premise. It is scoped to what a second lens can actually catch, and it never moves a rung.

Four decision classes **can never earn autonomy**, by category, no matter the record — `legal-gate`,
`publish-send`, `spend`, `client-commitment` (`runtime/dri_twin.py` §NEVER_EARNS).

## Training and coaching them — and the one role that is refused

- **Connectors**: a 14-lesson curriculum where **training gates advancement** — you cannot hold a rung
  until its training is done, in addition to the CRM evidence (`crm/connector_training.py`).
- **Advisors**: a 6-lesson curriculum (`processes/advisor-training/`).
- **Practice**, as distinct from curriculum: `crm/coach.py` serves authored drills; an agent judges
  free-text answers against the rubric. Self-marked and judged records never merge.
- ⚠️ **Partners are refused.** Their duties are undefined — the OA's own open gap #8 — so a partner
  curriculum would author Schedule C-1 by the back door, without counsel. The refusal states its own
  unblock condition and disappears the day D5 is answered.

## The substrate under all of it

`decisions/2026-08-13_agent-substrate-upgrade.md` — trigger-scoped learnings, the anti-library, a run
journal capturing per-run cost, provenance-typed context, failure-traces-to-skill-patches, agent
payroll, R1.5, calibration-gated autonomy, decaying approvals.

⚠️ **Most of it is wired and unproven.** All four stores started empty and cannot be backfilled. If you
copy this shape, copy the honesty too: "wired" is not "working."

## Done when

**one agent exists in the registry, holds a rung, and has produced a draft you approved.**

If you cannot point at that, the step is not finished — do not move on.
