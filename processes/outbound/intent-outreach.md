# Intent outreach — the Sadie → David → Reilly handoff (+ intent-aware copy)

> Wires Sadie's intent signals into the cold pipeline so Reilly's first touch **references the actual research Sadie found**. Cold, per `decisions/2026-06-15_prospect-data-architecture.md` — these are intent-*qualified* but still cold, so they run their own Instantly campaign and promote to the CRM on reply. Owners: **Sadie** (find) · **David** (dedup/CRM) · **Reilly** (stage + run) · **Michelle** (the copy).

## The flow
```
Sadie listens → surfaces an intent lead + the signal
   → David dedup (CRM check: are we already a relationship? if yes, NOT cold — route warm/human)
   → Reilly stages the fresh ones into the intent-themed Instantly campaign (cold, paused)
   → Michelle's copy opens by referencing the trigger (merge vars below)
   → reply → promote into the CRM (David), per the prospect-data architecture
```
David's dedup is automatic in `runtime/sourcing.py` (`_crm_index()`): any lead already in the CRM is pulled out and flagged `◆ already a relationship` — it never gets cold-contacted.

## Sadie's output (the handoff schema)
Sadie hands off a JSON list. One object per intent lead:
```json
[{
  "name": "YourCo Landscaping",
  "domain": "yourcoland.com",          // optional — enrich if missing
  "email": "owner@yourcoland.com",     // optional — no email → can't email-sequence (Enrich first / SMS)
  "phone": "",
  "intent": {
    "signal": "posted on r/landscaping: \"we keep missing calls during installs\"",
    "url": "https://reddit.com/r/landscaping/...",
    "platform": "reddit"             // reddit / x / linkedin / facebook / job-board / forum
  },
  "source": ["sadie"]
}]
```

## How Sadie produces the JSON (free + compliant sources, many verticals)
`runtime/intent_collect.py` pulls signals from sources that are **free *and* allowed** (per `agents/rafi/social-platform-scraping-assessment.md`) and writes the schema above — no scraping of X/Meta/LinkedIn (those are paid-API / licensed-data only). **Verticals are configured in `runtime/intent_verticals.json`** (14 seeded; add freely), each with YouTube queries + pain keywords + Google-Alert phrases.
```bash
python3 runtime/intent_collect.py --list-verticals
# one vertical — YouTube COMMENTS (real owners venting, keyword-filtered) + any configured RSS:
python3 runtime/intent_collect.py --vertical "Landscaping" --comments      # → intent-landscaping.json
# sweep EVERY vertical → one intent-<vertical>.json each:
python3 runtime/intent_collect.py --all-verticals --comments
```
- **`--comments` is the important flag:** it pulls the *comments* on the matched videos (real people in their own words) instead of the videos themselves (topic/market radar). Use it for lead-finding.
- **Sources per vertical (all free + compliant):** YouTube comments + **Google News RSS** (auto, no key) + **Bluesky** (app-password login) + **Mastodon** (hashtag RSS) + **Yelp** (key; business+rating) + **Google Alerts / forum RSS** (paste feed URLs). No-config verticals still get YouTube + Google News + Bluesky automatically.
- **Google Alerts RSS:** set a Google Alert per `alert_phrases` → paste the feed URL into that vertical's `rss_feeds` → joins the sweep. Setup: `runtime/intent-alerts-setup.md`.
- Plus **WebSearch** in a Cowork session (Sadie's live open-web capability) — she appends those hits to the same JSON by hand. All sources emit the same `intent` schema (+ a `vertical` tag for routing).

Each `intent-<vertical>.json` → its own `Intent — <vertical>` Instantly campaign (own copy referencing the trigger). One config, N industries.

## Reilly stages it (one command)
```bash
# create the campaign once (Michelle's intent copy loaded), then:
python3 runtime/sourcing.py --sadie-json sadie-intent.json --campaign "Intent — Landscaping" --commit
```
The `intent` block becomes Instantly **custom variables** on each lead:
`{{yourco_intent}}` · `{{yourco_intent_platform}}` · `{{yourco_intent_url}}` (+ `{{yourco_source}}` = `sadie`).

## The intent-aware first touch (Michelle owns)
Sadie-sourced leads get their **own** sequence — the opener references the trigger instead of a generic hook. The merge var carries the signal:

> **Subject:** `{{company}} + missed calls`
> Hi {{first_name|there}}, I came across {{yourco_intent}} — that's exactly the kind of thing we fix.
> I built a 60-second demo of an AI front desk for {{company}} that catches those calls 24/7: {{demo_url}}
> Worth a look? — the Founder

**Copy rules (Michelle, applying `brand/writing-rules.md`):**
- **Reference only PUBLIC signals, and naturally** — acknowledge the post the way a helpful peer would, never "I've been monitoring your activity." Disclose honestly; no creepy specificity.
- **Help-first, demo-led** — the trigger earns the open; the demo does the convincing. Never pitch before helping.
- **One reference, then move on** — cite the signal once in the opener; the rest of the sequence is the standard proof-led arc.
- If `{{yourco_intent}}` is empty (signal didn't carry), the copy falls back to the generic opener — never invent a signal.

## Guards (unchanged)
- Cold = Instantly, never the CRM until reply. David's dedup protects existing relationships.
- Drafts/staging only; **nothing sends** until the launch gate (OtherVenture + Rafi + warmup + batch approval).
- Platform compliance for *collecting* the signal: `agents/rafi/social-platform-scraping-assessment.md`.
