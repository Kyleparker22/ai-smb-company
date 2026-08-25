# Contracts — the suite (drafts; counsel review required)

**Owner:** Ray (the Founder holds). These are **starting-point templates**, not legal advice. **A Florida-licensed attorney must review the suite before the first real signature** — together with the FTSA/TCPA memo already in flight (`processes/10dlc-sending-infra-setup.md`).

## The documents
| File | Use | When |
|------|-----|------|
| `mutual-nda.md` | Mutual NDA | Before sharing sensitive ops detail on a fit/discovery call |
| `engagement-agreement.md` | The "sign to start" agreement — scope, fees, term, IP, data, the yourco-infra model. **Reconciled 2026-06-11** with the mature protective clauses (liability cap, indemnification, AI disclaimer, dispute resolution). | When a prospect says yes |
| `dpa.md` | Data Processing Addendum (attaches to the engagement agreement). **Reconciled 2026-06-11** — full definitions, state privacy laws, 72-hr breach clause, current sub-processor stack. | When an engagement processes client data |
| `baa.md` | **HIPAA Business Associate Agreement** (added 2026-06-12). Controls over the agreement + DPA on PHI. | When an engagement handles PHI (healthcare verticals) — signed **before any PHI flows**. Trigger: `agents/rafi/vertical-compliance-map.md` |
| `sla.md` | **Service Level Agreement** (added 2026-08-24). Availability, severity-based response times, credits, exclusions. Attaches to the engagement agreement and controls over its §10 on those subjects. | 🔴 **Not yet sendable** — §7 lists preconditions; yourco has no uptime monitoring today, so the availability clock is unmeasured. |
| `privacy-policy.md` | Site privacy policy (Webb publishes at `/privacy`) | Before the site collects data at go-live |
| `msa-v3-prior.md` · `dpa-v3-prior.md` | **Reference only** — imported prior v3 templates, harvested into the two docs above. Keep for the MSA+SOW architecture option (see below). | Counsel reference |

**Reconciliation note (2026-06-11):** the engagement agreement + DPA were upgraded by merging the mature clauses from the imported v3 templates. **Open question for counsel:** keep the single **Engagement Agreement** model, or move to **MSA + per-engagement SOWs** (better for repeat/expansion clients — the v3 files are drafted that way). Drafted for the single-agreement model; re-splitting is straightforward.

## Flow (go-live)
1. Fill every `[[PLACEHOLDER]]` from `finance/legal-docs/business-info.md` (entity) + the engagement specifics (employee, fees, scope).
2. **Counsel review** (one-time for the templates; spot-review material changes after).
3. Send via **DocuSign** (connector available) — the Founder approves the send + the counterparty.
4. Countersigned copy → store in `clients/<client>/` and log the date.

## Before first use — open items for counsel
- Governing law / venue (FL), limitation of liability, indemnification caps — placeholders, counsel sets.
- Data-processing / privacy addendum (client data the employee touches) — coordinate with Rafi (compliance) when built.
- Auto-renewal + termination-for-convenience notice periods — confirm enforceable in target states.
