# Stone OS — build

Monument & headstone dealers. Port **8871** (`prebuild-stone-os`).

```
python3 seed.py           # synthetic Hartwell Memorials
python3 test_stone_os.py  # the suite (90 assertions)
python3 server.py         # 127.0.0.1:8871
```

## The load-bearing refusals
- **Software never approves a proof.** Approval is a recorded human act by the family — a named
  person and a signature reference — and `approve_proof` is R0: the probe is refused and logged,
  and no approvable row is ever created. A proof approved by software is a misspelled headstone
  waiting to happen.
- **Engraving cannot start without the record.** No approval on the proof → refused with the
  reason; no force/skip parameter exists. A family correction places an engraving hold that even
  an approved proof does not clear — the corrected proof goes back to the family. Granite is not
  reworked.
- **The cemetery rulebook is cited or the answer is UNKNOWN.** Every compliance line cites the
  recorded per-cemetery rules sheet; a cemetery with no recorded rules reads UNKNOWN, never
  assumed, never borrowed from the cemetery next door.
- **Setting is two date checks.** The cemetery's recorded approval AND the foundation cure clock
  (per-cemetery cure days) — a pre-cure request is refused with the pour date and the settable
  date named. Granite over green concrete is a leaning monument.
- **The balance ladder is bounded and gentle.** Max 3 touches, 14-day cooldown, runs only after
  the monument is set, exits on "silence is an answer" — and no family-facing draft can carry
  urgency language (the tone check is structural). Nobody duns a widow by robot.

## Honesty rules (from `_kit`)
Costly eval label `proof_change` — the family correcting a date is the one message that can
never be mis-routed. Every outward draft is R1 and white-label. Recovered-this-week is counted
(balances collected, proofs family-approved, human sends — agent drafts don't count). ROI typed;
the remake that didn't happen is a scenario line that stays blank until the operator prices it.
A stalled order names its blocker or says "unrecorded" — it never guesses.

## What this does not do yet
No cemetery portal integrations (approval dates are recorded by staff, not fetched), no payment
processing (collections are counted from the ledger, not taken), no proof rendering (the proof
record carries the inscription text, not artwork), and no messaging transport. **Nothing is
sent.**
