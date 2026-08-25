# Agent activation wiring + the Kemba Agent Factory

**Date:** 2026-06-25
**Context:** Follow-on to the 11-agent deep-build (`decisions/2026-06-25_agent-roster-deep-build.md`). the Founder asked to (a) build an agent that builds agents, (b) create + wire the missing Slack channels, and (c) wire the dormant agents' activation triggers. All three done this pass.

## 1. The Agent Factory → built into Kemba (not a new agent)
Per the locked "lean roster — fold into the nearest agent" rule, the build-other-agents capability belongs to **Kemba** (Platform/Template Engineer), who already owns the golden template + runtime. Deep-built `agents/kemba/` (discovery/build/eval) centered on the **Agent Factory**: a governed pipeline that (1) runs a **should-this-exist GATE** (BUILD / FOLD-IN / DEFER against the shiny-tools test), (2) **recommends when** to build, (3) **researches → scaffolds** the `clients/<name>/` set from the template, (4) defines eval gates with Kolby, and (5) runs a **wiring checklist** (connectors · channel · registry · timer · handoffs) tagging each step `[DRAFT]` (Kemba) vs `[HOST]` (human). **Governance:** Kemba proposes/scaffolds only — the Founder approves every new agent, Rafi sanctions it in the registry, Kolby evals before it runs; Kemba never self-deploys, widens a connector scope, or enables a timer. It codifies what was done manually on 2026-06-25.

## 2. Slack channels — 7 created + sanctioned
Created `#yourco-{bella,webb,janice,kimi,bird,harry,kori}` (the built agents that lacked a channel). Bella/Webb are on-demand; the other five are pre-provisioned so they're summon-ready the instant their trigger fires. **Sanctioned** in `runtime/agent-registry.json` (so Rafi's drift watchdog stays clean) and mapped in `runtime/slack-channels.md` (with channel IDs).
- **Host step remaining:** channels were created via Cowork's Slack app, which may not be the runtime listener bot — so on the VPS, **invite the runtime bot** to each channel before its loop/command can post there.

## 3. Activation triggers — detect-and-notify wired
The 6 dormant agents are **event-triggered, not scheduled** (a timer today = empty no-op runs + hallucination risk). New runbook `runtime/activation-triggers.md` defines each agent's machine-checkable condition + the host activation steps. The **daily watchdog** (`runtime/prompts/watchdog.md`) now checks those conditions each run and leads its Slack post with `🟢 ACTIVATION TRIGGER MET: <agent> — <condition>` when one fires. **Detect-and-notify only — never auto-activate** (enabling stays the Founder's host action; cadenced agents go through Kemba-drafts → Rafi-sanctions → Kolby-evals → the Founder-enables).

## Net activation state
- **Live/armed now:** Charles, Mario (timers), + the existing live agents.
- **On-demand, now summonable:** Bella, Webb, Michelle (channels exist).
- **Event-gated, watched + ready:** Janice, Kimi, Kortney, Bird, Harry, Kori — the OS now watches for each trigger and flags it; one host step activates.
- **Kemba:** Agent Factory documented + governed; runs on request under approval.
