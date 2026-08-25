---
name: wire-new-agent
description: Create, activate, or give a Slack channel to an yourco agent. Use EVERY time an agent is born, promoted from dormant, or gets a new surface — the wiring has 13 steps across repo and host and half-done wiring is the known failure mode.
---

# wire-new-agent

## Canonical doc
`runtime/agent-wiring-checklist.md` — follow it exactly; this skill is the trigger + the summary. The Agent Factory (`agents/kemba/02_build.md`) drives it.

## Steps (summary — the checklist is the truth)
**Repo (Kemba drafts, commit + push; VPS syncs):**
1. Docs — `clients/<name>/` charter + discovery/build/eval docs
2. Roster row — `04_agent_roster.md`
3. Dashboard status — `dashboard/data.json` `agents[]`
4. Slack channel `#yourco-<name>` — **must be PUBLIC** (private = total silence, the listener can't see it)
5. Listener map — all three dicts in `runtime/slack-agent-listener.py`; verify with `--self-check`
6. Registry sanction (Rafi) — `runtime/agent-registry.json` (unsanctioned = drift watchdog flags it)
7. Channel map — `runtime/slack-channels.md`
8. Connector if needed headless — `runtime/connectors.md`
9. Scheduled loop only if it runs on a cadence — see the `add-runtime-loop` skill

**Host (the Founder on the VPS — never an agent's job):**
10. `/invite @atlas` in each new channel (atlas is the ONE control bot; there is no per-agent bot)
11. `git pull` + restart `yourco-slack-listener`
12. Connector auth/tokens
13. Enable the timer (scheduled agents only)

## Gotchas
- **Wiring ≠ activation.** Wiring makes an agent commandable; a trigger-gated agent still waits for its real trigger (`runtime/activation-triggers.md`). Never put a triggerless agent on a timer.
- The approval gate stays load-bearing: send/delete/Bash denied. Widening what an agent may *do* is a host edit, never a repo edit.
