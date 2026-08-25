# Central OS — alarm monitoring & installation (build 44)

**Working name:** Central OS · **Launch:** `prebuild-central-os` · **Port:** 8864
**Synthetic operator:** "Beacon Alarm & Monitoring" — ~4,200 monitored accounts, install crews.

## The bleeding neck
The social-engineering surface IS the product: a burglar's first move is a text that says "put my
account in test mode." False-alarm fines accrue per city ordinance; alarm permits lapse and turn
every dispatch into a fine; and the one dispatch decision that can never be automated away is
fire.

## Modules
1. **Signal & message triage** (Intake) — fire signal · burglary signal · a TEST-MODE request
   arriving by message · a passcode offered in a text thread · billing/service.
2. **The test-mode refusal** (Operations) — an account never enters test mode from a message
   thread; the request is refused, logged, and routed to a verified-callback task. THE refusal.
3. **Passcode discipline** (Operations) — software never accepts, confirms, or compares a
   passcode in text; verification is a human on a recorded callback to the number ON FILE
   (Ratio OS checklist pattern).
4. **The fire rule** (Operations) — a fire-signal dispatch is never cancelled by software,
   passcode or not. Burglary cancels are human decisions after verified callback.
5. **Permit & fine board** (Company Brain) — alarm permits per city as DATE ALERTS (config named
   default); false-alarm fine exposure counted per city's recorded schedule.

## Guardrails (load-bearing)
- `enter_test_mode_from_message` — **R0, logged.** The burglar's move, structurally unexpressable.
- `accept_passcode_in_text` — **R0.**
- `cancel_fire_dispatch` — **R0, never promoted, no exceptions.**
- Dunning/billing copy: threat-check as everywhere.

## ROI (typed)
False-alarm fines avoided (scenario — prevented fines can't be counted; exposure IS counted) ·
permit lapses caught (counted) · operator hours (time_saved) · the verified-callback file
(scenario).

## Demo path
Board (fine exposure by city, permits due) → "put me in test mode" text (refused + callback
task) → passcode in thread (refused) → try to cancel the fire dispatch (refused) → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the test-mode/passcode social-
engineering message.
