# The yourco AI Audit — SOP (the diagnostic front door)

> A productized, **free**, fixed-scope **first engagement** (no charge while yourco is getting started — the Founder 2026-08-16, `decisions/2026-08-16_audit-is-free.md`): diagnose a business's single biggest revenue-killing bottleneck and hand them a prioritized roadmap of which AI employee(s) to build — *before* they commit to a build + retainer. It's Stage 1 (discovery) of the delivery loop, packaged as a sellable product. Owner: **Bella** (runs it — the Audit Lead) + **Polo** (prices it) + **the Founder** (approves the report); the converted engagement hands off to **Kimi** for the build. Pricing: `pricing/v0/audit.md` (Polo proposes; **no prices on the website**). The Audit *fee credits 100% toward the build/implementation fee* if they proceed on a **minimum 6-month engagement** (the Founder-locked 2026-06-16).

## Why it exists
- **A small first yes.** Cold SMB owners won't jump to "build + monthly retainer." They'll pay a little to find out where they're bleeding money. The diagnosis *is* the sales pitch.
- **It qualifies hard.** Someone who pays for an audit is a real buyer, not a tire-kicker.
- **It is the discovery we would do anyway.** It no longer funds itself — the Audit is free (2026-08-16) — but it still de-risks the build for both sides and produces the exact inputs the scaffolder needs. ⚠️ Free also removes the qualification a price used to provide: guard the calendar with the intake form, not the invoice.
- **It counter-positions** vs. the "install it, you run it" players (CharlieOS et al., `agents/brett/competitive-watch.md`): we diagnose *your* specific bottleneck and quantify it in *your* dollars, then operate the fix — not a generic template you install and maintain.

**The Audit is the MANDATORY front door for every engagement** (decision: `2026-06-16_audit-first-os-as-product.md`). It's not a cold-prospect-only path anymore — *everyone* starts here, because it's how we learn the business well enough to build the **custom AI OS** (the product) via the scaffolder + Kimi. The fee credits the build (on a minimum 6-month engagement), so it's a smart first step, not a tollbooth. **Hot warm-intros** (e.g. Sample Client) can fast-track/compress it, but still run it. Steer the resulting build toward a **multi-agent AI OS**, not a single employee (single = the entry rung — a fine place to land, never the opener).

## The flow (≈1 week, ~4–6 hrs of the client's time)
```
Pre-call intake form (async, ~10 min)  →  Diagnostic call 1 (60–90 min)  →
  yourco analysis (offline)  →  Findings call 2 (45–60 min: present the report)  →
  Audit Report delivered  →  proposal for the first build (no audit fee to credit — the Audit is free)
```

## Step 0 — The online Revenue Leak Snapshot ⛔ PARKED — this step does not currently run

> **`snapshot.html` is not live.** It was dialled back to
> `agents/webb/pages/yourco-site-v2/_parked/` on 2026-06-22 along with the rest of the per-vertical
> funnel (`verticals.html`, `vertical-template.html`) — `decisions/2026-06-22_website-dial-back.md`
> — and the per-vertical *targeting* it assumed was retired on 2026-08-05. `snapshot-config.js` is
> kept for a possible future **generic** leak tool, and `runtime/snapshot_intake.py` sits idle.
>
> **In practice the Audit starts at Step 1.** Keep reading this step only if you are rebuilding the
> self-serve front door; do not describe it to a prospect as something they can go and do.
Before the Audit, prospects can take a **free online Revenue Leak Snapshot** on their vertical's landing page (`agents/webb/pages/yourco-site-v2/_parked/snapshot.html`, content in `snapshot-config.js`). It asks ~6 **vertical-specific** questions, gates the findings behind **name + email + business**, and renders an **instant yourco-branded snapshot report**: the likely leaks, the **dollar leak computed from their own inputs (math shown)**, **potential outcomes + ROI** with yourco, and a few **hard-hitting vertical stat-facts** (each cited — `[verify]` until Bella sources it). On completion the lead is **written to the CRM (source "online snapshot", owner Bella)** and the findings are **Slacked + emailed to the Founder** (staged handler: `runtime/snapshot_intake.py`). It is *not* the full audit — it's the teaser that earns the discovery call, then this SOP takes over. Decision: `decisions/2026-06-16_online-snapshot.md`. Owner: **Bella**.

## Step 1 — Pre-call intake (async)
The prospect fills the intake form (`agents/webb/pages/yourco-site-v2/audit-intake.html`) before call 1, so we walk in warm. It captures: business + vertical, size/revenue band, the tools they use, where time goes, what breaks, their #1 frustration, and — added 2026-08-10 — **up to three jobs they'd hand over, each scored on the delegation 2×2** (hours a month × how bad if it goes wrong unwatched). The form returns the verdict **live, before the call**: start here · built-but-you-approve · keep this one · leave it. So Bella walks in with the client's own sorting already done, and the approval-gate conversation has already started — including the *"keep this one"* verdict, which recommends against us and is what makes the other three credible. Bella reviews it + does a 15-min public-data scan (site, reviews, hours) before the call. For the site piece: `python3 runtime/firecrawl.py --crawl <their-site> --limit 15 --out-dir clients/<prospect>/site-crawl/` pulls the prospect's own site to agent-readable markdown (sanctioned path + bounds: `decisions/2026-07-05_tool-triage.md`; the connector refuses ToS-gated platforms by design).

> **Intake → CRM (capture spec).** A submitted intake is a *warm, contactable* lead (they gave name + email), so it goes **straight into the CRM** (David): a company + contact (status **"audit lead — follow up"**, source "audit-intake") + a **task on Bella/the Founder to book the diagnostic call**. This is the one inbound path that lands directly in the CRM (it has contact info + intent — the contact-info gate is satisfied). **Currently staged:** the form POSTs to `/api/audit-intake`; the live CRM write activates when the website is deployed (no backend until then). Same pattern as the "see yours" / referral captures.

## Step 2 — Diagnostic call 1 (60–90 min) — the questions
Run these in order. Listen for **where money leaks, where time goes, and what only-the-owner can do.**

**A. The money map**
1. Walk me through how a customer goes from "never heard of you" to "paid you." Where do they come from?
2. Roughly how many inquiries/leads a month? How many turn into customers?
3. What's an average job/customer worth to you?
4. Where in that journey do you *lose* people — and do you know why?

**B. The time map**
5. What do you (the owner) spend the most time on that isn't the actual work / isn't growth?
6. What happens to a call/message that comes in while you're on a job or after hours?
7. What's the task you most dread or keep putting off?
8. If you cloned yourself, what would the clone do first?

**C. The breakage map**
9. What falls through the cracks when you're busy? (follow-ups, quotes, scheduling, invoicing?)
10. What's something a customer complained about that was really an *ops* problem, not a quality one?
11. What's the bottleneck that, if it vanished, would let you take on more work *today*?

**D. The readiness check**
12. What tools/software do you already pay for? (CRM, scheduling, email, phone, etc.)
13. Who else touches these processes — just you, or a team?
14. If we fixed the #1 thing in 48 hours, what would "it's working" look like to you?

**E. The control map** (added 2026-08-24 — ask this on call 1, always. See §Step 4b for what the answers become.)

> Why it belongs in a diagnostic: the first four blocks find what to build. This one finds **what the
> client will let it do** — and if it isn't settled here, on the record, it gets settled ad hoc during
> build by whoever happens to be in the room. Ask it in the owner's language. Never say "autonomy rung,"
> "guardrail," or "governance" on this call.

15. When we build this, what should it be able to just *do* — and what should always come to you first?
16. Is there anything it should **never** touch, no matter how well it works? *(moving money, changing
    prices, firing a customer, anything legal or medical — let them name their own.)*
17. Today, who's the last set of eyes before something goes to a customer? What do they actually catch?
18. Would you rather it move fast and you catch the occasional mistake, or check with you first and move
    slower? *(Ask again for internal work vs. anything a customer sees — the answer usually flips.)*
19. If it got something wrong in front of a customer, what does that cost you — a shrug, an apology, or
    the account? *(This is blast radius in their words. Do not supply the word.)*
20. When something does go wrong, who do you want to hear it from, and how fast?
21. What would you need to *see* before you'd let it handle [their answer to 15] without asking you?
    *(The single most valuable answer in the block — it is the promotion criterion, in writing, on day
    one. Write it down verbatim.)*
22. Six months from now, what should you have stopped doing entirely?

## Step 3 — Bottleneck scoring (offline) — the framework
Score each candidate bottleneck on four axes (1–5), then rank. **Heat = Money × Frequency × Owner-drain × Fixability.**

| Axis | 1 (low) | 5 (high) |
|---|---|---|
| **Money at stake** | pennies | a big chunk of revenue leaks here |
| **Frequency** | rare | happens daily / every lead |
| **Owner-drain** | a helper could do it | only the owner does it / it eats their day |
| **Fixability (yourco)** | needs deep human judgment | clean, repeatable, automatable now |

For the top bottleneck, **quantify the dollar cost** in their numbers (see the Report template): e.g. *30 missed calls/mo × 30% would've booked × $1,000 avg job = $9,000/mo leaking.* That number is the whole pitch.

## Step 4 — Map bottlenecks → recommended agents
Translate the top 1–3 bottlenecks into named yourco employees / Tier-2 shapes (`clients/_yourco-template/employee-patterns-tier2.md`):

| Bottleneck pattern | Recommended employee |
|---|---|
| Missed calls / after-hours / slow response | **Front-desk / intake agent** (Vapi voice or text) |
| Slow quotes/estimates / proposal admin | **Estimate/proposal agent** (Beam/Forge shape) |
| Lead follow-up falling through | **Nurture/follow-up agent** |
| Manual scheduling / no-shows | **Scheduling + recall agent** |
| Marketing/content not happening | **Content/social agent** (Sloane/Lux/Saveur shape) |
| Back-office (invoicing/AR/data entry) | **Back-office agent** (Harry shape) |
| "I can't see what's happening" | **Reporting/ops dashboard** |
Always recommend **one** first build (the highest-heat, cleanest win) — the 48-hour go-live — then a phased roadmap for the rest.

### The build-vs-rent teardown lens (Bella; added 2026-08-07)
> Alongside workflow bottlenecks, look for the **angry invoice** — an overpriced single-workflow SaaS the client half-uses. It's often the sharpest, most quantified entry point of the whole Audit, and it feeds the **SaaS-replacement wedge** (`processes/new-offering-lines.md` B7, decision `decisions/2026-08-07_saas-replacement-wedge.md`).

- **Surface it in Step 2:** ask what tools they pay for, which they resent, and *which screens/workflows their team actually touches* (usually a fraction of the product). Capture the annual cost.
- **Score for replaceability (the qualification filter — clonable tier ONLY):** a candidate qualifies only if it's a **single-workflow horizontal tool** — form builder, scheduler, e-sign, approval flow, internal dashboard, reporting layer, light project tracker. **Disqualify** systems of record, compliance-locked tools, and anything with real network effects — those are where a replacement loses data and burns the brand. When in doubt, disqualify.
- **Frame the finding, don't clone:** *"you pay $X/yr for [category tool]; your team uses these N workflows; we'd rebuild those as a module you own and we operate, for less than the renewal."* Describe **workflows, never the incumbent's screens or product name** (clean-room; the legal guardrail). Quantify against *their* invoice — no fabricated numbers (same rule as the dollar-cost math).
- **It lands as an owned, operated module** (form factor 2/3), not a hand-off — the roadmap then expands into the pillars around it. ⚠️ Do **not** promise "you own it" until counsel-gate #13 (ownership/IP terms) clears.

### The delegation triage — the 2×2 an owner can apply in thirty seconds (Bella; added 2026-08-10)
> Pattern taken from a competitor's playbook (Altari, `decisions/2026-07-05_tool-triage.md` addendum 2026-08-10). It is our **autonomy matrix** made explainable without the matrix. Ask two questions about each piece of work the owner describes:
> **(1) How many hours a month does it eat? (2) If it goes wrong at 3am with nobody watching, how bad is it?**

- **High hours · low damage** → the first module. Research, monitoring, drafting, formatting — nothing leaves the building. This is where engagement #1 should start.
- **High hours · high damage** → a module **behind the approval gate**. Same work, but the last click is the client's. This is the quadrant that sells the moat: it is the only one a no-code operator cannot serve safely, and the owner arrives at that conclusion themselves rather than being told it.
- **Low hours · high damage** → they keep it. Say so plainly. Recommending against ourselves in this quadrant is what makes the other three credible.
- **Low hours · low damage** → not worth the setup, ours or theirs.

**Why it earns a place in the Audit:** the client sorts their own work, in their own words, and the output is simultaneously the module roadmap *and* the rationale for where the approval gates go. It also pre-frames the autonomy ladder — full autonomy is where an action *arrives* on eval evidence, never where it starts. ⚠ Use the plain 2×2 in the room; `processes/autonomy-matrix.md` remains the governing document and is not simplified by this.

### The full spend teardown (Bella + Charles; added 2026-08-08 — supersedes nothing, widens the lens above)
> the Founder's ruling 2026-08-08: don't stop at the angry invoice, and don't stop at the AI they've bought — **tear down the entire stack**. Every tool, seat, subscription, retainer and service. The conversation then asks for **no new budget**, which is the only cold open available to a business that has none. Tool: `python3 runtime/spend_teardown.py --inventory <their-stack.json>` (`--example` prints the schema). Full offering: `offerings/spend-teardown/SPEC.md` (frontier #23).

- **Build the inventory in Step 2** — walk their card statement, app list and vendor invoices with them (30–45 min). Per line: annual cost, seats, seats *actually* used, which screens/workflows get touched, what it overlaps with, and whether it's an AI tool and a sanctioned one.
- **Three columns, and they are NEVER summed.** **Evidenced cash** (money that provably left — a duplicate payment, a reconciliation error; Sample Realty's −$1,830.51 is the reference case). **Evidenced idle** (idle seats at their own per-seat price — evidenced as *idle*, **not** as *recoverable*: seat minimums and renewal terms decide that, and we check before quoting it as a saving). **Modelled** (what consolidation might return, gross, before build and operating cost). A blended headline is the number that dies on the first real question.
- **Governance is the finding that converts.** Flag unsanctioned AI tools, and flag hard where customer data is being entered into one. That is a risk the owner didn't know they had rather than a cost they'd accepted — and it routes straight to the approval-gate/eval/audit-log layer, which is the moat. State what's happening; no invented breach stats, no liability opinions.
- **The replaceability fence is the same one as above** and is enforced in code: clonable tier only; systems of record, compliance-locked tools, payments rails and network-effect products are marked out of scope and cannot be overridden by an optimistic input. Gate #13 still governs any "you own it" promise.
- **Never contingency-priced.** A percentage of found money would give us a reason to inflate the found column. The teardown runs inside the Audit fee.

### The calibration wager — capture at Step 2, settle at 90 days (Bella + Kolby; added 2026-08-08)
> Ten questions the owner is certain about, answered in their numbers, in writing, before anything is instrumented — then scored against their own records. Tool: `python3 crm/wager.py --questions` / `--open <dealId> --answers`. Offering: `offerings/calibration-wager/SPEC.md` (frontier #25).

- **Ask the ten in Step 2** and record them verbatim. They are the audit's before-picture and cost one conversation.
- **State yourco's own measured calibration bias first**, from the trust ledger. A wager offered by a party unwilling to be scored is a trap, and the owner will read it as one.
- **Never ask a question we cannot settle.** If we can't instrument it inside the window, it isn't asked — asking manufactures a debt we default on.
- **Unmeasured is reported unmeasured, never wrong** (enforced in the tool). If we failed to instrument it, that's our failure and the settlement says so.

### Preserve the baseline — immutably (added 2026-08-08; this is the only part of batch 5 that needs doing today)
> Every audit's quantified bottlenecks, wager answers and spend inventory are the **baseline the Re-Audit differences against at renewal** (`offerings/re-audit/SPEC.md`, frontier #31). Write them once, date them, and **never retro-edit them** — not to correct a wording, not to reflect what we learned later. A re-audit against a tidied-up baseline is worthless, and a day-one *estimate* silently reported later as if it had been a *measurement* manufactures a flattering delta out of a methodology change. Label estimates as estimates at capture time so the renewal comparison stays honest.

## Step 4a — The narrative frame: one connected picture that learns (the ontology + the write-back loop)
How Bella (and the Founder) *tell* the findings — the story that turns a bottleneck list into an OS sale. Internal shorthand: the **"Palantir-for-X" pattern** (integrate → model as objects+links → intelligence layer → write back so it compounds; `decisions/2026-07-05_tool-triage.md` §Base44 addendum). Never name-drop Palantir to an SMB owner — use the plain language below.

**The three beats of the findings call:**
1. **"Here's your business as one connected picture."** The diagnostic calls already produced it: the *things* (a lead, a call, a quote, a job, an invoice, a customer) and the *links between them* (a call becomes a booked estimate; a quote becomes a job; a job becomes an invoice; a happy customer becomes a review and a referral). Draw it — literally, in the report. **A bottleneck is a broken link in that picture**, and the dollar quantification (Step 3) is the cost of that one broken link. This lands because no tool they've bought has ever shown them their own business this way — each tool sees one box, never the links.
2. **"A system, not a tool — because the leak is in the links."** The reason the pile of software they already pay for (Step 2, question 12) didn't fix it: each tool works *inside* one box; the money leaks *between* boxes. What yourco builds watches the whole picture and acts across the links — that's what makes it an operating system rather than another subscription. (This is also the honest explanation of why we recommend a *system or its first module*, not a gadget.)
3. **"And it compounds — everything it does gets written back."** Every call answered, quote sent, follow-up made, and its *outcome* is recorded into the same picture. So the system doesn't just run your business — it **learns** it: which follow-up timing books jobs, which quotes stall, where the next leak is opening. **Month three is better than month one, automatically.** This is the beat that justifies the operated retainer — a template you install stays as smart as the day you installed it; the loop is the part DIY skips, and the part we operate. (It's the moat argument — reliability/eval/write-back — in owner language.)

**Why this frame wins:** it explains OS > tools without jargon; it makes expansion natural (the other weak links are already visible on the same picture — land-and-expand is just "want us to fix the next one?"); and it pre-answers "why a monthly fee" (you're paying for the loop that compounds, not for software that sits there).

**Worked one-liner (hardscaper example):** *"Thirty calls a month hit a dead end after hours — that link, calls→booked estimates, is where $9k/mo leaks. We start by fixing that one link, live in 48 hours. Everything the system does writes back into the picture, so by month three it knows your seasons, your good leads, and your slow payers — and we'll be showing you the next link worth fixing."*

**Language guardrails:** by-function only (external-surface rules — no internal agent names); "one connected picture of your business," "a system that learns your business," "every action writes back"; never "ontology," "knowledge graph," or "Palantir" on a call.

## Step 4b — The control map: turning Block E into rungs (added 2026-08-24)

Block E is not a comfort exercise. Every answer has a destination, and the mapping is mechanical:

| Their answer | Becomes | Where it lands |
|---|---|---|
| **Q16** — what it must never touch | the client's **deny-list**, enforced in config, not in a prompt | the build's guardrail layer; nothing promotes past it at any rung |
| **Q15 + Q18** — do on its own vs. come to you | the **starting rung** per action class | `processes/autonomy-matrix.md` §Default starting rungs |
| **Q19** — what a customer-facing mistake costs | **blast radius** → anything irreversible or customer-facing starts at the **R1 floor** | the R1 hard floor, no exceptions on day one |
| **Q21** — what they'd need to see | the **promotion criterion**, verbatim → the eval target that earns R2 | the streak rule + `runtime/agent_calibration.py` |
| **Q20** — who hears about failures, how fast | the **exception route** (who is notified, on what channel, in what window) | watchdog + notification config |
| **Q22** — what they've stopped doing | the **trajectory**, and the honest measure of whether the OS worked | the counterfactual twin's baseline; the 90-day review |

**Q21 is the one that matters most.** It converts "trust us" into a written, testable condition the
client set themselves — which is the whole autonomy argument made legible without ever using the word.
When the criterion is met, the promotion is a conversation about evidence they already agreed to, not a
request for more faith. **Record it verbatim; do not paraphrase it into something easier to satisfy.**

**Two failure modes to avoid.** First, *don't sell the moat here* — this block is diagnosis, and turning
it into a pitch for reliability makes the client defensive about answering honestly. Second, **don't let
an eager client talk you above the floor.** An owner who says "just let it do everything" on call 1 is
describing a wish, not a control decision; day-one full autonomy on high-stakes actions is the named
moat-killer (`decisions/2026-06-25_autonomy-by-default-standard.md`). Record the wish as the *destination*
— that is exactly what Q21 is for.

**It also front-loads the client trip-wires.** Q16 and Q21 are precisely the inputs
`runtime/client_tripwires.py` and `clients/_yourco-template/client-tripwires.md` need and which today
start empty. A criterion nobody wrote down is a fact nobody measures, and an unmeasured fact reads
`unmeasured` forever.

## Step 5 — Findings call 2 + the report
Present the **Audit Report** (`clients/_yourco-template/audit-report/`): the diagnosed bottlenecks, the dollar cost of the top one, the **signal inventory**, the prioritized agent roadmap, and the proposed first build — told through the Step-4a frame (the connected picture → the broken link → the loop that compounds). End with the offer: *"Here's the one we'd build first, live in 48 hours — and your audit fee comes off the build."*

### The signal inventory (Bella; added 2026-07-23)
A short table between the math and the roadmap: **the data the business already records** (phone log/voicemail, quotes won/lost, customer texts/emails, invoices/job history, reviews) → **what each has been telling them** → **which roadmap phase puts it to work**. Sourced from the "Signal Was Always There" triage (`decisions/2026-07-05_tool-triage.md` §Addendum 07-23): the owner's problem is never missing data — it's that nothing listens to the data they already have. Why it earns its place under the delete-pass rule: (1) it proves the diagnosis came from *their* records, not a template; (2) it pre-answers "do we need to set up new tracking first?" — no, day one works with what exists; (3) it makes Step-4a beat 3 concrete — these are the exact streams the write-back loop compounds on. **Bounds:** 4–6 rows max, only sources that actually surfaced in *this* diagnosis, every row mapped to a roadmap phase or to the audit itself — never a generic "AI can read your data" list.

### Report clarity — the delete-pass (Bella + Webb; added 2026-07-16)
> *"A confused mind doesn't buy — and a confused mind doesn't implement, doesn't get the ROI, and doesn't expand."* Borrowed from the Gannon assessment teardown (`decisions/2026-07-05_tool-triage.md` §Addendum 07-16), where the report was iterated **12 times asking only "what can I delete?"** — the single highest-leverage thing in an otherwise-inferior offer. Our report has never had that pass.

- **Run an explicit delete-pass** before the template is used on a real client: for every element ask *what can be deleted / merged / reordered* so the bottleneck and its dollar cost land in one glance. Fewer, sharper slides beat completeness — the report is a decision aid, not a record.
- **Put a one-word `primary focus` on the executive summary.** Our 4-axis scoring (Money × Frequency × Owner-drain × Fixability, Step 3) is **internal** and stays internal; the client-facing summary should name which single lever the roadmap pulls: **money** (effectiveness) · **time** (efficiency) · **quality** · **risk** (fewer errors, nothing sent unchecked — the approval-gate value said as a client outcome; added 2026-07-14 from the FDE-playbook triage: businesses measure AI in exactly three buckets — revenue uplift, cost savings, risk mitigation — and our reporting language should live in those buckets too). It gives the owner the "what do I get" answer before they read a word of detail.
- **Report every recommended build's expected outcome in the three buckets** (revenue uplift · cost savings · risk mitigation) — and carry the same three buckets through to the live client's monthly report, so the audit's promise and the operating system's proof use one language end-to-end.
- **Guardrail unchanged:** simplification never means invented numbers or dropped math — the dollar cost still uses *their* inputs and still shows its work.
- *Not* borrowed: their "4-day quick-start plan" solves a problem we don't have — their client self-implements off-the-shelf tools; **we operate the fix**. The yourco analogue, if any, is a first-week momentum view in the client console, not a homework list.

### The do-today box (Bella; added 2026-07-20)
The report includes a small **"Do these today — no yourco needed"** box: 2–3 concrete, copy-paste-ready fixes from the diagnosis the owner can execute themselves this week (e.g. a Google Business hours correction, a missed-call text-back their phone system already supports, one review-request template). Borrowed from CricketAI's "today's two highest-impact fixes" free drip (`decisions/2026-07-05_tool-triage.md` §Addendum 07-20). Why: it's the Block honest-diagnosis posture made tangible — we hand over real value they can verify *before* buying anything, it proves the diagnosis touched their actual business (not a template), and it sharpens the contrast with tool-prescribers whose "fix" is another subscription. **Bounds:** the fixes are owner-executable and small — never a free sample of the build itself, and never a homework list that shifts the operated work onto them (the roadmap stays the sale).

## Step 6 — Record it, or the Audit is uncountable (added 2026-08-25)

**The moment the report is in the prospect's hands, log an `Audit delivered` activity on their
company in the CRM**, with the path to the report in the summary.

This is one line and it is the entire measurement. The Audit is free, it is the front door of the
whole motion, and until 2026-08-25 nothing in the OS counted one — so *"how many audits become
engagements"*, the single most important unmeasured number in the company, was **unknowable rather
than merely unknown**. It is Bella's owned number (`runtime/agent-registry.json` → `agent_metrics`,
rendered on HQ → Agents), and it computes from these activities against the companies that later
reach a signed stage.

- **`Audit requested` ≠ `Audit delivered`.** The site's intake form writes the first; only a human
  writes the second. A request that never became an audit is a different failure from an audit that
  never became an engagement, and conflating them hides whichever one is actually happening.
- **Log it even when the answer was "we can't help you."** An honest no is still an audit delivered,
  and a conversion rate that quietly drops the ones that didn't sell is not a conversion rate.
- **No rate is reported below three audits** — a conversion off one is a coin flip wearing a
  percentage.

## Guardrails
- **Honest diagnosis.** If yourco can't meaningfully help, say so on the call and don't sell (CharlieOS does this too — it builds trust and protects the brand).
- **No fabricated numbers.** The dollar cost uses *their* inputs; show the math.
- **Report = drafts/approval.** the Founder approves the report before it's sent (brand + claims, `brand/writing-rules.md`).
- **Fee credits the build** — 100%, on a minimum 6-month engagement, so the Audit reads as a smart first step, not a tax.
- **Pricing is Polo's** — never quote a number that isn't Polo-locked; the website shows no prices.
