# Rafi — Social-platform data assessment: how Sadie can listen, compliantly

> **The ask (the Founder, 2026-06-15):** get Sadie able to pull intent signals from X, Reddit, Facebook, LinkedIn, and other platforms. **Rafi's finding:** the goal is reachable, but the compliant path is **buy licensed/official access — do not build scrapers that violate platform ToS.** That's both the lower-risk *and* the on-brand move: yourco sells reliability + compliance; we can't be reckless on our own intake. Extends `agents/rafi/reddit-api-assessment.md`.
>
> ⚠️ **Not legal advice.** This is an operational risk posture. Anything aggressive (especially LinkedIn) should be confirmed with counsel before launch.

## The core principle
**Scraping ≠ data access.** Almost every platform prohibits automated scraping in its ToS, but most offer a *licensed* path (official API, paid data tier, or a third-party vendor that already holds the rights). We use the licensed path. Public-on-a-page ≠ free-to-harvest: even public posts about an identifiable person are **personal data** (GDPR/CCPA) and the *outreach* is regulated separately (CAN-SPAM/CASL/TCPA — the existing send gate).

## Platform-by-platform
| Platform | Scraping (raw) | Compliant path | Cost / friction | Risk | Verdict for Sadie |
|---|---|---|---|---|---|
| **Reddit** | ✗ ToS-prohibited | **Reddit Data API** — but commercial + LLM use needs a **paid data-licensing agreement** (free tier is non-commercial) | Paid agreement; volume-priced | Med (contract + AI-use terms) | **Licensed API only.** Already assessed + parked pending the paid agreement. |
| **X (Twitter)** | ✗ ToS-prohibited | **Official X API** — filtered stream / search | Basic ~$200/mo (light), Pro ~$5k/mo, Enterprise custom | Med | **Paid API.** Start at Basic for listening; upgrade by volume. |
| **LinkedIn** | ✗✗ ToS-prohibited, **aggressively enforced** | **No scraping.** Sales Navigator (manual), official Partner/Marketing APIs (gated approval, no member scraping), or **licensed B2B-data vendors** | Sales Nav seat; vendor licensing | **High** — even *public*-data scraping (hiQ v. LinkedIn is *not* a green light) draws breach-of-contract action | **Manual + licensed data ONLY.** Highest-risk platform; never automate against it. |
| **Facebook / Meta** | ✗ ToS-prohibited | **Graph API** (only Pages/Groups you own or have permission for; public-post access heavily restricted post-2018) or **licensed social-listening vendors** | API limited; vendor cost | High | **Licensed listening vendor or own-page Graph API only.** No public scraping. |
| **TikTok** | ✗ ToS-prohibited (anti-scraping + bot-blocking) | **Research API** is real but **gated to vetted academic/research use, US/EU only — not commercial lead-gen**; Commercial Content API is ads-transparency, not comment search. So: **licensed social-listening vendor** (paid) that carries TikTok, or none | Vendor licensing; Research API won't approve our use | High | **No free compliant path.** Same bucket as X/Meta/LinkedIn — licensed listening vendor only; **do not scrape** comments/search. |
| **YouTube** | ✗ scraping prohibited | **YouTube Data API** (official, free quota) — search + comments | Free within quota | Low | **Official API — green-light.** Good for "people asking in comments." |
| **Forums / niche communities** | varies | Per-site: respect `robots.txt` + ToS; prefer RSS/official feeds | Low | Low–Med | **Per-site check**; RSS/feed where offered, else human-in-the-loop. |
| **Open web / Google** | ✗ scraping SERPs prohibited | **Assistant WebSearch** (already live) + official Custom Search API / licensed SERP vendors | Free–low | Low | **WebSearch — already Sadie's live capability.** No SERP scraping. |

## Cross-cutting compliance (applies to every channel)
- **Personal data (GDPR / CCPA / CPRA):** public ≠ unregulated. Document a **legitimate-interest basis** for B2B prospecting, keep it **public-only**, honor opt-out/deletion, and treat EU/UK contacts with extra care. Log source + basis per lead.
- **Outreach laws** (the *send*, not the listen): CAN-SPAM (US email), **CASL (Canada — opt-in)**, TCPA/FTSA (US SMS), ePrivacy (EU). Covered by the existing launch gate — Sadie's leads inherit it.
- **CFAA / breach-of-contract:** scraping behind a login or against an explicit ToS prohibition carries civil risk regardless of the public-data debate. We avoid it by using licensed access.
- **Brand / platform bans:** Sadie's **help-first, human-approved** model is itself a control — it keeps us inside community norms and off ban lists.

## Recommended posture (Rafi → the Founder)
1. **Buy compliant access; don't build scrapers.** Official paid APIs (X, YouTube, Reddit Data API) + licensed B2B-data / social-listening vendors. Cheaper than the legal/brand downside.
2. **LinkedIn + Facebook: never automate.** Manual Sales Navigator + licensed data for LinkedIn; own-page Graph API / licensed listening for Meta.
3. **Human-in-the-loop is the safe default today.** The assistant's **WebSearch** + the Founder/Sadie hand-picking public threads is fully usable *now*, with zero new contracts — start there.
4. **Personal-data hygiene** baked into the handoff: public-only, legitimate-interest logged, opt-out honored (feeds the same Rafi send gate).

## Tiered rollout (lowest risk → highest)
- **Now (no new contracts):** WebSearch open-web intent + YouTube Data API + human-picked public threads → `sadie-intent.json` → the wired pipeline (`processes/outbound/intent-outreach.md`).
- **Next (paid APIs):** X Basic API; Reddit Data API agreement.
- **Later (licensed data only):** LinkedIn (Sales Nav + B2B vendor) and Meta (licensing) — **after counsel sign-off**, never via scraping.

## "Can't we just use a free open-source scraper?" (asked 2026-06-15)
**No — that conflates two different things.** A scraper's **license** (MIT, free on GitHub) governs the *tool*; it says nothing about your **right to point it at a platform**. That right is governed by the *target platform's* ToS + the law — and a free scraper doesn't change that analysis one bit. It just moves the liability onto us and hides it.

- Running `snscrape`/`twscrape` (X), `facebook-scraper` (Meta), or an unofficial `linkedin_api` (LinkedIn) is **the same ToS violation** as any other scraping — free or not. LinkedIn especially: account bans + active litigation.
- They're also **brittle** — the platforms actively block them, so they break constantly (most X scrapers died after the 2023 API lockdown). And anything they pull is still **personal data** (GDPR/CCPA), so "it worked" creates downstream obligation, not relief.

**Hard no — detection-evasion tooling.** Anti-detect / stealth browsers (e.g. **camofox-browser** / Camoufox — fingerprint + GeoIP spoofing to "bypass bot detection") are **not adopted, ever.** They exist to scrape while evading detection — a ToS violation *and* active evasion, which is legal risk and the exact opposite of the brand we sell (reliability + compliance). Same logic rules out LLM-scrapers (Scrapegraph-ai) for ToS-gated platforms. (Decision: `decisions/2026-06-15_tool-evals-batch.md`.)

**Named additions (2026-07-05 tool triage — same bucket):** **curl-impersonate** (TLS/HTTP fingerprint impersonation of real browsers — detection evasion by definition) and **scrapling** (its "stealth"/anti-block mode) join camofox as **do-not-adopt, ever**. **Maxun, autoscraper, Crawlee, Scrapy** — parked as redundant scraper-framework installs (no compliant use case our tools don't cover). The one sanctioned crawl path: **Firecrawl** (hosted API; public open-web pages only, robots.txt respected, never pointed at ToS-gated platforms) + the existing native Enrich. (Decision: `decisions/2026-07-05_tool-triage.md`.)

**The genuinely free *and* compliant set** (what we actually use — all wired in `runtime/intent_collect.py`):
- **YouTube Data API** — official, free within quota (`--comments` = prospect-level signal).
- **Google News RSS** — Google's public news-search feed; auto, no key.
- **Bluesky** — open AT-Protocol; official app-password login (the *compliant* alternative to X — open by design, not scraping).
- **Mastodon** — public hashtag RSS, no key.
- **Yelp Fusion API** — official, free tier (business + rating/complaint signal; needs a key).
- **WebSearch** — the assistant's open-web tool, Sadie's in-session capability.
- **RSS / Atom feeds** — public feeds (incl. **Google Alerts RSS** + niche-forum feeds), public sitemaps.
- Official **free tiers** where commercial use is allowed (note: Reddit's free tier is *non*-commercial, so it doesn't count for us).

Everything else (X, Meta, LinkedIn) has **no free compliant path** — it's paid official API or licensed data, per the matrix above. Bottom line: **free-and-allowed ≠ free-but-prohibited; we only use free-and-allowed.** Built into code as `runtime/intent_collect.py` (YouTube API + RSS) + WebSearch in-session.

## Licensed social-listening vendors — coverage-per-dollar (for the paid tier)
The compliant way to "monitor X/Reddit/TikTok/Meta/LinkedIn for keywords + comments" is **one licensed listening tool** that already holds the data rights — far cheaper than buying each platform's API separately (X API alone is ~$200/mo; Reddit Data API is a paid agreement). The tool monitors your phrases; Sadie ingests its alerts (most offer an API or email/RSS export) into the existing collector.

| Vendor | ~Price/mo (SMB) | Platform coverage | Read |
|---|---|---|---|
| **Awario** | **~$29–$111** | Web, X, Reddit, news, blogs, forums (+ some IG/YT) | **Best value to start.** Cheap, good X/Reddit/web. Lighter on TikTok. |
| **Brand24** | **~$79–$199** | X, Reddit, **TikTok**, IG/FB (public), news, blogs, forums | **Best coverage-per-dollar incl. TikTok.** The pick if TikTok matters. |
| **Mention** | ~$41–$179 | Web, X, FB/IG, forums | Solid mid-option. |
| Brandwatch / Meltwater / Talkwalker | **$800–$3k+** (annual) | Everything incl. TikTok, enterprise-grade | Overkill + expensive for now — revisit at scale. |

- **The honest gaps (true of ALL of them):** **LinkedIn coverage is weak everywhere** (LinkedIn restricts API access — no tool solves it; LinkedIn stays manual Sales-Nav + B2B-data). **TikTok** is only on some (Brand24, Talkwalker).
- **Recommendation:** start with **Brand24 (~$149/mo)** if you want TikTok + Reddit + X + Meta-public in one bill; or **Awario (~$50/mo)** if TikTok can wait and you want the cheapest X/Reddit/web coverage. Either replaces *all* the per-platform API spend with one number and slots into Sadie's collector via their API/RSS export.

## Open items for the Founder
- [ ] Decide budget for paid APIs (X Basic ~$200/mo is the cheapest unlock).
- [ ] Pick a licensed B2B-data vendor for LinkedIn-class contact data (vs. manual Sales Nav).
- [ ] Counsel review before any LinkedIn/Meta data use at scale.
- [ ] Document the legitimate-interest basis + opt-out process (Rafi drafts; one-time).

## Standing category nos — added 2026-08-09 (triage: `decisions/2026-07-05_tool-triage.md` §Addendum 08-09)
Two whole **categories**, not two vendors — logged this way so the next instance isn't re-triaged from scratch.

### ❌ Visitor de-anonymisation / identity-resolution pixels
**AudienceLab.io (SuperPixel v3)** — and the same shape from **Warmly, RB2B, Vector, Opensend, Retention.com** and successors. A pixel resolves an *anonymous* site visitor to a named person + email against a third-party identity graph (AudienceLab claims 280M profiles / 60B behaviours), which is then used for ads or outreach.

- **Why it's a no:** it is **covert collection by construction** — the exact thing this document rules out (licensed access, never covert). It is also the hottest privacy-litigation target in the market: CIPA **pen-register / trap-and-trace** theories against tracking pixels (*Camplisson v. Adidas*, 2025), **Cal. Penal Code §637.2 statutory damages of $5,000 per violation** (or treble actual), 3,500+ privacy filings projected for 2026, with at least one live case aimed specifically at a data-broker SDK used to **de-anonymise visitors**. Under GDPR/state privacy law there is no lawful basis for the resolve-then-market step, and it implicates sale/share + opt-out obligations.
- **Applies to client builds too** — never scope one into an engagement, and **do not build an in-house version**: our own pixel is the same tort with yourco's code under it.
- **The compliant cousin, which we already do:** **first-party** — a consented form-fill flowing into our own CRM (the Instant Employee "see yours" → CRM path). Know who's in the funnel because they told you.

### ❌ Ringless voicemail (RVM) for cold outreach — incl. AI voice cloning
**VoiceDrop.ai** and the category. The **FCC's 21 Nov 2022 declaratory ruling** (*All About the Message*) holds that ringless voicemail to a wireless number **is a "call" using an artificial or prerecorded voice** under TCPA §227(b)(1)(A)(iii) and therefore requires **prior express consent**. Cold prospecting has none by definition; exposure is per-message and RVM is an active plaintiff's-bar target.

- **Vendor "compliance tooling" does not cure it.** DNC-list management and spam-report checks address a different obligation entirely — same misdirection as Vayne's "GDPR compliant" badge. Treat built-in-compliance marketing on a consent-gated channel as a red flag, not a green one.
- **Beyond the law:** AI-cloning the Founder's voice so a blast sounds like a personal message is **deception** — it fails the credibility gate and `brand/writing-rules.md` before counsel is even involved, and inverts **"the Founder sends; agents draft."**
- **Don't conflate this with our voice lane.** Vapi (locked) is **inbound/conversational** — answering a call the customer chose to place. That is a different legal and trust posture from pushing a cloned prerecorded voice at a cold list. *We build agents that pick up the phone, not agents that leave you a fake voicemail.*
- **Client delivery:** the only defensible use is a **consent-documented** list (existing customers with prior express consent for prerecorded calls), which most SMB lists do not have. If a client asks, it routes through **counsel gate #4** (FTSA/TCPA, still 🔲) as *their* liability decision — never an yourco default, never in the template, and **no internal build**.
