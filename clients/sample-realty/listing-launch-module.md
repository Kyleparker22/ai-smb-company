# Listing Launch — the operated module (Sample Realty)

> **What this is:** the spec for the first yourco module at Sample Realty — the one that turns "Kimi makes the flyer" into "the listing kit makes itself, Kimi approves it." Pillar 3 (**Marketing / Demand**) with a foot in Pillar 1 (**Intake**). Companion to the DIY tool at `tools/flyer-builder.html`, which is the same output produced by hand.
>
> **Status: SPEC — not built, not sold.** Sample Realty is a prospect (see `_README.md`). Nothing here is committed to; this exists so the conversation has something concrete behind it.

---

## The problem, stated honestly

Every new listing kicks off the same 3–6 hours of work, and it happens at the worst possible moment — the week Kimi is also negotiating, scheduling the photographer, and prepping the sellers:

| The task | Today | Why it slips |
|---|---|---|
| Property flyer | Hand-built per listing | Design drifts; often skipped for smaller listings |
| MLS description | Written from scratch | Keyword discipline is inconsistent under time pressure |
| Social posts | Ad hoc, if at all | Usually the first thing dropped |
| Cinematic / video tour | Not currently produced | No repeatable pipeline |
| Buyer inquiries | Answered when she can get to them | **Speed-to-lead is where the money leaks** |

The flyer is the visible symptom. The expensive one is the last row.

---

## What the module does

**Trigger:** a listing is signed and the photography comes back.

**One input:** the features sheet Kimi already writes (the same document behind the 2304 flyer) plus the photo set. Nothing new to author.

**The kit produces itself:**

1. **Property flyer** — the one-page print piece, in Sample Realty's brand, ready for the counter and the open house
2. **MLS description** — long and short forms, keyword-disciplined, written to the character limit
3. **Cinematic tour** — camera passes over the listing photography, published to a branded tour page. **Camera motion over real photographs only** — a generative model would invent finishes the house doesn't have, which is a misrepresentation exposure before it's a quality one. Built and working (Phase 0); hosting is what Phase 2 adds.
4. **Social cuts** — vertical video + still sets sized for Instagram, Facebook, and the site
5. **Listing page** — the property's own page on SampleRealtyteam.com, with the tour embedded and lead capture wired in
6. **Speed-to-lead** — every inquiry from any of the above gets answered in seconds, qualified, and offered showing times against the live calendar

**Kimi's job shrinks to one thing: approve.** One screen, one pass, per listing.

---

## What is automated vs. approved

Per the autonomy matrix, everything starts at the **approval floor (R1)** and earns autonomy only on evidence:

| Action | Launch setting | Can earn autonomy? |
|---|---|---|
| Generate flyer / description / tour / social | Auto-produce, **Kimi approves before publish** | Draft quality yes; **publish stays gated** |
| Publish to MLS | **Never automated** — Kimi publishes | No. Compliance surface |
| Publish to the website / social | Approve-then-publish | Yes, after a clean streak |
| Answer a buyer inquiry (first response) | Templated answer, auto-sent | Yes — this is the highest-value autonomy |
| Offer / book a showing | Auto-offer real calendar slots | Yes, within her rules |
| Answer a question about price, condition, or disclosures | **Escalate to Kimi, always** | **No. Hard stop.** |
| Anything touching an offer or negotiation | **Never touched** | **No.** |

**The guardrails that ship with it** (these are the product, not the flyer):
- **Facts come from one source.** Beds, baths, square footage, and year are read from the listing record — not retyped per asset. One correction fixes every surface.
- **Photo rights are enforced.** Only images uploaded from the listing's own shoot are usable. Street View / portal screenshots are blocked — this already came up three times building the sample.
- **AI imagery is disclosed.** Any generated tour carries an "AI-enhanced virtual tour" line, and the camera-movement-only rule means finishes, fixtures, and views are never altered.
- **Fair-housing screen.** Every generated description is checked against prohibited language before it reaches Kimi.
- **Nothing publishes on a stale fact.** If the listing record changes, dependent assets flag rather than silently disagree.

---

## What it needs from Sample Realty

- The features-sheet habit (already exists)
- Photographer images, in a folder per listing (already exists)
- MLS access for read + the calendar for showing slots
- Kimi's rules, once: what the assistant may say, what it must escalate, showing windows
- One decision: which surfaces auto-publish after the trust is earned

---

## Phasing

| Phase | What ships | Kimi's time per listing |
|---|---|---|
| **0 — today** | `tools/flyer-builder.html` — features sheet + photos in; flyer, both presentations, MLS copy, social kit, **cinematic tour and listing page** out | ~10 min, whole kit |
| **1** | Features sheet + photos in → flyer, MLS description, social cuts out. Approval screen. | ~10 min, whole kit |
| **2** | The tour and page **hosted** on SampleRealtyteam.com with real lead capture. Builder side is built and tested — one button, gated on fair-housing + facts. Blocked on one DNS record and who runs the publisher: `website-publishing.md` | ~10 min |
| **3** | Speed-to-lead: inquiries answered, showings offered against the calendar | ~10 min + approvals |
| **3b** | **Instagram publishing** — the launch week writes, schedules and posts itself behind one approval. Full build spec: `instagram-automation-spec.md` | ~90 sec per listing |
| **4** | Autonomy promotions on evidence; expansion to the next pillar (past-client nurture, review requests, transaction-coordination chasing) | trending down |

Phase 0 is real and delivered — including the tour and the listing page, which generate as self-contained files today. Everything after it is scoped, not started.

**One thing deliberately not built: portal syndication scraping.** Confirming a listing rendered correctly on Zillow / Realtor.com / Redfin means scraping sites that prohibit it, with no public API and markup that changes without notice — the automation would break silently and be trusted anyway. The module instead (a) puts a dated day-2 portal check on the launch checklist with exactly what to compare, and (b) scopes the real build as a diff against the **Canopy MLS RESO feed** — the record of record — which needs brokerage credentials and a data-licence agreement. Decided 2026-08-18.

---

## Why this is the right first module

- **It's the visible pain** — she already asked how to make flyers herself, which is the buying question in disguise.
- **It compounds per listing.** The value scales with her volume rather than being a one-time fix.
- **It's provable.** Time-per-listing and speed-to-first-response are both measurable from day one — this module can be held to a number.
- **It's a clean expansion path.** Marketing → Intake → Customer (reviews/nurture) → Back Office (transaction coordination) is the natural sequence through the pillars, and Bird's land-and-expand map runs straight down it.

## Pricing frame

Not quoted, and not to be quoted before an audit. For internal sizing only: this is a **Core**-shaped engagement (one function automated, ~3 agents, 1–2 pillars) against Polo's locked ladder. The audit sizes it and credits 100% toward implementation. See `pricing/v0/os-tiers.md`.

## What has to be true first

- ⚠️ **Stage 0 has not fired.** No audit, no proposal. This is a spec written to make a conversation concrete.
- Counsel/compliance pass on the fair-housing screen and the AI-tour disclosure before anything touches a live listing (Rafi + Ray).
- Kimi's own MLS rules confirmed — board rules on AI-generated imagery vary and are the binding constraint, not our preference.
