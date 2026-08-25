# Spec — Telegram command transport (phone control, reusing the Slack guardrails)

> **Status: BUILT, not deployed.** Code (`runtime/telegram-agent-listener.py`), systemd unit
> (`runtime/systemd/yourco-telegram-listener.service`), and registry sanctioning are all in the repo
> (2026-07-05); what remains is the human/one-time setup below (BotFather token → `.telegram.env` → enable
> the unit). Mobile sibling of `runtime/slack-agent-listener.py`. Lets the Founder command any
> yourco agent **from his phone via a Telegram DM** — under the *same* host approval gate, the *same*
> the Founder-only allowlist, the *same* injection hardening, and the *same* listener-does-persistence model.
> Rationale for reusing (not adopting a stock "claudegram"): a raw Telegram→Claude-Code bridge ships full
> Bash/send/delete access to the box — the exact moat-killer the approval gate exists to prevent. This spec
> keeps the moat by making Telegram just a **new transport in front of the existing gated agent invoker**.
>
> Parent model + security rationale: `decisions/2026-06-14_slack-agent-control-surface.md`.
> Sibling deploy doc this mirrors: `runtime/slack-control-setup.md`.

## Design in one line
Swap the transport (Slack Socket Mode → Telegram Bot API long-poll), keep everything below the transport
byte-for-byte: `invoke_agent()`, `_ENV_BOOTSTRAP`, `AGENT_PROMPT`, `git_sync()`, the rate limiter, and the
`AGENT_ROLE` map all lift straight out of `slack-agent-listener.py`.

## What changes vs. the Slack listener (the only real work)

| Concern | Slack listener today | Telegram transport |
|---|---|---|
| **Transport** | Socket Mode (dial-out, no open port) | Bot API **long-poll** `getUpdates` (dial-out, no open port) — same "no inbound port" property |
| **Allowlist** | `FOUNDER_SLACK_USER_ID` vs `event.user` | `FOUNDER_TELEGRAM_USER_ID` (numeric) vs `message.from.id` |
| **Which agent** | channel → agent (`CHANNEL_AGENT`) | **prefix routing + sticky default** (see below) — Telegram has no per-agent channels |
| **Reply identity** | posts *as* each agent (`chat:write.customize`) | single bot; prefix the reply with the agent name/emoji in text (`🖋️ *Katie:* …`) — no per-agent apps |
| **Reply length** | 3500-char cap | same cap (Telegram hard limit is 4096; send **plain text, no `parse_mode`** so arbitrary code/paths can't 400 the send) |
| **Dependency** | `slack_sdk` | **zero** — raw Bot API over `urllib.request` (no pip install; nice hardening + one less supply-chain dep) |

Everything else — the gate, the env bootstrap that loads the MCP connectors, the "listener commits because the
gate-bound agent can't push" persistence — is **identical** and should be imported/copied verbatim so the two
stay in sync.

## The one design decision: agent routing

Telegram gives you a single 1:1 DM thread with the bot, not 27 channels. Chosen model — **prefix + sticky**:

- First token of the message selects the agent when it matches a known slug:
  `katie: draft a LinkedIn post on eval gates` → routes to Katie **and** remembers Katie as this chat's
  sticky agent.
- A bare message (no known-agent prefix) goes to the **sticky** agent (default `atlas`), so a back-and-forth
  doesn't need the prefix every line.
- Bot commands: `/agents` (list slugs+roles), `/agent katie` (set sticky), `/whoami` (show sticky).

Rationale: zero Telegram-side setup, thumb-friendly on a phone, and it degrades safely (unknown prefix → falls
through to sticky, never to "wrong agent"). **Rejected alternative:** Telegram **forum topics** in a supergroup
(one topic per agent, a true channel-analog) — closest to the Slack UX but requires creating/maintaining 27
topics and mapping topic-ids; revisit only if the flat DM feels cramped.

## Security parity (must hold — these are the moat, not conveniences)
1. **the Founder-only, and it's the *whole* gate here.** A Telegram bot token isn't secret the way a Slack workspace
   is — anyone who discovers the bot handle can DM it. So `message.from.id != FOUNDER_TELEGRAM_USER_ID` →
   **silently ignored**, no reply (don't even confirm the bot exists). This check is non-negotiable and runs
   before anything else.
2. **Gate unchanged.** The agent still runs under `~/.claude/settings.json` (read/edit/draft/post allowed;
   **send/delete/Bash denied**). Telegram cannot escalate past a scheduled loop — same `AGENT_PROMPT`, same
   `_ENV_BOOTSTRAP`.
3. **Injection.** the Founder's literal message is the only instruction; quoted text / forwarded messages / links are
   untrusted DATA (already how `AGENT_PROMPT` is written).
4. **No open port.** Long-poll dials out; nothing listens. (If you ever switch to webhooks you'd expose a
   public URL — **don't**; keep long-poll.)
5. **Rate limit.** Reuse the 8/min rolling limiter.
6. **Persistence by the trusted daemon.** Gate-bound agent can't `git push`; the listener (`claudeops`, not
   under the gate) `pull --rebase`s before and `add/commit/push`es after — copied from `git_sync()`.

## Files this adds
- `runtime/telegram-agent-listener.py` — the transport ✅ (imports `invoke_agent`/`git_sync`/rate limiter/
  `AGENT_ROLE` from the Slack listener by path — shared, not copied, so the two can't drift).
- `runtime/systemd/yourco-telegram-listener.service` ✅ (mirror of the Slack unit; `EnvironmentFile` →
  `.telegram.env`).
- `runtime/agent-registry.json` ✅ — sanctioned in `sanctioned_services` + `sanctioned_daemons_no_timer`
  (the watchdog's repo check is two-way, so the unit file and the registry entry land in the same change).
- `runtime/.telegram.env` (gitignored, **created on the VPS in Step 3, never committed**) —
  `TELEGRAM_BOT_TOKEN`, `FOUNDER_TELEGRAM_USER_ID`, `CLAUDE_BIN`.

## Setup (mirrors slack-control-setup.md)
1. **[Phone/BotFather]** DM `@BotFather` → `/newbot` → name it (e.g. `yourco ops`) → copy the `123456:ABC…`
   **bot token**. Then `/setprivacy` → **Enable** (bot only sees DMs + explicit commands — we only use DMs).
2. **[Phone]** Get your numeric Telegram user id: DM `@userinfobot` → it replies with your `Id:` (a number).
   That is `FOUNDER_TELEGRAM_USER_ID`.
3. **[VPS]** Write the gitignored env (no editor needed):
   ```bash
   cd ~/yourco-os && git pull
   echo 'TELEGRAM_BOT_TOKEN=123456:ABC…' >  runtime/.telegram.env
   echo 'FOUNDER_TELEGRAM_USER_ID=00000000'  >> runtime/.telegram.env
   echo "CLAUDE_BIN=$(which claude)"       >> runtime/.telegram.env
   grep -c = runtime/.telegram.env   # expect 3
   ```
   No `pip install` — the transport is stdlib-only.
4. **[VPS]** Offline self-check: `python3 runtime/telegram-agent-listener.py --self-check`
   (want: token + allow-user both True, agent map printed).
5. **[VPS]** Run as a 24/7 service **as `claudeops`** (so it finds nvm `claude`, the gate in `~/.claude`, and
   keeps repo files claudeops-owned). The unit ships in the repo at
   `runtime/systemd/yourco-telegram-listener.service` — install it in one shot:
   ```bash
   sudo cp ~/yourco-os/runtime/systemd/yourco-telegram-listener.service /etc/systemd/system/
   sudo systemctl daemon-reload && sudo systemctl enable --now yourco-telegram-listener
   sudo journalctl -u yourco-telegram-listener -n 10 --no-pager   # expect "[telegram-listener] connected as @…"
   ```
   > `journalctl` needs **`sudo`** (claudeops isn't in the journal groups). After any `.telegram.env` edit:
   > `sudo systemctl restart yourco-telegram-listener`.
6. **[Phone]** Live test that proves command **and** gate: DM the bot
   `katie: draft a short post on what an eval gate is` → get her draft → then `email that to me` → she must
   **decline to send**. Same acceptance test as Slack Step 6.

## Telegram-specific gotchas (each is one debugging round-trip saved)
- **Privacy mode + DMs:** in a 1:1 DM the bot sees everything regardless — good. Only groups need privacy off.
  Keep it a DM; don't add the bot to a group.
- **`getUpdates` offset:** persist/advance the `update_id` offset or you reprocess the backlog on every poll
  (and re-run commands). Long-poll with `timeout=50`; ack by passing `offset=last+1`.
- **Send as plain text:** do **not** set `parse_mode` — agent replies contain code, underscores, brackets that
  break Markdown/HTML parsing and 400 the send. Truncate to 3500 chars (limit is 4096).
- **Bot token in chat = rotate it.** Same rule as every secret: it goes into `.telegram.env` on the box, never
  pasted into Cowork. A leaked bot token + a slipped allowlist = a shell-adjacent agent for a stranger.
- **Down = inert.** Stop the service → inbound path gone instantly, nothing queues. Fall back to Slack control
  or Cowork.

## Wiring / bookkeeping (so it doesn't become half-wired)
- ✅ `runtime/agent-registry.json` — sanctioned (services + daemons-no-timer), 2026-07-05, same change as the
  unit file, so the Mon 07:45 governance watchdog is clean in both directions.
- **At go-live (not before — these docs describe what's running):** one-line it in `runtime/README.md`'s
  daemon list and `runtime/connectors.md` (headless vs Cowork), and log the build in `decisions/` as a
  *transport addition* referencing the 2026-06-14 control-surface decision (no new security model — same
  gate, new door), per the `log-decision` skill.
- Follow `deploy-vps-daemon` for the systemd/ownership steps (it's a long-running daemon, not a timer loop).

## Estimate
~2 hours: the transport is ~120 lines and the invoker/gate/persistence code is lifted verbatim from the Slack
listener. The only genuinely new code is the long-poll loop + prefix router; the moat-critical parts are copied,
not rewritten.
