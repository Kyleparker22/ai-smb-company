# Setup — multi-source sourcing pipeline (Reilly)

> **Status: BUILT, NOT WIRED TO A LOOP.** `runtime/sourcing.py` exists and is referenced by 0 loop prompts — it runs by hand only. Treat the pipeline it describes as available, not automatic.

> Pull from Outscraper + Instantly SuperSearch + Vibe, dedupe, **stage into an Instantly campaign** (the cold system of record), then **promote warm replies into the CRM**. Sourcing only — no outreach. Implements `decisions/2026-06-07_multi-source-sourcing.md` + `decisions/2026-06-15_prospect-data-architecture.md`. Code: `runtime/outscraper.py`, `runtime/instantly.py` (supersearch + warm_replies), `runtime/sourcing.py`, `runtime/promote.py`.

## The architecture (where prospects live)
**Cold lives in Instantly; warm graduates to the CRM.** Sourced cold leads stage into an Instantly campaign — never the CRM. A lead enters the CRM only when it replies with positive intent (`promote.py`). The CRM stays the relationship system of record; Instantly is the cold/outbound one. Full rationale: `decisions/2026-06-15_prospect-data-architecture.md`.

**Flow:** source → dedupe → Instantly campaign (cold) → reply → promote → CRM (real lead) → discovery → close.

## Keys (yours — never committed; `*.env` is gitignored)
- **Outscraper:** `outscraper.com → Profile → API key` → paste into `runtime/.outscraper.env`.
- **Instantly:** already in `runtime/.instantly.env` (SuperSearch uses the same key; needs a plan with SuperSearch API access).
- **Vibe:** the Vibe MCP (connected in Cowork) — no key file; called by an agent, not this script.

## How to run — step 0: create the campaign (once per vertical)
Create the campaign loaded with Reilly's paused 4-touch sequence — via the connector (no UI needed):
```bash
python3 runtime/instantly.py --create "Landscaping ST"            # dry run — preview steps + subjects
python3 runtime/instantly.py --create "Landscaping ST" --commit   # create it — DRAFT/PAUSED, never activated
```
It parses `processes/outbound/sequence-copy.md` (Reilly's copy, Instantly-native `{{var|fallback}}` syntax) into the 4 email steps (days 0/3/6/10) and creates the campaign in draft. It can never send — the connector has no activate path. (You can still create it in the UI instead; the steps below stage into whichever exists.)

## How to run — step 1: source → Instantly (cold)
With the campaign created (above), stage leads into it:
```bash
# Outscraper only — dry run first (shows what would stage; no-email records reported separately)
python3 runtime/sourcing.py --outscraper "landscaping, Yourtown" --limit 10 --campaign "Landscaping ST"
# stage for real into Instantly (staging only — never sends)
python3 runtime/sourcing.py --outscraper "landscaping, Yourtown" --limit 10 --campaign "Landscaping ST" --commit
```
Omit `--campaign` to just preview the deduped list (no staging).
**Add Instantly SuperSearch:** append `--instantly-search "landscaping companies ST"` (skips gracefully if the API isn't on your plan).
**Add Vibe** (an MCP, fed in): in Cowork, have Reilly run the Vibe tool, save results normalized (`[{name,domain,phone,email,...}]`) to JSON, then append `--vibe-json /path/to/vibe.json`.

## How to run — step 2: promote warm replies → CRM
Once a campaign has replies, graduate the warm ones into the CRM:
```bash
python3 runtime/promote.py --campaign "Landscaping ST"            # dry run — who would graduate
python3 runtime/promote.py --campaign "Landscaping ST" --vertical "Landscaping" --commit
```

## What it does
**sourcing.py** normalizes every source to `{name, domain, phone, email, address, owner, source[]}`, dedupes (domain → phone → name), and **stages email-bearing records into the Instantly campaign** (custom vars carry the `source[]` tags + phone). Records with **no email** are reported separately — they need Enrich first, or run as SMS/call-channel. A prospect in ≥2 sources is high-confidence; **"only in Outscraper" = a weak-footprint local SMB = a positive ICP signal for trades.**
**promote.py** reads Instantly warm replies (positive interest / reply), de-dupes against the CRM, and writes each as a company ("warm — replied") + contact + `prospect` deal (owner Reilly, next action "Book a discovery call"). This is the only path cold leads enter the CRM.

## Guards
- **Dry-run by default** — `--commit` required (to stage into Instantly, and to write the CRM). Prints the plan first.
- **Staging ≠ sending.** Sourcing stages into Instantly but never starts/sends a campaign; sending stays gated (OtherVenture + warmup + Polo per-vertical pricing + batch approval), one human action in Instantly.
- **Costs money** — Outscraper bills per request; Vibe per credit. Confirm before large pulls.
- **promote.py reads Instantly only** — never sends, never mutates Instantly state.
- **Compliance:** Outscraper = public Google-Maps business listings via a managed service (name/address/phone/site) — lower-risk than personal-data scraping, and approved in the decision. Confirm Rafi's posture before a standing/automated cadence.
- **Beachhead:** point it at landscaping/hardscaping first (per `loops/advisor/2026-06-14_gtm-beachhead.md`) — also where Outscraper is strongest.
