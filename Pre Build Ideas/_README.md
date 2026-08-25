# Pre Build Ideas — 76<!--#count: files Pre Build Ideas/*/BUILD.md--> builds, 74 industries

> ⚠️ **NOT YOURS YET.** 76 prototypes on **synthetic data**, none of them sold, none with a customer. They exist to
demo an idea in a prospect's own industry. Reality level: BUILT, UNSOLD.


> **What this folder is.** 76 AI OS / platform builds, so yourco has something **already built and demoable on day one** for 74 SMB types. (Property management arrived 2026-08-24 from `offerings/`, where it had been built past the point of being a spec.) One industry per folder: `BUILD.md` is the idea, the ROI model, the demo path and the original build prompt; `build/` is the running prototype.
>
> **Status: all seventy-five built, tested, verified at full depth (72–75 added 2026-08-24).** 5,856 assertions across the seventy-five suites (716 in builds 1–10, 528 in 11–20, 479 in 21–30, 984 in 31–49, 87 in build 50, 978 in 51–60, 84 in build 61, 1,180 in 62–71, **335 in 72–75**) plus 42 in the kit's own suite ([`_kit/test_kit.py`](_kit/test_kit.py) — the shared contracts pinned directly, so a kit regression fails there first instead of as seventy-five mysterious build failures), all green. Each runs from a `.claude/launch.json` name on 127.0.0.1, on synthetic data, sharing one honesty engine in [`_kit/`](_kit/).
>
> **Still: nothing here is sold and nothing here has a client.** These are prototypes on invented data, not production systems. Every `build/README.md` ends with an honest "what this does not do yet".

---

## Why pre-build at all (the case, stated honestly)

yourco's motion is **Audit → custom AI OS**, and that stays true. A pre-build is not a product catalog and does not become one — it is a **starting position**:

- **Demo before Audit.** The hardest moment in the sale is the prospect who cannot picture it. A working surface for *their* industry, seeded with *their* kind of data, closes that gap in ten minutes.
- **Build speed on engagement #1 in that vertical.** The first real client in an industry starts at ~60–70% instead of zero. Every one of these is designed as a template to be *overlaid per client*, never shipped as-is.
- **The audit gets sharper.** Each build forces us to name the real bottleneck of that industry, in that industry's vocabulary, with the numbers the owner already tracks.

⚠️ **The honest counter-argument, kept in view:** pre-building seventy-six demos with n=0 clients is speculative inventory. The failure mode is ten half-built demos and no signed deal. Mitigation baked into the plan: (a) each build is a **prototype with synthetic data**, not a production system — days, not weeks; (b) **none of them ships externally** until the launch-gate clears and the client-facing surface is white-labelled; (c) build order follows warm-network reachability, not our own interest. Sample Client being unsigned at Proposal is still the bottleneck, and no amount of pre-build moves it.

## What is deliberately NOT here

Four verticals already have real assets and are excluded so we don't build them twice:

| Vertical | Where it already lives |
|---|---|
| Property management | `Pre Build Ideas/property-management/build/` (built, in progress) |
| Immigration / nurse ops | `offerings/conduit/SPEC.md` (spec, parked) |
| Hardscaping / landscaping | `clients/sample-client/platform/` (real engagement) |
| Roofing / storm restoration | Sample Product (Prospect A) |

---

## The seventy-five

| # | Folder | Working name | Launch name · port | Tests | The bleeding neck it solves |
|---|---|---|---|---|---|
| 1 | `home-services/` | **Dispatch OS** | `prebuild-dispatch-os` · 8821 | 72 | Missed calls, unsold estimates, deferred work nobody re-offered |
| 2 | `med-spa-aesthetics/` | **Consult OS** | `prebuild-consult-os` · 8822 | 68 | Expensive leads answered slowly; consults that no-show or never decide |
| 3 | `dental-practices/` | **Chair OS** | `prebuild-chair-os` · 8823 | 47 | Diagnosed-but-unscheduled treatment, holes in tomorrow's schedule, verification on hold |
| 4 | `insurance-agencies/` | **Renewal OS** | `prebuild-renewal-os` · 8824 | 64 | Renewals that arrive untouched; mono-line accounts never cross-sold |
| 5 | `accounting-firms/` | **Close OS** | `prebuild-close-os` · 8825 | 55 | The chase, and the partner who doesn't know who's blocking what |
| 6 | `law-firms/` | **Case OS** | `prebuild-case-os` · 8826 | 70 | Speed-to-retainer, and the records chase that adds months to every case |
| 7 | `freight-brokerage/` | **Carrier OS** | `prebuild-carrier-os` · 8827 | 71 | Carrier fraud / double-brokering, and 20 minutes of vetting per load |
| 8 | `wholesale-distribution/` | **Quote Desk OS** | `prebuild-quote-desk-os` · 8828 | 80 | RFQs quoted in days; POs keyed by hand into the ERP |
| 9 | `staffing-recruiting/` | **Redeploy OS** | `prebuild-redeploy-os` · 8829 | 93 | Submission speed, and the ending assignment nobody redeploys |
| 10 | `home-health-care/` | **Shift OS** | `prebuild-shift-os` · 8830 | 96 | The 6am callout with no fill, and compliance documentation that arrives late |
| 11 | `commercial-subcontractors/` | **Change OS** | `prebuild-change-os` · 8831 | 60 | Change orders performed on a handshake and never billed; retainage and notice deadlines |
| 12 | `auto-repair/` | **Bay OS** | `prebuild-bay-os` · 8832 | 55 | Declined inspection work never re-offered; safety findings softened into texts |
| 13 | `veterinary/` | **Visit OS** | `prebuild-visit-os` · 8833 | 57 | Lapsed patients, dark exam rooms, and the emergency that can't wait in a queue |
| 14 | `msp-it-services/` | **Queue OS** | `prebuild-queue-os` · 8834 | 55 | The phishing ticket behind forty printer tickets; scope work done free for years |
| 15 | `equipment-rental/` | **Yard OS** | `prebuild-yard-os` · 8835 | 52 | Billing past the off-rent call; damage charges with no evidence; the idle yard |
| 16 | `multi-unit-restaurants/` | **Unit OS** | `prebuild-unit-os` · 8836 | 46 | Food-cost variance nobody computes; the illness claim answered in writing |
| 17 | `gyms-franchises/` | **Member OS** | `prebuild-member-os` · 8837 | 51 | Failed cards nobody owns; quiet churn; cancellations handled like objections |
| 18 | `pest-control/` | **Route OS** | `prebuild-route-os` · 8838 | 46 | Reservice calls as unread churn signals; skipped stops billed; chemical questions |
| 19 | `dumpster-waste/` | **Haul OS** | `prebuild-haul-os` · 8839 | 50 | The hazardous item a bot must never approve; ticketless charges; idle containers |
| 20 | `title-escrow/` | **Closing OS** | `prebuild-closing-os` · 8840 | 56 | The "updated wiring instructions" email — the agency-ending event |
| 21 | `commercial-cleaning/` | **Crew OS** | `prebuild-crew-os` · 8841 | 44 | The security incident software must never close; "cleaned" claimed without an inspection |
| 22 | `moving-storage/` | **Move OS** | `prebuild-move-os` · 8842 | 51 | Binding estimates without a survey; charges beyond the binding + unsigned change orders |
| 23 | `self-storage/` | **Gate OS** | `prebuild-gate-os` · 8843 | 51 | The lien chain that must halt on a military signal (SCRA); the auction step no bot takes |
| 24 | `child-care/` | **Ratio OS** | `prebuild-ratio-os` · 8844 | 45 | The unlisted pickup a bot must never authorize; ratios assumed compliant with no records |
| 25 | `funeral-homes/` | **Arrangement OS** | `prebuild-arrangement-os` · 8845 | 48 | The 2am first call read casually; the quote that drifts off the recorded GPL |
| 26 | `physical-therapy/` | **Rehab OS** | `prebuild-rehab-os` · 8846 | 50 | The red flag buried in a "sore leg" message; visits billed beyond authorization |
| 27 | `optometry/` | **Exam OS** | `prebuild-exam-os` · 8847 | 46 | The chemical splash waiting in a queue; the expired Rx a reorder bot would refill |
| 28 | `catering-events/` | **Plate OS** | `prebuild-plate-os` · 8848 | 42 | The BEO change inside 72 hours auto-applied; the allergen question a bot answered |
| 29 | `machine-job-shops/` | **Traveler OS** | `prebuild-traveler-os` · 8849 | 43 | Quotes priced on stale material; the shipment that leaves without its certs |
| 30 | `ag-services/` | **Field OS** | `prebuild-field-os` · 8850 | 59 | The drift complaint handled casually — a state-investigation exhibit; billing without the as-applied record |
| 31 | `pool-service/` | **Pool OS** | `prebuild-pool-os` · 8851 | 60 | "Safe to swim" never leaves software; the stop billed with no readings behind it |
| 32 | `tree-care/` | **Canopy OS** | `prebuild-canopy-os` · 8852 | 55 | Neither "safe" nor "hazardous" ever leaves software; the power-line job with no utility clearance |
| 33 | `septic-services/` | **Pump OS** | `prebuild-pump-os` · 8853 | 54 | The unmanifested load — unprovable work AND a DEQ exhibit; the phone diagnosis |
| 34 | `towing-recovery/` | **Hook OS** | `prebuild-hook-os` · 8854 | 53 | The invoice above the filed rate card — structurally impossible; the lien clock |
| 35 | `fire-life-safety/` | **Code OS** | `prebuild-code-os` · 8855 | 53 | The device shown compliant with no record; the impairment softened by software |
| 36 | `property-inspection/` | **Inspect OS** | `prebuild-inspect-os` · 8856 | 52 | "Can you leave the roof note out" — refused, preserved verbatim; findings append-only |
| 37 | `medical-billing/` | **Claim OS** | `prebuild-claim-os` · 8857 | 52 | The upcode without provider documentation — the fraud line, structurally shut |
| 38 | `car-wash-detailing/` | **Shine OS** | `prebuild-shine-os` · 8858 | 48 | The damage claim denied by software; the charge after the cancellation request |
| 39 | `print-signage/` | **Proof OS** | `prebuild-proof-os` · 8859 | 52 | The job on the press with only a verbal go-ahead — the eaten reprint's origin story |
| 40 | `elevator-maintenance/` | **Cab OS** | `prebuild-cab-os` · 8860 | 49 | The desk that advises self-evacuation; the red-tagged unit turned back on |
| 41 | `used-car-dealers/` | **Lot OS** | `prebuild-lot-os` · 8861 | 54 | "Never wrecked" beyond the recorded report; the payment quote without lender terms |
| 42 | `security-guard-services/` | **Post OS** | `prebuild-post-os` · 8862 | 48 | The incident narrative edited after the fact; the expired card on an armed post |
| 43 | `propane-delivery/` | **Fuel OS** | `prebuild-fuel-os` · 8863 | 49 | The out-of-gas ticket closed without the leak check — how houses explode |
| 44 | `alarm-monitoring/` | **Central OS** | `prebuild-central-os` · 8864 | 47 | "Put me in test mode" by text — the burglar's first move; the fire dispatch cancelled |
| 45 | `trucking-fleet/` | **Hours OS** | `prebuild-hours-os` · 8865 | 54 | The dispatch past the recorded HOS clock; "fix his log" — the falsification line |
| 46 | `nemt-transport/` | **Ride OS** | `prebuild-ride-os` · 8866 | 51 | "Grandma seems confused" answered with "probably fine"; the bumped dialysis trip |
| 47 | `crane-rigging/` | **Rig OS** | `prebuild-rig-os` · 8867 | 48 | The lift plan approved by software; the boom up in wind the chart forbids |
| 48 | `marinas/` | **Slip OS** | `prebuild-slip-os` · 8868 | 49 | The sheen on the water handled casually — a USCG exhibit; the verbal yard bill |
| 49 | `dry-cleaners/` | **Garment OS** | `prebuild-garment-os` · 8869 | 56 | The wedding-dress claim haggled at the counter instead of settled from the schedule |
| 50 | `resale-consignment/` | **Consign OS** | `prebuild-consign-os` · 8870 | 87 | "Is it authentic?" — software never says genuine (or fake); the payout is the agreement's arithmetic; no personal-account channel exists by construction |
| 51 | `monument-dealers/` | **Stone OS** | `prebuild-stone-os` · 8871 | 90 | Only the family approves an inscription proof — granite is not reworked; setting waits for the recorded cure |
| 52 | `well-water/` | **Well OS** | `prebuild-well-os` · 8872 | 83 | "Is my water safe" only cites a recorded lab report; an overdue UV lamp is never "still fine" |
| 53 | `land-surveyors/` | **Plat OS** | `prebuild-plat-os` · 8873 | 98 | A boundary opinion from software is unlicensed surveying; the seal gate is structural |
| 54 | `locksmiths/` | **Key OS** | `prebuild-key-os` · 8874 | 103 | No rekey without recorded authority — a break-in with an invoice; key codes scrubbed like PHI |
| 55 | `party-tent-rental/` | **Marquee OS** | `prebuild-marquee-os` · 8875 | 89 | The wind call is human-only; overselling counted stock is impossible; the 811 ticket is a wall |
| 56 | `chimney-hearth/` | **Flue OS** | `prebuild-flue-os` · 8876 | 113 | "Safe to burn" cites the recorded inspection or books one; a CO alarm gets the evacuate script, never a booking |
| 57 | `process-servers/` | **Serve OS** | `prebuild-serve-os` · 8877 | 100 | The affidavit is a human's oath, assembled verbatim from an append-only attempt log |
| 58 | `appliance-repair/` | **Fix OS** | `prebuild-fix-os` · 8878 | 100 | Incomplete warranty claims refuse to submit, fields named — a denied claim is free work |
| 59 | `glass-glazing/` | **Pane OS** | `prebuild-pane-os` · 8879 | 89 | No fabricator release without two matching recorded measurements; "we don't sell code violations cheaper" |
| 60 | `pet-aftercare/` | **Ember OS** | `prebuild-ember-os` · 8880 | 113 | Tag verification at every custody transfer — the check is the chain, and the chain is the business |
| 61 | `real-estate-investing/` | **Deal OS** | `prebuild-deal-os` · 8881 | 84 | Never a verdict, bands never points, no estimate below the comp floor — the deal tool that refuses to flatter the deal |
| 62 | `house-blackbox/` | **Blackbox OS** | `prebuild-blackbox-os` · 8882 | 104 | The membership that prices itself per-home, every factor in dollars summing to the cent — and renewals go DOWN, proudly |
| 63 | `changeorder-camera/` | **Delta OS** | `prebuild-delta-os` · 8883 | 120 | The change order that writes itself the day the wall moves — notice letter citing the clause, inside the window |
| 64 | `evidence-halflife/` | **Halflife OS** | `prebuild-halflife-os` · 8884 | 122 | Evidence as perishable inventory: the dies-first queue, UNKNOWN decay sorts first, the ledger does not forgive |
| 65 | `claim-rehearsal/` | **Rehearsal OS** | `prebuild-rehearsal-os` · 8885 | 124 | The claim rehearsed against the actual policy before renewal — the $41k gap with the exclusions cited by form |
| 66 | `pharmacy-remit/` | **Remit OS** | `prebuild-remit-os` · 8886 | 111 | Every PBM line reconciled to the cent; recovered = counted corrections only — never 'a sales number, not a ledger' |
| 67 | `hoa-management/` | **Reserve OS** | `prebuild-reserve-os` · 8887 | 120 | Funding bands + the special-assessment horizon; one ledger, two doors — homeowners see the board's own math |
| 68 | `graveyard-rebid/` | **Rebid OS** | `prebuild-rebid-os` · 8888 | 129 | Lost quotes re-bid themselves when counted idle crosses the floor — and drafted re-bids hold their hours |
| 69 | `restaurant-lab/` | **Lab OS** | `prebuild-lab-os` · 8889 | 132 | TOO EARLY TO KNOW is a real verdict; rolling out noise 'institutionalizes luck' |
| 70 | `wholesale-no-meter/` | **Counter OS** | `prebuild-counter-os` · 8893 | 99 | Every 'we don't carry that' counted and priced — an anecdote is not demand, a counted mystery beats an invented dollar |
| 71 | `title-receipts/` | **Receipt OS** | `prebuild-receipt-os` · 8894 | 119 | The security log as an underwritable asset — the packet cannot render without its exceptions column |
| 72 | `peptide-testing-labs/` | **Assay OS** | `prebuild-assay-os` · 8895 | 79 | A forgeable certificate is the whole product; a missing assay reading as a clean one |
| 73 | `peptide-compounders/` | **Provenance OS** | `prebuild-provenance-os` · 8896 | 70 | A rulebook that moves under the business; packets nobody can assemble; complaints that arrive as clinical questions |
| 74 | `peptide-clinics/` | **Protocol OS** | `prebuild-protocol-os` · 8897 | 85 | Quiet churn — revenue here is retention, not the funnel — and an inbox that mixes a receipt with a swelling face |
| 75 | `telehealth-clinics/` | **Encounter OS** | `prebuild-encounter-os` · 8898 | 101 | Routing a patient to a clinician unlicensed in their state; the leak between paying and attending |
| 76 | `property-management/` | **Property OS** | `prebuild-property-management` · 8813 | 485 | Three loops at once with staff for none — maintenance, turnover and money. **Moved here from `offerings/` 2026-08-24**, where it had been built past the point of being a spec; it is the fullest worked example of the pattern and 13 other BUILD.md files tell you to mirror it. ⚠️ The one build that does not use `_kit/` — it predates it and carries its own honesty layer. |

**The one thing every build has in common:** each is organised around a refusal that a competitor's
demo will not have. The emergency stop that over-triggers on purpose. The clinical question routed
unanswered. The benefit that will not be called covered. The comparison that will not render without
its coverage diff. The scope creep that will not be asserted off a two-sided clause. The production
that is not complete because a PDF arrived. The carrier the system may refuse but may never approve.
The part number it will not guess. The candidate it will not reject. The crisis it hands to a human
inside one second.

The second ten add their own: the CO that cannot be submitted without a signed directive, the
brake finding that cannot leave as a text, the reminder that cannot reach a deceased patient, the
security ticket software cannot close, the invoice that cannot bill past the off-rent call, the
allergen question a bot never answers, the cancellation that cannot be slow-walked, the exposure
message that gets Poison Control language, the paint can that never gets a yes, and the wire
instruction the system can never send, change, confirm, or restate.

The third ten keep the through-line: the security incident only a human closes, the estimate that
cannot bind without its survey, the lien chain that freezes on a military signal, the pickup release
that is a lookup and never an authorization, the quote that cannot leave the recorded GPL, the
cauda-equina message that gets ER language instead of an appointment, the chemical splash that gets
irrigate-now instead of a queue position, the BEO change inside 72 hours that is never auto-applied,
the shipment that cannot certify what its paper cannot prove, and the drift complaint logged
regulator-grade while the system asserts nothing about cause.

**Nine of the first ten shipped with at least one honesty bug found by *running* it rather than
reading it** — an automation rate that read 1.000, a mean where the median belonged, a verifier
that over-refused until every sheet was an exception, two screens that silently re-ran their own
sweep, a staleness model that could never lower a perfect score, a tripwire that could never fire,
a matcher that broke a size tie on purchase history, an O(n²) lookup, and a compliance sweep that
wrote 4,202 rows a day. Each is named in its build's README. **The second and third tens shipped
against the hardened kit, so those bug classes were designed out; what running still caught was
classifier misses** — a tire regex that ignored plurals, "chewing" not matching a toxin pattern,
"limping" read as a collapse, "exercises" that a word boundary couldn't reach, "death certificates"
tripping a first-call pattern — which is exactly what the shipped evals exist to catch.

**The build-out (2026-08-16).** Builds 11–30 originally shipped leaner than the first ten — the
refusals and gates were all there, but the agents were thin. A full pass brought every one of the
twenty to first-ten depth: **drafted outward copy on every R1 action** (a human always sees the
actual words, white-label, no legal/medical/threat language by test), **bounded chase ladders**
with cooldowns and silence-is-an-answer exits, **a recovered-this-week read on every board**
(counted from the event log — human sends count, agent drafts don't), and **~5 new eval phrasings
per build**. The eval expansion earned its keep: in Rehab OS all five new phrasings missed on
first run, in Exam OS and Plate OS four of five — each miss widened a classifier that would have
mis-routed a real message (pins-and-needles cauda equina, a racquetball to the eye, a vegan RSVP).
Test counts roughly doubled across the twenty (528 + 479 vs the original 362 + 345).

**The fourth set (31–49, built 2026-08-17)** keeps the through-line and was built at the full
standard from day one — drafted R1 copy, bounded ladders, recovered-this-week counted, ~14-case
evals: the swim verdict that cannot be spoken, the tree that is neither safe nor hazardous, the
manifest that is also a DEQ exhibit, the invoice clamped to the filed card, the impairment no
software may soften, the finding no agent can get removed, the upcode held shut, the damage claim
never denied, the verbal go-ahead that is a note and not a gate pass, the desk that cannot say
"climb out", the "never wrecked" that is inexpressible, the narrative only its guard may correct,
the outage ticket the leak check holds open, the test-mode text refused as the burglar's first
move, the log nobody fixes, the dialysis trip nothing bumps, the lift plan only a director signs,
the sheen logged for the USCG, and the wedding dress settled by schedule instead of by argument.
Running caught the same two classes as always — first-run classifier misses (~15 across the
nineteen, each widening a pattern) and one real core bug: Shift OS's week started at the current
clock time instead of Monday midnight, found because the sweep ran at 00:30 on a Monday.

**Build 50 (Consign OS, 2026-08-17)** came in sideways — Partner B's FB-Marketplace-assistant idea,
rebuilt as the version that survives the anti-library: an operated OS for resale & consignment
SHOPS on their business channels, never automation of anyone's personal account (that posture is
`rejections/2026-07-05`'s). Same sweep also grew Redeploy OS a **Present** module — HireAra-grade
branded submittal rendering with a structural no-fabrication contract — which is why builds 1–10
now count 716 and row 9 reads 93 where it used to read 73.

**The fifth set (51–60, built 2026-08-17)** was chosen to a different brief — the Founder: the most
OVERLOOKED industries, the ones no AI vendor has ever called on, where the outcomes would be
largest. Every pick fails the "has anyone pitched them AI?" test and carries a refusal no
horizontal tool ships: the proof only a family may approve, the water only a lab may call safe,
the boundary only a licensed surveyor may state, the door only recorded authority may open, the
wind call only a human may make, the fireplace only the recorded inspection may clear, the
affidavit only a server may swear, the claim that refuses to submit incomplete, the glass that
needs two matching measurements, and the ashes whose chain of custody IS the business. Built in
parallel by ten scoped builders against the house standard, each suite re-verified unpiped and
each refusal re-proven live before its commit.

**Build 61 (Deal OS, 2026-08-17)** is a different animal from the sixty: real-estate deal
analysis is a CROWDED category (DealCheck, Mashvisor, AirDNA), picked anyway because every
incumbent flatters the deal — point predictions on hidden assumptions. Deal OS is the one that
refuses: hand-fixture-pinned mortgage math, all three strategies on stated overridable
assumptions, bear/base/bull bands from the market's own recorded history, the comp floor, the
stress grid, ranked only by the investor's recorded bar — and never, structurally, a verdict.
It pairs with `Pre Build Ideas/property-management/build` as the acquisition half of a real-estate suite.

**The sixth set (62–71, built 2026-08-17)** answered a different brief again — the Founder: one idea
per top-target industry that has never been seen before. Each build is a MECHANISM, not a
vertical: the membership that prices itself from the home's own record, the change order that
writes itself from the photo-vs-plan diff, evidence as perishable inventory, the claim
rehearsed before it happens, the remittance autopsied to the cent, the HOA whose homeowners
see the board's math through the same read path, the lost quote that re-bids itself against
counted idle hours, the experiment that refuses to conclude early, the priced ledger of every
"no," and the security log sold back to the insurer as evidence. "Never seen" is claimed
honestly: no shipped product we know of does these; several exist as enterprise practices
never productized for SMBs. Built in parallel by ten scoped builders; every suite re-verified
unpiped and every refusal re-proven live before its commit.

**Runners-up** (next ten if these land): private schools & tutoring centers · courier &
last-mile delivery · small wineries & cideries · septic tank installers (excavation side) ·
mobile-home park operators · upholstery & furniture repair · taxidermists · small quarries &
aggregate yards · bail bond agencies (counsel-gated) · municipal water/sewer contractors.

---

## The shared build contract (every prompt enforces this)

Each `BUILD.md` carries these inline so the prompt is self-contained in a fresh chat. Restated once here as the canonical version.

**Shape.** Mirror `Pre Build Ideas/property-management/build/`: `core.py` (all *rules* — nothing rule-shaped in the agents or the UI) · `agents.py` (the agents, each with a declared autonomy rung) · `seed.py` (synthetic data at any scale) · `data/` (JSON store, gitignored if it grows) · `app/` (the surfaces) · a stdlib server bound to `127.0.0.1` with a `.claude/launch.json` entry. Python stdlib only unless the build genuinely needs more.

**The two honesty rules** (lifted verbatim from property-os, because they are what make the thing sellable):
1. A number that cannot be computed from recorded events is returned as `None` with a `_missing` reason — **never estimated, never zero-filled.**
2. Every state change is written to an **append-only event log** with its actor (`agent:<name>` or `human:<id>`) and its autonomy rung. The "% automated" figure is **counted** from that log; it is never asserted.

**The moat layer is not optional.** Reliability · eval · observability · approval · audit log, per `processes/ai-os-modules.md`. The approval gate is the **R1 floor**; actions climb the rungs on recorded evidence per `processes/autonomy-matrix.md`. Every outward action (send, post, book, pay, dispatch, release) starts gated.

**Guardrails are per-industry and load-bearing.** Where a vertical has a licensure boundary — medical, legal, insurance, tax, clinical care — the AI **drafts for a licensed human**, never determines. This is the same pattern as Conduit's UPL rule and it is a selling point, not a limitation.

**Data.** Synthetic only. No real client data, no real PII, no real payer/carrier credentials, no outbound network calls from a demo build. Seeds must be realistic enough to be recognizable to an operator in that trade.

**ROI is a model, not a promise.** Every build ships a small ROI panel that computes from **the prospect's own inputs**, shows the arithmetic, and labels itself a MODEL with its assumptions listed. No fabricated metrics, no invented testimonials, no benchmark statistics we cannot source to the last 12–18 months. Pre-revenue means outcomes are stated qualitatively (`CLAUDE.md` §External-surface rules).

**White-label.** Client-facing surfaces carry the client's brand only — no yourco name, no yourco logo, no agent names. Agent names are internal-only on every external surface.

**Acceptance.** A build is done when: it runs from one launch.json name · the seed produces a recognizable business · the demo script below runs start-to-finish without a dead click · and a `test_*.py` suite pins the honesty rules (a refusal to state an uncomputable number is a **test**, not a nicety).

---

## How to use a folder

```bash
cd "Pre Build Ideas/<industry>/build"
python3 seed.py          # rebuild the synthetic business
python3 test_*.py        # the honesty suite
```

Then open it by launch name (never guess a port — `.claude/skills/show-surface/`). Each
`build/README.md` carries the 10-minute demo script and the honest limits. `BUILD.md` keeps the
sales-side framing and the original build prompt.

**Per client, this is a template, not a product.** The engagement still starts with an Audit; the
build gets overlaid with that client's own rules, brand and data. Anything shown externally needs
the launch-gate cleared and the surface white-labelled first.

**Where to start:** whoever is actually in the warm network. If that is a coin toss, home services
and insurance agencies are the two whose buyers most reliably think in the numbers these builds
compute.

## Running one

Each prototype ships a seeder and a server, both stdlib-only:

```bash
cd "Pre Build Ideas/<industry>/build"
python3 seed.py      # generates its synthetic data (data/ is gitignored, so this is required first)
python3 server.py    # prints the URL it bound; each prototype has its own fixed port
```

**The `data/` folder is empty on a fresh clone by design** — it is generated, not shipped. If a
prototype looks broken, you almost certainly have not run `seed.py`.

