# Decision — Always-On Runtime for YourCo's Agents

**Date:** 2026-06-09
**Owner:** **Kemba** (Platform / Template Engineer — *not yet built*; **the Founder holds as builder-operator** until Kemba exists)
**Status:** ✅ Plan locked · 🟢 **OPERATIONAL** — all 4 weekly loops live & self-gating (2026-06-10)

> **Update (2026-06-10): all four weekly loops LIVE.** Added + smoke-tested **sales** (Mon 07:00, Atlas), **finance** (Mon 07:15, Charles), **content** (Fri 07:00, Katie) alongside the **briefing** (Mon 07:55) — full Monday stack fires in dependency order. All ran clean headless via systemd, self-gated (no `--allowedTools`), auto commit/push. **Gate polished**: added WebSearch + Slack read tools to `allow` — content used WebSearch with zero denials. **Key insight that simplified things:** the weekly *sales* loop needs no Vibe (it's a pipeline review off `_pipeline.md` + Gmail + Calendar); Vibe is only for on-demand *sourcing* → deferred. Loops already earning: finance flagged a likely ~$194/mo Instantly duplicate-billing leak; sales surfaced the email-only-now vs wait-for-SMS decision. **Remaining:** customer-health loop (pre-client no-op; wire at first client), Vibe (on-demand sourcing), Descript/Higgsfield (Reed, deferred), Instantly-replies webhook (when sending starts).

> **Calendar LIVE (2026-06-10):** `@cocal/google-calendar-mcp` (stdio), read-only via `ENABLED_TOOLS=list-calendars,list-events,search-events,get-event,get-freebusy,get-current-time`. Auth: needed a **Desktop**-type OAuth client (the gongrzhe Gmail server used a Web client; @cocal requires `installed` format) — one-time auth on Mac → token `~/.config/google-calendar-mcp/tokens.json` + Desktop keys `~/.calendar-mcp/gcp-oauth.keys.json`, both scp'd to host. Gate allows `mcp__calendar` (safe — only read tools exposed). Briefing + sales loops now auto-populate "this week's calls" with no loop changes. Token holds broad `calendar` scope (not readonly) — same as Gmail; read-only enforced at the tool/exposure layer. **All connectors the live loops need are now wired: Slack + Gmail + Calendar.**

> **Cadence rounded out + watchdog added (2026-06-10):** Now **7 timers** live. Added: **runtime health-watchdog** (Mon 08:15 — Atlas verifies each weekly loop wrote a fresh artifact + logged OK; weekly Slack heartbeat, alerts on silent failure; `runtime/prompts/watchdog.md`), **Brett monthly advisor** (1st of month 08:00, `processes/loops/advisor.md`), **Charles monthly close** (1st Mon 08:30, `finance/monthly_close.md`). Deferred (no loop SOP yet + not due till early July): Luka brand audit, Polo quarterly pricing — write their loop SOPs before wiring. The watchdog is the observability layer of the moat, now self-hosted.

> **MILESTONE (2026-06-09 late): Steps 5–6 DONE — the Monday briefing runs fully autonomous.** systemd timer (`yourco-monday-briefing.timer`, Mon 07:55 ET) → `run-loop.sh` → headless `claude -p` → triple delivery (artifact + Gmail draft + Slack post) → auto commit/push. Smoke test (`systemctl start`) passed: `success`, draft NOT sent, commit `03bd9a5` pushed by the wrapper. **Approval gate proven in production**: ran with NO `--allowedTools` flag — the gate lives in the host `~/.claude/settings.json` `permissions` (allow drafts/posts/reads; deny send/delete/Bash), and `permission_denials` shows it *blocked* `mcp__slack__channels_list` (not on allowlist) while the agent adapted and completed. Scaffolding: `run-loop.sh`, `runtime/` (prompts, systemd units, gate reference, README). Server tz set to America/New_York.
> - **Watch-items (minor, non-blocking):** (a) date-labeling — the test ran across UTC-midnight so the model dated the artifact 06-09 (session date) vs the server's 06-10 clock, overwriting the prior 06-09 briefing (recoverable in git); real Monday runs won't straddle midnight. (b) `channels_list` denial is cosmetic — add Slack read tools to the gate `allow` list if we want loops to skip the wasted turns.
> - **What's left = repeat the proven pattern:** the other loops (sales 07:08, finance 07:24, customer-health Wed, content Fri, monthly/quarterly) each = a `runtime/prompts/<loop>.md` + a copied systemd unit; remaining connectors (Vibe for sales, Calendar/Drive nice-to-have, Descript/Higgsfield deferred); webhook endpoint for Instantly replies when sending starts.

> **Status snapshot (2026-06-09):** `_archive/always-on-runtime-status-2026-06-09.md` (archived — point-in-time report; runtime is now live).
>
> **Execution log (2026-06-09):** Base host + Claude Code runtime is **LIVE**. Steps 1–4 of the hand-off runbook done:
> - **Host:** Hostinger VPS, Ubuntu 24.04, hostname `srv1745256`, IP `2.25.192.101`. Working user `claudeops` (sudo).
> - **Runtime:** Node 24 LTS (nvm), Claude Code `2.1.170`, authed via `ANTHROPIC_API_KEY` in `~/.yourco/env` (chmod 600, outside repo).
> - **Repo:** `yourco-os` cloned to `~/yourco-os` via SSH **read-write deploy key** `yourco-host (claudeops VPS)` (enables unattended pull+push).
> - **Smoke test passed:** `claude -p "..." --output-format json` returned a correct `CLAUDE.md`-grounded answer, `is_error:false`, ran on Opus 4.8 (~$0.04). Full chain verified end-to-end.
> - Exact commands captured in `/processes/claude-code-setup.md` Appendix A.
>
> **Remaining (Steps 5–9):** MCP connectors re-auth (interactive OAuth on host — Gmail/Calendar/Slack/Vibe/Higgsfield/Descript), scheduled loops → systemd timers/cron with git-pull/commit wrapper, approval-gate hooks (always-on ≠ auto-send), test one loop e2e headless, webhook endpoint for Instantly replies, cutover.

> **Connector progress (2026-06-09 late):** **Slack LIVE** ✅ — first connector proven end-to-end (Claude Code → `slack-mcp-server` korotovsky stdio → posted to `#all-yourco`). Posts as **Atlas** (app "Atlas", bot user "webb"), bot-token auth, scopes `chat:write`+`channels:read`+`users:read`+`groups:read`+`im:read`+`mpim:read`. **Approval gate confirmed working**: headless `claude -p` *blocked* the Slack write by default; posted only when `--allowedTools "mcp__slack__conversations_add_message"` was passed — exactly the decided posture (internal post = auto-allow). Step 3 will encode this in `permissions.allow/deny` so loops run unattended. Descript/Higgsfield deferred (OAuth, off critical path).

> **Gmail LIVE** ✅ (2026-06-09 late) — second connector proven e2e. Server: `@gongrzhe/server-gmail-autoauth-mcp` (stdio). Auth: one-time OAuth on the Founder's Mac → refresh token in `~/.gmail-mcp/` → scp'd to server (no port-forward needed, no browser on host). **Internal Workspace consent screen** under the yourco.com GCP org ⇒ refresh token **never expires** (avoided the 7-day External-testing trap). Headless `claude -p` created a real **draft** to founder@yourco.example.com with `--allowedTools "mcp__gmail__draft_email"`. **Caveat (load-bearing):** gongrzhe requests the broad `gmail.modify` scope (can send+delete), so draft-only is enforced ONLY by the Step-3 permission gate (allow `draft_email`, deny send/delete), NOT by scope. **Both Monday-briefing connectors (Slack + Gmail) now live.** Remaining connectors: Vibe (sales loop), Calendar/Drive (nice-to-have), Descript/Higgsfield (deferred).

### Approval posture (decided 2026-06-09)
Two distinct kinds of "approval" — keep them separate:
- **Setup approvals** (MCP-server enable, folder trust, one-time OAuth) → one-time on the host, cached, then never recur. Not a business gate; eliminated for autonomous operation.
- **Business-action gates** (the moat) → scoped by tool allow/deny in Step 3, NOT removed.

**Day-one line (the Founder approved):**
- **Auto, no human:** all file writes, research/reads, internal Slack posts, Gmail/Drive *reads*, all drafting/staging (incl. Gmail *draft* creation).
- **Gated (must-approve):** external email *send*, publishing, payments, deletes, anything touching a client tenant.
- **Ratchet:** a gate is auto-approved only once the agent *earns* it via clean eval runs (eval → trust → automate). Rationale: YourCo sells "we own reliability + approval"; an ungated autonomous external send (esp. Reilly, given TCPA/FTSA/10DLC/warmup) is the one failure that damages the executive-trust being sold. Earn each removal.

## Problem
Today the agents run inside the **Cowork desktop app**. Consequences:
- Scheduled loops (Atlas Monday briefing, sales/finance loops, Wed customer-health, Fri content, etc.) only fire when the desktop app is open. Miss a Monday morning → the loop runs late or not at all (this already caused the silence-watchdog incident).
- API-gated, autonomous steps can't run: the Reed VO render, receipt auto-logging, and **inbound webhooks** (Instantly replies/bounces → Reilly) all need a process that's always listening.
- The whole "agents run the business while the Founder sleeps" thesis depends on a runtime that's always up.

## Decision
Migrate the agents to an **always-on, headless runtime**. Cowork remains the **human interface** (where the Founder directs + approves); the server runs the **automated** work against the same workspace.

### v0 target — Option A (recommended): Cloud VM + Claude Code headless + git-synced workspace + cron
- A small always-on Linux host (a $5–10/mo VPS, Fly.io, or Railway).
- **Claude Code** installed + authenticated, run **non-interactively** (`claude -p "<agent prompt>"`) for each scheduled job.
- The **workspace lives in a git repo** (GitHub) — persists, versions, and syncs between Cowork and the server. memory/ travels with it.
- **System cron** invokes each agent at its time (replacing Cowork's scheduler): Mon 7:00 sales, 7:15 finance, 7:55 Atlas briefing, etc.
- **MCP connectors** (Gmail, Calendar, Slack, Vibe, Higgsfield, Descript, …) re-authenticated in the server's Claude Code config.
- A tiny **webhook endpoint** on the host receives Instantly reply/bounce events → triggers Reilly's reply handler.

### Same-day stopgap — Option C: always-on desktop
If you want reliability *this week* with zero infra work: run Cowork on a machine that **stays on** (a spare Mac/mini, sleep disabled) and leave the app open. Fragile (OS updates, restarts, no headless API steps) but it fixes the "loops miss because the laptop was closed" problem immediately. Use as a bridge while Option A is stood up.

### Not now — Option B: Claude Agent SDK app
Rebuild agents as deployed SDK programs. More power (real orchestration), more engineering. Revisit at v1+ when complexity warrants — pairs with Kemba's `yourco-template` extraction.

## What migrates (Option A)
| Piece | Today | After |
|---|---|---|
| Workspace files + memory | Local folder (Cowork) | **Git repo** cloned on the host; Cowork pulls/pushes |
| Scheduler | Cowork scheduled tasks | **cron** → `claude -p` headless runs |
| Agent prompts | `/Scheduled/*/SKILL.md` | Same prompts, invoked headless |
| MCP connectors | Cowork session auth | Re-auth in server Claude Code config (one-time interactive setup) |
| Secrets/keys | Cowork-managed | Host env / secrets manager (least-privilege) |
| Webhooks | none | Small endpoint on the host (Reilly replies) |

## What it unblocks
- All scheduled loops fire **24/7**, desktop or not.
- **Reed VO render** can be automated via a TTS API call from the server (closes the one manual video step).
- **Charles receipt auto-logging**, **daily inbox triage**, **Reilly reply engine** all become real (they need an always-listening process).
- Webhook-driven feedback (replies/bounces → suppression + pipeline) works.

## Risks / watch-items
- **MCP OAuth in headless env** — Gmail/Calendar/Slack OAuth need a one-time interactive auth on the host; budget for it.
- **Sync discipline** — git is the source of truth; the server `git pull` before each run and commits after. Avoid editing the same file in Cowork and on the server simultaneously.
- **Secrets on a server** — least-privilege tokens, no plaintext in the repo.
- **Cost** — ~$5–10/mo host; negligible vs the value.
- **Approval gates still hold** — automated runs still **draft/stage**; anything in the must-approve list still waits for the Founder. Always-on ≠ auto-send.

## Execution runbook (hand-off — the Founder / dev)
> **Detailed step-by-step with exact commands:** `/processes/claude-code-setup.md` (Claude Code install/auth/MCP/systemd/approval-gates, grounded in current Claude Code docs).
1. Put the `YourCo LLC - AI` workspace into a **GitHub repo** (private).
2. Stand up the **host** (VPS / Fly / Railway).
3. Install **Claude Code** on it; authenticate (API key or subscription).
4. Clone the repo; set up `git pull`/commit hooks around runs.
5. **Re-auth the MCP connectors** in the host config (Gmail, Calendar, Slack, Vibe, Higgsfield, Descript).
6. Port the **scheduled tasks → cron** (one cron line per loop, invoking `claude -p` with that agent's prompt).
7. **Test one loop end-to-end headless** — run the Monday briefing manually on the host; confirm the triple delivery (artifact + Gmail draft + Slack) works.
8. Add the **webhook endpoint** for Instantly replies (when sending starts).
9. Cut over; keep Cowork as the human interface. Log completion here.

## Ownership
This is the **platform layer** → **Kemba** when built; **the Founder holds** now. Once live, it's the substrate Kemba's `yourco-template` and every agent runs on. Update CLAUDE.md's internal-platform section + the roster (done 2026-06-09).
