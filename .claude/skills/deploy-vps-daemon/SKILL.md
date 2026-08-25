---
name: deploy-vps-daemon
description: Deploy a long-running daemon, listener, or connector on the yourco VPS (Hostinger, Ubuntu 24). Use for any always-on process that is NOT a timer-fired loop — the 7 gotchas here each cost a debugging round-trip the first time.
---

# deploy-vps-daemon

## Canonical source
`learnings/ops/2026-06-14_vps-daemon-deploy-pattern.md` (learned wiring the Slack listener live) + the worked example `runtime/slack-control-setup.md`.

## The pattern
1. **Run as `claudeops`, never root** — `User=claudeops`/`Group=claudeops` in the unit. Root-owned files in the repo break the loops later; claudeops sees the `--user` pip packages, the nvm `claude` binary, and the approval gate.
2. **Python deps:** Ubuntu 24 is PEP-668 externally-managed — `python3 -m pip install --user --break-system-packages <pkg>` (after `sudo apt install -y python3-pip`).
3. **`PYTHONUNBUFFERED=1` in the unit** — otherwise `print()` never reaches the journal and a healthy service looks dead.
4. **`journalctl` needs `sudo`** for claudeops — "No entries" without sudo is a permissions artifact, not an empty log.
5. **Write config/units editor-free** — `echo 'K=v' >> file` for env lines, `sudo tee /etc/systemd/system/x.service > /dev/null <<'EOF' … EOF` for units.
6. **Build a `--self-check` mode** (config + env present, no network) and run it before burning a connect cycle.
7. **Foreground-run before systemd** — prove it works in the shell first; separates "does it work" from "does systemd run it."

## Gotchas
- `CLAUDE_BIN` is the nvm path — auto-fill with `echo "CLAUDE_BIN=$(which claude)"`; never wrap a literal path in `$( )` (that executes it).
- Slack: one control bot (`@atlas`) added via `/invite @atlas` or Integrations → Add apps — never the "Add people" dialog.
- Secrets live in gitignored `.env` files on the host (`runtime/.slack.env` pattern) — never in the unit file or the repo.
- Register the new service in `runtime/agent-registry.json` and keep a reference copy of the unit in `runtime/systemd/`.
