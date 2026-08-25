# 04 — Claude Code, MCP connectors, and local surfaces

> **Build step 04.** Nothing here is done yet. Where this page shows a filled-in value, that is
> the source company's — replace it with yours.

## What this layer is

The interactive environment. **Cowork** is the supervised session where a human is present; it reaches
many connectors and can run shell commands. The always-on runtime (step 05) is deliberately far more
restricted. Keeping those two straight is most of what makes this safe.

Setup: `processes/claude-code-setup.md`.

## MCP connectors — what is actually wired, and why so few

`.mcp.json` declares the servers available **headless**. As of 2026-08-25 that is exactly three:

| Server | Why it earns headless access |
|---|---|
| **slack** | agents post to their own channels; the Founder commands them back. The two-way control surface. |
| **gmail** | **draft-only.** Agents draft; sends are denied by the gate. |
| **calendar** | reads, plus a proven write path for holds |

**Cowork reaches many more** — Vibe, Higgsfield, Granola, DocuSign, Canva, Monarch, Drive, Todoist,
and others. Most are remote/OAuth servers that cannot be self-hosted on a VPS anyway.

⚠️ **"Migrate every connector headless" is explicitly NOT the goal.** Every server added to the
always-on runtime widens the unattended attack surface. `runtime/connectors.md` is the live map of what
runs where, and carries the 5-step procedure for migrating one connector when a loop genuinely needs it.

**Keep `.mcp.json` static.** Dynamically adding or removing tools invalidates the model's prompt cache
from the point of change — a lesson taken from Manus (`decisions/2026-07-05_tool-triage.md`).

## Credentials — one pattern, no exceptions

Every key lives in a **gitignored** env file: `runtime/.<service>.env`. The shape matters —
`.gitignore` matches `*.env`, so `runtime/.stripe.env` is ignored and **`runtime/.env.stripe` is
not**. Confirm before writing a single character of the secret:

```bash
git check-ignore -v runtime/.<service>.env
```

Wired today: `anthropic-admin`, `slack`, `twilio`, `instantly`, `firecrawl`, `outscraper`, `recraft`,
`yelp`, `youtube`, `bluesky`. Procedure for adding one: `.claude/skills/wire-credentialed-connector/`.

**Secrets never get pasted into chat** — transcripts persist on disk. One that does gets rotated.

## Before wiring any connector: the terms check

Read the service's *current* API terms for (a) commercial use and (b) feeding content to an LLM.
Several major platforms forbid one or both on free tiers — **Reddit and X are confirmed**
(`learnings/ops/2026-06-11_platform-api-terms-gate.md`). A ToS-violating scraper is an auto-skip, not
a design problem to work around.

## When there is no MCP

Build a small CLI instead — `.claude/skills/build-cli-connector/`. The thing to understand up front:
**a headless loop cannot run a CLI** (the gate denies Bash), so design for the *output*, not the
invocation. Three delivery paths, in preference order: an artifact a loop reads, wrapper injection via
`run-loop.sh`, or a real MCP server. Picking wrong produces a tool that works in Cowork and silently
does nothing in production.

## Local surfaces — never guess a port

`.claude/launch.json` is the single registry of every local server (~103 entries). Start things **by
name**, never by URL:

```bash
./show.sh        # website · HQ · CRM · connector console · the app gateway
```

A new surface gets a `launch.json` entry and a verified 200 **before** any link is shared —
`.claude/skills/show-surface/`. A consistency invariant enforces that no two entries share a port.

## Done when

**`./show.sh` opens a local surface, and one MCP connector answers a real query.**

If you cannot point at that, the step is not finished — do not move on.
