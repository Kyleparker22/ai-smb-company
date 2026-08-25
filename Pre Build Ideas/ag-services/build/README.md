# Field OS — build

Custom application / ag services. Port **8850** (`prebuild-field-os` in `.claude/launch.json`).

```
python3 seed.py          # synthetic Prairie Line Ag Services
python3 test_field_os.py # the suite
python3 server.py        # 127.0.0.1:8850
```

## The load-bearing refusals
- **Drift-first triage, causation never asserted.** A drift/exposure complaint is read first,
  logged verbatim with a timestamp (regulator-grade), and escalated to a human within the hour —
  and the system logs a `refused assert_drift_cause` event on every one. Acknowledging is not
  admitting; denying is not investigating.
- **The chemical question goes unanswered.** "What rate should I run" is routed to a licensed
  agronomist untouched. The label is the law; `recommend_chemical_or_rate` is R0, never promoted.
- **The as-applied billing gate.** `can_bill` refuses any invoice whose as-applied record is
  missing acres, product, rate, applied_at, or applicator_license — naming each missing field.
  An application without its record is unprovable work, and unprovable work is a dispute.
- **The RUP dispatch gate.** A restricted-use product cannot be dispatched without a licensed
  applicator recorded on the order — the violation happens before the rig leaves the yard.

## Honesty rules (from `_kit`)
Eval's costly label is `drift_exposure` and is reported alone. ROI is typed and labelled a model;
the complaint-file line is a scenario the operator prices ("a state investigation is not our
number to model"). Automation is counted from the event log. R0 refusals log events, never
approval rows. Synthetic data only; nothing is sent.
