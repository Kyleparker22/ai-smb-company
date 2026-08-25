# Calendar MCP — authenticating on the VPS (enables Jim's holds/reschedules)

> **Status: UNVERIFIED — treat as unresolved.** The calendar MCP is wired in `.mcp.json`, but this page and `proposed-holds.md` both describe write tools as unavailable headless, while a 2026-06-25 commit claims calendar-write was verified live. Nobody has reconciled the two. Do not assume Jim can place a hold until someone re-tests it.

> `.mcp.json` wires `@cocal/google-calendar-mcp` (nspady) with read tools + `create-event`/`update-event`, but it surfaces **no tools** until the OAuth flow is completed on the VPS **with calendar write scope**. Jim flagged this 2026-06-25 ("no calendar tools in the headless session"). This is the fix. Owner: Kemba (config) + the Founder (the one-time browser auth). Sources: [npm](https://www.npmjs.com/package/@cocal/google-calendar-mcp) · [auth docs](https://github.com/nspady/google-calendar-mcp/blob/main/docs/authentication.md).

> **Correction (2026-06-25):** the actual "no calendar tools" blocker was the **Slack-listener environment** — it spawned `claude` without sourcing `~/.yourco/env` + nvm, so the `npx`-based MCP servers (calendar/gmail/slack) didn't load for *commanded* agents (scheduled loops were fine). Fixed in `runtime/slack-agent-listener.py` (it now mirrors `runtime/run-loop.sh`). The OAuth/token were valid all along. **This runbook still applies only if you genuinely need to re-auth the calendar token** (e.g. the testing-mode expiry below).

## Likely root cause (check this first)
If the calendar MCP *used* to work and now shows no tools, the most common cause is an **expired refresh token**: a Google OAuth consent screen left in **"Testing"** mode expires refresh tokens after **~7 days**. Fix permanently by setting the OAuth consent screen to **"In production"** (Google Cloud Console → APIs & Services → OAuth consent screen → Publish app) — for a single internal user that's safe and stops the weekly death.

## 1. Diagnose (on the VPS)
```bash
ls -l ~/.calendar-mcp/gcp-oauth.keys.json          # the OAuth CLIENT keys (.mcp.json points here)
ls -l ~/.config/google-calendar-mcp/tokens.json    # the saved TOKEN (created by `auth`)
```
- **No keys file** → the OAuth client was never placed. In Google Cloud Console create an **OAuth client → Desktop app**, download the JSON, save it to `~/.calendar-mcp/gcp-oauth.keys.json`.
- **No tokens.json** → never authed (most likely Jim's case) → do steps 2–3.
- **tokens.json exists but write fails** → re-auth with the full calendar scope (step 2–3), or it's the testing-mode expiry above.

## 2. Make sure the consent grants WRITE
Google Cloud Console → OAuth consent screen → **Scopes** must include **`https://www.googleapis.com/auth/calendar`** (full read+write), not just `.../calendar.readonly`. Jim only needs create/update; full calendar covers it, and `delete-event` stays disabled at the `.mcp.json` layer regardless.

## 3. Authenticate — pick one (the VPS has no browser)
**Path A — easiest: auth on your Mac, copy the token up.** On the Mac (browser + the *same* `gcp-oauth.keys.json`):
```bash
export GOOGLE_OAUTH_CREDENTIALS=/path/to/gcp-oauth.keys.json
npx @cocal/google-calendar-mcp auth      # browser opens → sign in as founder@yourco.example.com → grant Calendar
```
Then push the token to the VPS:
```bash
ssh user@your-vps 'mkdir -p ~/.config/google-calendar-mcp'
scp ~/.config/google-calendar-mcp/tokens.json user@your-vps:~/.config/google-calendar-mcp/tokens.json
```

**Path B — auth on the VPS via an SSH tunnel.** The flow redirects to `http://localhost:<port>`; forward that port to your Mac's browser:
```bash
# from your Mac (swap the port for whatever the tool prints):
ssh -L 3000:localhost:3000 user@your-vps
# then on the VPS:
export GOOGLE_OAUTH_CREDENTIALS=~/.calendar-mcp/gcp-oauth.keys.json
npx @cocal/google-calendar-mcp auth      # paste the printed URL into your Mac browser; it redirects back through the tunnel
```
Path A avoids the port guesswork — prefer it.

## 4. Verify
```bash
ls -l ~/.config/google-calendar-mcp/tokens.json     # exists + fresh timestamp
```
Then the real test — in **#yourco-jim**: *"put a 30-min hold on my calendar tomorrow at 2pm."* If it lands, write scope is live. (No service restart needed — the MCP is spawned fresh per `claude -p` run.)

## Notes
- **Token is per OAuth client** — Path A works because it's the same client keys on both machines.
- **`delete-event` stays out** of `ENABLED_TOOLS` (cancellations remain manual); external-attendee invites stay approval-gated by Jim's prompt.
- **Version check:** confirm the `auth` subcommand against the installed `@cocal/google-calendar-mcp` version if it errors.
