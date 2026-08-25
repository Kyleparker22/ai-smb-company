# The Receipts — Build Spec

**Working name:** The Receipts (frontier #17)
**Author:** the Founder
**Stack:** the existing approval-flow audit trail (the substrate — already written by every module from day one) · append-only evidence store (the audit log's existing storage, with retention/immutability posture hardened) · Claude API (assembly + narrative summarization of the record, draft replies) · export to timestamped PDF/packet · the standard moat layer (eval · approval · audit log — this product *is* the audit log, productized)
**Status:** Spec — see `offerings/_frontier-roadmap.md` row #17. Build trigger: **first signed client** (substrate is on from day one).
**Pillar / form factor:** Back Office (pillar 6) with a Customer-pillar face, shipped as form factor 2 (headless assembly on demand) plus a client-console "request a receipt" surface (form factor 3).

---

## 1. Concept

When a dispute hits a small business — a chargeback, a "you never told me that" invoice fight, a false one-star review, an insurance question, a customer claiming a quote said something it didn't — the owner loses not because they were wrong but because they can't *produce the record*. The evidence is scattered across a phone, an inbox, a texting app, and memory, and assembling it takes an evening they don't have, so they eat the chargeback and absorb the review.

The Receipts is **evidence-grade operations**: on a dispute event, the OS assembles the receipt in minutes — the call summary with its timestamp, the quote as approved and when, every confirmation sent and delivered, the change-order the customer okayed, the full interaction chain in order — as a clean, exportable, timestamped packet. The emotional pitch is one line: **never lose an argument you were right about.**

**Centerpiece one: the record already exists.** Every yourco module runs on the moat layer, which means every action — every draft, approval, send, call summary, status change — already lands in the audit trail, because that's how the OS proves itself to the client. The Receipts productizes that existing substrate. **Zero new capture**: no new logging system, no new instrumentation, no behavior change. The dispute-day capability is a *view* over what reliability discipline was writing anyway, which is why it can be "on from day one" of any signed engagement.

**Centerpiece two: integrity rules.** A record you can edit is not evidence. Receipts records are **append-only** — corrections are new entries that reference the old, never edits; nothing is retroactively altered, re-worded, or deleted inside retention. And **yourco never fabricates or reconstructs a record that wasn't captured**: if the interaction predates the OS or happened off-channel, the packet reports the gap as a gap ("no record of this interaction in the system"), full stop. The gap-honesty is what makes the rest of the packet worth anything.

## 2. Why it's never been done

Enterprise legal-hold and e-discovery tooling exists — at enterprise price, for enterprise counsel, disconnected from operations. SMB tools each hold a shard (the phone system has call logs, the CRM has emails, the invoicing app has invoices) and none can assemble a cross-channel chain, because no one system saw the whole interaction. The new fact is that an operated AI OS *is* the whole interaction layer — intake, quoting, confirmations, follow-ups all flow through it — and the reliability layer already timestamps and audit-logs everything as a condition of earning autonomy. Evidence-grade record-keeping falls out of the moat for free; no-code operators don't keep this trail (they have nothing to prove), and point tools can't see across channels. The product is the discipline, surfaced.

## 3. Build shape

| Piece | What it is | Notes |
|---|---|---|
| Substrate hardening | The existing per-client audit trail gets an evidence posture: append-only enforcement, correction-by-supersession, a defined retention window, integrity metadata (hashes, capture timestamps) | Template-level, once. This also raises the trail's quality for its day-job (eval/approval evidence). |
| Dispute intake | "Request a receipt" on the client console + a trigger word to the client's OS contact — client names the customer/job/date range | The client initiates. No always-on surveillance framing; assembly happens on request. |
| Assembly agent | Headless run: query the trail for the interaction chain (calls, quotes, approvals, messages, confirmations, deliveries) → order it → narrative summary up top, verbatim records beneath, gaps explicitly flagged | LLM summarizes and organizes; it never paraphrases *into* the record — verbatim entries stay verbatim, summary is labeled as summary. |
| Receipt packet | Timestamped PDF/HTML export: chain-of-events narrative · the exhibits · the gap report · an integrity note describing how records are kept | White-label, client brand. Plain language — a packet the owner can hand a card processor, a platform, or their own attorney. |
| Reply drafting | For review-platform responses and dispute correspondence: drafts grounded strictly in the packet's records | **R1 permanently** — human-approved before anything posts or sends (see §5). |
| Chargeback kit | Format presets for common demand shapes (card-processor rebuttal fields, review-platform response norms) | Formatting help only — no legal advice, no representation. |

**Data sources:** the client's own OS audit trail exclusively (call summaries, message/send logs, quote + approval records, invoice events). Nothing external, nothing reconstructed. **Effort band:** S — substrate hardening + packet template ~2–3 focused days into `_yourco-template`; per-client cost is ~zero (the substrate is on by default), per-dispute assembly is minutes by design.

## 4. Moat fit

- **This is the moat, sold.** Approval flows + audit logging exist because reliability demands them; The Receipts is the first product where the client *feels* that discipline directly. It makes the invisible layer emotionally legible — the strongest possible answer to "what am I paying the reliability tier for?"
- **Trust compounding:** the first dispute a client wins with a receipt converts the audit trail from yourco's compliance habit into the client's asset. Feeds Exit-Asset OS (#3): a business with evidence-grade records diligences cleaner and sells better.
- **No-code can't follow:** an operator with no eval/approval layer has no trail — they'd have to build capture as a feature, and a capture-feature record has none of the born-in-the-workflow credibility.
- **Model-upgrade dividend:** better models assemble and narrate the chain better; the records themselves are deterministic logs, untouched by model churn.
- **Interlocks:** Self-Proving Invoice (#4) draws on the same trail; Trust Ledger (#1) is the same posture at company level; Leak Meter (#16) shares the event stream.

## 5. Gates / compliance

- **No new counsel gates.** Two scope-riders on **gate #1** (`processes/counsel-gates.md`, legal suite review): (a) **recording-consent language rides gate #1** exactly as already logged in the 2026-08-06 update for interviewable-employee/secret-shopper — Florida is two-party-consent, so v1 evidence scope is **written artifacts + system events only**; call *summaries* generated by consented voice-agent interactions are in scope only where the consent posture covering them is counsel-cleared, and no recording capability is added for this product; (b) the engagement agreement's retention/records clause should state the append-only posture, the retention window, and who owns the records (the client).
- **Not legal advice, ever:** packets organize the client's own records. No opinions on the merits, no representation, no "you'll win this." The packet's integrity note says what the system captures and how — it makes no admissibility claims.
- **Review-platform replies stay R1 permanently** — human-approved, no autonomy climb on public-posting actions (reputational, irreversible: standard matrix rule for high-stakes external surfaces).
- Customer PII inside packets is handled per house standard: tenant-isolated, released only to the client, who decides where it goes.
- White-label: packets carry the client's brand only (external-surface rules).

## 6. Pricing frame *(assumption-stated; Polo locks before first proposal)*

The substrate is **included in every OS retainer** — it exists anyway; charging for its existence is charging twice for reliability. What's priced is the capability tier: a **Receipts add-on band** (illustrative: low hundreds/mo) covering the console surface, unlimited assemblies, and reply drafting — or fold into Suite-and-up OS tiers as a named inclusion, with per-packet assembly (illustrative: tens-to-low-hundreds per packet) for Core-tier clients. Insurance-shaped value ("the month it saves one chargeback it paid for the quarter") is the framing, stated as framing — no promised win rates. All figures illustrative until first-ten-clients evidence; Polo prices.

## 7. Activation trigger (build)

**First signed client** — exactly as the roadmap row states. The substrate (audit trail) turns on at go-live as a property of every engagement, so evidence accrues from day one whether or not the client buys the add-on; the packet/assembly layer can be template-built before signing per the hooks-predate-clients sequencing rule. Recording-consent language travels with the gate-#1 counsel package (roadmap row note).

## 8. What we will NOT do

- **No fabricated or reconstructed records — the hard line.** A gap in the record is reported as a gap. We never infer, backfill, "restore," or plausibly-reconstruct an interaction that wasn't captured, no matter how sure the client is that it happened, and no matter what's at stake in the dispute. A single reconstructed entry poisons every packet the system will ever produce.
- **No retroactive editing.** Append-only means append-only: corrections supersede, they never overwrite. There is no admin path that rewrites history — including for yourco.
- **No selective assembly presented as complete.** A packet includes the full responsive chain — including entries unhelpful to the client's position. The client chooses what to *do* with the packet; the packet itself doesn't curate.
- **No legal advice or merit opinions.** Records and formatting, not counsel. Anything resembling a legal question routes to the client's attorney.
- **No covert recording, no new capture.** Evidence scope is what consented, disclosed channels already produce. Nothing records anything because of this product.
- **No autonomous public posting.** Review replies and dispute correspondence are R1 forever.
- **No fear marketing with fake stakes.** External copy uses no invented dispute statistics or fabricated win stories (house rule; pre-revenue → qualitative).
- **No yourco branding on packets** or the console surface (white-label rule).
