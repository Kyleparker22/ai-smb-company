# The YourCo Flywheel

> **Owner: Brett** (strategy). The self-reinforcing loop that should make every turn of the business easier than the last. A flywheel beats a funnel because the output of each turn becomes the input energy for the next. Built 2026-06-10.

## The growth flywheel

```
        ┌──────────────► REACH ──────────────┐
        │   Reilly (outbound) · Katie         │
        │   (content) · Reed (demos)       │
        │   + CONNECTORS  (the people loop ↓) │
        │                                     ▼
   COMPOUND                                  TRUST
   Kemba: patterns → template                demos + site + "we run
   (faster, higher-margin builds)            on our own agents"
        ▲                                     │
        │                                     ▼
     EXPAND ◄──── PROVE ◄──── OUTCOME ◄──── LAND
   Bird: 2nd/3rd     Pickle: case      the employee     Janice→Kimi:
   employee +        studies +         delivers a       named employee
   referrals         referrals         real result      live in 48h
                                       (Kortney keeps
                                        it healthy)
```

**The turn:** reach the right businesses → earn trust before a conversation → land a named employee in 48 hours → it delivers a real outcome → that becomes proof (case study) + a referral + a second employee → which lowers the cost and raises the credibility of the *next* reach. Repeat, faster each time.

## The people loop — ADVOCATE (added 2026-08-10)

The wheel above compounds **proof** and **patterns**. It does not compound **people**: a referral
appears in it as an *output* — one lead, once — when the thing that actually happened is that a new
**actor** joined the system and can produce reach repeatedly. That is the connector program, and it
is a second loop hanging off the first.

```
   OUTCOME / a warm relationship ──► becomes a CONNECTOR
                                            │
                        R0 Joined ──► R1 Proven ──► R2 Producing ──► R3 Trusted ──► R4 Advisor
                            │                            │
                            │                            └─► may recruit more connectors
                            ▼                                 (override pay ⚠ counsel-gated)
                      produces REACH ─────────────────────────────────► back to the top
```

**Why it belongs in the flywheel and not inside REACH.** A channel spends and stops. A connector is
an asset that appreciates: they climb rungs on *computed evidence* (`crm/connector_ladder.py`), each
rung unlocks more capability, and at **R2 they can recruit other connectors** — the loop feeding
itself. Clients can enter it too: a client who refers **becomes a connector** and earns the full escalator — taken off their own bill first, cash above it (`decisions/2026-08-13_one-referral-rate-card.md`) — per active referred
client, which is the arc from EXPAND back to REACH the old diagram never drew.

**The launch subsidy** (the mechanic worth naming, stolen from Barstool's cross-promotion —
`decisions/2026-07-05_tool-triage.md` §Portnoy addendum 2, 2026-08-10). A new connector must never
start cold. yourco lends its own proof to their first conversation: a generated demo kit (R1),
the console and glass ledger, co-branding (R2), and the case studies. Each new connector inherits a
warm start from the network instead of building one — which is exactly why the wheel gets easier
per turn rather than merely bigger.

**The dependency that protects the beachhead.** This loop *cannot* spin before the client loop does,
by construction: R1 requires a real referral conversation and **R2 requires a live client retained
90 days**. Connectors cannot climb without delivered outcomes. So "go recruit connectors" is never a
substitute for closing client #1 — the ladder itself refuses it.

> ⚠️ **Unproven — a belief, not a finding.** 0 active connectors, 152 prospective, $0 referred
> revenue, 0 referred clients. *(Live counts: `crm/connector_ladder.compute()` — every connector sits
> at rung −1, because a rung requires `teamStatus: active` and nobody has it. Re-based 2026-08-23;
> checked on every run by invariant 9 in `runtime/consistency-check.py`.)* This loop is drawn from the program's design, not from evidence that
> it turns. The **1% downline override is counsel-gated (MLM)** and renders as *informational ·
> NOT PAYABLE* until it clears; recruiting itself is unlocked at R2, paying on the downline is not.
> Treat every claim in this section as a hypothesis until the first referred client lands.

## Why each turn gets easier (the accelerants)
1. **Proof lowers CAC.** Every happy client = a case study + a referral. Referred + proof-backed leads convert higher and cost less than cold — so reach gets cheaper every turn.
2. **Patterns lower build cost.** Every engagement feeds reusable patterns into `yourco-template` (Kemba) — so the next build is faster and higher-margin. Time-to-live trends toward zero; margin trends up.
3. **Outcomes feed the top.** Real results become Reed demos + Katie content — better reach material, for free.
4. **Expansion compounds revenue.** Bird adds a 2nd/3rd employee inside happy accounts — near-zero CAC revenue (the "hire once, scale forever" pricing is built for this).
5. **People compound, not just proof** *(added 2026-08-10, ⚠ unproven — see ADVOCATE above)*. A case study is a one-time asset; a connector is a recurring one. Accelerant 1 says proof lowers CAC — this is the sharper version: the *relationship* is the compounding unit, and each turn should leave behind more people who can reach on yourco's behalf, not just more evidence that it works.

## The friction (what slows the wheel — watch these)
- A bad outcome (Kortney's job: catch friction before it churns). One unhappy client breaks the proof → referral link.
- A slow or inconsistent build (Kimi + Kemba): if 48h slips, trust erodes.
- Thin proof early (pre-revenue): the wheel is hardest to start — the first 2–3 outcomes are everything. Bootstrap with the "we run yourco on its own agents" proof until real client proof exists.
- **A connector who is given nothing to sell with** *(the people loop)*. The launch subsidy is the whole mechanic; a connector sent out cold with a packet and no proof produces one awkward conversation and then stops. Under-equipping them doesn't slow the loop, it prevents it from starting.

## Two flywheels underneath it
**The OS-leverage flywheel** — more agents + loops + `learnings/` → more leverage per founder-hour → the Founder ships more of the growth flywheel with less → revenue funds more OS → more leverage. The `learnings/` substrate means the agents get measurably better every run (Kolby observes → learnings → behavior adjusts).

**The moat flywheel** — more engagements → more eval/reliability/observability data → a stronger, more provable moat → more executive trust → easier wins. The thing competitors can't copy (reliability + eval + trust) deepens with every client.

## The single sentence
*Land outcomes fast, turn them into proof, patterns and people — proof lowers your cost to reach, patterns lower your cost to build, and people reach on your behalf — so growth, margin, and the moat all compound on the same turn.*
