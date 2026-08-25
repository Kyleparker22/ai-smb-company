# Phase 0 — Planner interview guide

> Field instrument for the 5 planner interviews in [`SPEC.md`](SPEC.md) §10. Feeds decisions **D1**
> (which buyer first) and **D4** (margin), and is the gate on [`product-planners.md`](product-planners.md)
> being built at all.
>
> **Run 5. No code until they're done.** Roughly 40 minutes each.

---

## What this is actually for

Not validation. **Falsification.** You already believe planners are the right first buyer — this
exercise exists to find out if that's wrong while finding out is still free.

Three things must come back true. Any one of them false changes or kills the product:

| # | Must be true | Falsified if… |
|---|---|---|
| 1 | The two failures are real for **them** (vendors don't reply · quotes aren't comparable) | See ⚠️ below — this is the likely killer |
| 2 | They're **capacity**-constrained, not demand-constrained | Their calendar has gaps and the real problem is booking couples |
| 3 | The money works — they can pay $1,500–3,000/mo and the capacity delta is credible | The arithmetic doesn't clear at their volume |

---

## ⚠️ The finding most likely to kill the planner-first recommendation

**"Vendors don't reply" may be a *couple* problem, not a *planner* problem.**

A couple is a stranger emailing a florist once in their life. A planner who has sent that florist
$40,000 of business gets a reply the same day. If that's true, the single highest-value agent in the
system — the chaser — has **no value to this buyer**, and the planner product shrinks to quote
normalisation, timeline and capacity.

That wouldn't kill the offering. It would mean **couples are the buyer with the real pain and planners
are the buyer with the real money**, which is a materially different product decision than the one the
spec currently recommends.

**Questions 3 and 4 exist to test exactly this. Do not lead them.** If you ask *"vendors are slow to
reply, right?"* every planner will politely agree and you will have learned nothing. Ask what happened
last week and count.

---

## Before you start

**Who to talk to.** Five planners in **one metro** (§8 — density beats scatter). Warm intros first,
per the GTM stance. Wedding planners live on Instagram; local wedding-vendor Facebook groups and venue
preferred-vendor lists are the other two obvious pools. Aim for a mix: at least two doing 20+ weddings
a year, and at least one who is visibly *not* busy — the demand-constrained case is data, not a wasted
slot.

**How to ask for it.** You are asking for help, not selling. Something like:

> *"I'm researching how wedding planners actually run their businesses — I'm not selling anything and
> I won't pitch you. 40 minutes, and I'll share what I learn across all five conversations if that's
> useful."*

Then honour both halves of that. If you pitch, the data is worthless and you've burned the intro.

**Notes.** Record with consent (Granola is in the stack — `processes/meeting-capture.md`). Verbatim
quotes on the two failures and on the capacity question are the deliverable; a summary is not.

**Afterward.** Each planner goes into the CRM as a **Connector-taxonomy contact** or prospect as
appropriate (`decisions/2026-07-06_advisors-connectors-taxonomy.md`), with the interview as the first
activity. Five conversations that leave no CRM trace is the pattern the audit already flagged.

---

## The four rules

Borrowed from *The Mom Test*, and they are the difference between data and flattery.

1. **Ask about their past, never their future.** "How many did you send last week?" not "would you
   use…?" People are unreliable narrators of their own future behaviour and reliably polite about it.
2. **Ask for specifics and numbers.** "A lot" is not an answer. Get the count.
3. **Never mention the product until the interview is over.** The moment they know what you're
   building, they start being nice to you.
4. **Shut up.** The silence after a question is where the real answer lives. Count to five before
   filling it.

---

## The interview

### Warm-up (5 min)

**1. Tell me about your business — how many weddings did you do last year, and what does a typical
package include?**
*Listen for:* volume, price point, whether they do full-service or day-of only, team size.
*You need:* weddings/year, average fee. Everything downstream is computed from these two.

---

### Part A — Where the time goes (10 min)

**2. Walk me through last week. What actually filled the hours?**
*The most important open question in the guide.* Do not steer it. Let them wander.
*Listen for:* what they name unprompted, and — just as telling — what they never mention.

**3. Think about the last wedding you booked vendors for. How many vendors did you contact, and how
many got back to you?**
*This is the wedge test. Get the two numbers.*
*Follow-ups:* How long did the slow ones take? Did any never reply? What did you do about it?
*⚠️ If the answer is "they all reply, they know me" — that is the finding. Write the quote down
verbatim and keep going. Do not argue with it or explain why it should be otherwise.*

**4. When you've got quotes from five photographers, how do you decide between them? Show me — can
you pull one up?**
*Listen for:* whether comparison is actually hard, or whether experience has made it trivial for them.
*Follow-up:* Where do the quotes differ in ways that aren't obvious? Has a client ever been surprised
by a cost you didn't catch?

**5. What part of the job do you like least?**
*Listen for:* whether it matches what the engine automates. If the thing they hate is tasting menus
and dress fittings, we're solving the wrong problem.

---

### Part B — The qualifier (10 min)

**6. How many weddings did you turn away last year — and why?**
*Follow-up:* Were you fully booked, or did those not fit for another reason?

**7. If you could do twice the weddings next year without hiring anyone, would you have the couples to
fill them?**

> ### ⚠️ Question 7 is the deal.
> **Yes → capacity-constrained.** The OS converts directly into revenue. Real prospect.
> **No / hesitation / "I'd need more leads" → demand-constrained.** **The product as scoped does not
> help them.** That is not a lost interview — it is the answer to D1, and it means their bottleneck is
> Marketing and Sales, not Operations. Route it, don't force it.
>
> If four of five say no, the planner-first recommendation is wrong and the spec needs re-sequencing.

**8. What's your ceiling right now — what would have to change for you to take on more?**
*Listen for:* whether they name time, money, staff, or demand. Their own diagnosis of their
constraint, in their words.

---

### Part C — The stack and the boundary (10 min)

**9. What software do you pay for every month? Roughly what does it all cost?**
*The build-vs-rent teardown lens from `processes/audit-sop.md`.*
*Follow-ups:* Which of those do you actually open every day? Which do you resent paying for? Which
screens does your team actually touch?
*Note:* these tools are **systems of record** — the teardown's own filter says overlay, never replace.
You're testing integration feasibility here, not a replacement target.

**10. Where does the couple's information live? If I asked you right now for the final headcount on a
wedding six months out, where would you look?**
*Listen for:* spreadsheets, their CRM, their inbox, their head. Tells you what an overlay must write
back into, and whether double entry is a risk.

**11. Would you be comfortable with software drafting emails to *vendors* on your behalf? What about
to *couples*?**
*Expect a hard yes on the first and hesitation on the second.*
*This defines the R1 boundary and the labour math* — if they insist on writing every couple-facing
message themselves, the time saved shrinks and the margin case with it.

**12. What part of this job would you never hand to software, no matter how good it got?**
*Listen for:* taste, relationships, the day itself. This is the positioning line — and if they name
something the engine *does* automate, that's a red flag for the whole thesis.

---

### Part D — Close (5 min)

**13. If you got ten hours a week back, what would you actually do with them?**
*Listen for:* "more weddings" (capacity-constrained, confirms Q7) vs "see my kids" (real answer, but
it means the ROI is lifestyle, not revenue — which is a much harder $3,000/mo sale).

**14. Who else should I talk to?**
*Every interview should produce the next one.*

---

## The transition — only after the questions are done

If and only if you've finished, you can drop the researcher hat. Say so explicitly, so they know the
interview part is over:

> *"That's everything I wanted to ask. Can I tell you what I'm actually working on?"*

Then describe it in one or two sentences and **stop**. If they lean in, you have a prospect. If they're
polite, you have data.

**Do not do this with a planner who answered "no" to Q7.** Pitching a capacity product to a
demand-constrained business is the churn you were warned about, and it costs you the referral in Q14.

---

## After each interview — capture within the hour

| Capture | Where |
|---|---|
| Weddings/year · average fee · turned-away count | This file's tally, below |
| **Q3's two numbers** (vendors contacted / replied) | The wedge test — the whole point |
| **Q7 verbatim** | The qualifier |
| Their monthly software spend + what holds their records | Teardown + integration feasibility |
| The quote you'd put in front of Partner B | Sessions run on evidence, not summaries |
| Contact + activity | The CRM |

### Tally sheet

| # | Planner | Metro | Weddings/yr | Avg fee | Vendors contacted → replied | Q7 capacity? | Software $/mo |
|---|---|---|---|---|---|---|---|
| 1 | | | | | → | | |
| 2 | | | | | → | | |
| 3 | | | | | → | | |
| 4 | | | | | → | | |
| 5 | | | | | → | | |

---

## After all five — the decision

**Compute, in their real numbers, no invented figures** (the audit SOP's no-fabricated-numbers rule
applies to internal analysis too):

- Median weddings/year × average fee = **their gross**
- $1,500/mo on-ramp and $3,000/mo Core as **a % of that gross** — if Core is above ~20%, the on-ramp is
  the only honest opener
- The capacity delta: (weddings they could do) − (weddings they do) × average fee = **the ROI story**,
  and it only exists if Q7 said yes

**Then answer D4:** how many hours per wedding would yourco's operator spend on approvals, and does the
margin survive it? The planner absorbing that labour is the whole reason this buyer was sequenced
first — confirm it's true.

### Kill criteria — real, and pre-committed

Write the verdict down before you talk yourself out of it.

| If… | Then |
|---|---|
| **3+ of 5 say vendors reply fine to them** | The chaser has no value here. Re-sequence: couples have the pain, planners have the money. Revisit D1 before building. |
| **3+ of 5 are demand-constrained (Q7 = no)** | Planner-first is wrong. The Marketing/Sales pillars are the real product for this buyer. |
| **Quote comparison is trivial for experienced planners** | The second wedge is couples-only too, and the planner product is just capacity software — a much weaker, more crowded position. |
| **Core lands above ~25% of a typical planner's gross** | The on-ramp is the only viable entry, and Polo should reprice before anything is built. |
| **They won't let software touch couple-facing comms** | The labour math changes. Re-run D4 before committing. |

**If two or more kill criteria trip, do not build the planner product.** Take the finding to the venue
interviews — a venue's economics are different enough that the answer may flip, and finding that out
costs three more conversations rather than a build.

---

## The one-sentence reminder

You are not there to find out whether they like the idea. **You are there to find out whether the two
failures are real for them and whether they have more demand than capacity.** Everything else is
texture.
