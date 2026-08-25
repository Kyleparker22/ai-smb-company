# Tier-2 / Production Employee Shapes

> The up-market catalog: employees that **create deliverables and run multi-step pipelines** (the "produce it" tier). Model + rules: `processes/employee-tiers.md`. Each shape names its **agent-able steps** and its **human-in-loop step** honestly (the agent-vs-service line). Tier-1 "handle it" shapes live in `employee-patterns.md`.
>
> **New candidate AI-OS offering lines (2026-06-16, internal-only):** see `processes/new-offering-lines.md` for the multi-agent OS lines spec'd this session — Company OS (acquisition handoff), GEO/AEO done-for-you, interior-design ops, staffing/delivery OS, plus two **counsel-gated DTC** OS candidates (hormonal-health, first-time-landlord). Not on the public site; built per-engagement when sold.

---

# ⭐ FLAGSHIP — "Sloane," the Real-Estate Listing Marketing employee

**Vertical:** Real estate · **Tier:** 2 (production + orchestration) · **Replaces:** a copywriter + a social manager + a media coordinator + the follow-up nobody does.

**The job (one line):** own a listing's marketing from "new listing" to "live and promoted" — produce the assets, coordinate the shoot, publish, and report — all gated for the agent's approval.

## Trigger
A new listing goes under the agent's control (a signed listing agreement / a new-listing event in the CRM). Sloane kicks off the listing's marketing pipeline automatically.

## The end-to-end pipeline
*(🤖 = agent does it · 🧍 = human-in-loop step Sloane coordinates · ✅ = gated to the agent)*

1. **Kickoff & intake** 🤖 — pull the property facts (address, beds/baths, sqft, features, price) from the agent's input or the CRM; build the listing's work file.
2. **Listing copy** 🤖✅ — write the MLS description *and* a punchier marketing version, in the agent's voice (held to brand). No fabricated features — only what the agent confirmed.
3. **Market context / comps** 🤖✅ — pull comparable sales + days-on-market, summarize where this listing sits. **Sources cited, no invented numbers**; the agent sets the price, Sloane supplies the context.
4. **Media coordination** 🧍 — **book the photographer / 3D-tour capture** (the physical step a human does). On "shoot done," Sloane runs the output through the processing + hosting pipeline (e.g. splat → clean → publish a tour link) 🤖 and files the assets.
5. **Marketing assets** 🤖✅ — draft the Instagram/Facebook posts, the "just listed" email to the agent's database, and a one-page flyer (Webb/Canva-style). All in the agent's brand.
6. **Publish & distribute** ✅🧍 — on the agent's approval: schedule the social, send the email-blast, post the tour link. **The MLS listing itself is published by the licensed agent** (the legal line — Sloane preps everything, the agent hits go).
7. **Lead capture** 🤖 — inbound from the listing/posts → qualify → book showings (hands to / pairs with the Tier-1 intake employee, "Ada").
8. **Weekly report + nudge** 🤖✅ — views, inquiries, showing count, what's converting; flags a price/strategy conversation when the data says so.

## Stack / connectors
CRM/MLS data · the agent's calendar · a comps/market data source · brand-voice profile · social + email tools · the 3D-tour/photo pipeline (capture vendor + processing + hosting APIs) · the asset store.

## The agent-vs-service line (honest)
**~85% autonomous agent + one named human step.** Copy, comps, asset drafting, coordination, publishing-prep, lead capture, and reporting are agent-able. The **physical capture (photos / 3D walk-through) is the human-in-loop step** Sloane *books and processes the output of* — it never pretends to shoot the house. And **the MLS publish is the licensed agent's action** (legal). Price + scope to that reality.

## Approval gates
Every external send (social, email, copy) = agent approves · pricing context only, never a fabricated comp or a set price · the MLS publish = the agent (licensed) · the shoot = booked, human-performed.

## Eval focus (Kolby, harder than Tier 1)
Copy quality + brand voice (Luka) · **comps factually grounded, sources cited, zero fabrication** · no MLS/legal misstep · media-pipeline reliability (the tour link actually renders) · the weekly report is honest (no inflated numbers).

## Why it's the flagship
It's a *much bigger retainer* than "answer the phone" — it replaces 3–4 fragmented vendors with one accountable employee — it's ~85% agent with an honest human step, and it's a natural **Tier-1 → Tier-2 expansion** (land Ada the intake employee, grow into Sloane the listing employee). It shows the whole Tier-2 thesis in one shape.

---

# 10 more Tier-2 shapes across industries
*Format: job · trigger · pipeline (🤖 agent · 🧍 human-in-loop · ✅ gated) · stack · the agent-vs-service line · gates · eval focus.*

## 1. Med spa — "Lux," Treatment-plan & promo-campaign employee
**Job:** turn a consult into a personalized treatment plan, run the promo campaigns, coordinate before/after content. **Trigger:** a completed consult / a monthly promo cadence.
**Pipeline:** consult synthesis 🤖 → treatment-plan draft from the locked menu 🤖✅ (provider confirms clinical recs 🧍) → seasonal promo: social/email/SMS 🤖✅ → before/after content (consented capture 🧍, drafted 🤖) → publish ✅ → rebook + package upsell 🤖✅.
**Stack:** practice CRM · calendar · social/email/SMS · service menu + brand voice · consent/asset store.
**Agent-vs-service:** the **clinical recommendation + the photo capture/consent are human**; plan drafting, campaigns, content, scheduling, follow-up are agent. **No medical/efficacy claims, ever.**
**Gates:** provider confirms clinical content · sends approved · PHI image consent (BAA). **Eval:** no medical claims, consent handling, factual pricing, brand voice.

## 2. Restaurant — "Saveur," Seasonal-menu & catering-proposal employee
**Job:** run the restaurant's marketing — menu campaigns, always-on social, catering/event proposals. **Trigger:** a menu change, a catering inquiry, a weekly content cadence.
**Pipeline:** new-menu announcement (social/email) 🤖✅ → weekly dish-spotlight content 🤖✅ (food photo 🧍) → catering inquiry → qualify + branded proposal from the catering menu 🤖✅ → reservations/event handoff 🤖 → review nudges + response drafts 🤖✅.
**Stack:** POS/menu · reservations/calendar · social/email · catering menu + pricing + brand voice · photo assets.
**Agent-vs-service:** **food photography + the cooking/event execution are human**; copy, campaigns, proposals, scheduling, review flows are agent.
**Gates:** pricing from the locked catering menu (no invented quotes) · sends approved · allergy/health accuracy. **Eval:** brand voice, factual menu/pricing, allergy accuracy.

## 3. Home services / contractor — "Beam," Estimate & proposal builder
**Job:** turn a site visit's rough notes into a polished branded estimate + proposal, then chase it to a decision. **Trigger:** the estimator finishes a site visit.
**Pipeline:** site visit (notes/measurements/photos) 🧍 → line-item estimate from the price book 🤖✅ → branded good/better/best proposal 🤖✅ → send + e-sign prep ✅ → follow-up until decision 🤖✅ → on signature, kick scheduling 🤖.
**Stack:** price book · CRM · the estimator's notes/photos · proposal + DocuSign · brand voice.
**Agent-vs-service:** the **site visit + measurements are human**; building/sending the estimate + follow-up are agent. **Pricing from the price book, not invented.**
**Gates:** pricing from the price book · sends + e-sign approved · scope matches the visit. **Eval:** estimate accuracy vs notes + price book, no fabricated scope/price, brand voice.

## 4. Law firm — "Counsel," Intake → matter-packet & engagement-letter employee
**Job:** turn a qualified lead into a clean matter packet — intake summary, conflict-check flag, engagement-letter draft, document checklist — ready for the attorney. **Trigger:** a qualified intake / booked consult.
**Pipeline:** intake synthesis + **conflict-check flag** 🤖✅ (run by human/system 🧍) → engagement-letter draft from the template 🤖✅ (attorney reviews 🧍) → document checklist + collection + filing 🤖 → kickoff scheduling 🤖 → status nudges 🤖✅.
**Stack:** practice management/CRM · firm templates · document intake/storage · calendar · brand voice.
**Agent-vs-service:** **all legal judgment + the conflict decision + the attorney review are human.** Counsel drafts from templates, organizes, collects, schedules — **never gives legal advice.**
**Gates:** attorney approves every client-facing doc · **no legal advice** (cardinal) · privilege-safe · conflict-check before engagement. **Eval:** no legal advice, template accuracy, privilege/confidentiality, conflict-flag reliability.

## 5. Auto dealership — "Axle," Inventory marketing employee
**Job:** market the lot — listing descriptions + social for every vehicle + lead nurture. **Trigger:** new inventory (a VIN/stock event).
**Pipeline:** inventory sync 🤖 → per-vehicle description from the feed 🤖✅ → "just arrived" social + weekly highlights 🤖✅ (vehicle photo 🧍) → inquiry nurture + price-drop alerts 🤖✅ → test-drive booking 🤖 → attention report 🤖✅.
**Stack:** DMS/inventory feed · CRM · social/email/SMS · photo assets · brand voice.
**Agent-vs-service:** **photography + the sale/financing are human**; copy, social, nurture, booking are agent. **Specs/price from the feed, not invented.**
**Gates:** specs/price from the feed · sends approved · pricing disclaimers compliant. **Eval:** spec/price accuracy, disclaimer compliance, brand voice.

## 6. Fitness / studio — "Pace," Content & challenge-campaign employee
**Job:** run content + membership campaigns — class promos, challenges, member-journey content. **Trigger:** weekly content cadence / a launch.
**Pipeline:** weekly content calendar 🤖✅ (shoots 🧍) → "30-day challenge" campaign: landing copy + social + email sequence 🤖✅ → trial→member nurture 🤖✅ → win-back lapsed 🤖✅ → class booking + waitlist 🤖.
**Stack:** booking/membership system · social/email · brand voice · content assets.
**Agent-vs-service:** **coaching + any shoots are human**; content, campaigns, nurture, booking are agent.
**Gates:** sends approved · **no health/medical claims** · accurate schedule/pricing. **Eval:** brand voice, no health claims, factual schedule/pricing, campaign quality.

## 7. E-commerce — "Quill," Product-listing & email-campaign employee
**Job:** produce merchandising content — product descriptions + SEO + lifecycle email/review flows. **Trigger:** a new product; a campaign cadence.
**Pipeline:** product sync 🤖 → listing copy + SEO (titles, meta, alt) from real data 🤖✅ → lifecycle email/SMS (welcome, abandoned-cart, post-purchase, win-back) 🤖✅ → review-request flow + UGC 🤖 → merch report 🤖✅.
**Stack:** the store platform · email/SMS · review tooling · product feed · brand voice.
**Agent-vs-service:** **photography + fulfillment are human**; copy, SEO, campaigns, review flows are agent. **No fabricated specs/claims.**
**Gates:** specs/claims from the data · sends approved · pricing/claims compliant. **Eval:** spec accuracy, claim compliance, SEO quality, brand voice.

## 8. Financial / insurance — "Ledger," Client-review prep & report employee
**Job:** prep the advisor's client reviews — pull the data, build the review packet + plain-English summary, draft talking points (the advisor decides). **Trigger:** an upcoming review/renewal date.
**Pipeline:** data pull from systems of record 🤖 → branded review packet (where they stand, what changed, questions to discuss) 🤖✅ → renewal/recommendation talking-points draft 🤖✅ (**advisor makes the recommendation** 🧍) → schedule the review 🤖 → doc collection + approved recap 🤖✅.
**Stack:** portfolio/policy systems · market data · calendar · doc collection · brand voice · **compliance guardrails**.
**Agent-vs-service:** **all advice + the recommendation + compliance sign-off are human (licensed advisor).** Ledger pulls data, builds packets, schedules, drafts talking points — **never advises, never fabricates a number.**
**Gates:** advisor approves everything · **no financial advice** (cardinal) · no fabricated figures · suitability/compliance. **Eval:** data accuracy (zero fabrication), no-advice line, compliance, brand voice.

## 9. Dental / medical — "Mela," Recall-campaign & patient-education employee
**Job:** run patient marketing — recall campaigns, education content, reputation — compliantly. **Trigger:** recall-due lists; a content cadence.
**Pipeline:** recall campaign (email/SMS) 🤖✅ → patient-education content 🤖✅ (**provider clinical review** 🧍) → review requests + response drafts 🤖✅ → reactivate lapsed 🤖✅ → booking 🤖 (escalate clinical 🧍).
**Stack:** practice management · email/SMS · brand voice · **HIPAA handling (BAA)** · content store.
**Agent-vs-service:** **all clinical content + advice + the exam are human (provider).** Mela runs campaigns, drafts education (provider-reviewed), books, reactivates — **no medical advice; PHI under a BAA.**
**Gates:** provider reviews clinical content · BAA + PHI minimization · no medical advice · sends approved. **Eval:** no medical advice/claims, PHI/HIPAA handling, brand voice, scheduling accuracy.

## 10. Construction / architecture — "Forge," Project-update & proposal employee
**Job:** keep clients informed and win the next job — turn project data into client-facing progress reports + proposals. **Trigger:** a project milestone / weekly cadence; a new-project RFP.
**Pipeline:** weekly progress report from PM data 🤖✅ (site photos 🧍) → change-order drafts from a scope change + the rate sheet 🤖✅ → RFP → branded proposal (scope/phases/timeline/pricing from the cost model) 🤖✅ → schedule check-ins + send approved updates 🤖✅ → chase proposals/decisions 🤖✅.
**Stack:** PM/scheduling tool · cost model/rate sheet · doc + e-sign · calendar · brand voice · project photos.
**Agent-vs-service:** **the construction + site photos + the estimator's judgment are human**; reports, change-orders, proposals, comms are agent. **Pricing from the cost model, not invented.**
**Gates:** pricing from the cost model · sends + change-orders approved · scope accuracy. **Eval:** cost/scope accuracy, no fabrication, brand voice, report honesty.

---

# ⭐ Internal-facing Tier-2 — "Company Brain," the institutional-memory employee
**Vertical:** any company with accumulated knowledge — ops-heavy SMBs, professional services, franchises, trades with years of project history. **Tier:** 2 · **Replaces:** the "go ask [the person who's been here 15 years]" bottleneck, the onboarding drag, and the SOPs nobody can find.

**The job (one line):** be the company's memory — ingest their SOPs, docs, past projects, and policies, and answer staff questions, onboard new hires, and draft from precedent — **grounded, cited, and never making it up.**

This is the one **internal-facing** shape: employees ask it, not customers. It's the [[gbrain]]/answer-with-citations idea (the thing yourco decided to build native rather than adopt) productized for a client — and the internal version already runs in the OS (Melanie's source-citations + reference library).

## How it works
- **Ingests** the company's knowledge — Drive / SharePoint / Notion / a wiki / past project files / SOPs — into a **private index inside their own tenant** (their data never leaves; yourco runs the index, the client owns the corpus).
- **Answers in Slack / Teams / email:** "how do we handle a change order over $10k?" · "what's the spec we used for the Henderson job?" · "what's our PTO policy?" — **with a citation to the source doc**, and an honest "I don't have that" instead of a guess.
- **Onboards new hires** — answers their questions, points them to the right SOP, so a senior person isn't the help desk.
- **Drafts from precedent** — a new SOW from past SOWs, a reply from past tickets, a checklist from how it was done last time.
- **Surfaces gaps** — "three docs disagree on the refund policy" · "no SOP exists for X yet."

## Stack / connectors
Their doc stores (Drive / SharePoint / Notion / etc.) · a private retrieval index in their tenant · Claude (grounded retrieval + synthesis) · Slack / Teams / email surface · Langfuse eval.

## The agent-vs-service line (honest)
**~fully agent on retrieval, Q&A, and drafting.** The human owns **what counts as authoritative** (which doc wins when two disagree) and **approves anything it would act on**. It reads and answers; it doesn't rewrite the source of truth on its own.

## Eval focus (Kolby — this is the hard one)
A Company Brain that fabricates is *worse than nothing* — it gives confident wrong answers about your own company. So the bar is: **every claim traceable to a source** (grounding/citation accuracy), **refuse-when-unknown** (no hallucinated policy), **access-control correctness** (it only surfaces what the asker is allowed to see), and **freshness** (it knows which doc is current). This is exactly yourco's moat — the reliability layer is the whole product here.

## Why it earns Tier-2 + sells
- **Pricing** to the corpus + number of sources, in the Tier-2 envelope ($5–10k build · $1.2–3k/mo) — Polo scopes it.
- **The natural expansion sell:** a Tier-1 client who trusts their intake employee is the easiest yes for a Company Brain (Bird). It also lands with companies that don't have a customer-facing automation need yet but are drowning in their own knowledge.

---
> **Pattern across all 12:** the agent owns the *digital production + orchestration* (or, for Company Brain, *retrieval + answering*); a named human owns the *physical/creative/licensed/authoritative* step and the agent works around it. **Pricing to the bundle of vendors/roles it replaces** (Polo); **eval gets a harder grounding + compliance bar** (Kolby — hardest of all for Company Brain); **these are the expansion sell** once a Tier-1 employee is trusted (Bird).

