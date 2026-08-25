# 2026-06-15 — Sadie intent pipeline: wired handoff, intent-aware copy, compliant collection

## Decisions (three, from the Founder)

### 1. Reilly's first touch references the research Sadie found
Sadie-sourced leads get **their own** Instantly campaign whose opener references the actual trigger ("I came across {{yourco_intent}} — that's exactly what we fix"). Mechanically: Sadie's intent block (`signal` / `url` / `platform`) rides into Instantly as **custom variables** (`{{yourco_intent}}`, `{{yourco_intent_platform}}`, `{{yourco_intent_url}}`); **Michelle** writes the intent-aware sequence around them. Copy rules: reference only *public* signals, naturally and once, help-first, disclose honestly, fall back to the generic opener if the signal didn't carry (never invent one). Spec: `processes/outbound/intent-outreach.md`.

### 2. The Sadie → David → Reilly handoff is wired
`runtime/sourcing.py` now takes `--sadie-json` (intent leads in the common schema + an `intent` block). Two guards added:
- **David's CRM-dedup** (`_crm_index()`): any lead already a relationship is pulled out and flagged `◆ already in CRM` — **never cold-contacted**. Cold pipeline only touches net-new.
- **Intent carry**: the signal survives into Instantly as merge vars (above).
Flow: Sadie finds → David dedup → Reilly stages cold into the intent campaign (paused) → reply → promote to CRM. Consistent with `2026-06-15_prospect-data-architecture.md` (intent ≠ warm; cold until reply).

### 3. Collection is compliant by design — buy licensed access, don't scrape
Per Rafi's assessment (`agents/rafi/social-platform-scraping-assessment.md`): every target platform prohibits raw scraping in ToS, so Sadie uses **official paid APIs + licensed data/listening vendors**, not scrapers. **LinkedIn + Facebook are never automated** (manual Sales Navigator + licensed B2B data; counsel sign-off before any scale). Public ≠ unregulated — personal-data hygiene (GDPR/CCPA legitimate-interest, public-only, opt-out) + the existing send gate apply. This is the on-brand call: yourco sells reliability + compliance; reckless intake would contradict the moat.

## Why this shape
- **Intent improves targeting + conversion, not lead temperature** — so it belongs in the cold pipeline, just with sharper copy and its own campaign.
- **David's dedup is the safety rail** — it stops us cold-emailing an existing client/warm relationship that Sadie happens to re-surface.
- **Compliance is a feature, not a tax** — buying licensed access is cheaper than the legal/brand downside and is exactly what we tell clients to do.

## Engagement autonomy — fast-approve (decided 2026-06-15)
the Founder asked whether Sadie could reply to comments with no approval. **Decision: no — fast-approve instead.** Sadie auto-drafts every reply and posts it to `#yourco-sadie`; the Founder one-tap approves, then it posts. Rationale: (1) blanket auto-posting contradicts the moat ("a human approves anything customer-facing" — we *sell* this); (2) most platforms' ToS **ban automated posting** (Reddit especially) — building it would violate the same posture Rafi just set; (3) one screenshotted bad reply or a bot-ban costs more than the leads. **Graduated path:** auto-post may later unlock on a permissive channel (Bluesky/Mastodon) once Sadie's drafts prove aligned — with disclosure + rate limits + templates + a kill switch; never on Reddit/YouTube. Same earn-it model as Melanie. (Note: posting connectors per platform are a *future* build — collectors are read-only today; until then, approved replies post by hand.)

## Tiered rollout (Rafi)
- **Now (no new contracts):** WebSearch open-web + YouTube Data API + human-picked public threads → the wired pipeline.
- **Next (paid):** X Basic API (~$200/mo) · Reddit Data API agreement.
- **Later (licensed data only, counsel sign-off):** LinkedIn · Meta.

## the Founder's open items
Budget for paid APIs · pick a licensed B2B-data vendor for LinkedIn-class data · counsel review before LinkedIn/Meta at scale · Rafi drafts the legitimate-interest basis + opt-out process. Nothing sends until the launch gate regardless.
