# Patronage — Build Spec

**Working name:** Patronage (frontier #13)
**Author:** the Founder
**Stack:** no new runtime — the standard golden-template delivery per sponsored SMB · a sponsor-facing portfolio report compiler (quarterly loop over per-client artifacts, aggregation layer enforcing the privacy wall) · CRM (sponsor = a B2B account; each sponsored SMB = its own normal client row) · sponsor one-pager + package sheet (Polo bands)
**Status:** Spec — see `offerings/_frontier-roadmap.md` row #13. Build trigger: **Launch; sponsor conversations may pre-stage via warm network.**
**Pillar / form factor:** a funding/channel layer over the whole catalog — the delivered thing per SMB is a normal first module in any of the three form factors; the sponsor buys distribution, not product.

---

## 1. Concept

The institutions that already hold portfolios of local SMBs — **community banks, insurers, chambers of commerce, franchisors** — pay for those SMBs' first yourco modules. One B2B check funds ten or fifty first modules; yourco lands a portfolio of clients through a single trusted introduction; the SMB gets its first agent at zero cost with the endorsement of an institution it already trusts. Everyone's incentive is real and stated: the bank wants healthier borrowers (an SMB whose intake and invoicing run doesn't miss loan payments), the insurer wants lower operational risk in its book, the chamber wants a member benefit that actually retains members, the franchisor wants unit-economics consistency across the system. yourco gets the two things pre-revenue GTM lacks most — **CAC paid by a third party, and borrowed trust at first contact.**

The shape is patronage, not resale: the sponsor **funds** first modules for a defined portfolio; it does not own, operate, white-label-resell, or manage the engagements. Each sponsored SMB signs yourco's standard engagement agreement, gets the standard golden-template delivery with the full moat layer, and owns its own client relationship from day one — the sponsor bought the introduction and the first check, nothing else. Expansion beyond the sponsored module is a direct yourco↔SMB commercial relationship (§6), which is where the economics actually live.

## 2. Why it's never been done

Sponsored software for SMB portfolios exists in degenerate forms only: banks bundle discounted SaaS logins nobody activates; franchisors mandate tools that get resented; chambers hand out coupon codes. All fail the same way — **a license is not an outcome**, so sponsored seats become unused seats and the sponsor learns "software perks don't move our portfolio." Sponsoring an *operated* outcome was never possible because operated meant human consultants, and no sponsor can fund consulting engagements across fifty SMBs — the cost structure is the same wall that keeps concierge services out of DTC (the yourco Care wedge, applied B2B2B). AI-native delivery collapses the per-SMB cost to where a portfolio sponsorship is a line item a marketing or member-benefits budget can carry, while the operated model guarantees the thing sponsors were always actually buying: **activation** — a named working agent producing evidenced outcomes, not a login. The second unlock is the reporting: yourco's eval/ledger layer can show a sponsor *portfolio-level, privacy-walled* proof that the benefit worked (aggregate modules live, aggregate outcome evidence) — the ROI artifact no coupon-code program ever produced. Nobody else has both the cost structure and the proof layer; that pairing is the offering.

## 3. Build shape

| Piece | What it is | Notes |
|---|---|---|
| Sponsor package sheet | Tiered packages by portfolio size — *(assumption-stated, Polo locks; illustrative shape:)* **Pilot** (~5–10 sponsored first modules) · **Portfolio** (~25–50) · **System** (franchisor-scale, negotiated) — each = funded first modules + the portfolio report + a bounded acknowledgment surface (§3.1) | Per-SMB delivery is the standard first-module scope regardless of tier; tiers scale count, not depth |
| Sponsor agreement | The B2B contract: what's funded, the portfolio definition, the privacy wall (§3.2) in writing, acknowledgment-surface bounds, term, and the explicit non-agency clause (sponsor has no direction rights over any engagement) | Joins gate #1's review batch (§5) |
| SMB onboarding path | Sponsor introduces → SMB **opts in** (never auto-enrolled) → standard audit-lite intake → standard engagement agreement (fee shown as sponsor-paid) → golden-template delivery | The SMB is a full client with full standing; declining costs it nothing with its sponsor — stated in the invite |
| Portfolio report compiler | Quarterly loop: per-client artifacts → **aggregates only** (modules live, activation rate, aggregate outcome evidence, anonymized pattern notes) → sponsor-facing report | The privacy wall is enforced in the compiler (aggregation floor, no per-SMB rows), not by editorial discipline |
| Acknowledgment surface | The one bounded co-branding artifact (§3.1) | Template, per-sponsor variant |
| CRM structure | Sponsor = B2B account with its own deal; each sponsored SMB = a normal company+deal row, channel-tagged | Expansion pipeline reads like any other client's |

### 3.1 Co-branding, reconciled with the white-label rule — explicitly

The house rule (external-surface rules, learned by violation): client-facing surfaces carry the client's brand only. Patronage does not breach it — it adds one **separate, bounded acknowledgment surface** and nothing else:

- **The SMB's operating surfaces stay 100% the SMB's brand.** The digital employee's name, mailbox, and everything the SMB's customers see: SMB brand only. No sponsor logo, no yourco logo. The sponsor never appears inside the delivered product.
- **The acknowledgment is its own artifact:** a line in the onboarding welcome and the SMB-facing monthly report — *"your first module is sponsored by [institution]"* — plus the sponsor's own marketing of the program to its portfolio (its newsletter, its member page). That is the entire co-brand footprint.
- **The sponsor may name the program; it may not brand the agent.** "The [Bank] Small Business AI Program, delivered by yourco" on the sponsor's page — fine. The bank's logo in the SMB's customer-facing chat — never.

### 3.2 The privacy wall (portfolio-level only)

The sponsor is often the SMB's **bank or insurer** — an entity with underwriting interest in exactly the operational data yourco now sees. Hard wall, in the sponsor agreement and in the compiler: the sponsor receives **aggregate, portfolio-level reporting only.** No per-SMB metrics, no per-SMB usage or outcome data, no "which of my borrowers is struggling," no ranked lists, no answering sponsor questions about a named SMB — ever, including verbally. Small-cohort reports aggregate up or omit rather than let a cohort of three be de-anonymized. Each SMB's engagement data belongs to that SMB under the standard agreement; the sponsor's check buys no window into it. If a sponsor's real goal in conversation turns out to be portfolio surveillance, the deal is declined (§8) — one leak here ends every future sponsorship and most future client trust.

**Data sources:** per-client delivery artifacts (already produced), aggregated per §3.2; sponsor CRM records. **Effort band:** S–M — package sheet + sponsor agreement draft + report compiler ~3–4 days; per-sponsored-SMB delivery is the already-costed standard first module, at portfolio cadence.

## 4. Moat fit

- **The sponsor is buying the moat, literally:** an institution putting its name on a program needs the vendor that can't blow up on its portfolio — reliability layer, approval gates, audit trail, and a proof-grade report. A no-code operator cannot be sponsored at institutional scale because it cannot produce the accountability artifact.
- **Trust transitivity:** the flywheel's hardest pre-revenue stage (Reach with zero brand) is solved by borrowing an institution's decades of it — and the portfolio report repays that trust with evidence, which renews the sponsorship.
- **Portfolio-scale proof:** ten sponsored modules generate ten ledgers' worth of Trust Ledger (#1) material and Immune System (#8) network density in one deal — sponsorship accelerates the entire proof stack.
- **Model-upgrade dividend, sponsor edition:** the sponsor's fixed check buys modules that appreciate — next year's report shows better outcomes at the same sponsorship price; the renewal pitch writes itself.
- **Flywheel:** Reach stage (roadmap coverage map) — the third-party-funded invented channel, paired with The Applicant (#11) as the intent-filtered one.

## 5. Gates / compliance

- **launch-gate (`processes/launch-gate.md`; scope row #12):** program marketing and any published sponsor materials wait for launch. Per the roadmap row, **warm-network sponsor conversations may pre-stage now** — in-person/unbranded/non-soliciting per the gate-12 scoping (`decisions/2026-07-20_in-person-local-gtm.md`); anything branded or sent-at-scale stays 🔴.
- **Gate #1 scope-rider (engagement legal suite):** the sponsor agreement joins the existing review batch — third-party-payor structure, the privacy wall as a contractual term, non-agency clause, acknowledgment-surface bounds, and the SMB-side disclosure that a sponsor is paying. **No new gate.**
- **Explicitly distinct from the referral program — and from gate #5:** Patronage is a **channel purchase** (the sponsor pays yourco for delivered modules), not a compensation arrangement (yourco pays nobody for introductions). No commissions, no escalators, no downline, no override — nothing that touches the MLM-gated structures behind gate #5 or the connector taxonomy. A sponsor who *also* wants connector-style commission economics is routed to the referral program's own gated track, papered separately; the two are never blended in one agreement.
- Regulated-sponsor caution, handled without a new gate: if a bank/insurer sponsor's own compliance regime imposes conditions (vendor review, marketing rules), those are the *sponsor's* obligations to run; any term they ask yourco to accept rides the gate-#1 counsel review like any contract question.
- **Privacy wall (§3.2)** is a hard product rule enforced in the compiler; **credibility gate:** portfolio reports contain only ledger-backed aggregates — no fabricated activation or outcome stats, cohort sizes stated.

## 6. Pricing frame *(assumption-stated; Polo locks)*

Sponsor pays a **per-sponsored-module package price** — assumption: roughly the standard first-module setup band times portfolio count, with a portfolio-scale efficiency discount at the larger tiers (batched onboarding is genuinely cheaper; the discount reflects real cost, not desperation) — plus a program fee covering the portfolio report and acknowledgment surface. Sponsorship covers a defined first-module term (assumption: setup + a fixed number of operating months). **The expansion economics are the point:** after the sponsored term, each SMB chooses directly — continue the module at the standard retainer, expand toward an OS tier, or lapse — at yourco↔SMB standard pricing, with no sponsor economics attached and no sponsor visibility beyond the aggregate continuation rate. The sponsored module is a funded on-ramp exactly as the house model already frames the single employee: smallest module first, OS as destination. All figures and terms illustrative until Polo locks against a real sponsor conversation.

## 7. Activation trigger (build)

**Launch; sponsor conversations may pre-stage via warm network** — exactly as roadmap row #13. Pre-trigger work permitted now: package sheet, sponsor agreement draft (into the gate-#1 batch), report-compiler design, and unbranded warm-network conversations under the gate-12 scoping. First signed sponsorship and any branded program surface wait for OtherVenture.

## 8. What we will NOT do

- **No per-SMB data to sponsors, ever** — not in reports, not in renewal negotiations, not verbally, not under a bigger check. A sponsorship whose real product is portfolio surveillance is declined by policy.
- **No sponsor branding inside the delivered product.** The acknowledgment surface (§3.1) is the entire co-brand footprint; the SMB's operating and customer-facing surfaces stay the SMB's brand only.
- **No sponsor direction rights.** Sponsors don't pick modules, set agent behavior, see approval queues, or direct any engagement — the non-agency clause is non-negotiable.
- **No auto-enrollment.** Every SMB opts in individually, signs its own agreement, and can decline or lapse without consequence from its sponsor — and the invitation says so.
- **No commission mechanics dressed as sponsorship.** Nothing in a Patronage deal pays anyone for introductions or per-signup — that is the referral program's separately-gated lane (gate #5 / #7), never blended here.
- **No mandate-washing for franchisors.** A franchisor may fund and promote the program; franchisee participation stays opt-in on yourco's side even if the franchisor would prefer to require it — resented mandatory tooling is the incumbent failure mode this offering exists to escape.
- **No fabricated program results.** Sponsor reports and renewal decks use ledger-backed aggregates with cohort sizes; pre-evidence conversations describe mechanism, not invented outcomes.
- **No exclusivity that outlives evidence.** No sponsor gets a categorical or geographic exclusive as a v1 term; exclusivity, if ever, is priced and time-boxed after the program has data.
