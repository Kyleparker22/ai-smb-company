> ⚠️ **EXAMPLE OUTPUT — not yours.** This is one run of this loop from the company this
> template was extracted from, kept so you can see the shape of what the loop produces.
> The dates, numbers, and findings describe **someone else's business**. Delete this file
> the first time your own loop writes a real one.

# Triage — 8 inputs: goal grids, 10 frameworks, Semantica, priming, 9 KPIs, 2 screenshots (2026-08-24)

Batch-triaged per `.claude/skills/tool-triage/`. Filter: does it move revenue or the reliability layer
in the next 60 days · does it strengthen the moat · does it clear the compliance posture. Default
verdict is **park**; adoption is the exception that clears all three.

## The state everything was triaged against (verified, not assumed)
**0 live clients · $0 MRR · 3 deals in motion (34 on the bench, 37 total) · 41 companies · 27 agents ·
9 HQ goal metrics · 0 agents owning a number** — `runtime/agent-registry.json` has no metric/kpi/target
field at all.

> **Corrected 2026-08-25.** This page first read *"37 deals in motion"*. Thirty-seven is the total;
> `dashboard/server.py` classifies `pre-convo` as bench, and 34 of the 37 sit there. **Three** are in
> motion. Same class of error as the 2026-08-13 stage-rename drift, and it survived because the
> number was repeated rather than computed. Every count below is corrected.

## THE CONVERGENT FINDING — three separate inputs point at one gap
The 9×9 grid's centre cell, OKR's single Objective, and Eric Siu's operating rules *"Every Role Owns a
Number"* + *"Reports Outcomes, Not Activity"* are the same observation arriving three ways:

> **yourco has nine goals, which is zero goals — and twenty-seven agents, none of which owns a number.**

The WBR work already reached this from a fourth direction (all nine goal metrics are *outputs* the Founder
cannot move on a Tuesday). Four independent routes to a gap the OS had half-found is the strongest
signal in the batch, and it is the only thing here worth building.

## Verdicts

| Input | Verdict | Why |
|---|---|---|
| **9×9 goal grid** (Mandala / Ohtani) | **Steal the centre cell, skip the 81** | yourco's failure mode is not too few planned actions — it is 3 deals in motion, 0 signed, ~20 loops, 27 agents, 24 surfaces. A grid that generates 64 more actions is the wrong medicine for this illness. The *one central goal everything ladders to* is the missing half. |
| **Garry Tan's rules** | **Confirmation, one real gap** | "Pure SaaS is no longer a wedge" validates the operated-OS position; "be multiples of yourself with agents" is literally the model; conflict → advisory panel + `prosecution.py`; mistakes → `rejections/` + failure-traces → skill patches. **Gap: "find your community"** is unaddressed as *founder support* — the repo treats local community purely as a prospecting channel. Non-commercial, real, the Founder's to act on. |
| **SWOT** | Skip | Four lists nobody actions. yourco already has strictly better: advisory panel, prosecution, premortems. |
| **Business Model Canvas** | Skip | Every block already exists with more specificity in `CLAUDE.md` / `01_company.md` / `06_business-plan.md`. Filling a canvas duplicates canonical facts onto a new surface — the #1 drift failure. |
| **Lean Canvas** | **ADOPT — scoped to `offerings/`** | The one framework built for pre-revenue assumption-testing. yourco holds **76 prototypes + 33 specs, all n=0, none sold.** A one-page canvas per offering forces the question those folders' own READMEs already admit. |
| **Porter's Five Forces** | Skip | Market-structure tool for industry entry; Brett's competitive watch covers the narrower real question. |
| **Value Chain** | Skip | The 8-pillar module taxonomy *is* yourco's value chain, already applied to clients. |
| **OKR** | **Partial — the O, not the ceremony** | One Objective + 3 leading, ownable Key Results fixes the nine-goals problem. Full OKR ritual at one human + agents is overhead. |
| **Balanced Scorecard** | Skip | Built for multi-division orgs. HQ's Evidence door already does "beyond financial" *and* refuses when it cannot support a number. |
| **McKinsey 7S** | Skip | Org-alignment diagnostic for orgs with org complexity. yourco is one person and a fleet. |
| **Ansoff Matrix** | Skip as a system; its conclusion is already known | It would say: penetration is at zero (3 live conversations) while you diversify into 76 prototypes, Care and Conduit. The repo has made that finding repeatedly. |
| **BCG Matrix** | Skip | Needs market share + growth across a portfolio. yourco has neither. |
| **Semantica** | **Steal the pattern, not the dependency** | Open-source MIT graph layer; decisions as first-class, provenance-typed, precedent-searchable nodes; deterministic reasoning under the LLM. Adopting it violates the framework stance (a runtime to own, secure and keep alive). But it names a real defect: **`decisions/` is a graph pretending to be a folder** — 8 of 13 wikilinks dangle and no agent traverses them (found this morning, `3c4ba61`). Fix the links; do not install the infrastructure. |
| **Kahneman priming** | **Skip the strong claim — keep the mechanisms** | ⚠️ Social priming is the epicentre of the replication crisis. **Kahneman himself** warned in 2012 that a "train wreck" was looming for the field, and later said he had placed too much faith in underpowered studies; the classic effects largely failed to replicate. The weaker cousins that *do* replicate — framing and anchoring — yourco already runs: the two-sided proposal frames cost against return, DESIGN.md and writing-rules set the register, the console frames autonomy as earned. **Ethics note:** "influence how people think and act via subtle cues" sits badly beside a glass-ledger brand whose moat is numbers that refuse to overstate. |
| **The 9 KPIs** | **ADOPT the definitions, REFUSE the numbers** | **7 of 9 are undefined at n=0** — NRR, LTV, CAC, LTV:CAC, churn and retention all need customers; burn multiple divides by net new ARR, which is zero. Only EBITDA and operating cash flow compute, and both reduce to "what are we spending and how long does the money last." Define all nine **now, with refusal conditions**, so they compute correctly the day client #1 signs and say *"not yet — needs N customers"* until then. |
| **Eric Siu's AI-native agency map** | **Confirmation — yourco is ahead on most layers** | Diagnosis Layer → Bella's audit (ahead). Agent Fleet → 27 agents (ahead). Knowledge + Memory → CLAUDE.md, learnings, decisions, rejections, attribution log (ahead). **Governance Layer → autonomy matrix + approval gate + counsel gates; this is the moat, and his map treats it as one box.** Human Judgment → "the Founder sends; agents draft." Pod of One → literally the operating model. **Gaps: the Measurement Layer's north-star metric, "Every Role Owns a Number", and "Reports Outcomes, Not Activity"** — all three are the convergent finding above. |

## What this batch is worth, honestly
**One build** (the single number + agents owning numbers) · **one adopt** (Lean Canvas on `offerings/`) ·
**one definitions job** (the KPI set with refusals) · **two link fixes already logged elsewhere.**
Everything else is a framework yourco already has a better, evidence-backed version of — which is a
good result to be able to state, not a disappointment.

**Beachhead guard:** none of this closes a deal. **3 in motion, 0 signed** is still the only number
that matters, and three of these inputs said so in three different vocabularies.
