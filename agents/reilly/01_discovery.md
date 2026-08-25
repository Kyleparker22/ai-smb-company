# Reilly — Stage 1: Discovery

## What this agent is
Reilly is the second dogfood digital employee, proving YourCo's outbound SDR pattern on YourCo itself before selling it.

## First use case
**Vertical → approved multi-touch cold campaign.** the Founder gives Reilly a target vertical (and ICP parameters). Reilly sources matching companies/contacts (multi-source: Outscraper + Instantly + Vibe), researches and enriches each, writes a v2 commission-breath-removal sequence per prospect (3 emails + 3 SMS, 21 days), requests an Email 2 demo video from Reed, has Luka brand-review the campaign, and stages the whole batch in Instantly for the Founder's approval. Reilly never sends without approval.

## Outcome the executive can repeat in one sentence
"the Founder names a vertical, and Reilly hands back a ready-to-approve, fully personalized multi-touch campaign — sourced, researched, and written — without the Founder opening a prospecting tool."

## The pipeline (4 internal stages, 1 employee)
1. **Sourcing** — vertical + ICP in → deduped lead list out. Tools: **multi-source per vertical** (Outscraper + Instantly SuperSearch + Vibe Prospecting for trade/services; subset for other verticals per Polo). Dedup-merge: domain → phone → name+city. Each prospect carries cross-source match tag. Gate: dedupe against suppression list + ICP-fit filter + ≥ coverage threshold.
2. **Research/enrichment** — per company: scrape site + recent news/signals; Vibe Prospecting (Explorium MCP) for firmographics/technographics; Gemini Flash synthesizes 3–5 data points and *one specific pain hypothesis*. Output: a research card per prospect.
3. **Copywriting** — research card in → v2 commission-breath-removal sequence (3 emails + 3 SMS, 21 days). Email 1 pokes the bear + paints Nirvana; Email 2 embeds Reed's demo video; Email 3 reframes + releases. SMS bumps reference prior email + Calendly + STOP. Standing claim: "Live in 48 hours from signed agreement." Pricing pulled from cold (first call only). CTAs live in the Founder's email signature, not body. Stronger model used here (quality converts). Gate: Luka brand review, no fabricated claims, methodology conformance check. **Canonical methodology lives in `/agents/reilly/copy-structure.md`.**
4. **Orchestration/send** — push approved batch to an Instantly campaign; apply state suppression (FL, WA, OK, MD, NY, CA from SMS); read replies/bounces via webhook; feed results back to stage 1 (suppression + ICP refinement).

One employee, one interface ("here's the vertical"). The decomposition is internal — and it *is* the moat: each stage is independently testable, swappable, observable.

## Owned capability: research & enrichment
Account/company research lives **inside Reilly** (stage 2) — YourCo does not run a separate Research Agent. Reilly owns: firmographic enrichment (via Vibe Prospecting), per-company web/news research (scrape + Gemini Flash synthesis), and turning that into a sourced research card with a specific pain hypothesis. Every data point carries a source URL (anti-hallucination gate). If another agent needs research, it requests it from Reilly rather than duplicating the capability — keeps the roster lean (see `04_agent_roster.md`).

## Systems Reilly touches (v0)
- **Vibe Prospecting (Explorium MCP)** — sourcing + enrichment (800M+ profiles, 50+ sources)
- **LLM research layer** — Gemini Flash (cheap) for per-company research synthesis; stronger model for copy
- **Instantly** — sending infrastructure (campaigns, sequences, warmup, deliverability, reply/bounce webhooks)
- **Workspace files** — reads `clients/_pipeline.md` (CRM) and a suppression list; writes campaign artifacts and research cards
- **Reed** — requests one demo asset per vertical/use-case for touch 2
- **Gmail / Slack** — drafts the approval summary to the Founder; posts campaign-ready notice to `#all-yourco`

## Multi-touch, by design (v2 commission-breath-removal — locked 2026-06-08)
Sequences are **3 emails + 3 SMS over 21 days**, all personalized off the one research card. Instantly auto-pauses a prospect on reply. Sequence shape:
- **Email 1 (Day 1):** poke the bear (2-3 problems the owner has normalized) + paint Nirvana (operational + financial outcomes) + 48-hour-from-signed-agreement claim
- **SMS 1 (Day 3):** reference Email 1 + Calendly + STOP
- **Email 2 (Day 7):** Reed-produced demo video (animated GIF preview → Loom landing page) — show, don't tell
- **SMS 2 (Day 10):** reference the video + Calendly + STOP
- **Email 3 (Day 14):** reframe the problem + sharper Nirvana + low-pressure release
- **SMS 3 (Day 21):** break-up + Calendly + STOP

Pricing never appears in cold copy. CTAs (Calendly + website) live in the Founder's signature only. Canonical methodology: `/agents/reilly/copy-structure.md`.

## Success criteria (eval set v0 — full harness in 03_eval.md)
1. **Reliability** — a named vertical produces a complete staged campaign with zero manual data steps. Target: 100%.
2. **Personalization depth** — every prospect's touch 1 references ≥1 specific, verifiable company fact (not generic). Target: 100%; 0 hallucinated facts.
3. **Deliverability hygiene** — no send from primary domain; SPF/DKIM/DMARC + warmup + one-click unsubscribe verified before any send. Target: 100%.
4. **Approval discipline** — 0 emails sent without the Founder's explicit batch approval. Target: 100% (hard gate).
5. **Outcome** — reply rate and booked-discovery-call rate tracked per campaign; target set after first campaign establishes a baseline.

## Approval pattern
- **Full autonomy** for: sourcing, research, drafting sequences, staging (un-launched) campaigns in Instantly, writing workspace artifacts, drafting the Founder's approval summary.
- **Human-must-approve** for: **launching/sending any campaign** (external email), adding new sending domains/inboxes, any spend > $1.
- **Human-in-loop** for: changing the ICP/vertical definition, suppression-list overrides.

## Digital employee identity
- **Name:** Reilly
- **Email:** `contact@yourco.example.com` (alias of `founder@yourco.example.com`, active 2026-06-09)
- **Signature on outreach:** sends as the Founder (or a provisioned sending persona) — never as "an AI"; internal notices signed "— Reilly, YourCo Ops"

## Scope — IN (v0)
Sourcing, enrichment, per-company research, multi-touch sequence writing, Instantly campaign staging, reply/bounce ingestion, approval summary.

## Scope — OUT (parked for v1+)
- Auto-sending without approval (never in v0)
- Per-prospect personalized *video* (Reed starts with reusable per-vertical demos)
- Touching any client tenant
- LinkedIn/social outbound (email only in v0)
- Auto-booking calls (Reilly flags reply → the Founder books, until reply handling is proven)

## v0 → v1 → v2 roadmap
- **v0:** one vertical, one approved campaign, reply/bounce visibility. Prove personalization + deliverability + approval discipline.
- **v1:** reply triage + suggested responses; ICP auto-refinement from lost/won signals; multiple concurrent verticals.
- **v2:** run the same pattern inside a *client's* tenant as a sold engagement (the productization payoff).

## Risks
- **Deliverability / domain reputation.** Cold email from a cold domain burns. Mitigation: cold-email domain `getteamyourco.com` (done-for-you via Instantly, separate from `yourco.com` primary), 2 mailboxes provisioned, warmup running through ~2026-07-08, hard approval gate. (Logged 2026-06-08; see `/decisions/2026-06-08_cold-email-infrastructure.md`.)
- **Hallucinated personalization.** A wrong "fact" about a prospect is worse than a generic email. Mitigation: stage-2 gate requires every claim trace to a source; stage-3 quality gate.
- **Data quality.** Vibe/Explorium match rates may disappoint. Mitigation: Clay (waterfall enrichment) is the documented fallback — see decision log 2026-06-07_outbound-sales-stack.
- **Compliance.** CAN-SPAM / one-click unsubscribe / suppression discipline are non-negotiable; built into stage 4.
