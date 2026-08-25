# Expansion by Vacancy — Build Spec

**Working name:** Expansion by Vacancy (frontier #30)
**Author:** the Founder
**Stack:** `dashboard/vacancies.py` (yourco's own unowned-work finder — absorb / activate / hire, proposing only) pointed at the **client's** organisation, fed by the engagement's own operational record + a short structured pass with the owner · output is a ranked artifact, not a pitch deck
**Status:** Spec — roadmap row #30. Build trigger: **first client ~90 days live** (needs an operational record to read).
**Pillar / form factor:** Operations (pillar 5) with a Company-Brain face; form factor 3 (a document reviewed together).

---

## 1. Concept

The quarterly expansion conversation is a defend-and-pitch ritual: the vendor arrives with a module to sell, the client braces, and both parties perform. It is the least productive recurring meeting in professional services, and it is where operated relationships either compound or flatline.

Expansion by Vacancy replaces the pitch with a **diagnosis the client asked for**. `vacancies.py` already does this for yourco — it finds work inside the company that has no owner and proposes absorb / activate / hire without deciding anything. Pointed at the client's organisation, it produces the same artifact about them: **the work in your business that nobody owns**, ranked by what it is costing, each item marked with the honest three-way choice — a person absorbs it, an existing module extends to cover it, or it needs a new module.

The reframe does the work. The buyer's mental comparison stops being *"another line item versus my current bill"* and becomes *"this unowned work versus the coordinator I keep meaning to hire."* And because at least some items resolve to *absorb* or *a person* rather than *a module*, the artifact is credible — a list where every finding conveniently requires more yourco is a pitch deck with a diagnosis costume on.

## 2. Why it's never been done

Account expansion has two established shapes and both are the vendor's story. **Usage-based upsell** points at consumption limits — the client's growth becomes the vendor's invoice, which the client experiences as a toll. **Consultative QBRs** bring a roadmap and a maturity model, which is a generic ladder the vendor authored and the client is invited to climb.

Neither starts from unowned work, because neither vendor can see it. A SaaS vendor sees its own product's telemetry; a consultant sees what the client describes in a workshop. Seeing work that *nobody is doing* requires visibility into how the business actually operates across functions — the intake that gets handled inconsistently, the follow-up that happens when someone remembers, the reconciliation that only occurs at year end.

An operated OS has exactly that visibility as a byproduct of running the operations. And the honest three-way output — where "hire a person" is a legitimate recommendation — is only sayable by a firm whose retainer does not depend on every finding becoming a module. That combination is rare enough to be unoccupied.

## 3. Build shape

| Piece | What it is | Notes |
|---|---|---|
| Vacancy detection | Work appearing in the operational record with no consistent owner: handled by different people each time · handled only when escalated · handled in bursts after a backlog · never handled and visibly absent | Reads the engagement's own record; supplemented by a short structured pass with the owner |
| Cost estimate | What the vacancy costs, in the client's own numbers, assumptions stated (the Audit's method, reused) | Never an industry benchmark |
| The three-way call | **absorb** (a person already close to it takes it) · **extend** (an existing module covers it, often at no new cost) · **new module** (priced) | The presence of real absorb/extend outcomes is what makes the artifact credible |
| Ranking | By cost × how long it has been unowned | Longest-unowned rises: those are the ones the business has learned to live around |
| Review format | Walked through together; the client marks each item themselves | Not sent as a proposal |

**Effort band:** S — the detection pattern exists internally; the per-client work is the structured pass and the cost estimates.

## 4. Moat fit

- **It monetises the operated position.** Only a firm running the operations can see unowned work; this converts that visibility directly into expansion without a pitch.
- **It reframes the budget comparison** from software spend to headcount — the comparison yourco wins, and the one the "digital employee" on-ramp was always reaching for.
- **Credibility through self-limitation:** recommending *absorb* or *hire a person* on some items is what makes the *new module* items believable. A vendor who never recommends against itself is not read as a diagnostician.
- **It compounds across clients.** Vacancy patterns recur by business shape; the library of what goes unowned in a hardscaper, a realty firm, a restoration contractor becomes cross-client IP — the same compounding logic as the Company OS pattern library (B1).
- **Interlocks:** Boardroom (#9) advises on decisions, this finds work; Understudy (#7) covers roles that exist but are single-threaded, this covers roles that do not exist; the Re-Audit (#31) is its scheduled home; the Churn Tripwire (#29) is where a withdrawn module's budget honestly goes.

## 5. Gates / compliance

- **No counsel gate.**
- **The artifact names work, never people.** "Nobody owns quote follow-up" — never "Jenna isn't doing follow-up." An expansion instrument that reads as a performance review of the client's staff is both wrong and radioactive, and it would end the client's willingness to let the OS see anything.
- **No recommendation to replace a named human.** If the honest answer is that a role is redundant, that is the owner's conclusion to reach from their own numbers, not yourco's recommendation to make. yourco reports unowned work; it does not restructure the client's team.
- **Cost figures are the client's own numbers with assumptions stated** (credibility gate; no benchmarks, no fabricated averages).
- **Employment-law adjacency:** anything touching roles, hours, or staffing decisions routes to the client's own HR/counsel. yourco has no view on it.

## 6. Pricing frame *(Polo)*

The **vacancy pass is included** in the operated retainer — it is a reading of work already being done. Only the *modules that result* are priced, at standard module bands. Charging for the diagnosis would recreate the incentive to find module-shaped vacancies, which is precisely the corruption the three-way output exists to prevent.

## 7. Activation trigger (build)

**First client ~90 days live.** Detection reads the operational record, and 90 days is roughly the point at which the record shows the difference between work that is owned and work that merely happened recently. Running it earlier produces a list of things not yet built, which is a scope conversation, not a vacancy diagnosis. The detection pattern and the artifact template are buildable now into `clients/_yourco-template/`.

## 8. What we will NOT do

- **Never name individuals.** Work and roles only.
- **Never recommend replacing a person.** yourco reports unowned work; staffing decisions are the owner's, with their own advisors.
- **Never publish a vacancy list where every item resolves to a new module.** If the pass produces no absorb and no extend outcomes, it has been run as a sales exercise and gets re-run honestly.
- **No benchmark costs.** The client's own numbers, assumptions stated, or no number at all.
- **No sending it as a proposal.** It is walked through together and the client marks the items; an emailed ranked list of things they are failing to do is an insult with a price attached.
- **No detection from covert observation.** What the OS reads to produce this is disclosed, like all client telemetry (same rule as #29).
- **No vacancy invented from absence of data.** If the record cannot show whether work is owned, the artifact says the record can't show it and names what would — it never scores silence as a vacancy.
