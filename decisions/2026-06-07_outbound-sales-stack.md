# 2026-06-07 — Outbound sales stack & agent architecture

## Decision
Build outbound as **two internal digital employees** — **Reilly** (Sales Agent: source → research → multi-touch copy → human-approved send → feedback) and **Reed** (Content/Demo Agent: vertical → credible reusable demo) — on a stack of **Vibe Prospecting (Explorium MCP) for sourcing+enrichment, Gemini Flash for per-company research, a strong model for copy, and Instantly for sending**. Drop Apollo. Keep Clay as a documented fallback.

## Context
YourCo is pre-pipeline (per the 2026-06-07 sales/finance loops). The highest-leverage move is generating first qualified conversations. Apollo was cancelled 2026-06-06. the Founder wants an agent that takes a vertical and returns researched, personalized, outcome-based multi-touch cold campaigns, plus an agent that produces demo videos showing YourCo's AI employees at work.

## Options considered
- **Apollo (all-in-one):** cancelled; data has a stale/over-used reputation (bounce risk); redundant with Vibe. Rejected.
- **Clay (waterfall enrichment):** best match rates (~85%+) but visual-workflow, less agent-native, ~$149/mo. Kept as **fallback** if Vibe match rates disappoint.
- **Vibe Prospecting (Explorium):** MCP-native (drivable by the agent directly), 800M+ profiles / 50+ sources, collapses source+enrich into one tool. **Chosen** as the data layer.
- **Instantly for sending:** API + webhooks (observability/feedback), unlimited inboxes at flat cost (scales into client tenants), native warmup + deliverability. **Chosen.**
- **One monolithic agent vs staged pipeline:** monolith is unreliable/unobservable — can't tell which step failed. **Chosen: one named employee, 4 internal stages with per-stage eval gates.** The staged, gated pipeline *is* the moat (reliability/eval/observability) and the sellable template.
- **Demo as a Reilly stage vs separate employee:** video production is a distinct tool stack + eval bar; bolting it into the sales pipeline bloats it. **Chosen: separate employee (Reed)** that supplies assets to Reilly.
- **Personalized video at scale now vs reusable-per-vertical first:** reusable first to prove lift before paying for personalization. **Chosen: reusable first.**

## Why
- **Agent-native beats all-in-one** for a solo founder dogfooding: fewer tools, driven conversationally, less glue code.
- **Staged + gated = the moat.** Each stage independently testable/swappable/observable — exactly what no-code operators can't deliver, and what YourCo sells.
- **Trust is the moat; demos build trust.** Showing a real agent working (Reed) is the highest-credibility outbound asset.
- **Hard human-must-approve on external send** protects domain reputation and compliance, consistent with Atlas's approval model.
- **Token economics on-brand:** Flash for volume research, strong model only where quality converts.

## Reversibility
- **Easily reversible:** swap Vibe→Clay if match rates/quality disappoint (fallback already chosen); swap media vendors for Reed.
- **Harder to reverse:** sending-domain reputation — get the separate domain + warmup right before any send. Don't send from `yourco.com` primary.
- **Revisit if:** Vibe data quality < usable, deliverability can't be kept healthy, or the staged pipeline proves overkill for volume (unlikely at this stage).

## Prerequisites flagged
- Separate sending domain (re-provision `mail.yourco.com`) + SPF/DKIM/DMARC + warmup + one-click unsubscribe **before** Reilly stage 4 goes live (ties to the 2026-06-07 briefing's deleted-sending-domain finding).
- Provision `contact@yourco.example.com` and `contact@yourco.example.com` (non-blocking for v0).

## Amendment 2026-06-07 (same session) — stack roadmap + coverage test
Researched three tools (Vibe, Leadbay, Clay) to validate the original choice. Findings reinforce Vibe as v0 and add explicit roadmap layers:

**Tool stack roadmap:**
- **v0 (now):** Vibe Prospecting (MCP-native source+enrich) → Gemini Flash research → strong-model copy → Instantly send. Locked above.
- **v1 (~Q4 2026, after first 3–5 closed deals):** add **Leadbay** (YC F25, $4.3M seed May 2026; $145/seat/mo; "no usage, no bill" pricing) as a **predictive ICP scoring layer on top of Vibe-sourced lists.** Leadbay explicitly targets SMB construction/services — strong fit for landscaping/hardscaping and the adjacent verticals. Requires won/lost training data YourCo doesn't yet have, so it's gated on pipeline maturity.
- **v2 (only if needed):** **Clay** for multi-step enrichment workflows Vibe can't express. Clay's March 2026 pricing update cut data costs 50–90%; Launch tier is $185/mo with 2,500 data credits + 15,000 actions; integrates natively with Instantly. Stays as documented fallback per the original decision; only promoted to v2 if a real workflow gap surfaces.

**New pre-campaign gate added to Reilly's 02_build.md:** **Vibe coverage test per vertical/geo before committing Vibe-only sourcing.** Run a representative sample query (e.g., "landscaping companies, Tampa–St. Pete–Clearwater, 10–50 employees"). If hit count is materially below market size, supplement Vibe with manual sourcing (Google Maps + LinkedIn) for that vertical, and accelerate the Leadbay timeline if the pattern repeats across verticals.

Sources reviewed: Vibe Prospecting site + Explorium MCP docs + Capterra 2026 listing; Clay.com 2026 pricing breakdowns (Warmly, Cleanlist, Landbase); Leadbay product page + Coldiq review + FinSMEs funding coverage.

## Amendment 2026-06-07 (later same session) — SMS as channel 2
Adding **SMS to Reilly's outbound stack** via **Instantly Hyper CRM tier** ($97/mo). Multi-channel email + SMS produces 30-40% higher response rates per Instantly's own data; SMS specifically suits owner-operator trade/services verticals where buyers are mobile, on-site, and text-native.

### Why Instantly Hyper CRM (not JustCall / Salesmsg / Aloware / Twilio)
- **Single tool** — SMS steps interleave into the same multi-touch sequences as email; no separate vendor, login, billing, or MCP/API to wire.
- **10DLC registration shepherded in-product** rather than user-managed.
- **No per-seat overhead** — JustCall has 2-user minimum; Salesmsg is credit-based with separate billing; Aloware is per-seat. For solo founder, Instantly's bundled pricing wins.
- **Reilly's send-layer architecture unchanged** — adding SMS doesn't restructure her pipeline, just adds steps inside an existing tool.

### Compliance gates (non-negotiable, hard pre-send requirements)
- **10DLC brand + campaign registration complete** (carriers block unregistered A2P traffic; takes 1–4 weeks)
- **STOP opt-out keyword** in every message
- **Sender identification** ("the Founder at YourCo —") in every message
- **DNC list scrub** before every batch
- **FTSA (Florida Telephone Solicitation Act) legal review** before first send to FL numbers — Florida is high-litigation; B2B carve-out is narrower when recipient phone is a mobile (almost always true for landscaping owners). Ray reviews when Ray is built; until then, manual review with outside counsel.

### Per-vertical channel selection
Channel selection joins pricing as a Polo per-vertical decision. Each `/pricing/v0/<vertical>.md` now carries a **Channels** section. Verticals fit:
- **SMS fits:** landscaping, roofing, hardscaping, real-estate brokerages, plumbing/HVAC (owner-operator mobile trade/services)
- **SMS does NOT fit:** law firms, wealth management, insurance / adjusting (formal-communication norms; would clash with executive-trust positioning)

### Suggested landscaping cadence (6 touches over 3 weeks)
Day 1 email → Day 3 SMS → Day 7 email → Day 10 SMS → Day 14 email → Day 21 SMS break-up.

### Cost impact
Reilly's Instantly tier moves from email-only (~$37–97/mo) to **Hyper CRM $97/mo flat.**

### Reversibility
- Reversible: drop the Hyper CRM tier and revert to email-only.
- Harder to reverse: 10DLC brand registration ties to your sending domain — pick the right domain (`mail.yourco.com`) once.
- Revisit if: FTSA risk in FL produces enforcement action; SMS deliverability craters; Instantly's SMS tier proves underbuilt.

Full standalone decision doc: `decisions/2026-06-07_sms-channel-addition.md`.

Sources: Instantly SMS docs + Hyper CRM tier announcement; B2B SMS Strategy & Compliance 2026 (Prospeo); 10DLC requirements (Beconversive 2026); JustCall, Salesmsg, Aloware 2026 pricing.

## Amendment 2026-06-07 (later same session) — coverage test result + sourcing-tool pivot

The Vibe coverage test (built into Reilly's pre-campaign gates earlier this session) fired with real data. **National US landscaping/hardscaping query** ($1M+ revenue, 5+ employees) returned:

- **Vibe Prospecting (Explorium):** 25–50 prospects — catastrophically low; healthy database should return thousands
- **Instantly SuperSearch:** ~500 prospects — still under-counts (likely 10,000+ qualified US businesses exist) but 10–20× better than Vibe

### Why Vibe under-delivers for this vertical
Explorium's database is built around B2B SaaS / mid-market financial / tech-equipped companies. Local trade SMBs have weak digital footprints (no recent funding rounds, no tech stack signals, no LinkedIn-heavy presence) and are systematically under-represented. Instantly SuperSearch pulls from a waterfall of 7+ providers (160M–450M verified contacts) — broader cumulative coverage of SMB trades.

### Architectural pivot — sourcing tool becomes per-vertical
Sourcing-tool selection joins pricing and channels as a Polo per-vertical decision. Lands in `/pricing/v0/<vertical>.md` under "Primary sourcing."

| Vertical type | Primary source | Reason |
| --- | --- | --- |
| Trade/services SMB (landscaping, roofing, hardscaping, plumbing/HVAC) | **Instantly SuperSearch** | Wider net for weak-digital-footprint businesses |
| White-collar / knowledge work (law, wealth, insurance, professional services) | **Vibe Prospecting (Explorium)** | Where Explorium's data shines |
| Hyper-local single-metro (any vertical) | **Outscraper / Google Maps scraping (v1, pilot)** | True coverage for businesses both miss |
| Predictive (ICP-informed, any vertical) | **Leadbay (v1, after won/lost data exists)** | Existing v1 commitment |

### Vibe's revised role
**Vibe stays in the stack** as the enrichment + per-company research layer for *all* verticals, even where it's not primary sourcing. Once Reilly has a company name from Instantly (or Maps), Vibe's firmographics + technographics + funding signals + tech-stack data are still useful for the research-card phase. Vibe demotes from "stage 1 sourcing" to "stage 2 enrichment helper."

### v1 watchpoint — Outscraper pilot within 30 days
Even Instantly's 500 hits at national scope is uncomfortably thin for landscaping. Pilot **Outscraper** (~$50–100/mo for Google Maps scraping) within 30 days. Target: 5,000+ named landscaping businesses in Tampa Bay metro alone with public phone + website. If coverage holds, Outscraper becomes the primary sourcing layer for trade verticals and Instantly SuperSearch demotes to backup.

### Updated stack (v0 as of this amendment)
| Layer | Tool | Notes |
| --- | --- | --- |
| Sourcing (trades) | **Instantly SuperSearch** | New primary for trade verticals |
| Sourcing (knowledge work) | **Vibe Prospecting** | Still primary here |
| Enrichment (all verticals) | **Vibe Prospecting (MCP)** | Demoted from sourcing but kept |
| Research | Gemini Flash | Unchanged |
| Copy | Strong model | Unchanged |
| Send (email + SMS) | Instantly Hyper CRM tier | $97/mo, locked above |
| Activation-layer CRM | Instantly CRM | Bundled |
| Canonical CRM | `clients/_pipeline.md` | See `decisions/2026-06-07_crm-architecture.md` |

### What changes downstream
- Reilly's `02_build.md` updates sourcing-stage architecture
- Polo's `01_discovery.md` adds sourcing-tool selection to scope
- Landscaping pricing doc adds "Primary sourcing: Instantly SuperSearch" line
- New decision doc on CRM architecture (`_pipeline.md` vs Instantly CRM separation)
- Memory entry updated

Sources for this amendment: the Founder's hands-on coverage test (Vibe and Instantly SuperSearch) on 2026-06-07 — the empirical data overruling the Saturday assumption. The closed-loop watchdog gate worked exactly as designed.

## Amendment 2026-06-07 (later same session) — multi-source sourcing supersedes primary-source-per-vertical

the Founder's read after staring at the coverage data: single-tool sourcing leaves real coverage on the table. Each tool catches prospects the others miss. **New architecture: run all approved sources in parallel for each vertical, deduplicate, and merge into one canonical list.**

This **supersedes** the "primary sourcing per vertical" framing from the previous amendment. The previous primary-vs-fallback hierarchy is retired.

### The new sourcing pipeline (per vertical, per campaign)

```
            ┌────────────────────────────────────┐
            │  the Founder: vertical + filters          │
            └────────────┬───────────────────────┘
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
        Outscraper   Instantly    Vibe
        (Maps)       SuperSearch  (Explorium)
              │          │          │
              └──────────┼──────────┘
                         ▼
              Normalize → common schema
                         │
                         ▼
              Dedup (domain → phone → name+city)
                         │
                         ▼
              Merge + cross-source-match tag
                         │
                         ▼
              Canonical merged prospect list
              → enrichment → research → copy → send
```

### Step-by-step
1. **Parallel source.** Query each approved tool with vertical-appropriate filters.
2. **Normalize.** Map each tool's output into a common schema: `name, domain, phone, address, owner, employees, revenue, source[]`.
3. **Dedup** hierarchically:
   - **Tier 1:** match on `domain` (highest-confidence merge)
   - **Tier 2:** match on `phone` (still high-confidence; one digit difference = miss)
   - **Tier 3:** match on `(name normalized + city)` (lowest-confidence; flag for human review when collision count is high)
4. **Cross-source match tag.** Each record marked `single-source` / `two-source` / `all-three`:
   - **`all-three`** = highest confidence; lead the campaign with these
   - **`two-source`** = high confidence; mid-priority
   - **`single-source`** = wider coverage but higher unknown; lighter first touch
5. **Output** the merged list into Reilly's downstream pipeline.

### Per-vertical source set (Polo decides; lands in `/pricing/v0/<vertical>.md` under Sourcing)

| Vertical type | Source set | Reason |
| --- | --- | --- |
| Trade / services SMB (landscaping, roofing, hardscaping, plumbing/HVAC) | **Outscraper + Instantly + Vibe** | Default for trades; cross-source coverage is the point |
| White-collar / knowledge work (law, wealth, insurance, professional services) | **Vibe + Instantly** | Skip Outscraper — Google Maps weak for these verticals' decision-makers |
| Hyper-local single-metro (any vertical) | **Outscraper + Instantly** | Vibe optional if vertical is also tech-equipped |
| Predictive (v1 with Leadbay) | Vertical's base set **+ Leadbay scoring overlay** | Leadbay ranks, doesn't source |

### Why this wins
- **Maximum coverage** without committing to any single tool's blindspots
- **Cross-source match = confidence signal.** A name in all three is high-validation; a name in only Outscraper is by definition a weak-digital-footprint local SMB (the exact ICP for trades)
- **Tool redundancy.** If one tool's data quality dips, the other two carry coverage; if pricing/policy changes at one vendor, swap without restructuring the pipeline
- **Future-proofs the architecture.** Adding Leadbay (v1) or replacing a tool slots into the same parallel structure — just adds or swaps a branch

### Cost implications
Sourcing cost ~3× per batch. At first 1,000 prospects per vertical the cost is still trivial (Outscraper ~$1–3 + Instantly SuperSearch bundled in Hyper CRM + Vibe credits ~$5–15). Math works as long as merged-list yield materially exceeds any single tool's yield — which the Vibe vs Instantly gap (25–50 vs 500) already proves.

### Implementation note
Outscraper has a REST API but no MCP — Reilly calls it via HTTP. Instantly SuperSearch — programmatic query via Instantly API. Vibe — MCP-native. Three different invocation styles, abstracted behind the "source step" in Reilly's pipeline so downstream stages don't care.

### Pre-campaign gate update
The previous "Vibe coverage test" gate generalizes to a **source-set coverage test**: run the planned source set on a representative query, count the deduplicated merged total, escalate to the Founder if below market-size expectation. Each tool's individual yield gets reported too, for ongoing per-tool monitoring.

### Standalone decision doc
Full architecture write-up: `decisions/2026-06-07_multi-source-sourcing.md`.
