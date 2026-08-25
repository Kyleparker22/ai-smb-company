# The Reversibility Guarantee — Build Spec

**Working name:** The Reversibility Guarantee (frontier #28)
**Author:** the Founder
**Stack:** a portable export of workflow logic + data + a documented manual fallback, assembled from artifacts every engagement already produces · a **quarterly exit drill** run on the pattern in `runtime/drills/` · the drill record published to the client and into the trust ledger · a 30-day exit clause in the engagement agreement
**Status:** Spec — roadmap row #28. Build trigger: **first signed client** (the kit is template-buildable now). ⚠️ Counsel on the clause.
**Pillar / form factor:** cross-cutting trust layer; form factor 3 (an export + a drill record).

---

## 1. Concept

The unspoken objection to handing your operations to a one-person firm is not price and it is not quality. It is **dependence**: *if I stop paying, does my business stop?* Nobody raises it out loud, because raising it sounds like distrust, so it goes unaddressed and quietly kills deals that appeared to be going well.

Every vendor's incentive is to leave it unaddressed, because lock-in is the business model. yourco can invert it into a closing instrument:

> *"You can leave in 30 days and your business keeps running. Here's the export, here's the manual fallback, and here's the record of the last time we rehearsed it — which was last quarter, because we rehearse it every quarter whether or not you ask."*

Three parts, and the third is the one that makes it real:
1. **A portable export** — workflow logic, prompts, decision rules, and the client's data in open formats.
2. **A documented manual fallback** — for each module, how a human does this job on Monday morning without the OS, written as an actual SOP rather than a shrug.
3. **A rehearsed drill** — quarterly, yourco runs the exit for one module against the export and the fallback, records what worked and what didn't, and hands the client the record. **An untested export is a promise; a drill record is evidence.**

## 2. Why it's never been done

Data-portability commitments exist and are close to worthless. GDPR-style export rights produce a database dump nobody can operate. SaaS "you can export anytime" means a CSV of rows, not a running process. Escrow arrangements (source code held by a third party against vendor failure) are an enterprise instrument, expensive, and almost never tested — the industry's open secret is that escrowed code frequently does not build.

The gap in all of them is the same: **nobody rehearses the exit**, because rehearsing it costs the vendor money to prove a thing that reduces switching costs. It is straightforwardly against interest.

It is *not* against yourco's interest, for a structural reason: yourco sells an operated relationship whose value is ongoing improvement, not captivity. A client who stays because leaving is hard is a churn event on a delay; a client who stays because leaving is easy and they don't want to is a reference. And yourco already runs drills against its own systems — the immune-drill machinery exists — so the marginal cost of pointing that discipline at the client's exit is small. The willingness is the moat, not the mechanism.

## 3. Build shape

| Piece | What it is | Notes |
|---|---|---|
| Export kit | Workflow logic (prompts, rules, thresholds), data in open formats, integration map, credential inventory — assembled from artifacts the engagement already produces | Template-level, into `clients/_yourco-template/`; overlaps the Exit-Asset dossier (#3) deliberately |
| Manual fallback SOP | Per module: how a human performs this job without the OS, at what cost in hours, with what degradation stated honestly | This is the part that takes real work and the part clients actually need |
| The drill | Quarterly: pick a module, run the exit against the export and the fallback, record time-to-operational and every gap found | Extends the `runtime/drills/` pattern |
| Drill record | Published to the client and into the trust ledger — including failures, especially failures | A drill that always passes is not being run honestly |
| The clause | 30-day exit, export delivered on request, no data hostage, no wind-down fee | ⚠️ counsel |

**Effort band:** M — the export is largely assembly; the **manual fallback SOPs are the genuine cost** (they are also the highest-value artifact for the client, and they double as Understudy #7 material and Exit-Asset #3 exhibits).

## 4. Moat fit

- **It removes the objection that kills solo-founder deals**, and it is the objection no competitor will touch.
- **It resolves gate #13 more cheaply than ownership does.** The open question on the SaaS-replacement wedge is IP/ownership terms. "You own your workflow logic and data, portable, exportable, and we rehearse the handover" delivers most of what "you own it" was meant to deliver, without needing the ownership ruling to promise it.
- **It converts churn risk into a reference.** Ease of exit is the cheapest retention mechanism there is, because it makes staying a choice the client made rather than a trap they noticed.
- **The drills improve the product.** Every rehearsal finds an undocumented dependency, an unexported threshold, a credential only the Founder has. Those are real reliability defects surfaced on a schedule.
- **Interlocks:** Exit-Asset OS (#3) is the same artifacts framed for a *buyer* rather than for departure; Understudy (#7) shares the fallback SOPs; Trust Ledger (#1) carries the drill record; Trip-Wire Pricing (#24) is its module-level sibling.

## 5. Gates / compliance

- **⚠️ Counsel — rides gate #1** (legal suite) as a scope rider: the 30-day exit, export scope, data ownership on departure, and the explicit absence of a wind-down fee. Also touches **gate #13** (ownership/IP) and may narrow it: portability is promisable without resolving IP ownership, and the two must not be conflated in copy.
- **Never promise portability that has not been rehearsed.** Until a module has passed a drill, the claim for that module is "documented, not yet rehearsed" — stated in exactly those words.
- **Credential handling** on exit follows the house secrets rule: credentials are transferred or revoked through the client's own vault, never pasted into a document or a chat.
- **The drill record is honest or it is nothing** — failures are published to the client. A sanitised drill record is worse than none, because it teaches the client the records can't be trusted.

## 6. Pricing frame *(Polo locks)*

**Included in every engagement, not an add-on.** Pricing reversibility would make it a hostage negotiation, which is the thing being counter-positioned against. The commercial argument is that it *supports* the retainer rather than discounting it: the client is paying for operation and improvement, not for captivity, and saying so plainly is how a premium price survives contact with a skeptical owner.

## 7. Activation trigger (build)

**First signed client** for the live version. The **export kit and fallback SOP templates are buildable now** into `clients/_yourco-template/` (hooks-predate-clients), and the *sentence* is usable immediately — it is the honest answer to the dependence objection at Sample Client's current stall, ahead of any drill existing, provided it is stated as a commitment rather than a track record.

## 8. What we will NOT do

- **No claim of a rehearsed exit before a drill has run.** "Documented, not yet rehearsed" is the exact wording until one has.
- **No sanitised drill records.** Failures are published to the client. This is the whole basis of the instrument's credibility.
- **No data hostage, ever** — not during a dispute, not over an unpaid invoice, not at churn. The export ships on request. Any collections matter is handled as a collections matter, never by withholding a client's operations.
- **No wind-down fee, no exit fee, no export charge.**
- **No conflating portability with ownership.** Until gate #13 rules, copy says the client's data and workflow logic are exportable — never that they own the reliability layer or the infrastructure.
- **No quiet degradation of the fallback SOPs.** If a module changes and its manual fallback goes stale, that is a defect against the guarantee and gets fixed on the same clock as any other reliability defect.
- **No using the guarantee as a churn-save device.** It is stated at sale time, not produced at the cancellation conversation.
