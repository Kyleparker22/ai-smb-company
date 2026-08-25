# Decision — Slack as the per-agent control surface (two-way command)

**Date:** 2026-06-14 · **Owners:** the Founder + Kemba (platform) · **Status:** Phase 1 live; **Phase 2 LIVE on the VPS 2026-06-14** (systemd `yourco-slack-listener`, control bot = atlas) · Security review: Rafi

## Decision
Make Slack a **per-agent control surface**: each agent has its own channel, and the Founder can **command an agent in its channel and have it act** — the multi-agent-in-Slack pattern. Built in two phases so the safe part ships immediately and the inbound path lands behind an explicit security model.

- **Phase 1 — per-agent channels (LIVE).** Every loop posts to its own `#yourco-<agent>` channel; `#all-yourco` stays the executive digest (briefings + watchdog alerts). Outbound only; no new capability or security surface. Map: `runtime/slack-channels.md`.
- **Phase 2 — two-way command (BUILT, STAGED).** A native Socket-Mode listener on the runtime: the Founder messages an agent's channel → that agent runs and acts → it replies in-channel. Code: `runtime/slack-agent-listener.py`. Deploy runbook: `runtime/slack-control-setup.md`. Not live until the Founder wires the Slack app tokens + the systemd unit (credentials/infra are the Founder's, never the assistant's).

## Why (and why native, not n8n)
The "Jarvis with a channel per agent" pattern is genuinely useful: Slack becomes the control panel the Founder already carries on his phone, each channel is a clean two-way log of that agent's work + the Founder's directives (observability — the moat), and it mirrors how a real team operates. It's buildable **natively** (Slack Socket Mode + the existing runtime), so it does not pull in n8n/Make or a third-party agent runtime — consistent with `decisions/2026-06-14_framework-adoption-stance.md` and the no-code stance. The viral builds glue this together with no-code; YourCo builds the durable, gated version.

## The security model (the reason Phase 2 is a decision, not a toggle)
Inbound command turns a Slack message into an **instruction source** — a new trust boundary. Controls, all enforced in the listener:

1. **Caller allowlist — the Founder only.** Only the Founder's Slack user ID may command. Every other user, every bot, and the listener's own posts are ignored (no command loops, no teammate/guest command, no spoof). A workspace member is *not* implicitly trusted.
2. **Capability gate preserved.** The agent runs under the same host approval gate (`~/.claude/settings.json`): read/edit files + Slack post + Gmail **draft** allowed; **send / delete / Bash denied.** A Slack command cannot escalate past what a scheduled loop can already do. Send/irreversible actions stay human.
3. **Prompt-injection hardening.** Only the Founder's literal message is authoritative. Channel history, quoted text, links, and file contents are untrusted **data** — same posture as Melanie's command layer (`ACTION_SYSTEM`). State-changing actions keep the "target must be explicitly named" guard.
4. **Transport = Socket Mode.** No public webhook, no inbound port opened on the VPS — the listener dials out to Slack over an app-level token. Smaller attack surface than an Events-API HTTP endpoint.
5. **Audit + bounded.** Every command and result lives in the channel (self-auditing) plus a local log; per-minute rate cap; per-command timeout. If the listener is down, nothing queues or fires later — the Founder just falls back to the dashboard console / Cowork.

## Options considered
- **Give the Founder a Jira/Asana/Slack-workflow board** → rejected (off-brand, second source of truth — see the no-code stance).
- **n8n/Make "Slack → agent" automation** → rejected (no-code substrate, can't gate/eval rigorously, supply-chain surface).
- **Events API (HTTP webhook)** → rejected for v0 (needs a public URL / reverse proxy; larger surface). Socket Mode is firewall-friendly and tokened.
- **Open command to any workspace member** → rejected (every member becomes a command authority; injection/abuse risk). the Founder-only allowlist for v0; widen later per-agent if a teammate ever needs it, behind the same model.

## Reversibility
- **Phase 1:** trivial — revert a loop's one Slack line back to `#all-yourco`.
- **Phase 2:** stop the systemd unit and the inbound path is gone instantly; Phase 1 (outbound) is unaffected. Nothing about Phase 2 is load-bearing for the rest of the OS.

## Revisit / widen triggers
- A teammate (e.g. a future ops hire) needs to command an agent → add their user ID to the allowlist per-channel, not globally.
- Volume makes Socket Mode chatty → move to Events API behind the authenticated reverse proxy (same gate, same allowlist).
