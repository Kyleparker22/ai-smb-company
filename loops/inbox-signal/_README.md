# loops/inbox-signal/

Weekly (Fri 07:15 ET), owner **Brett**. SOP: `processes/loops/inbox-signal.md`.

One dated artifact per run + `state.json` (message IDs already reported, plus the learned sender
allow/block lists). The state file is what stops `source-watch` — which runs 15 minutes later and
shares sources with this mailbox — reporting the same item twice.

**Empty is a real result.** A run that scanned 40 messages and kept none says so and lists what it
scanned. Padding a quiet week is the failure the loop contract's anti-spin clause exists to stop.
