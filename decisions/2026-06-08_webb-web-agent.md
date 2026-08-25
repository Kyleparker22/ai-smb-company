# Decision: Webb — YourCo's Web Agent (Site Operations / Custodian)

**Date:** 2026-06-08
**Owner:** the Founder, advised by Claude
**Status:** Locked — Webb scaffolded as a new digital employee

## What was decided
Add **Webb** to the YourCo agent roster as the **Web Operations / Site Custodian** digital employee. Webb owns all of YourCo's web surfaces (`yourco.com`, `getteamyourco.com`, future subdomains and landing pages) and maintains them as living brand infrastructure.

## Why this gap surfaced now
Task #44 in the readiness checklist was assigned to Luka: "Luka drafts brand-aligned landing page for getteamyourco.com." But Luka is the **brand custodian** — she reviews; she doesn't author. Reed produces videos, Katie writes editorial, Reilly drafts cold copy, Pickle (when built) makes static collateral. **No one owned the website.**

The website is structural infrastructure — it grows with every new vertical Polo locks, every video Reed ships, every campaign Reilly runs, every editorial post Katie writes. Without an owner, it would either get neglected or become an ad-hoc burden on the Founder.

## Webb's scope

**Owns:**
- `yourco.com` + `getteamyourco.com` + future subdomains
- All marketing/landing pages
- Site SEO + analytics (Plausible or PostHog)
- Uptime monitoring (UptimeRobot)
- Calendly booking flow integration
- Per-vertical landing pages (triggered by Polo's pricing locks)
- Publishing Katie's editorial content
- Embedding Reed's videos
- DNS and hosting maintenance
- Weekly readouts on site traffic, conversions, brand audit findings

**Does NOT own:**
- Brand guidelines (Luka's)
- Editorial content writing (Katie's)
- Video production (Reed's)
- Pricing logic (Polo's)
- Sales copy (Reilly's)
- Static collateral / decks (Pickle's when built)

## Tool stack (v0, locked)
- **Site builder + hosting:** Canva Sites (uses existing Canva Pro + brand kit `kAHMCKMxZN4`) — pending the Founder confirmation
- **Domain / DNS:** Cloudflare (or Instantly DNS) — free
- **Booking:** Calendly free tier (or $8/mo)
- **Analytics:** Plausible ($9/mo) or PostHog (free)
- **Uptime:** UptimeRobot (free)
- **Monthly recurring:** $0–$9/mo

v1 upgrade path: Framer ($15/mo) or Webflow ($14/mo) when site complexity outgrows Canva Sites (~ when 3+ pages).

## Approval gates
- **Draft / stage page (un-published)** → full autonomy
- **Publish any page** → **human-must-approve** (the core gate)
- **Change DNS records (production)** → must-approve
- **Change hosting provider** → must-approve
- **Add tracking scripts / pixels** → in-loop (privacy implications)
- **Any spend > $1** → in-loop
- **Brand voice on every page** → Luka in-loop

## Cross-agent dependencies
- **Luka** reviews every page for brand voice + visual conformance (hard gate)
- **Katie** writes editorial; Webb publishes
- **Reed** produces videos; Webb embeds and hosts the landing pages
- **Polo** locks per-vertical pricing; Webb builds the vertical page
- **Pickle** (when built) provides static collateral that links from the site
- **Reilly** signs off on copy that supports cold-campaign conversion
- **Atlas** reads Webb's analytics rollup for the Monday briefing

## Naming
"Webb" — literal, evokes the surface. Fits YourCo's naming convention (Atlas, Reilly, Reed, Luka, Polo, Charles, Brett, Katie — all real names that fit the role).

## Approval
the Founder approved in chat 2026-06-08: "yes scaffold Webb."

## Files touched
- `/agents/webb/_README.md` — engagement metadata
- `/agents/webb/01_discovery.md` — first use case, outcome, systems, success criteria, approval pattern
- `/agents/webb/02_build.md` — tool stack, publish pipeline, build status, hard launch gates
- `/agents/webb/03_eval.md` — eval set, gates, watchdogs, pre-go-live checklist
- `/04_agent_roster.md` — added Webb to the live/in-build table + org chart + capability boundaries
- `/CLAUDE.md` — internal platform list updated with Webb
- `/decisions/2026-06-08_webb-web-agent.md` — this file
- Memory — Webb captured for future-session continuity
- Task list — task #44 reassigned from Luka to Webb; tasks #42 and #43 updated to include Webb's mailbox + Slack bot; new tasks #69-71 added for v0 readiness (Canva Sites confirmation, DNS, analytics)

## Revisit conditions
- After 3+ pages live: extract Webb's publish pipeline pattern to `yourco-template` (when Kemba is built)
- If site complexity outgrows Canva Sites: migrate to Framer/Webflow; log as separate decision
- If brand drift becomes a recurring issue: tighten the brand gate process between Webb and Luka
- If Webb's recurring spend exceeds $50/mo: re-evaluate tool stack consolidation
