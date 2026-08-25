# 2026-06-17 — The agentic website: a recurring loop, an offering, and a "built-for-agents" workstream

## Decision (the Founder)
Three connected moves, all owned by **Mario** (AEO/GEO agent, `decisions/2026-06-14_mario-aeo-geo-agent.md`):
1. **Formalize the "agentic website" loop as a recurring artifact** on yourco.com — *CI/CD for search*:
   research the market → ship site changes (new sections, internal links, sharper pages, cleaner schema, added
   proof) → **measure** (rankings, impressions, **AI-citation/answer-engine** presence) → double down or adjust →
   repeat. The site should be *alive* — learning from real data and getting more retrievable, understandable, and
   recommendable every month. Extends Mario's existing AEO/GEO loop (`processes/loops/aeo-geo.md`,
   `loops/aeo-geo/`): each run now also produces a **dated "site improvement" artifact** (what shipped + the
   measured result) so the loop compounds.
2. **Make "living website / AEO" an offering** — the operated, done-for-you version of the above, *for clients*.
   It's the productized form of the GEO done-for-you offering (`decisions/2026-06-16_geo-done-for-you-offering.md`):
   a recurring retainer where yourco runs the research→ship→measure loop on the client's site. Can also surface as
   a **Ready-to-Hire-adjacent SKU** ("Living Website / AEO") once Polo prices it. Mario runs it; Webb ships changes.
3. **A "built for agents, not just humans" workstream** — make the site legible to AI crawlers + answer engines,
   because buyers increasingly arrive via AI (Google AI Mode, ChatGPT, Perplexity). Concrete checklist below.

## Why
- **Buyers retrieve via agents now.** A site optimized only for human eyeballs is invisible to the AI layer that's
  becoming the front door to the internet. Being *retrievable + citable* is the new SEO.
- **It's dogfood + offering.** yourco runs the loop on its own site (proof), then sells the same operated loop —
  exactly the "we run it for you" model. The agentic website is the moat applied to marketing.
- **A "useless chatbot bubble" is not agentic.** yourco's interactive layer is the **voice agent / Revenue Leak Snapshot /
  Missed-Money Meter**, not a "how can I help you?" widget — substance over decoration.

## The built-for-agents checklist (Mario + Webb)
- ✅ **`llms.txt`** — shipped (`agents/webb/pages/yourco-site-v2/llms.txt`): tells LLMs what yourco is + key links.
- **Schema.org JSON-LD** on key pages — `Organization`, `Service`, `Product`/`Offer` (with the locked Ready-to-Hire
  prices), `FAQPage`, `Review`. Machine-readable facts answer engines can lift.
- **Clean semantic HTML** + logical heading/section structure (the staged pages already lean this way).
- **Machine-readable answers** — pricing, FAQ, per-vertical claims, and the Leak Index stats written as crisp,
  extractable, *sourced* statements (already done on the stats — exactly what answer engines reward).
- **Crawlable + fast** — static pages, key facts not JS-gated, clean `robots.txt` + `sitemap.xml`.
- **Later:** an MCP endpoint / public API so an agent can query yourco directly; structured per-vertical feeds.
- **Measure** what's working: track AI-citation presence + organic/impression lift each loop run; double down.

## Owners
**Mario** (the loop, the AEO offering, the built-for-agents spec) · **Webb** (ships site changes + JSON-LD/robots/
sitemap) · **Polo** (prices the Living-Website/AEO offering) · **the Founder** approves. **Brett** flags it as a bet worth
making (it came from his ideas drop's spirit + the agentic-website thesis).

## Status
Direction set 2026-06-17. `llms.txt` shipped (staged with the site). The JSON-LD pass, the recurring "site
improvement" artifact in Mario's loop, and the offering packaging are Mario/Webb's next steps — staged behind the
launch-gate like the rest of the site, but the *internal* loop (dogfooding on the staged site) can start now.
