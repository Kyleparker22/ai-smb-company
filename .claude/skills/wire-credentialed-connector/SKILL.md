---
name: wire-credentialed-connector
description: Onboard any new API key / OAuth credential into the OS (Slack, Twilio, weather APIs, scraping APIs, …). Use the moment a task needs a service yourco doesn't have a key for yet, or the Founder says "I created the account, now what?" — replaces the ad-hoc where-does-the-key-go Q&A that burned ~18 rounds across 14 services in June–July 2026.
---

# wire-credentialed-connector — land an API credential without the Q&A loop

## When
Any new external service credential (API key, OAuth app, client ID/secret) for either machine (the Founder's Mac or the VPS). NOT for deploying the daemon that uses it (`deploy-vps-daemon`) or for adding a whole loop (`add-runtime-loop`) — this skill ends when the key is verified working.

## Steps
1. **Name the destination up front, before the Founder mints anything:** the exact gitignored env file (absolute path), the exact variable name(s), and **which machine** it lives on ([Mac] or [VPS `~/yourco-os`]). Create the empty scaffold + a committed `.env.example` and confirm the path is covered by `.gitignore`.
2. **Give the console click-path with the required scopes/type up front.** Wrong scopes are the #1 repeat failure (Slack `missing_scope` ×3; Instantly needed `leads:create`, got `all:read`). State exactly what to select at key-creation time, not after the first 401/403.
3. **Fetch the API docs yourself** (WebFetch) — never have the Founder paste doc pages into chat.
4. **Land the key with an echo-append one-liner** (`echo 'KEY=…' >> path`), not nano — and the secret goes **straight into the env file, never pasted into chat** (chat transcripts persist on disk; a pasted secret is a rotate-me secret).
5. **Verify live immediately:** one copy-paste self-check command (curl or the consuming script's dry-run) that proves the key + scopes work. Restart the consuming service if one exists.
6. **Register it:** add the connector + env path + scope to `runtime/connectors.md` (and `.mcp.json` where applicable), and to the sanctioned connectors list in `runtime/agent-registry.json` if a headless loop will use it.

## Gotchas
- A key that "will be added later" ships a dead integration — Sadie's intent loop ran for weeks with YouTube/Bluesky silently skipped on missing keys. Step 5 is not optional.
- Label every command block [Mac] or [VPS]; a VPS block once got run on the Mac.
- If a secret does end up pasted in chat: finish the wiring, then tell the Founder to rotate that key.

## Canonical doc
`runtime/connectors.md` is the registry of what's wired where; this skill is the procedure for adding to it.
