# Google Alerts → Sadie's intent feeds (paste-and-go)

> **Status: SETUP DONE — Google Alerts feeds are LIVE.** Evidence: `loops/sadie/` produced `2026-08-21_intent-sweep.md`. Kept for adding a new alert or re-keying.

> Google Alerts is the highest-signal **free** intent source — it indexes blogs, forums, news, and Q&A that YouTube/News miss. Each alert can deliver an **RSS feed**; paste that feed URL into the matching vertical's `rss_feeds` in `runtime/intent_verticals.json` and it joins the sweep automatically. (Google **News** RSS is already auto-wired, no setup — Alerts is broader coverage on top.)

## Setup (once per phrase, ~30 sec each)
1. Go to **google.com/alerts** (signed into a Google account).
2. Paste a phrase from the list below into the box.
3. Click **Show options** → set:
   - **How often:** As-it-happens (or At most once a day)
   - **Sources:** Automatic
   - **Deliver to:** **RSS feed**  ← *this is the important one*
4. Click **Create Alert**. A small **RSS icon** appears next to the alert — **right-click it → Copy link**.
5. Paste that feed URL into the vertical's `rss_feeds` array in `runtime/intent_verticals.json`.

Then it's automatic: `python3 runtime/intent_collect.py --vertical "Landscaping" --comments` (or `--all-verticals`) pulls those feeds, keyword-filtered, into the intent JSON.

## The phrases (grouped by vertical — these match the config)
**Landscaping:** `missed calls landscaping` · `landscaping answering service` · `landscaping too many leads`
**Hardscaping:** `hardscaping leads` · `hardscape contractor answering service`
**HVAC:** `HVAC missed calls` · `HVAC answering service` · `HVAC after hours calls`
**Plumbing:** `plumber missed calls` · `plumbing answering service`
**Roofing:** `roofing missed calls` · `roofing storm leads` · `roofing answering service`
**Electrical:** `electrician missed calls` · `electrical answering service`
**Dental:** `dental practice missed calls` · `dental office answering service` · `dental no-shows`
**Law Firms:** `law firm missed calls` · `law firm intake service` · `attorney answering service`
**Med Spa:** `med spa missed calls` · `med spa booking` · `med spa no-shows`
**Auto Repair:** `auto repair missed calls` · `auto shop answering service`
**Real Estate:** `realtor missed calls` · `real estate lead follow up` · `real estate answering service`
**Veterinary:** `veterinary clinic missed calls` · `vet answering service`
**Cleaning Services:** `cleaning business missed calls` · `maid service answering service`
**Pest Control:** `pest control missed calls` · `pest control answering service`

## Where each feed URL goes
In `runtime/intent_verticals.json`, find the vertical and fill its `rss_feeds`:
```json
{ "vertical": "Landscaping", ..., "rss_feeds": [
    "https://www.google.com/alerts/feeds/00000000000000000000/1111111111111111111",
    "https://www.google.com/alerts/feeds/00000000000000000000/2222222222222222222"
] }
```

## Tips
- **Quote multi-word phrases** in the alert box for tighter matches (`"missed calls landscaping"`).
- Start with your **beachhead** (Landscaping + Hardscaping) — 5 alerts — before doing all 14.
- The alert RSS feeds are tied to your Google account but contain no secret; they're fine to commit in the config (they're just feed URLs). The YouTube **API key** stays in the gitignored `.youtube.env`.
