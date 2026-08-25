# Decision — native CRM stays; Attio is the benchmark (build-vs-buy)

**Date:** 2026-06-14 · **Owners:** the Founder + David (CRM) · **Status:** settled (revisit trigger below)

## Decision
Keep the **native CRM** (`crm/`, David). Do **not** move to Attio or another SaaS CRM now. Treat Attio as the **category benchmark to steal ideas from**, not a system to adopt. Extends `decisions/2026-06-10_native-crm-david.md`.

## Why native wins now
The native CRM *is* the OS. The CRM, the HQ dashboard, Melanie, and the runtime loops all read/write the same git-backed JSON — **one source of truth, zero cost, fully owned**, and part of the glass-box story (yourco runs on the tools it builds). Adopting Attio means a second source of truth, a vendor holding the data, a subscription, and losing the native Melanie/dashboard/loop integration. For a solo founder running an integrated OS, that's a step backward.

## The honest caveat
Attio is genuinely excellent — if yourco weren't building this OS, it'd be a top pick. Much of Attio's "AI-native" 2026 feature set yourco already built independently: its **Web Research Agent ≈ Enrich**, **Ask Attio ≈ Melanie** (and Melanie cites sources, which Attio doesn't advertise), **AI Workflows ≈ Melanie's agentic write-commands**.

## Revisit trigger (when buy-vs-build flips)
Re-run the comparison when yourco has **a team that needs multi-user reporting, a mobile app, and mature email/calendar sync** — the things Attio does well out of the box that yourco would otherwise have to build and maintain. Native is right while solo + pre-scale; Attio's maturity matters more as headcount and client count grow. Trigger: first non-the Founder CRM user, or the native CRM becoming a maintenance drag.

## The forward signal worth noting
Attio put itself in the **ChatGPT store** and as an **MCP connection in Notion's agents** — i.e. *make your product usable by other AI agents.* Two implications for yourco: it validates Mario's mandate (be discoverable + citable by AI), and it foreshadows making yourco's *client employees* agent-accessible later. Attio's own "next generation of CRM" thesis is the same bet yourco makes (software becomes agent-operated) — yourco applies it as "digital employees," not "a smarter CRM."

## Borrow-ideas captured
Logged to `crm/_backlog.md`: (1) auto-log activities from the Gmail/Calendar connector (confirm-to-save) — closes the manual-activity gap; (2) AI Attributes — an auto-computed field (e.g. a one-line "why they're a fit" / company summary), fitting the existing derived-field pattern.

## Trip-wire
- **Review:** 2027-01-01
- **Overturn if:** the revisit trigger above fires — a first non-the Founder CRM user, or the native CRM becoming a maintenance drag (multi-user reporting, a mobile app, and mature email/calendar sync are what Attio gives out of the box).
- **Check:** `crmNonFounderUsers >= 1`
- **Check covers:** the "first non-the Founder user" half only, counted as active connectors + advisors — the people who read the CRM through the scoped console. "Maintenance drag" stays a human read.
