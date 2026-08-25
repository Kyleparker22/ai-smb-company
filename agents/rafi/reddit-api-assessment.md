# Rafi — compliance assessment: Reddit API for Sadie's intent listening

> **Status: PRELIMINARY.** Based on Reddit's publicly documented Data API Terms + Developer Terms (stable since the 2023 overhaul). The live policy text could not be fetched at assessment time (tooling outage) — **verify against the current text before any binding reliance, and route to counsel before agreeing to terms on YourCo's behalf.** Not legal advice.
> Date: 2026-06-11 · Trigger: the Founder hit Reddit's mandatory "Responsible Builder Policy" acknowledgment when creating an API app for `agents/sadie/listen.py`.

## The question
Can YourCo use the Reddit API for Sadie — i.e. **read public posts → feed them to an LLM to summarize buyer intent → for commercial lead-gen → low volume → humans do any outreach** — under Reddit's free tier, or does it require a commercial agreement?

## What Reddit's terms require (three relevant pillars)
1. **Commercial use is gated.** Reddit's free API access is scoped to *non-commercial* use (plus moderation/accessibility). Commercial use — explicitly including generating business value/leads — falls under Reddit's paid/enterprise **commercial data agreement**, which you arrange directly with Reddit. Free-tier rate limits (~100 queries/min authenticated) are for the non-commercial lane.
2. **AI/LLM use of content is restricted.** The centerpiece of Reddit's 2023 changes: using Reddit content to train, fine-tune, or otherwise process with AI/ML models is **restricted and requires a separate agreement.** Reddit monetizes this through licensing deals (Google, OpenAI). "We only summarize, we don't train" is a distinction Reddit's terms do **not** cleanly grant — the restriction is written broadly around *using content with AI*.
3. **The Responsible Builder Policy gate** (what the Founder hit) is the acknowledgment that you'll operate within all of the above — rate limits, no redistribution, honor deletions, no circumvention, and the commercial/AI restrictions.

## How YourCo's intended use maps
| Our use | Reddit's stance |
|---|---|
| Commercial lead-generation | Commercial → **outside free tier** |
| LLM reads + summarizes post content | AI/LLM use → **restricted, needs agreement** |
| Low volume, human outreach | Reduces *practical* risk; does **not** change the terms |

On **two independent grounds** (commercial purpose **and** LLM processing), our intended use sits **outside Reddit's free, non-commercial API access.**

## Verdict
**Do not accept the developer terms for this use, and do not wire the Reddit API for Sadie as designed.** Proceeding would put YourCo — a company whose moat *is* compliance + trust — in violation of a platform's data terms to find leads. The reputational and account-risk downside outweighs the modest pre-launch benefit, and it contradicts the brand we sell.

## The compliant paths
- **A. Reddit commercial data agreement.** Legitimate, but paid + overhead + likely overkill for our volume pre-launch. Revisit only if Reddit lead-gen becomes strategically important.
- **B. Don't use the Reddit API.** Keep Sadie on **open-web market intelligence via WebSearch** — reading public search results is a different, defensible research posture (not Reddit's API, not systematic scraping). Acceptable, with the guardrail: **no systematic scraping of Reddit (API or HTML) to build commercial lead lists** without an agreement.
- **C. Human-in-the-loop manual.** the Founder (a human) browses Reddit normally and brings interesting threads to Sadie for help-first draft replies. No API, no automated content ingestion — ordinary human use of the site.

## Recommendation
**Path B + C.** Park `agents/sadie/listen.py` (built, ready, not used). Keep Sadie producing market/competitive intel via WebSearch. If the Founder spots a specific thread worth engaging, hand it to Sadie manually for a help-first draft. Re-open the Reddit API question only if/when a commercial agreement is worth it.

## Conditions if we ever proceed (Path A)
- A signed Reddit commercial data agreement covering commercial + AI use.
- Documented rate-limit compliance, deletion-honoring, no-redistribution.
- Counsel sign-off on the agreement.

## Caveats
- Preliminary; live policy text not verified at assessment time — confirm current wording.
- Not legal advice; counsel reviews before YourCo agrees to any platform terms.
- X (Twitter): same posture, worse economics (paid API, stricter) — **deferred indefinitely.**

— Rafi, YourCo Compliance
