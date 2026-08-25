# Storm-command — enhancement roadmap (better/faster/more ROI for Nick)

Ideas beyond today's build (pull → cross-verify → AI-read → approve → SMS dispatch).
Grouped by lever, with the ROI logic. ★ = highest-ROI, build-next.

## A. Speed — first crew to the door gets paid
- ★ **Real-time alerts, not daily.** A live watcher polls NWS/Xweather every few minutes during active weather and pushes the instant a storm verifies. Today's loop is daily; storm-chasing is won in hours. *ROI: beat every competitor to the neighborhood.*
- **Pre-storm staging.** When severe weather is *forecast* for a county tomorrow, pre-position crews so they canvass as the storm clears — before competitors even know it hit. *ROI: first-mover, at zero extra drive time.*

## B. Precision — turn "county" into "these streets, in this order"
- ★ **Block-level hail swaths + canvassing map.** HailTrace/MESH down to zip/street; hand each crew a map, not a county. *ROI: no wasted driving; every door is inside the damage.*
- ★ **Route optimization.** Given the swath + crew home base, auto-generate the optimal door-knock route (max doors/hour, like a delivery route). *ROI: more doors per crew per day.*
- **Property overlay.** Prioritize by roof age / home value / owner-occupied (public property data). Knock the highest-ticket, most-likely-to-convert doors first. *ROI: higher revenue per door.*

## C. Lead → close → claim — compress the whole pipeline
- ★ **Door-knock script with the NOAA proof baked in.** "On 6/24 your neighborhood had *verified* 1.25″ hail — here's the report." Roofers show evidence, not a pitch. *ROI: higher close rate, shorter conversations.*
- ★ **Homeowner proof link / QR.** A per-address page: "your home was hit by verified hail on X — NOAA source of record." Instant trust. *ROI: converts skeptics, differentiates from door-knockers with no proof.*
- ★ **Claim-assist packet.** Auto-fill the storm-verification part of the insurance claim (date, location, hail size, NOAA source) — we already build the evidence trail (`VERIFICATION.md`). *ROI: faster approvals, fewer denials, homeowner happy, roofer paid sooner. This is the stickiness.*
- **Field lead capture.** Roofers log knocked / interested / not-home from their phone → CRM → auto follow-up sequence to warm leads. *ROI: no lead falls through; not-homes get a second touch.*

## D. Coordination — never waste a crew
- **Crew ack + live coverage map.** Roofers reply "on it"/"done"; Nick sees who's where in real time → no two crews on the same street, full coverage. *ROI: eliminates double-coverage waste.*
- **Capacity-aware dispatch.** 5 counties hit at once → allocate crews by severity × property value, not first-come. *ROI: crews on the most profitable damage first.*
- **Weather-safety hold.** Don't dispatch into active severe weather; auto-release on all-clear. *ROI: safety + no wasted trip into a storm still moving.*

## E. Learning loop — the moat, compounds every storm
- ★ **Outcome tracking → feed-forward.** Log doors knocked → jobs closed → revenue per storm/area/hail-size. Learn which storm profiles convert best and auto-prioritize future dispatches. *ROI: the system gets smarter and more profitable every storm — exactly what no-code can't do.*
- **Repeat-damage / storm-history overlay.** "This neighborhood was also hit in 2023." *ROI: repeat-damage areas convert better; target them.*

## F. Inbound — beyond door-knocking
- **Auto geo-targeted post/ad on a verified hit.** "Storm damage in [area]? NOAA-verified, free inspection." *ROI: inbound leads while crews canvass.*
- **Past-customer + referral blast.** Text past customers in a hit area: "your area was just hit — free inspection?" *ROI: warmest possible leads, near-zero cost.*

## G. Trust / prove the ROI
- ★ **ROI dashboard.** Attribute revenue to the system: storms → doors → jobs → $, plus "trips saved" from filtered storms. *ROI: shows Nick exactly what the tool made him — and justifies a subscription later.*
- **Multi-year claim archive.** Every storm + evidence archived, so a claim filed months later still has the proof. *ROI: claims lag; the evidence never expires.*

## Recommended build-next (3, in order)
1. **Real-time alerts** (A) — speed is the entire business; biggest single lift.
2. **Swath map + optimized route + door-knock proof script** (B+C) — turns a verified alert into a crew standing at the right door with evidence in hand.
3. **Outcome learning loop + ROI dashboard** (E+G) — makes it compound and proves the money, which is what turns Nick into a reference (and a subscription).

---

# Version 2 — the back of the business (PARKED — build after v1 is live)

**Status: v2, deferred.** These are captured for later, not being built now. The
priority is getting v1 (storm command → dispatch → crew app → claim tools) hosted
and in Nick's hands first. Revisit this list once v1 is running for real.

The front (find→dispatch→knock→capture) is built. At 27 signs/week + 2 new
companies, manual work now lives *after* the signature and *across* companies —
that's what v2 attacks.

## H. The signed-job pipeline (organization + less manual) ★
- **Production board** — every signed roof auto-moves through stages: inspected → claim filed → adjuster set → approved → supplement → scheduled → materials ordered → installed → final inspection → invoiced → collected. The AI drafts each stage's next doc/message; nothing stalls silently. *ROI: run 100+ live jobs without a job falling through the cracks.*
- **Aging/stall surfacing** — jobs stuck at a stage (adjuster no-response, unsigned estimate, uncollected balance) auto-surface with a one-tap nudge. *ROI: no revenue lost to things going quiet.*

## I. Insurance claim lifecycle (better outcomes + ROI — the money) ★
- **Auto-draft the claim submission** from the inspection + our storm evidence packet (already built).
- **Supplement drafting** — the AI drafts supplements from the scope + photos. Roofers leave real money on the table not supplementing; this captures it. *ROI: higher approved $ per job.*
- **Claim status tracking** — filed → approved → paid, with adjuster-meeting scheduling + reminders. *ROI: faster approvals, fewer stalls, paid sooner.*

## J. Customer comms + reviews/referrals (less manual + more leads) ★
- **Auto status updates** — homeowner gets the right message at each stage ("claim approved", "install Tuesday", "crew arriving AM") without Nick texting anyone. *ROI: better CX at 10× volume, zero manual.*
- **Review + referral engine** — auto-request a Google review + a referral at job completion (the moment they're happiest). *ROI: storm roofers live on reviews + referrals; automate the ask.*

## K. Money + people (organization at scale)
- **Commission ledger** — auto-computed from crew-app signings (already captured): who signed what, what's owed, payout runs. *ROI: no manual math, transparent to reps/companies.*
- **Cash-flow view** — pipeline value, expected collections (deposit → insurance check → final), aging receivables. *ROI: know the money as volume + companies grow.*
- **Materials order** — auto-generate the material list (squares/shingles) from the roof measurement/scope → supplier → delivery-to-job tracking. Aerial-measurement (EagleView/Hover) seam. *ROI: less ordering error, faster builds.*

## L. Multi-company command (the "adding 2 companies" need) ★
- **Portfolio view** — one screen across all his companies: production, comparative ROI, coverage — shared storm intel, separate rosters/dispatch/branding (multi-tenant). *ROI: run 3 companies like one.*
- **Daily ops brief** — a morning AI one-pager: today's verified storms, jobs needing action (adjuster, install, collect), crew coverage, new leads. Run the whole day off one screen. *ROI: replaces the mental juggling that breaks at scale.*

## Phase-2 build-next (3, in order)
1. **Signed-job production board + aging surfacing** (H) — the single biggest organization win at his volume.
2. **Claim lifecycle + supplement drafting** (I) — the biggest $ win (approved-dollars per job).
3. **Multi-company portfolio + daily ops brief** (L) — the "adding 2 companies" need, and how Nick runs it all from one screen.

---

# Nick's product vision (from 2026-07-04 texts) — StormVerified.com

Domain **StormVerified.com** is bought. Positioning crystallized by Nick:

> **"Use the same tools insurance carriers use for denials, and use it against them — beat them at their own game."**

Carriers use Nearmap et al. to check whether damage predates the "date of loss" (to deny claims). Nick wants to flip that: give roofers/PAs/attorneys the *same* pre-loss vs post-loss satellite evidence to *prove* the damage is new and *win* approvals.

**Marketing targets:** roofers, public adjusters, attorneys, contractors.
**Motto:** *"Better storm dates, real-time data. Verified."*
**Value prop:** take the guesswork out of multiple storm apps / conflicting weather reports; verified storm dates + data straight to the phone; a human/AI verifies a storm date is "good" before the alert sends.

**The product flow Nick described:**
1. **Login** — company username/password (roofing companies who work with Nick are grandfathered into a free subscription).
2. **Profile** — name, phone; **radius**: pick state + travel distance / areas of interest.
3. **Submit → automated VERIFIED storm dates** to cell or email; team verifies "good" before sending.
4. **Historical search up to 6 years** — address-specific date of loss, roof age, best canvassing neighborhoods.
5. **Pinpoint** — type address + damage type + affected side (N/S/E/W) + approx hail size → best data for that address.
6. **Custom NOAA report download** — per-address verified weather report, one tap.
7. **Pre-loss / post-loss roof photos** via hi-res satellite imagery → "new damage after MM/DD/YYYY" → increase approvals.
8. Marketing claim Nick wants: **"95% accuracy proprietary technology."**
9. After **3 months** of tracking claims → publish approval-vs-denial data on the site.

## Split: buildable NOW (data we already have) vs gated on an imagery vendor

**Buildable now — no new vendor (uses NWS/SPC/MESH/Xweather/Visual Crossing already wired):**
- ★ **Profile + radius/state alert-subscription** — extends the roster; the "login → profile → submit → alerts" flow. (Auth = the company-gate already on the pre-public list.)
- ★ **Historical weather search up to 6 years, address-specific** — Visual Crossing serves multi-year history; this is the "date of loss" finder without any imagery. Big, and free of imagery cost.
- ★ **Address + damage-type + side + hail-size → best-data pinpoint** — pure weather-data query.
- **Custom per-address NOAA report download** — we already build claim packets; generalize to any typed address.
- **Real-time verified alerts to phone/email** — Twilio (already flagged pre-public) + the GO/HOLD/REJECT verify step = the "we verify before sending."

**Gated on a hi-res dated-imagery vendor (the crown jewel — pre/post-loss + roof age):**
- **Roof age** (Nick wants Nearmap) and **pre-loss vs post-loss change detection** ("new shingles missing after 03/16") fundamentally require sub-10cm *dated* aerial imagery. That imagery IS the expensive asset — there is no cheap API shortcut. Nick's read ("built for billion-dollar carriers") is correct.
- Vendors with the exact APIs: **Nearmap** (Roof Age Prediction API + Betterview roof-condition/change + historical imagery by date), **CAPE Analytics** (roof age from historical imagery + change detection), **EagleView** (per-report, moved cheaper in 2026 — reports from ~$10.99; added AI change detection). All are quote-based; Nearmap has no free tier (reported real-world packages have run ~$2–3k/yr — i.e. *not* carrier-scale money; affordable to absorb into a subscription).
- **Path:** get ONE quote (Nearmap Roof Age API + historical tile access, or CAPE). The adapter is pre-built to auto-enable on an env key exactly like Xweather — the moment a key exists, roof-age + pre/post imagery light up. YourCo/StormVerified absorbs the imagery cost and spreads it across subscribers (same token-economics model as the rest of the OS).

## ⚠️ Two discipline flags before these go public
- **"95% accuracy proprietary technology"** — cannot publish a specific accuracy % we haven't measured (same rule as the approval-rate: market the *real tracked* number). Nick's own "after 3 months of testing" is exactly when that number becomes real and defensible. Until then, don't put 95% on the site.
- **Legal (already on the pre-public list, now higher stakes):** marketing to attorneys/PAs, "verified claim support," reselling weather + imagery data, and the "grandfathered free subscription" all need counsel before public launch.
