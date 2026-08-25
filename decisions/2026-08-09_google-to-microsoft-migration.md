# 2026-08-09 — Migrate the whole stack from Google to Microsoft 365

## Decision
yourco moves its entire workspace stack from Google to **Microsoft 365**: Gmail → **Outlook/Exchange**,
Google Drive → **OneDrive/SharePoint**, Google Docs/Sheets → **Word/Excel**, Google Calendar →
**Outlook Calendar**. the Founder's call, 2026-08-09. Upgrades the 2026-07-24 intent noted in
`processes/launch-runbook.md` from "post-launch someday" to a decided migration.

## Why
1. **Most SMB clients live on Microsoft 365.** Running the same tenant model yourco's clients run is
   dogfooding that pays — every integration lesson learned on yourco's own tenant transfers directly.
2. **MS Graph is already the planned stack for Conduit** (`offerings/conduit/SPEC.md`), so the runtime
   ends up on Graph either way. One API surface instead of two.
3. **Client credibility.** An yourco that operates inside the same Microsoft estate its clients use is
   a shorter conversation than one asking them to accept Google-shaped assumptions.

## ⚠️ Timing constraint — this is the part that can actually hurt
**Do not move MX records during the launch window or the first live-client ramp.** The sending domain
has been warming since June (`getteamyourco.com`, warmup tracked in Instantly). Changing mail routing
mid-warmup destroys deliverability and restarts a 4–6 week clock. The 2026-07-24 note already carried
this rule and it stands.

**Safe sequence:**
1. **Now (safe, zero risk):** stand up the M365 tenant, buy the seat, verify the domain, configure DNS
   *records only* — no MX cutover. Migrate **files first** (Drive → OneDrive/SharePoint): no
   deliverability exposure at all.
2. **Then:** move Calendar (low risk — no mail routing).
3. **Last, and only outside a ramp:** MX cutover for `yourco.com`. Mail is the risky one.
4. **Never** cut over while cold outbound is mid-sequence.

## What has to be rewired (the real scope — this is not just email)
| Surface | Today | After |
|---|---|---|
| Runtime connector | **Gmail MCP** (read + draft; send/delete DENIED by the approval gate) | **MS Graph** — *the draft-only approval gate must be preserved identically*; this is a moat behavior, not a config detail |
| Jim's inbox triage · `loops/inbox-triage/` | Gmail | Graph |
| Calendar connector (Jim's holds) | Google Calendar | Outlook Calendar |
| `runtime/site_intake.py`, `snapshot_intake.py` notifications | Gmail | Graph / SMTP |
| Bella's `contact@yourco.example.com` send flow | Workspace | Exchange |
| Agent aliases (currently riding one Workspace seat) | Workspace aliases | M365 aliases / shared mailboxes — **check per-seat cost**, this is where M365 gets expensive |
| **Connector email + Slack** (`connector-onboarding.md` §8a — every connector gets `contact@yourco.example.com`) | Workspace seats | M365 seats — **cost multiplies per connector; model it before committing** |
| Granola / Drive read-context | Drive | OneDrive/SharePoint |
| DNS/MX for `yourco.com` | Google | Microsoft — **last step** |

## Cost note (do this math before buying)
Google Workspace Business Starter is currently **$8.73/mo for one seat**. M365 Business Standard is
~$12.50/seat/mo. With the connector-email decision (every connector gets a mailbox), seat count is the
variable that matters — 10 connectors is ~$125/mo, not ~$12. **Charles models it before the purchase.**
Against $0 cash and ~$614/mo burn, this migration should not add net cost in the same month it happens.

## Options considered
Stay on Google (rejected — the Conduit/Graph work happens anyway, and the client-estate argument is
real) · hybrid, mail on Google + files on Microsoft (rejected — two identity systems is the worst of
both) · defer until post-launch (this decision supersedes that, but the **MX timing rule survives**).

## Reversibility
Files and calendar: high (re-migratable). **Mail: low** — once MX moves and warmup restarts, going back
costs another deliverability cycle. Which is exactly why mail moves last and never mid-ramp.

## Owner
**Kemba** (infra — DNS, tenant, MX) · **the Founder** (purchase, the actual cutover, since it needs credentials)
· **Charles** (seat-cost model before purchase) · Jim/Bella loops re-pointed at Graph after cutover.

## Trip-wire
Review when: (a) the launch gate clears and a ramp is scheduled — confirm mail cutover is NOT inside it;
or (b) connector count exceeds 5, at which point seat cost needs re-modelling; or (c) 2026-11-01,
whichever comes first.
