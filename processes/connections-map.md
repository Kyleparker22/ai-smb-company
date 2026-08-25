# Connections map — what's wired, where

> The authoritative "what's connected to what" for the OS. Two separate connection points — **Cowork** (the human session on the Founder's Mac) and **the runtime** (the always-on VPS where the loops + Reilly run) — plus native API integrations and per-client connections. Something connected in one place is NOT automatically available in the other. Update this when a connection changes. Owner: Kemba/platform.

## The three kinds of connection
1. **Cowork MCP connectors** — tools available to the assistant in a Cowork session (the Founder's Mac).
2. **Runtime connectors** — what the always-on VPS host can reach during headless loop runs (under the approval gate: post/draft yes, send/delete/Bash no).
3. **Native API integrations** — yourco-owned code that calls an API directly with a key in a gitignored env file (no MCP, no third party). Works wherever the code + key live.

## Cowork MCP connectors (this session)
Connected / available: **Gmail · Slack · Google Calendar · Google Drive · Vibe Prospecting · Canva · DocuSign · Granola (meetings) · a media/video generator (Higgsfield-class) · Descript · Monarch (the Founder's personal finance, not yourco's books)** · plus computer-use, Chrome, preview.
> Verify by what the assistant can actually call — the registry's "installed connectors" card has been unreliable. Re-check at add-time.

## Runtime connectors (the VPS)
- **Slack** (post) + **Gmail** (draft-only) — live on the host, draft/post allowed, send/delete/Bash denied (`~/.claude/settings.json`).
- **Slack two-way listener** — `runtime/slack-agent-listener.py` (systemd `yourco-slack-listener`), the Founder commands agents in their channels.
- Pending migration: **Vibe / Calendar** on the runtime (per `runtime/README.md`).

## Native API integrations (yourco-owned code + a key in a `*.env`)
- **Anthropic (Claude)** — `dashboard/melanie.py`, the brain for Melanie/Enrich/drafting. Key: `dashboard/melanie.env`.
- **ElevenLabs (voice)** — already integrated *natively* in `melanie.py` (`speak()`) for Melanie's voice. Key: `dashboard/melanie.env` (`ELEVENLABS_API_KEY`, `MELANIE_VOICE_ID`). **Not a Cowork MCP** — see below if you want it as one.
- **Outscraper (Google Maps sourcing)** — `runtime/outscraper.py` (built + **LIVE/verified 2026-06-15**): pulls local-business listings (name/address/phone/site). Verified live — pulled real Yourtownlandscapers; note most local trades return phone+address but **no website/email** (= a positive weak-footprint ICP signal, but means SMS/call-channel or needs Enrich before Instantly). Key: `runtime/.outscraper.env` (set on the Mac). Feeds the sourcing pipeline below.
- **Multi-source sourcing pipeline** — `runtime/sourcing.py` (built 2026-06-14, retargeted 2026-06-15): Outscraper + Instantly SuperSearch + Vibe → normalize → dedupe (domain/phone/name) → **stage into an Instantly campaign** (the cold system of record — NOT the CRM). Dry-run by default; staging only, never sends. Setup: `runtime/sourcing-setup.md`. Implements `decisions/2026-06-07_multi-source-sourcing.md` + `decisions/2026-06-15_prospect-data-architecture.md`.
- **Intent board push (the 1-click)** — `runtime/intent_server.py` (built 2026-06-15): serves a scored intent file as a clickable board; **Add to CRM** (David — only records with contact info, per the contact-info gate) + **Enrich → stage to Instantly** (Reilly — email-bearing → cold campaign, never sends). the Founder clicks, the agent does the labor. Run: `python3 runtime/intent_server.py intent-<vertical>.json --campaign "Intent — X"` → localhost:8799.
- **Audit → engagement scaffolder** — `runtime/scaffold_engagement.py` (built 2026-06-15): the realistic "1-click build" — takes the Audit findings → clones `_yourco-template` into a client folder + pre-fills `01_discovery.md` from the diagnosis + writes SCAFFOLD-NOTES. Scaffolds ~80%; integration + eval + the approval gate stay Kimi's human+build work (the moat, by design). Dry-run default; `--commit` creates.
- **Promotion gate (reply → CRM)** — `runtime/promote.py` (built 2026-06-15): reads Instantly warm replies (`instantly.warm_replies()`) and promotes each into the native CRM as a real lead (company "warm — replied" + contact + `prospect` deal, owner Reilly). Dry-run by default; reads Instantly only, never sends. The ONLY path cold leads enter the CRM. Per `decisions/2026-06-15_prospect-data-architecture.md`: **cold lives in Instantly, warm graduates to the CRM.**
- **Instantly (outbound)** — `runtime/instantly.py` (built + **LIVE/verified 2026-06-14**; campaign-create added 2026-06-15): authenticates against the API v2, reads campaigns, **creates a campaign loaded with Reilly's paused 4-touch sequence** (`--create`, parses `processes/outbound/sequence-copy.md` → DRAFT/PAUSED, **never activates** — no activate path exists), stages leads into campaigns, and reads warm replies (`warm_replies()`). **Staging only, never sends.** Key: `runtime/.instantly.env` (set on the Mac; **add the same on the VPS for Reilly's real runs**). Setup: `runtime/instantly-setup.md`. Note: Instantly is behind Cloudflare — the connector sends a browser User-Agent so requests aren't 403'd (code 1010).

## Set up as a tool/account, but NOT wired into the OS
- **NotebookLM (Google)** — Brett's (+ the Founder's) **manual research tool**, not an API/MCP. There's **no public NotebookLM connector** — it's a consumer/Workspace web app, so nothing auto-syncs. Use it by hand: spin up a notebook per competitor/topic, drop in sources (their site, reports, transcripts, the Meta-ad teardowns), interrogate it, and feed the synthesis back into Brett's `competitive-watch.md` + monthly memo. The *agent* stays Brett; NotebookLM is a power tool he's handed. (If the Founder wants it deeper, any automation would go through Google Workspace/Agentspace enterprise APIs — gated, confirm before relying.)
- **QuickBooks / real accounting** — Charles runs on markdown ledgers; QuickBooks not connected. (Monarch ≠ yourco's books.)
- **Voice stack — Vapi / Twilio / ElevenLabs-for-clients** — per-engagement; connected at a client's build, not standing.
- **Aspire** (Sample Client) — client-side, connected during that engagement's build, not now.

## ElevenLabs as a Cowork connector (the ask, 2026-06-14)
There is **no ElevenLabs connector in the registry** (searched), so it's not a click-connect. But ElevenLabs ships an **official, first-party MCP server** (`elevenlabs-mcp`) — low supply-chain risk (unlike a random third party). To add it as a Cowork tool: add the official `elevenlabs-mcp` server in Cowork's custom-MCP/connector settings with your `ELEVENLABS_API_KEY` (the one already in `dashboard/melanie.env`). **the Founder does this** — the assistant can't enter the key or change app settings. Note: ElevenLabs is *already* working natively for Melanie's voice; a Cowork MCP only adds in-session TTS for the assistant (useful for prototyping voice agents / Vapi voices; Reed's demos are animated-no-AI-voice by decision, so not for those).

## The rule that prevents the recurring confusion
"We set up X" (an account/tool exists) ≠ "X is connected to Cowork" (a tool the assistant can call) ≠ "X is on the runtime" (the VPS can reach it). Three different states. When asking "is X connected?", name which of the three.
