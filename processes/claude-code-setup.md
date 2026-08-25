# Claude Code Setup Runbook — Always-On YourCo Runtime

> **The runtime is now LIVE** (since 2026-06-09). This is the historical build runbook + a rebuild/reference guide. For day-to-day operation, the live docs are **`runtime/README.md`** (loops, units, approval gate) and **`runtime/phone-access.md`** (Tailscale + hosted apps + SSH). The redundant DIY duplicate was archived 2026-06-11 (`_archive/claude-code-setup-diy.md`).

The concrete how-to for the migration decided in `/decisions/2026-06-09_always-on-runtime.md`. Goal: run the YourCo OS (this workspace) headless + 24/7 on a server via Claude Code, with scheduled loops, MCP connectors, and human-approval gates intact.

**Owner:** Kemba/platform (the Founder holds). **Status:** ready to execute (infra task — developer-friendly).
**Note:** the OS is already in Claude Code's native format — `CLAUDE.md` auto-loads as boot context. This is a migration, not a rebuild.

---

## Step 1 — Workspace → private GitHub repo
Put the `YourCo LLC - AI` folder into a **private GitHub repo**. This is the source of truth the server runs against and how Cowork ⇄ server stay in sync. `memory/` and all SOPs travel with it.

## Step 2 — Stand up the host
A small always-on Linux box: a $5–10/mo VPS, Fly.io, or Railway (or an always-on Mac mini). Needs outbound HTTPS to `api.anthropic.com` and the MCP endpoints.

## Step 3 — Install Claude Code + authenticate
- **Install (Linux):** `sudo apt install claude-code` (Debian/Ubuntu; see https://code.claude.com/docs/en/setup for the repo + other distros). macOS: native installer or `npm install -g @anthropic-ai/claude-code` (Node 18+, no sudo).
- **Auth (headless → API key):** set `ANTHROPIC_API_KEY` (from the Anthropic Console, pay-as-you-go) in the host env / a sourced `.env`. API key takes priority over subscription login and is the right choice for unattended runs.
- **Clone the repo**, `cd` into it, verify: `claude -p "summarize CLAUDE.md" --output-format json`.

## Step 4 — MCP connectors
- Define servers in a project **`.mcp.json`** (committed to the repo) using `${ENV_VAR}` expansion for secrets — **never commit actual tokens.**
- Set the real values as env vars on the host (e.g., `export SLACK_BOT_TOKEN=...`). Add via `claude mcp add <name> <config>` or by editing `.mcp.json`.
- **OAuth servers (Gmail, Calendar, Slack):** need a one-time interactive auth on the server — run `claude` interactively once and use `/mcp` to authenticate each. After that, headless runs reuse the stored auth.
- Connectors to bring over: Gmail, Google Calendar, Slack, Vibe Prospecting, Higgsfield, Descript, Google Drive (+ any others in use).

## Step 5 — Scheduled loops → headless jobs
Claude Code has **no native scheduler** — use **systemd timers** (preferred) or cron. Each agent loop = `claude -p "<that agent's prompt>"` run from the repo dir.

Per loop, a `.service` (oneshot) + a `.timer`:
- `WorkingDirectory=/path/to/yourco-os`, `User=claude-ops`, env with `ANTHROPIC_API_KEY` + tokens.
- `ExecStart=/usr/local/bin/claude -p "<agent prompt>" --output-format json` → journald/log file.
- `OnCalendar=Mon *-*-* 07:00:00` (sales), `07:15` (finance), `07:55` (Atlas briefing), `Wed 07:00` (customer-health), `Fri 07:00` (content), etc. — mirror the current schedule.
- **Wrap each run:** `git pull` before, `git add/commit/push` after, so the OS stays synced and every run is versioned.

The agent prompts are the existing scheduled-task SKILL.md bodies — paste them in (or have the job read the prompt from a file in the repo).

## Step 6 — Approval gates (always-on ≠ auto-send)
Keep the human touchpoints intact in headless mode:
- **`--allowedTools`** / `permissions` in `~/.claude/settings.json` to scope what runs unattended (e.g., Read, Edit, Bash, the read/draft MCP tools) — and **exclude** the side-effectful ones.
- **Pre-tool hook** (`.claude/hooks/`) that blocks must-approve actions — external email send, publishing, payments, touching a client tenant — and routes them to the Founder (log + Slack alert) instead of executing. Mirrors the approval patterns already in each agent's discovery/eval docs.
- Result: loops draft/stage 24/7; anything gated queues for the Founder to approve async (via Cowork / email / Slack).

## Step 7 — Test, then cut over
1. Run the **Monday briefing** headless on the host; confirm the triple delivery (artifact written + Gmail draft + Slack post) and that gated actions were blocked, not executed.
2. Add the remaining loops.
3. (When sending starts) add a small **webhook endpoint** on the host for Instantly replies/bounces → Reilly's handler.
4. Keep **Cowork as the human interface** (direct + approve). Log completion in the decision doc.

## Gotchas
- **Stateless runs:** each `claude -p` is a fresh session — persist state in repo files (the loops already do this; that's the whole "artifact the next run reads" pattern).
- **Absolute paths** in prompts; always `cd` to repo root first.
- **Secrets:** host env / secrets manager, least-privilege, never in the repo.
- **Monitoring:** redirect output to logs; `journalctl -u <service>` for failures; pair with the silence-watchdog already built into the loops.

## References (current Claude Code docs)
- Setup: https://code.claude.com/docs/en/setup
- Headless: https://code.claude.com/docs/en/headless
- MCP: https://code.claude.com/docs/en/mcp
- Permission modes: https://code.claude.com/docs/en/permission-modes
- Env vars: https://code.claude.com/docs/en/env-vars

---

## Appendix A — Exact provisioning commands (copy-paste)

The concrete command sequence for Steps 2–4, with YourCo's real values. Run on a fresh Ubuntu/Debian VPS. Repo is **https://github.com/founder22/yourco-os** (private).

**Before you start, fill in the two real values:**
- `<ip>` — the host's IP, from your VPS provider after you create the box.
- The real `ANTHROPIC_API_KEY` (from the Anthropic Console, pay-as-you-go) — do **not** paste it into any file that gets committed. `~/.yourco/env` lives in the home dir, outside the repo, so it's safe there.

```bash
# A1. Base setup (as root)
ssh root@<ip>
adduser claudeops && usermod -aG sudo claudeops && apt update && apt upgrade -y
su - claudeops

# A2. Node + Claude Code (as claudeops, no sudo — nvm installs to home dir)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc && nvm install --lts
npm install -g @anthropic-ai/claude-code
claude --version

# A3. API key as a sourced secret (chmod 600, never committed)
mkdir -p ~/.yourco && echo 'export ANTHROPIC_API_KEY="sk-ant-..."' > ~/.yourco/env
chmod 600 ~/.yourco/env && echo 'source ~/.yourco/env' >> ~/.bashrc && source ~/.bashrc
```

### A4. Authenticate the private clone — REQUIRED, don't skip
A plain `git clone https://...` of a **private** repo on a fresh VM will stall on a username/password prompt (and GitHub no longer accepts passwords). Pick one:

**Option 1 — SSH deploy key (recommended; scoped to this one repo):**
```bash
ssh-keygen -t ed25519 -C "claudeops@yourco-host" -f ~/.ssh/id_ed25519 -N ""
cat ~/.ssh/id_ed25519.pub   # add this at: github.com/founder22/yourco-os → Settings → Deploy keys → Add (✅ Allow write access, for the git push after each run)
git clone git@github.com:founder22/yourco-os.git ~/yourco-os
```

**Option 2 — fine-grained PAT (if you prefer HTTPS):** create a token at github.com/settings/tokens scoped to *only* `yourco-os` with Contents read/write, then:
```bash
git clone https://<PAT>@github.com/founder22/yourco-os.git ~/yourco-os
```

### A5. Smoke test
```bash
cd ~/yourco-os
claude -p "In one line, what is this workspace?" --output-format json
```
Expect a one-line answer derived from `CLAUDE.md` (it auto-loads as boot context). If it errors on auth, confirm `echo $ANTHROPIC_API_KEY` is set in the shell.

> After this, continue with **Step 4 (MCP connectors)** above — note the OAuth servers (Gmail/Calendar/Drive) need a one-time interactive `claude` + `/mcp` auth on the host. Deploy-key write access (A4 Option 1) is what lets the per-run `git pull`/`commit`/`push` wrapper in Step 5 work unattended.

---

## Appendix B — MCP connector playbook (verified 2026-06-09)

Grounded in current Claude Code docs (code.claude.com/docs/en/mcp). Two auth classes — this is the whole mental model:

| Class | Connectors | How | Headless? |
|---|---|---|---|
| **Static bearer token** | Slack, Vibe, Higgsfield, Descript | Paste token into an `Authorization` header | ✅ Trivial — no browser ever |
| **Browser OAuth** | Gmail, Calendar, Drive (Google) | Google consent screen → token cached | ⚠️ Needs one-time SSH port-forward (server has no browser) |

**Auth-layer distinction (don't conflate):** `ANTHROPIC_API_KEY` (already set in `~/.yourco/env`) authenticates Claude Code → the *model*. That's done. MCP-connector auth below is a *separate* layer (Claude Code → Gmail/Slack/etc.). `CLAUDE_CODE_OAUTH_TOKEN`/`claude setup-token` are just alternates for the *model* layer — irrelevant here.

### CLI + schema (verified)
```bash
# Token-based HTTP connector:
claude mcp add --transport http <name> <url> --header "Authorization: Bearer <TOKEN>" --scope project
# Verify:
claude mcp list           # all servers
claude mcp get <name>     # one server's status
```
Project `.mcp.json` (committed; secrets via `${ENV_VAR}` from `~/.yourco/env`, never literal):
```json
{ "mcpServers": {
  "slack":    { "type": "http", "url": "https://mcp.slack.com/mcp",            "headers": { "Authorization": "Bearer ${SLACK_BOT_TOKEN}" } },
  "descript": { "type": "http", "url": "https://api.descript.com/v2/mcp/claude","headers": { "Authorization": "Bearer ${DESCRIPT_API_KEY}" } }
}}
```
MCP OAuth tokens persist after first interactive auth in `~/.claude/.credentials.json` (Linux, mode 0600); headless `claude -p` runs reuse them automatically — they never trigger a new browser flow.

### Headless Google OAuth — the SSH port-forward
The server has no browser. To complete Google's consent screen once:
```bash
# From the Mac, SSH in WITH the callback port tunneled back to the Mac's browser:
ssh -L 8080:localhost:8080 user@your-vps
# On the server, interactively:
cd ~/yourco-os && claude
/mcp            # pick the Google server → Authenticate → consent opens in the MAC browser via the tunnel → Allow
# token caches on the server; exit. All future headless runs reuse it.
```

### Setup order (easiest → hardest)
1. **Slack** — `api.slack.com/apps` → create app → Bot Token Scopes `chat:write`,`channels:read` → Install → copy `xoxb-…`. Invite bot to the loop channel (`#all-yourco`).
2. **Descript** — Settings → API key. URL `https://api.descript.com/v2/mcp/claude`.
3. **Vibe Prospecting** — provider dashboard → API key + MCP URL. (If OAuth-only, no key → different path.)
4. **Higgsfield** — provider dashboard → API key + MCP URL. (Same caveat.)
5–7. **Gmail / Calendar / Drive** — ONE Google Cloud OAuth client (Web app, redirect `http://localhost:8080/callback`), enable Gmail/Calendar/Drive APIs, scopes `gmail.readonly` + `gmail.compose` (**never** `gmail.send`), `calendar.readonly`, `drive.readonly`. Auth via the port-forward above.

> ⚠️ Vendor MCP endpoint URLs for Slack-hosted / Vibe / Higgsfield are to be confirmed at add-time (`claude mcp add` reports connect success/failure). The Slack *bot token* is required regardless of which Slack MCP server we use (hosted or stdio `npx` community server).

### Build findings (2026-06-09) — corrections from live setup
- **Interactive auth wall:** interactive `claude` forces a one-time `platform.claude.com` account login even with `ANTHROPIC_API_KEY` set (no menu; it jumps straight to OAuth). Complete it once via the copy-paste **code flow** (open URL on Mac, authorize under the **YourCo** org, paste code back). Headless `claude -p` still uses the env API key by precedence. Required before any `/mcp` OAuth.
- **"Easy token tier" mostly collapsed:** vendor *hosted* MCPs (Descript `…/v2/mcp/claude`, Slack `mcp.slack.com`, Higgsfield `mcp.higgsfield.ai/mcp`) require **OAuth**, NOT a bearer token. Descript returns `401 Unauthorized` even with the real API key in the header — confirmed twice.
- **Slack — use the stdio community server, not hosted:** `slack-mcp-server` (korotovsky), stdio via `npx`, bot-token auth, fully headless. Env: `SLACK_MCP_XOXB_TOKEN=${SLACK_BOT_TOKEN}` + `SLACK_MCP_ADD_MESSAGE_TOOL=true` (posting off by default). Bot must be **invited to the target channel**. This is the working `.mcp.json` pattern. (npx note: systemd jobs need nvm's `node`/`npx` on PATH.)
- **Project-MCP approval headless:** set `enableAllProjectMcpServers: true` in the host's **user** settings `~/.claude/settings.json` (machine-local, not committed — keeps Cowork unaffected).
- **Deferred (off critical path):** Descript + Higgsfield are Reed's video tools (OAuth, on-demand only). Parked until Reed's loop needs them; not required for the Monday-briefing dry-run. Critical-path connectors = **Slack + Gmail**.
