# Rebid OS — build

The graveyard re-bid desk for machine shops. Port **8888** (`prebuild-rebid-os`).

```
python3 seed.py           # synthetic Ridgeway Precision Machining
python3 test_rebid_os.py  # the suite
python3 server.py         # 127.0.0.1:8888
```

## The never-seen mechanism
Every lost quote becomes a **standing order** that watches the shop's **counted** idle
capacity. When counted idle hours can hold the job and the defensible price (marginal floor +
recorded target margin) sits at or below the price the quote died at, the lost job re-bids
itself — at R1, with the floor's arithmetic printed on the offer.

## The load-bearing refusals
- **No bid below the marginal floor — NO PATH, structural.** Per machine class: recorded
  variable cost/hr × hours + material + the recorded margin line = the floor. The refusal
  prints the arithmetic; there is no rung, click, or approval that reaches under it.
- **No hour sold that wasn't counted.** Idle = available shift hours − booked jobs, from the
  recorded schedule. A week whose schedule wasn't maintained reads *unmeasured* and the desk
  stands down — we don't sell hours we can't count. A drafted re-bid holds its hours, so two
  re-bids can never sell the same counted hour.
- **A capability loss never re-bids.** The machine didn't change, so the bid doesn't either.
- **Deadline answers cite counted hours, never optimism.** "Need 200 by Friday?" is answered
  from the class's counted idle ("31 counted idle hours; 200 pcs needs ~26h — yes, bookable"),
  or refused when the hours-per-piece was never recorded.
- **A quote with unrecorded hours is UNREBIDDABLE** — no hours, no marginal math — and is
  named so at the door, not discovered a quarter late.

## Bounds on the re-bid
One re-bid per quote per quarter (recorded `last_rebid_at` + 90-day cooldown); silence is an
answer — a re-bid that drew no reply retires the standing order for good.

## Honesty rules (from `_kit`)
Costly eval label `deadline_rfq`. Re-bids and deadline answers queue at R1; the four R0s
(`bid_below_marginal_floor`, `sell_uncounted_capacity`, `rebid_capability_loss`,
`promise_capacity_optimism`) never promote and never become approvable rows. ROI typed; the
recovery line stays blank until wins are counted; the defensible-price story is a scenario.
This-week figures are counted from the append-only event log. Synthetic only. White-label.
**Nothing is sent.**
