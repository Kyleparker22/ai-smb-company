# Meeting — Design & sales process workflow (HubSpot, Aspire, AI quoting platform)

**Date:** 2026-08-06 · **In person** at Sample Client
**Present:** the Founder (yourco) · the Client Owner · Colton (design/estimating) · Noah ("No", operations — approves labor/means-and-methods) · walk-in: Tim Mays (neighbor, prospect-grade — 200 acres off Mace Rd, 13919 Old Space Vermilion Dr; Client Owner: "could've had something mocked up and sold within two days")
**Source:** full transcript in the Founder's session 2026-08-07; this file is the working digest.

## Headline
The engagement has pivoted live onto **Phase 1 of the OS proposal — the Same-Day Design Studio / instant-quote platform**. Client Owner, Colton, and Noah spent the whole meeting co-designing it, volunteered their data, and asked "how long to build?" **the Founder committed: something ready by next week, then a ~2-week test phase, plus a 30–60 min walkthrough call next week.** The original Installation Proposal Automation use case was not discussed. Still $0 committed — Client Owner asked about pricing; the Founder deferred ("let me get it built out and make sure it's useful first"). Client Owner explicitly OK with a monthly fee for hosting/maintenance on yourco infrastructure.

## Their current process (as described)
- **Lead flow:** lead (web/phone) → Charlene routes → pipelines in HubSpot (installs = Client Owner, maintenance = Pack, fencing = Corey, designs = Client Owner). Stages: consultation scheduled → ballpark/design proposal → proposal estimating → contract sent → follow-ups → won/lost/revisit.
- **Ballpark path:** if priceable straight-up, Client Owner gets square footages → Colton enters in Aspire → team reviews → send. Ballpark email used to weed out non-buyers.
- **Design path:** design contract at **$100/hr**, ranges (6–10 / 8–12 / 10–15 hrs), **half upfront, credited if they install**. Lead time ~2 wks to start + ~2 wks to first copy = **4 wks to first design ("we say 4–6 weeks")**, revisions days-to-weeks, then **~2 more weeks to price** (waiting on sub quotes: mason, concrete, plumber/gas, deck carpenter). Sub pricing per-project is the pricing delay.
- **Time & materials on ~99.9%** of work — resists flat $/sqft. Cost drivers: access (36" gap vs skid steer), utility lines (hand-dig), grade, material logistics. Aspire has a difficulty-% buffer field.
- **Considering:** free design if client installs with them; 72-hour quote validity to force decisions (the Founder's anecdote landed); Corey already sells fencing on-site same-visit and "that has proven wonders."

## Their stack (verified in-meeting)
- **Aspire** — the core: pricing DB, labor markups, job dashboards (est vs actual by line item, updated as Charlene inputs labor weekly → moving to daily by install leaders), POs/expenses allocation by Charlene. Keeping it. "Competitors at $10–20M are obsessed with this software."
- **HubSpot** — pipelines, comms tracking, tasks, calendar, reporting (Aspire is bad at reporting/comms). Aspire→HubSpot sync being built by a third party ("he's building a connection"). Keeping both; the Founder advised don't replace what works, just make them talk.
- **SiteOne** — supplier account w/ login, **direct real-time pricing**; generally their most expensive supplier (good conservative quote basis). Aspire's SiteOne integration is sometimes wrong.
- **Moasure** ("Mosher") — on-site measurement incl. grade. Their ground-truth tool.
- **Polaris** (Mecklenburg Co. GIS) — parcels, topo, aerial, measuring tool; **no API found**. **VIP3D** — their design software, pulls GIS (property lines, setbacks, terrain) somehow; used for putting greens etc.
- **Nurseries** — Shepherd's, Kirk Davis + others; logins are CAPTCHA-walled, **but wholesalers will email weekly availability reports** ("week 32 availability report") — email ingestion is the sanctioned path.

## What they asked the platform to do (the co-designed spec)
1. **Accurate, scaled 2D drawing is the #1 deliverable** — Colton's words: render is the "sick picture" the client loves; the 2D that Colton can critique/adjust and take off from is what cuts "hours and hours of revisions." Current takeoff test: pergola rendered 12×16 vs actual 14×21; a 30 ft mark was actually 37'4" — **AI-invented dimensions are the failure mode; measurements must be ground truth** (Moasure export, uploaded site plan/survey, GIS assist). the Founder's own close: measurement + grade accuracy "is what's going to key."
2. **On-site flow:** crew/rep photos + Moasure measurements + client-supplied site plan/survey (**Charlene will request plan/survey at intake for every install call**) → design render on the real yard → talk-to-the-AI edits ("add a pergola here") → ballpark on-site → Colton dials pricing in Aspire → quote in 2–3 days instead of 6–8 weeks.
3. **Material/supplier catalog repository** (Client Owner offered to compile a master list): SiteOne pricing feed; natural stone sourcing regions (PA bluestone, TN veneer, ST); paver lines Techo-Bloc/Belgard/(Eagle?)—with **stock rules** ("Blu 60 always in stock all colors; Borealis always special order") so the AI designs in-stock-first; 10% blanket material waste.
4. **Labor benchmarks calculator:** e.g. 500 sqft pavers/day, herringbone takes more, install rates ("40–45/sqft range" mentioned), access-difficulty multiplier (their 1–10 idea), utility hand-dig buffer.
5. **Historical training data:** this year's Aspire quotes (won/lost/margin) — they floated ~500 total projects, agreed current-year subset.
6. **Scopes/descriptions in their voice** — their scope writing is intense; train it to best practice, they edit lines out. Not "Claude's voice."
7. **Style presets** for renders (craftsman/modern/rustic). Render already impressed by handling grade (auto-added small retainer).
8. **Plants:** availability via emailed nursery reports; plant selection stays human (Noah + Colton) except basics; clients only ever know hydrangeas/azaleas.
9. **Approval gates:** Noah must approve labor + means-and-methods (e.g. sleeves under hardscape) — today he walks jobs >$50–75k. the Founder framed watchdog/human-checkpoint model; landed well.
10. **Scope envelope they set:** ≤$60k jobs ≈ 80% coverable now; up to ~$100–140k with Colton confirming; mega-custom ($500k baseball-field build) out of scope. Cookie-cutter new-development patios = "knock that out seriously."
11. Pocket voice recorder / transcript upload for consult capture (the Founder floated; mild interest).

## Commitments made
- **the Founder:** v1 with these additions "ready by next week" (~wk of 2026-08-10) → 2-wk test → walkthrough call next week. Runs on yourco infrastructure; yourco owns maintenance; monthly fee acknowledged by Client Owner. ⚠️ the Founder also said "I'm going to hook it up either way" — pricing still unresolved.
- **Client Owner/team:** compile supplier/material master list + availability-report sources; can provide Aspire + HubSpot logins; Charlene to start collecting site plans/surveys at intake; get wholesalers emailing availability reports.

## Open items
- [ ] Data-request checklist to Client Owner (the Founder sends): current-year Aspire quote export, SiteOne access, Moasure sample exports, 2–3 priced designs w/ 2D (e.g. Hidden Cove $140k, Buffy $92k), labor benchmarks, Techo-Bloc stock rules, supplier/nursery master list
- [ ] v1 build triage + what "ready by next week" means (spec the demo, not the promise)
- [ ] Pricing conversation — convert to signed Phase 1 / $1,000-mo start before the free-build ratchet sets in
- [ ] Walkthrough call scheduled (30–60 min, wk of 08-10)
- [ ] CRM: log activity on Sample Client deal (still Proposal stage); Tim Mays = prospect-grade signal (Client Owner adjacent, wants project mocked up)
- [ ] Update 06_os-module-roadmap.md / prototype README to reflect Design-Studio-first reality
