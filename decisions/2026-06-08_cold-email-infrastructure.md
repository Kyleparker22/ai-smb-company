# 2026-06-08 — Cold-email infrastructure: getteamyourco.com via Instantly done-for-you

## Decision
Reilly's cold-email sending domain is **`getteamyourco.com`**, provisioned through Instantly's done-for-you flow on the Hyper CRM tier ($97/mo). Two mailboxes (`the Founder@getteamyourco.com`, `the Founder.parker@getteamyourco.com`) running on Google Workspace, both forwarding to `yourco.com` so prospects who investigate land at the real brand site. Total marginal cost: ~$11/mo for mailboxes and domain (on top of the Hyper CRM tier).

## Context
The original 10DLC runbook planned for `mail.yourco.com` as the sending subdomain with manual DNS work by the Founder. When walking through Instantly's setup tonight, three options appeared: pre-warmed accounts (kills brand — random Instantly-owned domains), done-for-you setup (Instantly registers and manages a new domain), and connect existing accounts (requires Workspace subdomain setup first). The done-for-you path won on a combination of brand isolation, zero registrar friction, and cleaner reputation separation.

## Why this won over `mail.yourco.com`
- **Reputation isolation.** A separate domain (`getteamyourco.com`) means cold-email spam reports can't damage `yourco.com`'s primary-domain reputation, where the Founder's real inbound mailbox `founder@yourco.example.com` lives. Subdomain isolation was theoretically possible but reputation can still spill back to the root in practice.
- **Zero DNS friction tonight.** Instantly handles registration, DNS, Workspace provisioning, and warmup configuration. No need to identify the registrar, manage TXT records, or chase DKIM keys manually.
- **Forwarding preserves brand legitimacy.** `getteamyourco.com` redirects to `yourco.com` for any prospect who pastes the domain into their browser — instant credibility recovery.
- **Industry-standard naming pattern.** "get + brand" is a recognizable B2B SaaS convention (recipients don't read it as suspicious).

## Why not the other paths
- **Pre-warmed accounts (Instantly-owned domains)** — rejected. Recipients would see random domains in the From field. Direct contradiction of YourCo's executive-trust positioning.
- **`mail.yourco.com` subdomain via connect-existing** — rejected. Requires Google Workspace subdomain setup as a 60-minute prerequisite. Subdomain reputation can still spill back to root.
- **Pure manual DNS at registrar** — rejected. More fragile, more places to typo, no upside.

## What got built tonight
- Domain registered: `getteamyourco.com` ($15/year domain registration)
- Two mailboxes on Google Workspace via Instantly:
  - `the Founder@getteamyourco.com` — primary cold-outreach sender
  - `the Founder.parker@getteamyourco.com` — secondary sender (firstname.lastname format, the industry-standard cold-email format)
- Forwarding: `getteamyourco.com` → `yourco.com` (for any prospect investigating the From-address domain)
- Automated warmup: enabled, runs 30 days through Instantly's network before any cold sends
- Monthly cost: ~$11/mo ($10 for 2 mailboxes + $1.25 amortized domain) on top of Hyper CRM tier

## What this changes in the OS
- 10DLC runbook (`/processes/10dlc-sending-infra-setup.md`): Phase 2 (domain + DNS + warmup) now effectively complete via the Instantly done-for-you flow. The manual registrar steps in the runbook are obsolete for the email side.
- Reilly's `02_build.md` (`/agents/reilly/`): cold-email domain reference updates from `mail.yourco.com` to `getteamyourco.com`.
- Memory: cold-email infra status updates from "pending" to "in progress (warmup running ~30 days)".

## What's still open
- **10DLC SMS brand registration** — separate from email infra. The brand registers YourCo LLC the legal entity with carriers; the phone number is allocated by Instantly. No coupling to `getteamyourco.com`. Submit in Instantly's SMS / Calling section using the data in `/finance/legal-docs/business-info.docx`. 1–7 day brand approval; 1–2 week campaign approval.
- **FTSA attorney engagement** — independent of email. Email 2–3 Florida TCPA attorneys this week per the runbook template.
- **Warmup completion** — automatic, ~30 days. No action required from the Founder during this window. First cold send possible after 2026-07-08.
- **First campaign content** — Reilly's first cold sequence drafts (copy + cadence). Can be drafted during the warmup window so it's ready to fire when warmup completes.

## Reversibility
- Easy. Drop the domain and mailboxes anytime ($11/mo recurring; the $15/year domain registration is the only sunk cost).
- Switching cold-email tools later would require disconnecting Instantly's Google Workspace setup but the domain itself is portable.

## Cost summary
| Line | Amount |
|---|---|
| Instantly Hyper CRM tier | $97/mo |
| 2 cold-outreach mailboxes (`the Founder@`, `the Founder.parker@`) | $10/mo |
| `getteamyourco.com` domain | $15/year (~$1.25/mo) |
| **Total monthly cost for cold-email infra** | **~$108/mo all-in** |
