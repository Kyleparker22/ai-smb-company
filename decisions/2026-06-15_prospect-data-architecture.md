# 2026-06-15 — Prospect data architecture: cold lives in Instantly, warm graduates to the CRM

## Decision
Two systems, two jobs, one promotion gate between them.

- **Instantly = the cold/outbound system of record.** Every sourced cold prospect lives here, with the sequences and reply tracking. High volume, low value per record, replaceable (re-sourceable any time). The multi-source sourcing pipeline (`runtime/sourcing.py`) deposits its deduped output **into an Instantly campaign — not the CRM.**
- **The native CRM = the relationship system of record.** It holds only what's *real*: prospects that replied or showed positive intent, anything warm from the start (warm network, referrals, "see yours" inbound captures), live opportunities, and every client. Lower volume, high value, owned and git-backed.
- **The promotion gate:** a cold prospect graduates *into* the CRM the moment it replies / shows positive intent in Instantly. `runtime/promote.py` reads Instantly's warm replies and writes them into the CRM as real leads (company + contact w/ email + a `prospect`-stage deal, owner Reilly, marked "replied"). Cold records never touch the CRM until they earn their way in.

**The full flow:**
`source (Outscraper + Vibe + Instantly SuperSearch) → dedupe → Instantly campaign (cold) → reply / positive intent → promote → CRM (real lead) → discovery → close`

## Why
- **Don't bloat the owned CRM.** Thousands of cold leads in a git-backed JSON is noise. The CRM's high-value features — Hot List, win-prob, forecast, the map, deal velocity — are *for* real opportunities; they get sharper when cold lists aren't diluting them, not weaker.
- **Each tool does its job.** Instantly is purpose-built to hold large cold lists, sequence them, and track replies. The CRM is built to track relationships and pipeline. Forcing one database to do both degrades both.
- **Ownership where it counts.** We own the relationships (clients, deals, warm leads) in git. A replaceable cold list living in a vendor is a fine trade — re-sourcing a cold list is cheap; losing a client relationship isn't. This is consistent with the build-vs-buy stance (`2026-06-14_crm-build-vs-buy-attio.md`): own the OS, rent the commodity.
- **Matches reality.** The current CRM contents are warm-network and a real engagement (Sample Client) — none were ever cold. They belong in the CRM; cold lists never did.

## What changed in the build
- `runtime/sourcing.py` — retargeted: dedupe → **stage into an Instantly campaign** (`--campaign`), staging only, never sends. The old CRM-write path is retired for cold sourcing.
- `runtime/instantly.py` — added `warm_replies()`: reads leads with a positive interest/reply status from a campaign, normalized for promotion.
- `runtime/promote.py` (new) — reads `warm_replies()` and promotes each into the CRM (dry-run by default; `--commit` writes). The reply→CRM gate.

## Nuance worth holding
- **Contact-info gate (the Founder, 2026-06-15): a signal with no contact info does NOT enter the CRM — or any campaign.** A YouTube/Bluesky/forum commenter is a *person + their words*, not a contactable lead. The CRM stays clean: a signal becomes a CRM record **only once we have a real way to reach them** — i.e. either (a) Sadie's approved reply elicits their email/phone/DM, or (b) it carries contact info already (a Yelp business with a phone), or (c) enrichment resolves an email. No contact → it lives as a *signal* in the intent board / engagement queue, not the CRM. This prevents the CRM filling with un-actionable names.
- **Intent ≠ warm. Sadie's leads are still cold.** Sadie (intent/social-listening) is another **cold source** — she surfaces people/companies showing a buying signal (asking about the problem, or hiring their way out of it). Reaching out is still cold (no prior contact), so her surfaced leads land in **their own intent-themed Instantly campaign** (Michelle writes intent-aware copy), NOT the CRM, and promote on reply like any cold lead. Intent improves targeting + conversion, not lead temperature. *(The one exception: a helpful reply in the very thread where someone publicly asked — that's on-platform engagement, not a cold campaign.)*
- **Instantly is email-first.** Cold records without an email (raw Outscraper = phone + address, no site) can't be sequenced by Instantly until enriched. They are SMS/call-channel leads (per the SMS decision, landscaping is SMS-approved) or need Enrich first. `sourcing.py` stages the email-bearing records into Instantly and reports the no-email count separately — it never invents an email.
- This **amends** `2026-06-07_crm-architecture.md` (the CRM is no longer the sourced-lead destination) and refines `2026-06-07_multi-source-sourcing.md` (merge target = Instantly, not CRM).

## Revisit trigger
If Instantly is ever churned, export the cold list first (it's the only thing that lives solely there). If a second cold channel needs a different sequencer, the promotion gate stays the same — only the source-of-cold changes.
