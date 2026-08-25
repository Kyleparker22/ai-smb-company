# Always-On Claude Code — DIY Step-by-Step (the Founder)

Hands-on guide to stand up the YourCo OS as a 24/7 headless Claude Code runtime, yourself. Follow top to bottom. Assumes: your Mac for local steps, an Ubuntu VPS for the server, GitHub as the git host (swap for self-hosted Gitea if you went that way — only the remote URL changes).

> **Verify-as-you-go:** Claude Code evolves; if a command differs, check the linked docs. Key refs: setup `https://code.claude.com/docs/en/setup`, headless `https://code.claude.com/docs/en/headless`, MCP `https://code.claude.com/docs/en/mcp`, permissions `https://code.claude.com/docs/en/permission-modes`, hooks `https://code.claude.com/docs/en/hooks`.

---

## PART A — Local (Mac): put the OS into git + GitHub

**A1. Confirm git is installed**
```bash
git --version    # if missing: xcode-select --install
```

**A2. Create a private GitHub repo**
- github.com → New repository → name `yourco-os` → **Private** → don't add a README → Create.
- Copy the repo URL (e.g., `https://github.com/<you>/yourco-os.git`).

**A3. Add a `.gitignore` so secrets never get committed**
In the workspace folder (`YourCo LLC - AI`), create a file named `.gitignore`:
```
.env
*.key
.DS_Store
**/secrets*
node_modules/
```

**A4. Initialize, commit, push**
```bash
cd "/Users/you/Documents/Claude/Projects/YourCo LLC - AI"
git init
git add .
git commit -m "YourCo OS — initial commit"
git branch -M main
git remote add origin https://github.com/<you>/yourco-os.git
git push -u origin main
```
You'll authenticate with a GitHub Personal Access Token (github.com → Settings → Developer settings → Tokens) or GitHub Desktop. Done — the OS is now versioned.

---

## PART B — Local (Mac): Obsidian (optional, 10 min, do it now)
- Install Obsidian → "Open folder as vault" → select the `YourCo LLC - AI` folder.
- Community plugins → search **Obsidian Git** → install + enable → set "Auto pull/commit/push" interval (e.g., 10 min). Now your edits sync to the same repo, and you get the graph view.

---

## PART C — Anthropic API key
- console.anthropic.com → API Keys → Create key → copy it (starts `sk-ant-...`).
- Add billing / a small credit balance (headless runs are pay-as-you-go).
- Keep the key secret — it goes in the server's env, never the repo.

---

## PART D — Server: provision an Ubuntu VPS
- Pick a provider (Hetzner, DigitalOcean, Vultr, Fly, Railway). Smallest tier is fine ($5–10/mo). Choose **Ubuntu 24.04 LTS**.
- SSH in:
```bash
ssh root@<server-ip>
```
- Create a non-root user + update:
```bash
adduser claudeops
usermod -aG sudo claudeops
apt update && apt upgrade -y
su - claudeops
```

---

## PART E — Server: install + authenticate Claude Code
**E1. Install Node 18+ then Claude Code** (npm path is the most reliable cross-platform; native installer also exists — see setup docs)
```bash
# Node via nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc
nvm install --lts
# Claude Code
npm install -g @anthropic-ai/claude-code
claude --version
```

**E2. Store the API key as an env secret**
```bash
mkdir -p ~/.yourco && nano ~/.yourco/env
# put this line in:
export ANTHROPIC_API_KEY="sk-ant-..."
chmod 600 ~/.yourco/env
echo 'source ~/.yourco/env' >> ~/.bashrc
source ~/.bashrc
```

**E3. Clone the OS repo**
```bash
git clone https://github.com/<you>/yourco-os.git ~/yourco-os
cd ~/yourco-os
```
(Use a GitHub token or set up an SSH deploy key so the server can pull/push non-interactively.)

**E4. Smoke test — CLAUDE.md auto-loads**
```bash
cd ~/yourco-os && claude -p "In one line, what is this workspace?" --output-format json
```
If it answers from CLAUDE.md, the project is wired.

---

## PART F — Server: reconnect the MCP connectors
This is the fiddliest part — budget time. Two categories:

**F1. Remote-MCP tools you already added (Higgsfield, Descript, Vibe)** — port directly. Add each with its URL + key:
```bash
claude mcp add --transport http higgsfield <higgsfield-mcp-url>
claude mcp add --transport http descript https://api.descript.com/v2/mcp/claude
claude mcp add --transport http vibe <vibe-mcp-url>
```
Or put them in a project `.mcp.json` (committed) using `${ENV_VAR}` for any keys, with the real values in `~/.yourco/env`.

**F2. The Google + Slack connectors (Gmail, Calendar, Drive, Slack)** — in Cowork these are built-in; on Claude Code you supply an MCP server for each. Options: official/community Google + Slack MCP servers, or an aggregator. Each OAuth server needs a **one-time interactive auth**:
```bash
claude        # start interactive once
/mcp          # authenticate each server in the browser flow
# then exit; headless runs reuse the stored auth
```
> Honest note: getting Gmail/Calendar/Slack MCPs working headless is the step most likely to need a docs dive per connector. Do this one connector at a time and test each with a small `claude -p` call before moving on.

---

## PART G — Server: schedule the loops (systemd timers)

**G1. A wrapper script that syncs + runs** — `~/yourco-os/run-loop.sh`:
```bash
#!/usr/bin/env bash
set -euo pipefail
source ~/.yourco/env
cd ~/yourco-os
git pull --rebase --autostash || true
claude -p "$1" --output-format json >> ~/yourco-os/loops/_runtime.log 2>&1
git add -A && git commit -m "loop run $(date -u +%FT%TZ)" || true
git push || true
```
```bash
chmod +x ~/yourco-os/run-loop.sh
```
Tip: store each agent's prompt (the existing scheduled-task SKILL.md body) in a file in the repo and have the script read it, instead of inlining long prompts.

**G2. One `.service` + `.timer` per loop.** Example — Monday sales loop:

`/etc/systemd/system/yourco-sales.service`
```ini
[Unit]
Description=YourCo sales loop
[Service]
Type=oneshot
User=claudeops
WorkingDirectory=/home/claudeops/yourco-os
ExecStart=/home/claudeops/yourco-os/run-loop.sh "You are Atlas running the Monday sales/pipeline loop. Read processes/loops/sales.md and follow it exactly."
```

`/etc/systemd/system/yourco-sales.timer`
```ini
[Unit]
Description=Run YourCo sales loop Mondays
[Timer]
OnCalendar=Mon *-*-* 07:00:00
Persistent=true
[Install]
WantedBy=timers.target
```
Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now yourco-sales.timer
sudo systemctl list-timers | grep yourco
```
Repeat for: finance (Mon 07:15), Atlas briefing (Mon 07:55), customer-health (Wed 07:00), content (Fri 07:00), Luka monthly, Polo quarterly, Brett monthly — mirroring the current Cowork schedule. Set `Persistent=true` so a missed run (server reboot) fires on next boot.

---

## PART H — Approval gates (always-on ≠ auto-send)
Keep the human touchpoints. Simplest robust gate: **only give unattended runs the safe tools.** The agents are already designed to *draft/stage*, not send.

In `~/.claude/settings.json` (or project `.claude/settings.json`), scope tools per the allowed set, e.g.:
```json
{
  "permissions": {
    "allow": ["Read", "Edit", "Write", "Bash", "mcp__gmail__create_draft", "mcp__slack__send_message"],
    "deny": ["mcp__gmail__send", "mcp__*__delete*", "mcp__*__pay*"]
  }
}
```
- Let the loops **draft emails, post to `#all-yourco`, write artifacts** — but **not** send external mail, publish, delete, or pay.
- Anything gated stays a draft; you approve + send via Cowork.
- Advanced (optional): a **PreToolUse hook** that inspects a tool call and blocks must-approve actions with a Slack alert — see the hooks docs for exact config (`https://code.claude.com/docs/en/hooks`). Start with the allow/deny list; add hooks later if you want finer control.

> Do NOT use a blanket "skip all permissions" flag for these runs — that removes the gates entirely. Scope the tools instead.

---

## PART I — Test, then cut over
1. **Dry-run the Monday briefing headless:**
```bash
~/yourco-os/run-loop.sh "You are Atlas. Run the Monday Morning Briefing per processes/loops/monday-briefing.md."
```
Confirm: artifact written to `loops/monday-briefing/`, a Gmail **draft** created (not sent), Slack post to `#all-yourco`, and the commit pushed.
2. **Verify the gate held** — check that no external send/publish happened automatically.
3. **Enable the rest of the timers.**
4. **Keep Cowork as your interface** — direct + approve from there (or your phone). The server just runs the loops + drafts.
5. Log completion in `/decisions/2026-06-09_always-on-runtime.md`.

---

## Order of operations (the short version)
A→B→C today (repo + Obsidian + API key). D→E this week (server + Claude Code). F is the time-sink (connectors) — do one at a time. G→H→I to schedule, gate, and cut over. Test the Monday briefing before trusting the rest.

## If you get stuck
The connectors (Part F) and the OAuth auth are where most people stall. Do them incrementally, test each with a tiny `claude -p` call, and lean on the Claude Code MCP docs. Everything else is standard Linux/systemd.
