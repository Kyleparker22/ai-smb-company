# Remit OS — build

Independent pharmacy, PBM reimbursement autopsy. Port **8886** (`prebuild-remit-os`).

```
python3 seed.py           # synthetic Lakeside Pharmacy (invented PBMs, drugs, patients)
python3 test_remit_os.py  # the suite
python3 server.py         # 127.0.0.1:8886
```

## The never-seen mechanism
Every remittance line reconciles against the **recorded** contract terms — rate basis, dispensing
fee, DIR schedule — and every underpayment lands in a recoverable ledger with the appeal draft
attached, **citing the clause and the delta to the cent**.

## The load-bearing refusals
- **No recorded contract, no audit.** Pinnacle Health Rx's remittances are in hand but its
  contract was never recorded — it reads **UNAUDITABLE** with the gap named. A guessed industry
  benchmark is not an audit.
- **An ambiguous clause goes to a human, with BOTH readings shown.** A brand on the MAC list
  reads two ways (§4.1 vs Exhibit B); software never picks the convenient one, in either
  direction — and never appeals a line the contract doesn't settle.
- **Recovered = counted remittance corrections only.** A recorded correction event, posted by a
  human from the PBM's corrected remittance. The estimate probe refuses at R0 and never becomes
  an approvable row.
- **"I think I got the wrong pills" never waits in a queue.** The pharmacist-now script is the
  whole reply, immediately — the queue is structurally refused.
- **No PHI outbound.** Findings are built from a field whitelist, so a patient identifier on a
  remittance line can never reach a finding — and an appeal drafts only from a finding. The
  regex scrub is the net behind the structure, tested by planting.
- **Margin is measured or unmeasured, never assumed.** The dispensed-at-a-loss list is counted
  from recorded acquisition costs; a drug with no recorded cost reads unmeasured, by name.

## Honesty rules (from `_kit`)
Costly eval label `wrong_med`. Appeal windows are the contract's own recorded numbers — DATE
ALERTS, not legal advice. The counted week (corrections, appeals sent, alerts, autopsies) comes
from the event log, never asserted. ROI typed; the at-a-loss list is a scenario line the owner
values. Appeals and outward drafts R1; autopsies and window alerts R2. Synthetic records only —
invented PBMs, invented patients, 555 phones. **Nothing is sent.**
