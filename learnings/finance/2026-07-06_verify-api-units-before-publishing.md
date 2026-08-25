# Verify a cost/usage API's units against ground truth before publishing its numbers

**Observed (2026-07-06):** the first pull from Anthropic's Admin `cost_report` was published to the HQ
tile + finance ledger as **$8,279.67/30d**. the Founder flagged it as implausible by eye. Recomputing one day's
cost by hand from `usage_report` token counts × list prices gave **$5.64** vs the reported "564.42" —
the amounts are **cents**. Real spend: $82.80/30d. The error shipped because the field said
`"currency": "USD"` and the value had decimals, both of which *look* like dollars.

**Why it matters:** a 100x error in the burn number nearly rewrote the runway story. Money numbers get
believed and re-quoted the moment they render on a dashboard — the bar for publishing them must be
higher than "the API returned it."

**How to apply:** any new metered $ or usage feed (Twilio, Stripe, future providers) gets ONE
ground-truth reconciliation before its numbers reach a surface: recompute a single day/item from raw
units × known prices, or diff against the provider's own billing UI. Write the verified unit into a code
comment at the conversion site. A number that can't be cross-checked ships with an explicit "unverified"
label, not silently.

Triggers: agent:charles, cost api, usage api, publishing a number, loop:finance, unit check
