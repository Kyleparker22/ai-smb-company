# Decision — paid advertising stance (deferred)

**Date:** 2026-06-12 · **Status:** deferred (not now; revisit post-funnel-proof) · **Owner:** the Founder + Reilly

## The call
**No paid ads (Facebook/Instagram/YouTube/etc.) yet.** Ads amplify a converting funnel; they don't create one. YourCo is pre-launch with zero conversion data and a high-trust, considered B2B sale — the worst fit for cold ad traffic. Spending now = paying to learn what a few organic conversions teach for free.

## Why not now
- **No conversion math** — no cost-per-lead, demo→call rate, close rate, or LTV. Ads before these numbers is guesswork at cost.
- **Trust sale, low-trust channel** — cold feed traffic is the lowest-intent audience for a $4k+/mo considered purchase. Outbound + partnerships borrow/build trust; ads don't.
- **Nothing live to point at** (OtherVenture) and the reliability moat doesn't fit a 15-sec creative. The assets that sell it (Instant Employee, demos) are interactive.
- **Solo, finite cash** — ads demand budget + constant optimization + a live destination.

## When/how ads earn their place (the sequence)
1. **Retargeting** visitors who already touched the Instant Employee / ROI calculator — warm, cheap, high-intent. The first ad dollar.
2. **YouTube as proof + SEO** — host demos + build-in-public; vertical pre-roll. Content-led, not pure paid.
3. **Vertical lead ads led by the demo** — "watch a 60-sec AI front desk for your [vertical]." The Instant Employee is a strong ad *because* it's proof. Only after a proven offer + case studies.

## The precondition test (don't spend until all are true)
- [ ] A proven funnel (outbound/partnerships/content converting).
- [ ] Known cost-per-qualified-lead + demo→call + close rate + LTV.
- [ ] ≥ a few reference clients / case studies to lead the creative with.
- [ ] Launched (OtherVenture cleared) with a live destination + retargeting pixel in place.

## What we do now instead
Prove the funnel with **outbound + partnerships + content** (cheap, trust-building, generates the conversion data ads would need). Build the **ad-ready creative** (Instant Employee clips, demo videos) as a byproduct of the content engine — so when the preconditions hit, ads are a switch-flip, not a cold start. Ads are a *scaling* tool, deployed on the channel that's already converting.

## Market update (2026-07-29 — filed for the eventual ads-on decision; stance UNCHANGED)
From the Isenberg×Cody Schneider marketing-agents episode (`decisions/2026-07-05_tool-triage.md` §Addendum 07-29): **Meta's Andromeda algorithm** now targets on *creative content* (interest targeting is dead — the ad's text/imagery/landing page determines who sees it), and practitioners are running fully agent-operated ad loops (research → creative → publish via Marketing API writes-only → kill losers → learn) that replace the $10k+/mo agency cost structure this stance assumed. Two implications for later: (a) the eventual ads-on math is **cheaper and more automatable** than when this was written — creative volume is now the lever, and yourco's stack (Higgsfield + `brand/DESIGN.md` + eval layer) is built for exactly that; (b) his blueprint (incl. the entropy problem — unattended loops decay by day 3 — and the ban-avoidance rule: **API for writes only, never bulk reads**) is the build-spec appendix to the Advertising Ops pattern below. Preconditions above still gate everything; nothing turns on pre-launch, pre-conversion-data.

## The creative engine (parked until ads-on)
When the preconditions clear and ads turn on, the creative engine is the **"Advertising Ops" media-buyer pattern** (a Claude Code skill, eval'd 2026-06-14): scrape **long-running + still-active** competitor ads from the public Meta Ad Library (Apify), tear down the winners (sample frames + transcript → hook/structure/CTA), brief one CTA, then generate variations via **Higgsfield** (already Reed's locked stack). Don't install it now — no ads = no job for the generate step, and Apify scraping wants a Rafi glance first. **But its core method is usable today, channel-free** — see `processes/content/content-engine.md` and `agents/brett/competitive-watch.md`: a competitor ad that started months ago and is *still running* is market-validated, so the Meta Ad Library is a free swipe file of proven messaging for Katie's copy and Reilly's outreach right now.

## Trip-wire
- **Review:** 2026-12-01
- **Overturn if:** the precondition test above goes all-true — a proven converting funnel, known cost-per-qualified-lead + demo→call + close rate + LTV, a few reference clients to lead the creative with, and a launched destination with a retargeting pixel in place.
- **Check:** `signedClients >= 3 and OtherVentureCleared`
- **Check covers:** the two machine-visible preconditions only (reference clients · launched). Cost-per-lead, close rate and LTV are instrumented nowhere yet, so a firing check is a prompt to re-read the full list — never a green light on its own.
