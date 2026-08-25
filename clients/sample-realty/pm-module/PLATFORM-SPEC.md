# Sample Realty Property Management Platform — build spec (v0)

> Status: pre-engagement spec, 2026-08-04. They run PM on two hand-kept Excel workbooks —
> no software at all. The accounting engine (journal → ledgers → trial balance → owner
> statements) already exists in this folder and was validated on their real data.
> Companion demo: `console/index.html` (the Kimi cockpit, seeded from the real journal).

## The honest buy-vs-build call

Commercial PM suites (Buildium, DoorLoop, AppFolio, TenantCloud) exist and are good at
tenant portals + online rent payment + screening. At Sample Realty's scale (~8 managed
doors + their own rentals) they are simultaneously **overkill and underwhelming**: $60–200/mo,
weeks of setup, and Kimi still does the work — the software is a filing cabinet, not an
employee. Nothing off-the-shelf gives her the thing that actually hurts: the NCREC trust
accounting she does by hand, operated for her.

**The call: build the operated OS thin, buy the two commodity edges when needed.**
- BUILD (yourco operates): trust accounting engine ✅ · rent roll + rent watchdog ·
  maintenance intake→ticket→ledger flow · owner statements ✅ + owner console ·
  compliance calendar · the Kimi console.
- BUY when the need appears: tenant screening (TransUnion SmartMove, per-applicant fee,
  no subscription) · online rent payment IF tenants outgrow Zelle (she collects fine today).
- The moat holds: the value is the operated loop + approval gate + trust-account
  reliability, not portal chrome.

## The 8 components (maps to the 8-pillar OS taxonomy)

1. **Books** (Back Office) — DONE in v0: journal-driven ledgers, trial balance, owner
   statements. Next: monthly loop on the runtime + bank-feed ingestion (statement CSV
   first, Plaid read-only later).
2. **Rent roll & lease registry** (Company Brain) — the missing single source: property,
   owner, tenant, rent, due day, lease start/end, SD amount + where held (acct 4808),
   fee %. Seeded from the journal; lease dates need one sit-down with Kimi.
3. **Rent watchdog** (Operations) — expected vs received per month; on the 6th, unpaid →
   flag + drafted reminder text for Kimi's approval; late fees computed per lease.
4. **Maintenance flow** (Intake/Operations) — tenant text/email → ticket draft → Kimi
   approves dispatch → vendor → cost posts to the property ledger and the owner statement
   automatically. (Today: maintenance lives as journal one-liners.)
5. **Owner service** (Customer) — monthly statement auto-drafted (exists) + a white-label
   owner console page per landlord (yourco client-console pattern), annual 1099 totals.
6. **Leasing** (Marketing/Sales) — vacancies flow to the site's For Lease section
   automatically (listings-data.js already does this for Donovan); screening via
   SmartMove; lease renewal radar 90/60/30 days out.
7. **Compliance calendar** (Back Office) — NCREC monthly trust reconciliation, SD 30-day
   itemization clock on move-outs, lease expirations, 1099 season.
8. **The Kimi console** — one screen: rent board, flags, tickets, owner balances,
   compliance due-dates. Demo at `console/index.html`.

## Stack (yourco standard, no new vendors for v1)

Runtime VPS loops (rent watchdog daily in season; books weekly; statements monthly) ·
SQLite/JSON registry in the client repo · the existing packet builder as the books engine ·
white-label HTML consoles (client-console pattern) · Slack/#yourco channel + email drafts
via the approval gate. No voice. Money movement: never — drafts only, Kimi executes.

## Phases

- **P1 (done today):** books engine + owner statements + findings packet.
- **P2 (first paid month):** rent roll registry (sit-down to confirm leases) · statement-CSV
  bank ingestion · rent watchdog + drafted reminders · Kimi console live on the runtime.
- **P3:** maintenance intake (dedicated email/SMS) · owner consoles · compliance calendar
  automated · site vacancy sync.
- **P4 (as earned):** Plaid read-only feed · SmartMove screening · autonomy promotions per
  the streak rule (e.g., reminder texts earn full autonomy after N clean approvals).

## Gates & guardrails

- Trust-account data isolated to this engagement; PII never leaves the repo/runtime.
- Read-and-draft only, forever, on money. Kimi approves every outbound text/statement at R1
  until the autonomy matrix promotes specific actions on evidence.
- Ray/counsel pass on NCREC record-keeping fit + tenant-comms rules before anything live.
- Pricing: Polo scopes — this is a module of the Sample Realty OS, not a per-door SaaS.

## Known data gaps (ask Kimi at the sit-down)

Lease start/end dates + due days + late-fee terms per unit · current status of 15721 Capps
(no rent since the March 19 pro-rate — moved out?) and 1138 Doveridge (silent since Feb) ·
Barossa Valley's irregular amounts (1,490–1,800) · which bank holds the trust account (feed
path) · SD ledger detail for acct 4808 · SC-side doors (the SC misc fund tab implies some).
