# Receipt OS — build 71

The underwritable audit trail for title & escrow agencies.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py               # synthetic Beacon Title & Escrow (~90 closings/mo x 6 months)
python3 test_receipt_os.py    # 119 assertions
python3 server.py             # 127.0.0.1:8894
```

Launch name **`prebuild-receipt-os`** (port 8894, 127.0.0.1 only). Env: `RECEIPTOS_DATA_ROOT`.

## What it is

"Beacon Title & Escrow" — 3 offices, ~90 closings/mo. The never-seen mechanism: the agency's
security controls already generate receipts — callback-verified wire changes, dual-control
releases, blocked attempts, drills — and Receipt OS packages that evidence into the
**coverage-year file** an insurer can price against and the **realtor one-pager** that wins
referrals. The moat itself becomes a revenue line: **evidence-backed premium reduction** — and
the premium claim is exactly what the file never makes.

Five modules: **the control ledger** (append-only; a correction is a new entry — there is no
edit function), **the coverage-year file** (counted verifications, counted blocks, drill record,
and the exceptions list), **the renewal packet** (R1), **the referral proof** (R1, zero client
data), **intake triage** (the wire change reads first).

## The refusals it is organised around

- **The wire stop, inherited exactly from Closing OS** — the law of this vertical. A wire-change
  email is recorded **verbatim** as the first receipt of the chain, the callback protocol is
  stated (*call the recorded number on file — NEVER the one in the message*), and
  `act_on_emailed_wire_change` is R0, never promotable. `record_callback` has no parameter that
  could carry the email's number into a receipt — the field cannot exist.
- **UNTESTED, never "in place."** A control with no drill result in the policy period reads
  UNTESTED — `claim_untested_control` is R0. positive_pay ships honestly undrilled in the seed,
  and the packet says so.
- **The exceptions cannot be omitted — structurally.** The exceptions query and the successes
  query are one read path over one store (`wire_chains`), and `render_renewal_packet` refuses to
  render without both halves. A packet without its exceptions data cannot exist; the 3 seeded
  gap-wires are listed by id in every draft.
- **No premium promise anywhere.** The packet ends *"underwriters price; we evidence"* and runs
  a forbidden-language check ("guaranteed discount", "will lower your premium", …) structurally
  before it drafts. `promise_premium_outcome` is R0. The ROI premium line is **blank until a
  renewal has actually happened** and computes only from the operator's own invoices.
- **The realtor one-pager carries zero client data** — built from counts only, then scrubbed
  against every recorded party name, file number, and amount (a planted client is hunted in the
  suite). White-label; two named humans on every dual-control receipt.

## Honesty rules (from `_kit`)

Costly eval label `wire_change` — *a missed wire-change signal is the agency-ending event* —
recall 1.0, zero missed. Every counted number is hand-checkable against the append-only ledger;
demo fixtures (`demo_tag`) are excluded from every count; the week panel is counted, never
asserted; ROI is typed with the breach line a blank scenario — prevented incidents cannot be
counted. R0 probes never become approvable rows.

Synthetic records only, invented parties, 555 phones. **Nothing is sent.**
