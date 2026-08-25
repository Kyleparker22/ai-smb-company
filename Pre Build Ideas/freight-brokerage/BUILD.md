# 7 · Freight Brokerage & 3PL — **Carrier OS**

*Pre-build. Not built, not sold, no client. See `../_README.md` for the shared build contract.*

## 1. The idea in one paragraph

A freight broker's business is a trust decision made under time pressure, dozens of times a day: *is this carrier who they say they are, and will this load actually arrive?* Getting it wrong means double-brokered freight, a stolen load, a cargo claim, and a customer lost. Getting it right the manual way means twenty minutes of authority checks, insurance certificates, safety scores, phone verification, and gut feel per load — which no broker has during a market spike. **Carrier OS** turns vetting into a scored, evidenced, auditable trust file that updates continuously, then runs the rest of the load lifecycle around it: offer triage against a rate benchmark, automated check calls and tracking-exception handling, and a fraud tripwire log that gets smarter every time something looks wrong. The broker still releases every load — the system never does.

## 2. Who buys it

The **owner or ops manager** of a 5–75 person freight brokerage or 3PL, $5M–$80M in gross revenue, running McLeod / Turvo / Alvys / Tai, buying loads off DAT and Truckstop. Carrier fraud and double-brokering have been an escalating, widely-reported industry problem — this buyer does not need to be convinced the pain is real, only that a tool can help without slowing them down. They are also margin-obsessed, which makes the rate-benchmark and check-call-labor math land.

## 3. The bleeding neck

- **Carrier fraud and double-brokering.** Fresh authorities, hijacked MC numbers, spoofed email domains, phone numbers that don't match the FMCSA record, "carriers" that are actually unlicensed re-brokers. The cost of one miss is a full cargo claim plus the customer relationship.
- **Vetting time.** Authority status, insurance certificate and expiry, safety and inspection history, entity age, contact verification — per carrier, per load, by hand.
- **Check calls.** Where's the truck? Ops burns hours on calls and portal checks that produce a status nobody logs.
- **Rate blindness.** Coverage decisions made under deadline without a defensible benchmark, so margin varies by whoever booked it.
- **After hours.** Freight moves at 3am and the desk doesn't.

## 4. What we build

**Pillars:** Operations (5) + Sales (2) + Company Brain (7). **Form factors:** headless automation (vetting, tracking) + embedded surface (the trust file and load board) + digital employee (the after-hours desk).

| Module | What it does | Autonomy start |
|---|---|---|
| **Carrier trust file** | A continuously-updated scored file per carrier: authority status and age, insurance limits and expiry, safety/inspection history, contact consistency (phone/email/domain vs. the official record), address anomalies, and behavioral signals across our own load history. Every score component shows its evidence and its timestamp. | R2 to **refuse**, **R1 hard floor to approve** |
| **Fraud tripwires** | Named, individually-testable patterns — new authority + immediately bidding high-value freight, contact details that don't match the registered record, a sudden domain change, a rate that is implausibly below market, an insurance certificate expiring inside the transit window. Each fires with its evidence, and a fired tripwire is logged forever. | R1 |
| **Offer triage** | Ranks inbound carrier offers against a rate benchmark built from our own booked history for that lane, equipment and season, showing margin at each option. | R1 |
| **Check-call engine** | Automated status collection by text/ELD seam on a load-appropriate cadence, with **exception handling** as the real product: late departure, dwell, off-route, silence — each raising a typed exception with a suggested next move. | R2 for collection, R1 for anything told to a customer |
| **Load board** | Loads at risk right now, ranked by exception severity and customer impact; carrier trust distribution; margin by lane. | — |

**Integrations:** FMCSA authority and safety data seams, a carrier-monitoring vendor seam (Highway / Carrier411 class), TMS (McLeod / Turvo / Alvys), load boards (DAT / Truckstop), ELD and tracking providers, SMS.

## 5. The ROI model (assumption-stated)

```
Vetting time    = loads/wk × minutes vetting saved × loaded ops rate
Fraud avoided   = loads × exposure per load × incident rate delta   ← stated as SCENARIO, not a claim
Check-call time = active loads × calls each × minutes × loaded rate
Margin capture  = loads × basis points from benchmark discipline × avg revenue per load
```

**Fraud avoidance must be labelled a scenario, not a saving.** Prevented incidents cannot be counted — the honest presentation is "here is the exposure per event, here is what our tripwires caught in your own history, you decide what that's worth." A tool that claims a fraud-savings number to a freight broker is a tool they will not trust.

## 6. The demo path (10 minutes)

1. Load board: 27 loads in transit, four exceptions ranked, one customer-impacting.
2. A carrier offer on a $14k electronics load → trust file assembles in seconds → three tripwires fire (authority 41 days old, phone doesn't match the registered record, rate 34% below the lane benchmark) → hard refusal with evidence.
3. A clean carrier: same process, scored, approved-for-human-release — and the system *not* releasing it.
4. A dwell exception at 3:40am: detected, carrier texted, no response, escalation staged for the ops lead with a drafted customer note awaiting approval.
5. Margin by lane against benchmark; one lane blank and labelled because we have no booked history there.
6. Event log, rungs, counted automation rate, tripwire history.

## 7. Guardrails

**The system never releases a load, never dispatches, and never approves a carrier on its own** — approval is R1 permanently in the prototype; refusal can be autonomous, because refusing is the safe direction. It never states a carrier is fraudulent — it states which tripwires fired and what evidence they fired on. No credentialed scraping of any portal without a written compliance assessment (route to Rafi); the demo stubs every external data seam. Public safety data is directional and sometimes stale — the build must timestamp every score component and de-rate stale evidence rather than treating it as current.

---

## 8. The prompt

> Copy everything below into a fresh chat in this workspace.

---

**Build a pre-built vertical AI OS prototype for freight brokerages and 3PLs. Working name: Carrier OS.**

Build it into `Pre Build Ideas/freight-brokerage/build/`. This is an yourco pre-build: a demoable prototype on synthetic data, not a production system, not connected to any live data source. Read `CLAUDE.md`, `processes/ai-os-modules.md` and `processes/autonomy-matrix.md`, then read `Pre Build Ideas/property-management/build/core.py` and mirror its architecture and honesty rules exactly.

**The business you are modelling.** A 22-person brokerage: ~$34M gross revenue, ~140 loads/week, dry van and reefer, a carrier base of ~900 with ~180 active in the last quarter, running McLeod and buying off DAT. Build realistic lanes with seasonal rate behaviour, a carrier population that includes clean long-standing carriers, brand-new authorities, one hijacked-identity pattern and one re-broker pattern, plus a year of booked history so a rate benchmark can actually be computed. An ops manager should recognize their own board in the seed.

**Trust under time pressure is the product thesis. Build these five:**

1. **Carrier trust file.** A continuously-scored file per carrier: authority status and age, insurance limits and expiry against the transit window, safety and inspection history, contact consistency (does the phone, email domain and address match the registered record), and behavioural signals from our own load history. **Every score component must carry its evidence and its timestamp**, and stale evidence must be de-rated explicitly rather than treated as current. The score is never a bare number.
2. **Fraud tripwires.** Named, individually-testable patterns, each firing with its evidence and logged permanently: new authority bidding immediately on high-value freight; contact details inconsistent with the registered record; a recent domain change; a rate implausibly below the lane benchmark; insurance expiring inside the transit window; a carrier whose equipment profile doesn't match the load. Design them so a broker can read the list and add their own.
3. **Offer triage.** Rank inbound carrier offers against a rate benchmark computed from our own booked history for that lane, equipment and season — and when there is not enough history, say so rather than producing a benchmark.
4. **Check-call engine.** Automated status collection on a load-appropriate cadence, with typed **exceptions** as the real output: late departure, excessive dwell, off-route, silence past threshold. Each exception carries a suggested next move and a drafted customer notification awaiting approval.
5. **Load board.** Loads at risk right now ranked by exception severity and customer impact, carrier trust distribution, and margin by lane — with any lane lacking history shown blank and labelled.

**The autonomy asymmetry is the central design idea and must live in `core.py`:** the system may **refuse** a carrier autonomously (refusing is the safe direction) but may **never approve** one, never release a load, and never dispatch — human release stays R1 permanently in this prototype, and a test must prove it cannot be bypassed. The system also never asserts that a carrier *is* fraudulent; it reports which tripwires fired and on what evidence.

**Architecture.** Python stdlib only. `core.py` holds every rule: the carrier and load models, the trust score and its components with timestamps and staleness de-rating, every tripwire as a separately testable function, the rate benchmark computation and its minimum-sample rule, exception typing and thresholds, and the autonomy matrix. `agents.py` holds the agents with a declared rung per action. `seed.py` generates the brokerage at any scale (`--loads 140 --weeks 52`) including the fraud patterns above, carriers with expiring insurance mid-transit, silent trucks at 3am, and lanes with too little history to benchmark. `data/` is a JSON store. `app/` is the surfaces on a stdlib server bound to `127.0.0.1`; add the `.claude/launch.json` entry and verify it responds.

**The two honesty rules, enforced in `core.py`:** (1) any number not computable from recorded events returns `None` with a `_missing` reason and renders as `unmeasured — <reason>` — the rate benchmark on a thin lane is the flagship case; (2) every state change appends to an immutable event log with actor and rung, and the automation rate is counted from it.

**ROI panel:** vetting time, check-call time, and margin capture computed from the brokerage's own inputs with arithmetic on screen, labelled a MODEL. **Fraud avoidance is presented as a SCENARIO, never as a saving** — show exposure per event and what the tripwires caught in their own recorded history, and state explicitly that prevented incidents cannot be counted. Do not use any published industry fraud statistic unless you can source it to the last 12–18 months, and prefer not using one at all.

**Moat layer:** approval gate as the R1 floor on carrier approval, load release and every customer-facing message; an eval harness scoring each tripwire independently against a labelled set you generate, reporting **false-negative rate separately** because a missed fraud costs a claim while a false positive costs a phone call; audit log view; rung promotion only on a recorded streak — and note that carrier *approval* is explicitly excluded from promotion.

**Data:** synthetic only — invented carrier names, fake MC/DOT numbers that are obviously fake, 555 phone ranges, **no live FMCSA calls, no load-board access, no scraping of any kind**. Stub FMCSA, the carrier-monitoring vendor, the TMS, load boards, ELD/tracking and SMS behind adapter interfaces; a missing adapter reports `cannot-simulate`, a blocker, not a pass. Note in the README that any real credentialed data access needs a written compliance assessment first.

**White-label:** the demo brokerage's brand only — no yourco name, logo, or agent names on any carrier- or customer-facing surface.

**Tests:** `test_carrier_os.py`, stdlib asserts, pinning: a carrier can never be approved without a human actor in the event log; a load can never be released by an agent; each tripwire fires on its pattern and stays quiet otherwise; a thin lane returns `None` for its benchmark instead of a number; stale evidence is de-rated and labelled; the system never emits the word "fraudulent" as a determination; the event log is append-only.

**Deliverables:** the running build, the launch.json entry, a build `README.md` with the 10-minute demo script (load board → a high-value offer refused with three tripwires and their evidence → a clean carrier scored and *not* auto-released → a 3:40am dwell exception escalated → margin by lane with one honest blank → event log), and an honest "what this does not do yet." Report the test count and everything it refuses to compute.

Do not send anything, do not deploy, do not use a real carrier's or broker's name.
