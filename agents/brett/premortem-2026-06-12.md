# Pre-Mortem — YourCo (2026-06-12)

> **Owner: Brett** (strategy; the "keep the Founder in line / watch the whole business" charter). Method: imagine it's 18 months out and YourCo has shut down. Work backward — what killed it? Ranked by *likelihood × severity*, honest over comfortable. Each risk: the mechanism, the early warning, the mitigation.

## The frame
It's late 2027. YourCo is dead. The post-mortem on the wall isn't flattering, because the most likely causes of death are the *quiet* ones — not a dramatic competitor, but a founder who built a beautiful machine and never drove it anywhere.

---

## Tier 1 — the most likely killers

### 1. It never actually launched. (highest probability)
**Mechanism:** The OS became the product. Building it was intellectually satisfying, safe, and infinite — there was always one more agent to generalize, one more demo to add, one more gate to harden. Launching meant exposure, rejection, and the end of the comfortable building phase. So the launch date kept not getting set. Eighteen months in, YourCo had the most sophisticated internal AI-operations OS anyone had ever seen, 30 agents, a flawless runtime — and **zero clients, zero revenue, and a founder who'd quietly moved on.** Building was a sophisticated form of procrastination.
**Early warning (already visible):** months of internal building with no launch date; "I can't set a launch date yet"; every session ends with "what else can we build" rather than "who did we talk to." *This is the single most-present warning sign in the whole company right now.*
**Mitigation:** Set a launch date and work backward — even an imperfect one. Define "launched" as *one real conversation with one real prospect this week*, not "the OS is ready." The OS is already past good-enough. **The next unit of work should be a human you don't know saying yes or no.**

> **UPDATE 2026-06-12 — material context (the Founder):** YourCo **cannot legally launch/go-live until an OtherVenture matter is resolved (~a few weeks out)**. This *materially lowers* the probability of cause #1 — the building isn't avoidance, it's productive use of a *forced* pre-launch window so launch is a switch-flip when the legal block lifts. That's a sound strategy. **Two residual cautions remain, though:** (a) when the block lifts, *actually go* — don't let the building *habit* outlast the *constraint* (the failure mode would be the block lifting and the OS still feeling "not quite ready"); and (b) the plan holds only if the **OtherVenture timeline holds** — "a few weeks" must not quietly become "a few months," or cause #1 reconverts. **And the bigger point:** a forced wait is a *gift* — but only if it's spent on the risks internal building *doesn't* touch. More agents don't de-risk demand or delivery. To the extent the constraint allows *any* pre-launch relationship-building (warm intros, a hand-built first-client pipeline, validating the offer in conversation), that's a higher-value use of these weeks than more internal polish — it attacks Tier 1.2 and 1.3, which remain fully live regardless of the legal timing.

### 2. No demand — the cold pitch to skeptical SMBs doesn't convert, and the trust paradox bites.
**Mechanism:** Sadie validated the *pain* (missed calls cost real money), but not that a $1M landscaper will buy a $4k + $750/mo *(pricing as written 2026-06-12; since superseded — on-ramp $1,500/mo floor, OS tiers from $3k/mo, `pricing/v0/os-tiers.md` — which raises, not lowers, this trust bar)* "managed AI employee" from a **cold email by an unknown solo founder with no logos, no case studies, no track record.** YourCo sells *trust and reliability* — the exact things it has least of at launch. Reply rates sat near zero; the few calls booked stalled at "let me think about it"; the chicken-and-egg (need a client for proof, need proof for a client) never broke.
**Early warning:** Email 1 goes out, reply rate < 1–2%; calls book but don't convert; everyone "loves it" and no one signs.
**Mitigation:** Don't launch cold-to-strangers as the *only* motion. Land the **first 1–3 clients through warm channels** — anyone in your network, a referral, a founder-led hand-built deal — even free or steeply discounted, to manufacture the proof (a real logo, a real outcome, a real case study). *The first client is a trust-purchase, not a sales-process. Buy it however you have to.*

### 3. The first delivery breaks the core promise on contact with reality.
**Mechanism:** "Live in 48 hours" and "the agents run delivery autonomously" are **unproven against a real client** — the dry-run was paper + a sandbox. The first real engagement hit a messy real-world stack, an integration that didn't behave, a client who wanted changes, and the 48 hours became two weeks. Or worse: it *did* go live, and an unsupervised employee mishandled a real customer (booked wrong, said something off, leaked something) — and for a business whose entire moat is *reliability*, **one public failure early was fatal.** The autonomy ambition amplified this: removing the human too soon (the stated goal) turned a recoverable error into a reputation-ending one.
**Early warning:** the first build slips past 48h; an eval gate gets waived "just this once"; an itch to go fully-autonomous before the eval track record exists.
**Mitigation:** Treat the first 3–5 deliveries as **white-glove, the Founder-in-the-loop, over-deliver** engagements — explicitly *not* the autonomous model yet. Earn the autonomy ladder's phase advances with real eval-vs-reality data (already designed — *honor it*). Better a flawless 4-day delivery than a broken 2-day one.

---

## Tier 2 — serious, second-order

### 4. The unit economics invert.
**Mechanism:** YourCo absorbs all token/model/voice/infra cost by design. A heavy-usage voice client (Vapi + Twilio + LLM minutes) or a few high-volume accounts ate the $750 retainer. Margin went negative exactly as YourCo "grew." The cost-absorption model — a feature in the pitch — became the thing that bled it out.
**Warning:** per-client `cost.md` creeping toward the retainer; Charles flagging margin compression.
**Mitigation:** Model worst-case per-vertical cost *before* pricing (Polo). Cap or meter the cost-absorption for outlier usage. Watch the heaviest client like a hawk.

### 5. The solo-founder ceiling (made worse by divided attention).
**Mechanism:** Selling, delivering, and improving all at once is impossible for one person past ~3–5 clients — *if the agents can't truly run delivery* (the central, unproven bet). Add that OtherVenture2 and OtherVenture split the founder's attention, and YourCo never got the focused push escape velocity requires. It didn't fail loudly; it just never got enough of the Founder.
**Warning:** the Founder personally doing delivery work the agents were supposed to do; weeks where YourCo got scraps of attention.
**Mitigation:** Prove the agents can actually carry delivery on the first client (the autonomy bet, validated small). Be honest about attention allocation across ventures.

### 6. Commoditization erodes the moat.
**Mechanism:** The $29 bots commoditized below; the platforms (Vapi, GHL, and the model labs themselves shipping agents) commoditized the middle. "Managed reliability + eval + trust" turned out to be a *feature a funded competitor or a platform could add*, not a durable moat — and a better-capitalized "managed AI employees" startup simply out-executed a solo bootstrapper.
**Warning:** a funded competitor with the same pitch; Vapi/the platforms adding eval/reliability layers.
**Mitigation:** Lean into the parts that *don't* commoditize — the per-client relationship, the executive trust, the vertical depth, the accountability. Win specific verticals deeply before someone wins the category broadly.

---

## Tier 3 — tail risks (lower probability, high severity)

- **7. A legal/compliance blowup.** Cold email/SMS at scale → a TCPA/FTSA action, or a client-customer data breach (PHI/PII through the agents). For a solo bootstrapped founder, one class action or one HIPAA breach is existential. *Mitigation:* the legal suite is drafted — get counsel review before the first send and the first PHI client; don't send SMS until 10DLC + FTSA sign-off; honor the BAA gate.
- **8. A security incident.** Always-on runtime + connectors + client-tenant access + the EIN-in-repo = real attack surface. *Mitigation:* the 2FA sweep (still open), least-privilege, the hardening already done — finish it.
- **9. Vendor concentration.** Anthropic, the VPS, Instantly, Vapi — a pricing/ToS/ban shock (you've already hit Reddit + QuickBooks walls) breaks the OS. *Mitigation:* know the fallbacks (already documented for some); don't single-thread the critical path.
- **10. AI progress collapses the value prop.** If building an AI employee becomes trivially easy, "let us manage the complexity" weakens. *Mitigation:* move the value from *building* to *running + accountability + trust* — the part that stays hard.

---

## The meta-pattern (the one thing)
Several of these share a root: **falling in love with the autonomous machine instead of the business it's supposed to serve.** It's what delays the launch (Tier 1.1), it's what tempts a too-early hands-off delivery (Tier 1.3), and it's what makes "build another internal thing" feel like progress when the only progress that matters now is *a real client*. The OS is a means. Right now it's being treated, a little, as the end.

## Bottom line — what actually kills YourCo
Not a competitor. Not the tech. **The overwhelmingly likely cause of death is that it never launches, or launches so late and so hesitantly that the founder's energy is gone — with a magnificent OS as the headstone.** Everything else is second-order to that.

## What to watch (the leading indicators)
1. **Days since the last conversation with a real prospect.** If this number keeps climbing while the repo grows, you are dying of cause #1. (This is the metric.)
2. First-reply rate on Reilly's batch (demand signal).
3. First delivery: actual hours to go-live; eval-vs-reality (autonomy honesty).
4. Per-client cost vs. retainer (margin).
5. Counsel-review + 2FA still open (the cheap insurance against the tail risks).

— Brett
