# Decision — dial the (staged) website way back to a lean, proof-led core

**Date:** 2026-06-22 · **Owners:** the Founder + Webb · **Status:** done (this pass) — verticals decision deferred

## Why
The staged site had **34 pages + a 50+ vertical funnel** for a **pre-revenue company with zero case studies.** Per the council/pre-mortem (`loops/advisor/2026-06-22_council-premortem.md`), this is the clearest evidence of building substituting for selling — and a sprawling, thin, proof-less site reads as a Potemkin village to a sharp buyer. Pre-revenue, the site has exactly **two jobs**: (1) **legitimacy** when a warm prospect Googles you after a conversation, and (2) **convert to a conversation.** Everything beyond that is surface that competes for founder attention and dilutes the story.

**"Dial back" ≠ delete.** Parked pages moved to `agents/webb/pages/yourco-site-v2/_parked/` — fully reversible (`git mv` back). Nothing lost.

## What changed (this pass)
- **Parked 11 pages** → `_parked/`:
  - **Ready-to-Hire catalog (the Founder: park it, lead with one motion):** `hire.html`, `hire-onboarding.html`, `employees.html`, `build-your-employee.html`, `roi-calculator.html`, `quiz.html`. (`hire-config.js` **kept** — locked prices preserved per the decision; revive after first signed logo.)
  - **Redundant diagnostics (keep one):** `missed-money-meter.html`, `leak-index.html` — the **Revenue Leak Snapshot (`snapshot.html`) is the single free diagnostic.** (Leak Index needs audit-volume data we don't have yet — Brett rated it "Later" anyway.)
  - **Roster-as-theater risk:** `team.html`, `org-chart.html` — a "meet our 22 AI employees" page when most are personas can read as inflated; park until the roster is real/proven.
  - **No clients to refer yet:** `refer.html`.
- **Link integrity:** every link in the 23 live pages that pointed to a parked page was **retargeted** to the nearest kept page (catalog→`audit.html`, diagnostics→`snapshot.html`, team/org-chart→`glass-box.html`). Verified **zero dead links**. (No markup deleted — safest path on a staged site whose nav gets rebuilt at launch.)
- **Home nav trimmed** to the lean set: Home · How it works · Industries · The glass box · The audit · Pricing · *Start the audit*.

## The intended lean site (~7–8 featured pages)
`index` (pitch + book CTA) · `audit` (the paid offer / front door) · `glass-box` (the one real pre-customer proof — "we run our own company on AI") · `instant-employee` ("see yours" demo hook) · `snapshot` (one free diagnostic) · `positioning`/`about` (who/what — merge to one) · `pricing` · `privacy` + `sms-terms` (compliance).

## Still live but NOT featured — "fold at launch" (left in place, not parked)
`compare`, `objections`, `manifesto`, `day-in-the-life`, `timeline-48h`, `reliability`, `eval-gated-seal`, `try-to-break-it`, `demos`, `demos-tier2`, `about`, `audit-intake`. These have real content; the launch nav rebuild should **consolidate** the trust cluster into `glass-box` and the "why-us" cluster into one page, rather than carry them all. Editorial work — deferred (don't gold-plate a staged site).

## Deferred (the Founder's call, pending)
- **Vertical landing pages** (`verticals.html` hub + `vertical-template.html` + 50+ in `snapshot-config.js`): **untouched** this pass. "Industries" stays in nav. Options on the table: beachhead-only (Landscaping + Hardscaping) vs. park-all vs. keep-all. Revisit.

## Known cosmetic debt (fix at launch, not now)
Retargeting fixed *links* but not *labels/copy* — some body CTAs that said "hire an employee" now point at `audit.html`. The nav is bespoke per page (no shared include — itself a sprawl symptom). At launch, Webb rebuilds a **single shared nav** for the lean set; that pass cleans the retargeted-label copy. Tracked here so it isn't lost.

## Revive triggers
- Catalog (`_parked/hire*`): after the first signed/live/retained logo proves the operated model — then re-feature the subscribe-and-go motion.
- Diagnostics/Leak Index: when there's audit volume to populate the benchmark.
- Team/org-chart: when the roster is genuinely built (autonomous systems, not personas).

## Status
Done 2026-06-22. Staged like everything external (launch-gate). 34 live pages → 23; featured set ~8. Verticals deferred.

## Trip-wire
- **Review:** 2026-10-01
- **Overturn if:** a parked surface earns its way back — the vertical funnel returns if cold outbound (not referral) becomes the lead source that needs it, and the roster/catalog pages return once the roster is real and proven rather than largely personas.
- **Check:** _none — lead source isn't yet instrumented per-channel in the CRM, so "which channel is producing" can't be read off a number._
