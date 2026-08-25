2026-07-05 — Detection-evasion do-not-adopt list extended; one sanctioned crawl path

Source: tool triage (`decisions/2026-07-05_tool-triage.md`); camofox precedent (`2026-06-15_tool-evals-batch.md`)
Pattern: The scraper-tool family keeps resurfacing under new names. curl-impersonate (TLS-fingerprint impersonation) and scrapling (stealth mode) are detection evasion by design — same "hard no, ever" bucket as camofox; Maxun/autoscraper/Crawlee/Scrapy are parked as redundant framework installs. The compliant crawl surface is now exactly two things: Firecrawl (hosted API; public open-web, robots.txt-respecting, never ToS-gated platforms) + native Enrich.
Implication: Rafi — the assessment (`agents/rafi/social-platform-scraping-assessment.md`) carries the named additions; anything future that advertises "bypass bot detection," "stealth," or "undetectable" is auto-no without a fresh review. If Firecrawl usage ever drifts toward gated platforms or logged-in pages, that's a sanction violation to flag.
Audience: Rafi (primary); Sadie, Reilly (sourcing must stay on licensed paths); Kemba (wiring the Firecrawl key = wiring the bounds)

Triggers: agent:rafi, agent:sadie, scraping tool, crawler adoption, detection evasion, skill:tool-triage, loop:source-watch