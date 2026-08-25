# The Spend Teardown — Build Spec

**Working name:** The Spend Teardown (frontier #23)
**Author:** the Founder
**Stack:** no new runtime — `runtime/spend_teardown.py` (built 2026-08-08) + an Audit lens in `processes/audit-sop.md`; input is a hand-built inventory of the business's line items (their own invoices, bank export, app-store receipts, vendor list), output is a three-column teardown
**Status:** **BUILT** — roadmap row #23. Merges what began as two ideas (audit the AI they already bought · the found-money pass) into one instrument, per the Founder 2026-08-08: audit the **entire** stack, not just the AI.
**Pillar / form factor:** Back Office (pillar 6) feeding the Audit; form factor 3 (a document).

---

## 1. Concept

The hardest thing to ask a business with no AI budget line for is an AI budget line. So don't. Audit what they are **already paying** — every tool, seat, subscription, retainer, and service — and the conversation stops being about new spend and becomes about approved spend that nobody has looked at in two years.

The teardown produces three columns that are deliberately never summed:

- **Evidenced cash** — money that provably left. A duplicate invoice paid twice. A reconciliation error. (Sample Realty's trust-account review found −$1,830.51 of exactly this, out of her own ledger. That number is unarguable because it is hers.)
- **Evidenced idle** — spend against nothing: idle seats at a known per-seat price. Evidenced as *idle*, explicitly **not** as *recoverable* — whether it comes back depends on seat minimums and renewal terms, and the instrument says so before the owner asks.
- **Modelled** — what consolidating or replacing might return, stated gross, before what a replacement costs to build and operate. No net saving is claimed.

Alongside them, a **governance** block: unsanctioned AI tools in use, flagged hard when customer data is being entered into them — which is the finding that most reliably converts, because it is a risk the owner did not know they had rather than a cost they had accepted.

**The refusal that makes it credible:** a blended headline ("we found you $40,000!") is the number that dies on the first real question. The tool has no field for it.

## 2. Why it's never been done

Three adjacent things exist and none does this job. **SaaS-spend management** (Zylo, Vertice, Torii) is enterprise software sold to companies with a procurement function; it optimises licences and stops there, and an SMB has neither the seat count nor the budget to be a customer. **Bookkeepers** find reconciliation errors but have no view of the tool stack and no mandate to question it. **Shadow-AI audits** exist in enterprise security, aimed at policy compliance, and are unheard of at SMB scale.

Nobody joins them because for everyone else the three findings lead nowhere. A spend-management vendor that finds an idle tool sells you a dashboard about it; a bookkeeper hands you a memo. For yourco the findings lead somewhere specific and already-decided: the overpriced single-workflow tool becomes an owned-and-operated module (the B7 build-vs-rent wedge), and the unsanctioned AI tool becomes the governance layer that *is* the moat — approval gate, eval, audit log. The teardown is the only version of this audit where the diagnosis has a native treatment.

## 3. Build shape

| Piece | What it is | Status |
|---|---|---|
| Inventory schema | Line items: `name · annual · category · seats · seatsUsed · screensUsed/Total · overlapsWith · aiTool · sanctioned · customerDataEntered`; plus `findings[]` with a required `evidence` field | **built** — `--example` |
| Three-column analysis | Evidenced cash · evidenced idle (with recoverability caveat) · modelled gross | **built** — `analyse()` |
| Replaceability fence | `CLONABLE` tier (forms, scheduling, e-sign, approval flows, dashboards, reporting, trackers, intake, notifications) vs `OUT_OF_SCOPE` (system-of-record, compliance-locked, network-effect, payments) — **the fence cannot be overridden by input** | **built** |
| Governance flags | Unsanctioned AI tools; hard flag when customer data is being entered | **built** |
| Warnings | Any finding lacking an `evidence` field is called out — an undocumented found-money figure is the first thing challenged | **built** |
| Audit lens | The teardown as a named step in the Audit SOP, with the question list that produces the inventory | **sweep** — `processes/audit-sop.md` |

**Effort band:** S per teardown — the analysis is instant; the work is assembling the inventory with the owner (a 30–45 minute pass over their card statement and app list).

## 4. Moat fit

- **It is the cold-open that needs no budget.** The single best answer to the pre-revenue reach problem: an instrument that asks for zero new spend and reliably finds either money or a risk.
- **Feeds the wedge already decided.** B7 (`decisions/2026-08-07_saas-replacement-wedge.md`) needs an angry invoice to point at; this is the machine that finds it — and inherits B7's qualification fence verbatim, in code.
- **The governance finding sells the moat directly.** "Your team is pasting customer details into a consumer chatbot" converts into approval gates, audit logs, and eval — the layer no-code operators cannot deliver, arrived at from the client's own facts rather than from our brochure.
- **Interlocks:** Leak Meter (#16) instruments what this finds once live; the Simulated Company (#22) takes its cost side from the inventory; the Calibration Wager (#25) turns the owner's stack beliefs into scored predictions.

## 5. Gates / compliance

- **No new counsel gate for the teardown itself.** It reads documents the client hands over in a paid or founders' Audit.
- **⚠️ Gate #13 applies downstream.** The moment a teardown leads to "we'll build you a replacement you own," the ownership/IP + retainer terms are counsel-gated (`processes/counsel-gates.md` #13). The teardown may *name* a replaceable tool; no proposal may promise ownership until Polo + Ray rule.
- **Never name a competitor product as a clone target** in any written output (B7 guardrail 1, and the clone-a-thon's own top legal risk). Categories and the client's own workflow spec only.
- **Client financial records are confidential** — tenant-isolated, returned or destroyed on request, never used as an example without written permission. Figures in this spec's examples are synthetic except the Sample Realty finding, which is yourco's own client work.
- **Not tax or accounting advice.** Reconciliation findings route to their bookkeeper or CPA; yourco reports what the records show.

## 6. Pricing frame *(Polo locks)*

Runs **inside the Audit** at no separate charge — it is a lens, not a SKU, and the Audit is already the front door (**free** since 2026-08-16; return price $1,000/$1,500, `pricing/v0/audit.md`, waived for the first three warm-network prospects). Deliberately *not* priced on contingency: a percentage of "found money" would give yourco an incentive to inflate the found column, which is precisely the corruption the three-column separation exists to prevent.

## 7. Activation trigger (build)

**None — built.** Its *use* trigger is any Audit, and any in-person conversation where an owner complains about a tool, a renewal, or "we pay for that and nobody uses it." It is the designated instrument for the St Pete/Tampa in-person lane (`decisions/2026-07-20_in-person-local-gtm.md`), which was activated with no instrument attached.

## 8. What we will NOT do

- **Never blend the columns.** Evidenced cash, evidenced idle, and modelled savings are three different claims with three different strengths. There is no combined headline, and the tool has no field to hold one.
- **Never present idle seats as recoverable money.** Contract terms decide that, and they get checked before anything is quoted as a saving.
- **Never mark a system of record, compliance-locked tool, payments rail, or network-effect product replaceable** — regardless of what the input says or how much the owner wants it gone. That fence is the whole difference between a wedge and a weekend replacement that loses someone's data.
- **Never name a competitor's product as a clone target**, in writing or in copy.
- **No found-money figure without a document behind it.** The tool warns on any finding missing evidence; an unevidenced number is the first one challenged and it takes the credible ones down with it.
- **No contingency pricing** on findings, ever — it would corrupt the instrument.
- **No fear framing on the governance finding.** State what is happening and what it exposes; no invented breach statistics, no implied liability opinions.
