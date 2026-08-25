# 2026-06-16 — Online Revenue Leak Snapshot + per-vertical landing pages (Bella's self-serve front door)

## Decision (the Founder)
Build a **free, online "Revenue Leak Snapshot"** that lives on each **per-vertical landing page**. It is a short,
vertical-specific mini-diagnostic that **gates the findings behind contact info**, renders an
**yourco-branded snapshot report on screen**, and routes the prospect into the funnel:
1. **Easy, apparent navigation to the right vertical.** An Industries hub (`verticals.html`) + a
   config-driven landing page per vertical (`vertical-template.html?v=<slug>`) where *all* content —
   pain, bottlenecks, stats, audit questions — is specific to that trade.
2. **A "Quick" Audit on the landing page.** ~6 vertical-specific questions. The prospect must enter
   **name + email + business (phone optional)** to see the findings.
3. **An instant, professional, yourco-branded report** showing: their findings, the **dollar leak
   computed from their own inputs (math shown)**, **potential outcomes + ROI** if they implement an
   yourco AI OS/agents, and **a few hard-hitting, vertical-specific stat-facts**.
4. **On completion:** the findings are **Slacked + emailed to the Founder**, and the person is **entered into
   the CRM as a warm lead, source "online snapshot."**
5. **Not the full audit** — a sneak peek sized to make them want the discovery call. The full paid
   Audit (`processes/audit-sop.md`) goes deeper; the Revenue Leak Snapshot is the teaser/lead-gen front of it.

**Owner: Bella** (end to end — the online Revenue Leak Snapshot, its config, the report, the leads it creates),
consistent with Bella owning the full Audit.

## Why this is right
- **It's the top of the audit-first funnel** (`2026-06-16_audit-first-os-as-product.md`): a no-risk
  first touch that demonstrates the diagnosis *before* asking for anything, then hands up to the paid
  Audit → custom AI OS. The Revenue Leak Snapshot *is* the sales pitch, in miniature.
- **It converts the warm-network + intent + outbound traffic** into self-qualifying warm leads with
  contact info already captured — exactly the contact-info gate the CRM architecture wants
  (`2026-06-15_prospect-data-architecture.md`).
- **One yourco entity, many vertical pages** (`2026-06-16_brand-architecture-vs-vertical-llcs.md`):
  config-driven, so a new vertical is a config block, not a new build.

## What got built
- `agents/webb/pages/yourco-site-v2/snapshot-config.js` — the single source for per-vertical content
  (landing copy, bottlenecks, **stats with source slots**, the Quick-Audit questions, report outcomes,
  first-build rec). Beachhead verticals populated: **Landscaping, Hardscaping**.
- `agents/webb/pages/yourco-site-v2/vertical-template.html` — config-driven landing page, `?v=<slug>`,
  primary CTA = the Revenue Leak Snapshot.
- `agents/webb/pages/yourco-site-v2/snapshot.html` — the gated mini-diagnostic + on-screen branded
  report. ROI computed from the prospect's inputs.
- `agents/webb/pages/yourco-site-v2/verticals.html` — the Industries hub (navigation).
- `runtime/snapshot_intake.py` — staged handler: CRM warm-lead write (source "online snapshot",
  owner Bella) + Slack summary (`#yourco-bella`) + email summary (to the Founder). Dedupes via the
  promote.py conventions. `--self-check`.

## Guardrails (held)
- **No fabricated numbers.** The report's dollar figure is computed from the prospect's own inputs and
  the math is shown. The "hard-hitting stats" carry a **`src` slot**: **Sadie (the research agent)
  sources + cites each stat** (real publication + URL + year) and hands them to Bella, who curates
  them into `snapshot-config.js`. Until a stat is sourced its `src` reads `[verify]` and the report
  renders that source line, so an unverified stat is visible and never silently shipped. (Brand:
  `brand/writing-rules.md`; Bella's hard gate.) Sadie → Bella is the standing handoff for keeping the
  stats fresh and cited.
- **Recency rule (the Founder, 2026-06-16):** stats must be **published within the last ~12 months (2025-present)** —
  **no recycled decade-old studies** (the 2011 HBR speed-to-lead study, the ~2007 Lead Response Management
  Study, undated vendor-blog claims are out). For an AI-native company, dated citations undercut the brand.
  If a classic stat only exists in old form, Sadie finds a current report with fresh data on the same theme;
  she refreshes the set on a recurring cadence so nothing goes stale.
- **Staged until launch (launch-gate).** The report renders client-side (no send needed). The CRM
  write + Slack + email are staged: `/api/snapshot` has no backend until the site deploys; the
  Slack/Gmail delivery rides the existing **draft-only, approval-gated** runtime connectors. Nothing
  external sends until the gate clears.
- **No prices.** The Revenue Leak Snapshot and report carry zero pricing; the fee is Polo's (`pricing/v0/audit.md`).
- **Honest framing.** The report is labeled a *preliminary snapshot*; it explicitly points to the full
  audit as the real, deeper diagnosis.
- **No per-report the Founder approval (the Founder, 2026-06-16).** The online Revenue Leak Snapshot report is **templated** —
  the only variable claims are (a) the prospect's own-number math (shown) and (b) Sadie's pre-sourced,
  cited stats. So it **ships without the Founder approving each instance.** the Founder still owns the standing
  template/brand once; the per-prospect report auto-delivers. *(This is the online Revenue Leak Snapshot only —
  the bespoke full **Audit Report** (`clients/_yourco-template/audit-report/`) is a freeform per-client
  deliverable and keeps its the Founder-approval gate.)*

## Owners
**Bella** (the Revenue Leak Snapshot + report + leads; curates the stats) · **Sadie** (sources + cites the stats →
Bella) · **Webb** (the pages) · **David** (CRM write target) · **Polo** (pricing, untouched here).
the Founder owns the standing template/brand, not each report.

## Open / before launch
- **Sadie sources + cites every stat** in `snapshot-config.js` (replace each `[verify]` with a real
  publication + URL); **Bella** curates them in. No per-report sign-off needed once a stat is cited.
- Wire `/api/snapshot` to `runtime/snapshot_intake.py` when the site deploys (CRM write + the
  draft-only Slack/email).
- Verticals live: Landscaping, Hardscaping + the home-services / emergency-dispatch cluster (HVAC,
  Plumbing, Electrical, Roofing, Restoration, Garage Door, Tree Service, Septic & Well) — **10 total.**
  Non-home-services verticals (clinics, finance, hospitality, etc.) need a tailored question set +
  leak model (the current generic model = leads × miss-rate × close × job value fits appointment/
  dispatch trades) — a separate next phase.
