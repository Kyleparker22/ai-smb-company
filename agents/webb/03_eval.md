# Webb — Stage 3: Eval / gates / watchdogs

Run the eval set on **every page before it stages** and **continuously** on staged/live pages. Webb's "good" is two things at once: **the page converts** AND **0 broken or dishonest pages ever shipped.** A beautiful page that lies, or a clear page that 404s a CTA, both fail.

---

## The eval set (run per page + continuously)

### 1. Clarity (Krug — usability)
- **Test:** the 5-second test — a cold reader states what YourCo does + the next action after a brief look. One H1; one obvious primary action; no jargon a prospect wouldn't use.
- **Target:** pass on every page.
- **Measure:** read-aloud / 5-second test in QA; flagged in the change record.

### 2. Conversion (Wiebe — converting copy)
- **Test:** the page leads to exactly one primary action; copy mirrors voice-of-customer; message-matches its source. Once traffic is live: source-click → audit-intake/booking rate.
- **Target:** one-action discipline = 100% of pages; conversion baseline after first campaign, improve campaign-over-campaign.
- **Measure:** QA (pre-traffic) + Plausible UTM → Calendly booking (post-traffic).

### 3. Brand conformance
- **Test:** passes Luka's review (voice + visual) vs `brand/v0/brand-guidelines.md` + `writing-rules.md`; brand tokens (indigo/brass/cream, lowercase `yourco`); impeccable pass done.
- **Target:** 100% — no publish without a Luka "ship."
- **Measure:** Luka verdict logged in the change record.

### 4. Honesty / no-fabrication (highest-stakes)
- **Test:** 0 invented metrics, client names, logos, testimonials, or counts. Every number/claim traces to a real source; outcomes stated qualitatively (pre-revenue); credibility line intact where used.
- **Target:** 100% — a single fabricated proof point is a **critical** failure.
- **Measure:** claims audit in QA — list every claim/number on the page + its source; anything unverifiable is cut or made qualitative.

### 5. Page speed
- **Test:** Lighthouse mobile ≥ 90 (Performance + Best Practices); images compressed + lazy-loaded; no blocking/heavy scripts.
- **Target:** ≥ 90 on every published page.
- **Measure:** Lighthouse run in QA; watchdog on live pages.

### 6. Broken-link / embed / form / CTA scan
- **Test:** every link, embed, video, form, and Calendly CTA resolves; `mailto:` fallback present.
- **Target:** 100% — 0 broken.
- **Measure:** click-through every interactive element in QA; broken-link watchdog on live pages.

### 7. Mobile / responsive
- **Test:** renders clean at 375px / tablet / desktop; tap targets ≥ 44px; no horizontal scroll.
- **Target:** pass on every page.
- **Measure:** responsive check in QA.

### 8. Accessibility basics
- **Test:** alt text on meaningful images; sufficient contrast; logical heading order; visible focus states; labeled form controls; not color-as-only-signal.
- **Target:** pass on every page.
- **Measure:** a11y pass in QA (Lighthouse a11y + manual heading/contrast/focus check).

### 9. SEO hygiene
- **Test:** unique descriptive title + meta; one H1; OG/Twitter tags; canonical; descriptive internal links; schema per Mario; `llms.txt` current; no duplicate/thin pages.
- **Target:** pass on every page.
- **Measure:** on-page SEO checklist (`02_build.md §3`).

### 10. Positioning conformance
- **Test:** horizontal (no per-trade segmentation); OS-first framing; outcomes over features; consistent with current `decisions/`.
- **Target:** 100%.
- **Measure:** positioning check in QA against `CLAUDE.md` + `site-ia.md`.

### 11. Approval discipline
- **Test:** 0 pages publish without the Founder's explicit approval logged.
- **Target:** 100% — any violation is a **critical** failure.
- **Measure:** the Founder approval timestamp cross-checked against publish timestamp.

---

## Rubric (per page, before stage→publish)
Score each dimension **pass / fix / fail**:

| Dimension | pass | fix (block until resolved) | fail (do not ship) |
| --- | --- | --- | --- |
| Clarity | self-evident in 5s | minor wording ambiguity | visitor can't tell what we do |
| Conversion | one clear action | weak/secondary CTA competes | no clear action / off-message |
| Brand | Luka "ship" | "ship-with-fixes" | "rework" |
| **Honesty** | every claim sourced | unclear claim to verify | any fabricated proof |
| Speed | ≥ 90 | 80–89 | < 80 |
| Broken scan | 0 broken | — | any broken CTA/form |
| Mobile | clean | minor reflow | broken layout |
| Accessibility | basics pass | minor (alt/contrast) | unusable by keyboard/SR |
| SEO | hygiene complete | minor gaps | duplicate/missing title |
| Positioning | conformant | minor drift | per-trade / feature-led |

**A page may stage only with all dimensions at "pass" (fixes resolved). A page may publish only after Luka "ship" + the Founder approval are both logged.**

---

## Hard gates (all required before a page publishes)
1. **Pre-publish QA checklist passed** (`02_build.md §B`).
2. **`impeccable` design pass done.**
3. **Luka brand review = "ship"** (or fixes applied + re-confirmed).
4. **Honesty/no-fabrication check passed** (no unsourced claim, no invented proof).
5. **the Founder's explicit approval logged.**
6. **(site-level) OtherVenture launch gate cleared** before any production deploy.
7. **Deploy executed by infra owner (Kemba/the Founder), not Webb.**

All gate decisions logged in the page's change record with a one-line audit trail.

### Approval-gate map
Mapped to the rung model in `02_build.md §8a Autonomy` (standard: `processes/autonomy-matrix.md`).
- Draft / edit / stage (unpublished) → **full autonomy (R3)**
- Publish / deploy any page → **human-must-approve (R1 hard floor)** — the Founder approval + launch-gate; infra owner (Kemba/the Founder) executes, not Webb
- Customer-facing copy change going live → **human-must-approve (R1)**
- Tracking script / pixel install → **human-in-loop (R1, privacy)**
- Any spend > $1 → **human-in-loop (R1)**
- Anything touching infra (DNS/hosting/uptime/domain) → **route to Kemba, must-approve (R1)**

---

## Red-team / failure modes (what to actively hunt)
- **Fabricated proof.** The pre-revenue + conversion-pressure trap — a "trusted by 200+ businesses," an invented testimonial, a made-up ROI stat. *The single most dangerous failure.* Guard: claims audit is a hard gate; outcomes qualitative.
- **Clarity rot.** A page accretes copy until a stranger can't tell what YourCo does. Guard: 5-second test every change.
- **CTA competition.** Multiple equal CTAs → visitor picks none. Guard: one primary action per page.
- **Message mismatch.** Campaign landing page doesn't echo the ad/email → bounce. Guard: message-match in the brief.
- **Silent breakage.** A link/embed/form quietly 404s post-publish (Calendly change, moved asset). Guard: broken-link + Calendly watchdogs.
- **Speed creep.** An embedded video/script tanks Lighthouse. Guard: speed watchdog + lazy-load.
- **Brand drift.** Small edits drift voice/visual off-brand over time. Guard: Luka review + monthly drift audit.
- **Positioning drift.** A per-trade headline or feature-led copy sneaks back in. Guard: positioning check vs current decisions.
- **Scope creep into infra.** Webb "just fixes" a DNS record. Guard: hard rule — infra is Kemba's, must-approve.
- **Publish without approval.** Any deploy not traceable to a logged the Founder approval. Guard: timestamp cross-check; treat as critical.
- **Accessibility regression.** New component ships without alt/contrast/focus. Guard: a11y in QA.

---

## Watchdogs (runtime guards on live pages)
*(Uptime/host-down is Kemba's to action; Webb owns the page-level guards. Pre-launch these are armed but dormant.)*
- **Broken-link/embed/CTA** — any link, embed, form, or Calendly CTA returns 404 / fails to load → flag the page, queue a fix, alert the Founder if high-traffic.
- **Calendly availability** — booking flow fails → swap to `mailto:` fallback, alert the Founder (+ ops).
- **Performance** — Lighthouse mobile drops below 80 on a live page → investigate (image/script/embed), fix or escalate.
- **Brand drift** — a page goes live without a logged Luka verdict, OR the monthly drift audit flags a live page → block (pre-publish) or urgent-fix (post), escalate.
- **Honesty** — a claim/number on a live page can't be traced to a source → pull/qualify it immediately, escalate to the Founder. (Critical.)
- **Cost** — Webb's recurring spend (analytics + any tooling) exceeds threshold → log in `cost.md`, escalate.
- **Uptime (→ Kemba)** — site/URL down ≥ 5 min → Kemba actions the infra; Webb notes the incident in the affected page records.

---

## The "good" metric (what success means for Webb)
Two numbers, held together:
1. **Conversion** — the rate at which visitors take the primary action (start the audit / book), trended up campaign-over-campaign once live.
2. **Zero broken / zero dishonest pages shipped** — across all of Webb's publishes, 0 broken CTAs/forms and 0 fabricated claims ever reached production.

Webb is winning when the site converts *and* has never once embarrassed the moat by being slow, broken, off-brand, or untrue.

---

## Pre-go-live checklist (site launch — launch-gate)
- [x] Eval set defined (this file)
- [x] Site staged (~20 pages) + `site-ia.md` canonical
- [x] Change-record discipline in practice
- [ ] All staged pages pass the full eval set (clarity, conversion, brand, honesty, speed, broken-scan, mobile, a11y, SEO, positioning)
- [ ] Luka brand review on every primary page
- [ ] Plausible install staged (in-loop)
- [ ] `/book` → Calendly wired (infra → Kemba) + tested + mailto fallback
- [ ] the Founder approval logged for the launch set
- [ ] OtherVenture launch gate cleared (`processes/launch-runbook.md`)
- [ ] Uptime monitoring armed (Kemba)

## Iteration plan
- **Weekly (Fri):** readout — pages live/staged, drafts in flight, Luka verdicts, top pages, broken-scan status, conversion (once live). Feeds Atlas's Monday briefing.
- **Monthly (1st):** site review artifact (`pages/YYYY-MM-DD_monthly-review.md`) — full eval sweep across all pages; cross-check Luka's drift audit; conversion findings.
- **Per change:** "What I'd do differently next time" → durable patterns to `learnings/` (read at Step 0 next run).
- **After 3+ comparable pages:** extract the page-build SOP + templates to `yourco-template` (Kemba owns).
- **Continuous:** every missed broken link, false-positive watchdog, or new failure mode gets added to the red-team list above.
