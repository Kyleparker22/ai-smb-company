# Setup — two-way Slack command (Phase 2 of the per-agent control surface)

> Wires `runtime/slack-agent-listener.py` so the Founder can command an agent **in its own Slack channel** and it
> acts (under the gate) and replies. Model + rationale: `decisions/2026-06-14_slack-agent-control-surface.md`.
> Prereq: Phase 1 channels exist (`runtime/slack-channels.md`).
> **Status: LIVE on the VPS as of 2026-06-14** (systemd unit `yourco-slack-listener`). This doc reflects the
> actual working deployment — paths, quirks, and all.

## What this adds vs. posting
Posting is outbound. This adds an **inbound** path: a Socket-Mode daemon that listens for *the Founder's* messages in
the agent channels and runs that agent. No public URL or open port — it dials out. The gate and the agents are
unchanged.

## The control bot (important — we run per-agent *apps*)
YourCo has a **separate Slack app per agent** (reilly, luka, webb, atlas, Reed, …). The listener routes
*all* channels through **one** Socket-Mode connection, so pick **one app as the control bot** and use its
tokens. **We use `atlas`** (the ops/monitoring identity). That one bot must be a member of all 11
`#yourco-<agent>` channels.

**Per-agent reply identity (no extra apps needed):** the control bot posts each reply *as* the answering agent
— name + avatar per channel (Katie 🖋️ in `#yourco-katie`, Charles 💰 in `#yourco-charles`, …) — via the
`chat:write.customize` scope and `AGENT_IDENTITY` in the listener. One app, distinct identities. (If the scope
isn't granted yet the listener falls back to posting as the plain atlas bot — replies still work.)

## Step 1 — turn the control app (atlas) into a listener
At `api.slack.com/apps` → **atlas**:
1. **Settings → Socket Mode → Enable** → generate an **App-Level Token** (name `socket`, scope
   `connections:write`) → copy the **`xapp-…`**.
2. **Features → OAuth & Permissions → Bot Token Scopes** → add `channels:history` + `channels:read`
   + **`chat:write.customize`** (lets the one control bot reply *as* each agent — name + avatar per channel;
   you already have `chat:write`). Private channels also need `groups:history` + `groups:read`.
3. **Features → Event Subscriptions → Enable** (no Request URL needed — Socket Mode is on) →
   **Subscribe to bot events** → add `message.channels` → **Save Changes**.
   > ⚠️ **`message.channels` is PUBLIC channels only.** If any `#yourco-<agent>` channel is **private**, Slack
   > delivers its messages via `message.groups` instead — so a private channel produces **total silence** (service
   > up, bot in channel, correct user id, and *still* nothing) until you also add the `message.groups` event +
   > `groups:history`/`groups:read` scopes and reinstall. **Simplest: keep the agent channels public.**
   > (This was the 2026-06-22 outage — channels had been made private; fix was making them public again.)
4. **Reinstall to Workspace** (scope changes require it) → copy the **`xoxb-…`** bot token.
5. Invite the atlas bot to **all 11** `#yourco-<agent>` channels. *Note: a bot is added via `/invite @atlas`
   in the channel or the channel's **Integrations → Add apps** tab — NOT the "Add people" dialog (humans only).
   The app must be installed with a bot user first, i.e. it has an `xoxb-…` token.*

## Step 2 — the Founder's Slack member id (the allowlist)
Slack → your profile → **⋮ More → Copy member ID** (`U0XXXXXXX`). Only this id can command.

## Step 3 — env on the VPS
On the server (`ssh claudeops@<host>`; repo at `~/yourco-os`), write the gitignored env file. No editor needed:
```bash
cd ~/yourco-os && git pull
echo 'SLACK_BOT_TOKEN=xoxb-…'   > runtime/.slack.env     # atlas bot token   (single >)
echo 'SLACK_APP_TOKEN=xapp-…'  >> runtime/.slack.env     # atlas socket token
echo 'FOUNDER_SLACK_USER_ID=U0…'  >> runtime/.slack.env     # your member id
echo "CLAUDE_BIN=$(which claude)" >> runtime/.slack.env  # auto-fills the nvm path
grep -c = runtime/.slack.env                              # expect 4
```
Both tokens must be from the **same** app (atlas). Install the one dependency (Ubuntu 24+ needs the PEP-668 flags):
```bash
sudo apt install -y python3-pip
python3 -m pip install --user --break-system-packages slack_sdk
```

## Step 4 — offline self-check (no connection)
```bash
set -a && . runtime/.slack.env && set +a
python3 runtime/slack-agent-listener.py --self-check     # want: allow-user/bot/app all True
```

## Step 5 — run it as a 24/7 service
Run **as `claudeops`** (so it finds the `--user` slack_sdk, the nvm `claude`, the gate in `~/.claude`, and keeps
repo files claudeops-owned). Write the unit in one shot:
```bash
sudo tee /etc/systemd/system/yourco-slack-listener.service > /dev/null <<'EOF'
[Unit]
Description=yourco Slack per-agent command listener
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=claudeops
Group=claudeops
WorkingDirectory=/home/claudeops/yourco-os
EnvironmentFile=/home/claudeops/yourco-os/runtime/.slack.env
Environment=PYTHONUNBUFFERED=1
ExecStart=/usr/bin/python3 /home/claudeops/yourco-os/runtime/slack-agent-listener.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload && sudo systemctl enable --now yourco-slack-listener
sudo journalctl -u yourco-slack-listener -n 10 --no-pager   # expect "[slack-listener] connected · …"
```
> `journalctl` needs **`sudo`** — `claudeops` isn't in the `systemd-journal`/`adm` group. `PYTHONUNBUFFERED=1`
> is what makes the script's `print()` lines actually appear in the journal.

## Step 6 — live test (proves command + gate)
In `#yourco-katie`: *"draft a short LinkedIn post on what an eval gate is."* → "On it — Katie is working…",
then her draft (~30–60s). Then *"email that to me."* → she should **decline to send** (gate holds). That's the
whole model: you can command her, she can't be talked past the gate.

## Operating notes
- **Manage:** `systemctl status yourco-slack-listener` · `sudo journalctl -u yourco-slack-listener -f` ·
  `sudo systemctl restart yourco-slack-listener` (after any `.slack.env` edit).
- **the Founder only.** Other members, bots, and the bot's own posts are ignored — no loops, no guest/spoof command.
  Add a teammate by adding their id to the listener's allowlist (per-channel), not globally.
- **Gate unchanged.** Agent can read/edit/draft/post; send/delete/Bash stay denied by `~/.claude/settings.json`.
- **Connector parity (fixed + verified 2026-06-25).** `invoke_agent` runs `claude` via a shell that sources `~/.yourco/env` + nvm (mirrors `runtime/run-loop.sh`), so a *commanded* agent loads the same MCP connectors as the scheduled loops (calendar, Gmail-draft, Slack). **Symptom if this regresses:** a commanded agent reports a connector tool is missing while the loops have it → check the `_ENV_BOOTSTRAP` step in `invoke_agent`. (Before the fix, commanded agents ran with the bare systemd env → no `npx` on PATH → zero MCP connectors, file-ops only.)
- **Down = inert.** Stop the service and the inbound path is gone instantly; nothing queues. Fall back to the
  dashboard console (Melanie) or Cowork. Posting (Phase 1) is unaffected.
- **Audit.** Every command + reply is in the channel; `sudo journalctl` has the process log.

## Troubleshooting — "I commanded an agent and got total silence"
Work down this list (it's ordered by 2026-06-22 likelihood):
1. **Channel is private.** #1 cause. `message.channels` only covers public channels → a private channel is silent even when everything else is right. Make it public (or add the `message.groups` event + `groups:*` scopes). **← the actual 2026-06-22 root cause.**
2. **Service down.** `sudo systemctl status yourco-slack-listener` → must be `active (running)`. If dead: `cd ~/yourco-os && git pull && sudo systemctl restart yourco-slack-listener`.
3. **atlas bot not in the channel.** Slack only delivers events for channels the bot is in → `/invite @atlas`.
4. **Wrong commanding user.** `grep FOUNDER_SLACK_USER_ID runtime/.slack.env` must equal your Slack member ID (profile → Copy member ID); the listener obeys only that id.
5. **Logs look empty?** Expected — stdout is buffered, so the `[slack-listener] connected` line may not flush. Steady CPU over days = it's connected. To see live output, stop the service and run it foreground: `set -a && . runtime/.slack.env && set +a && python3 runtime/slack-agent-listener.py`.
- **Persistence (auto, since 2026-06-22):** a Slack-commanded agent is gate-bound (Bash denied) so it can't `git push` its own work — so the **listener** now does it, exactly like `runtime/run-loop.sh` does for the scheduled loops: it `git pull --rebase`s before the agent runs, then `git add -A && commit && push`es whatever the agent wrote, and posts "_Committed + pushed: …_" in the channel. The agent gains **no** new permissions; the trusted daemon (claudeops, not under the gate) handles persistence. Requires the listener be redeployed (`git pull && sudo systemctl restart yourco-slack-listener`) to take effect.
