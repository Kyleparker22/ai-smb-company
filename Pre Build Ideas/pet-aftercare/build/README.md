# Ember OS — build

Pet aftercare & cremation. Port **8880** (`prebuild-ember-os`).

```
python3 seed.py            # synthetic Willow Creek Pet Aftercare
python3 test_ember_os.py   # the suite
python3 server.py          # 127.0.0.1:8880
```

## The load-bearing refusals
- **The chain of custody is structural.** Every transfer — clinic → van → facility → chamber →
  urn → return — requires the recorded tag verification; a transfer without it has **no code
  path**, a wrong tag HOLDs, and a gap in the record reads **HOLD, never assumed**. The identity
  worry ("are these really Max's ashes?") is never answered with comfort alone — the answer is
  the verbatim chain, every transfer and tag check quoted as written, sent by a human.
- **The service-level wall.** Private / individual / communal is recorded at intake with the
  family's signed election ref; a change is a human act with the family's recorded consent ref,
  and a private pet never enters a shared chamber load — a communal cremation performed on a
  paid-private pet is irreversible.
- **Grief tone, structurally.** No family draft can carry "shipment", "unit", "processed",
  "disposal", or "inventory" — the tone check runs on every draft and refusals are logged.
- **The proof rule.** An urn engraving is approved only by the family's recorded act — software
  never signs off a spelling that will be engraved forever.
- **The aged-remains clock.** Unreturned remains get a bounded, gentle ladder (3 touches, 21-day
  cooldown — grief is not chased); the final decision is human-only, after the recorded policy
  clock, never before and never by software.

## Honesty rules (from `_kit`)
Costly eval label `identity_worry` — THE WRONG ASHES END THE BUSINESS. The keepsake offer is made
once, gently, and never re-pitched. Recovered-this-week is counted (pets home, tag checks
recorded, proofs families approved, reminders a human sent). ROI is typed; the wrong-ashes file
is a scenario the operator values — never our number. Automation is counted from the event log or
refused below the floor. Triage is deterministic pattern-matching — a real deployment puts a
model behind the routine paths and leaves the identity-first priority and all seven R0s exactly
as they are. Synthetic records only — invented families, invented clinics, 555 phones.
**Nothing is sent.**
