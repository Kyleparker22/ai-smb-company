# 2026-08-24 — Competitor MSA teardown: five clauses adopted, the IP posture explicitly rejected

**Decision** — the Founder reviewed an executed **Master Services Agreement + SOW** from **Pulse Consulting**
(Kevin Hart, Prosper TX) to **Sample Contact**, dated 2025-08-15, $6,000/mo retainer. Five structural
ideas are adopted into yourco's existing contract stack; the counterparty's IP posture is **rejected on
the record** rather than quietly not-copied. **Structure and ideas only — no text was taken from that
document**, which is another firm's counsel's work product.

**Locks:** contract scope-control and acceptance

## Where it came from, and why that matters
the Founder's contact sent it as a sample. **The counterparty is already in yourco's CRM**: Sample Contact
exists twice — as a warm prospect at Sample Contact (`co-graymatter`) and as a **prospective connector**
tagged *"the rolodex IS the asset."* So this is not a generic sample; it is what a live prospect in
yourco's own pipeline was charged and agreed to by a direct competitor. Treat it as competitive
intelligence with a named source, and do not repeat its contents outside yourco.
*(CRM correction applied: his title reads **CFO** in the CRM and **Co-Founder / COO** on the signature
block. The document is the better source.)*

## Adopted — five clauses, all counsel-gated

| # | From | Into | Why |
|---|---|---|---|
| 1 | Change Orders (their §2.2) | Agreement **§1.1** | Neither yourco document contained the phrase *Change Order* at all. On a land-and-expand motion that is the missing scope-creep valve. |
| 2 | Multi-month expectation (their §2.3) | Agreement **§1.2** | States that a retainer month buys operation + a prioritised queue, not completion of an unbounded list. Pre-empts the most common retainer dispute. |
| 3 | Multi-tenant training ban (their §5.3/§6.2) | Agreement **§7** (widened) | yourco already banned foundation-model training but never said **multi-tenant / multi-client**, which is the phrasing that actually reassures a buyer and matches yourco's tenant-isolation moat. |
| 4 | Hallucination acknowledgement (their §7.3) | Agreement **§9** | yourco said *probabilistic* but never named hallucination. Naming it is stronger, not weaker. |
| 5 | — (their gap) | SOW **acceptance section** | See below. Not adopted *from* them; adopted *because* they had none. |

Plus one clause neither party had: **§3.1, the end-of-engagement handover.** yourco *operates* the
system, so "what happens if we stop?" is the first question a careful buyer asks and nothing answered it.
§3.1 now says what returns, what the client keeps (their accounts, numbers, tenant — always theirs), what
they receive in human-readable form, and — plainly — what does **not** transfer, and why: the employee
stops because it runs on yourco's infrastructure, which is the same reason the client never got a token
bill. That trade is stated in the sale, not discovered at the exit.

## Rejected on the record — their IP posture (their §4.3)
Their agreement gives the client only a **non-exclusive licence** to what was built, for internal use;
retains for the consultant every tool and method *"even if utilized in the creation of the Deliverables"*;
declares that **any raw or intermediate AI output is the sole property of the Consultant** — outputs
generated from the client's own data; and requires a **separate paid licence** if the client ever wants to
commercialise the system built for them, with a sales email address embedded in the contract.

yourco's §5 already takes the opposite position: **the client owns the work product the employee produces
for them.** Retaining platform IP is right and yourco does it. Claiming the client's AI output and
pre-monetising their own system back to them is extractive, and yourco's moat is *executive trust* — that
clause would cost more than it earns. **Do not import it, and do not let it drift in later** as
"industry standard."

## The finding that matters most: their document does not sell anything
Ten pages, and **no outcome, no baseline, no ROI, no payback, no success metric, no acceptance criteria,
no SLA.** Scope sells features (*"multi-agent system," "God View dashboard," "RBAC"*); Deliverables are
objects, not results (*"a deployed Agentic CS Platform with functional AI routing"*). Nothing defines what
working means. A client cannot tell what business result they bought for $72k/year.

That **validates `decisions/2026-07-20_two-sided-proposals.md`** — *"the cost number never travels alone"* —
and shows yourco is well ahead on the selling half. The gap ran the other way, which is why the work here
was contract-side, not sales-side.

## The acceptance section (SOW) — the one that changes how yourco sells
Go-live acceptance is now a table: what must be true · measured how · threshold, demonstrated against the
system's own records, with a client review window and a no-charge fix. Where acceptance is unmet **for
reasons within yourco's control**, the retainer does not start or is credited.

**The rule that keeps it honest:** *a criterion has to be measurable from the system's own records; if we
cannot measure it, it does not go in the table.* An acceptance test nobody can run is worse than none — it
moves the argument to the end of the engagement instead of settling it at the start. This is the same
refusal discipline the Evidence layer and the connector console already run on.

⚠️ **This section commits yourco to a definition of done, and the credit remedy is a fee term.** It is the
sharpest new obligation in the stack and the reason the whole change is counsel-gated.

## What was NOT copied, deliberately
Their 7-day payment terms; mandatory AAA arbitration venued in the consultant's home county; consultant-only
termination for convenience; and their drafting errors — an initial term of *"one (1) mont"*, *"at least
sixty (30) days"* in the same sentence, a warranty cross-reference pointing at the wrong section, and the
consultant's own name filled into the client's Project Lead field on the signed exhibit. The lesson taken
instead: **yourco's templates need a proofread gate before send.**

## Obligations
1. **Ray reviews before any of it goes out.** §3.1 and the SOW acceptance-credit remedy are the two that
   most need counsel — both create obligations that outlast termination or touch fees.
2. **The architecture question stays open.** `engagement-agreement.md`'s header has asked since 2026-06-11
   whether to split into MSA + per-engagement SOWs. Their document is a working example of the split, and
   the land-and-expand motion argues for it: sign terms once, add a SOW per module. Still the Founder's + counsel's
   call; nothing here presumes it.
3. **~~No SLA was written.~~ SLA written 2026-08-24 at the Founder's direction** — `processes/contracts/sla.md`,
   attached to the Agreement (§10) and summarised in the proposal. Targets: **99.5%** monthly availability
   on the layer yourco operates; **1 business hour** to a human on P1, 4 on P2, 1 business day on P3;
   credits capped at 50% of a month; and an **immediate termination right** after three consecutive missed
   months, because a discount on a service that does not work is not a remedy.

   **99.5% and not 99.9% is deliberate.** 99.9% allows 43 minutes a month and needs redundancy plus
   someone on call. yourco is one operator on one host with no failover, so 99.9% would be a number we
   intend rather than one we can hold. Raise it when the architecture earns it.

   ⚠️ **It is marked NOT SENDABLE, and that is the honest state.** There is **no uptime monitoring
   anywhere in `runtime/`** — no health check, no heartbeat, no alerting — and no incident record, so
   neither the availability clock nor the response clock can be computed. Under the SLA's own §6 an
   unmeasured month counts as a **miss**, which means shipping this today would be writing ourselves a
   monthly penalty. Preconditions and owners are in `sla.md` §7: **Kemba** (monitoring + alerting),
   **Kolby** (the incident record — it is eval/observability work), **Ray** (the document), **the Founder**
   (locks the numbers and the failover call).

   The rule this obeys is the one written into the acceptance section the same day: *if we cannot measure
   it, it does not go in the table.* The SLA exists so the commitment is drafted and priced; it stays
   behind a red gate until the instrumentation makes it true.

## Trip-wire
- **Review:** 2026-11-24
- **Overturn if:** the acceptance table stalls deals rather than closing them (prospects negotiating
  thresholds instead of signing); **or** a Change Order is ever used to bill for something the client
  reasonably read as ordinary iteration, which would mean the §1.1 test is drawn in the wrong place.
- **Check:** `signedClients >= 1`
- **Check covers:** only that a contract has actually been signed under these terms — the point at which
  either condition can be observed at all. It covers **neither** overturn condition; both need a human to
  notice how a live negotiation went.
