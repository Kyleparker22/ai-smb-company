# Phase 0 — Venue interview guide

> Field instrument for the 3–5 venue interviews in [`SPEC.md`](SPEC.md) §10. Feeds decisions **D1**
> (which buyer first) and **D4** (margin), and gates [`product-venues.md`](product-venues.md).
>
> **Run 3–5. No code until they're done.** Roughly 45 minutes each — longer than the planner interview,
> because the incumbent-software and authority questions can't be rushed.

---

## What's different about this interview

The planner interview hunts for a *pain they feel*. This one hunts for a **number they already track**.

A venue's #1 lever — inquiry response speed — is measurable, sits directly upstream of revenue, and is
something they can look up while you're sitting there. That makes this interview more concrete and
more falsifiable than the planner one. It also makes it easier to get wrong, because **the
self-reported answer will be flattering and the real answer is in their inbox.**

Three things must come back true:

| # | Must be true | Falsified if… |
|---|---|---|
| 1 | Slow inquiry response is **actually costing them bookings** | Their real response time is already fast (Q4) |
| 2 | An overlay can **write back into their system of record** | No usable API → double entry → worse than nothing |
| 3 | The person in the room can **buy, or reach who can** | 6-month multi-stakeholder cycle yourco can't fund |

---

## ⚠️ Do not mystery-shop them

The obvious move is to send a fake wedding inquiry and time the reply. **Don't.**
`offerings/secret-shopper/SPEC.md` §4 sets the standing rule: *no probe of any kind before the
counsel-blessed protocol exists — including "harmless" form fills.* Florida is an all-party-consent
state, the deception bounds are unresolved, and a fake inquiry also wastes a real person's time on a
wedding that doesn't exist.

**The honest substitute is better anyway.** In Q4 you ask them to open their own inbox and read the
timestamps with you. It's their data, it's not a probe, and — critically — **they discover the number
rather than being told it.** A venue director who has just watched themselves take 31 hours to answer
a live lead is in a different conversation than one who has been handed a statistic.

---

## Before you start

**Who to talk to.** 3–5 venues in the **same metro as the planner interviews** (§8 — one market deep).
Mix the types: a barn/estate venue, a hotel with event space, and a country club or dedicated event
centre behave differently. Aim to reach the **Director of Events or Catering** — the GM is often too
far from the inbox and the owner too far from the process.

**How to ask for it.** Same posture as the planner guide — help, not a pitch:

> *"I'm researching how wedding venues handle inquiries and coordination. Not selling anything, won't
> pitch you. 45 minutes, and I'll share what I learn across all the conversations."*

**Come prepared with two things:**
- Their public inquiry path — do they have a form, a phone number, both? (Look, don't submit.)
- Roughly how many weddings they appear to host (Instagram, their calendar page, review counts). You're
  not verifying, you're avoiding wasting Q1 on something you could have read.

**Notes.** Consented recording (Granola, `processes/meeting-capture.md`). The Q4 timestamps and the Q9
system name are the two things you cannot leave without.

---

## The four rules

Same as the planner guide, and they matter more here because you'll be talking to someone with a
professional interest in their numbers looking good.

1. **Ask about their past, never their future.**
2. **Ask for specifics — and here, ask to *see* them.** This is the interview where "show me" works.
3. **Never mention the product until the interview is over.**
4. **Shut up.** Especially after Q4.

---

## The interview

### Warm-up (5 min)

**1. Tell me about the venue — how many weddings do you host a year, and what's the typical package?**
*You need:* weddings/year and **average event value**. Every ROI number downstream is computed from
these two, in their numbers, per the no-fabricated-numbers rule.
*Follow-up:* What else do you host — corporate, galas, other events? *(Tests whether the year broadens
beyond weddings, which widens the product.)*

**2. Who's involved when a wedding inquiry comes in — is that you, a coordinator, a team?**
*Listen for:* headcount and whose job this is. It also tells you who a system would displace or help,
which shapes the politics at Q13.

---

### Part A — The inquiry funnel, which is the whole sale (15 min)

**3. Roughly how many wedding inquiries do you get in a month? And what happens to one that comes in
at 9pm on a Saturday?**
*The Saturday-night framing is deliberate* — that's when couples browse and when the events team is
working an event, not at a desk.
*Listen for:* whether anything happens at all until Monday.

**4. Can we look? Pull up the last five inquiries and the replies — I want to see the timestamps.**

> ### ⚠️ Question 4 is the whole interview.
> This is the number, and it's the one place a self-report will mislead you. Ask them to open the
> inbox and read the gaps out loud with you. Take the five actual figures.
>
> **If the gaps are hours or days** → the lever is real, they've just watched themselves prove it, and
> the rest of the conversation is easy.
> **If the gaps are minutes** → *write that down as a finding, not a disappointment.* The #1 lever
> doesn't exist at this venue, and if that repeats across venues the product's lead argument is gone.
>
> If they won't open the inbox, that's soft data too — note the refusal and move on. Don't push.

**5. Of the couples who inquire, roughly how many end up touring? And of those, how many book?**
*You're building their funnel in their numbers.* Inquiries → tours → bookings.
*Follow-up:* Do you know why the ones who never toured didn't? *(Usually they don't — which is itself
the finding.)*

**6. Has a couple ever told you they went elsewhere because someone got back to them first?**
*Asking for a memory, not an opinion.* One vivid story here is worth more than any statistic, and it's
the line you'd quote back to them later.

**7. Which dates do you struggle to fill — and what do you currently do about it?**
*Tests the off-peak yield play.* Fridays, Sundays, off-season.
*Follow-up:* Would you discount to fill a Friday? By how much? *(If yes, steering flexible couples to
those dates has direct, attributable margin.)*

---

### Part B — After they book (8 min)

**8. Once a wedding is booked, walk me through what your team does between then and the day. Where
does the time go?**
*Listen for:* headcount chasing, BEO revisions, vendor coordination, final payment chasing — and how
much of it is repetitive.
*Follow-up:* How many hours per event, roughly? *(Feeds the coordination half of the ROI.)*

**9. What system holds your bookings, BEOs and contracts? What does it not do well?**

> ### ⚠️ Question 9 is the gating technical risk.
> Tripleseat, Perfect Venue, Event Temple, Planning Pod, a hotel PMS — whatever it is, **the OS must
> write back into it or the venue gets double entry, which is worse than nothing** (`product-venues.md`).
> *Follow-ups:* Does it have an API, or an integrations page? Have you connected anything else to it?
> Who set it up?
> *Note the fence:* this is a **system of record**, which the audit's teardown filter says to
> **overlay, never replace**. You are testing integration feasibility, not a replacement target.

**10. Does it already do anything automatic with inquiries — auto-replies, lead routing?**
*The honest threat to the whole pitch.* If their existing platform already auto-responds, the lead
argument narrows to "ours is better," which is a much weaker position than "you have nothing."
*Follow-up:* Is it turned on? Do you use it? *(Very often the answer is "it's in there somewhere" —
which is the build-vs-rent finding: the tool exists and doesn't get used.)*

---

### Part C — Vendors, authority, and the conflict (12 min)

**11. Do you have a preferred-vendor list? How did vendors get on it, and how does that work
commercially?**

> ⚠️ **This surfaces the conflict with product 1.** Some venues take commissions or kickbacks from
> preferred vendors. Ask it neutrally and without judgment — it's a normal arrangement and they'll
> tell you plainly if you don't make it weird.
> **If commissions exist**, product 1 (which sells couples *aligned incentives*) cannot advise a couple
> while steering them toward a venue's commissioned vendor. Log it and route to Ray — it's a counsel
> question before those two products ever touch the same couple.

**12. When a couple books, do they usually have a planner? Do you ever have couples who clearly need
more help than your team can give?**
*This is the distribution test* — the strategic reason venues are sequenced ahead of couples. You're
finding out whether there's a real population of booked, un-planned couples they'd happily hand off to
something.

**13. Would you be comfortable with software drafting the first reply to an inquiry? What about
messages to couples who've already booked and paid a deposit?**
*Expect: yes to the first, hesitation on the second.* Defines the R1 boundary and the labour math.
*Watch the politics:* if a coordinator's job is largely inquiry response, the person in the room may
be protecting them — or may be them. That's not an objection to argue with; it's a fact about the sale.

**14. If you wanted to bring in something like this, how does that decision get made here? Who signs?**
*Asked plainly.* A Director of Events may not hold $5,000/mo authority.
*Follow-up:* What's the budget cycle? Have you brought in a new system recently — how long did it take?
*This answers whether yourco can afford the sales cycle at $0 cash.*

---

### Part D — Close (5 min)

**15. If inquiries were answered within five minutes, every time, day or night — what do you think
that's worth to you?**
*The only forward-looking question in the guide, and it's placed last on purpose,* after they've seen
their own timestamps and their own funnel. Their number, unprompted.

**16. Who else should I be talking to?**

---

## The transition — only after the questions are done

Same rule as the planner guide. Say the interview part is over, then:

> *"That's everything. Can I tell you what I'm actually working on?"*

Two sentences, then stop. **Skip it if Q4 came back in minutes** — you'd be pitching a fix for a problem
they demonstrably don't have, and they'll remember that.

---

## After each interview — capture within the hour

| Capture | Why |
|---|---|
| Weddings/year · **average event value** | Every ROI number is built from these |
| **Q4's five real timestamps** | The finding. Not their estimate — the actual gaps |
| Inquiries/month · tours · bookings | Their funnel, in their numbers |
| **Q9 system name + API answer** | The gating technical risk |
| Preferred-vendor commission arrangement | The product-1 conflict → Ray |
| Who signs, and the budget cycle | Whether the sale is affordable |
| The Q6 story, verbatim | The line you'd quote back |

### Tally sheet

| # | Venue | Type | Weddings/yr | Avg event $ | Q4 response gaps | System of record | API? | Who signs |
|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | |
| 2 | | | | | | | | |
| 3 | | | | | | | | |
| 4 | | | | | | | | |
| 5 | | | | | | | | |

---

## After all of them — the decision

**Build the ROI case in their real numbers, showing the math** (audit SOP rule, and it applies to
internal analysis too):

> *Inquiries/month × the share that currently go cold × their tour-to-book rate × average event value
> = the annual value of answering faster.*

Compare that to $2,000–2,500/mo for the on-ramp and $5,000–6,500 for Suite. At a typical venue, one
additional booking often covers a quarter — **but compute it, don't assert it.**

**Then answer D4:** with the venue absorbing the approval labour, does the margin hold? And answer
**D1** — comparing these five against the five planner interviews, which buyer has the sharper pain,
the shorter sale, and the better economics?

### Kill criteria — pre-committed

| If… | Then |
|---|---|
| **Most venues' Q4 gaps are already minutes** | The lead argument is gone. The venue product falls back to coordination-only, which is a weaker and more crowded pitch — re-scope before building. |
| **No usable API on the dominant system of record** | Double entry. **This is a hard stop** — do not build until integration is proven on at least one platform. |
| **Their platform already auto-responds and they use it** | You're selling an upgrade, not a capability. Much harder. Re-scope. |
| **Nobody in reach can sign, and the cycle is 6+ months** | The sale is real but unaffordable at $0 cash. Planners first, come back after revenue. |
| **Commissions are widespread on preferred-vendor lists** | Products 1 and 3 conflict. Ray rules before either ships to the same metro. |

**If the API criterion trips, that alone is enough to stop** — it's the one failure that can't be
positioned around.

---

## The one-sentence reminder

The planner interview asks what hurts. **This one asks to see the inbox.** If you leave without Q4's
real timestamps and Q9's API answer, you ran a nice conversation and learned nothing that decides
anything.
