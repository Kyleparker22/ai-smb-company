# Pool OS — build

Pool service & maintenance. Port **8851** (`prebuild-pool-os` in `.claude/launch.json`).

```
python3 seed.py         # synthetic Bluewater Pool Care
python3 test_pool_os.py # the suite
python3 server.py       # 127.0.0.1:8851
```

## The load-bearing refusals
- **The words "safe to swim" never leave software.** Readings are reported against the pool's
  own recorded ranges; a human (CPO) judges water. Both the report and the recovery copy are
  tested for the forbidden words.
- **An injury report gets no automated reply.** Verbatim log at R2, human callback — nothing
  admitted, denied, or assessed.
- **Chemical dosing questions route unanswered.** The label is the law; a certified tech answers.
- **A stop bills only with its proof.** Readings (FC/pH/TA) + arrival stamp, or the refusal
  names each missing field: unprovable service is a dispute.

## Honesty rules (from `_kit`)
Costly eval label is `injury`, reported alone. ROI is typed and labelled a model; liability is a
scenario. Automation counted from the log. Recovered-this-week counted (stops billed, quotes won,
recovery visits a human booked). Equipment quote ladder: 3 touches, 7-day cooldown, silence is an
answer. Synthetic data only; nothing is sent.
