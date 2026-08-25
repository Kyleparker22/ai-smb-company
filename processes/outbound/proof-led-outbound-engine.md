# Proof-led outbound engine

> The workhorse for first clients. Cold outreach is yourco's lowest-trust channel — so we **don't** lead with a pitch. We lead with a **working, personalized demo of the prospect's own business** (a per-prospect Instant Employee), built before we ever email them. Cold outreach that arrives already warm. Owners: **Reilly** (DRI — sourcing + campaign ops) + **Michelle** (the messaging/copy, split 2026-06-15) + **David** (CRM). **Internal-only:** build the engine + source the lists now; **no sending until launch** (CAN-SPAM/TCPA — Rafi gate; runtime `processes/10dlc-sending-infra-setup.md`).

> Copy rule: every email and text follows `brand/writing-rules.md` (plain words, the em-dash cap, the read-aloud test). Reilly reads it before drafting.

## The whole motion in one line
**ICP → source (Vibe) → qualify → generate a personalized Instant Employee per prospect → proof-first sequence → reply → 48h build.** Every step feeds David's CRM.

## 1 · The ICP (who)
The first, tightest beachhead (flagship vertical, locked pricing, FL home base):
- **Vertical:** landscaping / lawn / irrigation (NAICS **561730**), expanding to other service SMBs that take inbound calls.
- **Size:** ~1–50 employees (owner-operated; the owner feels the missed-call pain personally).
- **Geo:** Florida first (home turf, the CRM's existing batch), then out.
- **Must-have:** a **website** (it's the fuel for the personalized demo) and an **inbound phone/booking motion** (they live or die on catching calls).
- **The pain we hook:** missed calls = missed jobs. Owner can't answer the phone on a job site; leads go to voicemail and die.

## 2 · Source (Vibe) — the recipe that works
`fetch-entities` (free ~5-row sample) → `export-to-csv` (costs credits) once a query is dialed in.
- **Filters used:** `naics_category: ["561730","541320"]`, `company_region_country_code: ["US-FL"]`, `company_size: ["1-10","11-50"]`, `has_website: true`. (Filter values are objects: `{"values":[...]}`; `has_website` is a raw boolean.)
- **Cost:** ~1 credit/row for businesses; **enrichment (emails/phones) adds cost**, and contact emails require the paid export — the free sample is company-level only. A 200-row enriched list is a **the Founder credit-spend decision** (`mcp__Vibe__show-pricing-plans`).

### The qualification lesson (don't skip)
**NAICS over-includes.** The first real pull returned nurseries (Sturon), wholesalers, and even a SaaS platform (Procursys/DynaServ) under "Landscaping Services." A NAICS list is a *raw* list. **Qualify for: a service business that takes inbound customer calls and books jobs** — not wholesale/B2B/nursery/software. Quick filter: does their site have a "call us / get a quote / book an estimate" motion? If not, cut it.

## 3 · The hook — a personalized Instant Employee per prospect *(the differentiator)*
Before the first email, run the **Instant Employee Mode A** flow (`processes/instant-employee.md`) on the prospect's real website → a working demo of *their* front desk ("Reese for [Business]"). The email leads with **"I already built this for you."** No competitor doing cold landscaping outreach can show a working, branded demo of the prospect's own intake. This is the engine's edge — personalized proof at scale, powered by the asset we already built.

## 4 · The sequence (proof-first, ~10 days)
Email-led; SMS only where there's a number + consent (TCPA — Rafi).
1. **Touch 1 — Day 0 · the demo.** Subject: *"built an AI front desk for [Business]"*. Body (short): "I run yourco — we build AI employees for landscapers. I made a 60-second working demo of an AI front desk for [Business]: it answers your calls, qualifies the job, books the estimate. [personalized Instant Employee link]. If it's useful, I can have a real one live in your business in 48 hours. — the Founder"
2. **Touch 2 — Day 3 · the math.** "Did the demo land? Rough math: [missed calls/wk] × [avg job value] = $[X]/mo going to voicemail. Reese catches them 24/7. Worth 15 min?" (ties to the ROI calculator).
3. **Touch 3 — Day 6 · the trust.** Kill the "is it reliable / will it embarrass me?" fear: "Unlike a chatbot, it never quotes a price (your rule), routes anything odd to you, and you approve anything before it sends. Here's exactly how we keep it reliable: [glass-box / try-to-break-it link]."
4. **Touch 4 — Day 10 · the breakup.** "Last note — want me to close your file? If timing's off, no worries. If you want the 48h build: [calendar]."
- **SMS (optional, post-Touch-1, compliant only):** "Hi [Name], the Founder w/ yourco — made you a 60-sec demo of an AI front desk for [Business]: [link]. Worth a look?"

## 5 · Wire to the CRM + measure
- Every sourced target → a `company` (+ `deal`, stage `prospect`) in `crm/data.json`, `source: "Vibe — <vertical> <geo>"`, owner Reilly. Replies/bookings move the stage. Contacts added when enriched (paid) or when they reply.
- **Track per sequence:** reply rate · demo-open rate · call-booked rate. Write what's working to `learnings/` so the next batch's copy improves (closed-loop).

## 6 · Compliance + mandate (hard)
- **Email:** CAN-SPAM (identify, opt-out, no deception). **SMS:** TCPA + 10DLC registration — **consent required**; Rafi gate. Don't source-then-blast numbers.
- **Pre-send eval gate:** no staged batch is sent without a **dated PASS artifact** in `loops/outreach-eval/` for that exact batch (`processes/outbound/pre-send-eval-gate.md`). Mechanical pre-pass: `python3 runtime/instantly.py --eval-batch "<campaign>"`; Kolby scores the six dimensions on top. Copy edits or re-staging after a PASS void it — re-run the gate.
- **Internal-only until OtherVenture clears:** build the engine, dial the Vibe query, pre-generate demos, draft the sequence — **send nothing externally** until launch (`processes/launch-runbook.md`).

## First moves (now, internal)
1. ✅ Vibe query dialed in (above) + 3 real FL targets seeded in the CRM as a proof sample.
2. the Founder okays a credit spend → export a real **qualified** list (e.g., 100–200 FL landscapers, enriched) — Reilly runs the qualification pass.
3. Pre-generate the personalized Instant Employee demos for the list (Mode A, batched).
4. Finalize Touch 1–4 copy + the SMS, stage in the sending tool (Instantly), **paused** until launch.
5. Run the pre-send eval gate on the staged batch (`processes/outbound/pre-send-eval-gate.md`) so a PASS artifact is ready the day the launch-gate clears — send is then one human click, not a scramble.
