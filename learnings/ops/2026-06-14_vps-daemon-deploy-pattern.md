# Learning — deploying a long-running daemon on the yourco VPS (the gotchas)

**Date:** 2026-06-14 · **Type:** pattern / win · **Surfaced by:** wiring the Slack agent listener live

## What happened
Took the Slack two-way command listener from staged code to live on the Hostinger VPS with the Founder driving the
terminal. Several environment-specific snags slowed it down — none hard, but each cost a round-trip. Capturing
them so the **next** runtime daemon (or connector) deploys in one pass.

## The reusable pattern (apply to any new VPS daemon/connector)
1. **Run the service as `claudeops`, not root.** `User=claudeops` + `Group=claudeops` in the unit. This is what
   makes the service see `--user` pip packages (`~/.local`), the nvm `claude` binary, the approval gate at
   `~/.claude/settings.json`, and keeps any files the agent writes claudeops-owned (root-owned files in the repo
   break the loops later).
2. **Python deps:** Ubuntu 24 (noble) is PEP-668 "externally-managed" → plain `pip install` fails.
   Use `python3 -m pip install --user --break-system-packages <pkg>`. (`pip` itself needs `sudo apt install
   -y python3-pip` first.)
3. **`PYTHONUNBUFFERED=1` in the unit**, or the script's `print()` never reaches the journal (stdout is
   block-buffered under systemd) — looks like a dead service when it's actually running fine.
4. **`journalctl` needs `sudo`** for `claudeops` — it's not in the `systemd-journal`/`adm` group. "No entries"
   without sudo is a permissions artifact, not an empty log.
5. **Write config/units without an editor.** nano tripped the Founder up; `echo 'K=v' >> file` for env lines and
   `sudo tee /etc/systemd/system/x.service > /dev/null <<'EOF' … EOF` for units = one paste, no editor.
6. **Validate offline first.** A `--self-check` mode (config + env present, no network) catches the dumb stuff
   before burning a connect cycle. Build one into every daemon.
7. **Foreground-run before systemd.** Get it working in the shell (`python3 x.py`) and do the real end-to-end
   test, *then* wrap it in a unit. Separates "does it work" from "does systemd run it."

## Also worth remembering
- **Slack: per-agent apps, one control bot.** We have a separate Slack app per agent; the inbound listener uses
  ONE app (atlas) as the control bot across all channels. Apps are added to a channel via `/invite @bot` or
  **Integrations → Add apps**, never the "Add people" dialog.
- **CLAUDE_BIN is the nvm path** (`/home/claudeops/.nvm/versions/node/<v>/bin/claude`) — `echo "CLAUDE_BIN=$(which
  claude)"` auto-fills it; don't wrap a literal path in `$( )` (that *executes* it).

## Read this at Step 0
Kemba (platform) and the assistant on any "deploy a runtime daemon / connector on the VPS" turn. The runbook
that now reflects all of this: `runtime/slack-control-setup.md`.

Triggers: skill:deploy-vps-daemon, agent:kemba, daemon, systemd service, vps deploy, listener
