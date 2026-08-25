# The Referring Agent — Build Spec

**Working name:** The Referring Agent (frontier #26)
**Author:** the Founder
**Stack:** the connector program's existing R1 unlock (a real operated agent for the connector's own business, free while active — `processes/partnerships/connector-training/`) + one added capability: a **referral-surfacing pass that runs inside the partner's own tenant** and reports only to the partner · no yourco-side ingestion of the partner's client list
**Status:** Spec — roadmap row #26. Build trigger: **first professional-services partner conversation**. ⚠️ AICPA §1.520 flag applies to CPA partners.
**Pillar / form factor:** Sales (pillar 2) delivered as a partner-tenant module; form factor 2 (headless) with a short report surface.

---

## 1. Concept

yourco already gives R1 connectors a free operated agent for their own business, and already runs a connector ladder with training gates, an attribution log, and a 10/12.5/15% escalator. It has never connected those two facts for the highest-value partner type: the CPA, bookkeeper, or fractional CFO who *already sits on a book of a hundred SMB owners*.

The Referring Agent closes that gap. The partner's free agent does real work for their firm — intake, client onboarding paperwork, month-end chasing — and as a **byproduct of work it is already doing**, it surfaces the clients in their book showing the patterns yourco fixes: the ones whose bookkeeping arrives late every month because the owner is the bottleneck, the ones paying for four overlapping tools, the ones who mentioned they can't answer the phone.

The referral ask stops being *"please think of someone"* — the request every partner program dies on — and becomes *"your agent already named seven; do you want to introduce any of them?"*

**The architectural centrepiece, and the reason this is offerable at all: yourco never sees the book.** The pass runs in the partner's tenant, on the partner's data, and the output goes to the partner. yourco receives only what the partner chooses to hand over — a name, in a warm intro, the way it already works. There is no upload, no sync, no list.

## 2. Why it's never been done

Referral programs are built on the assumption that the partner does the identifying, from memory, unpaid, in gaps between real work. Every enablement kit in the category is an attempt to make that memory-work easier — a one-pager, a talk track, a "who to look for" checklist — and the reason they underperform is not motivation, it is that the partner is being asked to run a query against their own head.

Automating that query has always required the vendor to hold the partner's client list, which for a CPA or bookkeeper is professionally impossible: it is confidential client information, and handing it to a software vendor to be mined for leads is a straightforward breach. So the category has stalled at checklists.

The unlock is being an **operated** vendor that deploys inside the partner's own tenant. yourco is already running an agent in there. Pointing that agent at a question the partner wants answered, and returning the answer only to them, costs nothing structurally and is the one configuration in which the mining is not a breach — because no data moves and the partner is the only reader.

## 3. Build shape

| Piece | What it is | Notes |
|---|---|---|
| Base agent | The existing R1 unlock — a real operated module for the partner's own firm (their actual bottleneck, scoped in a short discovery) | Already specified; this rides it rather than adding a new give |
| Signal set | The patterns that indicate an yourco-shaped problem, expressed as questions over the partner's *own* workflow: chronically late document submission · owner-is-sole-contact · repeated "I'll get to it" · tool sprawl visible in the bookkeeping · after-hours activity | Written with the partner; they approve every signal before it runs |
| The pass | Scheduled run inside the partner tenant; produces a short ranked list **to the partner only** | No yourco endpoint receives it |
| The handover | Partner picks names and makes the intro themselves; the intro is what enters yourco's CRM, via the existing warm-lead path | Unchanged from today's flow — `promote-warm-lead` skill |
| Attribution | The existing connector attribution log records the intro; rungs compute from evidence as they already do | No new ledger |

**Effort band:** S on top of the base agent — the signal set is a conversation and a query, not a build. The base agent is the real cost, and it is already committed at R1.

## 4. Moat fit

- **It makes the highest-yield partner type actually productive.** A bookkeeper with a hundred-name book is the connector who can reach the 15% tier; a three-friend connector never will (`decisions/2026-07-20_in-person-local-gtm.md`).
- **It is a give, not an ask** — the partner gets a working agent for their own firm whether or not a single referral results, which is the only credible way to open a professional-services relationship pre-revenue.
- **Data posture is the differentiator.** "We never see your client list" is a sentence no lead-gen vendor can say, and it is the sentence that decides whether a CPA engages at all.
- **It dogfoods the tenant-isolation moat** in front of exactly the audience that evaluates such things professionally.
- **Interlocks:** the connector ladder + attribution log (already built) carry it; the Spend Teardown (#23) is the natural first engagement for any name the partner hands over; Patronage (#13) shares the third-party-channel logic.

## 5. Gates / compliance

- **⚠️ AICPA §1.520 (Commissions & Referral Fees) — the flag already logged.** A CPA must **disclose** a referral fee to the referred client, and may **not** accept one where they perform **attest** services for that client. Practical shape: favour **disclosed referrals for non-attest clients**, or a **reciprocal / non-fee** arrangement. **Ray confirms before any CPA-firm referral agreement is papered.** Florida Board of Accountancy has parallel rules. Note this is CPA-specific — bookkeepers, coaches and most other connectors do not carry it.
- **Referral-program counsel gates still apply** — the 1% downline override remains 🔴 (gate #5). This offering must work with the **flat, single-level** escalator so it is not blocked behind the MLM gate.
- **No data leaves the partner's tenant.** Enforced architecturally, stated in the partner agreement, and — because "we never see it" is a claim about a system — verifiable the same way the playground isolation check verifies yourco's own boundaries.
- **The partner approves every signal** before it runs. An agent that surfaces things the partner did not sanction is surveillance of their book by another name.
- **No contact with any surfaced name** unless the partner introduces them. yourco never receives, stores, or acts on an unsurfaced identity.

## 6. Pricing frame *(Polo)*

The base agent is **free while the connector is active** (existing R1 unlock, unchanged). The referral pass is included — pricing it would convert a give into a purchase and reintroduce the ask. yourco's return is the escalator it already pays on closed referred business, which is the only money that changes hands.

## 7. Activation trigger (build)

**First professional-services partner conversation** — a CPA, bookkeeper, or fractional CFO who reaches R1. Usable inside the launch-gate (1:1, unbranded, in-person), which makes it one of the few Reach instruments available before launch. The signal set should be drafted with the *first* such partner rather than pre-built, so it reflects a real firm's workflow instead of yourco's guess at one.

## 8. What we will NOT do

- **Never ingest, sync, copy, or receive the partner's client list.** Not in aggregate, not anonymised, not "just for scoring." The moment any of it lands on yourco's side, the offering is a breach with extra steps.
- **Never contact a surfaced name** unless the partner introduces them.
- **Never run an unapproved signal.** The partner sees and approves every question the agent asks of their data.
- **No silent commission with a CPA.** Disclosed or reciprocal, per §1.520 and Ray's ruling — never an undisclosed fee, and never a fee at all where they perform attest services for that client.
- **No downline/override structure attached to this** until gate #5 clears; it ships single-level or not at all.
- **No scoring or ranking of the partner's clients by "likelihood to buy"** in language the partner would be embarrassed to show a client. The output describes operational strain, not purchase propensity.
- **No withdrawal of the base agent as leverage** if referrals don't materialise. It is a give; a give with a hostage is an ask.
