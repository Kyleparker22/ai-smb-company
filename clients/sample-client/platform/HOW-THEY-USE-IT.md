# How Sample Client runs a project through the platform — start to finish

The walkthrough narrative: one project, every hand it touches. Written 2026-08-10 for the Client Owner walkthrough; mirrors what's actually built at :8804. The cast: **Charlene** (intake/admin) · **Client Owner** (owner, install/design sales) · **Corey** (sells on-site) · **Colton** (design + estimating — the daily power user) · **Noah** (operations — the gate).

## Phase 1 — The call comes in (Charlene, 3 minutes)
Homeowner calls wanting a backyard redone. Charlene clicks **+ New** in the platform header, types the client name and address into the **Project** tab, and — the new habit that makes everything downstream sharper — asks one question on the phone: *"Do you have a survey or site plan of the property? Text or email it over."* If it arrives, she uploads it on the **Measurements** tab. That's her whole job here. The project now exists on the shared server: whoever opens the platform next, on any device, sees it.

## Phase 2 — The site visit (Client Owner or Corey, ~1 hour on-site instead of a return trip)
At the house, the rep does three things they mostly already do:
1. **Photos** — a handful of phone shots of the yard → uploaded under Project → Site photos.
2. **Moasure walk** — trace the perimeter and key features. The trace goes into **Measurements → trace import**, and the board **draws the property, house line, and features to scale automatically** — the "drawing the house is the longest part" step, gone. Every envelope dimension registers as ground truth.
3. **Listen** — wants, style, budget signals → typed or dictated into Consult notes.
Then the on-site magic: on the **2D Board**, hit **✦ Propose layouts**. Three options appear — Entertainer, Resort Lawn, Essentials — every one geometrically locked inside the measured yard. Pick one with the client standing there, drag things where they want them, and flip to the **Design Studio ✦** tab: the client sees their photos, the plan to scale, three tier prices, and a **live ballpark range** — with the "give us your survey and watch this number tighten" moment played out on the screen in front of them. For jobs like fencing where Corey closes same-visit, this IS the close. Access difficulty, grade, and utility flags get set on the **Quote** tab sliders while it's all fresh.

## Phase 3 — The desk pass (Colton, same day or next morning — not two weeks later)
Colton opens the same project at the office. He tightens the 2D (bind any estimated dimension to a real measurement — anything unverified stays visibly flagged), picks exact materials (in-stock-first; special-order badged with lead-time warning), and sanity-checks the **Quote** tab: every line item priced from the SiteOne-basis catalog, labor from the benchmarks **already auto-corrected by the actuals history** (the ×-calibration from every completed job), difficulty multipliers applied. The **Scope** tab has already written the scope of work in Sample Client's voice — Colton edits or deletes lines instead of writing from scratch. Plants? The **Shepherd's availability feed pulls itself** — the catalog knows what's actually in stock this week before anyone orders.

## Phase 4 — Subs, without the phone tag (Colton/Noah → Client Owner sends)
If the design has a pergola or gas feature, the **Subs** tab has already generated a scoped RFQ per sub — the dims, the scope block, the access rating, addressed to Jonathan or the plumber — with the engine's **learned price band** shown next to it ("Kenny: $2.20–2.50/sqft") so the allowance is honest even before anyone answers. Client Owner copies and texts it (a human always sends). When the reply comes back, the number is logged and **replaces the allowance in the quote automatically** — and tightens that sub's band for every future job.

## Phase 5 — Noah's gate (Noah, 5 minutes, from anywhere)
Nothing customer-facing moves until the **Approvals** tab is green: labor and crew-days review, means-and-methods (sleeves, staging, machine access), any job over $50k flags his site walk, open sub allowances, NC811 locate if utilities are flagged, and any dimension not yet traced to a real measurement. He checks boxes on his phone. Gate open = the quote may go out.

## Phase 6 — The quote goes out (Client Owner/Colton)
Two buttons: **Print/PDF — client proposal** (the client-safe document: the accuracy badge, the range, tiers, scopes — never a cost, margin, or crew-day) and **→ Aspire CSV** (the same line items in Aspire's import shape — becomes a live API push the moment Aspire credentials land). The proposal carries the **72-hour validity** and the track record: *"our last N ballparks landed within ±X% of final price."* No other contractor in Yourtowncan print that sentence.

## Phase 7 — Signed → the pitch becomes the record (Charlene/crew lead, 1 minute a day)
Flip the project's stage to **Signed → In progress**. The same Design Studio link the client fell in love with now grows a **build journal**: crew photos and a one-line note per day land on the client's timeline. The client watches their own project instead of calling for updates. At **Complete**: pricing disappears from their view, replaced by the reveal and a **maintenance calendar** generated from what was actually installed.

## Phase 8 — The flywheel (Charlene, 2 minutes per closed job)
When the job closes in Aspire, the final numbers get logged on the **Actuals ⟳** tab (auto-imported once the Aspire integration is live): quoted vs final, estimated vs actual crew-days. The engine re-tunes itself — labor calibration, difficulty math, the accuracy badge. **Every job Sample Client finishes makes the next quote measurably more accurate**, which is the moat no competitor can copy, because it's powered by their history and nobody else's.

## Who touches what (the one-glance version)
| Person | Tabs they live in | Time per project |
|---|---|---|
| Charlene | Project (intake), stage flips, Actuals logging | ~10 min total |
| Client Owner / Corey | 2D Board + Design Studio ✦ on-site; sends RFQs & proposals | the site visit itself |
| Colton | Measurements, 2D Board, Quote, Scope, Subs — the craftsman's bench | ~1–2 hrs vs. 2 weeks |
| Noah | Approvals (phone-friendly checklist) | ~5 min |
| The client | Design Studio ✦ only — vision, plan, tiers, range, journal. Never costs. | — |
| The platform itself | Shepherd's availability pulls, sub price-band learning, self-tuning calibration, integration syncs | continuous, unattended |

The through-line to say out loud on the walkthrough: **today their sales cycle is 6–8 weeks of drawing, phone tag, and pricing lag. This is the same people doing the same judgments — with the drawing, the math, the writing, and the chasing already done. The judgment stays human; the waiting disappears.**
