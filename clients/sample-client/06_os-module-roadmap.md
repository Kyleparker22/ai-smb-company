# Sample Client — AI OS Module Roadmap

*Created 2026-07-22. The full menu of wow/ROI modules for Sample Client, mapped to yourco's 8 pillars. The Same-Day Design Studio (`prototype/design-studio/`, live at sample-client-studio.higgsfield.app) is Module 1; this doc is the expansion scope that turns the demo into a proposal. Each module = an outcome yourco builds + operates, not software Client Owner runs. Prices/tiers are illustrative until Polo locks; agent names never appear on client surfaces.*

## The frame
One product, one motion: **audit → custom AI OS**. Client Owner starts with the Design Studio (or its first module) and adds the next when it's already paying for itself. The unit of sale is the OS, not a per-feature meter. Everything is built on **his Aspire data + Belgard supplier pricing** — that shared dependency is the one thing to confirm (Aspire API or export access).

## Two hard dependencies (confirm with Client Owner)
1. **Aspire access** (API or scheduled export) — powers the quote, margin guardrail, auto-POs, scheduling, job-cost. The single most important integration to validate.
2. **Warranty terms** — the warranty/care-reminder module assumes SC's real windows (from Job #6051 T&Cs: sod 30 days, hardscape 5 yr, retaining walls 3 yr, natural stone 1 yr, brass lighting lifetime/10 yr, LED 5 yr, irrigation 5 yr, drainage 1 yr, water features 1 yr, labor 1 yr). Confirm these are current.

---

## Customer-facing modules (delight → close rate)

| Module | What it does | Outcome | Status |
|---|---|---|---|
| **1. Same-Day Design Studio** | Photo → design → 3-tier quote → 2D plan → cinematic tour, first visit | The close moment; kills the 2–6 wk gap | **LIVE in demo** |
| **2. Base / Better / Dream tiers** | Every quote auto-generates 3 budget tiers; homeowner picks | Raises avg ticket — the bigger yard sells itself | **LIVE in demo** (pure-CSS selector) |
| **3. Design variations on demand** | "Darker pavers / fire table instead / add a pergola" → instant re-render | Emotional close lever — people fall in love by playing | Needs render generation |
| **4. Draggable before→after slider** | Slide across their own yard, raw → finished | Visceral proof on their real space | Needs a matched before/after pair (same angle) |
| **5. Day/night + seasons + "in 3 years" toggle** | Dusk w/ lighting on; fall; plants at maturity | Emotional sell; their warranty PDF already promises "plants shown in full growth" | Needs render generation |
| **6. Belgard material picker** | Swap real paver colors/styles from the catalog; render + price update live | Interactive spec'ing; upsell to premium materials | Needs paver-swap renders + Belgard catalog data |
| **7. Shareable household link** | Send the design to the spouse for buy-in | Couples decide big spends together — removes the #1 stall | Concept in demo (link is shareable) |
| **8. Live project portal** | Post-sign: this week's work, crew ETA, photos, next payment, punch list | Kills "where are you guys?" calls (also an owner admin win) | Template exists (`clients/_yourco-template/client-console.html`) |

### Added 2026-07-22 (Client Owner asks)
- **Scope = hardscape AND landscape** — Client Owner wants the design/quote/render to cover full landscape work (planting plans, lawns/sod, garden beds, grading, irrigation, lighting), not just hardscape. Demo reframed to say so; the estimating assemblies already include sod/beds/plantings/mulch/lighting. *(No new build — positioning + assembly coverage.)*
- **Inspiration / vision upload (LIVE in demo)** — homeowner drops reference images, videos, or a Pinterest link with their photos; the AI reads the references so the *first* render matches their vision (image-to-image conditioning on their inspiration, not just the yard photos). Accuracy-on-first-try lever.
- **Command dashboard (LIVE in demo, module = Job-cost + ROI dashboard)** — owner surface showing turnaround, quote→close rate, revenue influenced, leads captured, design hours saved, render $ saved, with a 6-month trend. Sample figures labeled illustrative; populates with real Aspire + site data. This is the "prove the ROI" screen.
- **Live configurator (LIVE in demo 2026-07-22)** — the `#build` "Build it together — live" section: à-la-carte add-on toggles → live-updating total + render swap (real AI renders of the yard: base.jpg entry-level, hero.jpg Better, dream.jpg w/ outdoor kitchen + water feature). Real JS on the deployed SPA via a React `useEffect` enhancer. This is the guided in-person upsell tool. Add-on prices sum exactly to the tier totals ($15,900 base → $46,500 all). Remaining: per-add-on real-time generation (production), day/night + material-picker render variants (optional polish).
- **Interactive editing — decided:** *both, staged.* Full interactive design play (add/remove/swap, tier + material changes → live render + budget) at the **guided quote** (rep's iPad — drives upsells). A **bounded, approval-gated** version at the **proposal** — homeowner toggles pre-approved optional add-ons and watches price update, but can't gut scope or rearrange freely; material changes still route to Client Owner to approve. Same engine, two trust levels. Guided version to be built into the demo/HTML proposal.

### Materials availability / earliest-start (built into the quote — LIVE)
The instant quote checks supplier lead times against the calendar and tells the homeowner the **real start date up front** ("✓ in stock, start wk of Aug 25" vs "⚠ kitchen ~3-wk lead, start wk of Sept 15"). Same lead-time data that powers Auto-POs (Module 14). Homeowners care about "when can you start" more than almost anything.

### Anti-poaching guardrail (the lead-magnet moat)
Concern: homeowner gets the free visual, shops it to a competitor. Mitigation (reflected in the product):
- **Free tier = the dream** (watermarked concept image + budget *range*). **Paid/relationship tier = the blueprint** (full-res render, scaled plan, itemized takeoff, firm number) — only after the on-site visit. The accurate takeoff literally can't exist before Colton's Moasure measure, so there's nothing precise to hand off.
- Tiled **"Sample Client" watermark** on every free render — useless in a competitor's proposal.
- **Speed-to-lead (Module 11)** makes SC the first mover; the design is the reason for the appointment, not a takeaway.
- Range is **anchored to SC's assemblies** — a competitor can't honor it.
- **IP line** on renders ("concept © Sample Client, for installation by Sample Client") — SC's own T&Cs already claim design IP.
- Optional filter: **small refundable design fee** (credited to the job) for the full cinematic + detailed plan. Standard in the trade; evaporates free-render tourists.

---

## Owner-facing modules (ROI / margin / efficiency)

| # | Module | What it does | Outcome | Pillar |
|---|---|---|---|---|
| 9 | **24/7 website design magnet** | Homeowner drops a backyard photo on sampleclient.example.com → instant watermarked concept + range; lead captured | Site sells while he sleeps; fills top of funnel; pre-qualifies tire-kickers | Intake |
| 10 | **Speed-to-lead auto-responder** | Any new lead (web/Angi/Google LSA/FB) gets a personal text + booking link in <60s | Responding in 5 min vs 30 = ~10× contact rate; cheapest conversion win | Intake |
| 11 | **Follow-up autopilot** | Nurtures unsigned quotes through the 2–6 wk gap; re-works dead quotes | Recovers deals that used to just die | Sales |
| 12 | **Margin guardrail** | Checks each quote vs real Aspire cost history; flags underpriced bids before they go out | No more money-losing jobs | Sales |
| 13 | **Auto supplier POs** | On sign, drafts Belgard/supplier orders from the takeoff; checks lead times | Faster starts, no material-delay idle crews *(orig. SC proposal use case)* | Operations |
| 14 | **Crew scheduling + weather** | Books installs vs Aspire calendar, material lead times, forecast; flags conflicts | Fewer rained-out, idle crew days | Operations |
| 15 | **Review + referral engine** | Asks for the Google review at the perfect post-install moment; asks for referrals w/ their before/after render | Compounding, near-free leads + SEO | Marketing |
| 16 | **Auto marketing content** | Every finished job's before/after + render → ready-to-post reels/carousels | A portfolio + content feed that build themselves | Marketing |
| 17 | **Job-cost dashboard** | Real-time actual-vs-estimate per active job from Aspire | Catch overruns while they're still fixable | Back Office |
| 18 | **Warranty + care reminders** | Seasonal care + warranty-window reminders fire off each install date | Retention + maintenance-plan upsell | Customer |

*(Removed per Client Owner 2026-07-22: any financing module — SC does not finance projects.)*

---

## Suggested phasing
- **Phase 1 (the wedge, mostly built):** Same-Day Design Studio + tiers + materials-availability. Prove the close.
- **Phase 2 (revenue machine):** Website design magnet + speed-to-lead + follow-up autopilot. Fill and convert the funnel.
- **Phase 3 (margin + ops):** Margin guardrail + auto-POs + crew/weather scheduling + job-cost dashboard. Protect the money.
- **Phase 4 (compounding + retention):** Reviews/referrals + auto marketing content + live project portal + warranty reminders.
- **Ongoing render features** (variations, day/night, material picker, slider) layer onto Phase 1 as generation renders are produced.

## OS packaging fit
Maps cleanly to the four OS levels (Core ~3 agents / Suite ~5 / Operation ~7 / Command up to 10). Sample Client's full menu spans ~10–12 modules across 6 pillars → a **Suite→Operation** build, delivered in phases. Polo prices the band; brotherhood pricing ($0 kickoff / $1k-mo) holds for engagement #1 while the playbook hardens.

## Demo state (2026-07-22)
Live at sample-client-studio.higgsfield.app: 5-step Same-Day flow · 3-tier selector · Aspire-format quote (grouped assemblies, Items/Qty/Unit, +40% subs, PROJECT TOTAL, SC footer) · materials-availability card · Structure-Studios-caliber 2D plan + takeoff · Editing & revisions note · **"The whole operating system" section** (12 module cards) · honest section. See [[sample-client-design-studio-demo]].
