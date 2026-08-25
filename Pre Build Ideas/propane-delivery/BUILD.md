# Fuel OS — propane delivery (build 43)

**Working name:** Fuel OS · **Launch:** `prebuild-fuel-os` · **Port:** 8863
**Synthetic operator:** "Northline Propane" — ~2,800 tanks, 6 bobtails, keep-full + will-call mix.

## The bleeding neck
An out-of-gas event is not a missed delivery — it's a safety event: regulation requires a leak
check before the system relights, and skipping it is how houses explode and companies end. Under
that: runout prediction (degree-days nobody computes), will-call customers who call empty, and
contract customers billed off-contract by accident.

## Modules
1. **Call triage** (Intake) — GAS SMELL (evacuate script verbatim, R2, never troubleshoot) ·
   out-of-gas · delivery request · price/contract question.
2. **The leak-check gate** (Operations) — an out-of-gas delivery cannot close without a recorded
   leak-check result. Structurally: the ticket won't complete. THE refusal.
3. **Runout board** (Company Brain) — days-to-empty computed from recorded usage history +
   degree-days; a tank with no usage history reads UNKNOWN, never "fine."
4. **The contract clamp** (Back Office) — contract customers bill at their recorded contract
   price by construction; the market price cannot reach them.
5. **Requalification calendar** (Operations) — cylinder/tank requal dates as DATE ALERTS; an
   out-of-date tank can't be filled (gate names the date).

## Guardrails (load-bearing)
- `close_outage_without_leak_check` — **R0 by construction.**
- `troubleshoot_gas_smell` — **R0.** Evacuate language verbatim; a human and a truck, now.
- `bill_contract_customer_off_contract` — **R0 by construction.**
- `fill_unqualified_tank` — **R0**, the requal date named.

## ROI (typed)
Runouts predicted vs occurred (counted) · will-call converted to keep-full (counted × margin,
theirs) · dispatch hours (time_saved) · the leak-check file (scenario — never a saving).

## Demo path
Board (runout risk, UNKNOWN tanks honest) → gas-smell call (script verbatim) → close the outage
ticket without the leak check (refused) → contract clamp demo → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: gas smell.
