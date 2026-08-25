# Key OS — build

Locksmiths & access control. Port **8874** (`prebuild-key-os`).

```
python3 seed.py         # synthetic Ironclad Lock & Access
python3 test_key_os.py  # the suite
python3 server.py       # 127.0.0.1:8874
```

## The load-bearing refusals
- **No dispatch path exists for an unverified rekey or unlock.** Every job is an authorization
  question wearing a work order's clothes; with no recorded owner/manager of record the request
  drafts as *unverifiable* with the gap named (ID seen, deed/lease shown), and a human decides.
  Opening a door for the wrong person is a break-in with an invoice.
- **A phone claim is recorded as a claim — never as authority.** "The guy on the phone said he
  owns it" goes in the record as exactly that, and can never come back out as a verification.
- **Key codes never leave.** Every outbound draft passes a structural scrub (regex + the
  recorded codes themselves, like PHI) — a draft carrying a code cannot be produced.
- **The master-key registry is append-only.** A change is a new record; there is no edit
  function in the codebase, and the history — every tenant's security — is never rewritten.
- **No quote off the recorded rate card exists in this system.** After-hours pricing is the
  card's own multiplier, not a 2am judgment call.
- **The emergency reads first.** A person or child locked in danger leads the triage; the reply
  opens with the 911 script verbatim and the van rolls anyway.

## Honesty rules (from `_kit`)
Costly eval label `emergency_lockout`. Service-clock ladder: 3 touches, 14-day cooldown,
silence exit. Jobs close with their authorization ref + rate-card citation.
Recovered-this-week counted (jobs closed on the card, dispatches sent, emergencies recorded).
ROI typed; the lawsuit file is a scenario that renders blank, never estimated. Synthetic only.
**Nothing is sent.**
