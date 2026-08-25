# yourco — Ghost Quarter (dogfood run)

**The quarter you're about to have: 2026-08-07 → 2026-11-05** (through the November monthly close)
**Run by:** Atlas + Charles, per `offerings/ghost-quarter/SPEC.md`, against yourco's own engagement exhaust.
**Data floor check (§3.2·3):** PASS — ≥60 days of real operational data (finance ledger May–Aug, loop artifacts Jun–Jul, CRM activity Jun–Aug). This is yourco's own data; no benchmarks, no other company's numbers.

**How to read this page (§3.2·1):** every line is either a **RECORD** (ledger-backed, cited) or a **PROJECTION** (modeled, assumption stated inline, ranges not points). A projection never appears in record styling. Misses get scored publicly at the next run (§8).

---

## 1 · Named drivers (each with its evidence rows)

| Driver | Observed value | Evidence (RECORD) |
|---|---|---|
| D1 · Fixed burn | ~$614.22/mo (pre-triage); ~$362/mo if the written triage executes; ~$271/mo deeper cut | `finance/expenses.md` §Recurring; `finance/runway.md` §Burn triage |
| D2 · Cash | $0 — every charge is the Founder personally funding as it arrives | `finance/runway.md` 2026-08-05 |
| D3 · Payment-failure pattern | 6 distinct failure events in 60 days (Google Jun 1 · API dark Jun 16–18 · Hostinger Jul 9 + Jul 20 · Descript Jul 10–12 · Canva Jul 21/24); Hostinger still unpaid ($24.49 + Descript $35 backlog) | `finance/expenses.md` rows + notes |
| D4 · Runtime state | DARK since ~Jul 30 (API org credit $0; last loop artifact Jul 28) | `finance/expenses.md` 2026-07-30 row; `loops/finance/` (latest 2026-08-03 is Cowork-side) |
| D5 · Owner decision-loop lag | build tasks close in days; outside-human tasks don't: counsel 33 days flagged/0 engaged; triage written 08-05/unexecuted; OtherVenture definition fields blank since ≥07-05 | `processes/counsel-gates.md`; `finance/runway.md` |
| D6 · Warm-pipeline velocity | 1 warm deal; at Proposal ~60 days; scope pivoted 08-06 (Design Studio now leads); v1 walkthrough committed for week of 08-10; proposed retainer $0 kickoff + $1,000/mo | `clients/sample-client/_README.md`; CRM activity log |
| D7 · Build throughput | high and reliable: ~18–20 frontier specs, restructures, demos shipped Jun–Aug with zero revenue attached | `offerings/`, git log |

**Drivers we do NOT have (named, not imputed — §3.2·3):** no revenue history of any kind (close rate on warm proposals is n=1, unresolved) · API/token metering stale since Jul 22 · the Founder's personal funding capacity (the real solvency variable — unobservable from this workspace) · usage-tool tiers still TBD (Vibe, Higgsfield, Calendly) · HighLevel backfill. Projections below inherit these holes and say so.

---

## 2 · Baseline: the quarter on autopilot (no behavior change)

**PROJECTION — cash out of the Founder's pocket by Nov 5: ~$1,840–$2,100.**
*Arithmetic shown:* 3 × $614.22 fixed = $1,842.66; + $59.49 already-failed backlog (Hostinger + Descript) if funded; + $0–200 usage/TBD lines. *Assumes:* every charge continues to be personally funded as it arrives (D2, observed pattern), no cancellations (D5, observed pattern), no API top-up.

**PROJECTION — the runtime stays dark all quarter.** *Assumes* no top-up decision, which is the observed state for 8+ days (D4). Consequence chain, driver-linked: no loops → no Monday briefings, no eval passes, no consistency watchdog, no finance pulse from the runtime → the next Ghost Quarter has *less* data than this one. The instrumentation this product depends on is currently decaying. **Sub-projection: the OS bills like it's alive while operating like it's dead** — on autopilot the Founder pays full freight (~$614/mo) for a machine that is off (D1 × D4).

**PROJECTION — suspension event risk is material, not tail.** *Assumes* the D3 failure pattern (6 events/60 days) continues under $0 float. The specific exposure: Hostinger is 29 days unpaid after 2 failures; one suspension = whole-OS-dark including everything git-synced only to the VPS clone since last push. Range honesty: we cannot compute a probability from 60 days of data — we can say the *precondition* (unpaid + $0 float) has held for a month and Hostinger's patience is an unobserved driver.

**PROJECTION — Sample Client ages past 90 days at proposal (~Sep 10) without a forced answer.** *Assumes* D6 continues as observed: touches happen (real meeting 08-06), asks don't. The pivot bought energy but reset the deliverable clock; on the observed pattern the next scope conversation is likelier than a signature conversation. Least-reliable assumption in this whole report — see §5.

**PROJECTION — the gate/counsel state is unchanged on Nov 5.** *Assumes* D5 holds (0 engagements per 33 tracked days → 0 per next 90). Consequences, mechanically: gate #14 blocks the partner signature the Founder wants to make all quarter; gate #11 keeps the collaboration unpapered while Sample Product deepens; Year-1 ("launch the day the gate clears") cannot begin; business-plan §10 failure-mode #1 — *"one more productive quarter"* — completes its second consecutive instance, and D7 says the quarter will indeed look productive.

---

## 3 · Leaks: where this quarter drops value (each priced, arithmetic shown)

| Leak | Mechanism (driver) | Priced range over the quarter | Arithmetic |
|---|---|---|---|
| L1 · Duplicate/idle subscriptions | D1×D5: cancellations written, not executed | **$580–$760** | Instantly duplicate(s) $97–194/mo + Descript $35 + Granola $14 + Plausible $9 = $155–252/mo × 3 |
| L2 · Paying for a dark runtime | D1×D4: infra lines (VPS $24.49 + Tailscale $8) + the gated sender ($97–291 Instantly) run while nothing executes | **$100–$900** depending on whether L1 executes and the runtime is revived vs powered down deliberately | (24.49+8) × 3 = $97 floor; + idle Instantly if kept |
| L3 · The unsigned warm engagement | D6: proposed retainer not started | **$0–$3,000 of foregone revenue** — labeled carefully: this is *proposed*, never booked; it is opportunity range, not "lost revenue" | $1,000/mo × 0–3 months depending on signature date |
| L4 · Decision-loop lag as compound interest | D5: counsel unengaged blocks 4 gates incl. the OA signature and the launch definition | not honestly priceable in dollars — named as the structural leak the other three grow out of | — |

---

## 4 · Scenario variants (same quarter, one intervention each)

**V1 — Triage executed by ~Aug 15.**
PROJECTION: personal outlay drops to **~$1,090–$1,250** (first month partly at old rate, then ~$362/mo floor), or **~$850–$950** at the deeper ~$271 cut. *Assumes* the `runway.md` keep-list is honored and cancellations land mid-August. Changes driver D1 directly; costs one afternoon. This is the highest-certainty money in this report — it is subtraction, not forecasting.

**V2 — Runtime decision made deliberately (either direction).**
Fund: API top-up + auto-reload on a funded card (the runtime has died silently twice — RECORD, learnings/ops 2026-06-18) → loops, watchdogs, and this product's own data supply resume; adds unmetered API spend (~$83–130/mo trailing range, RECORD `token_spend.md`, stale). Power down: stop VPS/Tailscale (~$32/mo) and accept a Cowork-only OS honestly. PROJECTION: either branch beats autopilot, which pays for the machine and gets neither the compute nor the honesty. *Assumes* nothing — this is a decision, not a forecast.

**V3 — Sample Client signs ~Sep 1 at the proposed $1,000/mo.**
PROJECTION: **$2,000 collected by Nov 5** (Sep + Oct), first MRR ≠ 0 in company history; against the V1 floor burn the company is **cash-positive ~$750–$900 for the quarter**. *Assumes:* signature Sep 1 (driver D6 says the walkthrough week of 08-10 is the causal event to watch — a signature ask within 14 days of a landed walkthrough is the tested path); invoices net-monthly and paid on time (no evidence either way — n=0 on collections); scope = proposed retainer, no re-price on the pivot. Secondary effects, driver-linked: the Boardroom/Ghost-Quarter/Twin-Test build triggers start becoming *real* (first signed client, month 2; 60 days of client ops data), the 48h claim gets its validation shot (Year-0 milestone), and failure-mode #2 gets its first data point in the good direction.

**V4 — Counsel engaged once, this month (~$1,500–$5,000 one-time; unpriced by any record — stated as an assumption band, not a quote).**
PROJECTION: unblocks in one engagement: OA signature path (gate #14, counsel-ready), collaboration one-pager review (#11), privacy final (#2), the one-sentence OtherVenture scope confirmation (#12). By Nov 5 the launch gate has a written definition for the first time in company history. *Assumes* the Founder makes one phone call in August; D5 says this is the report's second-least-reliable assumption.

---

## 5 · This report's least-reliable assumption (named unprompted, §3.2·5)

**Anything involving the Sample Client signature date.** The close-rate driver rests on n=1 unresolved warm deal; we have literally never observed yourco closing revenue. V3's numbers are arithmetic on a proposal, not a forecast of behavior — treat the *date* as unknown and the *mechanism* (walkthrough → direct ask → answer) as the only part the data supports. Runner-up: D5 extrapolation (that decision-lag continues) — it is the projection the Founder can personally falsify fastest, and this report would be pleased to be wrong there.

## 6 · The question this report exists to ask

**Want to prevent this version of the quarter?** Each leak maps to an action already written down: L1 → the triage table (`finance/runway.md`), L2 → the V2 decision, L3 → R3/R4 in today's board minutes (`offerings/boardroom/dogfood/2026-08-07_yourco-board-minutes.md`), L4 → one counsel engagement covering four gates. Per spec, the selling stops here — this artifact is analysis; the conversation is a separate step.

## 7 · Retrospective scoring (standing commitment, §3.2·6)

At the 2026-11-05 close this report gets scored line-by-line against what actually happened — outlay vs projected bands, runtime state, signature state, counsel state — and the deltas, including misses, publish in the next run. Kolby owns the scoring pass.

---

*Operational planning estimate, not a financial forecast, valuation, or investment advice. Every projected figure above is modeled, labeled, and assumption-tagged; records are cited to the ledger rows they came from.*
