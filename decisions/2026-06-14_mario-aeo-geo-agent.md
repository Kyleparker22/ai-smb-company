# Decision — add Mario, the answer-engine visibility agent (AEO/GEO)

**Date:** 2026-06-14 · **Owner:** the Founder + Katie/Webb (implementation) · **Status:** settled — agent in build
> **Renamed 2026-06-15:** this agent was originally named **Cora**; renamed to **Mario** (the Founder's call). Name only — charter, scope, and lineage unchanged. (File + `clients/` folder renamed to match.)

## Decision
Add a named agent, **Mario**, who owns yourco's visibility in AI answer engines (ChatGPT, Claude, Gemini, Perplexity, Google AI Overviews) — Answer Engine Optimization and Generative Engine Optimization. He audits where yourco is cited, who's winning the citations and why, and prescribes the content, schema, and off-site presence that move yourco into the cited set, scored over time.

## Context
Reviewed "The Agency" (a 147-agent Claude Code pack). Declined to install it — generic personas with no scope, owner, trigger, or approval gate pollute yourco's curated roster, and an yourco agent is a gated loop with an artifact, not a prompt file (same logic as the framework-adoption stance). Mined it for role ideas instead. Of its five highlighted agents, four were already covered: Reality Checker = Kolby + eval gates, Compliance Auditor = Rafi, Tax Strategist = Charles's tax-prep handoff, Whimsy Injector conflicts with the restrained brand. The fifth, the AI Citation Strategist, mapped to a real gap: AEO/GEO had zero presence in the workspace and no owner.

## Why it earns a slot
yourco sells AI implementation. The buyers most likely to ask an AI "who builds AI employees for my business" are yourco's buyers. If yourco isn't in those answers, it's invisible to the fastest-growing slice of the funnel. Katie writes content, Webb runs blue-link SEO, Reilly does outbound — none of them owns "get cited by answer engines," which is its own discipline with its own levers (direct-answer content, schema, and presence in the sources LLMs pull from: Reddit, directories, roundups, YouTube).

## How it's scoped (the yourco pattern, not a persona)
- **Owner/charter:** `agents/mario/`. **Loop:** `processes/loops/aeo-geo.md` (monthly once live). **Runtime prompt:** `runtime/prompts/aeo-geo.md`. **Slack:** `#yourco-mario`, wired into the two-way control surface.
- **Prescribes, never publishes.** Mario drafts the audit + interventions; Katie writes the content he briefs, Webb implements the schema he specs, the Founder approves anything external. Same gate as everyone.
- **Boundaries:** Mario vs Webb = answer-engine citation (incl. off-site sources) vs classic site SEO; Mario vs Katie = decides what content must exist to win citations vs writes it; Mario vs Reilly = pull (get found) vs push (outbound).

## Pre-launch posture
yourco isn't live (OtherVenture), so answer engines can't cite it yet. Mario's first job is launch-readiness: build the citable assets + entity footprint so yourco is cited from day one, plus a category baseline (who's cited today, which sources the engines pull from — researchable now). The live brand audit and the monthly cadence start at launch.

## Reversibility
Low stakes. If AEO/GEO doesn't earn the monthly slot once live, fold the capability back into Webb/Katie and retire the loop. Nothing else depends on Mario.
