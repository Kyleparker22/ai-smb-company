# 2026-08-11 — Connector Program v2: referral modes, a submission bounty, recruiting at R1, and connectors as the primary growth lever

## Decision
Four calls, made together by the Founder from a transcript review of the connector program
(`processes/partnerships/connector-os.md`, `referral-program.md`). Each is stated here in the form it
was chosen, including the two that were chosen **against** the recommendation on this page — the
recommendation is preserved so the trade is legible later rather than re-argued.

### 1. Referral **mode**, not connector type — Introducer / Sourcer
A referral carries a mode; a **person does not**. The same connector can hand yourco a warm intro on
Monday and a list of names on Friday, and both are normal.

| Mode | What the connector did | Who does the outreach |
|---|---|---|
| **Introducer** | Made an actual introduction to a business owner they know | The connector opens the door; yourco takes it from there |
| **Sourcer** | Submitted a business owner's name + contact, no intro | **yourco** — we become the caller |

Stored per referral (`meta.referralMode[<companyId>]`), set by yourco, **read-only to the connector**
like stage and retainer. Rejected: modelling this as a permanent person-type ("Connector Partner" /
"Connector Referral"), because a person doing both would be mis-typed on half their book.

**Naming:** "Connector Partner" was rejected because **Partner is already the name of the 11+ active-client
commission tier** (15%) in `referral-program.md`. Two things named Partner across the console, the
statements, and the agreement is the exact drift `change-one-sweep-all` exists to stop.

### 2. A submission bounty — $25 verified contact + $25 booked call
A **Sourcer** submission pays, in two steps, on top of (not instead of) the normal commission if it
ever closes:

| Event | Bounty | Verified by |
|---|---|---|
| Contact submitted **and verified** as a real, reachable business owner | **$25** | yourco, within **24–48h** of submission |
| That contact **books a real conversation** (sit-down/audit — the same event the ladder computes as R1 evidence) | **$25** | The booking exists in the CRM |
| That contact becomes a paying client | normal escalator commission (10 / 12.5 / 15%) | Charles, at close |

Deliberately **not** the flat $200-at-signup from the transcript: that paid cash for *completing signup*,
which is compensation for enrolling. Open numbers the Founder still sets, carried as bracketed opens in
`referral-program.md`: submission cap per connector per `[[month]]`, what exactly counts as a verified
contact, whether the booked-call bounty stacks with or nets against the first commission payment.

### 3. Recruiting moves R2 → R1, and the override is payable at R1
- **May recruit connectors:** at **R1** (one referral reached a real conversation), not R2.
- **Override payable:** also at **R1**. No active-book qualification.

`UNLOCKS` in `crm/connector_ladder.py` moves `recruit_connectors` from R2 to R1 — that constant is the
single gate every surface reads, so the console, the onboarding script, and the packet follow it
automatically.

### 4. Connectors are yourco's **primary growth lever**
Promoted from "one channel among several" in `processes/demand-generation.md` to the stated primary
motion, modelled on agent/sub-agent networks. Swept into `CLAUDE.md`, `demand-generation.md`, and Bird's
scope in `04_agent_roster.md`.

## Context
the Founder reviewed transcript notes proposing: two connector subtypes, a $200-at-signup incentive (100
connectors × $200 = $20K, against ~300 leads → 10% close → $60K MRR), a tiered $25/$25 alternative, a
referral tree in the console, and reconsidering the R2 recruiting gate. Four things were true of the
existing program at the time of the review:

1. The console **already ships** the downline tree (production, pipeline, editable goals, per-member
   reporting). "Connectors can see their sub-connectors" was already built; only "super connectors
   manage their network" is genuinely open, and it remains open here.
2. **R2 was unreachable.** R2 requires a referred client live *and retained 90 days*. With zero signed
   clients, no connector could recruit anyone — the gate wasn't limiting some connectors, it was
   limiting all of them indefinitely. That is the strongest argument for moving it, and it is why
   moving it is the right call independent of the compliance trade below.
3. The R2 gate was **load-bearing for compliance**, not just product. It was offered to counsel as the
   active-book qualification standing in for the depth cap the Founder declined
   (`decisions/2026-08-07_override-depth-uncapped.md`, checklist item 4b).
4. `connector-os.md` §1 had already made the "nothing valuable for enrolling" call deliberately — it is
   why the free digital employee sits at R1 and not at join.

## Why (the Founder's call)
Connectors are the compounding channel: a network that recruits itself is the only motion that grows
without yourco's headcount, and the program has been designed but never *run*. The gates that made it
un-runnable (R2 unreachable, no reason for a connector to act before a close lands months later) were
removed in favour of getting the thing moving. The bounty exists because the gap between "signed up" and
"first referral" is where referral programs die, and $25 is a real reason to act this week.

**The recommendation this overrides, recorded honestly:** a booked-call-only bounty (no per-contact
payment) and recruit-at-R1-but-override-payable-at-R2 were recommended, on the grounds that both keep
"$0 is paid for anything but collected client revenue" true. the Founder chose the per-contact payment and the
full override unblock. Both were argued once and decided; this file is the record, not a re-argument.

## What this decision obligates

1. **Counsel is asked a materially different question — item 4c is new and is the point.** The program
   now (a) pays cash on two non-revenue events, (b) lets any R1 connector recruit, and (c) keeps
   uncapped override depth. The sentence §A rested on — *100% of payout is tied to real collected
   client revenue, $0 to recruiting* — **is no longer true**, and the active-book qualification offered
   as the non-depth guardrail **no longer exists**. Counsel must be asked to price the combination, not
   the pieces. Added to `legal/counsel-review-checklist.md` as item **4c** plus §A item 2a; this is now
   the checklist's second hard-stop alongside depth.
2. **Sourced contacts make yourco the caller.** §E of the checklist assumed the *connector* does the
   outreach and asked how to limit yourco's vicarious liability. Sourcer mode inverts it: better for
   agency exposure, worse for consent. TCPA / FL FTSA / CAN-SPAM now attach to yourco directly for
   every sourced contact. **The submission surface captures provenance and relationship at submission
   time** (how the connector knows this person, and whether the person knows the submission is
   happening) — this is a compliance field, not a nicety, and a submission without it is not verifiable.
   New checklist item **17a**.
3. **Nothing is payable before launch.** Bounties accrue and render as **staged / not payable**, exactly
   as the downline override already does. No cash moves until §A/§B clear and the launch gate opens.
4. **The verification queue is a promised SLA with a named owner.** "Verified within 24–48h" is a
   commitment to a person who is waiting to be paid. **Bird** owns the queue (program), **Kori** the
   people side, **Charles** the payout ledger. It runs on the operator side of the console.
5. **Delivery capacity is the unmodelled constraint.** The transcript's math (30 new clients at once)
   is multiples of what yourco can deliver today with the Founder personally running engagement #1. The bounty
   is being adopted as an *activation* mechanism, not as a volume plan; if submissions ever outrun
   delivery, the cap in §2 is the throttle.
6. **The 10% close rate is not a number yourco has.** It appears nowhere outside this Context section
   and must never reach a connector-facing surface — it is an unsubstantiated earnings claim under §C.

## Reversibility
**High on 1 and 2, moderate on 3, low on 4.** The bounty is a policy constant and a ledger section — it
can be switched off between runs, and pre-launch nothing has been paid. Referral mode is a per-record
field with a default. The recruiting rung is one line in `UNLOCKS`, but it is *socially* hard to reverse
once connectors have recruited under it — telling someone their downline no longer pays is a different
act from never having offered it. The growth-lever call is a positioning sweep and reversing it means
another one.

The likely forcing function on all four is counsel: if §A comes back hostile to the combination in
obligation 1, the bounty is the cheapest piece to drop and the override qualification the next
cheapest — in that order, and the Founder chooses.

## Trip-wire
- **Review:** 2026-11-11
- **Overturn if:** counsel finds the paid-at-enrollment + recruit-at-R1 + uncapped-depth combination
  indefensible; **or** the bounty runs for a full quarter and produces submissions that never become
  conversations (paying for lead volume yourco cannot convert); **or** submission volume outruns
  delivery capacity so that verified contacts sit uncalled.
- **Check:** `activeConnectors >= 5 and signedClients >= 1`
- **Check covers:** only that the program is actually running with real connectors and at least one
  signed client — the point at which the bounty's conversion can be measured at all. It covers **none**
  of the overturn conditions themselves: counsel's answer, submission→conversation conversion, and the
  uncalled-contact backlog are not instrumented. A firing check means *now the question can be asked*,
  not that the answer is yes.
