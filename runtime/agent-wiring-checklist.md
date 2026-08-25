# Agent wiring checklist — the canonical SOP

> **Status: LIVE SOP** — run it every time an agent is created, activated or given a channel. Half-done wiring is the known failure mode.

> **Run this EVERY time an agent is created, activated, or given a channel.** It's the single source of truth so wiring never gets half-done (and the Founder never has to catch a missed step). Owner: **Kemba** (does the repo steps) + **Rafi** (sanctions the registry). The Agent Factory (`agents/kemba/02_build.md`) drives this; this file is the checklist it follows.

## Key facts (so they're never re-litigated)
- **Control bot = `atlas`.** ONE Slack app routes every agent's commands and posts *as* each agent (name + avatar via `chat:write.customize`). There is no per-agent bot to add — just invite **`@atlas`**.
- **Channels must be PUBLIC** — the listener's `message.channels` event doesn't cover private channels (a private channel = total silence).
- **The listener map is code** — a channel does nothing until the agent is added to `CHANNEL_AGENT`/`AGENT_ROLE`/`AGENT_IDENTITY` in `runtime/slack-agent-listener.py` AND the listener is restarted.
- **The gate is load-bearing** — agents read/edit/draft/post; **send/delete/Bash stay denied** (`runtime/headless-settings.reference.json`). Host actions (enable timer, invite bot, connect a connector, widen a scope) are **never** an agent's job.

## The checklist
**Repo steps (Kemba drafts; committed to git — the VPS syncs them):**
1. **Docs** — `clients/<name>/` charter + `01_discovery.md` / `02_build.md` / `03_eval.md` (the Charles structure).
2. **Roster** — add/update the row + status in `04_agent_roster.md`.
3. **Dashboard** — set the agent's `status` in `dashboard/data.json` (`agents[]`).
3b. **The number it owns** — add an entry to `runtime/agent-registry.json` → `agent_metrics.agents`:
   the one number this agent moves, whether it ladders `direct` or `enabling` to the north star, and
   either a `source` that `dashboard/northstar.py` actually implements or `"unmeasured"` **plus**
   `needs` + `blockedBy`. *Invariant-checked* — an agent with no number fails
   `runtime/consistency-check.py`, which is the point: you cannot add an agent without answering what
   it moves. **Do not reach for an activity count.** "The loop ran" is not an outcome; an honest
   `unmeasured` with a named gap is worth more than a green number nobody would act on.
4. **Slack channel** — create `#yourco-<name>` (**public**).
5. **Listener map** — add the agent to all three dicts in `runtime/slack-agent-listener.py` (`CHANNEL_AGENT`, `AGENT_ROLE`, `AGENT_IDENTITY`). Verify with `python3 runtime/slack-agent-listener.py --self-check`.
6. **Registry (Rafi sanctions)** — add the channel to `sanctioned_slack_agent_channels` in `runtime/agent-registry.json` (+ any new prompt/timer/service/connector the agent introduces). Unsanctioned = the drift watchdog flags it.
7. **Channel map** — add the row + channel ID to `runtime/slack-channels.md`.
8. **Connector (if it needs one headless)** — follow `runtime/connectors.md` (add to `.mcp.json` read-only-scoped + gate allow + registry sanction).
9. **Scheduled loop (only if it runs on a cadence)** — `runtime/prompts/<x>.md` + a systemd `.service`/`.timer` + sanction in the registry.

**Host steps (the Founder, on the VPS — can't be done from Cowork):**
10. **Invite the bot** — in each new channel: `/invite @atlas`.
11. **Restart the listener** — `cd ~/yourco-os && git pull && sudo systemctl restart yourco-slack-listener`.
12. **Connector auth** — provide any token/OAuth on the host (e.g. calendar write scope under `~/.calendar-mcp/`).
13. **Enable a timer** — `sudo systemctl enable --now yourco-<x>.timer` (only for scheduled agents).

## Activation vs. wiring
Wiring makes an agent **commandable / ready**. *Running* a trigger-gated agent waits for its real trigger — see `runtime/activation-triggers.md`. Don't put a triggerless agent on a timer (empty runs + hallucination risk).
