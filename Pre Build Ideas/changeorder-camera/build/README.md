# Delta OS — build

Change-order detection for a drywall/framing sub. Port **8883** (`prebuild-delta-os`).

```
python3 seed.py           # synthetic Keystone Interior Systems
python3 test_delta_os.py  # the suite
python3 server.py         # 127.0.0.1:8883
```

## The never-seen mechanism
Daily structured site-photo **observations** are diffed deterministically against **recorded plan
lines**. The day the built work departs from the drawings, a **DELTA** exists — photo ref and plan
rev cited — and the change order plus the contract's notice letter draft themselves the same day,
inside the notice window, not at closeout when memory and leverage are gone. A matching
observation produces **no delta**; most days the field matches the plan, and the build says so.

## The honest seam
**No vision model runs in this demo.** In deployment, a vision model reads the daily site photos
into structured observations (location + what the wall measured or contained + photo ref); here
the field app records those observations directly, and everything downstream of that seam — the
diff, the drafted classification, the confirmation gate, the priced CO, the notice window math —
is real and proven by the suite. The seam is named so nobody mistakes the demo for the model.

## The load-bearing refusals
- **No delta is priced unconfirmed — structurally.** Classification is a *draft*; a human
  confirms it, and the only pricing path checks `confirmed` with no force parameter anywhere.
  A wrong delta invoiced is worse than a missed one.
- **No price leaves the recorded rate schedule.** An off-schedule spec refuses to price — the
  recorded schedule or a human, never an ad-hoc number.
- **No notice letter without the recorded clause.** The letter cites the clause **verbatim** with
  days remaining as a DATE ALERT (not legal advice). A contract with no recorded clause: the
  letter refuses and names the gap. A blown window: the letter still drafts, **leads** with
  "expired N days ago," and is dated today — a backdated notice is a forgery, not a fix.
- **A verbal go-ahead is a note, not a signed change order.** Recorded verbatim, quoted back,
  and nothing prices or invoices from it.
- **A backcharge accusation gets the record pulled** — dated photos, plan revs, the delta
  ledger — never conceded and never argued by software; a human takes the position.

## Honesty rules (from `_kit`)
Costly eval label `backcharge`. The closeout ledger counts **same-day detected vs found later**
from photo dates — the product's own proof. This-week is counted from the ledger and the event
log, never asserted. ROI is typed (revenue / cash timing / scenario / time saved); a line with an
unrecorded input renders blank with the reason. Events are append-only. Synthetic records only.

**Nothing is sent.**
