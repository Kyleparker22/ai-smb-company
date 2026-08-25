# The Mirror Close — Build Spec

**Working name:** The Mirror Close (frontier #21)
**Author:** the Founder
**Stack:** no new runtime — `crm/mirror.py` (the buyer-ladder computation, already live in the insight layer) + `crm/mirror_close.py` (the buyer-facing renderer, built 2026-08-08) · text or single-file HTML output · no model call in the critical path (the brief is computed, not written)
**Status:** **BUILT** — see `offerings/_frontier-roadmap.md` row #21. Runnable today: `python3 crm/mirror_close.py --deal southern`.
**Pillar / form factor:** Sales (pillar 2), shipped as form factor 3 — a document handed to one person.

---

## 1. Concept

Every vendor runs a private read of every deal. It is the one artifact they would never show the buyer, because it contains the places the vendor is pushing and the buyer is not moving.

The Mirror Close hands it over. At the stall — the moment a proposal has been out too long and the follow-up email is about to be written — the buyer receives yourco's own system read of the deal: where they sit on their **own** ladder (have they said the problem out loud, can they name the budget line, has everyone who can say no been in a room), and, load-bearing, **where yourco has got ahead of them**, named as yourco's sequencing error rather than the buyer's delay.

The Sample Client brief the tool produces today reads, in part: *"Our stage is Proposal, which assumed we sent pricing as though the money already has a home… That is our error in sequencing, not a complaint about your pace."* It ends with one question — the first unclear rung — and the line **"Not a signature. An answer."**

**The centrepiece: there is no second, softer model of the deal.** The brief is rendered from the same `compute()` the internal board runs. If the brief and the board ever disagree, the product is a lie, so the architecture forbids it — one computation, two renderings, and the buyer-facing one differs only in person (second, not third) and in what it admits about us.

## 2. Why it's never been done

Sales methodology has had buyer-side qualification for forty years — MEDDIC, Challenger, the whole shelf — and every one of them is scored *about* the buyer, *for* the rep, in a system the buyer will never see. The artifact's entire commercial logic assumes concealment: it records where the buyer is weak so the rep can work the weakness.

Two things have to be true before you can invert it. First, the read has to be **computed rather than opined** — a rep's private notes shown to a buyer are an insult; a system's structured read of cleared/unknown steps is a diagnosis. Second, the vendor has to be willing to have its **own overreach** in the same document, which requires a firm whose positioning is honesty-as-product rather than momentum-as-product. yourco has both: the insight layer already refuses to infer a cleared step from its own stage (that refusal is the entire point of `mirror.py`'s second column), and the house rule against confident-but-unearned claims is the brand. Nobody else's CRM has the buyer's column at all, so nobody else has anything to hand over.

## 3. Build shape

| Piece | What it is | Status |
|---|---|---|
| Ladder computation | The seven buyer steps + what each of our stages silently assumes (`REQUIRES`), overreach and out-of-order detection | **live** — `crm/mirror.py`, unchanged |
| Buyer renderer | `brief()` → text or standalone HTML; second-person phrasing (`BUYER_ASK`), theme-aware, no yourco assets required | **built** — `crm/mirror_close.py` |
| Overreach vocabulary | One plain-English line per step describing what *we* assumed, phrased as our error | **built** — `OVERREACH_LINE` |
| Our-exposure block | Computed, not rhetorical: if a `clients/<slug>/cost.md` ledger exists against an unsigned deal, the brief says we have been building before paper and names it as our risk | **built** — `our_exposure()` |
| Refusals | Unmapped deal → no brief, with the reason; unknown never rendered as cleared | **built** |

**Effort band:** XS — the renderer was a day's work on top of an insight layer that already existed. Per-brief cost is zero: it is a computation over the CRM, not a generation.

## 4. Moat fit

- **It is the insight layer, sold.** The CRM insight suite (`decisions/2026-08-07_crm-insight-layer.md`) was built as Sales-pillar product IP and dogfooded here first. This is the first surface where a *prospect* experiences it — which makes the demo and the diagnosis the same object.
- **Unforgeable.** A competitor can copy the language of the brief; they cannot produce the second column, because they never captured it. An imitation is a paragraph of flattery with no data underneath, and it reads that way.
- **Trust compounding:** the brief is the strongest available demonstration that yourco tells clients things they would rather not hear — the exact property the operated model is asking them to buy.
- **Interlocks:** feeds Trust Ledger (#1) as evidence of the honesty posture in commercial use; the wager (#25) is its natural follow-on (the brief names the unknown rung, the wager measures it); Two-sided proposals (`decisions/2026-07-20_two-sided-proposals.md`) supply the return side this brief deliberately does not restate.

## 5. Gates / compliance

- **No counsel gate.** A document handed to one person in a 1:1 conversation is inside the OtherVenture scope the Founder already ruled on (`decisions/2026-07-20_in-person-local-gtm.md`): unbranded, non-published, non-scaled. It is not marketing, not a send, not a public surface.
- **Agent names never appear** — the brief describes the system by function only (external-surface rule).
- **No fabricated stats, no third-party benchmarks.** The brief contains only the buyer's own marked steps and our own stage. It quotes no industry figure and makes no forward claim.
- **Not sent by an agent.** the Founder sends; agents draft (house rule). The renderer writes a file; a human hands it over.

## 6. Pricing frame

**Not priced.** It is a sales instrument, not a deliverable — the cost of producing one is a computation and the value is a closed deal. It never appears as a line item, and it is never offered as a paid "deal diagnostic" to someone we are not already in a deal with, which would turn a moment of honesty into a product with an incentive attached.

## 7. Activation trigger (build)

**None — built and runnable.** Its *use* trigger is a deal at or past Sit-Down with a filled mirror and at least one overreach step, that has been static longer than our own median stage velocity. Today that is exactly one deal: Sample Client (4/7 cleared, 2 overreach, out-of-order on story and switch). The other two live deals refuse to render because their mirrors have never been filled in — which is itself the instruction: fill the mirror from the record before reaching for the close.

## 8. What we will NOT do

- **No softened buyer edition.** The brief renders from the same computation as the internal board. There is no second model of the deal, no "external-safe" variant, and no field the buyer's copy hides.
- **No brief from an empty mirror.** An unmapped deal is refused, always. A diagnosis assembled from zero marked steps is our assumptions wearing the buyer's name — the single failure mode that would make this instrument dishonest.
- **No inference from our own stage.** If nobody marked a step yes, it renders as *we don't know* and asks. Inferring "they must have cleared budget, we sent a proposal" deletes the entire point.
- **No weaponising.** It is not a pressure device and carries no deadline, no scarcity, no "as you can see, you're behind." The out-of-order line is written as an observation about a pattern, not an accusation about a person.
- **No omission of our own exposure.** If we have been building before paper, the brief says so. A version that diagnoses only the buyer is the thing every vendor already does.
- **Never automated into a send.** It is handed over by a human, in a conversation, or not at all.
