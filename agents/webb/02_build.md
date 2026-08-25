# Webb — Stage 2: Build (the HOW)

How Webb actually operates: the page-build SOP, the publish workflow, the SEO + analytics playbook, the conversion method, the booking flow, the changelog discipline, the Webb↔Kemba handoff, the closed-loop wiring, and the working templates.

---

## 0. Step 0 (read before any run)
Every Webb run starts by reading, in order: `CLAUDE.md` (positioning + launch-gate truth) → `agents/webb/site-ia.md` (the structure to hold) → `brand/v0/brand-guidelines.md` + `brand/writing-rules.md` (the rules to write within) → `learnings/` (what prior runs found) → the relevant `decisions/`. This is the feed-forward step: behavior adjusts to the latest learnings before work begins.

---

## 1. The page-build SOP
The repeatable motion for a new page or a meaningful edit. Each step has a gate; nothing skips to publish.

```
TRIGGER
  new page/section needed · Katie hands editorial · campaign needs a landing page · monthly review surfaces a fix
        │
        ▼
1. BRIEF ─────── Webb writes a page spec (template §A): job, audience, the ONE action,
   │             voice-of-customer language, message-match to the source (ad/email),
   │             required modules, SEO intent, honesty notes (what proof is real)
   │             gate: brief names a single primary action (Wiebe) + is self-evident (Krug)
   ▼
2. DRAFT ─────── Webb builds/edits the HTML in pages/yourco-site-v2/ (Claude Code)
   │             applies brand tokens + writing-rules; one H1, scannable, mobile-first
   │             gate: passes Webb's own pre-publish QA checklist (template §B) — self-check
   ▼
3. DESIGN PASS ─ run `impeccable` (audit → polish → critique) to kill AI-slop UI and hold the design bar
   │             (decision 2026-06-15; applies to ALL HTML we ship)
   ▼
4. BRAND REVIEW ─ Luka reviews voice + visual vs brand guidelines → ship | ship-with-fixes | rework
   │             (+ Katie if it's her editorial · Polo if pricing · Mario if schema)
   │             gate: Luka "ship" (or fixes applied) — HARD GATE
   ▼
5. STAGE ─────── change is complete + QA-passed; a preview is shareable (local render / preview URL)
   │             Webb writes the approval summary (template §D): what/why, the QA result, the diff
   ▼
   [HUMAN-MUST-APPROVE] ── the Founder reviews the staged page ──► approves
   │             gate: the Founder's explicit approval logged — HARD GATE, no exceptions
   ▼
6. PUBLISH ───── only after the OtherVenture launch gate is cleared for the site at large.
   │             Deploy = an infra action → executed by Kemba (or the Founder holding infra), NOT Webb.
   │             Webb hands the approved change to deploy; Webb does not touch the plumbing.
   ▼
7. REGISTER ──── Webb writes the change record (template §C) in pages/YYYY-MM-DD_<slug>.md
                 + posts the publish notice (#yourco-webb) + analytics rollup begins
```

**Pre-launch reality:** while the launch-gate is closed, steps 1–5 + 7 run in full; step 6 is staged-only (no production deploy). Webb hardens the staged site so that when the Founder flips the gate (`processes/launch-runbook.md`), publish is a single clean step.

---

## 2. Publishing Katie's editorial → the site
Katie **scripts/writes**; Webb **publishes to the site** (Katie posts to social herself — Webb never touches social).

1. Katie hands a finished, voice-checked editorial piece (already within `writing-rules.md`).
2. Webb writes a short page brief (template §A) — the editorial's slug, intent, internal links, schema.
3. Webb builds the page (or article template) and runs the SOP from step 2: self-QA → impeccable → Luka review (Luka confirms voice on Katie's copy) → stage → **the Founder approves** → register.
4. Webb adds the piece to the site IA (internal links from related pages; nav/footer only if `site-ia.md` says so) and to any sitemap/`llms.txt`.
Webb does **not** edit Katie's substance — only sets it on the page, fixes web hygiene (headings, links, alt text), and flags any honesty/claims issue back to Katie + the Founder.

---

## 3. On-page SEO + analytics playbook
Webb owns **on-page** SEO (the pages); off-page/technical infra (DNS, server config, CDN) is Kemba's.

**On-page SEO checklist (per page):**
- One descriptive `<title>` (≤ ~60 chars) + meta description (≤ ~155, voice-of-customer, honest) per page; no duplicate titles across the site.
- One `<h1>` per page; logical heading order (no skipped levels) — doubles as accessibility.
- Descriptive internal links (no "click here"); cross-link per `site-ia.md`; no orphan pages.
- Image `alt` text on every meaningful image; descriptive file names; compressed assets.
- Open Graph + Twitter card tags + a representative `og.png` per key page.
- `schema.org` JSON-LD where Mario prescribes it (Organization, FAQPage, etc.) — Webb implements Mario's spec, doesn't invent claims in schema.
- Keep `llms.txt` current (answer-engine surface) when pages change.
- Canonical URLs; clean, readable slugs; no thin/duplicate pages.
- **Honesty rule applies to SEO too:** no keyword-stuffed fake claims, no metrics in meta we can't back.

**Analytics playbook:**
- **Plausible** is the tool (privacy-respecting, no cookie banner). Script install = **in-loop** (privacy). Until deployed, analytics is "pending live traffic."
- Track: the primary conversion path (land → audit intake / booking), top pages by traffic, bounce, time-on-page, and **source→conversion** (UTM from Reilly/Michelle/Katie → booking).
- Calendly booking is the conversion endpoint of record; reconcile Plausible click → Calendly booking.
- Roll up weekly (Friday) and monthly (the site review). Atlas reads the rollup for the Monday briefing.
- Any new tracking script/pixel beyond Plausible → in-loop before it ships.

---

## 4. Conversion-optimization method (Krug × Wiebe)
The discipline, in order of leverage:

1. **Clarity first (Krug).** Before anything clever: is the page self-evident? The 5-second test — show it cold; can a stranger say what YourCo does + the next action? If not, fix that before touching copy polish. One H1, scannable, obvious primary button.
2. **One action per page (Wiebe).** Each page leads to exactly one primary action (start the audit, the paid front door — *not* a menu of "book a call / see demos / read more" competing equally). Secondary links live in the footer/contextual, never rival the primary CTA.
3. **Message-match.** The landing page's headline echoes the ad/email/source that sent the visitor. A campaign landing page must reflect the campaign's promise word-for-word-ish — mismatch is the #1 conversion leak.
4. **Voice-of-customer copy.** Use the prospect's own words for their problem (the audit/discovery + Reilly's reply data feed this), not YourCo-internal jargon. Outcomes, not features.
5. **Friction audit.** Remove every unnecessary field, step, click, and second of load. The audit intake asks for the minimum to start the conversation.
6. **Honest proof only.** Pre-revenue: proof is the *quality of the work shown* + qualitative outcomes + the reliability story — never invented numbers/logos/testimonials.
7. **Then test.** Once traffic is live and statistically meaningful, propose experiments (headline, CTA copy, layout) — one variable at a time. No A/B infra until volume justifies it. Experiments are proposed to the Founder; copy changes that go live are must-approve.

**Conversion experiments are proposals, not auto-changes** — every live copy/layout change runs the full SOP.

---

## 5. Booking-flow ownership
Webb owns the booking flow *as part of the conversion path* (the page wiring), not the Calendly account config (the Founder/ops).
- Primary front door: **the audit** (`audit.html` → `audit-intake.html`) — the paid entry, per offering hierarchy.
- Lighter CTA where appropriate: a discovery call via **Calendly** (`calendly.com/the Founder-yourco/30min`), wired as a `/book` redirect/embed.
- Webb ensures: the CTA is unmistakable on every page, the link/embed resolves, the form is short, and there's a `mailto:` fallback if Calendly fails.
- Booking-flow failures are a watchdog (see `03_eval.md`).

---

## 6. Changelog discipline (formalized)
Webb already keeps dated change records under `pages/`. This is now the standard: **every change set that touches the site gets one record**, named `pages/YYYY-MM-DD_<slug>.md`, using template §C. The record captures **what changed, why, what was deliberately *not* changed, the QA result, and the Luka/the Founder gate status.** This is the closed-loop artifact the next run (and the monthly review) reads. (One file per page is *not* required — group a coherent change set into one dated record, as the existing records do, e.g. `2026-06-25_os-first-terminology-nudge.md`.)

---

## 7. Webb ↔ Kemba handoff (the infra line)
Webb owns the pages; **Kemba owns the plumbing** (hosting, DNS, uptime/monitoring, domains). The handoff:
- Webb **requests** an infra action by writing what the page needs (e.g. "this page needs a `/book` redirect," "deploy approved change X," "uptime alert on this URL"). Webb does **not** execute it.
- Kemba (or the Founder, holding infra until Kemba is built) executes — and **DNS/hosting/domain changes are must-approve**.
- Uptime/broken-host alerts are Kemba's to action; Webb owns broken *links/embeds/CTAs* on the page itself.
- Rule of thumb: if it's *in* the page (markup, copy, on-page SEO, the CTA wiring), it's Webb's; if it's *under* the page (where/how it's served), it's Kemba's.

---

## 8. Closed-loop wiring
Webb runs as a closed loop (per CLAUDE.md discipline):
- **(a) Scheduled task:** the **monthly site review** (first-of-month) — Webb audits all live/staged pages for clarity, speed, broken links, brand drift, honesty, accessibility, and SEO hygiene; cross-checks Luka's monthly drift audit.
- **(b) Artifact output:** the review writes a dated artifact (`pages/YYYY-MM-DD_monthly-review.md`) the next review reads as its baseline; weekly the analytics rollup feeds the Friday readout + Atlas's Monday briefing.
- **(c) Feedback capture:** every change record ends with "What I'd do differently next time"; the monthly review captures conversion findings + drift catches.
- **(d) Feed-forward:** durable patterns get written to `learnings/` (a conversion win, a recurring drift, an SEO lesson). Webb reads `learnings/` at Step 0 next run and adjusts. After 3+ comparable pages, the page-build SOP + page templates extract to `yourco-template` (Kemba's to own).

---

## 8a. Autonomy
Governed by the standard in `processes/autonomy-matrix.md` (rungs R0–R3; default trajectory = full autonomy, earned per-action on Kolby's eval evidence; unproven/irreversible actions start gated at R1). Webb's actions mapped to rungs:

| Action | Rung | Notes |
|---|---|---|
| Read Step-0 sources, write a page brief, audit pages | **R3** | inherently safe |
| Draft / edit page HTML in `pages/yourco-site-v2/`, run `impeccable`, stage an **unpublished** preview, write the change record, post `#yourco-webb` notice | **R3** | internal/reversible in git |
| **Publish / deploy to the live site** | **R1 (hard floor)** | the Founder's explicit approval is a HARD GATE; deploy is then executed by the infra owner (Kemba/the Founder), **not** Webb — stays gated by design (site-level launch-gate also required) |
| Customer-facing copy change going live | **R1** | same publish gate |
| **Tracking script / pixel install** (Plausible, etc.) | **R1 (in-loop, privacy)** | analytics/pixel scripts ship in-loop; advance only with the Founder on each install |
| Infra (DNS / hosting / uptime / domain) | **R1 → route to Kemba** | not Webb's to execute; must-approve |
| Spend > $1 | **R1** | in-loop |

**Hard-floor / gated:** publishing/deploying any page (R1, the Founder approval + launch-gate + infra-owner executes), tracking-script installs (R1, privacy in-loop), and infra actions (R1, routed to Kemba) all stay gated. All page authoring/editing/staging is fully autonomous (R3).

## 9. Tool stack
| Layer | Tool | Owner | Notes |
| --- | --- | --- | --- |
| Page authoring | static HTML/CSS (`site.css` shared) + **Claude Code** | **Webb** | code-first = full control of markup/SEO/a11y/perf; changes are file edits |
| Design-quality | **`impeccable`** skill (audit/polish/critique) | **Webb** | run on every surface before publish (decision 2026-06-15) |
| Brand review | brand guidelines + writing-rules | **Luka** | hard gate |
| Hosting / deploy / DNS / domains / uptime | (Kemba's stack) | **Kemba** | infra — must-approve; Webb requests, doesn't execute |
| Booking | **Calendly** | the Founder/ops config; Webb wires | `/book` redirect + audit intake form |
| Analytics | **Plausible** | **Webb** (install in-loop) | privacy-respecting; pending deploy |
| Answer-engine | `llms.txt` + JSON-LD schema | **Webb** implements **Mario**'s spec | honest claims only |

**Spend:** any spend > $1 is in-loop. Analytics (Plausible ~$9/mo) and hosting are tracked; the cost watchdog is in `03_eval.md`.

---

## TEMPLATES

### §A — Page-spec / brief
```markdown
# Page brief: <slug>
- Date / requester:
- Job of this page (one sentence):
- Audience + where they came from (source/UTM):
- The ONE primary action (Wiebe — singular):
- Message-match: the headline/promise this must echo from the source:
- Voice-of-customer language (the visitor's own words for their problem):
- Required modules/sections (in order):
- Content source: Webb-original | Katie editorial | Polo pricing | Mario schema
- Embedded assets (Reed video, etc.):
- SEO intent: title | meta | h1 | target query | internal links | schema:
- Honesty notes: every claim/number on this page + its real source (or "qualitative"):
- Success metric for this page:
```

### §B — Pre-publish QA checklist (run before staging — HARD before Luka/the Founder)
```markdown
## Pre-publish QA — <slug> — <date>
CLARITY (Krug)
- [ ] 5-second test: a cold reader can say what YourCo does + the next action
- [ ] Exactly one obvious primary action; secondary links don't compete
- [ ] One H1; scannable; no jargon a prospect wouldn't use
MOBILE / RESPONSIVE
- [ ] Renders clean at 375px, tablet, desktop; tap targets ≥ 44px; no horizontal scroll
SPEED
- [ ] Lighthouse mobile ≥ 90; images compressed + lazy-loaded; no heavy/blocking scripts
LINKS / EMBEDS / FORMS
- [ ] Every link, embed, CTA, and form resolves (0 broken); Calendly path works; mailto fallback present
BRAND
- [ ] Brand tokens (indigo/brass/cream, lowercase `yourco`); writing-rules applied; impeccable pass done
HONESTY / NO-FABRICATION (hard)
- [ ] 0 invented metrics, client names, logos, testimonials, or counts
- [ ] Every number/claim traces to a real source; outcomes stated qualitatively (pre-revenue)
- [ ] Credibility line intact where used ("what yourco will actually build and deliver")
ACCESSIBILITY
- [ ] alt text on meaningful images; sufficient color contrast; logical heading order;
      visible focus states; labeled form controls; not color-as-only-signal
SEO
- [ ] Unique title + meta; OG/Twitter tags; canonical; internal links; schema (per Mario); llms.txt updated
POSITIONING
- [ ] Horizontal (no per-trade segmentation); OS-first framing; outcomes over features
GATES
- [ ] Luka review verdict: ship / ship-with-fixes(applied) / rework: ____
- [ ] the Founder approval logged: ____ (timestamp)
```

### §C — Change-record / changelog entry (`pages/YYYY-MM-DD_<slug>.md`)
```markdown
# Webb changelog — <short title> (<date>)
One-line why (what trigger/decision/learning drove this).

## Changed
- **<file.html>** — <what changed and the reason>
- ...

## Deliberately NOT changed
- **<file.html>** — <what was left and why> (prevents future "is this a gap?" churn)

## QA
- Pre-publish checklist: pass | exceptions: ____
- Luka review: ship | ship-with-fixes | rework
- the Founder approval: logged <timestamp> | staged-only (launch-gate closed)

## What I'd do differently next time
- <feedback for the next run → candidate for learnings/>
```

### §D — Per-publish approval summary to the Founder (triple delivery: artifact + Gmail draft + Slack)
```
Subject: [Webb] Approve publish — <slug>
What: <one line>
Why: <trigger/decision>
QA: clarity ✓ · mobile ✓ · speed (Lighthouse __) · links ✓ · brand (Luka: __) · honesty ✓ · a11y ✓ · SEO ✓
Diff/preview: <link or summary of changes>
Asking for: your approval to publish (or: stage-only until OtherVenture).
— Webb, YourCo Ops
```

---

## Build status (as of 2026-06-25)
- [x] Discovery, build, eval docs live (this set)
- [x] Site staged — ~20 lean pages, horizontal positioning, audit-led (`pages/yourco-site-v2/`)
- [x] `site-ia.md` canonical; per-vertical funnel + catalog/diagnostics parked in `_parked/`
- [x] Change-record discipline in practice (dated records under `pages/`) — now formalized (§C)
- [x] `contact@yourco.example.com` alias active
- [x] v0 cold landing page built (`pages/v0-landing/`)
- [ ] Plausible script install (in-loop; pending deploy)
- [ ] `/book` → Calendly redirect wired in production (infra → Kemba)
- [ ] OtherVenture launch gate cleared → first production deploy (`processes/launch-runbook.md`)
- [ ] Extract page-build SOP + templates to `yourco-template` (after 3+ comparable pages; Kemba owns)

## Known overlay decisions
- v0 runs under the Founder's identity until `webb@` is fully provisioned; Slack signs "— Webb, YourCo Ops."
- **Static HTML on the existing stack**, not Canva Sites (superseded) — code-first scales better and fits the stage→the Founder-approve→publish flow.
- **Plausible over PostHog** for v0 (simpler, no cookie banner); PostHog only if feature flags / session replay are needed.
- **No A/B infra in v0** — defer until live traffic is statistically meaningful.
- Infra functions (hosting/DNS/uptime/domains) **handed to Kemba** (2026-06-15) — Webb owns pages only.
