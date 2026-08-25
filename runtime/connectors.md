# Connectors — what's wired headless vs. Cowork-only

> **Status: LIVE REFERENCE** — the headless-vs-Cowork map. Check here before assuming a loop can reach a connector.

> Honest map of where each connector lives, and how to migrate one to the always-on runtime if a loop actually needs it. Created 2026-06-25. Owner: Kemba (platform) + Rafi (sanctioning).

## Two surfaces
- **Headless runtime (VPS):** the always-on loops run via `claude -p` under the approval gate (`runtime/headless-settings.reference.json`). Their MCP servers are defined in **`.mcp.json`** (committed) and authenticated by host-side tokens/OAuth.
- **Cowork (interactive):** the Founder's supervised sessions reach *many* MCP connectors. These are designed for interactive use and are NOT all suitable for headless automation.

## Wired headless today (`.mcp.json`)
| Connector | Scope on runtime | Used by |
|---|---|---|
| **Slack** | post + read/search | every loop (posts to its channel) + the command listener |
| **Gmail** | read + **draft** + label/archive — **send/delete DENIED** by the gate | Jim (inbox triage), any drafting loop |
| **Calendar** | read + **write-holds** — ✅ **verified live 2026-06-25** (Jim placed a real hold via Slack command). `create-event`/`update-event` enabled; delete excluded; external-attendee invites approval-gated. | Jim (scheduling) |

That trio is exactly what the scheduled loops need: read context, draft, post — nothing that sends, pays, or deletes.

**Slack-commanded agents have the same connector access as the scheduled loops** (verified 2026-06-25): the listener sources `~/.yourco/env` + nvm before running the agent, so a commanded Jim/agent can use calendar, Gmail-draft, etc. — not just file ops. (Before the 2026-06-25 fix, commanded agents got *no* MCP connectors.)

## Cowork-only today (NOT headless — and mostly shouldn't be)
Drive · Canva · Descript · Higgsfield · DocuSign · Granola · Monarch · Todoist · Vibe Prospecting. All verified live in Cowork (smoke-test 2026-06-25). They stay interactive **by design** — the work that uses them is supervised:
- **Reed's** video/design (Higgsfield, Descript, Canva) is a creative-direct + review loop, not unattended.
- **Reilly's** sourcing (Vibe) is gated on the Founder's batch approval anyway; the `runtime/*.py` machine is run by the Founder (the gate denies `Bash` headless).
- **Ray** (DocuSign) touches contracts → human-supervised. **Monarch is the Founder's *personal* finances — deliberately NOT connected to yourco company finance (2026-06-25).** Charles/Harry's company-finance source is the repo ledgers (`finance/`) + a business account TBD, not Monarch.
- Granola/Drive/Todoist are read-context the Founder pulls in when relevant.

**So "migrate every connector headless" is not the goal** — it would expand the unattended attack surface for little benefit. Migrate a connector only when a *specific loop* needs it unattended.

## How to migrate ONE connector to the runtime (when a loop needs it)
1. **Add its MCP server to `.mcp.json`** — `npx` stdio server + env, scoping to **read-only tools** where supported (mirror the calendar `ENABLED_TOOLS` pattern).
2. **Provide auth on the host** — token env var or OAuth keys file under the runtime user (e.g. `~/.calendar-mcp/`). *(This step is host-only — it can't be done from Cowork.)*
3. **Allow its read tools in the gate** — add to `runtime/headless-settings.reference.json` `allow` (keep writes/sends in `deny`) and copy to the host's `~/.claude/settings.json`.
4. **Sanction it** — add to `sanctioned_connectors_allow` in `runtime/agent-registry.json` (so Rafi's drift watchdog stays clean).
5. **Restart + test** headless (`claude -p` smoke run; confirm send/write stays denied).

⚠️ **Caveat:** several Cowork connectors are **remote/OAuth MCPs** (Canva, DocuSign, Monarch, Granola, Vibe), not simple self-hostable stdio servers — a headless port may not exist or may need a server-token flow. Verify per provider before promising a loop.

## Realistic next candidates (only if you want them)
- **Calendar write** for Jim — ✅ **live + verified 2026-06-25** (Jim placed a hold via Slack command; event created on the Founder's calendar, no email/delete). `runtime/calendar-auth.md` is the fallback only if the token ever needs re-auth.
- **Drive read** for a docs-aware loop — low risk (read-only).
- Everything else: leave in Cowork unless a concrete loop demands it.

## Client-engagement connectors — Sample Client platform (added 2026-08-07)
The Design Studio platform (`clients/sample-client/platform/server.py`, :8804) has its own per-client credential store: **`clients/sample-client/platform/.env`** (gitignored; scaffold = `.env.example`; machine = the Founder's Mac, VPS copy at go-live). Status/tests: `/api/integrations/status` + `/api/integrations/test/<name>` — presence + live checks only, values never leave the file.

| Service | Env keys | Kind | Live check |
|---|---|---|---|
| HubSpot (Client Owner's tenant) | `HUBSPOT_TOKEN` (private-app token, crm.objects.contacts+deals r/w, companies read) | API | GET crm/v3/objects/deals?limit=1 |
| Aspire | `ASPIRE_CLIENT_ID` + `ASPIRE_CLIENT_SECRET` (Admin → Integrations → API) | API | POST cloud-api.youraspire.com/Authorization |
| SiteOne | `SITEONE_USER/PASS` | portal (no public API) | presence only — exports in via CSV; automated portal pulls ToS-gated (Ray) |
| Ewing Outdoor Supply | `EWING_ACCOUNT` + `EWING_OTP_PHONE` | portal-otp (passwordless — SMS code to shortcode 5488; login stays human, exports in via CSV) | presence only |
| Latham's Nursery | `LATHAM_PASSWORD` | password-gate (no username — one shared password unlocks lathamsnursery.com/wholesale) | presence only — human unlocks page, list in via CSV |
| Shepherd's Landscape Supply | (none — public site) | public-site reader (`platform/integrations/shepherds_reader.py`): robots.txt-allowed, identifying UA, 1 req/sec, weekly; JSON-LD name/SKU/price/in-stock from ~1,446 product pages | live sitemap check + pull endpoint |
| Kirk Davis Nursery | `KIRKDAVIS_USER/PASS` + `AVAILABILITY_REPORT_EMAIL` | email-report (portal is CAPTCHA-walled) | presence only — sanctioned path = emailed weekly availability reports |

⚠️ Client credentials in a client engagement folder, never in `~/.yourco/env` — per-client isolation. ⚠️ Ray's counsel gate: no pulls against Client Owner's production tenants until the 1-page agreement is signed (`processes/counsel-gates.md`).
